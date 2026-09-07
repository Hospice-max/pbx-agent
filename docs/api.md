# HTTP API

All endpoints return JSON except the static dashboard.

## GET /api/health

Example:

```json
{"ok":true,"health":{"ami_connected":true}}
```

## GET /api/status

Complete snapshot including health, summary, extensions, endpoints and channels.

## GET /api/extensions

Array of normalized extension states.

## GET /api/pjsip

Array of normalized PJSIP endpoint states.

## GET /api/calls

Active channel records and aggregate counters.
