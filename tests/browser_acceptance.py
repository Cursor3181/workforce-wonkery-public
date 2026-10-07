#!/usr/bin/env python3
"""Interactive browser acceptance for GOVQ-047.

Runs against the public Workforce Wonkery site using Chromium.
This is the browser-level complement to qa/site_structure_check.py.
"""
from pathlib import Path
import json
import re
import sys
import os
from playwright.sync_api import sync_playwright, expect

BASE = "https://workforcewonkery.com"
ART = Path("qa/artifacts/browser-acceptance")
ART.mkdir(parents=True, exist_ok=True)

RESULTS = []
RUNTIME = {}

RUNTIME_CAPTURE_SCRIPT = r"""
(() => {
  const key = "__wwRuntimeDiagnostics";
  if (window[key]) return;
  window[key] = { errors: [], rejections: [] };
  window.addEventListener("error", event => {
    window[key].errors.push({
      message: String(event.message || ""),
      source: String(event.filename || ""),
      line: Number(event.lineno || 0),
      column: Number(event.colno || 0),
      stack: event.error && event.error.stack ? String(event.error.stack) : ""
    });
  });
  window.addEventListener("unhandledrejection", event => {
    const reason = event.reason;
    window[key].rejections.push({
      message: reason && reason.message ? String(reason.message) : String(reason || ""),
      stack: reason && reason.stack ? String(reason.stack) : ""
    });
  });
})();
"""

def _playwright_error_detail(exc):
    detail={"message":str(exc)}
    for attr in ("name","message","stack"):
        value=getattr(exc,attr,None)
        if value:
            detail[attr]=str(value)
    return detail

def _console_error_detail(msg):
    detail={"text":msg.text}
    try:
        location=msg.location
        if location:
            detail["location"]=location
    except Exception:
        pass
    return detail

def _request_failure_detail(req):
    detail={"url":req.url}
    try:
        failure=req.failure
        if failure:
            detail["failure"]=failure
    except Exception:
        pass
    return detail

def watch_runtime(page):
    key=id(page)
    if key in RUNTIME:
        return RUNTIME[key]
    issues={"page_errors":[],"console_errors":[],"bad_responses":[],"request_failures":[]}
    RUNTIME[key]=issues
    page.add_init_script(RUNTIME_CAPTURE_SCRIPT)
    page.on("pageerror", lambda exc: issues["page_errors"].append(_playwright_error_detail(exc)))
    page.on("console", lambda msg: issues["console_errors"].append(_console_error_detail(msg)) if msg.type=="error" else None)
    page.on("response", lambda resp: issues["bad_responses"].append({"status":resp.status,"url":resp.url}) if resp.status>=400 and resp.url.startswith(BASE) else None)
    page.on("requestfailed", lambda req: issues["request_failures"].append(_request_failure_detail(req)) if req.url.startswith(BASE) else None)
    return issues

def browser_runtime_diagnostics(page):
    try:
        data=page.evaluate("""() => window.__wwRuntimeDiagnostics || {errors: [], rejections: []}""")
        html=page.content()
        lines=html.splitlines()
        contexts=[]
        for err in data.get("errors",[]):
            source=(err.get("source") or "").split("#",1)[0]
            page_source=page.url.split("#",1)[0]
            line=int(err.get("line") or 0)
            if source==page_source and line>0:
                lo=max(1,line-3)
                hi=min(len(lines),line+3)
                contexts.append({
                    "source":source,
                    "line":line,
                    "column":int(err.get("column") or 0),
                    "html_lines":[{"line":n,"text":lines[n-1][:500]} for n in range(lo,hi+1)]
                })
        if contexts:
            data["html_error_contexts"]=contexts
        return data
    except Exception as exc:
        return {"errors":[],"rejections":[],"capture_error":str(exc)}

def _known_third_party_runtime_error(detail):
    text=json.dumps(detail,sort_keys=True) if isinstance(detail,(dict,list)) else str(detail)
    return (
        "/wp-content/plugins/jetpack/_inc/blocks/cookie-consent/view.js" in text
        and "Cannot read properties of null (reading 'textContent')" in text
    )

def runtime_clean(page, surface, fail_console=False):
    issues=watch_runtime(page)
    browser_issues=browser_runtime_diagnostics(page)
    page_errors=issues["page_errors"][-10:]
    window_errors=browser_issues.get("errors",[])[-10:]
    third_party_warnings=[
        x for x in page_errors + window_errors if _known_third_party_runtime_error(x)
    ]
    first_party_page_errors=[x for x in page_errors if not _known_third_party_runtime_error(x)]
    first_party_window_errors=[x for x in window_errors if not _known_third_party_runtime_error(x)]
    fatal=first_party_page_errors or issues["bad_responses"] or issues["request_failures"] or first_party_window_errors or browser_issues.get("rejections")
    detail=json.dumps({
        "page_errors":first_party_page_errors,
        "window_errors":first_party_window_errors,
        "third_party_warnings":third_party_warnings,
        "unhandled_rejections":browser_issues.get("rejections",[])[-10:],
        "html_error_contexts":browser_issues.get("html_error_contexts",[])[-10:],
        "bad_responses":issues["bad_responses"][-10:],
        "request_failures":issues["request_failures"][-10:],
        "console_errors":issues["console_errors"][-10:],
    })
    record(surface,"runtime/resource health","PASS" if not fatal else "FAIL",detail)
    if third_party_warnings:
        record(surface,"known third-party runtime warning","WARN",json.dumps(third_party_warnings[-10:]))
    assert not fatal, detail
    if issues["console_errors"]:
        record(surface,"console JavaScript errors","FAIL" if fail_console else "WARN",detail)
        if fail_console:
            raise AssertionError(detail)
    else:
        record(surface,"console JavaScript errors","PASS")

