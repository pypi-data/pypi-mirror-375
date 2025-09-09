import os
import re
from datetime import date as base_date, datetime as base_datetime
from functools import lru_cache
from typing import Any, Callable, Self, override

# 和暦定義（start_date, era_name, short_name）
WAREKI_ERAS: dict[str, tuple[base_date, str]] = {
    "R": (base_date(2019, 5, 1), "令和"),
    "H": (base_date(1989, 1, 8), "平成"),
    "S": (base_date(1926, 12, 25), "昭和"),
    "T": (base_date(1912, 7, 30), "大正"),
    "M": (base_date(1868, 1, 25), "明治"),
}


NAME_TO_START: dict[str, base_date] = {v[1]: v[0] for v in WAREKI_ERAS.values()}
ABBR_TO_START: dict[str, base_date] = {k: v[0] for k, v in WAREKI_ERAS.items()}


def to_wareki(date: base_date, format: str) -> str | None:
    """和暦フォーマット変換.

    Parameters
    ----------
    date : base_date
        変換対象の日付
    format : str
        フォーマット指定子

    Returns
    -------
    str | None
        変換された和暦文字列またはNone
    """
    for k, (start, _) in WAREKI_ERAS.items():
        if date >= start:
            match format:
                case "EN":
                    return WAREKI_ERAS[k][1]
                case "EY":
                    return str(date.year - start.year + 1)
                case "E":
                    return k
    return None


REPLACEMENTS: dict[str, Callable[[base_datetime], str]] = {
    "EN": lambda m: to_wareki(date=m.date(), format="EN") or "",
    "EY": lambda m: to_wareki(date=m.date(), format="EY") or "",
    "E": lambda m: to_wareki(date=m.date(), format="E") or "",
}


def to_halfwidth_digits(s: str) -> str:
    """
    全角数字→半角

    Parameters
    ----------
    s : str
        全角数字

    Returns
    -------
    str
        変換された半角文字列
    """
    table = {ord(f): ord("0") + i for i, f in enumerate("０１２３４５６７８９")}
    return s.translate(table)


def build_wareki_regex(fmt: str) -> tuple[re.Pattern[str], list[tuple[str, str]]]:
    """
    fmtを正規表現に変換

    Parameters
    ----------
    fmt : str
        フォーマット文字列

    Returns
    -------
    tuple[re.Pattern, list[tuple[str, str]]]
        正規表現 + [("EN","era_name1"), ("EY","era_year1"), ...] の対応リスト
    """
    pat = re.escape(fmt)
    tokens: list[tuple[str, str]] = []
    counter = {"EN": 0, "E": 0, "EY": 0}

    def repl_EN(_: Any) -> str:
        counter["EN"] += 1
        name = f"era_name{counter['EN']}"
        tokens.append(("EN", name))
        return f"(?P<{name}>" + "|".join(map(re.escape, NAME_TO_START)) + ")"

    def repl_E(_: Any) -> str:
        counter["E"] += 1
        name = f"era_abbr{counter['E']}"
        tokens.append(("E", name))
        return f"(?P<{name}>" + "|".join(map(re.escape, ABBR_TO_START)) + ")"

    def repl_EY(_: Any) -> str:
        counter["EY"] += 1
        name = f"era_year{counter['EY']}"
        tokens.append(("EY", name))
        return f"(?P<{name}>元|[0-9０-９]+)"

    pat = re.sub(r"%EN", repl_EN, pat)
    pat = re.sub(r"(?<!%)%E(?!Y)", repl_E, pat)
    pat = re.sub(r"%EY", repl_EY, pat)
    pat = re.sub(r"%[A-Za-z]", r".+?", pat)

    return re.compile("^" + pat + "$"), tokens


