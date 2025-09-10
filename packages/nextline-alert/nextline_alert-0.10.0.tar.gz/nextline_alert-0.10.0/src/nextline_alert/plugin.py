from collections.abc import Mapping
from contextlib import asynccontextmanager
from logging import getLogger
from pathlib import Path
from typing import Optional, cast

from dynaconf import Dynaconf, Validator

from nextline import Nextline
from nextlinegraphql.hook import spec

from . import alerts
from .__about__ import __version__
from .emitter import Emitter
from .schema import Mutation, Query, Subscription

HERE = Path(__file__).resolve().parent
DEFAULT_CONFIG_PATH = HERE / 'default.toml'

assert DEFAULT_CONFIG_PATH.is_file()

PRELOAD = (str(DEFAULT_CONFIG_PATH),)
SETTINGS = ()
VALIDATORS = (
    Validator('ALERT.CAMPANA_URL', must_exist=True, is_type_of=str),
    Validator('ALERT.PLATFORM', must_exist=True, is_type_of=str),
    Validator('ALERT.IDLE_TIMEOUT_MINUTES', must_exist=True, is_type_of=(int, float)),
)


class Plugin:
    @spec.hookimpl
    def dynaconf_preload(self) -> Optional[tuple[str, ...]]:
        return PRELOAD

    @spec.hookimpl
    def dynaconf_settings_files(self) -> Optional[tuple[str, ...]]:
        return SETTINGS

    @spec.hookimpl
    def dynaconf_validators(self) -> Optional[tuple[Validator, ...]]:
        return VALIDATORS

    @spec.hookimpl
    def configure(self, settings: Dynaconf):
        logger = getLogger(__name__)
        logger.info(f'{__package__} version: {__version__}')
        url = settings.alert.campana_url
        platform = settings.alert.platform
        self._idle_timeout_minutes = settings.alert.idle_timeout_minutes
        self._emit = Emitter(url=url, platform=platform)

    @spec.hookimpl
    def schema(self) -> tuple[type, type | None, type | None]:
        return (Query, Mutation, Subscription)

    @spec.hookimpl
    @asynccontextmanager
    async def lifespan(self, context: Mapping):
        nextline = cast(Nextline, context['nextline'])
        alerts.register(
            nextline=nextline,
            emit=self._emit,
            idle_timeout_minutes=self._idle_timeout_minutes,
        )
        yield
