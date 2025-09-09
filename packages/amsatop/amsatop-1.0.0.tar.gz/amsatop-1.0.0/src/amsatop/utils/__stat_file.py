import logging
from dataclasses import dataclass


@dataclass(frozen=True)
class StatFile:
    """
    Represents key fields from a process's or thread /proc/[pid or tgid]/stat file.
    """
    pid: int
    command: str        # Filename of the executable (in parentheses)
    state: str          # Process state
    ppid: int           # Parent PID
    pgrp: int           # Process group ID
    session: int        # Session ID
    tty_nr: int         # Controlling terminal
    tpgid: int          # Foreground process group ID
    flags: int          # Kernel flags
    minflt: int         # Minor faults
    cminflt: int        # Minor faults with children
    majflt: int         # Major faults
    cmajflt: int        # Major faults with children
    utime: int          # User mode jiffies
    stime: int          # Kernel mode jiffies
    cutime: int         # User mode jiffies with children
    cstime: int         # Kernel mode jiffies with children
    priority: int       # Priority value
    nice: int           # Nice value
    num_threads: int    # Number of threads
    starttime: int      # Start time since boot (in jiffies)

    @classmethod
    def from_stat_line(cls, line: str) -> "StatFile":
        """
        Get a StatFile from the lines of the file
        :meta private:
        """
        first_paren = line.find('(')
        last_paren = line.rfind(')')
        if first_paren == -1 or last_paren == -1:
            raise ValueError("Malformed stat line: missing parentheses around command")
        before = line[:first_paren].strip()
        command = line[first_paren + 1:last_paren]
        after = line[last_paren + 1:].strip()
        fields = before.split() + [command] + after.split()
        if len(fields) < 22:
            raise ValueError("Malformed stat line: insufficient fields")

        return StatFile(
            pid=int(fields[0]),
            command=fields[1],
            state=fields[2],
            ppid=int(fields[3]),
            pgrp=int(fields[4]),
            session=int(fields[5]),
            tty_nr=int(fields[6]),
            tpgid=int(fields[7]),
            flags=int(fields[8]),
            minflt=int(fields[9]),
            cminflt=int(fields[10]),
            majflt=int(fields[11]),
            cmajflt=int(fields[12]),
            utime=int(fields[13]),
            stime=int(fields[14]),
            cutime=int(fields[15]),
            cstime=int(fields[16]),
            priority=int(fields[17]),
            nice=int(fields[18]),
            num_threads=int(fields[19]),
            starttime=int(fields[21]),
        )


def get_stat_file_from_path(path: str) -> StatFile | None:
    """
    Given a path, returns a StatFile, which can be useful for analyzing a process or thread.

    :param path: path to the stat file (will be usually in the form of /proc/[pid or tgid]/stat
    :returns: StatFile or None if the path doesn't exist.
    :raises: ValueError if the path isn't valid.
    """
    if not path.endswith("/stat"):
        raise ValueError(f"Stat file, should end with /stat......")

    try:
        with open(path, "r", encoding="utf-8") as f:
            line = f.readline()
            return StatFile.from_stat_line(line)
    except FileNotFoundError:
        return None
    except Exception as e:
        logging.error(
            "Unhandled error in amsatop library (not your solution), please report to the instructors: %s",
            e
        )
        return None