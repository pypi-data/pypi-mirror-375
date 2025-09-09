import logging
import sys
from pathlib import Path

logger = logging.getLogger(__name__)


def find_job_folder(
    *,
    jobs_base_folder: Path,
    fractal_job_id: int,
) -> Path:
    fractal_job_folders = list(
        item
        for item in jobs_base_folder.glob(
            f"proj_v2_*_job_{fractal_job_id:07d}_*"
        )
        if item.is_dir()
    )
    if len(fractal_job_folders) > 1:
        sys.exit(f"ERROR: Found more than one {fractal_job_folders=}.")
    fractal_job_folder = fractal_job_folders[0]
    logging.debug(
        f"Job folder for {fractal_job_id=}: {fractal_job_folder.as_posix()}."
    )
    return fractal_job_folder


def find_task_subfolders(fractal_job_folder: Path) -> list[Path]:
    task_subfolders = sorted(
        list(item for item in fractal_job_folder.glob("*") if item.is_dir())
    )
    return task_subfolders


def find_slurm_job_ids(task_subfolder: Path) -> list[str]:
    logging.debug(f"Find SLURM job IDs for {task_subfolder.as_posix()}")
    slurm_job_ids_set = set()
    for f in task_subfolder.glob("*.out"):
        # Split both using `_` and `-`, to cover conventions for fractal-server
        # below/above 2.14.0.
        jobid_str = f.with_suffix("").name.split("_")[-1].split("-")[-1]
        # Verify that `jobid_str` can be cast to `int`, and then append it
        int(jobid_str)
        slurm_job_ids_set.add(jobid_str)
    slurm_job_ids_list = sorted(list(slurm_job_ids_set))
    logging.debug(
        f"SLURM job IDs for {task_subfolder.as_posix()}: {slurm_job_ids_list}"
    )
    return slurm_job_ids_list
