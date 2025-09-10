from strawberry.types import ExecutionResult

import nextline_alert
from nextline_alert.graphql import QUERY_VERSION
from tests.schema.conftest import Schema


async def test_schema(schema: Schema) -> None:
    resp = await schema.execute(QUERY_VERSION)
    assert isinstance(resp, ExecutionResult)
    assert resp.data
    assert resp.data['alert']['version'] == nextline_alert.__version__
