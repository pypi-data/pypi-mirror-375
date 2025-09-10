from typing import Protocol


class EmitFunc(Protocol):
    async def __call__(self, alertname: str, description: str) -> None: ...
