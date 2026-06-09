<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="branding/logo-dark.svg">
    <img src="branding/logo.svg" alt="monobrain" width="76">
  </picture>
</p>

# monobrain

Code-native memory + curator for coding agents — **one shared brain** that compounds what
every run learns and knows when it's stale, because it's anchored to the code.

## Layout

| Path | What |
|---|---|
| `src/monobrain/schema` | the canonical types + event taxonomy (shared; codegens dex + ui) |
| `src/monobrain/core`   | FastAPI front door: event log, memory metadata, anchor index, queue |
| `src/monobrain/worker` | Litestar + DeepAgents: embeddings, agent fleets, owns LanceDB |
| `ui/`  | web SPA — the brain UI (browse memory, approval queue, curator) · *stub* |
| `dex/` | Rust CLI — the agent interface (emit · retrieve · staleness) · *stub* |

## Dev

```sh
uv sync --all-extras
uv run uvicorn monobrain.core.app:app   --reload --port 8000   # core   → /health
uv run uvicorn monobrain.worker.app:app --reload --port 8001   # worker → /health
# or the full stack:
docker compose up
```
