from __future__ import annotations

from typing import Annotated, Literal, Union
from uuid import UUID

from pydantic import BaseModel, Field, model_validator

Role = Literal["lead", "coder", "reviewer", "curator", "human"]


class Actor(BaseModel):
    user_id: str
    role: Role


# Payloads the brain learns from. Loop/fleet telemetry (phase, heartbeat, ports, …)
# stays in the companion and never reaches here. Discriminated on `type`.


class Note(BaseModel):
    type: Literal["note"] = "note"
    text: str
    level: Literal["info", "warn", "error"] = "info"
    topic: str | None = None
    scope: Literal["spec", "project", "skill"] = "spec"


class TestResult(BaseModel):
    type: Literal["test.result"] = "test.result"
    passed: int
    failed: int
    cmd: str | None = None


class ReviewVerdict(BaseModel):
    type: Literal["review.verdict"] = "review.verdict"
    round: int
    verdict: Literal["pass", "fail", "notes"]
    blockers: int = 0
    issues: int = 0


class MemoryProposed(BaseModel):
    type: Literal["memory.proposed"] = "memory.proposed"
    memory_id: str
    patch: dict  # the actual entry/diff — so "accept" is deterministic, can't drift


class MemoryDecided(BaseModel):
    type: Literal["memory.decided"] = "memory.decided"
    memory_id: str
    decision: Literal["accept", "reject"]
    by: str


class MemoryUsed(BaseModel):
    type: Literal["memory.used"] = "memory.used"
    memory_id: str


class SkillUsed(BaseModel):
    type: Literal["skill.used"] = "skill.used"
    skill: str


class LibrarianRun(BaseModel):
    type: Literal["librarian.run"] = "librarian.run"
    phase: Literal["distill", "organize", "dedup", "heal", "prune", "promote"]


Payload = Annotated[
    Union[
        Note,
        TestResult,
        ReviewVerdict,
        MemoryProposed,
        MemoryDecided,
        MemoryUsed,
        SkillUsed,
        LibrarianRun,
    ],
    Field(discriminator="type"),
]


class Event(BaseModel):
    id: UUID  # client-assigned UUIDv7 → server dedupes (spool retries) + index locality
    type: str  # mirrors data.type (the taxonomy string); kept on the envelope for routing
    team: str | None = None
    project: str | None = None
    spec: str | None = None  # nullable: curator/skill.* aren't spec-scoped
    actor: Actor
    data: Payload
    schema_version: int = 1
    # server stamps `received_at` + `seq` on ingest — not wire fields.

    @model_validator(mode="after")
    def _type_mirrors_payload(self) -> "Event":
        if self.type != self.data.type:
            raise ValueError(f"envelope type {self.type!r} != data.type {self.data.type!r}")
        return self
