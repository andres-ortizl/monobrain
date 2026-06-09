from fastapi import FastAPI

from monobrain.core.events.router import router as events_router

app = FastAPI(title="monobrain core")
app.include_router(events_router)


@app.get("/health")
def health() -> dict[str, str]:
    return {"service": "core", "status": "ok"}
