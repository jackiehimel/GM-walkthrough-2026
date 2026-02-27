"""Smoke tests — verify scaffold boots and auth works."""
import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture()
def client():
    with TestClient(app) as c:
        yield c


def test_root_redirects_to_login(client):
    resp = client.get("/", follow_redirects=False)
    assert resp.status_code == 302
    assert "/login" in resp.headers["location"]


def test_login_page_renders(client):
    resp = client.get("/login")
    assert resp.status_code == 200
    assert "confirmation" in resp.text.lower()


def test_staff_login_page_renders(client):
    resp = client.get("/staff/login")
    assert resp.status_code == 200
    assert "employee" in resp.text.lower()


def test_guest_login_valid(client):
    resp = client.post(
        "/login",
        data={"confirmation_code": "GM-2026-001", "last_name": "Parker"},
        follow_redirects=False,
    )
    assert resp.status_code == 303
    assert "/guest" in resp.headers["location"]


def test_guest_login_invalid(client):
    resp = client.post(
        "/login",
        data={"confirmation_code": "GM-2026-001", "last_name": "WrongName"},
    )
    assert resp.status_code == 200
    assert "error" in resp.text.lower() or "invalid" in resp.text.lower()


def test_staff_login_valid(client):
    resp = client.post(
        "/staff/login",
        data={"employee_id": "EMP-2026-002", "last_name": "Wilson"},
        follow_redirects=False,
    )
    assert resp.status_code == 303
    assert "/staff" in resp.headers["location"]


def test_guest_routes_require_auth(client):
    resp = client.get("/guest", follow_redirects=False)
    # Should redirect to login
    assert resp.status_code == 303
    assert "/login" in resp.headers["location"]


def test_guest_home_welcome_emily(client):
    client.post("/login", data={"confirmation_code": "GM-2026-001", "last_name": "Parker"})
    resp = client.get("/guest")
    assert resp.status_code == 200
    assert "Emily" in resp.text
    assert "Welcome" in resp.text


def test_guest_home_welcome_david(client):
    client.post("/login", data={"confirmation_code": "GM-2026-002", "last_name": "Kim"})
    resp = client.get("/guest")
    assert resp.status_code == 200
    assert "David" in resp.text
    assert "Welcome" in resp.text


def test_guest_home_quick_action_tiles(client):
    client.post("/login", data={"confirmation_code": "GM-2026-001", "last_name": "Parker"})
    resp = client.get("/guest")
    assert resp.status_code == 200
    assert "Extra Towels" in resp.text
    assert "Room Service" in resp.text
    assert "Late Checkout" in resp.text


def test_guest_home_extra_towels_tile_links_correctly(client):
    client.post("/login", data={"confirmation_code": "GM-2026-001", "last_name": "Parker"})
    resp = client.get("/guest")
    assert resp.status_code == 200
    assert 'href="/guest/requests/new?category=housekeeping&request_type=Extra+towels"' in resp.text


def test_staff_routes_require_auth(client):
    resp = client.get("/staff", follow_redirects=False)
    # Should redirect to staff login
    assert resp.status_code == 303
    assert "/staff/login" in resp.headers["location"]


def test_submit_form_renders(client):
    client.post("/login", data={"confirmation_code": "GM-2026-001", "last_name": "Parker"})
    resp = client.get("/guest/requests/new")
    assert resp.status_code == 200
    assert "category" in resp.text.lower()
    assert "priority" in resp.text.lower()
    assert "description" in resp.text.lower()


def test_submit_form_category_preselected_from_tile(client):
    client.post("/login", data={"confirmation_code": "GM-2026-001", "last_name": "Parker"})
    resp = client.get("/guest/requests/new?category=dining&request_type=Room+service")
    assert resp.status_code == 200
    assert 'value="dining" selected' in resp.text or 'value="dining" selected' in resp.text.replace(" ", "")


