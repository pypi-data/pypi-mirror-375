"""
Main entry point for the Ethical Gardeners simulation environment.
"""
import os
import sys
from importlib.resources import files

import hydra
import numpy as np
from omegaconf import OmegaConf

from ethicalgardeners import algorithms
from ethicalgardeners.action import create_action_enum
from ethicalgardeners.actionhandler import ActionHandler
from ethicalgardeners.gardenersenv import GardenersEnv
from ethicalgardeners.metricscollector import MetricsCollector
from ethicalgardeners.observation import TotalObservation, PartialObservation
from ethicalgardeners.renderer import GraphicalRenderer, ConsoleRenderer
from ethicalgardeners.rewardfunctions import RewardFunctions
from ethicalgardeners.gridworld import GridWorld


def make_env(config=None):
    """
    Create the environment using Hydra configuration.

    This function initializes the environment with the provided configuration,
    setting up the grid, action space, observation strategy, reward functions,
    metrics collector, and renderers.

    Args:
        config (OmegaConf): The configuration object containing environment
            parameters.
    """
    if config is None:
        config = OmegaConf.create({
            "grid": {},
            "observation": {},
            "metrics": {},
            "renderer": {
                "graphical": {},
                "console": {}
            }
        })

    # Base simulation parameters
    num_iter = config.get("num_iterations", 1000)
    render_mode = config.get("render_mode", "human")

    # Random generator initialization
    random_seed = config.get("random_seed", None)
    if random_seed is not None:
        random_generator = np.random.RandomState(random_seed)
    else:
        random_generator = np.random.RandomState()

    # Common parameters for all grid initializations
    min_pollution = config.grid.get("min_pollution", 0)
    max_pollution = config.grid.get("max_pollution", 100)
    pollution_increment = config.grid.get("pollution_increment", 1)
    collisions_on = config.grid.get("collisions_on", True)
    num_seeds_returned = config.grid.get("num_seeds_returned", 1)
    flowers_data = config.grid.get("flowers_data", None)

    # Random initialization parameters
    width = None
    height = None

    # Grid initialization
    grid_init_method = config.grid.get("init_method", "random")

    init_config = {}
    if grid_init_method == "from_file":
        file_path = config.grid.file_path

        init_config = {"file_path": file_path}

    elif grid_init_method == "from_code":
        grid_config = config.grid.get("config", None)

        init_config = {"grid_config": grid_config}

    elif grid_init_method == "random":
        width = config.grid.get("width", 10)
        height = config.grid.get("height", 10)
        obstacles_ratio = config.grid.get("obstacles_ratio", 0.2)
        nb_agent = config.grid.get("nb_agent", 2)

        init_config = {
            "obstacles_ratio": obstacles_ratio,
            "nb_agent": nb_agent
        }

    grid_world = GridWorld.create_from_config(
        init_method=grid_init_method,
        init_config=init_config,
        width=width,
        height=height,
        min_pollution=min_pollution,
        max_pollution=max_pollution,
        pollution_increment=pollution_increment,
        collisions_on=collisions_on,
        num_seeds_returned=num_seeds_returned,
        random_generator=random_generator,
        flowers_data=flowers_data
    )

    # Create the action space from the number of flowers types
    num_flower_types = len(grid_world.flowers_data)
    action_enum = create_action_enum(num_flower_types)

    # Initialise ActionHandler
    action_handler = ActionHandler(
        grid_world,
        action_enum
    )

    # Initialise observation strategy
    observation_type = config.observation.get("type", "total")
    if observation_type == "total":
        observation_strategy = TotalObservation(
            grid_world
        )
    elif observation_type == "partial":
        obs_range = config.observation.get("range", 1)
        observation_strategy = PartialObservation(
            obs_range
        )
    else:
        raise ValueError(
            f"Unknown observation type: {observation_type}. "
            "Supported types are 'total' and 'partial'."
        )

    # Initialise reward functions
    reward_functions = RewardFunctions(
        action_enum
    )

    # Initialise metrics collector
    metrics_out_dir = config.metrics.get("out_dir_path", "./metrics")
    export_metrics = config.metrics.get("export_on", False)
    send_metrics = config.metrics.get("send_on", False)

    # Read `config.metrics.wandb` if present and convert to a plain dict
    wandb_cfg = config.metrics.get("wandb", {})
    wandb_params = dict(wandb_cfg)

    metrics_collector = MetricsCollector(
        metrics_out_dir,
        export_metrics,
        send_metrics,
        **wandb_params
    )

    # Initialise renderers
    renderers = []

    # Determine if the user wants to display the environment
    # Initialize Graphical renderer based on configuration
    if config.renderer.graphical.get("enabled", True):
        post_analysis_on = config.renderer.graphical.get(
            "post_analysis_on", False
        )
        out_dir = config.renderer.graphical.get("out_dir_path", "./videos")
        cell_size = config.renderer.graphical.get("cell_size", 50)
        colors = config.renderer.graphical.get("colors", None)

        graphical_renderer = GraphicalRenderer(
            cell_size=cell_size,
            colors=colors,
            post_analysis_on=post_analysis_on,
            display=True,
            out_dir_path=out_dir,
        )
        renderers.append(graphical_renderer)

    # Initialize Console renderer based on configuration
    if config.renderer.console.get("enabled", False):
        post_analysis_on = config.renderer.console.get(
            "post_analysis_on", False
        )
        out_dir = config.renderer.console.get("out_dir_path", "./videos")
        characters = config.renderer.console.get("characters", None)

        console_renderer = ConsoleRenderer(
            characters=characters,
            display=True,
        )
        renderers.append(console_renderer)

        # Add a Graphical renderer if post analysis is enabled to
        # create a video after the simulation
        if post_analysis_on:
            cell_size = config.renderer.graphical.get("cell_size", 50)
            colors = config.renderer.graphical.get("colors", None)

            graphical_renderer = GraphicalRenderer(
                cell_size=cell_size,
                colors=colors,
                post_analysis_on=post_analysis_on,
                display=False,  # No real-time rendering
                out_dir_path=out_dir
            )
            renderers.append(graphical_renderer)

    return GardenersEnv(
        random_generator=random_generator,
        grid_world=grid_world,
        action_enum=action_enum,
        num_iter=num_iter,
        render_mode=render_mode,
        action_handler=action_handler,
        observation_strategy=observation_strategy,
        reward_functions=reward_functions,
        metrics_collector=metrics_collector,
        renderers=renderers
    )


