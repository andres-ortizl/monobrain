from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from monobrain.core.events import store
from monobrain.schema import Event


class IngestResult(BaseModel):
    received: int
    accepted: int
    duplicates: int


async def ingest(session: AsyncSession, events: list[Event]) -> IngestResult:
    accepted = await store.append(session, events)
    return IngestResult(
        received=len(events), accepted=accepted, duplicates=len(events) - accepted
    )
