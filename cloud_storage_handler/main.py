"""API server entry point."""

import os
from pathlib import Path
from flask import Flask, send_from_directory, current_app, render_template
from connexion import FlaskApp
from foca import Foca
from cloud_storage_handler.api.elixircloud.csh.tus import tus_manager
from cloud_storage_handler.api.elixircloud.csh.client import register_minio_client
from cloud_storage_handler.api.elixircloud.csh.controllers import TusController
import logging


logger = logging.getLogger(__name__)


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
    
    tus_controller = TusController(app)

    app.add_url_rule('/elixircloud/csh/v1/file-upload', 'file-upload', tus_controller.tus_file_upload, methods=['OPTIONS', 'POST'])
    app.add_url_rule('/elixircloud/csh/v1/file-upload/<resource_id>', 'file-upload-chunk', tus_controller.tus_file_upload_chunk, methods=['HEAD', 'PATCH', 'DELETE'])
    app.add_url_rule('/elixircloud/csh/v1/file-upload/<resource_id>/download', 'file-download', tus_controller.tus_file_download, methods=['GET'])
    app.add_url_rule('/elixircloud/csh/v1/file-upload', 'file-list', tus_controller.list_files, methods=['GET'])  
    app.add_url_rule('/elixircloud/csh/v1/file-upload/all/download', 'file-download-all', tus_controller.download_all_files, methods=['GET'])


    app.run(port=app.port)


if __name__ == "__main__":
    main()
