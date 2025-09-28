# Caroline Springs CC Real-Time Cricket Agent — System Design

## 1. Overview & Goals  

We are building a specialized chatbot agent for **Caroline Springs Cricket Club**, powered by **PlayHQ APIs** and **Google Vertex AI**. The agent answers questions on fixtures, player stats, ladder positions, rosters, and results. It will be available via:  

- **Web chat** → `/cricket`  
- **WhatsApp bridge** → powered by Baileys  

Key design goals:  
- Provide **grounded answers** (no hallucinations).  
- Maintain **low latency** (p50 < 3s).  
- Follow **Google Cloud best practices** (Vertex AI, Workload Identity, Secret Manager, Cloud Run).  
- Be **secure, extensible, and maintainable** for other clubs in future.  

---

## 2. Versions & Compatibility  

**Python Services**  
- Python: 3.10 / 3.11  
- FastAPI: 0.95.x  
- Uvicorn: 0.24.x  
- google-cloud-aiplatform: [adk, agent_engine] >=1.112.0,<2.0  
- google-cloud-secret-manager: >=2.20.0  
- google-cloud-logging: >=3.10.0  
- httpx: >=0.25,<0.30  
- pydantic: >=2.5,<3.0  
- tenacity: >=9,<10  
- orjson: >=3.10  
- pytest: >=8,<9  

**Node Services (WhatsApp bridge)**  
- Node.js: 20.x LTS  
- Baileys (WhatsApp): ^6.7.0  
- Express: ^4.18.0  
- Axios: ^1.7.0  
- TypeScript: ^5.5.0  
- tsx: ^4.17.0  

**External APIs**  
- PlayHQ API v1 (Public External API, cursor pagination)  

---

## 3. Architecture Overview  

```text
[User: Web (/cricket)]                 [WhatsApp Group]
        |                                        |
        |  HTTPS (JSON; fetch/SSE)               |  WebSocket/MD session (Baileys)
        v                                        v
+------------------------+            +---------------------------+
|  Website Frontend      |            |  services/cricket-bridge |  Node 20 + Baileys ^6.7
|  (website/*)           |            |  (Cloud Run, 1+ min inst)|  /healthz, /relay
+------------+-----------+            +---------------------------+
             \                                 /
              \  HTTP (REST/JSON)             /
               \_____________________________/
                              |
                              v
                    +--------------------------+
                    |  services/cricket-agent |  Python 3.11 + FastAPI 0.95
                    |  (Cloud Run; ADK/Vertex)|  /v1/ask, /internal/refresh
                    +------------+-------------+
                                 |
                   ┌─────────────┴──────────────┐
                   v                            v
         +----------------------+      +------------------------+
         | Retrieval / RAG      |      |  PlayHQ Data Sync     |
         | (Vertex RAG Managed  |      |  (nightly + matchday  |
         |  DB; fallback: KS)   |      |   + on-demand)        |
         +----------+-----------+      +-----------+------------+
                    |                               |
                    v                               v
        +---------------------------+     +----------------------------+
        | Embeddings + Chunks       |     | Raw + Normalized Records  |
        | (Vertex RAG / Matching    |     | (GCS buckets; JSON/Parquet|
        | Engine; or knowledge-svc) |     |  optional: Firestore/SQL) |
        +---------------------------+     +----------------------------+
## Supporting Infrastructure  

- **Secrets**: PlayHQ x-api-key, tenant/org/season IDs, internal tokens → Secret Manager  
- **Identity**: Cloud Run service accounts with Workload Identity (no JSON keys)  
- **Monitoring**: Cloud Logging, Error Reporting, metrics/alerts  

---

## 4. Data Sources & APIs  

- **PlayHQ Public APIs**  
  - Endpoints: `/games`, `/summary/:gameId`, `/ladder/:gradeId`  
  - Pagination: `cursor` + `metadata.hasMore`  
  - Headers: `x-api-key`, `x-phq-tenant`  

- **Private APIs & Webhooks** (future, approval required)  

- **Live Scoring Webhooks** (if enabled by PlayHQ)  
  - Subscriptions can be filtered by entity (team, competition, venue)  

---

## 5. Agent & Tools  

- Built with **ADK-based agent** (Python, Vertex AI)  
- Tools:  
  - `playhq_client` → REST client for fixtures, ladders, summaries  
  - `vector_client` → Vertex RAG (retrieval + embeddings)  
  - `sync` → refresh jobs (nightly/matchday/on-demand)  
- Vector store: **Vertex RAG Managed DB** (preferred)  

---

## 6. Security & IAM  

- Secrets in **Secret Manager**  
- Workload Identity for service-to-service auth  
- No personal credentials stored  
- Respect PlayHQ visibility: do not leak hidden teams/players  
- Logs must exclude secrets & PII  

---

## 7. Update Strategy  

- **Nightly + matchday syncs**  
- **Delta updates** (hash-based content change detection)  
- **Webhook ingestion** (for real-time live scoring, if enabled)  

---

## 8. Deployment & Scaling  

- `cricket-agent` → Python + FastAPI → Cloud Run  
- `cricket-bridge` → Node + Baileys → Cloud Run  
- Auto-scaling via GCP infra  
- Logging & monitoring via Cloud Logging & Error Reporting  

---

## 9. Implementation Guide  

### Service Contracts  

**cricket-agent**  
- `POST /v1/ask` → handle user queries  
- `POST /internal/refresh` → trigger sync  
- `GET /healthz`  

**cricket-bridge**  
- `POST /relay` → forward WhatsApp messages  
- `GET /healthz`  

### Request Lifecycle  

1. `/v1/ask` receives input → route via regex + Gemini  
2. Query vector DB → fallback: PlayHQ client  
3. Normalize + embed + upsert (async)  
4. Generate answer (Gemini or deterministic)  
5. Return `{answer, latency, intent}`  

### Data Contracts  

Entities: **Team**, **Fixture**, **Scorecard**, **Ladder**, **Roster**  
(see schema section in repo)  

### Freshness & Caching  

- Cache hot queries (10–30 mins)  
- Auto-refresh ladder/results >2h stale  
- Re-embed only when content hash changes  

### Error Handling  

- Retries/backoff on PlayHQ 429/5xx  
- Graceful fallback responses  
- Baileys auto-reconnect; session persisted in GCS/Secret Manager  

### Observability  

- Structured logs: `{request_id, source, intent, tool_times, tokens, latency}`  
- Metrics: latency, RAG hit rate, PlayHQ errors  
- Alerts: p95 >5s, sync failures, >2% PlayHQ errors  

### WhatsApp Bridge  

- Node 20.x + Baileys  
- Session persisted in GCS/Secret Manager  
- Responds to `!cscc` prefix or @mention  

---

## 10. Canonical Queries  

Router implements these six baseline queries (deterministic where possible):  
1. Which team a player belongs to  
2. Runs scored in last match  
3. Fixtures list  
4. Ladder position  
5. Next fixture details  
6. Team roster  

---

## Final Notes  

This design is aligned with:  
- **PlayHQ API v1** (public/private/webhooks)  
- **Google Vertex AI ADK & Agent Engine**  
- **Cloud Run deployment model**  


