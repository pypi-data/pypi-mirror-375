import json
import logging
import sys
from pathlib import Path
from typing import Any

from .parse_job_folders import find_job_folder
from .parse_job_folders import find_slurm_job_ids
from .parse_job_folders import find_task_subfolders
from .parse_sacct_info import parse_sacct_info

logger = logging.getLogger(__name__)


def process_fractal_job(
    fractal_job_id: int,
    jobs_base_folder: Path,
) -> list[dict[str, Any]]:
    # Find Fractal job folder and subfolders
    fractal_job_folder = find_job_folder(
        jobs_base_folder=jobs_base_folder,
        fractal_job_id=fractal_job_id,
    )
    task_subfolders = find_task_subfolders(fractal_job_folder)

    # Run `sacct` and parse output
    fractal_job_output_rows = []
    for task_subfolder in task_subfolders:
        logging.debug(f"Process task subfolder {task_subfolder.as_posix()}")
        slurm_job_ids = find_slurm_job_ids(task_subfolder)
        for slurm_job_id in slurm_job_ids:
            slurm_job_output_rows = parse_sacct_info(
                slurm_job_id,
                task_subfolder_name=task_subfolder.name,
            )
            fractal_job_output_rows.extend(slurm_job_output_rows)

    return fractal_job_output_rows


def cli_entrypoint(
    *,
    jobs_base_folder: str,
    fractal_job_id: int,
    output_folder: Path,
):
    import pandas as pd

    # Preliminary steps
    if not Path(jobs_base_folder).exists():
        sys.exit(f"ERROR: missing {jobs_base_folder=}.")
    if not output_folder.exists():
        output_folder.mkdir()

    # Process single Fractal job
    fractal_job_output_rows = process_fractal_job(
        fractal_job_id=fractal_job_id,
        jobs_base_folder=Path(jobs_base_folder),
    )
    # Write output to disk
    json_output_file = output_folder / f"out_{fractal_job_id}.json"
    with json_output_file.open("w") as f:
        json.dump(fractal_job_output_rows, f, indent=2)
    csv_output_file = output_folder / f"out_{fractal_job_id}.csv"
    df = pd.read_json(json_output_file)
    df.to_csv(csv_output_file)
