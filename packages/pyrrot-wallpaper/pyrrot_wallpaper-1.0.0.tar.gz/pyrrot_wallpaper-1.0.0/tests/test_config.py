"""
This module ensures that the pyrrot_wallpaper.config works as intended.
"""

import unittest

from pyrrot_wallpaper.config import SelectionMode, WallpaperConfig

class TestConfig(unittest.TestCase):
    """
    This class check that the pyrrot_wallpaper.config.WallpaperConfig class works fine.
    """
    
    def test_instanciation_conf_inexist(self):
        """
        This method ensures that the instanciation of a non-existing config file fails.
        """
        
        with self.assertRaises(FileNotFoundError):
            WallpaperConfig(config_file="tests/res/configs/404.conf")

    def test_instanciation_valid_all(self):
        """
        This method ensures that the instantiation of the config valid_all.conf is right.
        """

        valid_wallpaper_config_all = WallpaperConfig(config_file="tests/res/configs/valid_all.conf")
        
        self.assertFalse(valid_wallpaper_config_all.debug)

        self.assertEqual(valid_wallpaper_config_all.selection_mode, SelectionMode.ALL)

        self.assertDictEqual(valid_wallpaper_config_all.music, {
            "directory": "~/Music",
            "albumart_path": "/tmp/cover.png"
        })

        self.assertEqual(valid_wallpaper_config_all.selection_options, {
            "include_tags": ["nature"],
            "include_colours": ["orange"],
            "include_files": [],
            "exclude_tags": [],
            "exclude_colours": [],
            "exclude_files": ["hated_wallpaper.jpg", "bad_wallpaper.png"]
        })

        self.assertDictEqual(valid_wallpaper_config_all.theme, {
            "do_update_theme": True,
            "use_static_theme": True,
            "default_theme": "base16-dracula",
            "powerline_colours": "~/scripts/wallpaper/powerline-color.sh"
        })
    
    def test_instanciation_valid_selection(self):
        """
        This method ensure that the instantiation of the config valid_selection.conf is right.
        """
        
        valid_wallpaper_config_all = WallpaperConfig(config_file="tests/res/configs/valid_selection.conf")
        
        self.assertTrue(valid_wallpaper_config_all.debug)

        self.assertEqual(valid_wallpaper_config_all.selection_mode, SelectionMode.SELECTION)

        self.assertDictEqual(valid_wallpaper_config_all.music, {
            "directory": "~/Musique",
            "albumart_path": "/tmp/cover.jpg"
        })

        self.assertEqual(valid_wallpaper_config_all.selection_options, {
            "include_tags": [],
            "include_colours": [],
            "include_files": ["cool_wallpaper.jpg"],
            "exclude_tags": ["photo", "cat"],
            "exclude_colours": ["white"],
            "exclude_files": []
        })

        self.assertDictEqual(valid_wallpaper_config_all.theme, {
            "do_update_theme": False,
            "use_static_theme": False,
            "default_theme": "",
            "powerline_colours": "~/scripts/wallpaper/powerline-color.sh"
        })
