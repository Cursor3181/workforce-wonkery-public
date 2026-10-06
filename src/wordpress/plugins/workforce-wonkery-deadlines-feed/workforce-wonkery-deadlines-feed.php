<?php
/**
 * Plugin Name: Workforce Wonkery Deadlines Feed
 * Description: Serves the governed Workforce Deadlines runtime as a stable public iCalendar subscription feed.
 * Version: 1.0.0
 * Author: Workforce Wonkery
 * License: GPL-2.0-or-later
 */

if ( ! defined( 'ABSPATH' ) ) {
	exit;
}

const WWDF_FEED_PATH = '/workforce-deadlines.ics';
const WWDF_RUNTIME_SLUG = 'ww-runtime-policy-deadlines';
const WWDF_RUNTIME_SCRIPT_ID = 'ww-policy-deadlines-runtime';

function wwdf_request_path() {
	$uri = isset( $_SERVER['REQUEST_URI'] ) ? wp_unslash( $_SERVER['REQUEST_URI'] ) : '';
	$path = wp_parse_url( $uri, PHP_URL_PATH );
	return is_string( $path ) ? rawurldecode( $path ) : '';
}

function wwdf_ical_escape( $value ) {
	$value = wp_strip_all_tags( (string) $value );
	$value = str_replace( '\\', '\\\\', $value );
	$value = str_replace( array( "\r\n", "\r", "\n" ), '\\n', $value );
	return str_replace( array( ';', ',' ), array( '\\;', '\\,' ), $value );
}

function wwdf_fold_line( $line ) {
	$line = (string) $line;
	if ( strlen( $line ) <= 74 ) {
		return $line;
	}

	$parts = array();
	while ( strlen( $line ) > 74 ) {
		$chunk = function_exists( 'mb_strcut' ) ? mb_strcut( $line, 0, 74, 'UTF-8' ) : substr( $line, 0, 74 );
		if ( '' === $chunk ) {
			break;
		}
		$parts[] = $chunk;
		$line = ' ' . substr( $line, strlen( $chunk ) );
	}
	$parts[] = $line;
	return implode( "\r\n", $parts );
}

function wwdf_runtime_payload() {
	$page = get_page_by_path( WWDF_RUNTIME_SLUG, OBJECT, 'page' );
	if ( ! $page || 'publish' !== $page->post_status ) {
		return new WP_Error( 'wwdf_runtime_missing', 'The governed deadline runtime is unavailable.' );
	}

	$pattern = '/<script[^>]+id=["\']' . preg_quote( WWDF_RUNTIME_SCRIPT_ID, '/' ) . '["\'][^>]*>(.*?)<\/script>/s';
	if ( ! preg_match( $pattern, $page->post_content, $match ) ) {
		return new WP_Error( 'wwdf_payload_missing', 'The governed deadline payload is unavailable.' );
	}

	$raw = html_entity_decode( trim( $match[1] ), ENT_QUOTES | ENT_HTML5, 'UTF-8' );
	$data = json_decode( $raw, true );
	if ( ! is_array( $data ) || '1.0' !== ( $data['schema_version'] ?? '' ) || ! isset( $data['records'] ) || ! is_array( $data['records'] ) ) {
		return new WP_Error( 'wwdf_payload_invalid', 'The governed deadline payload is invalid.' );
	}

	return array(
		'page' => $page,
		'data' => $data,
		'raw'  => $raw,
	);
}

function wwdf_next_day( $date ) {
	try {
		$day = new DateTimeImmutable( $date . ' 12:00:00', new DateTimeZone( 'UTC' ) );
		return $day->modify( '+1 day' )->format( 'Ymd' );
	} catch ( Exception $e ) {
		return preg_replace( '/[^0-9]/', '', (string) $date );
	}
}

