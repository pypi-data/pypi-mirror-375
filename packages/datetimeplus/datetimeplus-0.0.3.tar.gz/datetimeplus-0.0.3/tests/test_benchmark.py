# mypy: disable-error-code="misc"
from datetime import datetime as base_datetime

import pytest
from pytest_benchmark.fixture import BenchmarkFixture

from core import datetime


class TestBenchmark:
    @pytest.mark.parametrize(
        "dt, fmt",
        [
            (datetime(2023, 1, 1, 12, 3, 45), "%Y/%m/%d %H:%M:%S"),
            (datetime(2023, 1, 1, 12, 3, 45), "%Y/%y/%m/%d %w %H/%I%M%S %j %U %W"),
            (datetime(2023, 1, 1, 12, 3, 45), "%w %H/%I%M%S %j %U %W %E %EN %EY"),
            (
                datetime(2023, 1, 1, 12, 3, 45),
                "%_Y/%_y/%_m/%_d %_w %_H/%_I%_M%_S %_j %_U %_W",
            ),
            (
                datetime(2023, 1, 1, 12, 3, 45),
                "%-Y/%-y/%-m/%-d %-w %-H/%-I%-M%-S %-j %-U %-W",
            ),
        ],
    )
    def test_strftime_custom(
        self, benchmark: BenchmarkFixture, dt: datetime, fmt: str
    ) -> None:
        benchmark(dt.strftime, fmt)

    @pytest.mark.parametrize(
        "dt, fmt",
        [
            (base_datetime(2023, 1, 1, 12, 3, 45), "%Y/%m/%d %H:%M:%S"),
            (base_datetime(2023, 1, 1, 12, 3, 45), "%Y/%y/%m/%d %w %H/%I%M%S %j %U %W"),
        ],
    )
    def test_strftime_base(
        self, benchmark: BenchmarkFixture, dt: base_datetime, fmt: str
    ) -> None:
        benchmark(dt.strftime, fmt)

    @pytest.mark.parametrize(
        "dt_str, fmt",
        [
            ("2023/01/01 12:03:45", "%Y/%m/%d %H:%M:%S"),
            (
                "2023/23/01/01 0 12/120345 001 01 00",
                "%Y/%y/%m/%d %w %H/%I%M%S %j %U %W",
            ),
            ("0 12/120345 001 01 00 R 令和 5", "%w %H/%I%M%S %j %U %W %E %EN %EY"),
            (
                "2023/23/ 1/ 1 0 12/12 345   1  1  0",
                "%_Y/%_y/%_m/%_d %_w %_H/%_I%_M%_S %_j %_U %_W",
            ),
            (
                "2023/23/1/1 0 12/12345 1 1 0",
                "%-Y/%-y/%-m/%-d %-w %-H/%-I%-M%-S %-j %-U %-W",
            ),
        ],
    )
    def test_strptime_custom(
        self, benchmark: BenchmarkFixture, dt_str: str, fmt: str
    ) -> None:
        benchmark(datetime.strptime, dt_str, fmt)

    @pytest.mark.parametrize(
        "dt_str, fmt",
        [
            ("2023/01/01 12:03:45", "%Y/%m/%d %H:%M:%S"),
            (
                "2023/23/01/01 0 12/120345 001 01 00",
                "%Y/%y/%m/%d %w %H/%I%M%S %j %U %W",
            ),
        ],
    )
    def test_strptime_base(
        self, benchmark: BenchmarkFixture, dt_str: str, fmt: str
    ) -> None:
        benchmark(base_datetime.strptime, dt_str, fmt)
