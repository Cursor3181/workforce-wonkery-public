#!/usr/bin/env python3
"""Browser-render approved public WordPress source, without private snapshots.

This is a visual-source smoke test, not an authenticated WordPress acceptance
test or a substitute for the private prepublication and rollback checks.
No unpublished preview app, external credentials, or private fixture is used.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "src" / "wordpress"
ART = ROOT / "qa" / "artifacts" / "public-preview"
CASES = (
    ("home", "templates/homepage-editorial.html", "ww-pilot-v6", "page-id-1943"),
    ("policy", "templates/policy-editorial.html", "ww-policy-page", "page-id-6"),
    ("data", "templates/data-editorial.html", "wd-landing", "page-id-2896"),
    ("practice", "templates/practice-editorial-v2.html", "ww-practice-v2", "page-id-935"),
    ("report", "templates/intelligence-report.html", "ww-intelligence-report", "page-id-0"),
    ("etpl", "templates/etpl-coordinator-desk.html", "ww-etpl", "page-template-default"),
)
WIDTHS = (1440, 768, 390)


def build_document(source_path: str, body_class: str) -> str:
    header = (SOURCE / "template-parts/header-editorial-blocks.html").read_text(encoding="utf-8")
    footer = (SOURCE / "template-parts/footer-editorial-blocks.html").read_text(encoding="utf-8")
    content = (SOURCE / source_path).read_text(encoding="utf-8")
    css = (SOURCE / "css/site-shell.css").read_text(encoding="utf-8")
    # WordPress resolves navigation ref=4 at runtime. A local public-only
    # navigation stand-in lets us check the shared responsive layout without
    # fetching authenticated WordPress records.
    navigation = (
        '<nav class="ww-global-nav" aria-label="Preview navigation">'
        '<ul class="wp-block-navigation__container" style="display:flex;gap:18px;list-style:none">'
        '<li><a href="#policy">Policy</a></li>'
        '<li><a href="#data">Data</a></li>'
        '<li><a href="#practice">Practice</a></li>'
        '<li><a href="#reports">Reports</a></li>'
        '</ul></nav>'
    )
    header, n = re.subn(r"<!--\s*wp:navigation\s+.*?/-->", navigation, header, count=1, flags=re.S)
    if n != 1:
        raise ValueError("Expected exactly one WordPress site navigation placeholder")
    # Disable scripts in the browser rather than trying to reconstruct private
    # WordPress REST, editorial decisions, or remote subscriber state.
    return (
        '<!doctype html><html lang="en"><head><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width,initial-scale=1">'
        '<meta name="robots" content="noindex,nofollow">'
        '<title>Local public-source visual preview</title>'
        '<style>html,body{margin:0;max-width:100%;background:#fcfaf6}'
        '*,*::before,*::after{box-sizing:border-box}'
        '.wp-site-blocks{width:100%}'
        '.wp-block-post-content{width:100%;max-width:none;margin:0;padding:0}'
        '.ww-global-header,.ww-global-footer{width:100%}</style>'
        '<style>' + css + '</style></head>'
        '<body class="' + body_class + '"><div class="wp-site-blocks">'
        + header +
        '<main class="wp-block-group"><div class="wp-block-post-content">'
        + content +
        '</div></main><footer class="wp-block-template-part">'
        + footer +
        '</footer></div></body></html>'
    )


def run() -> int:
    ART.mkdir(parents=True, exist_ok=True)
    results = []
    with sync_playwright() as pw:
        browser = pw.chromium.launch()
        try:
            for name, path, root_id, body_class in CASES:
                document = build_document(path, body_class)
                for width in WIDTHS:
                    context = browser.new_context(
                        viewport={"width": width, "height": 900},
                        device_scale_factor=1,
                        java_script_enabled=False,
                        reduced_motion="reduce",
                    )
                    # Do not call third-party URLs or live WordPress APIs.
                    context.route("**/*", lambda route: route.abort())
                    page = context.new_page()
                    issues = []
                    try:
                        page.set_content(document, wait_until="domcontentloaded", timeout=20_000)
                        page.evaluate("document.fonts.ready")
                        root = page.locator("#" + root_id)
                        heading = page.locator("#" + root_id + " h1").first
                        if root.count() != 1:
                            issues.append("expected one public source root")
                        if heading.count() == 0 or not heading.is_visible():
                            issues.append("primary heading absent or hidden")
                        elif not heading.inner_text().strip():
                            issues.append("primary heading empty")
                        document_width = page.evaluate("document.documentElement.scrollWidth")
                        if document_width > width + 2:
                            issues.append(f"horizontal overflow: {document_width}px > {width}px")
                        if page.locator(".ww-global-header").count() != 1:
                            issues.append("shared header absent")
                        if page.locator(".ww-global-footer").count() != 1:
                            issues.append("shared footer absent")
                        if width in (1440, 390):
                            page.screenshot(path=str(ART / f"{name}-{width}.png"), full_page=True,
                                            timeout=20_000, animations="disabled")
                        result = {"surface": name, "viewport": width, "document_width": document_width,
                                  "result": "FAIL" if issues else "PASS", "issues": issues}
                    except Exception as exc:
                        result = {"surface": name, "viewport": width,
                                  "result": "FAIL", "issues": [str(exc)[:300]]}
                    finally:
                        context.close()
                    results.append(result)
                    print(f'{result["result"]} public-source visual {name} {width}px: '
                          + (", ".join(result["issues"]) if result["issues"] else "responsive, H1 and shell present"))
        finally:
            browser.close()
    report = {"scope": "public-source static presentation only", "results": results,
              "failures": sum(1 for r in results if r["result"] == "FAIL"),
              "limitations": [
                  "JavaScript is disabled; this test does not verify interactive behavior.",
                  "WordPress block rendering, remote imagery, and private publication records are not simulated.",
                  "Live site and approved private publication checks remain separate."
              ]}
    (ART / "results.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(f'PUBLIC_SOURCE_VISUAL_SUMMARY checked={len(results)} failures={report["failures"]}')
    return 1 if report["failures"] else 0


if __name__ == "__main__":
    raise SystemExit(run())
