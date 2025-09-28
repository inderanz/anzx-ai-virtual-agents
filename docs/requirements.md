# Requirements — Caroline Springs CC Real-Time Cricket Agent

## Target Stack & Versions
- Python: 3.10/3.11
- FastAPI: 0.95.x
- Uvicorn: 0.24.x
- google-cloud-aiplatform[adk,agent_engine]: >=1.112.0,<2.0  # ADK & Agent Engine included
- google-cloud-secret-manager: >=2.20.0
- google-cloud-logging: >=3.10.0
- httpx: >=0.25,<0.30
- pydantic: >=2.5,<3.0
- tenacity: >=9,<10
- orjson: >=3.10
- pytest: >=8,<9
- Node: 20.x LTS
- @adiwajshing/baileys: ^6.7.0
- express: ^4.18.0
- axios: ^1.7.0
- typescript: ^5.5.0
- tsx: ^4.17.0
- PlayHQ External API: v1 (public), pagination via `cursor` + `metadata.hasMore`, headers `x-api-key`, `x-phq-tenant`

## Functional Requirements
1) Answer grounded questions (fixtures, last-match runs, ladder, roster via lineups, player→team).
2) Channels: web (/cricket UI) and WhatsApp (bridge).
3) Latency: p50 < 3s (warm), retrieval < 100 ms where possible.
4) Freshness: nightly + match-day sync; on-demand refresh for time-sensitive asks; optional webhooks if PlayHQ approves.
5) Deterministic when exact numbers exist (e.g., runs); otherwise LLM formats concise output.
6) Extensible to additional teams/clubs without code restructure.

7. **Answer natural-language queries** (examples):
   - Which team is player “Harshvardhan” part of?
   - How many runs did Harshvardhan score in the last match?
   - List fixtures for “Caroline Springs Blue U10” under 2025/26 competition.
   - What is their position on the ladder?
   - Next match details (venue + start time) for “White 10s.”
   - List players in “White 10s” roster.

8. **Channels**
   - Web UI (chat interface on `anzx.ai/cricket`) → calls agent API.
   - WhatsApp (group chat) via `cricket-bridge`.

9. **Response Speed & UX**
   - p50 end-to-end latency < 3s (warm path).
   - Retrieval/query time < 100ms.
   - Use streaming responses if supported.

10. **Data Freshness**
   - Regular syncs (nightly, match days).
   - Real-time updates via PlayHQ webhooks if available (for cricket, live scoring webhooks exist). :contentReference[oaicite:8]{index=8}

10. **Grounded Answers Only**
   - Responses must be based on data (fixtures, scorecards, ladder). If no data, respond “I don’t know.”
   - Do not hallucinate new information.

12. **Support for Private Mode**
   - If PlayHQ grants private API / webhook access, the agent can fetch hidden data using token/credentials.
   - Only expose private data in responses if authorized (future feature).

13. **Scalability & Extensibility**
   - Ability to add more teams or clubs by config.
   - Vector store should support many documents (~10k+ scale).


## Non-Functional Requirements

- Security: Secret Manager + Workload Identity; least-privilege IAM; no personal PlayHQ credentials; never leak private/hidden data.
- Reliability: retries/backoff for PlayHQ 429/5xx; serve cached data when upstream down; idempotent sync.
- Maintainability: repo-aligned structure under `/services`; OpenAPI for service; unit tests for tools.
- Observability: structured logs (intent, tool timings, latency), metrics & alerts (p95 > 5s, sync failures, API error spikes).
- Cost: incremental embeddings (hashing); use Vertex RAG; keep LLM calls minimal.

1. **Security & Credential Management**
   - Use Secret Manager for all credentials.
   - Workload Identity / IAM roles for least privilege.
   - No secrets or PII logged.

2. **Reliability & Fault Tolerance**
   - Retry/backoff on PlayHQ API failures / rate limits.
   - Sync job idempotent.
   - Monitor error rates; fallback to cached data when upstream is unavailable.

3. **Maintainability**
   - Clean module separation: agent logic, tools, sync, API, models.
   - Use OpenAPI spec for agent API and generate client stubs/tests.
   - Document architectural decisions (ADR).

4. **Observability**
   - Structured logs with metadata (request_id, intent, latency, tool times).
   - Export metrics: ask_latency, tool_invocation_count, error_rate.
   - Set alerts on high latency or sync failures.

5. **Cost Control**
   - Use incremental embeddings updates.
   - Prefer managed vector store (Vertex RAG) to reduce infra overhead.
   - Control usage of premium LLMs (Cursor prompt budgets).

## External Interfaces

- **Agent HTTP API**
  - `POST /v1/ask` with `{ text, source, team_hint? }`
  - `POST /internal/refresh` protected with bearer token
  - `GET /healthz`

- **PlayHQ APIs (public, v1)**
  - `GET /organisations/:id/seasons` etc. (public APIs) :contentReference[oaicite:9]{index=9}
  - `GET /games` collection (with pagination) :contentReference[oaicite:10]{index=10}
  - `GET /summary/:gameId` (public summary of game) :contentReference[oaicite:11]{index=11}
  - `GET /ladder/:gradeId` (Ladder Collection) :contentReference[oaicite:12]{index=12}

- **Webhook Endpoint** (optional / private mode)
  - POST `/webhooks/playhq` to receive live game updates (scorecard, events) :contentReference[oaicite:13]{index=13}

## External Interfaces
- `POST /v1/ask`  → `{text, source?, team_hint?}` → `{answer, meta:{latency_ms,intent?}}`
- `POST /internal/refresh` (bearer) → `{scope: all|team|match|ladder, id?}`
- `GET /healthz`
- Optional: `POST /webhooks/playhq` (private/webhooks mode)

## Acceptance Criteria
- The 6 sample queries return correct, data-grounded output.
- The `/cricket` chat UI functions (frontend ↔ agent).
- WhatsApp integration responds only when triggered (no spam).
- Sync job works and updates vector store.
- No secrets appear in logs; all requests traceable.
- System recovers gracefully when PlayHQ APIs are slow or failing.