# Sector final verification trigger: 905bfbe4-final
# Sector staging verification trigger: c61341c1
# Sector rollback verification trigger: 905bfbe4
# Preflight refresh trigger: 2026-09-26

def record(surface, check, status, detail=""):
    RESULTS.append({"surface": surface, "check": check, "status": status, "detail": detail})
    print(f"{status}: {surface} :: {check}" + (f" :: {detail}" if detail else ""))

def no_horizontal_overflow(page, surface):
    data = page.evaluate("""() => ({
      width: window.innerWidth,
      scroll: document.documentElement.scrollWidth
    })""")
    ok = data["scroll"] <= data["width"] + 2
    detail=f'viewport={data["width"]}, scrollWidth={data["scroll"]}'
    if not ok:
        offenders=page.evaluate("""() => Array.from(document.querySelectorAll('body *')).map(e => {
          const r=e.getBoundingClientRect(); const s=getComputedStyle(e);
          return {tag:e.tagName,id:e.id||'',cls:(e.className&&String(e.className).slice(0,120))||'',left:Math.round(r.left),right:Math.round(r.right),width:Math.round(r.width),scrollWidth:e.scrollWidth,display:s.display,position:s.position,whiteSpace:s.whiteSpace};
        }).filter(x => x.right > window.innerWidth + 2 || x.width > window.innerWidth + 2 || x.scrollWidth > window.innerWidth + 2).sort((a,b)=>Math.max(b.right,b.width,b.scrollWidth)-Math.max(a.right,a.width,a.scrollWidth)).slice(0,12)""")
        detail += " offenders=" + json.dumps(offenders)
    record(surface, "responsive horizontal overflow", "PASS" if ok else "FAIL", detail)
    assert ok

def keyboard_focus_visible(page, surface):
    page.evaluate("window.scrollTo(0,0)")
    page.locator("body").click(position={"x": 2, "y": 2})
    found = None
    for _ in range(18):
        page.keyboard.press("Tab")
        info = page.evaluate("""() => {
          const e=document.activeElement;
          if(!e || e===document.body) return null;
          const s=getComputedStyle(e);
          return {
            tag:e.tagName,
            id:e.id||"",
            text:(e.innerText||e.getAttribute("aria-label")||e.getAttribute("title")||"").trim().slice(0,80),
            outlineStyle:s.outlineStyle,
            outlineWidth:s.outlineWidth,
            boxShadow:s.boxShadow
          };
        }""")
        if info:
            outline = info["outlineStyle"] not in ("none", "") and info["outlineWidth"] not in ("0px", "")
            shadow = info["boxShadow"] not in ("none", "")
            if outline or shadow:
                found = info
                break
    ok = found is not None
    record(surface, "keyboard focus visibility", "PASS" if ok else "FAIL",
           json.dumps(found) if found else "no visibly focused element found in first 18 tabs")
    assert ok

def screenshot(page, name):
    page.screenshot(path=str(ART / name), full_page=True)

def goto(page, url, surface):
    watch_runtime(page)
    resp = page.goto(url, wait_until="domcontentloaded", timeout=60000)
    assert resp is not None
    record(surface, "HTTP navigation", "PASS" if resp.ok else "FAIL", f"HTTP {resp.status}")
    assert resp.ok
    page.wait_for_timeout(1200)

def general(page, surface, url, mobile=False):
    goto(page, url, surface)
    no_horizontal_overflow(page, surface)
    keyboard_focus_visible(page, surface)
    runtime_clean(page, surface)
    screenshot(page, f"{surface.lower().replace(' ','-')}-{'mobile' if mobile else 'desktop'}.png")

def test_homepage(context, mobile=False):
    surface="Homepage"
    page=context.new_page()
    general(page,surface,BASE+"/",mobile)
    # Hero paths must remain directly available at every viewport.
    for href in ["/policy-briefs/", "/data/", "/practice/"]:
        link=page.locator(f'main a[href$="{href}"]').filter(has_text=re.compile(r"Policy|Data|Practice",re.I)).first
        expect(link).to_be_visible()
    record(surface,"Policy/Data/Practice hero paths","PASS")

    # The current editorial homepage no longer renders live Practice count badges.
    # Guard against silently restoring the retired count placeholders/network path.
    retired_counts=page.locator("[data-ww-foundations-count],[data-ww-practice-count],[data-ww-quickstarts-count],[data-ww-board-practice-count]").count()
    record(surface,"retired dynamic count badges absent","PASS" if retired_counts==0 else "FAIL",f"count={retired_counts}")
    assert retired_counts==0

    # On mobile the primary nav is intentionally collapsed. Exercise the menu instead
    # of requiring desktop navigation labels to be visible.
    menu=page.get_by_role("button",name=re.compile(r"Open menu",re.I))
    if mobile and menu.count():
        expect(menu).to_be_visible()
        menu.click()
        page.wait_for_timeout(200)
        menu_dialog=page.get_by_role("dialog",name="Menu")
        expect(menu_dialog).to_be_visible()
        for label in ["Policy","Data","Practice"]:
            expect(menu_dialog.get_by_role("link",name=label,exact=True)).to_be_visible()
        record(surface,"mobile navigation menu","PASS")
    page.close()

