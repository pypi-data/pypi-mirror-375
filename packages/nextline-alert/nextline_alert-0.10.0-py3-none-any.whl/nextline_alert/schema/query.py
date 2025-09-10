import strawberry

import nextline_alert


@strawberry.type
class AlertRDB:
    version: str = nextline_alert.__version__


@strawberry.type
class Query:
    @strawberry.field
    async def alert(self) -> AlertRDB:
        return AlertRDB()
