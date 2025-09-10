from nextline import Nextline

from .idle import AlertIdle
from .run_failed import AlertRunFailed
from .types import EmitFunc


def register(nextline: Nextline, emit: EmitFunc, idle_timeout_minutes: float) -> None:
    nextline.register(AlertRunFailed(emit=emit))
    nextline.register(AlertIdle(emit=emit, timeout_minutes=idle_timeout_minutes))