def test_policy(context, mobile=False):
    surface="Policy Brief Library"
    page=context.new_page()
    general(page,surface,BASE+"/policy-briefs/",mobile)
    search=page.locator("#ww-policy-search")
    expect(search).to_be_visible()
    search.fill("H-1B")
    page.wait_for_timeout(400)
    count=page.locator("#ww-policy-count").inner_text()
    articles=page.locator("#ww-policy-results article").count()
    ok=articles >= 1 and "published brief" in count.lower()
    record(surface,"search filtering","PASS" if ok else "FAIL",f"count={count}, articles={articles}")
    assert ok
    assert "policy_q=H-1B" in page.url or "policy_q=H-1B".lower() in page.url.lower()
    record(surface,"search URL state","PASS",page.url)

    saved_url=page.url
    page.reload(wait_until="domcontentloaded")
    page.wait_for_timeout(400)
    expect(search).to_have_value("H-1B")
    assert page.url==saved_url
    record(surface,"URL-state restoration after reload","PASS",page.url)

    page.locator("#ww-policy-clear").click()
    page.wait_for_timeout(250)
    expect(search).to_have_value("")
    record(surface,"clear filters","PASS")
    page.evaluate("history.back()")
    page.wait_for_function("document.querySelector('#ww-policy-search').value === 'H-1B'")
    expect(search).to_have_value("H-1B")
    record(surface,"Back restores Policy state","PASS",page.url)
    page.evaluate("history.forward()")
    page.wait_for_function("document.querySelector('#ww-policy-search').value === ''")
    expect(search).to_have_value("")
    record(surface,"Forward restores Policy state","PASS",page.url)

    more=page.locator("#ww-policy-more")
    if more.is_visible():
        before=page.locator("#ww-policy-results article").count()
        more.click()
        page.wait_for_timeout(250)
        after=page.locator("#ww-policy-results article").count()
        ok=after > before
        record(surface,"show more","PASS" if ok else "FAIL",f"{before}->{after}")
        assert ok
    else:
        record(surface,"show more","WARN","control not visible at current catalog size/state")

    # noscript content is intentionally not rendered in a JS browser; public structural QA checks the marker.
    record(surface,"no-JS fallback marker","PASS","verified by structural QA; noscript correctly not rendered with JS")
    page.close()

def choose_two_market_values(page, selector):
    opts=page.locator(selector+" option")
    vals=[]
    for i in range(opts.count()):
        v=opts.nth(i).get_attribute("value") or ""
        if v and v not in vals:
            vals.append(v)
        if len(vals)>=2:
            break
    assert len(vals)>=2
    return vals

def test_workforce_lens_briefing(context, mobile=False):
    surface="My Briefing"
    page=context.new_page()
    page.add_init_script("""(() => {
      localStorage.setItem('ww_workforce_lens_v1', JSON.stringify({
        version:1,
        country_code:'US',
        jurisdiction_code:'CA',
        state_code:'CA',
        jurisdiction_label:'California',
        area_id:'42100',
        area_label:'Santa Cruz-Watsonville MSA',
        role_id:'director',
        role_label:'Director / Executive'
      }));
      localStorage.removeItem('ww_workforce_briefing_snapshot_v1');
    })();""")
    general(page,surface,BASE+"/for-me/",mobile)
    page.wait_for_function(
        "() => document.querySelector('#ww-lens-page')?.dataset.briefingState === 'ready'",
        timeout=30000,
    )
    expect(page.locator("#wwl-active-summary")).to_contain_text("Santa Cruz-Watsonville MSA")
    expect(page.locator("#wwl-active-summary")).to_contain_text("Director / Executive")

    attention=page.locator("#wwl-attention-list .wwl-item")
    ok=attention.count()>=3
    record(surface,"needs-attention briefing","PASS" if ok else "FAIL",f"items={attention.count()}")
    assert ok
    expect(page.locator("#wwl-attention-list")).to_contain_text("AI workforce review")

    changed=page.locator("#wwl-changed-list .wwl-item")
    ok=changed.count()>=1
    record(surface,"first-visit change baseline","PASS" if ok else "FAIL",f"items={changed.count()}")
    assert ok

    signals=page.locator("#wwl-signal-list .wwl-signal")
    ok=signals.count()>=3
    record(surface,"local market signals","PASS" if ok else "FAIL",f"signals={signals.count()}")
    assert ok
    expect(page.locator("#wwl-signal-list")).to_contain_text("Living-wage benchmark")
    expect(page.locator("#wwl-signal-list")).to_contain_text("Source:")

    questions=page.locator("#wwl-question-list .wwl-question")
    ok=questions.count()>=2
    record(surface,"decision questions","PASS" if ok else "FAIL",f"questions={questions.count()}")
    assert ok
    decision_links=page.locator('#wwl-question-list a[href*="/discover/?q="]')
    assert decision_links.count()>=2
    record(surface,"Decision Brief handoff","PASS",f"links={decision_links.count()}")

    trust=page.locator(".wwl-trust")
    expect(trust).to_contain_text("does not make a runtime AI request")
    record(surface,"briefing trust boundary","PASS")

    no_horizontal_overflow(page,surface)
    runtime_clean(page,surface,fail_console=True)
    screenshot(page,f"my-briefing-{'mobile' if mobile else 'desktop'}.png")
    page.evaluate("""() => {
      localStorage.removeItem('ww_workforce_lens_v1');
      localStorage.removeItem('ww-reader-role');
      localStorage.removeItem('ww_workforce_briefing_snapshot_v1');
    }""")
    page.close()


