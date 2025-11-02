from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from pathlib import Path
import random
import string
from datetime import datetime

templates_path = Path(__file__).parent.parent / "templates"
templates = Jinja2Templates(directory=str(templates_path))

router = APIRouter(prefix="/reservas")

def obtener_usuario_actual(request: Request):
    """Obtiene el usuario actual desde el token en las cookies"""
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
        usuario = db.query(Usuario).filter(Usuario.id == user_id).first()
        return usuario
    finally:
        db.close()

@router.post("/reservar/{vuelo_id}")
async def reservar_vuelo(
    vuelo_id: int,
    request: Request,
    num_pasajeros: int = Form(1)
):
    """Crear una nueva reserva"""
    from app.modelos.modelos_base import SessionLocal
    from app.modelos.reserva import Reserva
    from app.modelos.vuelo import Vuelo
    
    usuario = obtener_usuario_actual(request)
    if not usuario:
        return RedirectResponse(url="/login", status_code=302)
    
    db = SessionLocal()
    try:
        # Verificar que el vuelo existe y tiene asientos
        vuelo = db.query(Vuelo).filter(Vuelo.id == vuelo_id).first()
        if not vuelo:
            return RedirectResponse(url="/vuelos?error=vuelo_no_existe", status_code=302)
        
        if vuelo.asientos_disponibles < num_pasajeros:
            return RedirectResponse(url="/vuelos?error=sin_asientos", status_code=302)
        
        # Generar código de reserva único
        codigo = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
        
        # Calcular precio total
        precio_total = vuelo.precio * num_pasajeros
        
        # Crear reserva
        reserva = Reserva(
            usuario_id=usuario.id,
            vuelo_id=vuelo.id,
            num_pasajeros=num_pasajeros,
            precio_total=precio_total,
            pagado=False,
            estado="Pendiente",
            codigo_reserva=codigo,
            fecha_reserva=datetime.utcnow()
        )
        
        db.add(reserva)
        
        # Reducir asientos disponibles
        vuelo.asientos_disponibles -= num_pasajeros
        
        db.commit()
        db.refresh(reserva)
        
        # Redirigir a la página de pago
        return RedirectResponse(url=f"/reservas/confirmar/{reserva.id}", status_code=302)
        
    except Exception as e:
        print(f"Error al crear reserva: {e}")
        db.rollback()
        return RedirectResponse(url="/vuelos?error=error_reserva", status_code=302)
    finally:
        db.close()

@router.get("/mis-reservas", response_class=HTMLResponse)
async def mis_reservas(request: Request):
    """Ver todas las reservas del usuario actual"""
    from app.modelos.modelos_base import SessionLocal
    from app.modelos.reserva import Reserva
    from app.modelos.vuelo import Vuelo
    
    usuario = obtener_usuario_actual(request)
    if not usuario:
        return RedirectResponse(url="/login", status_code=302)
    
    db = SessionLocal()
    try:
        # Obtener reservas del usuario con información del vuelo
        reservas = db.query(Reserva).filter(Reserva.usuario_id == usuario.id).all()
        
        # Enriquecer reservas con información del vuelo
        reservas_con_vuelo = []
        for reserva in reservas:
            vuelo = db.query(Vuelo).filter(Vuelo.id == reserva.vuelo_id).first()
            reservas_con_vuelo.append({
                'reserva': reserva,
                'vuelo': vuelo
            })
        
        return templates.TemplateResponse(
            "mis_reservas.html",
            {
                "request": request,
                "reservas": reservas_con_vuelo,
                "usuario": usuario
            }
        )
    finally:
        db.close()

@router.get("/confirmar/{reserva_id}", response_class=HTMLResponse)
async def confirmar_pago_get(reserva_id: int, request: Request):
    """Mostrar página de pago simulado"""
    from app.modelos.modelos_base import SessionLocal
    from app.modelos.reserva import Reserva
    from app.modelos.vuelo import Vuelo
    
    usuario = obtener_usuario_actual(request)
    if not usuario:
        return RedirectResponse(url="/login", status_code=302)
    
    db = SessionLocal()
    try:
        reserva = db.query(Reserva).filter(
            Reserva.id == reserva_id,
            Reserva.usuario_id == usuario.id
        ).first()
        
        if not reserva:
            return RedirectResponse(url="/reservas/mis-reservas", status_code=302)
        
        vuelo = db.query(Vuelo).filter(Vuelo.id == reserva.vuelo_id).first()
        
        return templates.TemplateResponse(
            "pago_mock.html",
            {
                "request": request,
                "reserva": reserva,
                "vuelo": vuelo,
                "usuario": usuario
            }
        )
    finally:
        db.close()

@router.post("/confirmar/{reserva_id}")
async def confirmar_pago_post(reserva_id: int, request: Request):
    """Procesar pago simulado y confirmar reserva"""
    from app.modelos.modelos_base import SessionLocal
    from app.modelos.reserva import Reserva
    
    usuario = obtener_usuario_actual(request)
    if not usuario:
        return RedirectResponse(url="/login", status_code=302)
    
    db = SessionLocal()
    try:
        reserva = db.query(Reserva).filter(
            Reserva.id == reserva_id,
            Reserva.usuario_id == usuario.id
        ).first()
        
        if not reserva:
            return RedirectResponse(url="/reservas/mis-reservas", status_code=302)
        
        # Simular pago exitoso
        reserva.pagado = True
        reserva.estado = "Confirmada"
        
        db.commit()
        
        return RedirectResponse(url="/reservas/mis-reservas?success=pago_exitoso", status_code=302)
        
    except Exception as e:
        print(f"Error al confirmar pago: {e}")
        db.rollback()
        return RedirectResponse(url="/reservas/mis-reservas?error=pago_fallido", status_code=302)
    finally:
        db.close()

@router.get("/cancelar/{reserva_id}")
async def cancelar_reserva(reserva_id: int, request: Request):
    """Cancelar una reserva"""
    from app.modelos.modelos_base import SessionLocal
    from app.modelos.reserva import Reserva
    from app.modelos.vuelo import Vuelo
    
    usuario = obtener_usuario_actual(request)
    if not usuario:
        return RedirectResponse(url="/login", status_code=302)
    
    db = SessionLocal()
    try:
        reserva = db.query(Reserva).filter(
            Reserva.id == reserva_id,
            Reserva.usuario_id == usuario.id
        ).first()
        
        if not reserva:
            return RedirectResponse(url="/reservas/mis-reservas", status_code=302)
        
        # Devolver asientos al vuelo
        vuelo = db.query(Vuelo).filter(Vuelo.id == reserva.vuelo_id).first()
        if vuelo:
            vuelo.asientos_disponibles += reserva.num_pasajeros
        
        # Marcar como cancelada
        reserva.estado = "Cancelada"
        
        db.commit()
        
        return RedirectResponse(url="/reservas/mis-reservas?success=reserva_cancelada", status_code=302)
        
    except Exception as e:
        print(f"Error al cancelar reserva: {e}")
        db.rollback()
        return RedirectResponse(url="/reservas/mis-reservas?error=cancelacion_fallida", status_code=302)
    finally:
        db.close()