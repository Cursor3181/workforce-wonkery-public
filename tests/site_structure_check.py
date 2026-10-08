#!/usr/bin/env python3
"""Credential-free live structural smoke checks for governed public surfaces.

Repository/source invariants live in qa/source_contract_check.py. This file only
checks the public site and therefore remains a live/manual smoke layer.
"""
import json
import re
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "tests" / "site-surfaces.json"

def fetch(url):
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": "Workforce-Wonkery-GitHub-QA/1.0 (+public structural check)",
            "Accept": "text/html,application/xhtml+xml",
        },
    )
    last = None
    for delay in (0, 2, 5):
        if delay:
            time.sleep(delay)
        try:
            with urllib.request.urlopen(req, timeout=25) as resp:
                return resp.status, resp.read().decode("utf-8", "replace"), None
        except urllib.error.HTTPError as exc:
            last = exc
            if exc.code == 429:
                continue
            try:
                body = exc.read().decode("utf-8", "replace")
            except Exception:
                body = ""
            return exc.code, body, str(exc)
        except Exception as exc:
            last = exc
    return None, "", str(last) if last else "unknown fetch failure"

def rendered_script_corruption(html):
    for attrs,body in re.findall(r"<script\\b([^>]*)>([\\s\\S]*?)</script>",html,flags=re.I):
        if "application/json" in attrs.lower():
            continue
        if "&#038;&#038;" in body or "&amp;&amp;" in body:
            return True
    return False

def has_noindex(html):
    for tag in re.findall(r"<meta\b[^>]*>", html, flags=re.I):
        if re.search(r"name\s*=\s*['\"]robots['\"]", tag, flags=re.I) and re.search(r"noindex", tag, flags=re.I):
            return True
    return False

def policy_count_issue(html):
    """Validate visible and fallback counts against the generated public floor.

    Never freeze a specific brief total in the live structure manifest.
    Readers may see newly published briefs before the next asset refresh.
    """
    visible = re.search(r'\bid\s*=\s*["\']ww-policy-total["\'][^>]*>\s*(\d+)\s*<', html, re.I)
    fallback = re.search(r'\bAll\s+(\d+)\s+published\s+policy\s+briefs\s+remain\s+available\s+below', html, re.I)
    if visible is None or fallback is None:
        return "Policy Library visible total or accessible fallback total is missing"
    shown, alternate = int(visible.group(1)), int(fallback.group(1))
    if shown != alternate:
        return f"Policy Library visible/fallback totals disagree: {shown} vs {alternate}"
    public_index = ROOT / "data" / "runtime" / "policy" / "runtime.json"
    private_index = ROOT / "generated" / "public" / "policy" / "runtime.json"
    index_path = public_index if public_index.exists() else private_index
    if not index_path.exists():
        return "Policy Library generated runtime count is unavailable"
    try:
        minimum = int(json.loads(index_path.read_text(encoding="utf-8"))["count"])
    except (OSError, ValueError, KeyError, TypeError) as exc:
        return f"Policy Library runtime count is invalid: {exc}"
    if shown < minimum:
        return f"Policy Library displays {shown} briefs, below generated runtime floor {minimum}"
    return None

def main():
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    failures = []
    warnings = []
    verified = 0

    for surface in manifest["surfaces"]:
        status, html, err = fetch(surface["url"])
        name = surface["name"]
        if status == 429 or status is None:
            warnings.append(f"{name}: fetch unavailable ({status or err}); browser verification still required")
            print(f"::warning title={name}::{warnings[-1]}")
            continue
        if status != 200:
            failures.append(f"{name}: HTTP {status} ({err or 'unexpected response'})")
            continue
        if has_noindex(html):
            failures.append(f"{name}: robots noindex detected")
        if rendered_script_corruption(html):
            failures.append(f"{name}: HTML-encoded logical AND detected in executable script")
        if name == "Policy Brief Library":
            issue = policy_count_issue(html)
            if issue:
                failures.append(issue)
        lower = html.lower()
        for marker in surface.get("required_markers", []):
            if marker.lower() not in lower:
                failures.append(f"{name}: required marker missing: {marker}")
        verified += 1
        print(f"PASS structural fetch: {name} ({len(html):,} bytes)")

    print(f"STRUCTURAL_SUMMARY verified={verified} warnings={len(warnings)} failures={len(failures)}")
    if failures:
        for failure in failures:
            print(f"FAIL: {failure}", file=sys.stderr)
        return 1
    print("Structural live QA passed. Interactive browser acceptance remains a separate gate.")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
