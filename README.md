# The Grand Meridian - Guest Services

Hotel guest services app — guests submit requests, staff manages them.

## Quick Start

```bash
make setup && make dev
```

App runs at http://localhost:8000

## Demo Logins

| Role  | Credentials                    |
|-------|--------------------------------|
| Guest | GM-2026-001 / Parker (Emily)   |
| Staff | EMP-2026-002 / Wilson (James)  |

## Build Order

See `REQUIREMENTS.md` for detailed feature tiers and acceptance criteria. Auth is already implemented — start here:

1. Guest home screen
2. Submit request form + handler
3. Guest request list
4. Staff dashboard
5. Request detail + timeline
6. Status update handler
7. Stretch: real-time (HTMX + SSE), AI chat, filters
