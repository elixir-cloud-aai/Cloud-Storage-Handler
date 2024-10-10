"""Utility functions for the Cloud Storage Handler package."""

import os
from pathlib import Path

from foca import Foca

from cloud_storage_handler.custom_config import CustomConfig


def get_config_path() -> Path:
    """Get the configuration path.

    Returns:
      The path of the config file.
    """
    # Determine the configuration path
    if config_path_env := os.getenv("CSH_FOCA_CONFIG_PATH"):
        return Path(config_path_env).resolve()
    else:
        return (Path(__file__).parents[1] / "deployment" / "config.yaml").resolve()


def get_custom_config() -> CustomConfig:
    """Get the custom configuration.

    Returns:
      The custom configuration.
    """
    conf = Foca(config_file=get_config_path()).conf
    return CustomConfig(**conf.custom)
