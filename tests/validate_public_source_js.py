#!/usr/bin/env python3
"""Syntax-check inline JavaScript in public WordPress HTML without executing it."""
from __future__ import annotations

import re
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = re.compile(r"<script\b([^>]*)>(.*?)</script\s*>", re.IGNORECASE | re.DOTALL)
TYPE = re.compile(r"\btype\s*=\s*['\"]([^'\"]+)['\"]", re.IGNORECASE)


def main() -> int:
    root = ROOT / "src/wordpress"
    if not root.is_dir():
        raise SystemExit("FAIL: public WordPress source directory missing")
    validated = 0
    with tempfile.TemporaryDirectory() as scratch:
        for html in sorted(root.rglob("*.html")):
            source = html.read_text(encoding="utf-8")
            for _, (attrs, script) in enumerate(SCRIPTS.findall(source)):
                if re.search(r"\bsrc\s*=", attrs, re.I) or not script.strip():
                    continue
                kind = TYPE.search(attrs)
                script_type = kind.group(1).strip().lower() if kind else ""
                if script_type not in ("", "text/javascript", "application/javascript", "module"):
                    continue
                ext = "mjs" if script_type == "module" else "js"
                temporary = Path(scratch) / f"inline-{validated}.{ext}"
                # These source blueprints are not executable until the private
                # governed builder replaces the two explicit JSON-array tokens.
                # Normalize only those documented tokens for syntax checking.
                parse_only = script
                if html.name.startswith("wae-map-engine-v2-"):
                    parse_only = parse_only.replace("{{EXCLUDED_PLACE_NAMES_JSON}}", "[]")
                    parse_only = parse_only.replace("{{PLACE_NAMES_JSON}}", "[]")
                temporary.write_text(parse_only, encoding="utf-8")
                check = subprocess.run(
                    ["node", "--check", str(temporary)], capture_output=True,
                    text=True, timeout=10, check=False,
                )
                if check.returncode:
                    raise SystemExit(
                        f"FAIL: inline JavaScript parse error in {html.relative_to(ROOT)}"
                        f" (script {validated}):\\n{check.stderr}"
                    )
                validated += 1
    if not validated:
        raise SystemExit("FAIL: no inline website JavaScript was checked")
    print(f"PASS: syntax-checked {validated} inline WordPress JavaScript blocks")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
