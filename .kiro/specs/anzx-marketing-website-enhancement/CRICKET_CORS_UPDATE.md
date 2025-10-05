# Optional: Tighten CORS for Cricket Agent

## Current Configuration

The cricket agent currently allows **all origins**:
```python
allow_origins=["*"]  # Allow all origins for development
```

## Recommended Production Configuration

For better security, restrict CORS to only your domains:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://cricket.anzx.ai",
        "https://d1e8b1c8.anzx-cricket.pages.dev",  # Direct Pages URL
        "http://localhost:3000",  # Local development
        "http://localhost:3001",  # Local development
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## How to Update

1. Edit `services/cricket-agent/app/main.py`
2. Replace the CORS middleware configuration (around line 100)
3. Redeploy the cricket agent:
   ```bash
   gcloud builds submit --config=infrastructure/cloudbuild/cricket-agent.yaml
   ```

## Why This Matters

- **Security**: Prevents other websites from calling your API
- **Cost Control**: Reduces unauthorized API usage
- **Best Practice**: Production apps should have restricted CORS

## Current Status

✅ **Working**: The current `allow_origins=["*"]` configuration works fine
⚠️ **Optional**: Tightening CORS is a security best practice but not required

## When to Update

- Before going to production
- If you notice unauthorized API usage
- As part of security hardening

---

**Note**: The current configuration works perfectly. This is just an optional security enhancement.
