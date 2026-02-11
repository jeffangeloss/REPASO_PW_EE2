# Ejercicio 2: Conversor de unidades (con historial en memoria)
# Contexto
# API que convierte valores entre unidades (temperatura, distancia, peso) y guarda un
# historial temporal en memoria.
from datetime import datetime
from typing import Literal, Optional
from uuid import uuid4
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

# Llama tu router!
router = APIRouter(
    prefix = "",
    tags = ["Ejercicio2"]
)

# Crear la entidad de conversión
# Lo que nos ayudará a determinar de qué temperatura a qué temperatura
# Además del valor que deseo convertir
class ConvertRequest(BaseModel): # Backend asigna id
    category: Literal["temperature","distance","weight"] # Esto ya limita mis categorias
    from_unit: str
    to_unit: str
    value: float

class Conversion(BaseModel):
    id: str
    category: str
    from_unit: str
    to_unit: str
    value: float
    result: float
    formula: str
    timestamp: str

history_conversion : list[Conversion] = []

def time_now():
    return datetime.utcnow().isoformat()

# 1. POST /convert
# - Devuelve { "result": float, "formula": str }.
@router.post("/convert") # req actúa como payload - esto trae a LOS ATRIBUTOS DE LA ENTIDAD
async def convert(req: ConvertRequest):
    # Creado dentro para no gastar memoria haciendolo si al final se desecha
    req_id = str(uuid4())
    # Inicializar resp y formula porque estos cambian dependiendo del if
    id = req_id
    resp = None
    formula = None
    
    if req.category == "temperature":
        # Conversiones de temperature
        # Pasar de F a C
        if req.from_unit == "F" and req.to_unit == "C":
            resp = (req.value - 32) * (5/9)
            formula = "(valor - 32) * (5/9)"
        # Pasar de C a F
        elif req.from_unit == "C" and req.to_unit == "F":
            resp = (req.value * (9/5)) + 32
            formula = "valor * (9/5) + 32"
        else:
            raise HTTPException(
                status_code = 400,
                detail = {
                    "msg" : "Unidades de temperatura inválidas."
                }
            )
            
    elif req.category == "distance":
        # Conversiones de distance
        # Pasar de M a KN
        if req.from_unit == "M" and req.to_unit == "KM":
            resp = req.value / 1000
            formula = "valor / 1000"
        # Pasar de KM a M
        elif req.from_unit == "KM" and req.to_unit == "M":
            resp = req.value * 1000
            formula = "valor * 1000"
        else:
            raise HTTPException(
                status_code = 400,
                detail = {
                    "msg" : "Unidades de distancia inválidas."
                }
            )
            
    elif req.category == "weight":
        # Conversiones de weight
        # Pasar de G a KG
        if req.from_unit == "G" and req.to_unit == "KG":
            resp = req.value / 1000
            formula = "valor / 1000"
        # Pasar de KG a G
        elif req.from_unit == "KG" and req.to_unit == "G":
            resp = req.value * 1000
            formula = "valor * 1000"
        else:
            raise HTTPException(
                status_code = 400,
                detail = {
                    "msg" : "Unidades de peso inválidas."
                }
            )
    # Si todo ha salido bien se crea la conversión
    conversion = Conversion(
        id = id,
        category = req.category,
        from_unit = req.from_unit,
        to_unit = req.to_unit,
        value = req.value,
        result = resp,
        formula = formula,
        timestamp = time_now()
    )
    
    # Se añade al historial de conversiones
    # append a la lista de historial de conversiones
    history_conversion.append(conversion)
    
    return{
        "result" : resp,
        "formula" : formula
    }

## Listar todas mis conversiones
@router.get("/history_conversion_all")
async def getAllHistoryConversion():
    return{
        "msg" : "",
        "data" : history_conversion
    }

# 2. GET /history/{category}
# - Path param: category
# - Devuelve conversiones previas de esa categoría.
@router.get("/history/{category}") # por path param
async def filtrarHistorialCategory(category: str):
    historial_filtrado: list[Conversion] = []
    for conversion in history_conversion:
        if conversion.category != category:
            continue
        historial_filtrado.append(conversion)
    
    return{
        "msg" : "",
        "data" : historial_filtrado
    }
    
# 3. GET /history
# - Query params:
# - category: str | null
# - min_value: float | null
# - Filtra historial.
@router.get("/history")
async def getFiltroHistory(
    category: Optional[str] = Query(default = None),
    min_value: Optional[float] = Query(default = None)
):
    filtrado_x_categoria: list[Conversion] = []
    for conversion in history_conversion:
        if category is not None and conversion.category != category:
            continue
        if min_value is not None and conversion.value < min_value:
            continue
        filtrado_x_categoria.append(conversion)

    return {
        "msg": "",
        "data" : filtrado_x_categoria
    }