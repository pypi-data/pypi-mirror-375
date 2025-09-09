"""
This module manages pyrrot's configuration.
"""

from enum import auto, Enum
from os import path, environ
import configparser
import json

class SelectionMode(Enum):
    """
    SelectionMode represents the different selection choices.
    """
    ALL = auto()
    SELECTION = auto()
    ALBUMART = auto()

class WallpaperConfig():
    """
    This class represents the configuration of pyrrot.
    It handles the various accessible options.
    """

    def __init__(self, config_file=None) -> None:
        self.config_file = config_file or \
            path.join(
                environ.get('XDG_CONFIG_HOME') or
                environ.get('APPDATA') or
                path.join(environ['HOME'], '.config'),
                "pyrrot/pyrrot.config"
            )
        print(self.config_file)
        if not path.exists(config_file):
            raise FileNotFoundError(config_file)
        config = configparser.ConfigParser()
        config.read(config_file)

        self.debug = config["global"]["debug"] == "true"
        selection_mode_possibilities = {
            "all": SelectionMode.ALL,
            "selection": SelectionMode.SELECTION,
            "albumart": SelectionMode.ALBUMART
        }
        if config["global"]["mode"] not in ("all", "selection", "albumart"):
            raise Exception("Error: Mode is wrong ! Must be one of all, selection or albumart.")

        self.selection_mode = selection_mode_possibilities[config["global"]["mode"]]

        self.metadata_file = config["global"]["picture_infos"]

        self.music = {
            "directory": config["music"]["music_dir"],
            "albumart_path": config["music"]["albumart_path"]
        }

        self.selection_options = {
            "include_tags":     [tag.strip() for tag in config["selection_options"]["include_tags"].strip("[]").split(',')],
            "include_colours":  [colour.strip() for colour in config["selection_options"]["include_colours"].strip("[]").split(',')],
            "include_files":    [filename.strip() for filename in config["selection_options"]["include_files"].strip("[]").split(',')],
            "exclude_tags":     [tag.strip() for tag in config["selection_options"]["exclude_tags"].strip("[]").split(',')],
            "exclude_colours":  [colour.strip() for colour in config["selection_options"]["exclude_colours"].strip("[]").split(',')],
            "exclude_files":    [filename.strip() for filename in config["selection_options"]["exclude_files"].strip("[]").split(',')]
        }

        for option_name, option_value in self.selection_options.items():
            if "" in option_value:
                self.selection_options[option_name].remove("")

        if self.debug:
            print(json.dumps(self.selection_options, sort_keys=True, indent=2))

        self.theme = {
            "do_update_theme": config["theme"]["update_theme"] == "true",
            "use_static_theme": config["theme"]["use_static_theme"] == "true",
            "default_theme": config["theme"]["default_theme"],
            "powerline_colours": config["theme"]["powerline_colours"]
        }

        self.monitor = config["global"]["monitor"]

        self.bg_backend = config["global"]["bg_backend"]
