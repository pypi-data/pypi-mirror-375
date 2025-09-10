import asyncio
import re
import time
from unittest.mock import AsyncMock

import pytest

from nextline import Nextline
from nextline_alert.alerts import AlertRunFailed
from nextline_alert.emitter import Emitter


def func_success():  # pragma: no cover
    time.sleep(0.001)


def func_raise_ignore():  # pragma: no cover
    time.sleep(0.001)
    raise KeyboardInterrupt


def func_raise():  # pragma: no cover
    time.sleep(0.001)
    raise ValueError('test')


@pytest.mark.parametrize('func', [func_success, func_raise_ignore])
async def test_emit_no_alert(func) -> None:
    nextline = Nextline(func)

    emit = AsyncMock(spec=Emitter)
    alert = AlertRunFailed(emit=emit)
    assert nextline.register(alert)

    # Run a script that does not raise an exception
    async with nextline:
        event = asyncio.Event()
        await nextline.run_continue_and_wait(event)

    emit.assert_not_called()


async def test_emit_alert() -> None:
    nextline = Nextline(func_raise)

    emit = AsyncMock(spec=Emitter)
    alert = AlertRunFailed(emit=emit)
    assert nextline.register(alert)

    # Run a script that raises an exception
    async with nextline:
        event = asyncio.Event()
        await nextline.run_continue_and_wait(event)

    emit.assert_awaited_once()
    alertname = emit.call_args.kwargs['alertname']
    description = emit.call_args.kwargs['description']
    assert re.fullmatch(r"Run \d+ failed", alertname)
    assert 'ValueError' in description