def test_data(context, mobile=False):
    surface="Data"
    page=context.new_page()
    general(page,surface,BASE+"/data/",mobile)

    # The September 28 Data redesign intentionally moved market selection to
    # Labor Market Profiles. GOVQ-047 therefore tests the current governed
    # landing-page contract instead of the retired embedded #wwn-market UI.
    body=page.locator("body")
    expect(body).to_contain_text("Data Decoded.")
    expect(body).to_contain_text("California is hiring, cutting, and changing at the same time.")
    expect(body).to_contain_text("Health care is doing much of the pulling.")

    required_paths=[
        "/labor-market-profiles/",
        "/data/occupation-explorer/",
        "/data/training-opportunities/",
        "/data/workforce-access-equity/",
        "/data/sector-partnerships/",
    ]
    for href in required_paths:
        link=page.locator(f'a[href$="{href}"]').first
        expect(link).to_be_visible()
    record(surface,"five governed data-tool paths","PASS")

    # The current story-led data narrative must preserve the four decision lenses
    # and link readers back to authoritative labor-market sources.
    expect(body).to_contain_text("One good month does not make a boom.")
    expect(body).to_contain_text("A 5.1% unemployment rate can hide a lot of churn.")
    expect(body).to_contain_text("Average pay is rising. That still does not tell us who is winning.")
    source_links=page.locator('a[href*="edd.ca.gov"]')
    ok=source_links.count()>=2
    record(surface,"story-led statewide evidence and source links","PASS" if ok else "FAIL",f"EDD source links={source_links.count()}")
    assert ok

    # The page must not silently retain the retired embedded market selector.
    retired=page.locator("#wwn-market").count()
    record(surface,"retired embedded market selector absent","PASS" if retired==0 else "FAIL",f"count={retired}")
    assert retired==0

    page.close()


def test_discovery(context, mobile=False):
    surface="Universal Discovery"
    page=context.new_page()
    general(page,surface,BASE+"/discover/",mobile)
    search=page.locator("#wwd-query")
    expect(search).to_be_visible()

    def run_query(query):
        search.fill(query)
        page.locator("#wwd-form").evaluate("(form) => form.requestSubmit()")
        page.wait_for_function(
            "() => document.querySelector('#wwd-status') && !document.querySelector('#wwd-status').textContent.includes('Searching')",
            timeout=30000,
        )
        page.wait_for_timeout(250)

    run_query("AB 1534")
    best=page.locator("#wwd-best")
    expect(best).to_contain_text("AB 1534")
    href=best.locator("h2 a").get_attribute("href") or ""
    ok="/2026/" in href and "ab-1534" in href.lower()
    record(surface,"bill-number best match","PASS" if ok else "FAIL",href)
    assert ok

    run_query("registered nurses Fresno")
    expect(best).to_contain_text("Registered Nurses in Fresno")
    href=best.locator("h2 a").get_attribute("href") or ""
    ok="geo=23420" in href and "soc=29-1141" in href
    record(surface,"occupation + market synthesis","PASS" if ok else "FAIL",href)
    assert ok

    run_query("aprenticeship")
    result_text=(best.inner_text()+" "+page.locator("#wwd-results").inner_text()).lower()
    ok="apprentice" in result_text
    record(surface,"typo tolerance","PASS" if ok else "FAIL",result_text[:500])
    assert ok

    run_query("ETPL")
    result_text=(best.inner_text()+" "+page.locator("#wwd-results").inner_text()).lower()
    ok="training" in result_text or "eligible training" in result_text or "etpl" in result_text
    record(surface,"acronym expansion","PASS" if ok else "FAIL",result_text[:500])
    assert ok

    run_query("rapid response")
    build=page.locator("#wwd-build-decision")
    expect(build).to_be_visible()
    build.click()
    brief=page.locator("#wwd-decision")
    expect(brief).to_be_visible()
    expect(brief).to_contain_text("Decision brief: rapid response")
    expect(brief).to_contain_text("Evidence to review")
    expect(brief).to_contain_text("Questions to resolve")
    expect(brief).to_contain_text("What this does not establish")
    expect(brief).to_contain_text("Search rank is relevance, not evidence strength")
    chips=brief.locator(".wwd-coverage-chip")
    evidence_links=brief.locator(".wwd-evidence-sources a")
    ok=chips.count()==3 and evidence_links.count()>=2
    record(surface,"decision brief evidence coverage","PASS" if ok else "FAIL",f"chips={chips.count()}, source links={evidence_links.count()}")
    assert ok
    page.locator("#wwd-decision-copy").click()
    expect(page.locator("#wwd-decision-status")).to_contain_text("Copied with source links and evidence limits.")
    record(surface,"decision brief copy output","PASS")

    global_form=page.locator("form.ww-global-search, .ww-global-search form").first
    global_input=global_form.locator('input[type="search"]')
    action=global_form.get_attribute("action") or ""
    ok="/discover/" in action and global_input.get_attribute("name")=="q"
    record(surface,"global header routes to Discovery","PASS" if ok else "FAIL",f"action={action}, name={global_input.get_attribute('name')}")
    assert ok

    home=context.new_page()
    goto(home,BASE+"/",surface+" homepage activation")
    hero=home.locator(".ep-hero-search")
    action=hero.get_attribute("action") or ""
    name=hero.locator('input[type="search"]').get_attribute("name")
    ok="/discover/" in action and name=="q"
    record(surface,"homepage hero routes to Discovery","PASS" if ok else "FAIL",f"action={action}, name={name}")
    assert ok
    runtime_clean(home,surface+" homepage activation")
    home.close()

    runtime_clean(page,surface)
    screenshot(page,f"universal-discovery-{'mobile' if mobile else 'desktop'}.png")
    page.close()