function wwdf_build_calendar( $payload ) {
	$data = $payload['data'];
	$reviewed = preg_replace( '/[^0-9]/', '', (string) ( $data['last_reviewed'] ?? gmdate( 'Y-m-d' ) ) );
	$stamp = substr( $reviewed, 0, 8 ) . 'T000000Z';

	$lines = array(
		'BEGIN:VCALENDAR',
		'VERSION:2.0',
		'PRODID:-//Workforce Wonkery//Workforce Deadlines//EN',
		'CALSCALE:GREGORIAN',
		'METHOD:PUBLISH',
		'X-WR-CALNAME:Workforce Wonkery Workforce Deadlines',
		'X-WR-CALDESC:Governed workforce policy dates. Official sources control.',
		'X-WR-TIMEZONE:America/Los_Angeles',
		'REFRESH-INTERVAL;VALUE=DURATION:PT1H',
		'X-PUBLISHED-TTL:PT1H',
	);

	foreach ( $data['records'] as $row ) {
		$id = sanitize_key( (string) ( $row['id'] ?? '' ) );
		$date = preg_replace( '/[^0-9]/', '', (string) ( $row['date'] ?? '' ) );
		$identifier = trim( (string) ( $row['identifier'] ?? '' ) );
		$label = trim( (string) ( $row['label'] ?? '' ) );
		$source = esc_url_raw( (string) ( $row['source'] ?? '' ) );
		$brief_url = esc_url_raw( (string) ( $row['brief_url'] ?? '' ) );
		if ( ! $id || 8 !== strlen( $date ) || ! $identifier || ! $label || ! $source ) {
			continue;
		}

		$lines[] = 'BEGIN:VEVENT';
		$lines[] = 'UID:' . wwdf_ical_escape( $id ) . '@workforcewonkery.com';
		$lines[] = 'DTSTAMP:' . $stamp;

		$is_timed = isset( $row['all_day'] ) && false === $row['all_day'] && ! empty( $row['time'] );
		if ( $is_timed ) {
			$hhmm = preg_replace( '/[^0-9]/', '', (string) $row['time'] );
			$hhmm = substr( $hhmm, 0, 4 );
			if ( 4 === strlen( $hhmm ) ) {
				$timezone = ! empty( $row['timezone'] ) ? preg_replace( '/[^A-Za-z0-9_+\/-]/', '', (string) $row['timezone'] ) : 'America/Los_Angeles';
				$lines[] = 'DTSTART;TZID=' . $timezone . ':' . $date . 'T' . $hhmm . '00';
				$lines[] = 'DURATION:PT15M';
			}
		} else {
			$lines[] = 'DTSTART;VALUE=DATE:' . $date;
			$lines[] = 'DTEND;VALUE=DATE:' . wwdf_next_day( (string) $row['date'] );
		}

		$lines[] = 'SUMMARY:' . wwdf_ical_escape( $identifier . ' - ' . $label );
		$lines[] = 'DESCRIPTION:' . wwdf_ical_escape( 'Official source controls. ' . $source );
		if ( $brief_url ) {
			$lines[] = 'URL:' . wwdf_ical_escape( $brief_url );
		}
		if ( ! empty( $row['kind'] ) ) {
			$lines[] = 'CATEGORIES:' . wwdf_ical_escape( (string) $row['kind'] );
		}
		$lines[] = 'TRANSP:TRANSPARENT';
		$lines[] = 'END:VEVENT';
	}

	$lines[] = 'END:VCALENDAR';
	return implode( "\r\n", array_map( 'wwdf_fold_line', $lines ) ) . "\r\n";
}

function wwdf_maybe_render_feed() {
	if ( WWDF_FEED_PATH !== untrailingslashit( wwdf_request_path() ) ) {
		return;
	}

	$payload = wwdf_runtime_payload();
	if ( is_wp_error( $payload ) ) {
		status_header( 503 );
		header( 'Content-Type: text/plain; charset=utf-8' );
		header( 'Cache-Control: no-store' );
		echo esc_html( $payload->get_error_message() );
		exit;
	}

	$calendar = wwdf_build_calendar( $payload );
	$etag = '"ww-deadlines-' . hash( 'sha256', $payload['raw'] ) . '"';
	$if_none_match = isset( $_SERVER['HTTP_IF_NONE_MATCH'] ) ? trim( wp_unslash( $_SERVER['HTTP_IF_NONE_MATCH'] ) ) : '';

	if ( $if_none_match && hash_equals( $etag, $if_none_match ) ) {
		status_header( 304 );
		header( 'ETag: ' . $etag );
		exit;
	}

	status_header( 200 );
	header( 'Content-Type: text/calendar; charset=utf-8' );
	header( 'Content-Disposition: inline; filename="workforce-wonkery-deadlines.ics"' );
	header( 'Cache-Control: public, max-age=900, stale-while-revalidate=3600' );
	header( 'ETag: ' . $etag );
	header( 'Last-Modified: ' . mysql2date( 'D, d M Y H:i:s', $payload['page']->post_modified_gmt, false ) . ' GMT' );
	header( 'X-Content-Type-Options: nosniff' );
	echo $calendar; // phpcs:ignore WordPress.Security.EscapeOutput.OutputNotEscaped -- RFC 5545 output, not HTML.
	exit;
}
add_action( 'template_redirect', 'wwdf_maybe_render_feed', 0 );
