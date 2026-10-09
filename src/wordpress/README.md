# Workforce Wonkery public WordPress source

This `src/wordpress/` tree is the public development home for approved, reader-facing code and page templates. It is separate from the private operations and publication system.

- `css/`, `javascript/`, and `plugins/`: public website code
- `templates/`, `template-parts/`, and `fragments/`: selected reader-facing WordPress source
- Changes go through a public branch and pull request, with CI checks.
- Public merges **do not publish to WordPress**. A reviewed public commit must be brought into the private repository with the controlled manual import workflow; the private Publisher still handles approval, snapshots, rollback, and live verification.
- Never commit credentials, unpublished research, confidential County records, subscriber details, or participant data.
- Generated data and documentation in the rest of the public repository are maintained by a separate, allowlisted export from the private control system, whose provenance is recorded in `PROVENANCE.json`. That export must never replace this directory.

## WAE and sector page blueprints

The `fragments/wae-map-engine-v2-*.html` files are reusable WordPress source templates. A governed builder fills placeholders such as `{{AREA_NAME}}` and JSON-array slots before publication. Public CI substitutes empty arrays for the two known JSON placeholders **only in temporary syntax-check copies**. The published source is never changed by this test.

WAE uses public aggregate geography information, never participant-level records. `enhancements/` contains reusable sector brief presentation source. Superseded prototypes and paused reader experiences are not automatically treated as current public source.

See [LICENSE-NOTICE.md](../../LICENSE-NOTICE.md). Public visibility alone does not grant permission to reuse copyrighted material.

**Cutover:** Public-first ownership and protected synchronization were verified on October 9, 2026. The private repository remains the publication and operational authority.
