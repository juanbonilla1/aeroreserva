from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from pathlib import Path

templates_path = Path(__file__).parent.parent / "templates"
templates = Jinja2Templates(directory=str(templates_path))

router = APIRouter(prefix="/vuelos")

@router.get("/", response_class=HTMLResponse)
async def listar_vuelos(request: Request):
    from app.modelos.modelos_base import SessionLocal
    from app.modelos.vuelo import Vuelo
    
    db = SessionLocal()
    try:
        vuelos = db.query(Vuelo).filter(Vuelo.activo == True).all()
        return templates.TemplateResponse(
            "vuelos.html",
            {"request": request, "vuelos": vuelos}
        )
    finally:
        db.close()

@router.get("/crear", response_class=HTMLResponse)
async def crear_vuelo_get(request: Request):
    return templates.TemplateResponse("crear_vuelo.html", {"request": request})

@router.post("/crear")
async def crear_vuelo_post(
    origen: str = Form(...),
    destino: str = Form(...),
    aerolinea: str = Form("AeroReserva"),
    precio: int = Form(...),
    duracion: str = Form("1h 30m"),
    asientos: int = Form(100)
):
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
        return RedirectResponse(url="/vuelos", status_code=302)
    finally:
        db.close()

@router.post("/eliminar")
async def eliminar_vuelo(id: int = Form(...)):
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