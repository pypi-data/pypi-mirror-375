#
# This file is part of storagetools.
#
# Copyright (c) 2025 Mauritz Mälzer
#
# BSD-3-Clause License
#

"""Context for a data analysis environment.

Provides a context class, its setup and an attachment function
"""

DEFAULT_LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "format": "%(asctime)s %(levelname)s %(filename)s:%(lineno)d (%(funcName)s): %(message)s"
        }
    },
    "handlers": {
        "screen": {
            "class": "logging.StreamHandler",
            "level": "INFO",
            "formatter": "default",
            "stream": "ext://sys.stdout",
        },
        "file": {
            "class": "logging.FileHandler",
            "level": "DEBUG",
            "formatter": "default",
            "filename": "debug.log",
            "mode": "a",
        },
    },
    "loggers": {"": {"level": "DEBUG", "handlers": ["screen", "file"]}},
}

import ast
import configparser
import logging
import logging.config
import os

from rich import traceback
from typeguard import typechecked

traceback.install()
log = logging.getLogger(__name__)


class Context:
    """
    A class used to store various paths and properties.

    This may be reduced to being a dictionary in the future.
    """

    def __init__(self) -> None:
        self.paths = {}
        self.prep = {}
        self.cores = 1
        self.max_kvsize = 1099511627776  # 1 TB

    @typechecked
    def gather_paths(self, config: configparser.ConfigParser, defaults: dict) -> None:
        """
        Gathers working paths from config file and stores them in self.

        Args:
            config (ConfigParser): The configuration object.
        """
        self.paths["work"] = os.path.join(
            config.get(
                "storagetools.locations",
                "workdir_root",
                fallback=defaults["storagetools.locations"]["workdir_root"],
            ),
            config.get(
                "environment",
                "analysis_name",
                fallback=defaults["environment"]["analysis_name"],
            ),
        )
        self.paths["storage"] = os.path.join(
            self.paths["work"],
            config.get(
                "storagetools.locations",
                "storage_dir",
                fallback=defaults["storagetools.locations"]["storage_dir"],
            ),
        )
        self.paths["database"] = os.path.join(
            self.paths["work"],
            config.get(
                "storagetools.locations",
                "database_filename",
                fallback=defaults["storagetools.locations"]["database_filename"],
            ),
        )
        log.debug("paths gathered from config")

    @typechecked
    def paths_prepend(self, path_to_main: str) -> None:
        """
        Prepends the main directory path to the existing paths.

        Args:
            path_to_main (str): The path to the main directory.
        """
        for k, v in self.paths.items():
            self.paths[k] = os.path.join(path_to_main, v)
        log.info(f"prepended '{path_to_main}' to ctx.paths")

    @typechecked
    def gather_property_columns(
        self, config: configparser.ConfigParser, defaults: dict
    ) -> None:
        """
        Gathers the property columns from the config file.

        This affects experiments, sensors and channels.

        Args:
            config (ConfigParser): The configuration object.
        """
        self.experiment_properties = ast.literal_eval(
            config.get(
                "property_columns",
                "experiment",
                fallback=str(defaults["property_columns"]["experiment"]),
            )
        )
        self.sensor_properties = ast.literal_eval(
            config.get(
                "property_columns",
                "sensor",
                fallback=str(defaults["property_columns"]["sensor"]),
            )
        )
        self.channel_properties = ast.literal_eval(
            config.get(
                "property_columns",
                "channel",
                fallback=str(defaults["property_columns"]["channel"]),
            )
        )
        log.debug("properties gathered from config")

    def create_folders(self):
        """
        Creates necessary folders (workdir).
        """
        os.makedirs(self.paths["work"], exist_ok=True)
        os.makedirs(self.paths["storage"], exist_ok=True)
        log.debug("folders created")


@typechecked
def attach(conf="config.ini", path_to_main: str = ".") -> Context:
    """
    Attaches to a context as described in the configuration.
    Set up logging and working paths.

    Args:
        conf (str): The path to the configuration file. Defaults to "config.ini".
        path_to_main (str, optional): The path to the main directory. Defaults
            to '.', meaning the config is stored in same directory. This is
            relevant, if a data analysis project contains many scripts in
            different subdirectories and the config file is stored in the top
            level.

    Returns:
        Context: The context object with the gathered paths and properties.
    """
    # Define default values
    defaults = {
        "environment": {
            "analysis_name": "default_analysis",
            "available_cores": 1,
            "max_kvsize": 1099511627776,
        },
        "storagetools.locations": {
            "workdir_root": "work",
            "storage_dir": "data",
            "plot_dir": "plots",
            "database_filename": "database.db",
        },
        "property_columns": {"experiment": {}, "sensor": {}, "channel": {}},
    }

    if path_to_main != ".":
        conf = os.path.join(path_to_main, conf)
    if not os.path.exists(conf):
        with open(conf, "w") as f:
            f.write("[environment]\nanalysis_name = default_analysis")
    try:
        logging.config.fileConfig(conf, disable_existing_loggers=False)
    except KeyError:
        logging.config.dictConfig(DEFAULT_LOGGING_CONFIG)

    config = configparser.ConfigParser()
    config.read(conf)
    log.info(
        f"{config.get('environment', 'analysis_name', fallback=defaults['environment']['analysis_name'])}"
    )

    ctx = Context()
    ctx.gather_paths(config, defaults)
    # Prepend main path if necessary
    if path_to_main != ".":
        ctx.paths_prepend(path_to_main)
    ctx.gather_property_columns(config, defaults)
    ctx.create_folders()

    # Writes maximum size for LMDB key value storage from config file to ctx.
    ctx.max_kvsize = int(
        config.get(
            "environment", "max_kvsize", fallback=defaults["environment"]["max_kvsize"]
        )
    )
    log.debug(f"set max_kvsize to {ctx.max_kvsize}")

    # Get available cores with default
    ctx.cores = int(
        config.get(
            "environment",
            "available_cores",
            fallback=defaults["environment"]["available_cores"],
        )
    )
    log.debug(f"set available_cores to {ctx.cores}")

    return ctx
