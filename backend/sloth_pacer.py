"""
SlothSort — The Sloth Pacer 🦥
Monitors system CPU/RAM so inference only runs when the machine is idle.
"Slow and Steady" — never lag the user's laptop.
"""

import asyncio
import psutil
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional
import time


class SlothState(str, Enum):
    NAPPING = "Napping"
    SORTING = "Sorting"
    PAUSED = "Paused"
    IDLE = "Idle"


@dataclass
class PacerConfig:
    cpu_threshold: float = 35.0        # Max CPU % before napping
    memory_threshold: float = 85.0     # Max RAM % before napping
    nap_duration: float = 5.0          # Seconds to sleep between checks / between files
    check_interval: float = 1.0        # Seconds between CPU samples


@dataclass
class SystemSnapshot:
    cpu_percent: float = 0.0
    memory_percent: float = 0.0
    is_system_busy: bool = False
    timestamp: float = field(default_factory=time.time)


class SlothPacer:
    """
    The heartbeat of SlothSort. Monitors real-time system load and decides
    whether the sloth daemon is allowed to work or must nap.
    """

    def __init__(self, config: Optional[PacerConfig] = None):
        self.config = config or PacerConfig()
        self._state: SlothState = SlothState.IDLE
        self._running: bool = False
        self._latest_snapshot: SystemSnapshot = SystemSnapshot()

    @property
    def state(self) -> SlothState:
        return self._state

    @state.setter
    def state(self, value: SlothState):
        self._state = value

    @property
    def running(self) -> bool:
        return self._running

    @property
    def snapshot(self) -> SystemSnapshot:
        return self._latest_snapshot

    def take_snapshot(self) -> SystemSnapshot:
        """Sample current CPU and memory usage."""
        cpu = psutil.cpu_percent(interval=self.config.check_interval)
        mem = psutil.virtual_memory().percent
        busy = cpu > self.config.cpu_threshold or mem > self.config.memory_threshold
        self._latest_snapshot = SystemSnapshot(
            cpu_percent=round(cpu, 1),
            memory_percent=round(mem, 1),
            is_system_busy=busy,
        )
        return self._latest_snapshot

    async def wait_for_idle(self) -> SystemSnapshot:
        """Block (async) until the system is idle enough for inference."""
        while True:
            snap = self.take_snapshot()
            if not snap.is_system_busy:
                return snap
            self._state = SlothState.NAPPING
            await asyncio.sleep(self.config.nap_duration)

    async def inter_file_nap(self):
        """Sleep between files — slow and steady wins the race."""
        await asyncio.sleep(self.config.nap_duration)

    def start(self):
        self._running = True
        self._state = SlothState.IDLE

    def pause(self):
        self._running = False
        self._state = SlothState.PAUSED

    def resume(self):
        self._running = True
        self._state = SlothState.IDLE
