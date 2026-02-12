# Ejercicio 3: Validador de formulario de registro
# Contexto
# API que valida datos de registro (sin guardar nada), ideal para practicar validaciones.
import re
from typing import Optional
from fastapi import APIRouter, Query
from pydantic import BaseModel, EmailStr, Field

router = APIRouter(
    prefix = "",
    tags = ["Ejercicio3"]
)

class UsuarioType(BaseModel):
    # username : str = Field(..., min_length=3, max_length=20,example="usuario123")
    # email : EmailStr = Field(..., example="usuario@ejemplo.com")
    # password : str = Field(..., min_length=8, pattern=r'.*\d.*',example="MiClave123")
    # age : int = Field(..., ge=13,example=18)
    
    # Nosotros vamos a validar manualmente dentro
    username : str
    email : str
    password: str
    age : int

history_users : list[UsuarioType] = []

# 1. POST /register/validate
# - username (3–20)
# - email (formato email)
# - password (mínimo 8, al menos 1 número)
# - age (>= 13)
# - Devuelve:
# - Si válido: { "ok": true }
# - Si inválido: { "ok": false, "errors": [...] }
@router.post("/register/validate")
async def RegistrarUsuario(user : UsuarioType):
    # Esto era si validamos arriba
    # usuario = UsuarioType(
    #     username = user.username,
    #     email = user.email,
    #     password = user.password,
    #     age = user.age,
    # )
    errores = []
    
    # validamos username
    if not (3 <= len(user.username)<=20):
        errores.append("El username debe estar entre 3 y caracteres.")
    
    # validamos email
    email_regex = r"^[^@]+@[^@]+\.[^@]+$"
    if not re.match(email_regex, user.email):
        errores.append("El email no tiene formato válido")
        
    # validamos password
    if len(user.password) < 8:
        errores.append("La contraseña debe tener al menos de 8 caracteres")
    if not re.search(r'\d', user.password):
        errores.append("La contraseña debe tener al menos un número")
    
    # validamos age
    if user.age < 13:
        errores.append("La edad del usuario debe ser mayor o igual que 13 años")
    
    
    # Si hay errores (por lo menos uno) se retornan los errores, sino todo ok
    if errores:
        return {
            "ok": False,
            "errors" : errores
        }
    else:
        # Si todo está bien se coloca!
        history_users.append(user)
        return{
            "ok": True
        }

# 2. GET /users/{username}/availability
# - Path param: username
# - Simula disponibilidad comparando contra una lista en memoria.

# AH YA ENTENDI: TE PIDEN VERIFICAR QUE NO SE REPITA TU USERNAME
@router.get("/users/{username}/availability")
async def isAvailable(username: str):
    for usuario in  history_users: # Buscas un usuario en la lista de historial de usuarios
        if usuario.username == username: # si el nombre del usuario que se encuentra en la lista de historial de usuarios es igual al usuario ingresado
            return{ # vas directo al error para salir del for
                "msg" : "Usuario no disponible"
            }
            
    return{ # luego si ya recorriste todo y no encontraste nada pues se dice que el usuario si está disponible
        "msg" : " Usuario disponible"
    }

# 3. GET /password/rules
# - Query params:
# - lang: "es"|"en" (default "es")
# - Devuelve reglas de contraseña.
@router.get("/password/rules")
async def rules_pass(
    lang: Optional[str] = Query(default = "es")
):
    if lang == "es" or lang == "en":
        if lang == "es":
            return{
                "reglas" : "minimo 8 caracteres y al menos 1 número"
            }
        else:
            return{
                "rules" : "minimum 8 characters and at least 1 number"
            }
    else:
        return{
            "msg" : "Lenguaje inválido"
        }
