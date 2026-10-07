# Living Policy Records

Status: backend foundation plus reader module implemented October 5, 2026.

Each published policy brief can now become a durable record with identity, lifecycle status, dated milestones, authoritative relationships, deadlines, role-specific actions, and source provenance.

## Authority boundary

The ordinary Policy Library remains the broad inventory. Lifecycle status, deadlines, supersession, amendment, and implementation relationships are added only when explicitly governed in `governance/policy-record-overrides.json` and backed by an authoritative HTTPS source.

The Intelligence Graph may still make conceptual or geographic connections. Those connections do not establish legal supersession or amendment.

## Generated products

- `generated/public/policy/records.json`
- `generated/public/policy/deadlines.json`
- `generated/public/policy/deadlines.ics`
- enriched Universal Discovery policy records with status, key date, document type, jurisdiction, and official source

Governed coverage is expanded in prioritized sprints. As of October 6, 2026, 23 records have verified lifecycle data; the remaining briefs stay indexed living records and can be enriched incrementally without changing URLs.

## Reader roles

Director, Fiscal, Program, and Board member are the initial role lenses. Role actions are practical editorial guidance, not controlling authority.

## Reader module

The single policy template now includes `wordpress/fragments/policy-living-record.html`. It looks up the current brief by canonical URL against a hidden WordPress runtime page (`ww-runtime-policy-records`) containing the generated 234-record dataset.

All indexed briefs can show identity, document type, jurisdiction, and official source. Only `record_state=governed` records may show verified lifecycle status, timeline, key dates, authoritative relationships, and role-specific actions.

The role selector uses the local browser key `ww-reader-role`, intentionally matching the future site-wide reader-preference system. A role preference ranks/display actions only; it does not hide general policy content.

## Next reader-facing work

Publish the noindex policy-record runtime and single-post template, then expand authoritative lifecycle backfill, add memo/print outputs, and extend the same local reader preference to place as well as role.