_STRPTIME_REGEX_MAP = {
    "Y": r"\d{4}",
    "y": r"\d{2}",
    "m": r"0[1-9]|1[0-2]",
    "d": r"0[1-9]|[12]\d|3[01]",
    "H": r"[01]\d|2[0-3]",
    "I": r"0[1-9]|1[0-2]",
    "M": r"[0-5]\d",
    "S": r"[0-5]\d",
    "j": r"00[1-9]|0[1-9]\d|[12]\d{2}|3[0-5]\d|36[0-6]",
    "w": r"[0-6]",
    "U": r"[0-5]\d",
    "W": r"[0-5]\d",
    "p": r"AM|PM",
    "%": r"%",
    "_Y": r"\s{3}\d|\s{2}\d{2}|\s\d{3}|\d{4}",
    "_y": r"\s\d|\d{2}",
    "_m": r"\s[1-9]|1[0-2]",
    "_d": r"\s[1-9]|[12]\d|3[01]",
    "_H": r"\s\d|1\d|2[0-3]",
    "_I": r"\s[1-9]|1[0-2]",
    "_M": r"\s\d|[0-5]\d",
    "_S": r"\s\d|[0-5]\d",
    "_j": r"\s{2}[1-9]|\s{1}[1-9]\d|[12]\d{2}|3[0-5]\d|36[0-6]",
    "_w": r"[0-6]",
    "_U": r"\s\d|[0-5]\d",
    "_W": r"\s\d|[0-5]\d",
    "EN": "|".join(map(re.escape, NAME_TO_START)),
    "E": "|".join(map(re.escape, ABBR_TO_START)),
    "EY": r"元|[0-9０-９]+",
    "_EY": r"\s\d|\d{2}",
    "-Y": r"\d{1,4}",
    "-y": r"\d{1,2}",
    "-m": r"[1-9]|1[0-2]",
    "-d": r"[1-9]|[12]\d|3[01]",
    "-H": r"\d|1\d|2[0-3]",
    "-I": r"[1-9]|1[0-2]",
    "-M": r"\d|[0-5]\d",
    "-S": r"\d|[0-5]\d",
    "-j": r"[1-9]|[1-9]\d|[12]\d{2}|3[0-5]\d|36[0-6]",
    "-w": r"[0-6]",
    "-U": r"\d|[0-5]\d",
    "-W": r"\d|[0-5]\d",
    "-EY": r"\d|\d{2}",
}

_STRPTIME_DIRECTIVE_RE = re.compile(
    r"%(?:(EN)|([_-])?(EY)|(E)|([_-])?([YymdWHIMSjUwpa%]))"
)


@lru_cache(maxsize=128)
def _build_strptime_info(
    format: str,
) -> tuple[re.Pattern[str], list[dict[str, str]]]:
    """Build regex pattern and token list from format string."""
    pattern = ""
    last_pos = 0
    tokens = []
    group_counters: dict[str, int] = {}

    for m in _STRPTIME_DIRECTIVE_RE.finditer(format):
        pattern += re.escape(format[last_pos : m.start()])
        last_pos = m.end()

        m_groups = m.groups()
        code_en = m_groups[0]
        is_padded_ey = m_groups[1]
        code_ey = m_groups[2]
        code_e = m_groups[3]
        is_padded_other = m_groups[4]
        code_other = m_groups[5]

        if code_en:
            key = "EN"
        elif code_ey:
            key = f"{is_padded_ey or ''}EY"
        elif code_e:
            key = "E"
        elif code_other == "%":
            pattern += "%"
            continue
        elif code_other:
            key = f"{is_padded_other or ''}{code_other}"
        else:
            continue

        group_counters[key] = group_counters.get(key, 0) + 1
        group_name = f"{key}_{group_counters[key]}".replace("-", "hyphen")
        pattern += f"(?P<{group_name}>{_STRPTIME_REGEX_MAP[key]})"
        tokens.append({"kind": key, "gname": group_name})

    pattern += re.escape(format[last_pos:])
    pattern = f"^{pattern}$"
    return re.compile(pattern), tokens


