import pytest
from devtools import debug
from fractal_slurm_tools.query_user_interval import _get_months_range


def test_unit_get_months_range():

    # Fail 1: invalid MM-YYYY
    with pytest.raises(ValueError) as e:
        _get_months_range("01-2025", "abc")
    debug(e.value)

    with pytest.raises(ValueError) as e:
        _get_months_range("13-2025", "12-2026")
    debug(e.value)

    with pytest.raises(ValueError) as e:
        _get_months_range("01-2025", "14-03-2026")
    debug(e.value)

    with pytest.raises(ValueError) as e:
        _get_months_range("01-2025", "03-26")
    debug(e.value)

    # Fail 2: stop < start
    with pytest.raises(ValueError) as e:
        _get_months_range("01-2025", "12-2024")
    debug(e.value)

    # Same date
    assert _get_months_range("02-2025", "02-2025") == [(2, 2025)]

    # Within a solar year
    assert _get_months_range("02-2025", "08-2025") == [
        (2, 2025),
        (3, 2025),
        (4, 2025),
        (5, 2025),
        (6, 2025),
        (7, 2025),
        (8, 2025),
    ]

    # Across two solar years
    assert _get_months_range("02-2025", "08-2026") == [
        (2, 2025),
        (3, 2025),
        (4, 2025),
        (5, 2025),
        (6, 2025),
        (7, 2025),
        (8, 2025),
        (9, 2025),
        (10, 2025),
        (11, 2025),
        (12, 2025),
        (1, 2026),
        (2, 2026),
        (3, 2026),
        (4, 2026),
        (5, 2026),
        (6, 2026),
        (7, 2026),
        (8, 2026),
    ]

    # Across four solar years
    assert _get_months_range("02-2025", "08-2028") == [
        (2, 2025),
        (3, 2025),
        (4, 2025),
        (5, 2025),
        (6, 2025),
        (7, 2025),
        (8, 2025),
        (9, 2025),
        (10, 2025),
        (11, 2025),
        (12, 2025),
        (1, 2026),
        (2, 2026),
        (3, 2026),
        (4, 2026),
        (5, 2026),
        (6, 2026),
        (7, 2026),
        (8, 2026),
        (9, 2026),
        (10, 2026),
        (11, 2026),
        (12, 2026),
        (1, 2027),
        (2, 2027),
        (3, 2027),
        (4, 2027),
        (5, 2027),
        (6, 2027),
        (7, 2027),
        (8, 2027),
        (9, 2027),
        (10, 2027),
        (11, 2027),
        (12, 2027),
        (1, 2028),
        (2, 2028),
        (3, 2028),
        (4, 2028),
        (5, 2028),
        (6, 2028),
        (7, 2028),
        (8, 2028),
    ]