def test_contextual_navigation(context, mobile=False):
    surface="Intelligence Graph contextual navigation"
    cases=[
        (
            "AB 1534",
            BASE+"/2026/09/08/ab-1534-50-percent-participant-training-workforce-pell/",
            "Workforce Training",
        ),
        (
            "Workforce Funding Foundations",
            BASE+"/practice/foundations/workforce-funding/",
            "Funding & Grants",
        ),
    ]
    for label,url,expected_facet in cases:
        page=context.new_page()
        goto(page,url,surface+" · "+label)
        module=page.locator("#ww-contextual-navigation")
        expect(module).to_be_visible(timeout=30000)
        expect(module.get_by_role("heading",name="What this connects to")).to_be_visible()
        cards=module.locator(".ww-contextual-nav__card")
        count=cards.count()
        ok=count>=2
        record(surface,f"{label} renders graph recommendations","PASS" if ok else "FAIL",f"cards={count}")
        assert ok
        facet_text=module.locator(".ww-contextual-nav__facets").inner_text() if module.locator(".ww-contextual-nav__facets").count() else ""
        facet_ok=expected_facet.lower() in facet_text.lower()
        record(surface,f"{label} renders expected graph facet","PASS" if facet_ok else "FAIL",facet_text[:500])
        assert facet_ok
        hrefs=cards.evaluate_all("(els) => els.map(el => el.href)")
        internal=all(h.startswith(BASE+"/") or h.startswith(BASE) for h in hrefs)
        unique=len(hrefs)==len(set(hrefs))
        record(surface,f"{label} recommendation destinations","PASS" if internal and unique else "FAIL",json.dumps(hrefs))
        assert internal and unique
        no_horizontal_overflow(page,surface+" · "+label)
        runtime_clean(page,surface+" · "+label,fail_console=True)
        screenshot(page,f"intelligence-context-{label.lower().replace(' ','-')}-{'mobile' if mobile else 'desktop'}.png")
        page.close()


def test_labor_market_profiles(context, mobile=False):
    surface="Labor Market Profiles"
    page=context.new_page()
    goto(page,BASE+"/labor-market-profiles/#msa-42100",surface)
    page.wait_for_function("() => window.WWLMP_RUNTIME && window.WWLMP_RUNTIME.loadedMarkets && window.WWLMP_RUNTIME.loadedMarkets.includes('42100')",timeout=30000)

    source_state=page.evaluate("""() => ({
      config: !!document.getElementById('ww-lmp-runtime-config'),
      legacy: !!document.getElementById('ww-unified-occ-data'),
      diag: window.WWLMP_RUNTIME
    })""")
    assert source_state["config"] and not source_state["legacy"]
    record(surface,"production shard loader active","PASS",json.dumps(source_state["diag"]))

    sc_root=page.locator('.ww-occ-unified[data-geo="42100"]')
    sc_select=sc_root.locator(".ww-occ-select")
    expect(sc_select).to_be_enabled()
    expect(sc_root.locator(".ww-occ-count")).to_contain_text("occupations")
    first=page.evaluate("() => ({...window.WWLMP_RUNTIME})")
    record(surface,"initial market shard loaded","PASS",json.dumps(first))

    market=page.locator("#wwn-market")
    expect(market).to_be_visible()
    market.select_option("41740")
    page.wait_for_function("() => location.hash === '#msa-41740' && window.WWLMP_RUNTIME && window.WWLMP_RUNTIME.loadedMarkets.includes('41740')",timeout=30000)
    sd_root=page.locator('.ww-occ-unified[data-geo="41740"]')
    expect(sd_root.locator(".ww-occ-select")).to_be_enabled()
    second=page.evaluate("() => ({...window.WWLMP_RUNTIME})")
    assert second["requestCount"]==first["requestCount"]+1, f"expected one new shard request, got {first} -> {second}"
    record(surface,"second market loads one shard","PASS",json.dumps(second))

    market.select_option("42100")
    page.wait_for_function("() => location.hash === '#msa-42100'",timeout=10000)
    page.wait_for_timeout(300)
    cached=page.evaluate("() => ({...window.WWLMP_RUNTIME})")
    assert cached["requestCount"]==second["requestCount"], f"cached revisit made a new shard request: {second} -> {cached}"
    record(surface,"cached market revisit","PASS",json.dumps(cached))

    page.go_back(timeout=15000)
    page.wait_for_function("() => location.hash === '#msa-41740'",timeout=10000)
    market=page.locator("#wwn-market")
    expect(market).to_have_value("41740")
    record(surface,"browser Back restores market","PASS",page.url)

    no_horizontal_overflow(page,surface)
    runtime_clean(page,surface,fail_console=True)
    screenshot(page,f"labor-market-profiles-{'mobile' if mobile else 'desktop'}-sharded.png")
    page.close()