def test_submit_request_creates_and_redirects(client):
    client.post("/login", data={"confirmation_code": "GM-2026-001", "last_name": "Parker"})
    resp = client.post(
        "/guest/requests",
        data={
            "category": "dining",
            "priority": "high",
            "request_type": "Room service",
            "description": "Breakfast for two",
        },
        follow_redirects=False,
    )
    assert resp.status_code == 303
    assert "/guest/requests" in resp.headers["location"]


def test_submit_request_appears_in_list(client):
    client.post("/login", data={"confirmation_code": "GM-2026-001", "last_name": "Parker"})
    client.post(
        "/guest/requests",
        data={
            "category": "dining",
            "priority": "high",
            "request_type": "Room service",
            "description": "Breakfast for two",
        },
    )
    resp = client.get("/guest/requests")
    assert resp.status_code == 200
    assert "dining" in resp.text.lower() or "Dining" in resp.text
    assert "high" in resp.text.lower()
    assert "new" in resp.text.lower()
    assert "Breakfast for two" in resp.text


def test_submit_other_requires_description(client):
    client.post("/login", data={"confirmation_code": "GM-2026-001", "last_name": "Parker"})
    resp = client.post(
        "/guest/requests",
        data={"category": "other", "priority": "medium", "request_type": "Other", "description": ""},
    )
    assert resp.status_code == 200
    assert "required" in resp.text.lower() or "description" in resp.text.lower()


def test_submit_other_with_description_succeeds(client):
    client.post("/login", data={"confirmation_code": "GM-2026-001", "last_name": "Parker"})
    resp = client.post(
        "/guest/requests",
        data={"category": "other", "priority": "low", "request_type": "Other", "description": "Custom request details"},
        follow_redirects=False,
    )
    assert resp.status_code == 303
    assert "/guest/requests" in resp.headers["location"]


# ---------------------------------------------------------------------------
# Feature 4 — View own requests
# ---------------------------------------------------------------------------

def test_guest_requests_shows_seeded_requests(client):
    client.post("/login", data={"confirmation_code": "GM-2026-001", "last_name": "Parker"})
    resp = client.get("/guest/requests")
    assert resp.status_code == 200
    assert "Housekeeping" in resp.text
    assert "Dining" in resp.text


def test_guest_requests_isolation(client):
    """Lisa should only see her own requests, not Emily's."""
    client.post("/login", data={"confirmation_code": "GM-2026-003", "last_name": "Chen"})
    resp = client.get("/guest/requests")
    assert resp.status_code == 200
    assert "Front Desk" in resp.text
    assert "Housekeeping" not in resp.text


def test_guest_requests_status_badges(client):
    client.post("/login", data={"confirmation_code": "GM-2026-001", "last_name": "Parker"})
    resp = client.get("/guest/requests")
    assert "bg-info" in resp.text  # in_progress
    assert "bg-success" in resp.text  # completed


def test_guest_requests_priority_badges(client):
    client.post("/login", data={"confirmation_code": "GM-2026-001", "last_name": "Parker"})
    resp = client.get("/guest/requests")
    assert "bg-warning" in resp.text  # medium priority
    assert "bg-secondary" in resp.text  # low priority


def test_guest_requests_empty_state(client):
    """A newly created request can prove the empty state path isn't hit for seeded guests, 
    but we can test that the page renders for a guest whose requests we know about."""
    client.post("/login", data={"confirmation_code": "GM-2026-003", "last_name": "Chen"})
    resp = client.get("/guest/requests")
    assert resp.status_code == 200
    assert "Late checkout" in resp.text or "Front Desk" in resp.text


def test_guest_requests_newest_first(client):
    """Submit a new request as Emily and verify it appears before the seeded ones."""
    client.post("/login", data={"confirmation_code": "GM-2026-001", "last_name": "Parker"})
    client.post(
        "/guest/requests",
        data={"category": "concierge", "priority": "high", "request_type": "Event tickets", "description": "Concert tonight"},
    )
    resp = client.get("/guest/requests")
    text = resp.text
    concierge_pos = text.find("Concert tonight")
    breakfast_pos = text.find("Breakfast for two")
    assert concierge_pos < breakfast_pos, "Newest request should appear first"


