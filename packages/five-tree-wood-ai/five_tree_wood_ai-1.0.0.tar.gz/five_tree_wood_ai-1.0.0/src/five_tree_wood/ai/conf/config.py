"""
Configuration management for Five Tree Wood AI.

This module provides centralized configuration loading and directory management.
It loads configuration from both config.ini and secrets.ini files, with secrets
overlaying the base configuration.
"""

import configparser
import os
from typing import Optional

# Global configuration directory
_config_dir: Optional[str] = None


def set_config_dir(config_dir: str) -> None:
    """
    Set the global configuration directory.

    Args:
        config_dir: Path to the configuration directory
    """
    global _config_dir  # pylint: disable=global-statement
    _config_dir = config_dir


def get_config_dir() -> str:
    """
    Get the current configuration directory.

    Returns:
        str: Path to the configuration directory

    Raises:
        RuntimeError: If configuration directory has not been set
    """
    if _config_dir is None:
        # Default to './conf' if not set
        return os.path.join(os.getcwd(), "conf")
    return _config_dir


def get_config() -> configparser.ConfigParser:
    """
    Load configuration from config.ini and secrets.ini.

    Loads base configuration from config.ini, then overlays any settings
    from secrets.ini. This allows sensitive information to be kept separate
    from the main configuration.

    Returns:
        configparser.ConfigParser: Combined configuration object

    Raises:
        FileNotFoundError: If required configuration files are not found
    """
    config_dir = get_config_dir()

    # Initialize configuration parser
    config = configparser.ConfigParser()

    # Load base configuration
    config_path = os.path.join(config_dir, "config.ini")
    if os.path.exists(config_path):
        config.read(config_path)

    # Load secrets configuration (overlay)
    secrets_path = os.path.join(config_dir, "secrets.ini")
    if os.path.exists(secrets_path):
        config.read(secrets_path)
    elif not os.path.exists(config_path):
        # If neither file exists, check in project root for backward compatibility
        root_secrets_path = os.path.join(os.getcwd(), "secrets.ini")
        if os.path.exists(root_secrets_path):
            config.read(root_secrets_path)
        else:
            raise FileNotFoundError(
                f"No configuration files found. Expected config.ini or secrets.ini "
                f"in {config_dir} or secrets.ini in project root."
            )

    return config
