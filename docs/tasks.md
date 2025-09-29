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

## 12b. Cloudflare Worker deploy that proxies ✅ **COMPLETED**
`/cricket*` → `cricket-chatbot` Cloudflare Pages URL with static asset support.



**IMPLEMENTATION COMPLETED:**
- ✅ No local `gcloud` runs for provisioning. Everything happens inside Cloud Build.
- ✅ Read all Cloudflare values from Secret Manager.
- ✅ Fully automated deployment with Cloud Storage integration.
- ✅ Never echo secrets (token, IDs) in logs.
- ✅ Idempotent: safe to re-run; route and script updated in place.
- ✅ Custom domain working: https://anzx.ai/cricket
- ✅ Static assets proxied: /_next/* and /images/*
- ✅ Enterprise-grade UI/UX deployed

Project constants:
- PROJECT_ID=virtual-stratum-473511-u5
- REGION=australia-southeast1
- STATE_BUCKET=gs://anzx-deploy-state   # already referenced by Task 12b

Secrets (already created with values):
- CLOUDFLARE_API_TOKEN             # token string
- CLOUDFLARE_ACCOUNT_ID            # account id for anzx.ai
- CLOUDFLARE_ZONE_ID               # zone id for anzx.ai
- CLOUDFLARE_WORKER_NAME           # e.g., anzx-cricket-proxy
- CLOUDFLARE_ROUTE_PATTERN         # e.g., anzx.ai/api/cricket*

DELIVERABLES (new/updated files):
1) infrastructure/cloudflare/worker.js
   - A minimal proxy that forwards /api/cricket/* → CRICKET_AGENT_URL (Worker var)
   - CORS: allow-origin https://anzx.ai; allow headers content-type, authorization
   - For OPTIONS requests under /api/cricket/* return 204 with CORS headers.
   - For everything else, passthrough fetch(request).

2) infrastructure/cloudflare/wrangler.toml.tmpl
   - Templated; do NOT hardcode secrets.
   - Fields:
       name = "${CLOUDFLARE_WORKER_NAME}"
       main = "infrastructure/cloudflare/worker.js"
       compatibility_date = "<today in YYYY-MM-DD>"
       account_id = "${CLOUDFLARE_ACCOUNT_ID}"
       routes = [
         { pattern = "${CLOUDFLARE_ROUTE_PATTERN}", zone_id = "${CLOUDFLARE_ZONE_ID}" }
       ]
       [vars]
       CRICKET_AGENT_URL = "${CRICKET_AGENT_URL}"

3) infrastructure/cloudbuild/pipelines/cricket-deploy.yaml (update)
   Add a gated block executed only if `_CLOUDFLARE_DEPLOY == "true"`:
   - Step A: obtain cricket-agent URL (if not already captured). Use:
       gcloud run services describe cricket-agent --region ${_REGION:-australia-southeast1} \
         --format='value(status.url)'
     Save to a file AGENT_URL.txt and export as build env var for following steps.

   - Step B: materialize wrangler.toml from secrets (no echo):
       Read secrets via `gcloud secrets versions access latest --secret=NAME`.
       Render a runtime wrangler.toml by substituting placeholders in the tmpl.
       Ensure we never print the secret values to logs (use env and heredoc without echo).

   - Step C: deploy Worker with wrangler:
       Use `node:lts` step; install wrangler: `npm i -g wrangler@latest`.
       Set env:
         CF_API_TOKEN (from CLOUDFLARE_API_TOKEN secret)
       Run:
         wrangler deploy --config infrastructure/cloudflare/wrangler.toml \
                         --name "$CLOUDFLARE_WORKER_NAME"
       The deploy should be idempotent; if route exists, it updates script.

   - Step D: record Worker info into state JSON:
       Append to the state structure:
         "cloudflare": {
            "worker_name": "...",
            "route_pattern": "...",
            "zone_id": "...",
            "account_id": "...",
            "wrangler_version": "..."
         }
       Then write to ${STATE_BUCKET}/state/deploy-${_DATE:-auto}-${SHORT_SHA}.json
       (Extend the existing write_state step; do not duplicate.)

   Notes:
   - Mask secrets in logs by not echoing them. Use env only for wrangler, remove env after.
   - If any secret missing OR _CLOUDFLARE_DEPLOY != "true", skip Worker steps gracefully and log “Cloudflare Worker deploy skipped”.

4) docs/DEPLOYMENT_GUIDE.md (update)
   Add “Cloudflare Worker (optional)” section:
   - Prereqs: secrets listed above
   - Toggle: set `_CLOUDFLARE_DEPLOY=true` in Cloud Build trigger
   - What it does: proxies https://anzx.ai/api/cricket/* → cricket-agent
   - Validate:
       curl -I https://anzx.ai/api/cricket/healthz
       curl -X POST https://anzx.ai/api/cricket/v1/ask -H 'Content-Type: application/json' -d '{"text":"Ladder for Blue 10s"}'

IMPLEMENTATION DETAILS

A) worker.js minimal content:
- Handle CORS preflight under /api/cricket/*:
    if request.method === 'OPTIONS' → return 204 with CORS headers.
- For /api/cricket/*:
    - Map path by stripping `/api/cricket` prefix.
    - Forward method, headers, and body to `${CRICKET_AGENT_URL}${mappedPath}${search}`.
    - Return response with CORS headers: Access-Control-Allow-Origin: https://anzx.ai
- Else: return fetch(request).

B) wrangler.toml.tmpl rendering:
- Read agent URL from AGENT_URL.txt → env CRICKET_AGENT_URL.
- Fill placeholders with secret values:
    CLOUDFLARE_ACCOUNT_ID, CLOUDFLARE_ZONE_ID, CLOUDFLARE_WORKER_NAME, CLOUDFLARE_ROUTE_PATTERN
- Never print the token. The token is only provided as env CF_API_TOKEN for wrangler.

C) cloudbuild pipeline snippet (pseudo; you generate full steps):
- name: 'gcr.io/google.com/cloudsdktool/cloud-sdk:slim'
  id: 'get-agent-url'
  entrypoint: 'bash'
  args:
    - -lc
    - |
      set -euo pipefail
      URL="$(gcloud run services describe cricket-agent --region ${_REGION:-australia-southeast1} --format='value(status.url)')"
      echo -n "$URL" > AGENT_URL.txt

- name: 'gcr.io/google.com/cloudsdktool/cloud-sdk:slim'
  id: 'render-wrangler-config'
  entrypoint: 'bash'
  args:
    - -lc
    - |
      set -euo pipefail
      [[ "${_CLOUDFLARE_DEPLOY:-false}" == "true" ]] || { echo "skip CF: flag off"; exit 0; }
      CF_ACCOUNT_ID="$(gcloud secrets versions access latest --secret=CLOUDFLARE_ACCOUNT_ID)"
      CF_ZONE_ID="$(gcloud secrets versions access latest --secret=CLOUDFLARE_ZONE_ID)"
      CF_WORKER_NAME="$(gcloud secrets versions access latest --secret=CLOUDFLARE_WORKER_NAME)"
      CF_ROUTE_PATTERN="$(gcloud secrets versions access latest --secret=CLOUDFLARE_ROUTE_PATTERN)"
      AGENT_URL="$(cat AGENT_URL.txt)"
      sed -e "s|\${CLOUDFLARE_ACCOUNT_ID}|$CF_ACCOUNT_ID|g" \
          -e "s|\${CLOUDFLARE_ZONE_ID}|$CF_ZONE_ID|g" \
          -e "s|\${CLOUDFLARE_WORKER_NAME}|$CF_WORKER_NAME|g" \
          -e "s|\${CLOUDFLARE_ROUTE_PATTERN}|$CF_ROUTE_PATTERN|g" \
          -e "s|\${CRICKET_AGENT_URL}|$AGENT_URL|g" \
          infrastructure/cloudflare/wrangler.toml.tmpl > infrastructure/cloudflare/wrangler.toml
      echo "wrangler.toml rendered (values masked)"

- name: 'node:lts'
  id: 'wrangler-deploy'
  entrypoint: 'bash'
  args:
    - -lc
    - |
      set -euo pipefail
      [[ "${_CLOUDFLARE_DEPLOY:-false}" == "true" ]] || { echo "skip CF: flag off"; exit 0; }
      CF_API_TOKEN="$(gcloud secrets versions access latest --secret=CLOUDFLARE_API_TOKEN)"
      export CF_API_TOKEN
      npm i -g wrangler@latest >/dev/null
      WRANGLER_VERSION="$(wrangler --version)"
      echo "Wrangler $WRANGLER_VERSION"
      wrangler deploy --config infrastructure/cloudflare/wrangler.toml --name "$(gcloud secrets versions access latest --secret=CLOUDFLARE_WORKER_NAME)"
      # clean env var to avoid accidental echo
      unset CF_API_TOKEN
      # record worker info for state writer
      echo -n "$WRANGLER_VERSION" > WRANGLER_VERSION.txt

- name: 'gcr.io/google.com/cloudsdktool/cloud-sdk:slim'
  id: 'state-append-cloudflare'
  entrypoint: 'bash'
  args:
    - -lc
    - |
      set -euo pipefail
      [[ "${_CLOUDFLARE_DEPLOY:-false}" == "true" ]] || { echo "skip CF: flag off"; exit 0; }
      CF_ACCOUNT_ID="$(gcloud secrets versions access latest --secret=CLOUDFLARE_ACCOUNT_ID)"
      CF_ZONE_ID="$(gcloud secrets versions access latest --secret=CLOUDFLARE_ZONE_ID)"
      CF_WORKER_NAME="$(gcloud secrets versions access latest --secret=CLOUDFLARE_WORKER_NAME)"
      CF_ROUTE_PATTERN="$(gcloud secrets versions access latest --secret=CLOUDFLARE_ROUTE_PATTERN)"
      WRANGLER_VERSION="$(cat WRANGLER_VERSION.txt)"
      # write a small JSON fragment that your existing write_state.sh can merge or accept as extra env
      cat > cf_state.json <<JSON
      {
        "cloudflare": {
          "worker_name": "$CF_WORKER_NAME",
          "route_pattern": "$CF_ROUTE_PATTERN",
          "zone_id": "$CF_ZONE_ID",
          "account_id": "$CF_ACCOUNT_ID",
          "wrangler_version": "$WRANGLER_VERSION"
        }
      }
      JSON
      # Suggestion: modify write_state.sh to merge this fragment into the main state JSON before uploading.

TESTS / ACCEPTANCE
- `_CLOUDFLARE_DEPLOY=false` (default) → Worker steps skipped; build succeeds.
- With `_CLOUDFLARE_DEPLOY=true` and secrets present:
  - Pipeline renders wrangler.toml without echoing secrets.
  - Wrangler deploys/updates the Worker and route idempotently.
  - State JSON in ${STATE_BUCKET}/state includes a “cloudflare” entry with worker_name, route_pattern, zone_id, account_id, wrangler_version.
  - `curl -I https://anzx.ai/api/cricket/healthz` returns 200 after deploy.

Docs:
- Update docs/DEPLOYMENT_GUIDE.md with a “Cloudflare Worker (optional)” section that shows:
  - Flag `_CLOUDFLARE_DEPLOY=true`
  - Required secrets names
  - Validation curl examples

---

## 12b.1. Cricket Chatbot Deployment - COMPLETED ✅

**ACHIEVEMENTS:**
- ✅ **Enterprise-Grade UI/UX**: Professional cricket chatbot interface with modern design
- ✅ **Fully Automated CI/CD**: Cloud Build pipeline with Cloud Storage integration
- ✅ **Custom Domain**: https://anzx.ai/cricket working with Cloudflare Worker proxy
- ✅ **Static Asset Support**: CSS, JS, and images properly proxied
- ✅ **Zero Manual Intervention**: Complete end-to-end automation

**TECHNICAL IMPLEMENTATION:**
- **Frontend**: Next.js 14 with TypeScript, Tailwind CSS, and enterprise styling
- **Deployment**: Cloudflare Pages with automatic URL capture
- **Custom Domain**: Cloudflare Worker with multiple route patterns
- **CI/CD**: Cloud Storage for URL transfer between build steps
- **Secrets**: Automatic CRICKET_CHATBOT_URL updates

**FILES CREATED/UPDATED:**
- `services/cricket-marketing/` - Complete Next.js application
- `infrastructure/cloudbuild/pipelines/cricket-chatbot-deploy-fixed.yaml` - Automated pipeline
- `infrastructure/cloudflare/worker.js` - Proxy worker with static asset support
- `infrastructure/cloudflare/wrangler.toml.tmpl` - Configuration template
- `scripts/deploy-cricket-chatbot.sh` - Deployment script

**DEPLOYMENT COMMAND:**
```bash
gcloud builds submit --config=infrastructure/cloudbuild/pipelines/cricket-chatbot-deploy-fixed.yaml \
  --substitutions=_PROJECT_ID=virtual-stratum-473511-u5,_REGION=australia-southeast1
```

**RESULT:**
- Custom domain: https://anzx.ai/cricket ✅
- Enterprise-grade UI/UX ✅
- Fully automated deployment ✅
- Static assets working ✅

---

## 12c. CI/CD Bootstrap — Triggers & First Deploy (Cloud Build only, no local CLI)

> **Prerequisites:** Task 12b (Cloudflare Worker) must be completed first.

**Goal:** Provision everything via Cloud Build jobs (no laptop `gcloud`, no Terraform).  
We commit infra-as-code to the repo, then run a single **bootstrap pipeline** from the Cloud Build UI.  
This bootstrap pipeline:
- Enables required GCP APIs (idempotent)
- Creates state bucket if missing
- Creates Artifact Registry repo
- Creates service accounts & IAM roles
- Creates required Secret Manager secrets if missing (placeholders; DO NOT overwrite existing)
- Creates GitHub trigger for main pipeline (cricket-deploy)
- Builds & deploys `cricket-agent` and `cricket-bridge`
- (Optional) Deploys Cloudflare Worker if `_CLOUDFLARE_DEPLOY=true` and secrets exist
- Writes deployment state JSON to GCS (`gs://anzx-deploy-state/state/...`)

**Inputs (fixed):**
- PROJECT_ID: `virtual-stratum-473511-u5`
- REGION: `australia-southeast1`
- ARTIFACT_REPO: `anzx-agents`
- STATE_BUCKET: `gs://anzx-deploy-state`
- REPO: `github.com/inderanz/anzx-ai-virtual-agents`
- BRANCH: `main`

**Files added by this task:**
- `infrastructure/cloudbuild/pipelines/cricket-bootstrap.yaml` — one-shot bootstrap pipeline
- `infrastructure/cloudbuild/triggers/cricket-deploy.trigger.json` — trigger *as code* (referenced by bootstrap)
- `infrastructure/scripts/gcb_assert.sh` — idempotent helpers (create-if-missing)
- `infrastructure/scripts/write_state.sh` — state JSON writer to GCS
- (ensures) `infrastructure/cloudbuild/pipelines/cricket-deploy.yaml` — main pipeline from Task 12b

**Bootstrap pipeline stages (cricket-bootstrap.yaml):**
1) **APIs:** enable `run, artifactregistry, secretmanager, cloudbuild, cloudscheduler, aiplatform, iam, serviceusage`
2) **GCS:** create `anzx-deploy-state` bucket if missing (`gsutil mb` idempotent)
3) **Artifact Registry:** ensure repo `${ARTIFACT_REPO}` exists in `${REGION}`
4) **SAs & IAM (idempotent):**
   - `sa-cricket-agent`, `sa-cricket-bridge`
   - IAM bindings for Cloud Build SA and service SAs:
     - `roles/run.admin`, `roles/iam.serviceAccountAdmin`, `roles/iam.serviceAccountUser`
     - `roles/artifactregistry.admin`, `roles/secretmanager.admin`, `roles/cloudscheduler.admin`
     - `roles/storage.admin`, `roles/serviceusage.serviceUsageAdmin`, `roles/aiplatform.user`, `roles/logging.logWriter`
5) **Secrets (create-if-missing):**
   - `CSCC_IDS`, `CRICKET_INTERNAL_TOKEN` (generate base64 if missing)
   - Optional: `PLAYHQ_X_API_KEY`, `WHATSAPP_SESSION`, `CLOUDFLARE_*`
6) **Create GitHub Trigger (idempotent)** for `cricket-deploy`:
   - Source: repo `inderanz/anzx-ai-virtual-agents`, branch `^main$`
   - Build config: `infrastructure/cloudbuild/pipelines/cricket-deploy.yaml`
   - Default substitutions:  
     `_REGION=australia-southeast1`, `_BRIDGE_SESSION_BACKEND=NONE`, `_CLOUDFLARE_DEPLOY=false`
7) **(Optional) First run of main deploy**:
   - Kick `cricket-deploy` pipeline via `gcloud builds triggers run` (if created successfully)
8) **Write state to GCS** (image digests, URLs, revisions, trigger id, timestamp, Git SHA)

**One-time manual action (in console, not laptop CLI):**
- Open **Cloud Build → Builds → Run build**  
  - Config file: `infrastructure/cloudbuild/pipelines/cricket-bootstrap.yaml`  
  - Substitutions (optional): `_CLOUDFLARE_DEPLOY=true` if CF secrets already exist

**Acceptance:**
- After the bootstrap build completes:
  - A Cloud Build **trigger** named `cricket-deploy` exists
  - The **main pipeline** runs (via trigger) and deploys services
  - GCS state JSON is present at `gs://anzx-deploy-state/state/deploy-*.json`
  - Re-running bootstrap is **idempotent** (no errors on “already exists”)


## 13. Marketing Site — Scaffold & Dependencies (anzx.ai landing page)

Go though all tasks from 1-12 and the the code & ensuring without breaking existing feature start of task 13 

> This task creates the **enterprise marketing website for anzx.ai** — the public-facing landing page at **https://anzx.ai**.  
> It must match the polish, UX, and performance grade of [bixie.ai](https://www.bixie.ai) (patterns only; no text/assets copied).  
> **Single CI/CD system:** Google **Cloud Build** for both CI (tests/quality gates) and CD (deploy to Cloudflare Pages).

### Scope
- Create new service: `services/marketing-site`
- This site **is the landing page of anzx.ai** and becomes the single entry point for all platform messaging.
- Integrates platform-wide positioning **“Intelligent Enterprise Teammate”** and features the **Cricket Agent** as an example solution.
- Make it clear users can integrate ANZx agents into **their websites**, **WhatsApp**, or **use directly on anzx.ai**.

### Deliverables
1. **Scaffold app** with Next.js 14 (App Router) + TypeScript + Tailwind + shadcn/ui
2. **Global UI:** Header, footer, theme, reusable components
3. **Routes/pages:**
   - `/` (Home, hero with **“One platform. Many AI Teammates.”**)
   - `/pricing`
   - `/about`
   - `/contact`
   - `/legal/*` (privacy, terms, cookies in MDX)
   - `/status` (external link)
   - `/(auth)` route group prepared
4. **Copy & Content:**
   - All text centralized in `/content/site.ts`
   - Hero H2: **“An AI agents workforce for support, accounting, admin, sports, content, and insights — ready to work alongside you every day.”**
   - Consistent **cloud-native** and **enterprise-ready** phrasing (never say Google Cloud)
   - Include **Featured solution: Cricket Agent** tile on Home and card on About
5. **SEO & Analytics:**
   - `next-sitemap`, robots.txt, JSON-LD, OG/Twitter meta
   - Consent banner gating GA4 + PostHog

### CI (Cloud Build) — Quality Gates
- Add **CI pipeline**: `infrastructure/cloudbuild/pipelines/site-ci.yaml`
  - Runs on PRs and `main` (via trigger).
  - Steps (in `services/marketing-site`):
    1. Install with `pnpm` (with cache).
    2. Lint (`pnpm lint`) + typecheck (`pnpm typecheck`).
    3. Unit tests (Vitest + RTL) → upload JUnit to GCS artifacts.
    4. Build (`pnpm build`).
    5. Start a local server and run **Playwright e2e** (keyboard nav, pricing toggle, contact submit, cookie reject, axe scan 0 critical).
    6. **Lighthouse CI** (mobile) against `/` and `/pricing` with budgets:
       - Performance ≥ 90, Accessibility ≥ 95, Best Practices ≥ 95, SEO ≥ 95.
    7. Upload all artifacts (Playwright traces/videos, LHCI reports) to `${_STATE_BUCKET}/artifacts/site-ci/<date>-<sha>/`.
  - Add CI trigger: `infrastructure/cloudbuild/triggers/site-ci.trigger.json`
    - Source: `inderanz/anzx-ai-virtual-agents`
    - Branch: `.*` (PRs and main)
    - Subs: `_SITE_DIR=services/marketing-site`, `_STATE_BUCKET=gs://anzx-deploy-state`

### CD (Cloud Build) — Deploy to Cloudflare Pages
- Add **deploy pipeline**: `infrastructure/cloudbuild/pipelines/site-deploy.yaml`
  - Build the site with `pnpm`.
  - Prefer static export with `next export` → `.out` (or Pages Functions via `.vercel/output` if needed).
  - Read secrets from **Secret Manager**: `CLOUDFLARE_API_TOKEN`, `CLOUDFLARE_ACCOUNT_ID` (do **not** echo).
  - Use `node:lts` and `npm i -g wrangler@latest`.
  - `wrangler pages project create anzx-marketing` (idempotent).
  - `wrangler pages deploy .out --project-name=anzx-marketing --branch=main`.
  - Write deployment state JSON to `${_STATE_BUCKET}/state/marketing-<date>-<sha>.json`.
- Add deploy trigger: `infrastructure/cloudbuild/triggers/site-deploy.trigger.json`
  - Source: `inderanz/anzx-ai-virtual-agents`
  - Branch: `^main$`
  - Subs: `_SITE_DIR=services/marketing-site`, `_STATE_BUCKET=gs://anzx-deploy-state`

### Acceptance
- Local: `pnpm i && pnpm dev` runs; `pnpm build` passes with **0 TypeScript errors**.
- **Cloud Build CI** passes on PRs and main:
  - Lint / Typecheck ✅
  - Unit ✅
  - Build ✅
  - Playwright e2e (incl. axe 0 critical) ✅
  - Lighthouse budgets met on `/` & `/pricing` ✅
  - Artifacts uploaded to GCS ✅
- **Cloud Build Deploy** succeeds idempotently:
  - Cloudflare Pages updated (`anzx-marketing`).
  - State JSON written to GCS.
- Site serves with CSP nonce headers; no inline scripts; cookie consent gates analytics.
- SEO files (sitemap/robots) and OG/Twitter tags present.



## 14. Marketing Site — Copy & SEO

### Scope
- Replace placeholders with **production-ready copy**:
  - Hero H1: **“One platform. Many AI Teammates.”**
  - Hero H2: **“An AI agents workforce for support, accounting, admin, sports, content, and insights — ready to work alongside you every day.”**
  - Feature cards: Support, Admin, Content, Insights, Secure by Design, Cloud-native Architecture
  - KPI band: metrics (`<30s per invoice`, `99% extraction accuracy`, `3 min setup`) as placeholders in `/content/site.ts`
  - Cricket Agent tile (Home) and blurb (About)
- Ensure **all text** lives in `/content/site.ts` (centralized for localization).
- Write legal pages (`/legal/privacy`, `/legal/terms`, `/legal/cookies`) in **MDX** with “Last updated” + AU jurisdiction placeholders.

### SEO
- Add `next-sitemap` and generate `/sitemap.xml`, `/robots.txt`.
- Add OpenGraph + Twitter meta tags for Home, Pricing, About.
- Add canonical URLs via `lib/seo.ts`.
- Add JSON-LD structured data:
  - `Organization`
  - `WebSite`
  - `Product` (AI teammate platform)
- Verify OG preview and Twitter cards render correctly.

### Acceptance
- Copy is concise, professional, and **no lorem ipsum**.
- All editable values are centralized in `/content/site.ts`.
- SEO passes Lighthouse (SEO ≥ 95).
- OG/Twitter cards render correctly when shared.

---

## 15. Marketing Site — Consent, Analytics & Testing

### Scope
- Implement **cookie consent banner**:
  - Blocks GA4 + PostHog until consent.
  - Buttons: “Accept all” / “Reject all”.
  - “Reject all” disables all analytics calls.
- Add GA4 + PostHog stubs (consent-gated).
- Ensure **no analytics loads without consent**.

### Testing
- Add unit tests:
  - `FeatureCard`, `Timeline`, `PriceCard`, `FAQList`, `Contact form validation`.
- Add Playwright e2e tests:
  1. Header nav traversal with keyboard (Tab/Shift+Tab).
  2. Pricing toggle Monthly/Annual.
  3. Contact form submit → success toast.
  4. Cookie banner “Reject all” → assert GA/PostHog not called.
  5. Axe scan: **0 critical a11y violations**.
- Add Lighthouse CI runs (via GitHub Actions):
  - Pages: `/` and `/pricing`.
  - Mobile thresholds: Perf ≥90, A11y ≥95, BP ≥95, SEO ≥95.

### Acceptance
- Consent banner works in all flows.
- All Playwright tests pass.
- Lighthouse CI passes thresholds.
- Axe scan returns 0 critical violations.

---

## 16. Marketing Site — CI/CD (Cloud Build only)

> **Single CI/CD system = Cloud Build.**  
> CI validates (install, lint, typecheck, unit, build, e2e, Lighthouse).  
> CD deploys to **Cloudflare Pages** via Wrangler (optional Worker proxy already covered in Task 12b).

### 16a. **Cloud Build CI** (source of truth; runs on PRs & main)
**Files to add:**
- `infrastructure/cloudbuild/pipelines/site-ci.yaml`
- `infrastructure/cloudbuild/triggers/site-ci.trigger.json`

**site-ci.yaml** — must:
- Use Node LTS and Playwright container.
- Steps:
  1) `pnpm install` (with cache) in `services/marketing-site`
  2) Lint (`pnpm lint`) + Typecheck (`pnpm typecheck`)
  3) Unit tests (`pnpm test`) — export JUnit to `artifacts/`
  4) Build (`pnpm build`)
  5) Playwright e2e (serve dev, wait-on, run tests, kill dev)
  6) Lighthouse CI on built site (serve `.next`, lhci collect/assert with mobile budgets)
  7) Upload artifacts to `${_STATE_BUCKET}/artifacts/site-ci/<date>-<sha>/`
- No secrets required; **no deploy** here.

**site-ci.trigger.json** — must:
- GitHub source: repo `inderanz/anzx-ai-virtual-agents`
- Branch regex: `.*` (PRs and main)
- Substitutions:
  - `_SITE_DIR=services/marketing-site`
  - `_STATE_BUCKET=gs://anzx-deploy-state`
- Filename: `infrastructure/cloudbuild/pipelines/site-ci.yaml`

### 16b. **Cloud Build Deploy** (to Cloudflare Pages)
**Files** (ensure present / updated):
- `infrastructure/cloudbuild/pipelines/site-deploy.yaml`
- `infrastructure/cloudbuild/triggers/site-deploy.trigger.json`

**site-deploy.yaml** — must:
- Build `services/marketing-site` with `pnpm`.
- Prefer `next export` → `.out` (static). If Pages Functions required, package `.vercel/output`.
- Read secrets from Secret Manager:
  - `CLOUDFLARE_API_TOKEN`, `CLOUDFLARE_ACCOUNT_ID`
- Use `node:lts` and `npm i -g wrangler@latest`
- Create project if missing: `wrangler pages project create anzx-marketing` (ignore if exists)
- Deploy: `wrangler pages deploy .out --project-name=anzx-marketing --branch=main`
- **Never** echo secrets. Use env var `CF_API_TOKEN` only for deploy step; unset afterward.
- Write deploy state JSON to `${_STATE_BUCKET}/state/marketing-<date>-<sha>.json`

**site-deploy.trigger.json** — must:
- Source: repo `inderanz/anzx-ai-virtual-agents`, branch `^main$`
- Filename: `infrastructure/cloudbuild/pipelines/site-deploy.yaml`
- Subs:
  - `_SITE_DIR=services/marketing-site`
  - `_STATE_BUCKET=gs://anzx-deploy-state`

### 16c. Docs
- Update `docs/DEPLOYMENT_GUIDE.md`:
  - “Marketing Site CI” (Cloud Build) — how it runs on PRs & main, where artifacts are uploaded.
  - “Marketing Site Deploy” — Trigger on `main`, how to verify:
    - Pages URL from Wrangler output
    - `curl -I https://anzx.ai` (after DNS/Pages connected)
    - Check CSP headers, sitemap, robots, OG tags.
- Include troubleshooting (common Playwright/LHCI issues, caching notes).

---

### Deliverables (Tasks 13–16)
- `services/marketing-site/` (full app):
  - `app/(site)/layout.tsx`, `app/(site)/page.tsx`, `pricing/page.tsx`, `about/page.tsx`, `contact/page.tsx`, `status/page.tsx`
  - `app/legal/privacy/page.mdx`, `app/legal/terms/page.mdx`, `app/legal/cookies/page.mdx`
  - `app/api/contact/route.ts`
  - `components/*`, `content/site.ts`, `lib/seo.ts`, `lib/csp.ts`, `lib/validators.ts`
  - `public/logos/*`, `styles/globals.css`
  - `playwright.config.ts`, `vitest.config.ts`, `lighthouserc.json`
  - `package.json`, `next.config.js`, `postcss.config.js`, `tailwind.config.ts`, `tsconfig.json`, `.eslintrc.js`, `.prettierrc`, `.env.example`, `README.md`
- Cloud Build CI:
  - `infrastructure/cloudbuild/pipelines/site-ci.yaml`
  - `infrastructure/cloudbuild/triggers/site-ci.trigger.json`
- Cloud Build Deploy:
  - `infrastructure/cloudbuild/pipelines/site-deploy.yaml`
  - `infrastructure/cloudbuild/triggers/site-deploy.trigger.json`
- Docs:
  - `docs/DEPLOYMENT_GUIDE.md` (CI + Deploy sections)

### Acceptance (CI/CD)
- **CI (Cloud Build)** passes on PRs and main:
  - Lint / Typecheck: ✅
  - Unit: ✅
  - Build: ✅
  - Playwright e2e: ✅
  - LHCI budgets met on `/` & `/pricing`: Perf ≥ 90, A11y ≥ 95, BP ≥ 95, SEO ≥ 95
  - Artifacts uploaded to `gs://anzx-deploy-state/artifacts/site-ci/...`
- **Deploy (Cloud Build)**:
  - Pages deploy succeeds idempotently (project autocreated if missing)
  - State JSON written to `gs://anzx-deploy-state/state/marketing-*.json`
  - Site reachable via Cloudflare Pages with CSP headers and SEO files present