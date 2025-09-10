#! /usr/bin/python
"""
This is the main script that pyrrot should launch.

It is currently in the process of being cleaned and refactored.
"""

## TODO
#
# * If the song is paused (for more than x seconds), use a "normal" wallpaper
# * CONFIG_FILE override

import sys
from os.path import expanduser, dirname

from pyrrot_wallpaper.wallpaper_metadata import WallpaperMetadata
from pyrrot_wallpaper.config import SelectionMode, WallpaperConfig
from pyrrot_wallpaper.wallpaper_setter import WallpaperSetter

def main():
    wallpaper_config = WallpaperConfig(expanduser("~") + "/.config/pyrrot/pyrrot.config")

    if wallpaper_config.debug:
        print(f"Mode: {wallpaper_config.selection_mode}")

    wallpaperMetdata = WallpaperMetadata(
        expanduser(dirname(wallpaper_config.metadata_file)),
        expanduser(wallpaper_config.metadata_file)
        )

    """
    # TODO : use argparse or something like this
    flag_tags = False
    flag_pinfo = False
    flag_ptags = False
    for arg in sys.argv:
        if flag_tags:
            TAGS = arg.split(',')
            for i in range(len(TAGS)):
                TAGS[i] = TAGS[i].strip(' ')
            flag_tags = False
        if arg == "--tags":
            flag_tags = True
        if arg == "--pinfos":
            flag_pinfo = True
        if arg == "--ptags":
            flag_ptags = True
        if arg == "--albumart":
            USE_ALBUMART = True

    if flag_ptags:
        all_tags = print_all_tags(infos)
        all_tags.sort()
        for t in all_tags:
            print(t)
    elif flag_pinfo:
        print(TAGS)
        for pic in get_wallpapers_with_tags(infos):
            print(pic["name"])
    elif USE_ALBUMART:
        pic = {}
        set_wallpaper(pic);
    else:
        set_wallpaper(select_wallpaper(infos))
    """
    wallpaper_setter = WallpaperSetter()
    if wallpaper_config.selection_mode == SelectionMode.ALBUMART:
        pic = {}
    else:
        pic = wallpaperMetdata.select_single_wallpaper(wallpaper_config)
    pic["file"] = wallpaper_setter.get_wallpaper_full_path(pic, wallpaper_config)
    wallpaper_setter.set_wallpaper(pic, monitor=wallpaper_config.monitor, backend=wallpaper_config.bg_backend, options=wallpaper_config.bg_backend_options)
    if wallpaper_config.theme["do_update_theme"]:
        wallpaper_setter.set_theme(pic["file"],
            theme=wallpaper_setter.get_theme(pic, wallpaper_config))


if __name__ == '__main__':
    sys.exit(main())
