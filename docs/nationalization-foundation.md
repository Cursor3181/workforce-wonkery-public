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

The foundation originally kept the selector dark. The public Workforce Lens is now active, while California remains the only deep jurisdiction and other jurisdictions use transparent national fallback.

Generated public assets are committed with the foundation so GitHub contract checks remain reproducible before merge.

### Browser preference helper

`wordpress/javascript/workforce-lens-runtime.js`

Stores only country code, state code, selected area ID, and selected role ID in local browser storage. It performs no geolocation and sends no preference to a third party.

## Readiness model

California is the reference `deep` State Desk because it already has mature policy, data, practice, and local-market products.

Every other state begins as `schema_ready`. This means the geography and routing architecture is ready, not that a complete State Desk has been published.

## Backward compatibility

Phase 1 does not change the homepage, show a state selector, redirect visitors, infer a visitor's location, replace California URLs, alter existing WordPress publication, or introduce a runtime AI dependency.

## Current reader phase

The national Workforce Lens foundation remains built and governed, but the **public For Me / My Briefing experience is paused** while the product is developed further. The public header and navigation do not expose the Lens, and the paused shell clears previously stored Lens preferences so hidden personalization does not continue without a visible control.

The underlying geography, role, fallback, and Jurisdiction Desk models remain available for development and future relaunch.

The next nationalization step is still substantive coverage: pilot one non-California Jurisdiction Desk before treating another jurisdiction as deep.

## 2026-10-06 reader launch reconciliation

The canonical Workforce Lens now models 57 workforce jurisdictions while preserving the existing California deep experience. The public selector is user-controlled, does not geolocate, and stores the selected jurisdiction, local area where governed, and reader role in the browser. California remains the only deep jurisdiction; incomplete jurisdictions use transparent national fallback rather than relabeling national content as jurisdiction-specific.
