# Pluk

Git-commit–aware symbol lookup & impact analysis engine

---

## What is a "symbol"?

In Pluk, a **symbol** is any named entity in your codebase that can be referenced, defined, or impacted by changes. This includes functions, classes, methods, variables, and other identifiers that appear in your source code. Pluk tracks symbols across commits and repositories to enable powerful queries like "go to definition", "find all references", and "impact analysis".

Pluk gives developers “go-to-definition”, “find-all-references”, and “blast-radius” impact queries across one or more Git repositories. Heavy lifting (indexing, querying, storage) runs in Docker containers; a lightweight host shim (`pluk`) boots the stack and delegates commands into a thin CLI container (`plukd`) that talks to an internal API.

---

## Key Features

- **Fuzzy symbol search** (`pluk search`) for finding symbols in the current commit
- **Definition lookup** (`pluk define`)
- **Impact analysis** (`pluk impact`) to trace downstream dependents
- **Commit-aware indexing** (`pluk diff`) across Git history
- **Containerized backend**: PostgreSQL (graph) + Redis (broker/cache)
- **Strict lifecycle**: `pluk start` (host shim) is required before any containerized commands; use the shim on the host to manage services (`start`, `status`, `cleanup`).
- **Host controls**: `pluk status` to check, `pluk cleanup` to stop services

---

## Quickstart

1. **Install**

```bash
pip install pluk
```

2. **Start services (required)**

```bash
pluk start
```

This creates/updates `~/.pluk/docker-compose.yml`, **pulls latest images**, and brings up: `postgres`, `redis`, `api` (FastAPI), `worker` (Celery), and `cli` (idle exec target). The API stays **internal** to the Docker network. Note: service lifecycle commands (`start`, `status`, `cleanup`) are implemented in the host shim; run them on your host shell using the `pluk` command.

3. **Index and query**

```bash
pluk init /path/to/repo           # queue full index (host shim extracts repo's origin URL and commit and forwards them into the containerized CLI)
pluk search MyClass               # fuzzy lookup; symbol matches branch-wide
pluk define my_function           # show definition (file:line@commit)
pluk impact computeFoo            # direct dependents; blast radius
pluk diff symbol abc123 def456    # symbol changes between commits abc123 → def456, local to the current branch
```

Important: the repository you index must be public (or otherwise directly reachable by the worker container). The worker clones repositories inside the container environment using the repository URL; private repositories that require credentials are not supported by the host shim workflow.

**Note:** CLI commands that poll for job status (like `pluk init`) now display real-time output, thanks to unbuffered Python output in the CLI container.

4. **Check / stop (host-side)**

```bash
pluk status     # tells you if services are running
pluk cleanup    # stops services (containers stay; fast restart)
```

If you want a full teardown (remove containers/network), use:

```bash
docker compose -f ~/.pluk/docker-compose.yml down -v
```

---

## Data Flow

[![](https://mermaid.ink/img/pako:eNp9UtGO2jAQ_BVrHyqQAiKBhCSVKrWg6irRit6dVKmkqkyyl0Qkdmo7BUr4967D0eNe-rT27OzsztonSGWGEMNTJfdpwZVhq_tEMKbbba54U7A7qY0FGHsoynqTQFO1OzYoCGaakGECP2weRZaIV5VLme5Q_fyCZi_V7qKxWH0iibQqmUb1u0wxEQMrmL1leMCUGa5yNFdNxt6vLZ83t_yPXBvCX0jfSB4V8fb94Ya6wArV8YV5j1mpN4M-JGKrpKW_YSlPCxw-c5YfNoM1ucsVPnxdJUIf662sWO9p-Nqq3Qgbjd51_eylMLKzDm2KQp-5e3xcd9aGBSlc6OJXiy2SW73THXse52qkp6RS6Lb-L2WvSoPUNcNDR1PfNlDIM0Y9VIna5sCBXJUZxEa16ECNqub2CidblYApsMYEYjpmnN4KEnGmmoaL71LW1zIl27yA-IlXmm5tk3GDy5LTZup_qKLloFrIVhiIg8j3ehWIT3CAeOSF_tibzqahO43mURDNZw4cIXa9YBzOCJyEfjQJvDA4O_Cn7-yOPd-fBG7ou-48CN25A7QKI9Xny7_tv-_5L0GP5fk?type=png)](https://mermaid.live/edit#pako:eNp9UtGO2jAQ_BVrHyqQAiKBhCSVKrWg6irRit6dVKmkqkyyl0Qkdmo7BUr4967D0eNe-rT27OzsztonSGWGEMNTJfdpwZVhq_tEMKbbba54U7A7qY0FGHsoynqTQFO1OzYoCGaakGECP2weRZaIV5VLme5Q_fyCZi_V7qKxWH0iibQqmUb1u0wxEQMrmL1leMCUGa5yNFdNxt6vLZ83t_yPXBvCX0jfSB4V8fb94Ya6wArV8YV5j1mpN4M-JGKrpKW_YSlPCxw-c5YfNoM1ucsVPnxdJUIf662sWO9p-Nqq3Qgbjd51_eylMLKzDm2KQp-5e3xcd9aGBSlc6OJXiy2SW73THXse52qkp6RS6Lb-L2WvSoPUNcNDR1PfNlDIM0Y9VIna5sCBXJUZxEa16ECNqub2CidblYApsMYEYjpmnN4KEnGmmoaL71LW1zIl27yA-IlXmm5tk3GDy5LTZup_qKLloFrIVhiIg8j3ehWIT3CAeOSF_tibzqahO43mURDNZw4cIXa9YBzOCJyEfjQJvDA4O_Cn7-yOPd-fBG7ou-48CN25A7QKI9Xny7_tv-_5L0GP5fk)

**How it works**

- **Host shim (`pluk`)** writes the Compose file, **pulls images**, and runs `docker compose up`.
- **CLI container (`plukd`)** is the exec target; it calls the API at `http://api:8000`.
- **API (FastAPI)** serves read endpoints (`/search`, `/define`, `/impact`, `/diff`) and enqueues write jobs (`/reindex`) to **Redis**.
- **Worker (Celery)** consumes jobs from **Redis**, clones/pulls repos into a volume (`/var/pluk/repos`), parses deltas, and writes to **Postgres**.
- Reads never block on indexing; write progress can be polled via job status endpoints (planned).

---

## Architecture (current)

- **Single image, multiple roles**: Compose selects per-service `command`
  - `api` → `uvicorn pluk.api:app --host 0.0.0.0 --port 8000`
  - `worker` → `celery -A pluk.worker worker -l info`
  - `cli` → `sleep infinity` (keeps container up for `docker compose exec`)
- **Internal networking**: API is _not_ exposed to the host; CLI calls it over Docker DNS (`PLUK_API_URL=http://api:8000`).
- **Config**: `PLUK_DATABASE_URL`, `PLUK_REDIS_URL` injected via Compose; worker uses `PLUK_REPOS_DIR=/var/pluk/repos`.
- **Images**: by default the shim uses `jorstors/pluk:latest`, `postgres:16-alpine`, and `redis-alpine`

---

## Development

- **Project layout** (`src/pluk`):
  - `shim.py` — host shim entrypoint (`pluk`)
  - `cli.py` — container CLI (`plukd`)
  - `api.py` — FastAPI app (internal API)
  - `worker.py` — Celery app & tasks
- **Entry points** (`pyproject.toml`):

```toml
[project.scripts]
pluk  = "pluk.shim:main"
plukd = "pluk.cli:main"
```

---

## Testing

```bash
pytest
```

Docker must be running; services must be started via `pluk start` for integration tests.

---

## License

MIT License
