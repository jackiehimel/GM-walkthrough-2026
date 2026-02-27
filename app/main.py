# app/main.py — Application entry point
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware

from app.auth import _RedirectException
from app.config import settings
from app.database import engine
from app.models import SQLModel
from app.routes import auth, guest, staff
from app.seed import seed

# -----------------------------------------------------------------------------
# App setup
# -----------------------------------------------------------------------------
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: create tables, apply SQLite migrations, seed data.
    _on_startup()
    yield


app = FastAPI(
    title="The Grand Meridian - Guest Services",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)


@app.exception_handler(_RedirectException)
async def redirect_exception_handler(request: Request, exc: _RedirectException):
    return RedirectResponse(url=exc.url, status_code=303)

# Session-based auth: stores guest_id or staff_id in encrypted cookie
app.add_middleware(SessionMiddleware, secret_key=settings.secret_key)

# Static assets (CSS, images) served at /static
app.mount("/static", StaticFiles(directory=str(Path(__file__).parent.parent / "static")), name="static")

# Route modules: auth, guest, staff
app.include_router(auth.router)
app.include_router(guest.router)
app.include_router(staff.router)


def _on_startup():
    # Run on startup: create tables, seed data. Fresh scaffold — no migrations.
    SQLModel.metadata.create_all(engine)
    seed()


@app.get("/")
async def root(request: Request):
    # Root redirect: logged-in users → home, others → guest login
    if request.session.get("guest_id"):
        return RedirectResponse(url="/guest", status_code=302)
    if request.session.get("staff_id"):
        return RedirectResponse(url="/staff", status_code=302)
    return RedirectResponse(url="/login", status_code=302)
