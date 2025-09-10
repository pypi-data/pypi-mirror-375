"""
This module tests the module lib.wallpaper_metdata for errors, using pytest.
"""

from json import JSONDecodeError
import unittest
from pyrrot_wallpaper import wallpaper_metadata
from pyrrot_wallpaper.config import SelectionMode, WallpaperConfig

from pyrrot_wallpaper.wallpaper_metadata import WallpaperMetadata

class TestWallpaperMetadata(unittest.TestCase):
    """
    This class tests the function in module lib.wallpaper_metdata.
    """

    def test_instanciation_validation(self):
        """
        This tests the instanciation of WallpaperMetdata and the validation of the metadata.

        :param self:
        """

        with self.assertRaises(JSONDecodeError):
            WallpaperMetadata("tests/res", "tests/res/invalid_json.json")

        with self.assertRaises(Exception, msg="Error: The info file does not contain any image !"):
            WallpaperMetadata("tests/res", "tests/res/invalid_no_picture.json")

        with self.assertRaises(Exception, msg="Error: Picture {str(picture)} has no name !"):
            WallpaperMetadata("tests/res", "tests/res/invalid_miss_image_name.json")

        with self.assertRaises(Exception, msg="Error: Picture \"Hazard Stripes\": no \"file\" is defined !"):
            WallpaperMetadata("tests/res", "tests/res/invalid_no_file_defined.json")

        with self.assertRaises(Exception, msg="Error: Picture \"Hazard Stripes\": file src/tests/res/img/this-file-does-not-exist.png does not exist"):
            WallpaperMetadata("tests/res", "tests/res/invalid_image_file.json")

        wallpaper_metadata = WallpaperMetadata("tests/res", "tests/res/valid_infofile.json")
        self.assertEqual([{
            "name": "Hazard Stripes",
            "author": "masuksa",
            "file": "img/hazard-stripes.png",
            "tags": ["test", "workinprogress", "🚧"],
            "colours": ["yellow", "black"]
        }], wallpaper_metadata.metadata)

    def test_get_wallpapers_with_colours(self):
        """
        """
        wallpaper_metadata = WallpaperMetadata("tests/res", "tests/res/valid_infofile.json")

        self.assertEqual(wallpaper_metadata.get_wallpapers_with_colours(["transparent"]), [])

        self.assertEqual(wallpaper_metadata.get_wallpapers_with_colours(["yellow"]),
        [{
            "name": "Hazard Stripes",
            "author": "masuksa",
            "file": "img/hazard-stripes.png",
            "tags": ["test", "workinprogress", "🚧"],
            "colours": ["yellow", "black"]
        }])

        self.assertEqual(wallpaper_metadata.get_wallpapers_with_colours(["yellow", "black"]),
        [{
            "name": "Hazard Stripes",
            "author": "masuksa",
            "file": "img/hazard-stripes.png",
            "tags": ["test", "workinprogress", "🚧"],
            "colours": ["yellow", "black"]
        }])

    def test_get_wallpapers_with_tags(self):
        """
        """
        wallpaper_metadata = WallpaperMetadata("tests/res", "tests/res/valid_infofile.json")

        self.assertEqual(wallpaper_metadata.get_wallpapers_with_tags(["does-not-exist"]), [])

        self.assertEqual(wallpaper_metadata.get_wallpapers_with_tags(["test"]),
        [{
            "name": "Hazard Stripes",
            "author": "masuksa",
            "file": "img/hazard-stripes.png",
            "tags": ["test", "workinprogress", "🚧"],
            "colours": ["yellow", "black"]
        }])

        self.assertEqual(wallpaper_metadata.get_wallpapers_with_tags(["🚧"]),
        [{
            "name": "Hazard Stripes",
            "author": "masuksa",
            "file": "img/hazard-stripes.png",
            "tags": ["test", "workinprogress", "🚧"],
            "colours": ["yellow", "black"]
        }])

        self.assertEqual(wallpaper_metadata.get_wallpapers_with_tags(["test", "🚧"]),
        [{
            "name": "Hazard Stripes",
            "author": "masuksa",
            "file": "img/hazard-stripes.png",
            "tags": ["test", "workinprogress", "🚧"],
            "colours": ["yellow", "black"]
        }])

    def test_select_wallpaper_config_all(self):
        """
        Test if selecting a wallpaper works fine.
        """
        
        wallpaper_config = WallpaperConfig("tests/res/configs/valid_all.conf")
        wallpaper_metadata = WallpaperMetadata("tests/res", "tests/res/valid_infofile.json")
        wallpaper_result = wallpaper_metadata.wallpaper_selection_list(wallpaper_config)
        self.assertEqual(wallpaper_result, [{
            "name": "Hazard Stripes",
            "author": "masuksa",
            "file": "img/hazard-stripes.png",
            "tags": ["test", "workinprogress", "🚧"],
            "colours": ["yellow", "black"]
        }])
