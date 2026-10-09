# Workforce Wonkery Website

**Policy. Data. Practice. Decoded.**

This is the public development home for Workforce Wonkery reader-facing WordPress source, public datasets, accessible testing, and reusable documentation.

## Repository ownership

- **Public-owned website source:** `src/wordpress/` contains the source of approved website pages, shared components, CSS, JavaScript, and selected WordPress plugin code. Changes are reviewed through public pull requests.
- **Private-owned generated outputs:** `data/`, public methodology exports, and the `PROVENANCE.json` manifest are exported from the protected Workforce Wonkery control repository. Public changes to generated files must be reconciled back into their source, not edited in place.
- **Protected production operations:** the separate private repository owns research under review, governance records, production WordPress transactions, deployment credentials, and newsletter delivery safeguards.

## How a website change reaches readers

1. Propose a change to `src/wordpress/` on a public branch.
2. Run CI, including the relevant browser, accessibility, syntax, and data checks, and receive review.
3. Merge into public `main`. **This is not a WordPress deployment.**
4. Manually import the exact approved public main commit using the private workflow `Import approved public website source`.
5. Review the generated private pull request, pass the private source and publication gates, then use the governed Publisher to update WordPress and verify the live site.

The existing WordPress website remains the public publication platform. No public pull request or public CI job receives production publishing credentials.

## Data sync and provenance

The private exporter uses an explicit allowlist and records generated files in `PROVENANCE.json`. It cannot write to, overwrite, or delete the public-owned `src/wordpress/` tree. Public `main` and the generated sync branch must not diverge for unrelated reasons, or promotion stops for review.

## Contribution, security and licensing

See `CONTRIBUTING.md`, `SECURITY.md`, and `LICENSE-NOTICE.md`. Do not commit private information or credentials. Visibility is not an open-source license; reuse requires separate authorization until a license is adopted.

## Migration status

The public-first model is being introduced through coordinated pull requests. Until those pull requests are merged and verified, the earlier private-first sync and production workflow remain authoritative.
