from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from ..modelos.modelos_base import SessionLocal
from ..modelos.vuelo import Vuelo
from ..modelos.usuario import Usuario
from ..config import settings

router = APIRouter(prefix="/admin")
templates = Jinja2Templates(directory="app/templates")

def es_admin(request: Request):
    token = request.cookies.get("access_token")
    if not token:
        return False
    from .ruta_auth import verificar_token
    user_id = verificar_token(token)
    if not user_id:
        return False
    db = SessionLocal()
    try:
        u = db.query(Usuario).get(user_id)
        return u and u.es_admin
    finally:
        db.close()

@router.get("/", response_class=HTMLResponse)
def admin_dashboard(request: Request):
    if not es_admin(request):
        return RedirectResponse(url="/vuelos", status_code=302)
    db = SessionLocal()
    try:
        vuelos = db.query(Vuelo).all()
        return templates.TemplateResponse("admin.html", {"request": request, "vuelos": vuelos})
    finally:
        db.close()
