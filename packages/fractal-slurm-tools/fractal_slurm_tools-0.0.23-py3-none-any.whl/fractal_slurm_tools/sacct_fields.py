import os

SACCT_FIELDS: list[str] = [
    "JobID",
    "JobName",
    "NodeList",
    "NTasks",
    "Submit",
    "Start",
    "End",
    "State",
    "Elapsed",
    "CPUTime",
    "CPUTimeRaw",
    "TotalCPU",
    "NCPUS",
    "MaxDiskRead",
    "AveDiskRead",
    "MaxDiskReadTask",
    "MaxDiskWrite",
    "AveDiskWrite",
    "MaxDiskWriteTask",
    "MaxRSS",
    "MaxRSSTask",
    "AveRSS",
    "MaxVMSize",
    "AveVMSize",
    "MaxVMSizeTask",
    "AveCPU",
    "MinCPU",
    "MinCPUTask",
    "ReqTRES",
    "AllocTRES",
    "Partition",
    "QOS",
    "SubmitLine",
    "WorkDir",
    "ElapsedRaw",
]

if os.getenv("USE_LEGACY_SLURM_FIELDS") is not None:
    # Expose legacy mode, which works with slurm 15.08.7
    SACCT_FIELDS.pop(SACCT_FIELDS.index("SubmitLine"))
    SACCT_FIELDS.pop(SACCT_FIELDS.index("WorkDir"))
    SACCT_FIELDS.pop(SACCT_FIELDS.index("ElapsedRaw"))


SACCT_FIELDS_PERCENT: list[str] = []
for field in SACCT_FIELDS:
    mod_field = field
    if field == "JobName":
        mod_field = f"{field}%30"
    if "TRES" in field:
        mod_field = f"{field}%40"
    SACCT_FIELDS_PERCENT.append(mod_field)

SACCT_FIELDS = [item.split("%")[0] for item in SACCT_FIELDS_PERCENT]
SACCT_FMT: str = ",".join(SACCT_FIELDS_PERCENT)
DELIMITER: str = "|"
