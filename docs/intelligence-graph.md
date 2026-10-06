# Workforce Wonkery Intelligence Graph

State: Phase 1 backend foundation  
Implemented: October 4, 2026

## Purpose

Universal Discovery answers **where is the thing I need?**

The Intelligence Graph adds a second layer: **what is this connected to, and what should I examine next?**

It converts Workforce Wonkery's governed content and data products into canonical entities and typed, evidence-backed relationships. It does not use an AI service at runtime and does not change the public design in Phase 1.

## Authority

The graph is generated from already governed public assets, primarily:

- Universal Discovery;
- Labor Market Profiles;
- Sector Partnership Explorer;
- Occupation Explorer;
- Content Inventory;
- Public Content Registry;
- governed Discovery aliases.

Relationship and entity rules live in:

`governance/intelligence-graph-rules.json`

The generator is:

`qa/build_intelligence_graph.py`

The contract is:

`qa/intelligence_graph_contract.py`

Generated assets live under:

`generated/public/intelligence-graph/`

## Entity model

Phase 1 supports these canonical entity kinds:

- policy;
- policy digest;
- occupation;
- geography;
- training opportunity;
- sector partnership;
- access and equity;
- practice;
- report;
- data tool;
- methodology;
- page;
- concept;
- agency;
- program;
- funding source;
- organization type;
- geography type.

Discovery records remain the intake layer, but the graph can canonicalize them further.

The first important example is Sector Partnership Explorer. It contains 94 market appearances but 74 unique cases. The graph represents those as **74 canonical sector-partnership entities** connected to the markets where they appear.

## Relationship model

Phase 1 creates only deterministic relationships that can be supported by governed metadata.

### `addresses_concept`

A reader-facing entity contains an exact governed concept, acronym, or alias phrase.

Examples:
- a policy brief addresses Eligible Training Provider List;
- a practice guide addresses On-the-Job Training;
- a report addresses Artificial Intelligence.

This is phrase-boundary matching, not fuzzy semantic inference.

### `applies_to_geography`

The entity has a governed Geography value that maps to a canonical geography entity.

### `appears_in_market`

A canonical sector-partnership case has an explicit market appearance in Sector Partnership Explorer.

### `training_for_occupation`

A training Decision Brief has an exact normalized title match to a canonical occupation.

No relationship is created merely because two pages seem generally similar.

## Context layer

Every entity receives one precomputed context record containing:

- direct graph relationships;
- concept/program/agency/funding connections;
- geography connections;
- a short ranked set of related reader destinations.

Recommendations are deterministic. They are ranked from:

1. direct relationships;
2. shared geography;
3. shared governed concepts;
4. cross-content-type usefulness;
5. existing Discovery priority.

Recommendations are capped and diversified by entity kind so one content family does not crowd out all others.

## Change propagation

`impact-index.json` is the first backend for bounded change propagation.

For concept, program, agency, funding, organization-type, geography-type, and geography nodes it records the governed entities directly connected to that node.

This does **not** claim that every connected object must change when a source changes. It identifies a bounded review set.

Example:

`Eligible Training Provider List`
→ connected policies  
→ connected training opportunities  
→ connected practice guidance

The Evidence Change Sentinel or Managing Editor can use that set later to determine what actually requires review.

## Sharding

Graph runtime assets are intentionally small.

- Entity records are sharded by entity kind.
- Relationship records use 16 deterministic SHA-1 modulo shards.
- Context records use the same 16-shard strategy.
- The manifest carries a graph-wide SHA-256 fingerprint and fingerprints for every shard.

A future public feature can calculate the shard for a known entity ID without downloading the whole graph.

## Phase 2 reader context runtime

The first reader-facing graph capability is active.

The manifest now reports:

`public_ui_enabled: true`

Eligible detail pages load one compact reader-context shard through the WordPress REST API. The global renderer identifies the current governed entity from the WordPress body class, calculates its deterministic graph shard, verifies the shard SHA-256 from the active runtime index, and renders the module only when at least two governed destinations are available.

Current eligible entity kinds:

- policy;
- practice;
- intelligence report;
- training opportunity;
- access and equity.

The module renders:

- **Connected intelligence** as the editorial label;
- **What this connects to** as the reader-facing heading;
- up to three governed concept/program/funding facets;
- up to four unique internal recommendations.

The active runtime is recorded in `wordpress/runtime-assets/intelligence-context-20261004.json`. WordPress runtime shards are noindex and are not included in Discovery.

Live desktop and mobile acceptance covers an AB 1534 policy brief and the Workforce Funding Foundations lesson. Acceptance requires expected facets, at least two unique internal recommendations, no horizontal overflow, and no first-party runtime/resource errors.

## Next visitor uses

The graph can now be extended to support:

- geography-specific contextual modules inside labor-market tools;
- selected occupation-to-training pathways;
- policy-to-data-to-practice decision paths;
- better Universal Discovery ranking using graph relationships;
- regional "what should we pay attention to?" briefs;
- bounded change propagation after new policy or source releases.

## Safety rule

The graph may suggest **review**. It must not infer that a source change automatically invalidates or changes a published conclusion.

Existing source-resilience, claim-impact, and publication governance remain authoritative.


## National geography foundation

_Implemented October 5, 2026._

The Intelligence Graph now has a canonical United States geography hierarchy from `data/geography/us-states.json`.

Phase 1 seeds:

- one United States geography entity;
- all 50 states plus the District of Columbia;
- deterministic `part_of_geography` relationships from each state/DC to the United States;
- a migration bridge from each currently published labor market to California;
- additive `scope_levels`, `state_codes`, and `audience_roles` metadata on graph entities.

The public reader-context runtime is intentionally isolated from this backend expansion. Existing "What this connects to" reader shards remain unchanged unless reader-facing recommendations actually change. Runtime integrity is therefore checked against the exact reader shard hashes rather than the full internal graph fingerprint.

This allows the graph to become nationally aware without forcing a WordPress redeploy or changing the current California reader experience.

The Workforce Lens selector contract and rollout rules are documented in `docs/nationalization-foundation.md`.