def make_agent_algorithm():
    """
    Placeholder function to create an agent algorithm.
    """
    # Currently, this function does not implement any specific agent algorithm.
    # It can be extended to return an RL agent or a policy.
    return None


def run_simulation(env, agent_algorithms=None, deterministic=None,
                   needs_action_mask=None, **kwargs):
    """
    Run the simulation loop for the environment.

    This function iterates through the agents in the environment,
    collects observations, rewards, and flags for termination or truncation
    and steps the environment with an action for each agent.

    Args:
        env (GardenersEnv): The environment to run the simulation in.
        agent_algorithms (list, optional): List of agent algorithms to use.
            Defaults to None, which means random actions will be taken.
        needs_action_mask (list, optional): List of booleans indicating whether
            each agent algorithm requires an action mask. Defaults to None.
    """
    env.reset()

    if needs_action_mask is None:
        needs_action_mask = [False for _ in env.possible_agents]

    if deterministic is None:
        deterministic = [True for _ in env.possible_agents]

    for agent in env.agent_iter():
        observations, rewards, termination, truncation, infos = env.last()
        observation, action_mask = observations.values()

        if termination or truncation:
            break

        if agent_algorithms is None:
            action = env.action_space(agent).sample(
                action_mask
            )
        else:
            # Use the corresponding agent algorithm to determine the action
            agent_index = env.possible_agents.index(agent)
            action = algorithms.predict_action(
                agent_algorithms[agent_index],
                observation,
                action_mask,
                needs_action_mask=needs_action_mask[agent_index],
                deterministic=deterministic[agent_index],
                **kwargs
            )

        env.step(action)

    # Close the environment
    env.close()


def _find_config_path():
    """
    Return a valid path to the 'configs' directory prioritizing:
    1) The CWD ('./configs')
    2) The packaged resources ('ethicalgardeners/configs')
    3) The GitHub repo/ZIP (the 'configs' folder next to the module)
    """
    # 1) The CWD
    cwd_cfg = os.path.join(os.getcwd(), "configs")
    if os.path.isdir(cwd_cfg):
        print(f"Using config path from CWD: {cwd_cfg}")
        return cwd_cfg

    # 2) Packaged resources
    try:
        pkg_cfg = files("ethicalgardeners").joinpath("configs")
        if pkg_cfg.is_dir():
            print(f"Using config path from installed package: {pkg_cfg}")
            return str(pkg_cfg)
    except Exception:
        pass

    # 3) Source tree (repo/ZIP)
    repo_cfg = os.path.join(os.getcwd(), "../configs")
    if os.path.isdir(repo_cfg):
        print(f"Using config path from source tree: {repo_cfg}")
        return repo_cfg

    raise FileNotFoundError(
        "The 'configs' directory could not be found in the CWD, "
        "the installed package, or the source tree."
        "Please set the config path with --config-dir /path/to/configs"
    )


# Decide the default config path if the user does not provide `--config-dir`
_HAS_CONFIG_DIR = any(a == "--config-dir" for a in sys.argv)
_DEFAULT_CONFIG_PATH = None if _HAS_CONFIG_DIR else _find_config_path()


@hydra.main(version_base=None, config_path=_DEFAULT_CONFIG_PATH)
def main(config):
    # Check if the configuration has the correct structure
    try:
        valid_cfg = any(
            key in config for key in ["grid", "observation",
                                      "metrics", "renderer"]
        )
    except Exception:
        valid_cfg = False

    # If the configuration is not valid, use None to trigger defaults
    if not valid_cfg:
        config = None

    # Initialise the environment with the provided configuration
    env = make_env(config)

    env.reset()

    # Main loop for the environment
    run_simulation(env)


if __name__ == "__main__":
    main()
