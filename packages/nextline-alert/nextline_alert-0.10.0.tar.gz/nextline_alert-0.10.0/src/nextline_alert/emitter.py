from logging import getLogger

import httpx


class Emitter:
    def __init__(self, url: str, platform: str):
        self._url = url
        self._platform = platform
        self._logger = getLogger(__name__)
        self._logger.info(f'Campana endpoint: {url}')
        self._logger.debug(f'Platform: {platform!r}')

    async def __call__(self, alertname: str, description: str) -> None:
        data = self.compose_data(alertname, description)

        self._logger.info(f"Emitting alert: '{alertname}'")
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(self._url, json=data)
                response.raise_for_status()
        except BaseException:
            self._logger.exception(f"Failed to emit alert: '{alertname}'")
            self._logger.debug(f'Alert description: {description!r}')

    def compose_data(self, alertname: str, description: str):
        return {
            'status': 'firing',
            'alerts': [
                {
                    'status': 'firing',
                    'labels': {'alertname': alertname, 'platform': self._platform},
                    'annotations': {'description': description, 'groups': 'nextline'},
                }
            ],
        }
