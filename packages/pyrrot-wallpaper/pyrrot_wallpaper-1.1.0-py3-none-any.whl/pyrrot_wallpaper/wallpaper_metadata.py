"""
This module handles wallpaper metadata.
"""

import json
from os.path import exists
from typing import Dict, List, Tuple
import random
from pyrrot_wallpaper.config import SelectionMode, WallpaperConfig


class WallpaperMetadata():
    """
    This class manages Wallpaper metadata
    """

    def __init__(self, image_directory, metdata_file) -> None:
        """
        :param string metadata_file: Path to the metadata json file
        """
        self.image_directory = image_directory
        with open(metdata_file, 'r', encoding="utf-8") as file:
            extracted_metadata = json.loads(file.read())
            self.metadata = extracted_metadata
            metadata_validity = self.is_infofile_valid()
            if not metadata_validity[0]:
                raise Exception(metadata_validity[1])

    def get_wallpapers_with_colours(self, colours: List[str]) -> List[Dict]:
        """
        :param List[str] colours: List of the colours to get
        :return: List of wallpapers with at least a colour in the list colours.
        :rtype: List[Dict]
        """
        res = []
        for pic in self.metadata:
            for colour in pic["colours"]:
                if colour in colours:
                    res.append(pic)
                    break
        return res

    def get_wallpapers_with_tags(self, tags: List[str]) -> List[Dict]:
        """
        :param List[str] tags: List of the tags to get
        :return: List of wallpapers with at least a tag in the list tags.
        :rtype: List[Dict]
        """

        res = []
        for pic in self.metadata:
            for tag in pic["tags"]:
                if tag in tags:
                    res.append(pic)
                    break
        return res

    def is_infofile_valid(self) -> Tuple[bool, str]:
        """The file has been opened with json lib, so we do not need to check
        whether it is a valid json file.
        Two checks are made :
        The first one is that the picture has a name.
        The second one is whether the file truly exists.

        :param dict infos: Metadata about the collection of wallpapers
        :return: (True, "") if the file is valid, else (False, "<Error message>")
        :rtype: Tuple(bool, str)
        """
        if not(isinstance(self.metadata, list)) or len(self.metadata) == 0:
            return False, "Error: The info file does not contain any image !"
        for picture in self.metadata:
            if not "name" in picture:
                return False, f"Error: Picture {str(picture)} has no name !"
            if "file" not in picture:
                return False, f"Error: Picture \"{picture['name']}\": no \"file\" is defined !"
            imagefile = self.image_directory + "/" + picture["file"]
            if not exists(imagefile):
                return False, \
                f"Error: Picture \"{picture['name']}\": file {imagefile} does not exist"
        return True, ""

    def wallpaper_selection_list(self, wallpaper_config: WallpaperConfig) -> List:
        """
        :param selection_mode: Selection mode
        :param wallpaper_config: Wallpaper configuration
        :return: A list of the usable dictionaries
        :rtype: List
        """
        selected_pictures = []

        if wallpaper_config.selection_mode != SelectionMode.SELECTION:
            return self.metadata

        for pic in self.metadata:
            excluded = False
            for tag in wallpaper_config.selection_options["exclude_tags"]:
                if tag in pic["tags"]:
                    excluded = True
                    break
            for colour in wallpaper_config.selection_options["exclude_colours"]:
                if colour in pic["colours"]:
                    excluded = True
                    break
            for file in wallpaper_config.selection_options["exclude_files"]:
                if file in pic["file"]:
                    excluded = True
                    break
            if not excluded:
                if len(wallpaper_config.selection_options["include_tags"]) == 0:
                    selected_pictures.append(pic)
                else:
                    for tag in pic["tags"]:
                        if tag in wallpaper_config.selection_options["include_tags"] \
                            and pic not in selected_pictures:
                            selected_pictures.append(pic)
                            break
                if len(wallpaper_config.selection_options["include_colours"]) > 0:
                    selected_pictures.append(pic)
                else:
                    for colour in pic["colours"]:
                        if colour in wallpaper_config.selection_options["include_colours"] \
                            and pic not in selected_pictures:
                            selected_pictures.append(pic)
                            break
                if len(wallpaper_config.selection_options["include_files"]) > 0:
                    selected_pictures.append(pic)
                else:
                    if pic["file"] in wallpaper_config.selection_options["include_files"] \
                        and pic not in selected_pictures:
                        selected_pictures.append(pic)
        return selected_pictures

    def select_single_wallpaper(self, wallpaper_config: WallpaperConfig, random_seed=None) -> Dict:
        """
        :param WallpaperConfig wallpaper_config:
        :param (int|None) random_seed: Seed for the random generator.
        :return: A single picture, which abides by the selection criteria.
        :rtype: Dict
        """
        random.seed(random_seed)
        selected_pictures = self.wallpaper_selection_list(wallpaper_config)
        if len(selected_pictures) == 0:
            raise Exception("There is no wallpaper matching your criteria.")
        pic = random.choice(selected_pictures)
        print(json.dumps(pic, sort_keys=True, indent=4))
        return pic
