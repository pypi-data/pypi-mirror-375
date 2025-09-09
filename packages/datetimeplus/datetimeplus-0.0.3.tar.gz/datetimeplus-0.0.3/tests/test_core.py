# mypy: disable-error-code="misc"
import pytest

from core import datetime


class TestCore:
    @pytest.mark.parametrize(
        "dt, fmt, expected",
        [
            (
                datetime(2023, 1, 1, 12, 3, 45),
                "%Y/%y/%m/%d %w %H/%I%M%S %j %U %W",
                "2023/23/01/01 0 12/120345 001 01 00",
            ),
            (
                datetime(2023, 1, 1, 12, 3, 45),
                "%w %H/%I%M%S %j %U %W %E %EN %EY",
                "0 12/120345 001 01 00 R 令和 5",
            ),
            (
                datetime(2023, 1, 1, 12, 3, 45),
                "%_Y/%_y/%_m/%_d %_w %_H/%_I%_M%_S %_j %_U %_W",
                "2023/23/ 1/ 1 0 12/12 345   1  1  0",
            ),
            (
                datetime(2023, 1, 1, 12, 3, 45),
                "%_w %_H/%_I%_M%_S %_j %_U %_W %E %EN %_EY",
                "0 12/12 345   1  1  0 R 令和  5",
            ),
            (
                datetime(2023, 1, 1, 12, 3, 45),
                "%-Y/%-y/%-m/%-d %-w %-H/%-I%-M%-S %-j %-U %-W",
                "2023/23/1/1 0 12/12345 1 1 0",
            ),
            (
                datetime(2023, 1, 1, 12, 3, 45),
                "%-w %-H/%-I%-M%-S %-j %-U %-W %E %EN %-EY",
                "0 12/12345 1 1 0 R 令和 5",
            ),
        ],
    )
    def test_strftime(self, dt: datetime, fmt: str, expected: str) -> None:
        assert dt.strftime(fmt) == expected

    @pytest.mark.parametrize(
        "dt_str, fmt, expected_dt",
        [
            (
                "2023/23/01/01 0 12/120345 001 01 00",
                "%Y/%y/%m/%d %w %H/%I%M%S %j %U %W",
                datetime(2023, 1, 1, 12, 3, 45),
            ),
            (
                "0 12/120345 001 01 00 R 令和 5",
                "%w %H/%I%M%S %j %U %W %E %EN %EY",
                datetime(2023, 1, 1, 12, 3, 45),
            ),
            (
                "2023/23/ 1/ 1 0 12/12 345   1  1  0",
                "%_Y/%_y/%_m/%_d %_w %_H/%_I%_M%_S %_j %_U %_W",
                datetime(2023, 1, 1, 12, 3, 45),
            ),
            (
                "0 12/12 345   1  1  0 R 令和  5",
                "%_w %_H/%_I%_M%_S %_j %_U %_W %E %EN %_EY",
                datetime(2023, 1, 1, 12, 3, 45),
            ),
            (
                "2023/23/1/1 0 12/12:345 1 1 0",
                "%-Y/%-y/%-m/%-d %-w %-H/%-I:%-M%-S %-j %-U %-W",
                datetime(2023, 1, 1, 12, 3, 45),
            ),
            (
                "0 12/12:345 1 1 0 R 令和 5",
                "%-w %-H/%-I:%-M%-S %-j %-U %-W %E %EN %-EY",
                datetime(2023, 1, 1, 12, 3, 45),
            ),
        ],
    )
    def test_strptime(self, dt_str: str, fmt: str, expected_dt: datetime) -> None:
        assert datetime.strptime(dt_str, fmt) == expected_dt
