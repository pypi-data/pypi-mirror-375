import asyncio
from collections.abc import AsyncIterator

import pytest

from nextline_alert.graphql import QUERY_VERSION
from nextlinegraphql import create_app
from nextlinegraphql.plugins.graphql.test import TestClient, gql_request


@pytest.fixture
async def client() -> AsyncIterator[TestClient]:
    app = create_app()  # the plugin is loaded here
    async with TestClient(app) as y:
        await asyncio.sleep(0)
        yield y


async def test_plugin(client: TestClient) -> None:
    data = await gql_request(client, QUERY_VERSION)
    assert data
