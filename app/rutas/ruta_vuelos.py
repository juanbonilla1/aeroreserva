from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from pathlib import Path

templates_path = Path(__file__).parent.parent / "templates"
templates = Jinja2Templates(directory=str(templates_path))

router = APIRouter(prefix="/vuelos")

def obtener_usuario_actual(request: Request):
    """Obtiene el usuario actual desde el token"""
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

def es_admin(request: Request):
    """Verifica si el usuario es administrador"""
    usuario = obtener_usuario_actual(request)
    return usuario and usuario.es_admin

@router.get("/", response_class=HTMLResponse)
async def listar_vuelos(request: Request):
    from app.modelos.modelos_base import SessionLocal
    from app.modelos.vuelo import Vuelo
    
    db = SessionLocal()
    try:
        vuelos = db.query(Vuelo).filter(Vuelo.activo == True).all()
        usuario = obtener_usuario_actual(request)
        
        return templates.TemplateResponse(
            "vuelos.html",
            {
                "request": request,
                "vuelos": vuelos,
                "usuario": usuario
            }
        )
    finally:
        db.close()

@router.get("/crear", response_class=HTMLResponse)
async def crear_vuelo_get(request: Request):
    # Solo admins pueden crear vuelos
    if not es_admin(request):
        return RedirectResponse(url="/vuelos", status_code=302)
    
    usuario = obtener_usuario_actual(request)
    return templates.TemplateResponse(
        "crear_vuelo.html",
        {
            "request": request,
            "usuario": usuario
        }
    )

@router.post("/crear")
async def crear_vuelo_post(
    request: Request,
    origen: str = Form(...),
    destino: str = Form(...),
    aerolinea: str = Form("AeroReserva"),
    precio: int = Form(...),
    duracion: str = Form("1h 30m"),
    asientos: int = Form(100)
):
    # Solo admins pueden crear vuelos
    if not es_admin(request):
        return RedirectResponse(url="/vuelos", status_code=302)
    
    from app.modelos.modelos_base import SessionLocal
    from app.modelos.vuelo import Vuelo
    
    db = SessionLocal()
    try:
        vuelo = Vuelo(
            origen=origen,
            destino=destino,
            aerolinea=aerolinea,
            precio=precio,
            duracion=duracion,
            asientos_disponibles=asientos,
            activo=True
        )
        db.add(vuelo)
        db.commit()
        return RedirectResponse(url="/admin", status_code=302)
    finally:
        db.close()

@router.post("/eliminar")
async def eliminar_vuelo(request: Request, id: int = Form(...)):
    # Solo admins pueden eliminar vuelos
    if not es_admin(request):
        return RedirectResponse(url="/vuelos", status_code=302)
    
    from app.modelos.modelos_base import SessionLocal
    from app.modelos.vuelo import Vuelo
    
    db = SessionLocal()
    try:
        vuelo = db.query(Vuelo).filter(Vuelo.id == id).first()
        if vuelo:
            db.delete(vuelo)
            db.commit()
        return RedirectResponse(url="/admin", status_code=302)
    finally:
        db.close()