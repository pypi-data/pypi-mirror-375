import logging
from dataclasses import dataclass, field
from typing import List


@dataclass(frozen=True)
class StatusFile:
    """
    Represents the parsed contents of a `/proc/[pid or tgid]/status` file on a Linux system.
    All fields map to their corresponding values in the status file.
    """
    Name: str
    State: str
    Tgid: int
    Ngid: int
    Pid: int
    PPid: int
    TracerPid: int
    Uid: List[int]
    Gid: List[int]
    FDSize: int
    Groups: List[int] = field(default_factory=list)
    NStgid: int = 0
    NSpid: int = 0
    NSpgid: int = 0
    NSsid: int = 0
    Kthread: int = 0
    VmPeak: int = 0
    VmSize: int = 0
    VmLck: int = 0
    VmPin: int = 0
    VmHWM: int = 0
    VmRSS: int = 0
    RssAnon: int = 0
    RssFile: int = 0
    RssShmem: int = 0
    VmData: int = 0
    VmStk: int = 0
    VmExe: int = 0
    VmLib: int = 0
    VmPTE: int = 0
    VmSwap: int = 0
    HugetlbPages: int = 0
    CoreDumping: int = 0
    THP_enabled: int = 0
    untag_mask: str = ''
    Threads: int = 0
    SigQ: str = ''
    SigPnd: str = ''
    ShdPnd: str = ''
    SigBlk: str = ''
    SigIgn: str = ''
    SigCgt: str = ''
    CapInh: str = ''
    CapPrm: str = ''
    CapEff: str = ''
    CapBnd: str = ''
    CapAmb: str = ''
    NoNewPrivs: int = 0
    Seccomp: int = 0
    Seccomp_filters: int = 0
    Speculation_Store_Bypass: str = ''
    SpeculationIndirectBranch: str = ''
    Cpus_allowed: str = ''
    Cpus_allowed_list: str = ''
    Mems_allowed: str = ''
    Mems_allowed_list: str = ''
    voluntary_ctxt_switches: int = 0
    nonvoluntary_ctxt_switches: int = 0
    x86_Thread_features: str | None = ''
    x86_Thread_features_locked: str | None = ''
    Umask: str | None = None

    @classmethod
    def __from_lines(cls, lines: List[str]) -> "StatusFile":
        def parse_value(key: str, value: str):
            value = value.strip()
            if not value:
                return "" if "x86_Thread" in key else []

            if key in {"Uid", "Gid", "Groups"}:
                return list(map(int, value.split()))

            if key.startswith("Vm") or key in {
                "HugetlbPages", "voluntary_ctxt_switches", "nonvoluntary_ctxt_switches"
            }:
                return int(value.replace("kB", "").strip())

            if key in {
                "Tgid", "Ngid", "Pid", "PPid", "TracerPid", "FDSize", "NStgid",
                "NSpid", "NSpgid", "NSsid", "Kthread", "CoreDumping", "THP_enabled",
                "Threads", "NoNewPrivs", "Seccomp", "Seccomp_filters"
            }:
                return int(value)

            return value

        data = {}
        for line in lines:
            if not line.strip() or ':' not in line or line.strip() == "EOF":
                continue
            key, value = line.split(":", 1)
            field_key = key.strip().replace("-", "_")
            parsed_value = parse_value(key.strip(), value)
            data[field_key] = parsed_value

        return cls(**data)


def get_status_file_from_path(path: str) -> StatusFile | None:
    """
    Given a path, returns a StatusFile, which can be useful for analyzing a process or thread.

    :param path: path to the status file (will be usually in the form of /proc/[pid or tgid]/status
    :returns: StatusFile or None if the path doesn't exist (or other unhandled exception)
    :raises: ValueError if the path isn't valid.
    """
    if not path.endswith("/status"):
        raise ValueError("Status file, should end with /status.....")

    try:
        with open(path, "r", encoding="utf-8") as f:
            return StatusFile.__from_lines(f.readlines())
    except FileNotFoundError:
        return None
    except Exception as e:
        logging.error(
            f"Unexpected error in amsatop library (not caused by this code). "
            f"Please report it to your instructors. Error: {e}"
        )
        return None
