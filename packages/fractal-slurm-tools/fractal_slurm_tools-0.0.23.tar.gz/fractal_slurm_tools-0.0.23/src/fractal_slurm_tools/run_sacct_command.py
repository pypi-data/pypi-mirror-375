import shlex
import subprocess  # nosec
import sys

from .sacct_fields import DELIMITER
from .sacct_fields import SACCT_FMT


def run_sacct_command(job_string: str) -> str:
    """
    Run the `sacct` command

    Args:
        job_string:
            Either a single SLURM-job ID or a comma-separated list, which is
            then provided to `sacct` option `-j`.

    Returns:
        Standard output of `sacct` command.
    """
    cmd = (
        "sacct "
        f"-j {job_string} "
        "--noheader "
        "--parsable2 "
        f'--format "{SACCT_FMT}" '
        f'--delimiter "{DELIMITER}" '
    )

    res = subprocess.run(  # nosec
        shlex.split(cmd),
        capture_output=True,
        encoding="utf-8",
        check=False,
    )
    if res.returncode != 0:
        print(f"ERROR in running {cmd=}.")
        print(f"STDOUT:\n{res.stdout}")
        print(f"STDERR:\n{res.stderr}")
        sys.exit("Exit.")
    return res.stdout
