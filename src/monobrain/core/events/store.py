import uuid
from datetime import datetime, timezone

from sqlalchemy import JSON, DateTime, Integer, String, Uuid, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, mapped_column

from monobrain.core.db import Base
from monobrain.schema import Event


class EventRow(Base):
    """The append-only journal — the history of what happened, nothing more. Read only
    to fold projections and for owner-/spec-scoped history reads (distill). The
    consumable read models are separate projection tables."""

    __tablename__ = "events"

    seq: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)  # server order / cursor
    id: Mapped[uuid.UUID] = mapped_column(Uuid, unique=True)  # client UUIDv7 — dedupe + locality
    type: Mapped[str] = mapped_column(String, index=True)
    received_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))  # server stamp
    team: Mapped[str | None] = mapped_column(String, nullable=True)
    project: Mapped[str | None] = mapped_column(String, nullable=True)
    spec: Mapped[str | None] = mapped_column(String, nullable=True)
    actor_id: Mapped[str] = mapped_column(String, index=True)  # owner-scoped reads
    actor_role: Mapped[str] = mapped_column(String)
    data: Mapped[dict] = mapped_column(JSON)
    schema_version: Mapped[int] = mapped_column(Integer)


async def append(session: AsyncSession, events: list[Event]) -> int:
    """Append events not already present — idempotent on the client-assigned id (spool
    retries are harmless). Returns the number actually inserted."""
    ids = [e.id for e in events]
    seen = set(
        (await session.execute(select(EventRow.id).where(EventRow.id.in_(ids)))).scalars()
    )
    now = datetime.now(timezone.utc)
    inserted = 0
    for e in events:
        if e.id in seen:
            continue
        seen.add(e.id)  # also dedupe within the same batch
        session.add(
            EventRow(
                id=e.id,
                type=e.type,
                received_at=now,
                team=e.team,
                project=e.project,
                spec=e.spec,
                actor_id=e.actor.user_id,
                actor_role=e.actor.role,
                data=e.data.model_dump(),
                schema_version=e.schema_version,
            )
        )
        inserted += 1
    await session.flush()
    return inserted
