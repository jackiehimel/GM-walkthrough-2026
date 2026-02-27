# The Grand Meridian — Assignment Requirements

## TIER 1 (Must Have)

1. **Guest login** — lookup by confirmation code + last name
2. **Guest home screen** — welcome message with guest name, quick-action tiles (Extra Towels, Room Service, Late Checkout, etc.)
3. **Submit a request** — guest selects category, sets priority, writes description (required when "Other" is selected)
4. **View own requests** — list of guest's requests with status, category, priority, and time

## TIER 2 (Should Have)

1. **Staff login** — lookup by employee ID + last name (same pattern as guest login)
2. **Staff dashboard** — queue of all requests with status and priority badges
3. **Request detail page** — full request info with activity timeline
4. **Status updates** — staff moves requests through: new → assigned → in progress → completed

## TIER 3 (Stretch — only after Tier 1 + 2 are solid)

- Real-time updates without page reloads (HTMX polling or SSE)
- AI chat — integrate LLM for guest support
- Filters & search on staff dashboard

## Constraints

- Runnable locally with single setup command: `make setup && make dev`
- Seed data: 3 demo guests with pre-populated service requests
- Functionality matters more than polish
- Don't over-engineer auth — simple DB lookup is fine

## Build Order (live session)

1. ~~Guest login POST handler~~ *(already implemented in scaffold)*
2. Guest home screen
3. Submit request form + handler
4. Guest request list
5. ~~Staff login~~ *(already implemented in scaffold)* + staff dashboard
6. Request detail + timeline
7. Status update handler
8. Stretch goals (remaining time)

---

## Behavior & Success Criteria

Each feature lists acceptance criteria and a concrete smoke test to run in the browser before moving on.

### 1. Guest login *(implemented in scaffold)*

- **Accept when:**
  - POST `/login` with valid confirmation_code + last_name (case-insensitive) → 303 redirect to `/guest`
  - Invalid credentials → re-render login page with visible error message, no redirect
  - Session persists: after login, navigating to `/guest/requests` works without re-login
  - Unauthenticated GET `/guest` → 303 redirect to `/login`
- **Smoke test:**
  1. `make dev` → open [http://localhost:8000/login](http://localhost:8000/login)
  2. Enter `GM-2026-001` / `Parker` → confirm redirect to `/guest`, page shows "Emily"
  3. Enter `GM-2026-001` / `WrongName` → confirm error message on login page
  4. After successful login, navigate directly to `/guest/requests` → confirm page loads (session intact)
  5. Open incognito tab, go to `/guest` → confirm redirect to `/login`
  6. Run `make test` → all login tests pass

### 2. Guest home screen

- **Accept when:**
  - Welcome message includes guest's first name (e.g., "Welcome, Emily")
  - Quick-action tiles displayed: Extra Towels, Room Service, Late Checkout (minimum 3 tiles)
  - Each tile links to `/guest/requests/new` with category/type pre-filled
  - Page renders correctly at 375px viewport width (no horizontal scroll, tiles stack)
- **Smoke test:**
  1. Log in as `GM-2026-001` / `Parker` → confirm "Emily" in welcome text
  2. Log in as `GM-2026-002` / `Kim` → confirm "David" in welcome text
  3. Click "Extra Towels" tile → confirm navigates to submit form with category pre-selected
  4. Chrome DevTools → toggle device toolbar to 375px width → confirm layout is usable
  5. Run `make test` → all home screen tests pass

### 3. Submit a request

- **Accept when:**
  - Form shows: category (dropdown), priority (low/medium/high), description (textarea)
  - Submitting with valid data → creates ServiceRequest in DB → 303 redirect to `/guest/requests`
  - New request visible at top of request list with correct category, priority, status="new"
  - When category is "Other", description is required — form rejects empty description
  - Pre-filled category from quick-action tile is selected in dropdown on page load
- **Smoke test:**
  1. Log in as Emily → click "Room Service" tile → confirm category pre-selected as "dining"
  2. Set priority to "high", enter description "Breakfast for two" → submit
  3. Confirm redirect to `/guest/requests` with new request showing: dining, high, new
  4. Navigate to `/guest/requests/new` → select "Other" category → leave description blank → submit → confirm validation error
  5. Fill in description for "Other" → submit → confirm success
  6. Run `make test` → all submit tests pass

### 4. View own requests

- **Accept when:**
  - Page shows only the logged-in guest's requests (not other guests')
  - Each request row displays: status badge, category, priority badge, created timestamp
  - Requests ordered by most recent first
  - Empty state shown when guest has no requests (meaningful message, not blank page)