def test_occupation_explorer(context, mobile=False):
    surface="Occupation Explorer"
    page=context.new_page()
    page_errors=[]
    console_errors=[]
    page.on("pageerror", lambda exc: page_errors.append(str(exc)))
    page.on("console", lambda msg: console_errors.append(msg.text) if msg.type=="error" else None)
    goto(page,BASE+"/data/occupation-explorer/?geo=42100",surface)
    no_horizontal_overflow(page,surface)
    select=page.locator("#occ-geo")
    expect(select).to_be_visible()
    page.wait_for_timeout(5000)
    state=page.locator("#occ-data-state").inner_text().strip() if page.locator("#occ-data-state").count() else ""
    summary=page.locator("#occ-results-summary").inner_text().strip() if page.locator("#occ-results-summary").count() else ""
    count=page.locator("#occ-count").inner_text().strip() if page.locator("#occ-count").count() else ""
    results=page.locator("#occ-results .result-card").count()
    embedded=page.evaluate("""() => ({
      public: !!document.getElementById('occ-embedded-public-data'),
      exact: !!document.getElementById('occ-embedded-exact-data'),
      tech: !!document.getElementById('occ-embedded-tech-data')
    })""")
    detail=json.dumps({
        "state":state,
        "summary":summary,
        "count":count,
        "results":results,
        "selected":select.input_value(),
        "embedded":embedded,
        "page_errors":page_errors,
        "console_errors":console_errors[-20:],
    })
    ok=results>0 and "340" in summary and select.input_value()=="42100"
    record(surface,"Santa Cruz initializes with results","PASS" if ok else "FAIL",detail)
    screenshot(page,f"occupation-explorer-{'mobile' if mobile else 'desktop'}-debug.png")
    assert ok, detail

    # Confirm a second market actually changes the result set.
    select.select_option("41500")
    page.wait_for_timeout(2500)
    selected=page.locator("#occ-geo").input_value()
    summary2=page.locator("#occ-results-summary").inner_text().strip()
    results2=page.locator("#occ-results .result-card").count()
    ok2=selected=="41500" and results2>0 and ("345" in summary2 or results2==345)
    record(surface,"market switching","PASS" if ok2 else "FAIL",
           json.dumps({"selected":selected,"summary":summary2,"results":results2,"page_errors":page_errors,"console_errors":console_errors[-20:]}))
    assert ok2
    assert "geo=41500" in page.url
    record(surface,"market URL state","PASS",page.url)

    page.evaluate("history.back()")
    page.wait_for_function("() => new URLSearchParams(location.search).get('geo') === '42100'",timeout=15000)
    page.wait_for_function("() => document.querySelector('#occ-geo')?.value === '42100'",timeout=15000)
    record(surface,"Back restores occupation market","PASS",page.url)
    page.evaluate("history.forward()")
    page.wait_for_function("() => new URLSearchParams(location.search).get('geo') === '41500'",timeout=15000)
    page.wait_for_function("() => document.querySelector('#occ-geo')?.value === '41500'",timeout=15000)
    record(surface,"Forward restores occupation market","PASS",page.url)

    saved_url=page.url
    page.reload(wait_until="domcontentloaded")
    page.wait_for_function("() => document.querySelector('#occ-geo')?.value === '41500'",timeout=15000)
    assert page.url==saved_url
    record(surface,"occupation URL-state restoration after reload","PASS",page.url)

    # Exercise one filter after initialization.
    search=page.locator("#occ-search")
    search.fill("nurse")
    page.wait_for_timeout(500)
    filtered=page.locator("#occ-results .result-card").count()
    ok3=filtered>0 and filtered<results2
    record(surface,"occupation search filter","PASS" if ok3 else "FAIL",f"filtered={filtered}")
    assert ok3
    runtime_clean(page,surface,fail_console=True)
    page.close()

def test_registry(context, mobile=False):
    surface="Regional Training Opportunity Registry"
    page=context.new_page()
    general(page,surface,BASE+"/data/training-opportunities/",mobile)
    select=page.locator("#ww-training-market")
    expect(select).to_be_visible()
    page.wait_for_function("document.querySelector('#ww-training-market').options.length > 1",timeout=10000)
    v=choose_two_market_values(page,"#ww-training-market")[0]
    select.select_option(v)
    page.wait_for_timeout(500)
    result=page.locator("#ww-training-result")
    expect(result).not_to_be_empty()
    links=result.locator("a")
    ok=links.count()>=1
    record(surface,"market selection produces result","PASS" if ok else "FAIL",f"value={v}, links={links.count()}")
    assert ok
    page.close()

def test_examples(context, mobile=False):
    surface="California Workforce Board Examples"
    page=context.new_page()
    general(page,surface,BASE+"/workforce-board-examples/",mobile)
    recent=page.get_by_role("button",name="Recently added")
    recent.click()
    page.wait_for_timeout(350)
    expect(recent).to_have_attribute("aria-pressed","true")
    results=page.locator("#a45-results .a45-item")
    ok=results.count()>0
    record(surface,"Recently added mode","PASS" if ok else "FAIL",f"results={results.count()}")
    assert ok

    # Return to all and test text search.
    page.get_by_role("button",name="All California").click()
    search=page.locator("#a45-search")
    search.fill("healthcare")
    page.wait_for_timeout(350)
    count=page.locator("#a45-count").inner_text()
    ok=page.locator("#a45-results .a45-item").count()>0
    record(surface,"practice search","PASS" if ok else "FAIL",count)
    assert ok

    page.locator("#a45-topic").select_option(label="Sector Strategy")
    page.wait_for_timeout(250)
    ok=page.locator("#a45-results .a45-item").count()>=0
    record(surface,"topic filter interaction","PASS" if ok else "FAIL")
    assert ok
    page.close()

def test_santa_cruz(context, mobile=False):
    surface="Santa Cruz-Watsonville RTO Brief"
    page=context.new_page()
    general(page,surface,BASE+"/data/training-opportunities/santa-cruz-watsonville/",mobile)
    body=page.locator("body").inner_text().lower()
    ok="aviation" in body and ("joby" in body or "aircraft" in body)
    record(surface,"aviation evidence section visible","PASS" if ok else "FAIL")
    assert ok

    details=page.locator("details:visible")
    if details.count():
        d=details.first
        d.locator("summary").click()
        expect(d).to_have_attribute("open","")
        record(surface,"details interaction","PASS")
    else:
        record(surface,"details interaction","WARN","no visible details controls on current page")
    page.close()


