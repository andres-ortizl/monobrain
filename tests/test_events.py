import uuid


def note_event(eid: str | None = None, project: str = "p", text: str = "hi") -> dict:
    return {
        "id": eid or str(uuid.uuid4()),
        "type": "note",
        "project": project,
        "actor": {"user_id": "u1", "role": "coder"},
        "data": {"type": "note", "text": text},
        "schema_version": 1,
    }


async def test_ingest_accepts_then_dedupes(client):
    e = note_event()

    r1 = await client.post("/v1/events", json=[e])
    assert r1.status_code == 200
    assert r1.json() == {"received": 1, "accepted": 1, "duplicates": 0}

    # spool retry: same id again → idempotent no-op
    r2 = await client.post("/v1/events", json=[e])
    assert r2.json() == {"received": 1, "accepted": 0, "duplicates": 1}


async def test_dedupes_within_a_batch(client):
    e = note_event()
    r = await client.post("/v1/events", json=[e, e])
    assert r.json() == {"received": 2, "accepted": 1, "duplicates": 1}


async def test_rejects_envelope_type_mismatching_payload(client):
    e = note_event()
    e["data"] = {"type": "test.result", "passed": 1, "failed": 0}  # type=note ≠ data.type
    r = await client.post("/v1/events", json=[e])
    assert r.status_code == 422
