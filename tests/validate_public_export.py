#!/usr/bin/env python3
"""Validate the generated Workforce Wonkery public companion repository."""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

FORBIDDEN_ROOTS = {
    "agents", "archive", "governance", "migration", "preview", "qa", "research"
}
FORBIDDEN_NAMES = {
    ".env", ".env.local", ".env.production", "credentials.json", "secrets.json"
}
SECRET_PATTERNS = [
    re.compile(r"(?i)(api[_-]?key|client[_-]?secret|access[_-]?token|refresh[_-]?token|password)\s*[:=]\s*['\"]?[A-Za-z0-9_\-./+=]{16,}"),
    re.compile(r"gh[pousr]_[A-Za-z0-9]{20,}"),
    re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
]
TEXT_EXTENSIONS = {
    ".css", ".csv", ".html", ".js", ".json", ".md", ".php", ".py",
    ".txt", ".xml", ".yaml", ".yml", ".ics"
}


def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def fail(message: str) -> None:
    raise SystemExit(f"FAIL: {message}")


def validate_repository_boundary() -> None:
    for root in FORBIDDEN_ROOTS:
        if (ROOT / root).exists():
            fail(f"private control-plane root is present: {root}")
    for path in ROOT.rglob("*"):
        if not path.is_file() or ".git" in path.parts:
            continue
        if path.name.lower() in FORBIDDEN_NAMES:
            fail(f"forbidden file is present: {path.relative_to(ROOT)}")
        if path.suffix.lower() in TEXT_EXTENSIONS:
            try:
                text = path.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                continue
            for pattern in SECRET_PATTERNS:
                if pattern.search(text):
                    fail(f"potential credential material in {path.relative_to(ROOT)}")


def validate_provenance() -> None:
    path = ROOT / "PROVENANCE.json"
    if not path.exists():
        fail("PROVENANCE.json is missing")
    data = json.loads(path.read_text(encoding="utf-8"))
    if data.get("source_repository") != "Workforce-Wonkery/workforce-wonkery":
        fail("unexpected source repository")
    if data.get("target_repository") != "Workforce-Wonkery/workforce-wonkery-public":
        fail("unexpected target repository")
    files = data.get("files", [])
    if data.get("file_count") != len(files):
        fail("provenance file count mismatch")
    targets = set()
    for item in files:
        target = item.get("target")
        if not target or target in targets:
            fail(f"blank or duplicate provenance target: {target}")
        targets.add(target)
        file_path = ROOT / target
        if not file_path.exists():
            fail(f"provenance target is missing: {target}")
        if digest(file_path) != item.get("sha256"):
            fail(f"provenance hash mismatch: {target}")


def validate_public_runtime() -> None:
    out = ROOT / "data" / "runtime"
    manifest_path = out / "manifest.json"
    if not manifest_path.exists():
        fail("public runtime manifest is missing")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    assets = manifest.get("assets", [])
    if not assets:
        fail("public runtime manifest contains no assets")
    for item in assets:
        rel = item.get("path")
        expected = item.get("sha256")
        if not rel or not re.fullmatch(r"[0-9a-f]{64}", str(expected or "")):
            fail(f"invalid public runtime manifest row: {item}")
        path = out / rel
        if not path.exists():
            fail(f"runtime asset missing: {rel}")
        if digest(path) != expected:
            fail(f"runtime asset hash mismatch: {rel}")


def validate_json() -> None:
    checked = 0
    for path in (ROOT / "data").rglob("*.json"):
        json.loads(path.read_text(encoding="utf-8"))
        checked += 1
    if checked == 0:
        fail("no JSON data files were found")
    print(f"PASS: parsed {checked} public JSON files")


def main() -> int:
    validate_repository_boundary()
    validate_provenance()
    validate_public_runtime()
    validate_json()
    print("PASS: public companion boundary, provenance, runtime hashes, and JSON are valid")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
