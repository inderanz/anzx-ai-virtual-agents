
---

# Cursor Budget Tips & Model Usage (Aligned with Design)

Cursor Pro gives you ~$20/month of frontier model credit + unlimited Auto mode.

### When to use **Auto**
- Small edits, boilerplate rows, file scaffolding (Dockerfiles, requirements)
- Minor changes, import fixes, test stubs
- YAML/JSON generation

### When to use **Premium / Frontier**
- Multi-file scaffolding (e.g. entire router + tool set)
- Complex logic (vector integration, fallback paths)
- Prompt engineering or cross-module refactors
- ADK agent definition with multiple tools and orchestration logic

### Strategies to stay in budget
- Start tasks in Auto; escalate only if Generator fails or reference context is large.
- Split large tasks into atomic ones (Cursor handles small ones better).
- Reuse previously generated code; don’t regenerate large swaths repeatedly.
- Monitor your Cursor credit usage dashboard.
- Pin `docs/tasks.md` and only copy the relevant task into Cursor chat — keeps token use low.