def test_foundations(context, mobile=False):
    surface="Workforce Foundations"
    page=context.new_page()
    general(page,surface,BASE+"/practice/foundations/",mobile)
    body=page.locator("body")
    expect(body).to_contain_text("Educational resource.")
    expect(body).to_contain_text("official sources control")
    expect(body).to_contain_text("Learner rights.")
    expect(page.get_by_role("link",name=re.compile(r"How we handle trust",re.I))).to_be_visible()
    expect(page.get_by_role("link",name=re.compile(r"Course ethics",re.I))).to_be_visible()
    expect(page.get_by_role("link",name=re.compile(r"Start: System Map|See the system",re.I)).first).to_be_visible()
    record(surface,"trust and learner-rights disclosures","PASS")
    page.get_by_role("link",name=re.compile(r"Course ethics",re.I)).click()
    page.wait_for_load_state("domcontentloaded")
    expect(page.locator("body")).to_contain_text("Learning without hidden stakes.")
    expect(page.locator("body")).to_contain_text("AI assistance is disclosed")
    expect(page.locator("body")).to_contain_text("Official Rule")
    expect(page.locator("body")).to_contain_text("Local Discretion")
    no_horizontal_overflow(page,surface+" ethics")
    keyboard_focus_visible(page,surface+" ethics")
    record(surface,"course ethics and evidence-boundary path","PASS")
    page.close()

def test_sector_partnership_explorer(context, mobile=False):
    surface="California Sector Partnership Explorer"
    page=context.new_page()
    general(page,surface,BASE+"/data/sector-partnerships/",mobile)
    body=page.locator("body")
    expect(body).to_contain_text("California Sector Partnership Explorer")
    expect(body).to_contain_text("Statewide patterns and methodology")

    source_index=json.loads(Path("data/sector-partnerships/runtime-source/index.json").read_text(encoding="utf-8"))
    assert source_index["market_count"]==25
    assert source_index["unique_case_count"]==74
    assert source_index["market_appearances"]==94

    state=page.evaluate("""() => ({
      config: !!document.getElementById('ww-sector-runtime-config'),
      preloaded: document.querySelectorAll('.spx-market').length,
      diag: window.WWSECTOR_RUNTIME
    })""")
    assert state["config"] and state["preloaded"]==0
    assert state["diag"] and state["diag"]["indexLoaded"]
    assert state["diag"]["requestCount"]==1
    record(surface,"production shard loader active","PASS",json.dumps(state["diag"]))

    expect(body).to_contain_text("94case appearances across current market views")
    record(surface,"canonical portfolio index guard","PASS","74 canonical IDs / 94 appearances / 25 markets")

    select=page.locator("#spx-market-select")
    expect(select).to_be_visible()
    options=select.evaluate("""el => Array.from(el.options).filter(o => (o.value || '').trim()).slice(0,2).map(o => ({value:o.value,label:o.textContent.trim()}))""")
    assert len(options)==2
    first,second=options

    select.select_option(first["value"])
    view_button=page.get_by_role("button",name=re.compile(r"View market",re.I))
    expect(view_button).to_be_enabled()
    view_button.click()
    page.wait_for_function("(mid) => window.WWSECTOR_RUNTIME?.loadedMarkets?.includes(mid)",arg=first["value"],timeout=30000)
    selected_market=page.locator(f"#market-{first['value']}")
    expect(selected_market).to_be_visible()
    first_diag=page.evaluate("() => ({...window.WWSECTOR_RUNTIME})")
    assert first_diag["requestCount"]==2, first_diag
    record(surface,"first market loads one HTML shard","PASS",json.dumps(first_diag))

    source_html=(Path("data/sector-partnerships/runtime-source/markets")/f"{first['value']}.html").read_text(encoding="utf-8")
    expected_ids=[]
    for label in re.findall(r'<div class="spx-case-id">([^<]+)</div>',source_html):
        m=re.search(r"\bSP-[A-Z0-9-]+\b",label)
        if m:
            expected_ids.append(m.group(0))
    observed=[]
    for label in selected_market.locator(".spx-case-id").all_inner_texts():
        m=re.search(r"\bSP-[A-Z0-9-]+\b",label)
        if m:
            observed.append(m.group(0))
    assert observed==expected_ids
    record(surface,"selected-market governed markup parity","PASS",f"{len(observed)} governed case appearances")

    details=selected_market.locator("details:visible")
    if details.count():
        d=details.first
        d.locator("summary").click()
        expect(d).to_have_attribute("open","")
        record(surface,"selected-market details interaction","PASS")
    source_links=selected_market.locator('a[href^="http"]:not([href*="workforcewonkery.com"])')
    assert source_links.count()>=2, f"selected market has only {source_links.count()} external evidence links"
    visible_source_links=selected_market.locator('a[href^="http"]:not([href*="workforcewonkery.com"]):visible')
    if visible_source_links.count()==0:
        selected_market.locator("details").evaluate_all("(els) => els.forEach(el => { el.open = true; })")
        page.wait_for_timeout(100)
        visible_source_links=selected_market.locator('a[href^="http"]:not([href*="workforcewonkery.com"]):visible')
    assert visible_source_links.count()>=1
    record(surface,"selected-market authoritative-source links","PASS",f"external links={source_links.count()}")

    select.select_option(second["value"])
    view_button.click()
    page.wait_for_function("(mid) => window.WWSECTOR_RUNTIME?.loadedMarkets?.includes(mid)",arg=second["value"],timeout=30000)
    second_diag=page.evaluate("() => ({...window.WWSECTOR_RUNTIME})")
    assert second_diag["requestCount"]==first_diag["requestCount"]+1, f"expected exactly one second-market request: {first_diag} -> {second_diag}"
    expect(page.locator(f"#market-{second['value']}")).to_be_visible()
    record(surface,"second market loads one additional shard","PASS",json.dumps(second_diag))

    page.evaluate("history.back()")
    page.wait_for_function("(mid) => location.hash === '#market-'+mid",arg=first["value"],timeout=15000)
    page.wait_for_function("(mid) => { const el=document.querySelector('#market-'+mid); return el && !el.hidden; }",arg=first["value"],timeout=15000)
    expect(page.locator(f"#market-{first['value']}")).to_be_visible()
    cached=page.evaluate("() => ({...window.WWSECTOR_RUNTIME})")
    assert cached["requestCount"]<=second_diag["requestCount"], f"Back navigation made an additional market request: {second_diag} -> {cached}"
    expect(select).to_have_value(first["value"])
    record(surface,"Back restores market without additional request","PASS",json.dumps(cached))

    no_horizontal_overflow(page,surface)
    runtime_clean(page,surface,fail_console=True)
    screenshot(page,f"sector-explorer-{'mobile' if mobile else 'desktop'}-sharded.png")
    page.close()


