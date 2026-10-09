#!/usr/bin/env python3
"""Ensure public Practice source promotes the focused portfolio, not courses."""
from pathlib import Path
root = Path(__file__).resolve().parents[1]
hub = (root / "src/wordpress/templates/practice-editorial-v2.html").read_text(encoding="utf-8")
footer = (root / "src/wordpress/template-parts/footer-editorial-blocks.html").read_text(encoding="utf-8")
body = hub[hub.index('<section class="wwp-hero"'):]
for value in ('id="wwp-deep-dives"', 'id="wwp-desk-aids"', 'Practice Deep Dives',
              'Desk Aids &amp; Toolkits', '/practice/etpl-coordinator/',
              '/practice-insight-employer-engagement/', '/practice/foundations/strong-wioa-file/'):
    assert value in body, f"Practice focus missing {value}"
for value in ("Foundations Course", "Workforce in Practice", "AI Readiness Lab", "Build capability"):
    assert value not in body, f"Retired learning navigation still visible: {value}"
    assert value not in footer, f"Retired learning link in footer: {value}"
for anchor in ('#wwp-deep-dives', '#wwp-desk-aids'):
    assert anchor in footer, f"Missing footer anchor: {anchor}"
assert hub.count("<!-- wp:html -->") == hub.count("<!-- /wp:html -->")
assert hub.count("<section ") == hub.count("</section>")
academy = (root / "src/wordpress/templates/etpl/coordinator-academy.html").read_text(encoding="utf-8")
for value in ("Your First 30 Days as an ETPL Coordinator", "Week 1", "Week 4", "Before handing over routine work"):
    assert value in academy, f"ETPL onboarding missing {value}"
for value in ("Academy progress:", "Case Lab mastery:", "data-level=", "ww_etpl_academy_v2"):
    assert value not in academy, f"ETPL onboarding still tracks course completion: {value}"
assert "ETPL Coordinator Academy" not in (root / "src/wordpress/templates/etpl-coordinator-desk.html").read_text(encoding="utf-8")
print("PRACTICE FOCUS CONTRACT: PASS")
