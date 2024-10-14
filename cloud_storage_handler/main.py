"""API server entry point."""

import os
from pathlib import Path

from connexion import FlaskApp
from foca import Foca

from cloud_storage_handler.api.elixircloud.csh.client import (
    register_minio_client,
)


def init_app() -> FlaskApp:
    """Initialize and return the FOCA app.

    This function initializes the FOCA app by loading the configuration
    from the environment variable `CSH_FOCA_CONFIG_PATH` if set, or from
    the default path if not.

    Returns:
        A Connexion Flask application instance.
    """
    config_path = Path(
        os.getenv(
            "CSH_FOCA_CONFIG_PATH",
            Path(__file__).parents[1] / "deployment" / "config.yaml",
        )
    ).resolve()

    foca = Foca(
        config_file=config_path,
        custom_config_model="cloud_storage_handler.custom_config.CustomConfig",
    )
    return foca.create_app()


def main() -> None:
    """Run FOCA application."""
    app = init_app()
    app = register_minio_client(app)
    app.run(port=app.port)


if __name__ == "__main__":
    main()
