"""
This module handles the setting of a wallpaper.
"""

from os.path import dirname, expanduser
import subprocess
import pywal

from pyrrot_wallpaper.config import SelectionMode,WallpaperConfig

class WallpaperSetter():
    """
    This class manages the setting of a wallpaper.
    """

    def __init__(self) -> None:
        pass

    def get_wallpaper_full_path(self, wallpaper_dict: dict, wallpaper_config: WallpaperConfig) \
         -> str:
        """
        :param Dict wallpaper_dict: Wallpaper dictionary, with the "file" key either non-existent
        or containing the path relative to the metadata file
        : param WallpaperConfig wallpaper_config: Pyrrot configuration
        :return: Full path to the image
        :rtype: str
        """
        if wallpaper_config.selection_mode == SelectionMode.ALBUMART:
            fullpath = expanduser(wallpaper_config.music["albumart_path"])
        else:
            fullpath = expanduser(dirname(wallpaper_config.metadata_file)) + "/" \
                + wallpaper_dict["file"]
        return fullpath

    def set_wallpaper(self, wallpaper_dict: dict, backend: str="swaymsg", monitor: str="eDP-1", options: tuple=("fill",)) -> None:
        """
        Sets the wallpaper given in wallpaper_dict, according to the options in wallpaper_config,
        using feh.
        :param Dict wallpaper_dict: Wallpaper dictionary, with "file" containing the full path
        :param tuple feh_options: list of arguments to be supplied to feh
        """
        # feh is used, and not pywal.wallpaper.change() as the latter doesn't support feh arguments
        if backend == "feh":
            subprocess.run(["feh", wallpaper_dict["file"]] + list(options), check=True)
        else:
            subprocess.run(["swaymsg", "output", monitor, "bg", wallpaper_dict["file"]] + list(options), capture_output=True, check=True)

    def get_theme(self, wallpaper_dict: dict, wallpaper_config: WallpaperConfig):
        """
        Get the theme name.

        :param Dict wallpaper_dict: The object describing a wallpaper
        :param WallpaperConfig wallpaper_config: wallpaper configuration
        :return: The name of the theme, compatible with `wal --theme`
        :rtype: str
        """
        if wallpaper_config.theme["use_static_theme"]:
            theme = wallpaper_config.theme["default_theme"]
        else:
            theme = wallpaper_dict["theme"] if "theme" in wallpaper_dict else None
        return theme

    def set_theme(self, wallpaper_path: str, theme: str=None):
        """
        Set the theme

        :param str wallpaper_path: Path to the wallpaper. This is the final path, and no prefix
        will be added, contrary to what may be store in the objects of the metadata files.
        :param str theme: Name of the theme, compatible with `wal --theme`.
        """
        if theme is not None:
            colors = pywal.theme.file(theme)
        else:
            # bug when for covers, see https://github.com/dylanaraps/pywal/issues/429
            # cache is not reset, so we have to do it by hand first - SHOULD BE FIXED
            # (require test)
            # The two lines below do the following : wal -c
            #scheme_dir = os.path.join(CACHE_DIR, "schemes")
            #shutil.rmtree(scheme_dir, ignore_errors=True)
            colors = pywal.colors.get(wallpaper_path)
        pywal.sequences.send(colors, vte_fix=True)
        pywal.export.every(colors)
        pywal.reload.env()
        # fixing powerline colors
        # subprocess.run([abspath(expanduser(wallpaper_config.theme["powerline_colours"]))],
        # check=True)
        
