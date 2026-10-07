# My Briefing

Status: development retained; public surface paused October 6, 2026.

## Public status

My Briefing is currently **paused from the public site** at the owner's request. The source, runtime design, and development contracts remain in GitHub so the product can be improved before relaunch. Public navigation, sitewide Lens prompts, and page publication are disabled while this state is `paused`.

## Purpose

My Briefing is designed to turn the **For Me / Workforce Lens** page into a proactive reader briefing.

The page answers a bounded question:

> What should I pay attention to right now, given the place and role I saved in my Workforce Lens?

It does not create a recommendation engine and does not make a runtime AI request.

## Reader experience

When a reader has a saved Lens, `/for-me/` presents four sections before the Lens editor:

1. **Needs attention** — up to five time-sensitive or highly relevant governed items.
2. **What changed** — new or changed governed records compared with the prior briefing snapshot stored on that device.
3. **Your local signals** — a small set of local labor-market measures when the selected market has governed Labor Market Profile coverage.
4. **Questions worth asking** — bounded questions that hand off to Universal Discovery and the Decision Brief Builder.

The Lens editor remains on the same page and is collapsed after a successful briefing load.

## Runtime sources

My Briefing reuses accepted same-origin WordPress runtimes. It does not introduce a new evidence store.

- Workforce Deadlines runtime: `ww-runtime-policy-deadlines`
- Universal Discovery policy shard
- Universal Discovery practice shard
- Universal Discovery site shard
- Labor Market Profiles runtime index
- the selected Labor Market Profiles market shard

These sources remain authoritative for their own fields and release controls.

## Ranking and scope

### Geography

A record may enter the briefing when it:

- explicitly matches the selected local market;
- explicitly matches the selected jurisdiction; or
- is genuinely national and has no conflicting jurisdiction code.

National fallback content remains available when a jurisdiction does not yet have deep Workforce Wonkery coverage. California-only material must not be silently relabeled for another jurisdiction.

### Role

Explicit `audience_roles` metadata receives the strongest role boost.

Where explicit role metadata is absent, a small governed role-term vocabulary provides an additive relevance score. This changes ordering only. It does not make a record applicable when its geography does not fit.

### Needs attention

Upcoming governed deadlines within 120 days are considered first. The reader's deadline role filter is honored.

The remaining slots are filled from relevant current Policy, Intelligence Report, and Practice records. The product shows **why the item is here** rather than hiding the ranking logic.

## What changed

The browser stores a compact record-signature snapshot under:

`ww_workforce_briefing_snapshot_v1`

A later visit compares current governed record signatures with that snapshot.

The comparison can identify:

- a newly added record;
- a changed title, date, summary, lifecycle date/status, official source, or deadline field.

This is device-local convenience state, not a governance record and not an account feature.

On a first visit, the page shows recent governed items from the prior 14 days and records the first baseline.

## Local signals

Local signals are available only when the selected Lens includes a governed California Labor Market Profile market.

The first release may show:

- local living-wage benchmark;
- largest projected opening count in the maintained 40-occupation decision set;
- fastest projected growth in that maintained set; and
- count of occupations with a published median annual wage at or above the annualized local living-wage benchmark.

Every signal must carry its source period and an explicit limit. In particular:

- the 40-occupation decision set is not the full labor market;
- projected openings do not prove employer demand today;
- high growth can reflect a small base;
- wage coverage across the maintained set is not the share of all jobs paying a living wage.

## Questions worth asking

Questions are deterministic prompts created from:

- the highest-priority deadline;
- local opening and growth signals; and
- the saved reader role.

Each question links to `/discover/?q=...`, where the reader can use **Build decision brief**.

The questions are prompts for investigation, not recommendations.

## Trust boundary

My Briefing must never:

- say that a program, investment, partnership, training strategy, or policy response should be approved;
- convert search relevance into evidence strength;
- infer current employer demand from projection data alone;
- infer causal effectiveness from a practice example;
- present California-only content as applicable to another jurisdiction;
- claim that a local signal covers the full labor market when it comes from the maintained occupation set;
- replace official policy guidance; or
- hide evidence limits.

The page must continue to state that it is deterministic and does not make a runtime AI request.

## Acceptance

Repository contracts require:

- valid My Briefing JSON configuration;
- syntactically valid inline application JavaScript;
- all four briefing sections;
- the device-local snapshot key;
- Decision Brief handoff links; and
- trust-boundary language.

Live browser acceptance seeds a Santa Cruz-Watsonville + Director Lens and verifies on desktop and mobile:

- at least three Needs attention items;
- the AI workforce deadline appears;
- at least one first-visit change item;
- at least three local market signals;
- living-wage/source labels;
- at least two questions;
- at least two Decision Brief handoff links;
- no horizontal overflow; and
- no first-party runtime errors.
