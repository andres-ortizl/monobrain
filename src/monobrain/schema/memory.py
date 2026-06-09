from __future__ import annotations

from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, Field

# `kind` is a registry, not a closed enum and not free-text: the recommended starter
# set, extended per-deployment via config without a code change.
KINDS: tuple[str, ...] = (
    "lesson",
    "improvement",
    "plan",
    "debt",
    "decision",
    "gotcha",
    "convention",
)

Scope = Literal["spec", "project", "skill", "tooling"]
Visibility = Literal["private", "team", "project"]
State = Literal["active", "stale", "retired"]


class Anchor(BaseModel):
    """Where a memory is rooted in the code — the decay edge no SaaS memory layer has.

    Anchor to a *symbol*, not line numbers: ordinary refactors shift lines but not the
    symbol, so they don't false-stale the entry. When the anchored code changes past
    `git_rev`, the entry is marked `stale` and re-validated/retired.
    """

    repo: str | None = None  # owner/name or remote URL — which repo the symbol lives in
    paths: list[str] = Field(default_factory=list)
    symbol: str | None = None
    git_rev: str | None = None


class MemoryEntry(BaseModel):
    id: str
    kind: str
    scope: Scope = "project"
    visibility: Visibility = "private"
    owner: str

    title: str
    abstract: str  # L0 one-liner — always injectable; this is what gets embedded
    body: str  # L2 full markdown
    trigger: str | None = None  # "when this applies" — a retrieval key
    tags: list[str] = Field(default_factory=list)

    embedding: list[float] | None = None  # computed server-side; never client-supplied
    provenance: list[str] = Field(default_factory=list)  # event / spec ids distilled from
    anchor: Anchor = Field(default_factory=Anchor)
    confidence: float = 0.5
    state: State = "active"
    data: dict[str, Any] | None = None  # per-kind extras (debt→severity/effort, plan→steps)

    created_at: datetime
    updated_at: datetime
    last_validated_at: datetime | None = None
