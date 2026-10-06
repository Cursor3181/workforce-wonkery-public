# Workforce Wonkery Nationalization Foundation

State: Phase 1 implemented

## Product rule

Workforce Wonkery uses one national intelligence system with state and local lenses layered on top.

The state lens changes the answer. It is not merely a filter.

The geography hierarchy is:

`United States -> state/DC -> local workforce or labor-market area`

Audience context is independent of geography and currently supports:

- Director / Executive
- Fiscal
- Program
- Business Services
- Board Member
- Education / Training Partner
- Research / Policy

## Phase 1 foundation

### Canonical geography registry

`data/geography/us-states.json`

Stable IDs, USPS abbreviations, FIPS codes, aliases, and parent relationships for the United States, all 50 states, and the District of Columbia.

### Workforce Lens contract

`governance/workforce-lens-rules.json`

Defines role IDs, browser persistence, selection fields, and the California migration bridge.

The Lens never auto-detects location. State, area, and role are explicit user choices. No account is required.

### Generated runtime

`generated/public/workforce-lens/runtime.json`

Exposes the national selector model, current published California labor-market areas, role taxonomy, and readiness metadata.

Phase 1 deliberately sets `public_ui_enabled: false`. The live California experience does not change merely because the national model exists.

Generated public assets are committed with the foundation so GitHub contract checks remain reproducible before merge.

### Browser preference helper

`wordpress/javascript/workforce-lens-runtime.js`

Stores only country code, state code, selected area ID, and selected role ID in local browser storage. It performs no geolocation and sends no preference to a third party.

## Readiness model

California is the reference `deep` State Desk because it already has mature policy, data, practice, and local-market products.

Every other state begins as `schema_ready`. This means the geography and routing architecture is ready, not that a complete State Desk has been published.

## Backward compatibility

Phase 1 does not change the homepage, show a state selector, redirect visitors, infer a visitor's location, replace California URLs, alter existing WordPress publication, or introduce a runtime AI dependency.

## Next phase

Phase 2 should activate a compact state/area/role control in Universal Discovery and Workforce Deadlines, rank exact-local then state then national context, preserve an explicit All U.S. option, and pilot one non-California State Desk before broader rollout.
