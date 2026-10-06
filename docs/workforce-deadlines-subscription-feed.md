# Workforce Deadlines Subscription Feed

Status: implementation candidate, October 5, 2026.

## Stable URL

`https://workforcewonkery.com/workforce-deadlines.ics`

The feed is served by the first-party plugin in:

`wordpress/plugins/workforce-wonkery-deadlines-feed/workforce-wonkery-deadlines-feed.php`

## Design

The plugin does not contain policy dates. On every feed request it reads the accepted, noindex WordPress runtime page with slug `ww-runtime-policy-deadlines`, extracts the `ww-policy-deadlines-runtime` JSON payload, and renders RFC 5545-compatible iCalendar output.

That means subscribers keep one permanent URL while the calendar changes whenever the governed WordPress deadline runtime changes.

## Interoperability

The endpoint returns `text/calendar`, a stable filename, ETag/Last-Modified cache validators, one-hour calendar refresh hints, all-day boundaries, and timezone-aware timed events.

Readers can:

- use the `webcal:` Subscribe button for compatible desktop/mobile calendar apps;
- copy the HTTPS subscription URL into Google Calendar's **Add calendar → From URL**;
- use the same HTTPS URL in Outlook's subscription/import-by-web flow.

## Authority boundary

The endpoint is only a rendering layer. It never discovers or infers deadlines. Source authority remains:

`governance/policy-record-overrides.json → generated/public/policy/deadlines.json → accepted WordPress deadline runtime → subscription feed`

If the runtime payload is missing or invalid, the endpoint returns HTTP 503 rather than serving stale or invented events.

## Deployment

The plugin requires a one-time upload and activation on the Atomic WordPress site. WordPress plugin-management writes require explicit user confirmation.

After activation:

1. verify the HTTPS endpoint returns `text/calendar`;
2. verify all nine governed event UIDs are present;
3. verify the two 11:59 p.m. Pacific deadlines are timed events;
4. publish the deadline runtime with its `feed_url` field so the reader page exposes Subscribe and Copy subscription URL controls;
5. record acceptance in the deployment manifest.