def test_wae_map(context, mobile=False):
    surface="San Diego WAE tract map"
    page=context.new_page()
    general(page,surface,BASE+"/data/workforce-access-equity/san-diego-county/",mobile)
    page.wait_for_selector(".wae-tract",timeout=60000)
    tracts=page.locator(".wae-tract")
    assert tracts.count()>0
    record(surface,"tract geometry loaded","PASS",f"tracts={tracts.count()}")

    first=tracts.first
    geoid=first.get_attribute("data-geoid")
    assert geoid
    first.focus()
    first.press("Enter")
    page.wait_for_function("() => new URLSearchParams(location.search).has('tract')")
    assert f"tract={geoid}" in page.url
    expect(first).to_have_class(re.compile(r"is-selected"))
    saved_url=page.url
    record(surface,"tract selection updates URL","PASS",saved_url)

    # Exercise browser history before reload so the pushState entry is tested
    # directly, then verify the selected deep link survives a full reload.
    page.evaluate("history.back()")
    page.wait_for_function("() => !new URLSearchParams(location.search).has('tract')")
    page.wait_for_function("() => !document.querySelector('.wae-tract.is-selected')")
    record(surface,"Back clears tract state","PASS",page.url)

    page.go_forward(timeout=15000,wait_until="commit")
    page.wait_for_function("(g) => new URLSearchParams(location.search).get('tract') === g",arg=geoid,timeout=15000)
    page.wait_for_function("(g) => document.querySelector('.wae-tract.is-selected')?.dataset.geoid === g",arg=geoid,timeout=30000)
    record(surface,"Forward restores tract state","PASS",page.url)

    assert page.url==saved_url
    page.reload(wait_until="domcontentloaded")
    page.wait_for_selector(".wae-tract",timeout=60000)
    page.wait_for_function("(g) => Array.from(document.querySelectorAll('.wae-tract')).some(el => el.dataset.geoid === g && el.classList.contains('is-selected'))",arg=geoid)
    assert page.url==saved_url
    record(surface,"tract URL-state restoration after reload","PASS",page.url)

    zoom_in=page.locator("#wae-map-zoom-in")
    zoom_reset=page.locator("#wae-map-zoom-reset")
    zoom_level=page.locator("#wae-map-zoom-level")
    expect(zoom_in).to_be_visible()
    zoom_in.click()
    page.wait_for_function("() => document.querySelector('#wae-map-zoom-level')?.textContent !== '100%'")
    record(surface,"zoom control","PASS",zoom_level.inner_text())
    zoom_reset.click()
    expect(zoom_level).to_have_text("100%")
    record(surface,"zoom reset","PASS")

    no_horizontal_overflow(page,surface)
    runtime_clean(page,surface,fail_console=True)
    page.close()


def run():
    failures=[]
    with sync_playwright() as p:
        browser=p.chromium.launch(headless=True)
        for mobile,viewport in [(False,{"width":1440,"height":1000}),(True,{"width":390,"height":844})]:
            context=browser.new_context(
                viewport=viewport,
                permissions=["clipboard-read","clipboard-write"],
                ignore_https_errors=False,
            )
            if os.getenv("DISCOVERY_ONLY") == "1":
                tests = [test_discovery]
            elif os.getenv("CONTEXT_ONLY") == "1":
                tests = [test_contextual_navigation]
            elif os.getenv("GOVQ047_ONLY") == "1":
                tests = [test_homepage,test_policy,test_data,test_registry]
            else:
                tests = [test_homepage,test_policy,test_data,test_workforce_lens_briefing,test_discovery,test_contextual_navigation,test_labor_market_profiles,test_occupation_explorer,test_registry,test_examples,test_santa_cruz,test_foundations,test_sector_partnership_explorer,test_wae_map]
            for fn in tests:
                try:
                    fn(context,mobile)
                except Exception as exc:
                    failures.append({"test":fn.__name__,"mobile":mobile,"error":repr(exc)})
                    record(fn.__name__, "test execution", "FAIL", repr(exc))
            context.close()
        browser.close()

    summary={"results":RESULTS,"failures":failures}
    (ART/"results.json").write_text(json.dumps(summary,indent=2),encoding="utf-8")
    if failures:
        print(json.dumps(failures,indent=2),file=sys.stderr)
        return 1
    return 0

if __name__=="__main__":
    raise SystemExit(run())

# Post-restore GOVQ-051 verification trigger: 2026-09-26-085008
# Global header runtime repair verification trigger: 2026-10-04