# ---------------------------------------------------------------------------
# Feature 6 — Staff dashboard
# ---------------------------------------------------------------------------

def test_staff_dashboard_renders(client):
    client.post("/staff/login", data={"employee_id": "EMP-2026-002", "last_name": "Wilson"})
    resp = client.get("/staff")
    assert resp.status_code == 200
    assert "Service Requests" in resp.text


def test_staff_dashboard_shows_all_guests(client):
    client.post("/staff/login", data={"employee_id": "EMP-2026-002", "last_name": "Wilson"})
    resp = client.get("/staff")
    assert resp.status_code == 200
    assert "Emily" in resp.text and "Parker" in resp.text
    assert "David" in resp.text and "Kim" in resp.text
    assert "Lisa" in resp.text and "Chen" in resp.text


def test_staff_dashboard_status_badges(client):
    client.post("/staff/login", data={"employee_id": "EMP-2026-002", "last_name": "Wilson"})
    resp = client.get("/staff")
    assert "bg-secondary" in resp.text  # new
    assert "bg-info" in resp.text  # in_progress
    assert "bg-success" in resp.text  # completed
    assert "bg-primary" in resp.text  # assigned


def test_staff_dashboard_priority_badges(client):
    client.post("/staff/login", data={"employee_id": "EMP-2026-002", "last_name": "Wilson"})
    resp = client.get("/staff")
    assert "bg-danger" in resp.text  # high
    assert "bg-warning" in resp.text  # medium


def test_staff_dashboard_view_links(client):
    client.post("/staff/login", data={"employee_id": "EMP-2026-002", "last_name": "Wilson"})
    resp = client.get("/staff")
    assert "/staff/requests/" in resp.text
    assert "View" in resp.text


def test_staff_dashboard_shows_categories(client):
    client.post("/staff/login", data={"employee_id": "EMP-2026-002", "last_name": "Wilson"})
    resp = client.get("/staff")
    assert "Housekeeping" in resp.text
    assert "Dining" in resp.text
    assert "Maintenance" in resp.text
    assert "Front Desk" in resp.text


# ---------------------------------------------------------------------------
# Feature 7 — Request detail page
# ---------------------------------------------------------------------------

def test_request_detail_renders(client):
    client.post("/staff/login", data={"employee_id": "EMP-2026-002", "last_name": "Wilson"})
    resp = client.get("/staff/requests/1")
    assert resp.status_code == 200
    assert "Request #1" in resp.text


def test_request_detail_shows_guest_info(client):
    client.post("/staff/login", data={"employee_id": "EMP-2026-002", "last_name": "Wilson"})
    resp = client.get("/staff/requests/1")
    assert "Emily" in resp.text and "Parker" in resp.text
    assert "12-501" in resp.text


def test_request_detail_shows_request_fields(client):
    client.post("/staff/login", data={"employee_id": "EMP-2026-002", "last_name": "Wilson"})
    resp = client.get("/staff/requests/1")
    assert "Housekeeping" in resp.text
    assert "Extra towels" in resp.text
    assert "bg-info" in resp.text or "bg-warning" in resp.text  # status or priority badge


def test_request_detail_shows_activity_timeline(client):
    client.post("/staff/login", data={"employee_id": "EMP-2026-002", "last_name": "Wilson"})
    resp = client.get("/staff/requests/1")
    assert "Activity Timeline" in resp.text


def test_request_detail_shows_status_update_form(client):
    """A request with status 'new' should show an update form with 'assigned' option."""
    client.post("/staff/login", data={"employee_id": "EMP-2026-002", "last_name": "Wilson"})
    resp = client.get("/staff/requests/3")  # David's AC issue, status=new
    assert "Update Status" in resp.text
    assert "Assigned" in resp.text


