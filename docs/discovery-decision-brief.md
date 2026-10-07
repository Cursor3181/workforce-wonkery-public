# Universal Discovery Decision Brief Builder

Status: implemented October 6, 2026.

## Purpose

Move Universal Discovery from search and routing into bounded decision support without turning relevance ranking into a recommendation engine.

A reader starts with the same plain-language question already used for Discovery. After the governed search completes, the reader can build a decision brief that organizes the current result set into:

- Policy evidence;
- Data evidence;
- Practice evidence;
- saved Workforce Lens context;
- explicit evidence gaps;
- questions to resolve before acting;
- source links; and
- evidence limits.

The brief can be copied or printed for a staff meeting, board discussion, partner conversation, or research handoff.

## Trust boundary

The Decision Brief Builder is deterministic and runs entirely from the governed Universal Discovery index already loaded in the browser. It does not make a runtime AI request.

The builder must never:

- convert search rank into evidence strength;
- tell a reader that a program, investment, partnership, or policy response should be approved;
- infer employer demand from labor-market data alone;
- infer causal effectiveness from a practice example;
- treat a Workforce Wonkery policy summary as controlling authority;
- hide a missing evidence family; or
- silently replace local validation, fiscal review, partner agreement, or professional judgment.

When a Policy, Data, or Practice family is absent from the result set, the brief must say so and turn the gap into a decision question.

## Evidence selection

The brief takes up to:

- two Policy matches;
- two Data matches;
- two Practice matches; and
- one Intelligence Report when available.

The underlying Discovery ranking remains Lens-aware, but the brief requests the full cross-domain ranked result set even when the reader has temporarily filtered the visible search results to one family.

## Reader context

The saved Workforce Lens contributes only reader context and ranking:

- jurisdiction or local area;
- reader role.

It does not hide broader results or change the meaning of the evidence.

Role-specific questions may be added for Director / Executive, Fiscal, Program, Business Services, Board Member, Education / Training Partner, and Research / Policy readers.

## Output contract

Every generated brief contains:

1. the reader's question;
2. the active Lens context;
3. Policy / Data / Practice coverage;
4. evidence cards with Workforce Wonkery links and official-source links where available;
5. questions to resolve; and
6. a section titled **What this does not establish**.

Copy output preserves the source URLs and evidence-limit language. Print output isolates the brief from the surrounding search interface.

## Verification

Repository source contracts require the Decision Brief Builder markers and evidence-limit language.

Browser acceptance must verify at desktop and mobile that:

- a normal Discovery query can build a brief;
- the brief exposes all three coverage categories;
- evidence links are present;
- evidence limits are visible; and
- copy output succeeds with source-link and evidence-limit confirmation.
