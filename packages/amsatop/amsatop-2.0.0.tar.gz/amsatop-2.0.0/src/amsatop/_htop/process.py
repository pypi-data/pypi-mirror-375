from dataclasses import dataclass
from enum import Enum


class TaskType(Enum):
    """
    Enumeration of tasks types.
    """

    PROCESS = "process"
    THREAD = "thread"
    KTHREAD = "kthread"


@dataclass(frozen=True)
class Process:
    """
    Immutable data class representing a system process.

    :param pid: The unique process ID.
    :type pid: int

    :param command: The command or executable that launched the process.
    :type command: str

    :param type: The type of the process
    :type type: TaskType

    :param priority: The scheduling priority of the process.
                     Can be None if unavailable or you're doing Prac-2.1 .
    :type priority: int | None
    """

    pid: int
    command: str
    type: TaskType
    priority: int | None
