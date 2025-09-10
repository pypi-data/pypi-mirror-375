import asyncio
import reprlib
import time
from collections.abc import Generator
from typing import Any
from unittest.mock import AsyncMock, Mock

import pytest
from hypothesis import HealthCheck, Phase, given, settings
from hypothesis import strategies as st

from nextline import Nextline
from nextline_alert.alerts import AlertIdle


@pytest.fixture()
def mock_sleep(monkeypatch: pytest.MonkeyPatch) -> AsyncMock:
    from nextline_alert.alerts import idle

    mock_module = Mock(wraps=asyncio)
    mock_module.sleep = AsyncMock()
    mock_module.CancelledError = asyncio.CancelledError
    monkeypatch.setattr(idle, 'asyncio', mock_module)
    return mock_module.sleep


async def test_mock_sleep(mock_sleep: AsyncMock) -> None:
    from nextline_alert.alerts import idle

    assert idle.asyncio.sleep is mock_sleep
    assert idle.asyncio is not asyncio

    await mock_sleep(0)


async def quick(*_, **__) -> None:
    await asyncio.sleep(0)


async def never(*_, **__) -> None:
    await asyncio.Event().wait()


class MockEmit:
    def __init__(self) -> None:
        self.alertname: str | None = None
        self.description: str | None = None
        self._event = asyncio.Event()

    def __repr__(self) -> str:
        return (
            f'{self.__class__.__name__}('
            f'alertname={reprlib.repr(self.alertname)}, '
            f'description={reprlib.repr(self.description)})'
        )

    def reset(self) -> None:
        self.alertname = None
        self.description = None
        self._event.clear()

    async def __call__(self, alertname: str, description: str) -> None:
        self.alertname = alertname
        self.description = description
        self._event.set()

    def __await__(self) -> Generator[Any, None, Any]:
        return self._event.wait().__await__()


def func():  # pragma: no cover
    time.sleep(0.0001)


@settings(
    phases=(Phase.generate,),
    suppress_health_check=[HealthCheck.function_scoped_fixture],
    max_examples=10,
)
@given(data=st.data())
async def test_property(mock_sleep: AsyncMock, data: st.DataObject) -> None:
    mock_sleep.reset_mock()  # As Hypothesis tests multiple times

    emit = MockEmit()
    repr(emit)  # For coverage of __repr__

    timeout_minutes = data.draw(st.floats(min_value=1))
    timeout = timeout_minutes * 60
    alert = AlertIdle(emit=emit, timeout_minutes=timeout_minutes)

    nextline = Nextline(func)
    assert nextline.register(alert)

    idle = data.draw(st.booleans(), label='idle')

    mock_sleep.side_effect = quick if idle else never

    async with nextline:
        mock_sleep.assert_called_once_with(timeout)
        mock_sleep.reset_mock()
        if idle:
            await emit
            assert emit.alertname
            assert emit.description
        else:
            assert emit.alertname is None
            assert emit.description is None
        emit.reset()

        n_runs = data.draw(st.integers(min_value=0, max_value=3), label='n_runs')
        for _ in range(n_runs):
            if nextline.state == 'finished':
                await nextline.reset()

            idle = data.draw(st.booleans(), label='idle')
            mock_sleep.side_effect = quick if idle else never

            await nextline.run_continue_and_wait()

            mock_sleep.assert_called_once_with(timeout)
            mock_sleep.reset_mock()
            if idle:
                await emit
                assert emit.alertname
                assert emit.description
            else:
                assert emit.alertname is None
                assert emit.description is None
            emit.reset()
