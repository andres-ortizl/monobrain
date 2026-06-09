from datetime import datetime, timezone

from sqlalchemy import JSON, DateTime, Integer, String, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, mapped_column

from monobrain.core.db import Base
from monobrain.schema import Event


class EventRow(Base):
    __tablename__ = "events"

    seq: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)  # log order / cursor
    id: Mapped[str] = mapped_column(String, unique=True, index=True)  # client-assigned, dedupe key
    type: Mapped[str] = mapped_column(String, index=True)
    time: Mapped[datetime] = mapped_column(DateTime(timezone=True))  # server-receive
    client_time: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    team: Mapped[str | None] = mapped_column(String, nullable=True)
    project: Mapped[str | None] = mapped_column(String, nullable=True, index=True)
    spec: Mapped[str | None] = mapped_column(String, nullable=True, index=True)
    actor: Mapped[dict] = mapped_column(JSON)
    subject: Mapped[str | None] = mapped_column(String, nullable=True)
    data: Mapped[dict] = mapped_column(JSON)
    schema_version: Mapped[int] = mapped_column(Integer)


async def append(session: AsyncSession, events: list[Event]) -> int:
    """Append events not already present — idempotent on the client-assigned id (spool
    retries are harmless). Returns the number actually inserted."""
    ids = [str(e.id) for e in events]
    seen = set(
        (await session.execute(select(EventRow.id).where(EventRow.id.in_(ids)))).scalars()
    )
    now = datetime.now(timezone.utc)
    inserted = 0
    for e in events:
        if str(e.id) in seen:
            continue
        seen.add(str(e.id))  # also dedupe within the same batch
        session.add(
            EventRow(
                id=str(e.id),
                type=e.type,
                time=now,
                client_time=e.client_time,
                team=e.team,
                project=e.project,
                spec=e.spec,
                actor=e.actor.model_dump(),
                subject=e.subject,
                data=e.data.model_dump(),
                schema_version=e.schema_version,
            )
        )
        inserted += 1
    await session.flush()
    return inserted