class datetime(base_datetime):
    """extended datetime class"""

    @override
    def strftime(self, format: str) -> str:
        """Strftime with wareki and padding support.

        Parameters
        ----------
        format : str
            The format string.

        Returns
        -------
        str
            The formatted datetime string.
        """

        def _handle_padding(m: re.Match[str]) -> str:
            specifier = m.group(2)

            if specifier == "EY":
                unpadded_val = to_wareki(self.date(), "EY") or ""
            else:
                unpadded_val = super(datetime, self).strftime(
                    f"%{'#' if os.name == 'nt' else '-'}{specifier}"
                )

            if m.group(1) == "-":
                return unpadded_val

            padding_map = {
                "d": 2,
                "m": 2,
                "H": 2,
                "I": 2,
                "M": 2,
                "S": 2,
                "U": 2,
                "W": 2,
                "y": 2,
                "w": 1,
                "j": 3,
                "Y": 4,
                "EY": 2,
            }
            width = padding_map.get(specifier)
            if not width:
                return m.group(0)

            return unpadded_val.rjust(width)

        format = re.sub(r"%([_-])([YymdWHIMSjUw]|EY)", _handle_padding, format)

        masked_format = re.sub(
            pattern=r"%(EN|EY|E)",
            repl=lambda m: REPLACEMENTS[m.group(1)](self),
            string=format,
        )

        return super().strftime(masked_format)

    @override
    @classmethod
    def strptime(cls, date_string: str, format: str) -> Self:
        """Strptime with wareki and padding support."""
        compiled_regex, tokens = _build_strptime_info(format)
        match = compiled_regex.match(date_string)
        if not match:
            msg = f"time data '{date_string}' does not match format '{format}'"
            raise ValueError(msg)

        groups = match.groupdict()
        data: dict[str, Any] = {}

        for i, token in enumerate(tokens):
            if token["kind"] in ("EN", "E"):
                if i + 1 < len(tokens) and tokens[i + 1]["kind"] in (
                    "EY",
                    "_EY",
                    "-EY",
                ):
                    era_gname, year_gname = token["gname"], tokens[i + 1]["gname"]
                    if era_gname in groups and year_gname in groups:
                        era_txt = groups.pop(era_gname)
                        year_txt = groups.pop(year_gname)
                        year_val = (
                            1
                            if year_txt == "元"
                            else int(to_halfwidth_digits(year_txt.strip()))
                        )
                        start_date = (
                            NAME_TO_START[era_txt]
                            if token["kind"] == "EN"
                            else ABBR_TO_START[era_txt]
                        )
                        data["year"] = start_date.year + year_val - 1

        for gname, value in groups.items():
            kind, _ = gname.rsplit("_", 1)
            kind = kind.replace("hyphen", "-")
            value = value.strip()
            if kind in ("Y", "_Y", "-Y"):
                data["year"] = int(value)
            elif kind in ("y", "_y", "-y"):
                year = int(value)
                data["year"] = 1900 + year if year >= 69 else 2000 + year
            elif kind in ("m", "_m", "-m"):
                data["month"] = int(value)
            elif kind in ("d", "_d", "-d"):
                data["day"] = int(value)
            elif kind in ("H", "_H", "-H", "I", "_I", "-I"):
                data["hour"] = int(value)
            elif kind in ("M", "_M", "-M"):
                data["minute"] = int(value)
            elif kind in ("S", "_S", "-S"):
                data["second"] = int(value)

        if "p_1" in groups and "hour" in data:
            if groups["p_1"].upper() == "PM" and data["hour"] < 12:
                data["hour"] += 12
            elif groups["p_1"].upper() == "AM" and data["hour"] == 12:
                data["hour"] = 0

        defaults = {
            "year": 1900,
            "month": 1,
            "day": 1,
            "hour": 0,
            "minute": 0,
            "second": 0,
        }
        final_data = {**defaults, **data}
        return cls(
            final_data["year"],
            final_data["month"],
            final_data["day"],
            final_data["hour"],
            final_data["minute"],
            final_data["second"],
        )
