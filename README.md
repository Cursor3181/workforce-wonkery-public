# Workforce Wonkery Public

**Policy. Data. Practice. Decoded.**

This repository is the public companion to Workforce Wonkery. It contains selected reader-facing code, public runtime data, and reusable methodology from the project behind workforcewonkery.com.

## What is here

- public data used by Workforce Wonkery tools
- selected WordPress CSS, JavaScript, and plugin code
- selected methodology and design documentation
- reusable editorial standards for workforce-development analysis

## What is not here

The private Workforce Wonkery control repository remains the source of truth for internal governance, QA, research, drafts, publication controls, automation instructions, and operational history.

This public repository intentionally excludes those materials.

## How this repository is produced

Content is exported from the private control repository through an explicit allowlist. Files are not copied here simply because they exist in the private repository.

Each release should include a provenance record showing the source commit used for the export.

## Use and licensing

Public visibility does not by itself grant an open-source license. See `LICENSE-NOTICE.md`.

## Security

Please see `SECURITY.md` before reporting a possible security issue.

## Contributing

Suggestions, corrections, and public-facing improvements are welcome. See `CONTRIBUTING.md`.


## Continuous integration

Public-only validation runs here, including public data checks and live-site browser/structure acceptance. This keeps public testing separate from the private Workforce Wonkery control plane.

This repository is generated from an explicit allowlist in the private source-of-truth repository. If a public pull request changes generated or mirrored material, the accepted change must be reconciled back into the private source before the next sync.
