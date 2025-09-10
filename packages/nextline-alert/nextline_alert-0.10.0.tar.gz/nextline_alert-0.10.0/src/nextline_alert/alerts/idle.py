import asyncio
import datetime
from logging import getLogger

from nextline.plugin.spec import hookimpl

from .types import EmitFunc


class AlertIdle:
    '''A plugin of Nextline.

    The name of this class appears as the plugin name in the log.
    '''

    def __init__(self, emit: EmitFunc, timeout_minutes: float):
        self._emit = emit
        self._timeout = timeout_minutes * 60  # in seconds
        self._alertname = f'Idle for {timeout_minutes} minutes'
        self._logger = getLogger(__name__)
        self._logger.info(f'Timeout: {timeout_minutes} minutes')

    @hookimpl
    async def start(self) -> None:
        self._task = asyncio.create_task(self._emit_on_timeout())

    @hookimpl
    async def on_start_run(self) -> None:
        self._task.cancel()
        await self._task

    @hookimpl
    async def on_finished(self) -> None:
        self._task = asyncio.create_task(self._emit_on_timeout())

    @hookimpl
    async def close(self) -> None:
        self._task.cancel()
        await self._task

    async def _emit_on_timeout(self) -> None:
        start = datetime.datetime.now(datetime.timezone.utc)
        start_fmt = start.strftime("%Y-%m-%d %H:%M %Z")
        description = f'Not running since {start_fmt}'
        self._logger.info(f'Starting idle timer: {self._timeout} seconds')
        try:
            await asyncio.sleep(self._timeout)
            self._logger.info('Idle timeout reached, emitting alert')
            await self._emit(alertname=self._alertname, description=description)
        except asyncio.CancelledError:
            self._logger.info('Idle timer cancelled')
            return
