from litestar import Litestar, get


@get("/health")
async def health() -> dict[str, str]:
    return {"service": "worker", "status": "ok"}


app = Litestar(route_handlers=[health])
