# Workforce Deadlines

Status: live product; phase-two deadline coverage and timed-event support implemented October 5, 2026.

## Purpose

Workforce Deadlines turns governed policy dates into a reusable planning product. It reads from the living-policy deadline registry rather than maintaining a second editorial calendar.

## Reader experience

The page at the intended route `/workforce-deadlines/` provides:

- an editorial "next on the calendar" lead;
- role filters for Director, Fiscal, Program, and Board member;
- topic and date-type filters;
- 90-day, 12-month, and all-future time horizons;
- optional past-date display;
- keyword search;
- shareable filter state in the URL;
- direct links to the Workforce Wonkery brief and official authority;
- per-event Google Calendar links;
- per-event and filtered-calendar ICS downloads;
- exact Pacific-time handling for governed timed deadlines such as grant submissions.

The page is intentionally not presented as a compliance calendar. Only dates backed by the governed policy-record layer appear.

## Runtime pattern

The reader page fetches a noindex WordPress runtime page by the stable slug `ww-runtime-policy-deadlines`. That runtime page should contain:

```html
<script id="ww-policy-deadlines-runtime" type="application/json">...</script>
```

The payload is the generated `generated/public/policy/deadlines.json` content. Fetching by slug avoids coupling the reader page to a WordPress page ID.

## Calendar subscription

The UI supports an optional `feed_url` field in the runtime payload. If a stable public ICS endpoint is available, the page automatically exposes a webcal subscription button. Until a stable endpoint exists, the product uses deterministic ICS downloads and per-event Google Calendar links rather than claiming a subscription that may not refresh.

## Accessibility

The page uses native form controls, visible focus, an aria-live result count, semantic `time` elements, responsive layout, and reduced-motion handling. Deadline text is inserted with DOM text nodes rather than raw HTML.

## Publication

GitHub remains the source of truth. Publication requires:

1. a noindex WordPress runtime page using the stable runtime slug;
2. a published reader page at `/workforce-deadlines/`;
3. read-back verification that the runtime contains the governed dates and the reader page contains the calendar application markers;
4. optional discovery/navigation wiring after the live page URL is accepted.
