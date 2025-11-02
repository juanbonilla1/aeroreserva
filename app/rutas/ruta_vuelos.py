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
        usuario = db.query(Usuario).filter(Usuario.id == user_id).first()
        return usuario
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
        return RedirectResponse(url="/admin?success=vuelo_creado", status_code=302)
    except Exception as e:
        print(f"Error al crear vuelo: {e}")
        return RedirectResponse(url="/admin?error=error_crear", status_code=302)
    finally:
        db.close()

@router.get("/editar/{vuelo_id}", response_class=HTMLResponse)
async def editar_vuelo_get(vuelo_id: int, request: Request):
    """Mostrar formulario para editar un vuelo"""
    from app.modelos.modelos_base import SessionLocal
    from app.modelos.vuelo import Vuelo
    
    # Verificar que sea admin
    if not es_admin(request):
        return RedirectResponse(url="/vuelos", status_code=302)
    
    db = SessionLocal()
    try:
        # Obtener el vuelo
        vuelo = db.query(Vuelo).filter(Vuelo.id == vuelo_id).first()
        
        if not vuelo:
            return RedirectResponse(url="/admin?error=vuelo_no_existe", status_code=302)
        
        # Obtener usuario actual
        usuario = obtener_usuario_actual(request)
        
        # Renderizar template con TODOS los datos
        return templates.TemplateResponse(
            "editar_vuelo.html",
            {
                "request": request,
                "vuelo": vuelo,
                "usuario": usuario
            }
        )
    except Exception as e:
        print(f"Error al cargar formulario de edición: {e}")
        import traceback
        traceback.print_exc()
        return RedirectResponse(url="/admin?error=error_cargar", status_code=302)
    finally:
        db.close()

@router.post("/editar/{vuelo_id}")
async def editar_vuelo_post(
    vuelo_id: int,
    request: Request,
    origen: str = Form(...),
    destino: str = Form(...),
    aerolinea: str = Form(...),
    precio: int = Form(...),
    duracion: str = Form(...),
    asientos: int = Form(...)
):
    """Procesar la edición de un vuelo"""
    if not es_admin(request):
        return RedirectResponse(url="/vuelos", status_code=302)
    
    from app.modelos.modelos_base import SessionLocal
    from app.modelos.vuelo import Vuelo
    
    db = SessionLocal()
    try:
        vuelo = db.query(Vuelo).filter(Vuelo.id == vuelo_id).first()
        
        if not vuelo:
            return RedirectResponse(url="/admin?error=vuelo_no_existe", status_code=302)
        
        # Actualizar campos
        vuelo.origen = origen
        vuelo.destino = destino
        vuelo.aerolinea = aerolinea
        vuelo.precio = precio
        vuelo.duracion = duracion
        vuelo.asientos_disponibles = asientos
        
        db.commit()
        return RedirectResponse(url="/admin?success=vuelo_actualizado", status_code=302)
    except Exception as e:
        print(f"Error al editar vuelo: {e}")
        db.rollback()
        return RedirectResponse(url="/admin?error=error_editar", status_code=302)
    finally:
        db.close()

@router.post("/eliminar/{vuelo_id}")
async def eliminar_vuelo(vuelo_id: int, request: Request):
    """Eliminar un vuelo permanentemente"""
    if not es_admin(request):
        return RedirectResponse(url="/vuelos", status_code=302)
    
    from app.modelos.modelos_base import SessionLocal
    from app.modelos.vuelo import Vuelo
    
    db = SessionLocal()
    try:
        vuelo = db.query(Vuelo).filter(Vuelo.id == vuelo_id).first()
        if vuelo:
            db.delete(vuelo)
            db.commit()
            return RedirectResponse(url="/admin?success=vuelo_eliminado", status_code=302)
        else:
            return RedirectResponse(url="/admin?error=vuelo_no_existe", status_code=302)
    except Exception as e:
        print(f"Error al eliminar vuelo: {e}")
        db.rollback()
        return RedirectResponse(url="/admin?error=error_eliminar", status_code=302)
    finally:
        db.close()

@router.post("/activar/{vuelo_id}")
async def activar_vuelo(vuelo_id: int, request: Request):
    """Activar o desactivar un vuelo sin eliminarlo"""
    if not es_admin(request):
        return RedirectResponse(url="/vuelos", status_code=302)
    
    from app.modelos.modelos_base import SessionLocal
    from app.modelos.vuelo import Vuelo
    
    db = SessionLocal()
    try:
        vuelo = db.query(Vuelo).filter(Vuelo.id == vuelo_id).first()
        if vuelo:
            vuelo.activo = not vuelo.activo  # Alternar estado
            db.commit()
            return RedirectResponse(url="/admin?success=estado_cambiado", status_code=302)
        else:
            return RedirectResponse(url="/admin?error=vuelo_no_existe", status_code=302)
    except Exception as e:
        print(f"Error al cambiar estado: {e}")
        db.rollback()
        return RedirectResponse(url="/admin?error=error_estado", status_code=302)
    finally:
        db.close()