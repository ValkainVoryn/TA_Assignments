# imp
import json
import re
from pathlib import Path

from PIL import Image
# region Functions


def get_images_in_path(src_path: Path) -> list[Path]:
    """
    Searches a list of images that Pillow can process
    :param src_path: root folder to search
    :return: list of image paths
    """
    extensions = Image.registered_extensions().keys()
    l_img_paths:  list[Path] = []
    for path in src_path.rglob("*"):
        if path.suffix.lower() in extensions:
            l_img_paths.append(path)
    return l_img_paths


def parse_name(image_name: str, config: dict) -> tuple[str,str,str,str]:
    """
    breaks up the name in prefix, name, suffix and extensions
    :param image_name: name of img
    :param config:
    :return: tuple
    """
    possible_prefixes = "|".join(config["prefix"]["naming_conventions"])

    pattern = re.compile(rf"^(?:({possible_prefixes})_)?(.+?)_([A-Za-z0-9]+)(\.[^.]+)$")
    match = re.match(pattern, image_name)
    prefix, name, suffix, ext = match.groups()
    prefix = prefix or ""
    return prefix, name, suffix, ext


def process_images(list_image_paths: list[Path], config: dict) -> None:
    """
    process images rename and repack
    :param list_image_paths: paths of image
    :param config: json config file
    :return: None
    """
    print(list_image_paths)
    for img_path in list_image_paths:
        prefix, name, suffix, ext = parse_name(img_path.name, config)

        if suffix in config["suffix"]["Base"]["naming_conventions"]:
            print(f"File is in color: {img_path}")
        elif suffix in config["suffix"]["packing"]["naming_conventions"].keys():
            print(f"File is a channel/grey packed image {img_path}")
        elif suffix in config["suffix"]["packing"]["separate_maps"].keys():
            print(f"Files is an single channel image: {img_path}")
        else:
            print(f"OTHER: File is something else: {img_path}")


def load_json(json_path: str) -> dict | None:
    with open(json_path, "r") as file:
        return json.load(file)

