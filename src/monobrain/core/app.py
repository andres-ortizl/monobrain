from fastapi import FastAPI

app = FastAPI(title="monobrain core")


@app.get("/health")
def health() -> dict[str, str]:
    return {"service": "core", "status": "ok"}
