from fastapi import APIRouter, Request, Form, Depends, HTTPException
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from ..modelos.modelos_base import SessionLocal
from ..modelos.usuario import Usuario
from ..config import settings
import jwt
from datetime import datetime, timedelta

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

def crear_token(usuario_id: int):
    payload = {
        "sub": usuario_id,
        "exp": datetime.utcnow() + timedelta(hours=12)
    }
    token = jwt.encode(payload, settings.JWT_SECRET, algorithm="HS256")
    return token

def verificar_token(token: str):
    try:
        data = jwt.decode(token, settings.JWT_SECRET, algorithms=["HS256"])
        return data.get("sub")
    except Exception:
        return None

@router.get("/registro", response_class=HTMLResponse)
def registro_get(request: Request):
    return templates.TemplateResponse("registro.html", {"request": request})

@router.post("/registro")
def registro_post(request: Request, nombre: str = Form(...), email: str = Form(...), password: str = Form(...)):
    db = SessionLocal()
    try:
        if db.query(Usuario).filter(Usuario.email == email).first():
            return templates.TemplateResponse("registro.html", {"request": request, "error": "Correo ya registrado"})
        u = Usuario(nombre=nombre, email=email)
        u.set_password(password)
        db.add(u)
        db.commit()
        # crear token y cookie
        token = crear_token(u.id)
        response = RedirectResponse(url="/vuelos", status_code=302)
        response.set_cookie("access_token", token, httponly=True)
        return response
    finally:
        db.close()

@router.get("/login", response_class=HTMLResponse)
def login_get(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@router.post("/login")
def login_post(request: Request, email: str = Form(...), password: str = Form(...)):
    db = SessionLocal()
    try:
        u = db.query(Usuario).filter(Usuario.email == email).first()
        if not u or not u.check_password(password):
            return templates.TemplateResponse("login.html", {"request": request, "error": "Credenciales inválidas"})
        token = crear_token(u.id)
        response = RedirectResponse(url="/vuelos", status_code=302)
        response.set_cookie("access_token", token, httponly=True)
        return response
    finally:
        db.close()

@router.get("/logout")
def logout():
    response = RedirectResponse(url="/vuelos", status_code=302)
    response.delete_cookie("access_token")
    return response
