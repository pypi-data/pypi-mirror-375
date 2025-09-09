from typing import List, Set, Tuple, Optional, Dict

from dataset_builder.core.utility import SpeciesDict


def _aggregate_all_species(species_data: SpeciesDict, target_classes: Optional[List[str]] = None) -> Set[str]:
    """
    Aggregates all species from the provided species data into a set of unique species names.

    Args:
        species_data (SpeciesDict): A dictionary where keys are species classes (str)
            and values are lists of species names (str).

    Returns:
        Set[str]: A set containing all unique species names from the input species data.
    """
    if target_classes is None:
        target_classes = list(species_data.keys())
    species_set = set()
    for species_class, species_list in species_data.items():
        if species_class not in target_classes:
            continue
        species_set.update(species_list)
    return species_set


def _match_and_diff_sets(
    set_1: Set[str], set_2: Set[str]
) -> Tuple[Set[str], Set[str]]:
    """
    Computes the intersection and symmetric difference of two datasets.

    Args:
        set_1: The first set of data
        set_2: The second set of data

    Returns:
        Tuple(Set[str], Set[str]): A tuple containing
            - `matches`: Elements that exist in both sets
            - `not_matches`: Elements that are unique to either sets
    """
    matches = set_1 & set_2
    not_matches = set_1 ^ set_2
    return matches, not_matches


def cross_reference_set(
    species_dict_1: SpeciesDict,
    species_dict_2: SpeciesDict,
    target_classes: List[str],
) -> Tuple[SpeciesDict, int, Dict]:
    """
    Cross-reference two species dataset, identifying matched and unmatched species, and exports
    the results to a JSON file.

    Args:
        species_dict_1: SpeciesDict
        species_dict_2: SpeciesDict

    Returns:
        Tuple[SpeciesDict, int]: A dictionary containing species class as keys and their species
        as values and the total number of matches.
    """

    all_species_set_1 = _aggregate_all_species(species_dict_1, target_classes)
    all_species_set_2 = _aggregate_all_species(species_dict_2, target_classes)
    matches, unmatched = _match_and_diff_sets(
        all_species_set_1, all_species_set_2)
    # Union class to cover all unique classes from both dicts
    all_classes = set(species_dict_1) | set(species_dict_2)
    matched_dict: SpeciesDict = {}
    report = {
        "total_matched": len(matches),
        "total_unmatched": len(unmatched),
        "class_comparison": {},
    }

    for class_name in all_classes:
        if class_name not in target_classes:
            continue
        class_species_set_1 = set(species_dict_1.get(class_name, []))
        class_species_set_2 = set(species_dict_2.get(class_name, []))
        matched_species = class_species_set_1 & class_species_set_2
        not_matched_species = (class_species_set_1 | class_species_set_2) - matched_species

        matched_dict[class_name] = sorted(list(matched_species))

        report["class_comparison"][class_name] = {  # type: ignore
            "matched": sorted(matched_species),
            "unmatched": sorted(not_matched_species),
        }

    return matched_dict, len(matches), report