- **Smoke test:**
  1. Log in as `GM-2026-001` (Emily) → go to `/guest/requests` → confirm Emily's seeded requests appear
  2. Count requests — should match seed data count for Emily
  3. Log in as `GM-2026-003` (Lisa) → go to `/guest/requests` → confirm Lisa's requests (different from Emily's)
  4. Submit a new request as Emily → confirm it appears at top of list
  5. Verify status badge colors: new=secondary, assigned=primary, in_progress=info, completed=success
  6. Run `make test` → all request list tests pass

### 5. Staff login *(implemented in scaffold)*

- **Accept when:**
  - GET `/staff/login` renders staff login form with employee ID + last name fields
  - POST `/staff/login` with valid employee_id + last_name → 303 redirect to `/staff`
  - Invalid credentials → re-render with error message
  - Session stores staff_id; unauthenticated GET `/staff` → redirect to `/staff/login`
- **Smoke test:**
  1. Open `/staff/login` → confirm form with employee ID and last name fields
  2. Enter `EMP-2026-002` / `Wilson` → confirm redirect to `/staff` dashboard
  3. Enter `EMP-2026-002` / `Wrong` → confirm error message
  4. Run `make test` → all staff login tests pass

### 6. Staff dashboard

- **Accept when:**
  - Shows ALL requests across ALL guests (not scoped to one guest)
  - Each row: guest name, category, priority badge, status badge, created time
  - Rows are clickable — link to `/staff/requests/{id}` detail page
  - Requests ordered by newest first (or by priority — either is acceptable)
- **Smoke test:**
  1. Log in as staff `EMP-2026-002` / `Wilson` → confirm dashboard shows requests from Emily, David, and Lisa
  2. Verify status badges use correct Bootstrap classes (new=secondary, assigned=primary, etc.)
  3. Verify priority badges: low=secondary, medium=warning, high=danger
  4. Click a request row → confirm navigation to detail page
  5. Run `make test` → all dashboard tests pass

### 7. Request detail page

- **Accept when:**
  - Shows full request info: guest name, room number, category, priority, status, description, created_at
  - Activity timeline lists all status changes with: action, staff name, timestamp
  - Timeline entries ordered chronologically (oldest first)
  - Status update controls visible to staff (dropdown or buttons for valid next status)
- **Smoke test:**
  1. From staff dashboard, click a seeded request → confirm all fields displayed
  2. Verify seeded activity entries appear in timeline with timestamps
  3. Confirm status update form/buttons are present on page
  4. Run `make test` → all detail page tests pass

### 8. Status updates

- **Accept when:**
  - Staff can advance: new → assigned → in_progress → completed (one step at a time)
  - Each transition creates a RequestActivity record (action, staff name, timestamp)
  - Invalid transitions rejected (e.g., new → completed) with error feedback
  - After update, page re-renders showing new status and new timeline entry
  - Updated status visible on staff dashboard and on guest's request list
- **Smoke test:**
  1. Open a request with status="new" → update to "assigned" → confirm timeline entry with staff name
  2. Update same request to "in_progress" → confirm second timeline entry
  3. Update to "completed" → confirm final entry, no further update options shown
  4. Try to skip a step (new → completed via direct POST) → confirm rejection
  5. Log in as the guest who owns the request → confirm updated status on `/guest/requests`
  6. Run `make test` → all status update tests pass

### 9. Stretch — Real-time updates

- **Accept when:**
  - Guest's `/guest/requests` page updates without manual reload when staff changes a status
  - No full page reload — partial update via HTMX polling or SSE
  - Update visible within ~3 seconds of staff action
- **Smoke test:**
  1. Open two browser windows: guest view (`/guest/requests`) and staff view
  2. As staff, update a request status
  3. Watch guest window — confirm status badge updates without page reload within ~3s

### 10. Stretch — AI chat

- **Accept when:**
  - Guest can access chat interface from guest home or nav
  - Guest sends a message → LLM responds in hotel/concierge context
  - When API key not set → graceful fallback message (not a crash)
- **Smoke test:**
  1. Log in as guest → navigate to chat
  2. Send "What restaurants are nearby?" → confirm contextual response
  3. Unset OPENAI_API_KEY → restart → send message → confirm fallback message

### 11. Stretch — Filters & search

- **Accept when:**
  - Staff dashboard has filter controls: status dropdown, category dropdown
  - Text search by description or guest name
  - Filtering updates results without full page reload (HTMX preferred)
  - Clearing filters restores full list
- **Smoke test:**
  1. On staff dashboard, filter by status="new" → confirm only new requests shown
  2. Filter by category="housekeeping" → confirm filtered results
  3. Search for "Emily" → confirm only Emily's requests shown
  4. Clear all filters → confirm full list restored

