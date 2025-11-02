from fastapi import APIRouter, Request, Form
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from pathlib import Path

templates_path = Path(__file__).parent.parent / "templates"
templates = Jinja2Templates(directory=str(templates_path))

router = APIRouter()

def crear_token(usuario_id: int):
    from app.config import settings
    import jwt
    from datetime import datetime, timedelta
    
    payload = {
        "sub": usuario_id,
        "exp": datetime.utcnow() + timedelta(hours=12)
    }
    return jwt.encode(payload, settings.JWT_SECRET, algorithm="HS256")

def verificar_token(token: str):
    try:
        from app.config import settings
        import jwt
        data = jwt.decode(token, settings.JWT_SECRET, algorithms=["HS256"])
        return data.get("sub")
    except:
        return None

@router.get("/registro", response_class=HTMLResponse)
async def registro_get(request: Request):
    return templates.TemplateResponse("registro.html", {"request": request, "usuario": None})

@router.post("/registro")
async def registro_post(
    request: Request,
    nombre: str = Form(...),
    email: str = Form(...),
    password: str = Form(...)
):
    from app.modelos.modelos_base import SessionLocal
    from app.modelos.usuario import Usuario
    
    db = SessionLocal()
    try:
        existe = db.query(Usuario).filter(Usuario.email == email).first()
        if existe:
            return templates.TemplateResponse(
                "registro.html",
                {"request": request, "error": "El correo ya está registrado", "usuario": None}
            )
        
        usuario = Usuario(nombre=nombre, email=email, telefono="")
        usuario.set_password(password)
        db.add(usuario)
        db.commit()
        db.refresh(usuario)
        
        token = crear_token(usuario.id)
        response = RedirectResponse(url="/vuelos", status_code=302)
        response.set_cookie("access_token", token, httponly=True)
        return response
        
    except Exception as e:
        print(f"Error en registro: {e}")
        return templates.TemplateResponse(
            "registro.html",
            {"request": request, "error": f"Error al registrar: {str(e)}", "usuario": None}
        )
    finally:
        db.close()

@router.get("/login", response_class=HTMLResponse)
async def login_get(request: Request):
    return templates.TemplateResponse("login.html", {"request": request, "usuario": None})

@router.post("/login")
async def login_post(
    request: Request,
    email: str = Form(...),
    password: str = Form(...)
):
    from app.modelos.modelos_base import SessionLocal
    from app.modelos.usuario import Usuario
    
    db = SessionLocal()
    try:
        usuario = db.query(Usuario).filter(Usuario.email == email).first()
        
        if not usuario or not usuario.check_password(password):
            return templates.TemplateResponse(
                "login.html",
                {"request": request, "error": "Credenciales inválidas", "usuario": None}
            )
        
        token = crear_token(usuario.id)
        response = RedirectResponse(url="/vuelos", status_code=302)
        response.set_cookie("access_token", token, httponly=True)
        return response
        
    except Exception as e:
        print(f"Error en login: {e}")
        return templates.TemplateResponse(
            "login.html",
            {"request": request, "error": f"Error al iniciar sesión: {str(e)}", "usuario": None}
        )
    finally:
        db.close()

@router.get("/logout")
async def logout():
    response = RedirectResponse(url="/vuelos", status_code=302)
    response.delete_cookie("access_token")
    return response