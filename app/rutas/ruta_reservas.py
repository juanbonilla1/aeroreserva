from fastapi import APIRouter, Request, Form, Depends, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from ..modelos.modelos_base import SessionLocal
from ..modelos.reserva import Reserva
from ..modelos.vuelo import Vuelo
from ..modelos.usuario import Usuario
from ..rutas.ruta_auth import verificar_token
import random, string
from datetime import datetime

router = APIRouter(prefix="/reservas")
templates = Jinja2Templates(directory="app/templates")

def obtener_usuario_actual(request: Request):
    token = request.cookies.get("access_token")
    if not token:
        return None
    user_id = verificar_token(token)
    if not user_id:
        return None
    db = SessionLocal()
    try:
        u = db.query(Usuario).get(user_id)
        return u
    finally:
        db.close()

@router.post("/reservar/{vuelo_id}")
def reservar(vuelo_id: int, num_pasajeros: int = Form(1), request: Request = None):
    user = obtener_usuario_actual(request)
    if not user:
        return RedirectResponse(url="/login", status_code=302)
    db = SessionLocal()
    try:
        vuelo = db.query(Vuelo).get(vuelo_id)
        if not vuelo or vuelo.asientos_disponibles < num_pasajeros:
            return RedirectResponse(url="/vuelos", status_code=302)
        # Simular creación de reserva y pago (mock)
        codigo = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
        precio_total = vuelo.precio * num_pasajeros
        reserva = Reserva(usuario_id=user.id, vuelo_id=vuelo.id, num_pasajeros=num_pasajeros, precio_total=precio_total, pagado=False, codigo_reserva=codigo, fecha_reserva=datetime.utcnow())
        db.add(reserva)
        vuelo.asientos_disponibles -= num_pasajeros
        db.commit()
        # Redirigir a pantalla de "pago" mock
        return RedirectResponse(url=f"/reservas/confirmar/{reserva.id}", status_code=302)
    finally:
        db.close()

@router.get("/mis-reservas", response_class=HTMLResponse)
def mis_reservas(request: Request):
    user = obtener_usuario_actual(request)
    if not user:
        return RedirectResponse(url="/login", status_code=302)
    db = SessionLocal()
    try:
        reservas = db.query(Reserva).filter(Reserva.usuario_id == user.id).all()
        return templates.TemplateResponse("mis_reservas.html", {"request": request, "reservas": reservas, "usuario": user})
    finally:
        db.close()

@router.get("/confirmar/{reserva_id}", response_class=HTMLResponse)
def confirmar_pago_get(reserva_id: int, request: Request):
    # Mock page con botón "Pagar (Sandbox)"
    db = SessionLocal()
    try:
        reserva = db.query(Reserva).get(reserva_id)
        if not reserva:
            return RedirectResponse(url="/vuelos", status_code=302)
        return templates.TemplateResponse("pago_mock.html", {"request": request, "reserva": reserva})
    finally:
        db.close()

@router.post("/confirmar/{reserva_id}")
def confirmar_pago_post(reserva_id: int, request: Request = None):
    # Simula pago exitoso y marca pagado=True
    db = SessionLocal()
    try:
        reserva = db.query(Reserva).get(reserva_id)
        if not reserva:
            return RedirectResponse(url="/vuelos", status_code=302)
        reserva.pagado = True
        reserva.estado = "Pagada"
        db.commit()
        return RedirectResponse(url="/reservas/mis-reservas", status_code=302)
    finally:
        db.close()
