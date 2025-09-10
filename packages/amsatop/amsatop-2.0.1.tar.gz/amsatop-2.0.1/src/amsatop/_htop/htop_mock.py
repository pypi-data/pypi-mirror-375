import random
from typing import override

from amsatop._htop.htop import Htop
from amsatop._htop.process import Process, TaskType


class HtopMock(Htop):
    """
    Mock implementation of the Htop interface for testing or demonstration purposes.

    This class simulates process information by returning hardcoded `Process` instances.
    Each method (`get_processes`, `get_priorities`, `get_hup`) returns a random subset
    of predefined mock processes.

    Useful for testing code that depends on Htop without requiring access to the actual
    system process tree.
    """

    RETURN_PROCESSES = 5

    @override
    def get_processes(self) -> list[Process]:
        not_real_processes = [
            Process(pid=1, command="init", type=TaskType.PROCESS, priority=None),
            Process(pid=2, command="bash", type=TaskType.THREAD, priority=None),
            Process(pid=3, command="kworker", type=TaskType.KTHREAD, priority=None),
            Process(pid=4, command="python", type=TaskType.PROCESS, priority=None),
            Process(pid=5, command="top", type=TaskType.THREAD, priority=None),
            Process(pid=6, command="_htop", type=TaskType.PROCESS, priority=None),
            Process(pid=7, command="systemd", type=TaskType.KTHREAD, priority=None),
            Process(pid=8, command="tmux", type=TaskType.THREAD, priority=None),
            Process(pid=9, command="node", type=TaskType.PROCESS, priority=None),
            Process(pid=10, command="java", type=TaskType.KTHREAD, priority=None),
            Process(pid=11, command="emacs", type=TaskType.THREAD, priority=None),
            Process(pid=12, command="vim", type=TaskType.PROCESS, priority=None),
            Process(pid=13, command="zsh", type=TaskType.THREAD, priority=None),
            Process(pid=14, command="docker", type=TaskType.KTHREAD, priority=None),
        ]
        return random.sample(
            not_real_processes, min(self.RETURN_PROCESSES, len(not_real_processes))
        )

    @override
    def get_priorities(self) -> list[Process]:
        not_real_processes = [
            Process(pid=15, command="sshd", type=TaskType.PROCESS, priority=10),
            Process(pid=16, command="nginx", type=TaskType.THREAD, priority=5),
            Process(pid=17, command="postgres", type=TaskType.KTHREAD, priority=1),
            Process(pid=18, command="redis", type=TaskType.PROCESS, priority=7),
            Process(pid=19, command="chrome", type=TaskType.THREAD, priority=8),
            Process(pid=20, command="firefox", type=TaskType.PROCESS, priority=6),
            Process(pid=21, command="docker", type=TaskType.KTHREAD, priority=3),
            Process(pid=22, command="mysql", type=TaskType.PROCESS, priority=9),
            Process(pid=23, command="emacs", type=TaskType.THREAD, priority=4),
            Process(pid=24, command="vim", type=TaskType.PROCESS, priority=2),
            Process(pid=25, command="zsh", type=TaskType.THREAD, priority=5),
            Process(pid=26, command="python", type=TaskType.PROCESS, priority=7),
            Process(pid=27, command="java", type=TaskType.KTHREAD, priority=6),
        ]
        return random.sample(
            not_real_processes, min(self.RETURN_PROCESSES, len(not_real_processes))
        )

    @override
    def get_hup(self) -> list[Process]:
        not_real_processes = [
            Process(pid=28, command="sshd", type=TaskType.PROCESS, priority=10),
            Process(pid=29, command="nginx", type=TaskType.THREAD, priority=5),
            Process(pid=30, command="postgres", type=TaskType.KTHREAD, priority=1),
            Process(pid=31, command="redis", type=TaskType.PROCESS, priority=7),
            Process(pid=32, command="chrome", type=TaskType.THREAD, priority=8),
            Process(pid=33, command="firefox", type=TaskType.PROCESS, priority=6),
            Process(pid=34, command="docker", type=TaskType.KTHREAD, priority=3),
            Process(pid=35, command="mysql", type=TaskType.PROCESS, priority=9),
            Process(pid=36, command="emacs", type=TaskType.THREAD, priority=4),
            Process(pid=37, command="vim", type=TaskType.PROCESS, priority=2),
            Process(pid=38, command="zsh", type=TaskType.THREAD, priority=5),
            Process(pid=39, command="python", type=TaskType.PROCESS, priority=7),
            Process(pid=40, command="java", type=TaskType.KTHREAD, priority=6),
        ]
        return random.sample(
            not_real_processes, min(self.RETURN_PROCESSES, len(not_real_processes))
        )
