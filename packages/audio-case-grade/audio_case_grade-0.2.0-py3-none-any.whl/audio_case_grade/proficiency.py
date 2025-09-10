"""Module to get a student's proficiency"""

from .types import Proficiency


def get_proficiency(lexical_density: float) -> Proficiency:
    """Grade a student's proficiency based on lexical density"""

    if lexical_density >= 40:
        return Proficiency.ADVANCED
    if 30 <= lexical_density < 40:
        return Proficiency.PROFICIENT
    if 20 <= lexical_density < 30:
        return Proficiency.AVERAGE

    return Proficiency.LOW