def test_request_detail_completed_has_no_update_form(client):
    """A completed request should not show status update controls."""
    client.post("/staff/login", data={"employee_id": "EMP-2026-002", "last_name": "Wilson"})
    resp = client.get("/staff/requests/2")  # Emily's dining request, status=completed
    assert "Update Status" not in resp.text


def test_request_detail_nonexistent_redirects(client):
    client.post("/staff/login", data={"employee_id": "EMP-2026-002", "last_name": "Wilson"})
    resp = client.get("/staff/requests/999", follow_redirects=False)
    assert resp.status_code == 303
    assert "/staff" in resp.headers["location"]


def test_request_detail_back_link(client):
    client.post("/staff/login", data={"employee_id": "EMP-2026-002", "last_name": "Wilson"})
    resp = client.get("/staff/requests/1")
    assert 'href="/staff"' in resp.text


# ---------------------------------------------------------------------------
# Feature 8 — Status updates
# ---------------------------------------------------------------------------

def test_status_update_new_to_assigned(client):
    """Advance request #3 (David's AC issue, status=new) to assigned."""
    client.post("/staff/login", data={"employee_id": "EMP-2026-002", "last_name": "Wilson"})
    resp = client.post(
        "/staff/requests/3/status",
        data={"status": "assigned"},
        follow_redirects=False,
    )
    assert resp.status_code == 303
    assert "/staff/requests/3" in resp.headers["location"]


def test_status_update_creates_activity(client):
    """After updating status, a timeline entry should appear on the detail page."""
    client.post("/staff/login", data={"employee_id": "EMP-2026-002", "last_name": "Wilson"})
    client.post("/staff/requests/3/status", data={"status": "assigned"})
    resp = client.get("/staff/requests/3")
    assert "assigned" in resp.text.lower()
    assert "James Wilson" in resp.text


def test_status_update_full_lifecycle(client):
    """Walk request #3 through new -> assigned -> in_progress -> completed."""
    client.post("/staff/login", data={"employee_id": "EMP-2026-002", "last_name": "Wilson"})
    client.post("/staff/requests/3/status", data={"status": "assigned"})
    client.post("/staff/requests/3/status", data={"status": "in_progress"})
    client.post("/staff/requests/3/status", data={"status": "completed"})
    resp = client.get("/staff/requests/3")
    assert "Completed" in resp.text
    assert "Update Status" not in resp.text


def test_status_update_invalid_transition_rejected(client):
    """Trying to skip new -> completed should be rejected."""
    client.post("/staff/login", data={"employee_id": "EMP-2026-002", "last_name": "Wilson"})
    resp = client.post(
        "/staff/requests/3/status",
        data={"status": "completed"},
    )
    assert resp.status_code == 200
    assert "Invalid" in resp.text or "invalid" in resp.text


def test_status_update_visible_on_dashboard(client):
    """After updating a request, the new status should appear on the dashboard."""
    client.post("/staff/login", data={"employee_id": "EMP-2026-002", "last_name": "Wilson"})
    client.post("/staff/requests/3/status", data={"status": "assigned"})
    resp = client.get("/staff")
    assert "Assigned" in resp.text


def test_status_update_visible_on_guest_requests(client):
    """After staff updates a request, the guest should see the new status."""
    staff_client = client
    staff_client.post("/staff/login", data={"employee_id": "EMP-2026-002", "last_name": "Wilson"})
    staff_client.post("/staff/requests/3/status", data={"status": "assigned"})
    staff_client.post("/logout")
    staff_client.post("/login", data={"confirmation_code": "GM-2026-002", "last_name": "Kim"})
    resp = staff_client.get("/guest/requests")
    assert "Assigned" in resp.text


def test_status_update_nonexistent_request(client):
    client.post("/staff/login", data={"employee_id": "EMP-2026-002", "last_name": "Wilson"})
    resp = client.post(
        "/staff/requests/999/status",
        data={"status": "assigned"},
        follow_redirects=False,
    )
    assert resp.status_code == 303
    assert "/staff" in resp.headers["location"]
