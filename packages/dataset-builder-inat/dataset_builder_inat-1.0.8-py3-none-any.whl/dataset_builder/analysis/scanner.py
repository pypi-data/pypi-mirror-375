import os
from typing import Dict, List, Optional, Tuple
from collections import defaultdict
from dataset_builder.core.log import log
from dataset_builder.core.constants import IGNORE_DIRS
from dataset_builder.core.utility import (
    read_species_from_json,
    SpeciesDict,
)

IMAGE_EXTENSION = '.jpg'


def _is_valid_class_dir(path: str, name: str) -> bool:
    return os.path.isdir(path) and name not in IGNORE_DIRS


def scan_species_list(
    data_path: str, target_classes: Optional[List[str]] = None
) -> Tuple[SpeciesDict, int]:
    """
    Scan directory structure.

    Returns:
        SpeciesDict (Dict[str, list[str]]): Dictionary containing classes as keys and their species as values.
    """

    species_counter = 0
    species_dict = defaultdict(list)
    for class_name in os.listdir(data_path):
        if target_classes and class_name not in target_classes:
            continue

        class_path = os.path.join(data_path, class_name)
        if not _is_valid_class_dir(data_path, class_name):
            continue

        species_dict[class_name] = [
            species
            for species in os.listdir(class_path)
            if os.path.isdir(os.path.join(class_path, species))
        ]
        species_counter += len(species_dict[class_name])

    return species_dict, species_counter


def scan_image_counts(
    data_path: str, target_classes: Optional[List[str]] = None
) -> Dict[str, Dict[str, int]]:
    """
    Counts number of images per species under each class.
    Only image ends with .jpg is counted.

    Returns:
        Dict(str, Dict[str, int]): Dictionary contains class as key, an inner dictionary as values.
        The inner dictionary contains species as keys and their representations as values.
    """
    dataset_props: Dict[str, Dict[str, int]] = defaultdict(dict)
    for class_name in os.listdir(data_path):
        if target_classes and class_name not in target_classes:
            continue

        class_path = os.path.join(data_path, class_name)
        if not _is_valid_class_dir(data_path, class_name):
            continue

        for species in os.listdir(class_path):
            species_path = os.path.join(class_path, species)
            if os.path.isdir(species_path):
                count = sum(
                    1 for f in os.listdir(species_path) if f.lower().endswith(IMAGE_EXTENSION)
                )
                dataset_props[class_name][species] = count
    return dataset_props


def filter_species_from_json(
    json_file_path: str, target_classes: List[str], verbose: bool = False
) -> SpeciesDict:
    """
    Extracts species data from a JSON file, filtering only the specified classes.

    Args:
        json_file_path: Path to the JSON file containing species data.
        target_classes: List of class names to include (e.g.)
        verbose: whether to print the progress to stdout

    Returns:
        SpeciesDict: A dictionary with filtered species data.

    Raises:
        FileNotFoundError: If the file does not exist
        ValueError: If the file does not contain any of the specified classes.
    """
    if not os.path.isfile(json_file_path):
        raise FileNotFoundError(f"Error: File '{json_file_path}' not found.")

    data = read_species_from_json(json_file_path)

    if not (
        isinstance(data, dict) 
        and all(
            isinstance(k, str) and isinstance(v, list) and all(isinstance(s, str) for s in v)
            for k, v in data.items()
        )
    ):
        raise ValueError(f"Invalid JSON structure in {json_file_path}. It should be Dict[str, List[str]]")

    filtered_data: SpeciesDict = {
        class_name: species_list
        for class_name, species_list in data.items()
        if class_name in target_classes
    }

    if not filtered_data:
        raise ValueError(
            f"No matching classes found in {json_file_path}: {target_classes}"
            f"Available classes: {list(data.keys())}"
        )

    total_species = sum(len(species) for species in filtered_data.values())

    log(f"Extracting data from {json_file_path}", verbose)
    log(f"Extracted {total_species} species from {len(filtered_data.keys())} classes: ", verbose)

    for species_class, species in filtered_data.items():
        log(f"Extracted {len(species)} species from {species_class}", verbose=verbose)
    log(str(list(filtered_data.keys())), verbose=verbose)

    return filtered_data
