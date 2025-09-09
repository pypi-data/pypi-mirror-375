import logging
from datetime import datetime

import humanfriendly

logger = logging.getLogger(__name__)


def _identity(arg: str) -> str:
    return arg


def _str_to_float_to_int(arg: str) -> int:
    if arg.strip() == "":
        return 0
    return int(float(arg))


def _dhhmmss_to_seconds(arg: str) -> int:
    """
    Supports both `HH:MM:SS` and `D-HH:MM:SS`.
    """
    if arg.strip() == "":
        return 0
    if "-" in arg:
        days, hhmmss = arg.split("-")
    else:
        days = "0"
        hhmmss = arg[:]
    hh, mm, ss = hhmmss.split(":")[:]
    return int(days) * 3600 * 24 + int(hh) * 3600 + int(mm) * 60 + int(ss)


def _str_to_datetime(arg: str) -> str:
    return datetime.fromisoformat(arg).isoformat()


def _str_to_bytes(arg: str) -> int:
    if arg.strip() == "":
        return 0
    return humanfriendly.parse_size(arg)


def _str_to_bytes_to_friendly(arg: str) -> str:
    return humanfriendly.format_size(_str_to_bytes(arg))


def _isoformat_to_datetime(arg: str) -> datetime:
    """
    > The output is of the format `YYYY-MM-DDTHH:MM:SS`, unless changed
    > through the `SLURM_TIME_FORMAT` environment variable.
    > (https://slurm.schedmd.com/sacct.html#OPT_End)
    """
    return datetime.fromisoformat(arg)
