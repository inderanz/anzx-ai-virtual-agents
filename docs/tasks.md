# Tasks — Caroline Springs CC Real-Time Cricket Agent

> Follow order; keep changes inside `/services/cricket-agent` and `/services/cricket-bridge` unless specified.

---

## 0. Boilerplate & Service Scaffolding
- Create `services/cricket-agent` (Python) with:
  - `app/` (main app, config, observability)
  - `agent/` (prompt, router, tools)
  - `models/` (Team, Fixture, Scorecard, Ladder, Roster)
  - `jobs/` (sync refresh)
  - `tests/`
  - `Dockerfile`, `requirements.txt`, `openapi.yaml`

- Create `services/cricket-bridge` (Node) with:
  - `src/` (index, forwarder)
  - `package.json`, `tsconfig.json`, `Dockerfile`, `.env.example`

- Pin Python & Node versions; create/refresh:
  - `services/cricket-agent/requirements.txt` with versions in `requirements.md`
  - `services/cricket-bridge/package.json` with versions in `requirements.md`

- Ensure Dockerfiles use `python:3.11-slim` and `node:20-slim`.

---

## 1. FastAPI Surface (cricket-agent)
- Files: `app/main.py`, `app/config.py`, `app/observability.py`, `openapi.yaml`
- Endpoints:
  - `/healthz`
  - `/v1/ask`
  - `/internal/refresh` (bearer token from Secret Manager)
- Logging: Cloud Logging JSON; include `request_id`, `source`, `latency`.

---

## 2. PlayHQ Public Client
- File: `agent/tools/playhq.py`
- Implement methods:
  - `get_seasons`
  - `get_grades`
  - `get_teams`
  - `get_team_fixtures(team_id, season_id)`
  - `get_game_summary(game_id)` (public summary)
  - `get_ladder(grade_id)`

- Requirements:
  - Handle pagination (`cursor`, `metadata.hasMore`).
  - Headers: `x-api-key`, `x-phq-tenant`.
  - Respect public visibility (hidden entities not returned).
  - Retries for 429/5xx.

- Tests:
  - `tests/test_playhq_client.py`
  - Mocked JSON responses.

---

## 3. Models & Normalization
- Files: `models/{team,fixture,scorecard,ladder,roster}.py`, `agent/tools/normalize.py`
- Tasks:
  - Normalize raw JSON → Pydantic models.
  - Produce short text snippets per record type (fixture list, batting summary).
  - Add metadata tags: `team_id`, `season_id`, `grade_id`, `type`.
  - Chunk text (<1000 tokens) for embeddings.

---

## 4. Configuration & Secrets
- File: `app/config.py`
- Load secrets from Secret Manager:
  - `PLAYHQ_API_KEY`
  - `CSCC_IDS` (org/season/team IDs)
  - `PRIVATE_API_TOKEN` (if private mode)
  - `INTERNAL_REFRESH_TOKEN`
- Fallback: plain env vars in local dev.
- Inject settings: `playhq_mode`, `vector_backend`, etc.

---

## 5. Retrieval & Embeddings
- File: `agent/tools/vector_client.py`
- Use **Vertex RAG Managed DB** or wrap existing knowledge-service.
- Embeddings: `text-embedding-005`; chunks 800–1200 tokens.
- Methods:
  - `upsert(docs)`
  - `query(text, filters, k)`
- Sync job integration: only upsert deltas (skip unchanged hashes).

---

## 6. Sync Job
- File: `jobs/sync.py`
- Modes: nightly, match-day (Cloud Scheduler), and `/internal/refresh`.
- Tasks:
  - Pull fixtures, ladder, recent game summaries.
  - Normalize + upsert new docs.
  - Write raw + normalized JSON to GCS.

---

## 7. Intent Router & Agent Logic
- Files: `agent/router.py`, `agent/prompt.py`, `agent/llm_agent.py`
- Detect intents via regex + fallback LLM.
- Map intents → tools or RAG queries:
  1. Player → team
  2. Player → last-match runs
  3. Fixtures list (Blue U10s, 2025/26)
  4. Ladder position (Blue 10s)
  5. Next fixture venue/time (White 10s)
  6. Roster list (White 10s)

- Use deterministic formatting for exact stats.
- Use Gemini 1.5 Flash only for natural language stitching.
- Support streaming if deployed with Vertex Agent Engine.

---

## 8. WhatsApp Bridge
- Service: `services/cricket-bridge`
- Files:
  - `src/index.ts` (Baileys MD session, Express relay)
  - `src/forwarder.ts` (optional split)

- Features:
  - Persist Baileys session (GCS or Secret Manager).
  - Respond to `!cscc` or @mention.
  - Relay to `cricket-agent /v1/ask` with `source="whatsapp"`.
  - Return responses to group.
  - Add health & logging.

---

## 9. Web UI
- Add `/cricket` page in `website/`.
- Call `/v1/ask` via AJAX or WebSocket.
- Render bullet lists; bold important info; handle streaming gracefully.

---

## 10. Observability & Alerts
- Structured logs: `{intent, rag_ms, api_ms, tokens_in, tokens_out, latency_ms}`.
- Metrics & alerts:
  - p95 latency
  - Sync failures
  - PlayHQ error rates

---

## 11. Private/Webhook Mode (optional, feature-flag)
- Env: `PLAYHQ_MODE=private` (default: public).
- If approved:
  - Add `/webhooks/playhq` receiver.
  - Verify signatures.
  - Upsert deltas.
- Never expose `visibility: private` fields in public endpoints.

---

## 12. CI/CD Hooks
- Cloud Build:
  - Build & deploy both services → Cloud Run.
  - Configure WI access for Secret Manager & GCS.
  - Minimum instances for bridge.

---

