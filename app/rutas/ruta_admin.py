from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from pathlib import Path

templates_path = Path(__file__).parent.parent / "templates"
templates = Jinja2Templates(directory=str(templates_path))

router = APIRouter(prefix="/admin")

def obtener_usuario_actual(request: Request):
    from app.modelos.modelos_base import SessionLocal
    from app.modelos.usuario import Usuario
    from app.rutas.ruta_auth import verificar_token
    
    token = request.cookies.get("access_token")
    if not token:
        return None
    
    user_id = verificar_token(token)
    if not user_id:
        return None
    
    db = SessionLocal()
    try:
        return db.query(Usuario).filter(Usuario.id == user_id).first()
    finally:
        db.close()

@router.get("/", response_class=HTMLResponse)
def admin_dashboard(request: Request):
    from app.modelos.modelos_base import SessionLocal
    from app.modelos.vuelo import Vuelo
    from app.modelos.reserva import Reserva
    
    usuario = obtener_usuario_actual(request)
    
    # Verificar que el usuario sea admin
    if not usuario or not usuario.es_admin:
        return RedirectResponse(url="/vuelos", status_code=302)
    
    db = SessionLocal()
    try:
        vuelos = db.query(Vuelo).all()
        reservas = db.query(Reserva).all()
        
        return templates.TemplateResponse(
            "admin.html",
            {
                "request": request,
                "vuelos": vuelos,
                "reservas": reservas,
                "usuario": usuario
            }
        )
    finally:
        db.close()