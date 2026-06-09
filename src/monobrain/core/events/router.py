from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from monobrain.core.db import get_session
from monobrain.core.events.service import IngestResult, ingest
from monobrain.schema import Event

router = APIRouter(prefix="/v1", tags=["events"])


@router.post("/events", response_model=IngestResult)
async def post_events(
    events: list[Event], session: AsyncSession = Depends(get_session)
) -> IngestResult:
    result = await ingest(session, events)
    await session.commit()
    return result
