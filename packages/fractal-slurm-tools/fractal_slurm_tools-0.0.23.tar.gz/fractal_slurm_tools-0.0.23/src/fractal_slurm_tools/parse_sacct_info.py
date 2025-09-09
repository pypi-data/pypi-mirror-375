import logging
import os
from copy import deepcopy
from typing import Any
from typing import Callable
from typing import TypedDict

from .run_sacct_command import run_sacct_command
from .sacct_fields import DELIMITER
from .sacct_fields import SACCT_FIELDS
from .sacct_parser_functions import _isoformat_to_datetime
from .sacct_parsers import SACCT_FIELD_PARSERS

logger = logging.getLogger(__name__)

SLURMTaskInfo = dict[str, Any]

INDEX_JOB_NAME = SACCT_FIELDS.index("JobName")
INDEX_STATE = SACCT_FIELDS.index("State")
INDEX_JOB_ID = SACCT_FIELDS.index("JobID")

INDEX_JOB_SUBMIT = SACCT_FIELDS.index("Submit")
INDEX_JOB_START = SACCT_FIELDS.index("Start")
INDEX_JOB_END = SACCT_FIELDS.index("End")

INDEX_REQ_TRES = SACCT_FIELDS.index("ReqTRES")
INDEX_PARTITION = SACCT_FIELDS.index("Partition")
INDEX_QOS = SACCT_FIELDS.index("QOS")
INDEX_WORK_DIR = (
    SACCT_FIELDS.index("WorkDir") if os.getenv("USE_LEGACY_FIELDS") else None
)
SKIPPED_INDICES_FOR_MISSING_VALUES = {
    INDEX_REQ_TRES,
    INDEX_PARTITION,
    INDEX_QOS,
    INDEX_WORK_DIR,
}


class JobSubmitStartEnd(TypedDict):
    job_Submit: str
    job_Start: str
    job_End: str
    job_queue_time: int
    job_runtime: int


def get_job_submit_start_end_times(
    *,
    job_string: str,
    sacct_lines: list[str],
) -> JobSubmitStartEnd:
    for job_id in job_string.split(","):
        try:
            main_job_line = next(
                line
                for line in sacct_lines
                if line.split(DELIMITER)[INDEX_JOB_ID] == job_id
            )

            main_job_line_fields = main_job_line.split(DELIMITER)
            job_Submit = main_job_line_fields[INDEX_JOB_SUBMIT]
            job_Start = main_job_line_fields[INDEX_JOB_START]
            job_End = main_job_line_fields[INDEX_JOB_END]
            if job_Start != "None":
                job_queue_time = (
                    _isoformat_to_datetime(job_Start)
                    - _isoformat_to_datetime(job_Submit)
                ).total_seconds()
                job_runtime = (
                    _isoformat_to_datetime(job_End)
                    - _isoformat_to_datetime(job_Start)
                ).total_seconds()
            else:
                job_queue_time = 0
                job_runtime = 0

            return dict(
                job_Submit=job_Submit,
                job_Start=job_Start,
                job_End=job_End,
                job_queue_time=job_queue_time,
                job_runtime=job_runtime,
            )

        except StopIteration:
            raise ValueError(
                f"Could not find the main job line for {job_id=} in"
                f"\n{sacct_lines}"
            )


def parse_sacct_info(
    job_string: str,
    task_subfolder_name: str | None = None,
    parser_overrides: dict[str, Callable] | None = None,
) -> tuple[list[SLURMTaskInfo], list[dict[str, int]]]:
    """
    Run `sacct` and parse its output

    Args:
        job_string:
            Either a single SLURM-job ID or a comma-separated list, which is
            then provided to `sacct` option `-j`.
        task_subfolder_name:
            Name of task subfolder, which is included in the output.
        parser_overrides:
            Overrides of the parser defined in `SACCT_FIELD_PARSERS`

    Returns:
        List of `SLURMTaskInfo` dictionaries (one per `python` line in
        `sacct` output).
    """
    logger.debug(f"START, with {job_string=}.")

    # Update parsers, if needed
    actual_parsers = deepcopy(SACCT_FIELD_PARSERS)
    actual_parsers.update(parser_overrides or {})

    # Run `sacct` command
    stdout = run_sacct_command(job_string=job_string)
    lines = stdout.splitlines()

    job_info = get_job_submit_start_end_times(
        job_string=job_string,
        sacct_lines=lines,
    )

    list_task_info = []
    missing_values = {}
    for line in lines:
        line_items = line.split(DELIMITER)
        # Skip non-Python steps/tasks
        if "python" not in line_items[INDEX_JOB_NAME]:
            continue
        # Skip running steps
        if line_items[INDEX_STATE] == "RUNNING":
            continue

        # Parse all fields
        try:

            missing_values_count = [
                item.strip()
                for i, item in enumerate(line_items)
                if i not in SKIPPED_INDICES_FOR_MISSING_VALUES
            ].count("")
            if missing_values_count > 0:
                key = line_items[INDEX_JOB_ID].split(".")[0]
                missing_values.setdefault(key, 0)
                missing_values[key] += missing_values_count
            task_info = {
                SACCT_FIELDS[ind]: actual_parsers[SACCT_FIELDS[ind]](item)
                for ind, item in enumerate(line_items)
            }

        except Exception as e:
            logger.error(f"Could not parse {line=}")
            for ind, item in enumerate(line_items):
                logger.error(f"'{SACCT_FIELDS[ind]}' raw item: {item}")
                logger.error(
                    f"'{SACCT_FIELDS[ind]}' parsed item: "
                    f"{actual_parsers[SACCT_FIELDS[ind]](item)}"
                )
            raise e

        # Enrich `sacct` output for single-step lines with job-level info
        task_info.update(job_info)

        # Add task subfolder name to `sacct` info
        if task_subfolder_name is not None:
            task_info.update(dict(task_subfolder=task_subfolder_name))

        list_task_info.append(task_info)

    return list_task_info, missing_values
