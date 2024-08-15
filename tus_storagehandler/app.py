"""API server entry point."""

import logging
import os
from enum import Enum
from pathlib import Path
from typing import Optional

from connexion import FlaskApp
from foca import Foca


class Environment(Enum):
    """Defines possible environments for the application."""

    DEV = "dev"
    PROD = "prod"


logger = logging.getLogger(__name__)


def init_app() -> FlaskApp:
    """Initialize and return the FOCA app.

    This function initializes the FOCA app by loading the configuration
    from the environment variable `TUS_FOCA_CONFIG_PATH` if set, or from
    the default path if not. It raises a `FileNotFoundError` if the
    configuration file is not found.

    Returns:
        A Connexion application instance.

    Raises:
        FileNotFoundError: If the configuration file is not found.
    """
    # Determine the configuration path
    if config_path_env := os.getenv("CSH_FOCA_CONFIG_PATH"):
        print(config_path_env)
        config_path = Path(config_path_env).resolve()
    else:
        config_path = (
            Path(__file__).parents[1] / "deployment" / "config.yaml"
        ).resolve()

    # Check if the configuration file exists
    if not config_path.exists():
        raise FileNotFoundError(f"Config file not found at: {config_path}")

    foca = Foca(
        config_file=config_path,
    )
    return foca.create_app()


def main(env: Optional[str] = None) -> None:
    """Run FOCA application.

    Args:
        env (str, optional): The environment in which to run the application.
                             Defaults to 'dev' if not specified. Acceptable values
                             are 'dev' and 'prod'.
    """
    # Set default port
    default_port = 8081

    # Initialize application
    app = init_app()

    # Set environment and port
    if env is None:
        env = Environment.DEV.value
    elif env not in [e.value for e in Environment]:
        raise ValueError(
            f"Invalid environment: {env}. Must be one of "
            f"{[e.value for e in Environment]}"
        )

    port = app.port if env == Environment.DEV.value else default_port

    # Run the application
    app.run(port=port)


if __name__ == "__main__":
    # Get environment variable or default to 'dev'
    environment = os.getenv("ENVIRONMENT", "dev")
    main(environment)
