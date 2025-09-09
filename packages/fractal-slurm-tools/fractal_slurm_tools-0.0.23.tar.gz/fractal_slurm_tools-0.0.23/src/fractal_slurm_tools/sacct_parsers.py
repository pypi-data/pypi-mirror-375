from typing import Callable

from fractal_slurm_tools.sacct_parser_functions import _dhhmmss_to_seconds
from fractal_slurm_tools.sacct_parser_functions import _identity
from fractal_slurm_tools.sacct_parser_functions import (
    _str_to_bytes_to_friendly,
)
from fractal_slurm_tools.sacct_parser_functions import _str_to_datetime
from fractal_slurm_tools.sacct_parser_functions import _str_to_float_to_int

from .sacct_fields import SACCT_FIELDS


SACCT_FIELD_PARSERS: dict[str, Callable] = {
    field: _identity for field in SACCT_FIELDS
}

for field in [
    "JobID",
    "NCPUS",
    "NTasks",
    "MinCPUTask",
    "MaxDiskReadTask",
    "MaxDiskWriteTask",
    "MaxPagesTask",
    "MaxRSSTask",
    "MaxVMSizeTask",
    "CPUTimeRaw",
    "ElapsedRaw",
    "NCPUS",
]:
    SACCT_FIELD_PARSERS[field] = _str_to_float_to_int

for field in ["Elapsed", "CPUTime", "MinCPU", "AveCPU"]:
    SACCT_FIELD_PARSERS[field] = _dhhmmss_to_seconds

for field in ["Submit", "Start", "End"]:
    SACCT_FIELD_PARSERS[field] = _str_to_datetime

for field in [
    "MaxDiskWrite",
    "MaxDiskRead",
    "MaxRSS",
    "MaxVMSize",
    "AveDiskWrite",
    "AveDiskRead",
    "AveRSS",
    "AveVMSize",
]:
    SACCT_FIELD_PARSERS[field] = _str_to_bytes_to_friendly
