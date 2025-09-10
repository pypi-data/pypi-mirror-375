"""Tests for proficiency scale"""

from audio_case_grade import Proficiency, get_proficiency


def test_get_proficiency():
    """Test proficiency scale"""

    test_cases = [
        (45, Proficiency.ADVANCED),
        (40, Proficiency.ADVANCED),
        (35, Proficiency.PROFICIENT),
        (30, Proficiency.PROFICIENT),
        (25, Proficiency.AVERAGE),
        (20, Proficiency.AVERAGE),
        (15, Proficiency.LOW),
        (0, Proficiency.LOW),
    ]

    for lexical_density, expected in test_cases:
        actual = get_proficiency(lexical_density)
        assert actual == expected, f"Failed for {lexical_density}"
