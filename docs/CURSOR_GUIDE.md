# Cursor Guide — anzx-ai-virtual-agents (Cricket Feature)

This file defines **constraints, rules, and style** for using Cursor with the Caroline Springs CC Cricket Agent.  
All code generated or modified by Cursor must follow these guidelines to remain consistent with the repo architecture.

---

## 1. Language & Versions

**Python Services**  
- Python: 3.10 or 3.11  
- FastAPI: 0.95.x  
- google-cloud-aiplatform[adk,agent_engine] >=1.112.0  

**Node Services (WhatsApp bridge)**  
- Node: 20.x LTS  
- Baileys: ^6.7.0  
- Express: ^4.18.0  
- Axios: ^1.7.0  
- TypeScript: ^5.5.0  

---

## 2. Repository Structure Rules  

- **New code must live under:**  
  - `/services/cricket-agent`  
  - `/services/cricket-bridge`  

- **Do not:**  
  - Create a top-level `agents/` directory  
  - Modify unrelated services (except for API proxy additions, e.g. core-api → `/cricket`)  

---

## 3. Model & Library Constraints  

- Use **Google Vertex AI**, not OpenAI.  
- Use **`google-cloud-aiplatform`** and **ADK plugins** for agents.  
- Use ADK’s `Agent` and tool definitions where applicable.  
- Deploy only to **Cloud Run** or **Vertex Agent Engine**.  

**PlayHQ API Rules**  
- Use **PlayHQ API v1** (public) with required headers:  
  - `x-api-key`  
  - `x-phq-tenant`  
- Always handle **pagination** (`cursor`, `metadata.hasMore`).  

---

## 4. Prompting Style (for Cursor)  

- **Auto mode** → default; use for small changes (functions, fixes).  
- **Premium (Gemini) mode** → only for:  
  - Multi-file scaffolding  
  - Logic-heavy generation (routers, embedding pipeline)  
- Always provide context in prompts, e.g.:  
  - “This is a Vertex AI + ADK project, use Secret Manager, place code under `/services/cricket-agent`, do not import openai.”  

---

## 5. Testing & Validation  

- Ensure `tests/` folders exist under services.  
- Use **mock PlayHQ JSON files** for test validation.  
- Validate request/response via **OpenAPI spec**.  
- Run tests locally before deploy:  
  - Python: `pytest`  
  - Node: `npm test`  

---

## 6. Budget Guidance  

- Use **Auto mode** for small edits.  
- Reserve **Premium mode** for generators, routers, or major refactors.  
- Break work into small, iterative requests.  
- Monitor usage in Cursor dashboard; if hitting limits → switch back to Auto.  

---

## 7. Do’s & Don’ts  

**✅ Do’s**  
- Use ADK agent + tools.  
- Use PlayHQ API v1 with proper headers & pagination.  
- Fetch secrets from **Secret Manager**.  
- Follow repo structure: `/services/cricket-agent`, `/services/cricket-bridge`.  

**❌ Don’ts**  
- Don’t import `openai`.  
- Don’t hardcode credentials.  
- Don’t create `agents/` folder at repo root.  

---
