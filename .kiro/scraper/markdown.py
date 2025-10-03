#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Generate Markdown backlog from pages_summary.json.
- Per-page .md files (default) OR a single combined .md
- Uses an LLM (OpenAI) to produce structured issues, or a deterministic fallback with --no-llm
- No GitHub calls; purely local files

Usage examples:
  # Per-page Markdown files (default)
  python gen_markdown.py --summary out_teammates/pages_summary.json --out-dir backlog_md

  # Single README.md with everything
  python gen_markdown.py --summary out_teammates/pages_summary.json --out-dir backlog_md --single-file

  # Deterministic fallback (no LLM)
  python gen_markdown.py --summary out_teammates/pages_summary.json --out-dir backlog_md --no-llm

Env (only if using LLM):
  OPENAI_API_KEY
"""

import argparse
import json
import os
import re
import time
from pathlib import Path
from typing import List, Optional

from pydantic import BaseModel, Field

# ---------- Models (same shape as earlier script) ----------

class DevTask(BaseModel):
    task: str
    estimate: str = Field(..., pattern="^(small|medium|large)$")

class BackendSpec(BaseModel):
    method: str
    path: str
    request: Optional[str] = None
    response: Optional[str] = None

class IssueOut(BaseModel):
    title: str
    user_story: str
    acceptance_criteria: List[str]
    dev_tasks: List[DevTask]
    components: List[str]
    backend: List[BackendSpec]

# ---------- Utils ----------

def slugify(text: str, max_len: int = 80) -> str:
    text = text.strip().lower()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[\s_-]+", "-", text)
    text = text.strip("-")
    return text[:max_len] or "issue"

def safe_title(s: str) -> str:
    return s.replace("\n", " ").strip()

# ---------- LLM generation (optional) ----------

def openai_generate_issues(model: str, page_record: dict, temperature: float = 0.2) -> List[IssueOut]:
    from openai import OpenAI
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY not set")
    client = OpenAI(api_key=api_key)

    url = page_record.get("url", "")
    ext = page_record.get("extracted", {}) or {}
    title = ext.get("title") or ""
    h1 = ext.get("h1") or ""
    meta = ext.get("meta_description") or ""
    forms = ext.get("forms", [])
    links = ext.get("links", [])[:20]

    html_path = page_record.get("html_path")
    html_sample = ""
    try:
        with open(html_path, "r", encoding="utf-8", errors="ignore") as f:
            html_sample = f.read(3000)
    except Exception:
        pass

    sys_prompt = (
        "You are a senior product-engineering assistant. Convert a web page description into a small set "
        "of actionable development issues for rebuilding the page in a modern stack (Next.js + React + Tailwind + React Query; Node/FastAPI backend).\n"
        "Rules:\n"
        "- Do NOT copy the site's text; use neutral placeholders.\n"
        "- Keep to 1–3 issues per page.\n"
        "- Estimates: small, medium, or large only.\n"
        "- If static, backend can be [].\n"
        "- Return JSON object with key 'issues' as an array. No prose."
    )

    user_prompt = {
        "url": url,
        "page_title": title,
        "h1": h1,
        "meta_description": meta,
        "forms_summary": [
            {
                "action": f.get("action"),
                "method": f.get("method"),
                "inputs_count": len(f.get("inputs", []))
            } for f in (forms or [])
        ],
        "notable_links": links,
        "html_sample": html_sample
    }

    schema_hint = (
        "JSON schema:\n"
        "{\"issues\":[{\"title\":\"string\",\"user_story\":\"string\",\"acceptance_criteria\":[\"...\"],"
        "\"dev_tasks\":[{\"task\":\"string\",\"estimate\":\"small|medium|large\"}],"
        "\"components\":[\"...\"],"
        "\"backend\":[{\"method\":\"GET|POST|PUT|DELETE\",\"path\":\"/api/...\",\"request\":\"optional\",\"response\":\"optional\"}]}]}"
    )

    msgs = [
        {"role": "system", "content": sys_prompt},
        {"role": "user", "content": "Page record (summarized):\n" + json.dumps(user_prompt, ensure_ascii=False, indent=2)},
        {"role": "user", "content": schema_hint}
    ]

    resp = client.chat.completions.create(
        model=model,
        temperature=temperature,
        messages=msgs,
        response_format={"type": "json_object"},
    )
    raw = resp.choices[0].message.content
    data = json.loads(raw)
    issues_raw = data.get("issues", [])
    issues = [IssueOut(**i) for i in issues_raw]
    return issues

# ---------- Deterministic fallback ----------

def fallback_issues(page_record: dict) -> List[IssueOut]:
    url = page_record.get("url", "")
    ext = page_record.get("extracted", {}) or {}
    page_title = (ext.get("title") or ext.get("h1") or "Rebuild page").strip()[:120]

    issue = IssueOut(
        title=f"Rebuild: {page_title}",
        user_story=f"As a visitor, I want to use the page at {url} so I can learn and act.",
        acceptance_criteria=[
            "Responsive layout (mobile & desktop)",
            "Primary call-to-action present and working",
            "SEO head tags set (title, meta description)",
            "Basic analytics event on page view"
        ],
        dev_tasks=[
            DevTask(task="Create Next.js route & page component", estimate="small"),
            DevTask(task="Implement layout with Tailwind and reusable components", estimate="medium"),
            DevTask(task="Add SEO head tags (title/meta)", estimate="small"),
            DevTask(task="Add unit/snapshot test", estimate="small"),
        ],
        components=["PageLayout", "Header", "Footer", "PrimaryCTA"],
        backend=[]
    )
    return [issue]

# ---------- Markdown rendering ----------

def render_issue_md(page_record: dict, issue: IssueOut) -> str:
    url = page_record.get("url", "")
    html_path = page_record.get("html_path", "")
    shot_path = page_record.get("screenshot_path", "")
    har_path = page_record.get("har_path", "")

    lines = []
    lines.append(f"# {safe_title(issue.title)}")
    lines.append("")
    lines.append(f"**Source page:** {url}")
    lines.append("")
    lines.append("## User story")
    lines.append(issue.user_story)
    lines.append("")
    lines.append("## Acceptance criteria")
    for ac in issue.acceptance_criteria:
        lines.append(f"- [ ] {ac}")
    lines.append("")
    if issue.components:
        lines.append("## Components")
        lines.append(", ".join(f"`{c}`" for c in issue.components))
        lines.append("")
    if issue.backend:
        lines.append("## Backend endpoints")
        for b in issue.backend:
            lines.append(f"- **{b.method} {b.path}**")
            if b.request:
                lines.append(f"  - Request: `{b.request}`")
            if b.response:
                lines.append(f"  - Response: `{b.response}`")
        lines.append("")
    if issue.dev_tasks:
        lines.append("## Dev tasks")
        for t in issue.dev_tasks:
            lines.append(f"- [ ] {t.task} _(estimate: {t.estimate})_")
        lines.append("")
    lines.append("## Artifacts")
    lines.append(f"- HTML: `{html_path}`")
    lines.append(f"- Screenshot: `{shot_path}`")
    lines.append(f"- HAR: `{har_path}`")
    lines.append("")
    return "\n".join(lines)

def render_index_md(index_items: List[dict]) -> str:
    lines = []
    lines.append("# ANZX Backlog")
    lines.append("")
    lines.append("> Auto-generated from `pages_summary.json`. Each item links to a Markdown spec.")
    lines.append("")
    lines.append("| Page | Issue Title | File |")
    lines.append("|------|-------------|------|")
    for item in index_items:
        lines.append(f"| {item['page']} | {item['title']} | [{item['file']}]({item['file']}) |")
    lines.append("")
    return "\n".join(lines)

# ---------- Main ----------

def main():
    ap = argparse.ArgumentParser(description="Create Markdown backlog from pages_summary.json")
    ap.add_argument("--summary", required=True, help="Path to pages_summary.json")
    ap.add_argument("--out-dir", required=True, help="Directory to write .md files")
    ap.add_argument("--model", default="gpt-4o-mini", help="OpenAI model (when not using --no-llm)")
    ap.add_argument("--no-llm", action="store_true", help="Use deterministic fallback (no OpenAI)")
    ap.add_argument("--max-pages", type=int, default=None, help="Limit number of page records processed")
    ap.add_argument("--single-file", action="store_true", help="Write a single README.md instead of per-page files")
    ap.add_argument("--file-prefix", default="anzx", help="Filename prefix for per-page files")
    args = ap.parse_args()

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    with open(args.summary, "r", encoding="utf-8") as f:
        pages = json.load(f)
    if not isinstance(pages, list) or not pages:
        raise SystemExit("pages_summary.json is empty or invalid")

    combined_lines = []
    index_rows = []
    processed = 0

    for page in pages:
        if args.max_pages and processed >= args.max_pages:
            break

        url = page.get("url", "")
        try:
            if args.no_llm:
                issues = fallback_issues(page)
            else:
                issues = openai_generate_issues(model=args.model, page_record=page)
        except Exception as e:
            print(f"[warn] LLM failed for {url}: {e}\nUsing fallback.")
            issues = fallback_issues(page)

        for issue in issues:
            title = safe_title(issue.title)
            md = render_issue_md(page, issue)

            if args.single_file:
                # Append to combined buffer
                combined_lines.append(md)
                combined_lines.append("\n---\n")
                index_rows.append({
                    "page": url,
                    "title": title,
                    "file": "README.md#"+slugify(title)
                })
            else:
                # Per-page file
                base_slug = slugify(args.file_prefix) + "-" + slugify(url.replace("https://", "").replace("http://", ""))
                title_slug = slugify(title)
                fname = f"{base_slug}--{title_slug}.md"
                path = out_dir / fname
                path.write_text(md, encoding="utf-8")
                index_rows.append({"page": url, "title": title, "file": fname})

        processed += 1
        # small pause to be nice to the LLM API limits
        time.sleep(0.2 if not args.no_llm else 0.0)


    # Write index/README
    if args.single_file:
        readme_path = out_dir / "README.md"
        readme_path.write_text("\n".join(combined_lines), encoding="utf-8")
        print(f"[ok] Wrote {readme_path}")
    else:
        idx_md = render_index_md(index_rows)
        idx_path = out_dir / "INDEX.md"
        idx_path.write_text(idx_md, encoding="utf-8")
        print(f"[ok] Wrote {idx_path}")

    print(f"Done. Processed {processed} page(s). Output: {out_dir}")

if __name__ == "__main__":
    main()
