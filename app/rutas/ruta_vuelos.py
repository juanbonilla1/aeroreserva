from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from ..modelos.modelos_base import SessionLocal
from ..modelos.vuelo import Vuelo

router = APIRouter(prefix="/vuelos")
templates = Jinja2Templates(directory="app/templates")

@router.get("/", response_class=HTMLResponse)
def listar_vuelos(request: Request):
    db = SessionLocal()
    try:
        vuelos = db.query(Vuelo).filter(Vuelo.activo==True).all()
        return templates.TemplateResponse("vuelos.html", {"request": request, "vuelos": vuelos})
    finally:
        db.close()

@router.get("/crear", response_class=HTMLResponse)
def crear_vuelo_get(request: Request):
    return templates.TemplateResponse("crear_vuelo.html", {"request": request})

@router.post("/crear")
def crear_vuelo_post(origen: str = Form(...), destino: str = Form(...), aerolinea: str = Form(""), precio: int = Form(...), duracion: str = Form(""), asientos: int = Form(100)):
    db = SessionLocal()
    try:
        v = Vuelo(origen=origen, destino=destino, aerolinea=aerolinea, precio=precio, duracion=duracion, asientos_disponibles=asientos)
        db.add(v)
        db.commit()
        return RedirectResponse(url="/vuelos", status_code=302)
    finally:
        db.close()

@router.post("/eliminar")
def eliminar_vuelo(id: int = Form(...)):
    db = SessionLocal()
    try:
        v = db.query(Vuelo).get(id)
        if v:
            db.delete(v)
            db.commit()
        return RedirectResponse(url="/vuelos", status_code=302)
    finally:
        db.close()
