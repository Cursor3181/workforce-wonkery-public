# Workforce Wonkery public WordPress source

This `src/wordpress/` tree is the public development home for approved, reader-facing code and page templates. It is separate from the private operations and publication system.

- `css/`, `javascript/`, and `plugins/`: public website code
- `templates/`, `template-parts/`, and `fragments/`: selected reader-facing WordPress source
- Changes go through a public branch and pull request, with CI checks.
- Public merges **do not publish to WordPress**. A reviewed public commit must be brought into the private repository with the controlled manual import workflow; the private Publisher still handles approval, snapshots, rollback, and live verification.
- Never commit credentials, unpublished research, confidential County records, subscriber details, or participant data.
- Generated data and documentation in the rest of the public repository are maintained by a separate, allowlisted export from the private control system, whose provenance is recorded in `PROVENANCE.json`. That export must never replace this directory.

See [LICENSE-NOTICE.md](../../LICENSE-NOTICE.md). Public visibility alone does not grant permission to reuse copyrighted material.

**Cutover note:** Public ownership starts only after the coordinated private-sync change is approved and verified. Until then the existing synchronization rules remain in force.
