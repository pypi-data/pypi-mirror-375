import pytest
from devtools import debug
from fractal_slurm_tools.parse_sacct_info import get_job_submit_start_end_times


def test_get_job_submit_start_end_times():
    STDOUT = (
        "22496092|__TEST_ECHO_TASK__|u20-cva0000-009||2025-07-22T08:44:09|2025-07-22T08:44:14|2025-07-22T08:44:18|COMPLETED|00:00:04|00:00:04|4|00:00.140|1||||||||||||||||billing=1,cpu=1,mem=2000M,node=1|billing=1,cpu=1,mem=2000M,node=1|standard|normal|sbatch --parsable /shares/prbvc.biovision.uzh/fractal/bvc/proj_v2_0000213_wf_0000243_job_0000538_20250722_064409/0___test_echo_task__/non_par-slurm-submit.sh|/shares/prbvc.biovision.uzh/fractal/bvc/proj_v2_0000213_wf_0000243_job_0000538_20250722_064409/0___test_echo_task__|4\n"
        "22496092.batch|batch|u20-cva0000-009|1|2025-07-22T08:44:14|2025-07-22T08:44:14|2025-07-22T08:44:18|COMPLETED|00:00:04|00:00:04|4|00:00.026|1|0|0|0|0.00M|0.00M|0|1064K|0|1064K|1820K|1820K|0|00:00:00|00:00:00|0||cpu=1,mem=2000M,node=1|||||4\n"
        "22496092.extern|extern|u20-cva0000-009|1|2025-07-22T08:44:14|2025-07-22T08:44:14|2025-07-22T08:44:18|COMPLETED|00:00:04|00:00:04|4|00:00.001|1|0|0|0|0|0|0|0|0|0|0|0|0|00:00:00|00:00:00|0||billing=1,cpu=1,mem=2000M,node=1|||||4\n"
        "22496092.0|python|u20-cva0000-009|1|2025-07-22T08:44:15|2025-07-22T08:44:15|2025-07-22T08:44:17|COMPLETED|00:00:02|00:00:02|2|00:00.113|1|0|0|0|0|0|0|0|0|0|266248K|266248K|0|00:00:00|00:00:00|0||cpu=1,mem=2000M,node=1|||srun --ntasks=1 --cpus-per-task=1 --mem=2000MB /shares/prbvc.biovision.uzh/fractal/bvc/env/bin/python -m fractal_server.app.runner.executors.slurm_common.remote --input-file /shares/prbvc.biovision.uzh/fractal/bvc/proj_v2_0000213_wf_0000243_job_0000538_20250722_064409/0___test_echo_task__/non_par--input.json --output-file /shares/prbvc.biovision.uzh/fractal/bvc/proj_v2_0000213_wf_0000243_job_0000538_20250722_064409/0___test_echo_task__/non_par--output.json||2\n"
    )
    lines = STDOUT.splitlines()

    with pytest.raises(ValueError):
        get_job_submit_start_end_times(
            job_string="9999999",
            sacct_lines=lines,
        )

    job_info = get_job_submit_start_end_times(
        job_string="22496092",
        sacct_lines=lines,
    )
    debug(job_info)
    assert abs(job_info["job_queue_time"] - 5.0) < 1e-10
    assert abs(job_info["job_runtime"] - 4.0) < 1e-10
