"""
This module tests the module pyrrot_wallpaper.wallpaper_setter for errors, using pytest.
"""

from os.path import dirname, expanduser
import unittest
from pyrrot_wallpaper.config import WallpaperConfig, SelectionMode

from pyrrot_wallpaper.wallpaper_setter import WallpaperSetter

class TestWallpaperSetter(unittest.TestCase):
    def setUp(self) -> None:
        self.wallpaper_dict = {
            "name": "Hazard Stripes",
            "author": "masuksa",
            "file": "img/hazard-stripes.png",
            "tags": ["test", "workinprogress", "🚧"],
            "colours": ["yellow", "black"]
        }
        self.wallpaper_config = WallpaperConfig("tests/res/configs/valid_all.conf")
        self.wallpaper_setter = WallpaperSetter()
    
    def test_get_wallpaper_full_path(self):
        self.assertEqual(self.wallpaper_setter.get_wallpaper_full_path(self.wallpaper_dict, self.wallpaper_config), "tests/res/img/hazard-stripes.png")
        music_pic = dict()
        self.wallpaper_config.selection_mode = SelectionMode.ALBUMART
        self.assertEqual(self.wallpaper_setter.get_wallpaper_full_path(music_pic, self.wallpaper_config), "/tmp/cover.png")
        self.wallpaper_config.selection_mode = SelectionMode.ALL

    # def test_set_wallpaper(self):
    #     wallpaper_dict_w_full_path = self.wallpaper_dict
    #     wallpaper_dict_w_full_path["file"] = self.wallpaper_setter.get_wallpaper_full_path(self.wallpaper_dict, self.wallpaper_config)
    #     self.wallpaper_setter.set_wallpaper(self.wallpaper_dict)
    #     TODO check that the error is raised when using it wrong

    def test_get_theme(self):
        theme = self.wallpaper_setter.get_theme(self.wallpaper_dict, self.wallpaper_config)
        self.assertEqual(theme, "base16-dracula")
        self.wallpaper_dict["theme"] = "base16-unikitty"
        theme = self.wallpaper_setter.get_theme(self.wallpaper_dict, self.wallpaper_config)
        self.assertEqual(theme, "base16-dracula")
        self.wallpaper_config.theme["use_static_theme"] = False
        theme = self.wallpaper_setter.get_theme(self.wallpaper_dict, self.wallpaper_config)
        self.assertEqual(theme, "base16-unikitty")
        del self.wallpaper_dict["theme"]
        theme = self.wallpaper_setter.get_theme(self.wallpaper_dict, self.wallpaper_config)
        self.assertIsNone(theme)

    # def test_set_theme(self):
    #     wallpaper_path = expanduser(dirname(self.wallpaper_config.metadata_file)) + "/" + self.wallpaper_dict["file"]
    #     # TODO the following doesn't work as the example image is too simple
    #     # self.wallpaper_setter.set_theme(wallpaper_path)
    #     theme = "base16-dracula"
    #     self.wallpaper_setter.set_theme(wallpaper_path, theme=theme)
