# app/routes/auth.py — Guest and staff login/logout routes
from pathlib import Path

from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlmodel import Session

from app.auth import lookup_guest, lookup_staff
from app.database import get_session

router = APIRouter()
templates = Jinja2Templates(directory=str(Path(__file__).resolve().parent.parent.parent / "templates"))


@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    if request.session.get("guest_id"):
        return RedirectResponse(url="/guest", status_code=302)
    if request.session.get("staff_id"):
        return RedirectResponse(url="/staff", status_code=302)
    return templates.TemplateResponse(request, "auth/login.html")


@router.post("/login")
async def guest_login(
    request: Request,
    confirmation_code: str = Form(...),
    last_name: str = Form(...),
    session: Session = Depends(get_session),
):
    guest = lookup_guest(session, confirmation_code.strip(), last_name.strip())
    if guest:
        request.session["guest_id"] = guest.id
        return RedirectResponse(url="/guest", status_code=303)
    return templates.TemplateResponse(
        request, "auth/login.html",
        context={"error": "Invalid confirmation code or last name"},
    )


@router.get("/staff/login", response_class=HTMLResponse)
async def staff_login_page(request: Request):
    return templates.TemplateResponse(request, "auth/staff_login.html")


@router.post("/staff/login")
async def staff_login(
    request: Request,
    employee_id: str = Form(...),
    last_name: str = Form(...),
    session: Session = Depends(get_session),
):
    staff = lookup_staff(session, employee_id.strip(), last_name.strip())
    if staff:
        request.session["staff_id"] = staff.id
        return RedirectResponse(url="/staff", status_code=303)
    return templates.TemplateResponse(
        request, "auth/staff_login.html",
        context={"error": "Invalid employee ID or last name"},
    )


@router.post("/logout")
async def logout(request: Request):
    request.session.clear()
    return RedirectResponse(url="/login", status_code=303)
