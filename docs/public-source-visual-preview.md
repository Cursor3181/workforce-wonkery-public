# Public-source visual preview

This test assembles **already-public** WordPress template source and site chrome into local, noindex HTML and renders six reader-facing surfaces at desktop (1440px), tablet (768px), and mobile (390px).

Run with `python -m pip install playwright==1.63.0`, `python -m playwright install chromium`, then `python tests/public_source_visual_preview.py`. CI runs it in the public repository, at no private Actions runner cost.

The test checks for a single page root, visible primary heading, shared header/footer, and horizontal overflow. It saves screenshots for 1440px and 390px under `qa/artifacts/public-preview/`, retained for seven days by public CI.

**Boundaries:** Scripts and remote requests are disabled in this static preview. WordPress navigation is represented by a stand-in, not an authenticated theme render. This is **not** an equivalent replacement for private candidate-preview tests, dynamic behavior tests, or WordPress publishing readback. Keep the existing public live browser acceptance and private publication source/rollback gates.

Do not copy `preview/`, private `qa/editorial-shell/`, private `wordpress/snapshots/`, unpublished research, or subscriber data into this repository.
