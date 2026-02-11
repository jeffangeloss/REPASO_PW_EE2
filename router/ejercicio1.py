# Ejercicio 1: Gestor de tareas (To-Do) en memoria
# Una mini API para gestionar tareas de una lista (sin persistencia).

# Endpoints requeridos
# 1. POST /tasks
# 2. GET /tasks/{task_id}
# 3. GET /tasks
# 4. PATCH /tasks/{tasks_id}/complete
from typing import Optional
from uuid import uuid4
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

# Llama tu router!
router = APIRouter(
    prefix = "",
    tags = ["Ejercicio1"]
)

# 1. POST → "/tasks"
# - Body (JSON): { "title": str, "description": str | null,
# "priority": int (1-5) }
# - Crea una tarea con id autogenerado y completed=false.

# Creamos la clase Tasks
class Task(BaseModel): # Esto es lo que el backend asigna a cada task ingresado
    # OJO: En las clases van saltos de línea
    id: str
    title: str
    description: Optional[str] = None
    priority: int = Field(...,ge = 1, le = 5)
    complete: bool = False

class TasksCreate(BaseModel): # Esto es para cliente, es decir es solo lo que va a editar. No tiene id ni complete porque el backend lo asigna!
    title: str
    description: Optional[str] = None
    priority: int = Field(...,ge = 1, le = 5)

# Para guardar mis tasks
# tasks_repertory: dict[str,Task] = {}
# OJO: Para agilizar las pruebas vamos a precargar unos datos
tasks_repertory : dict[str,Task] = {
    "60799464-972d-419b-857e-379664f33b91": Task(
        id="60799464-972d-419b-857e-379664f33b91",
        title="Optimizar consultas SQL",
        description="Agregar índices a la tabla de usuarios para mejorar el tiempo de respuesta.",
        priority=5,
        complete=False
    ),
    "a1b2c3d4-e5f6-4a5b-bc6d-7e8f9a0b1c2d": Task(
        id="a1b2c3d4-e5f6-4a5b-bc6d-7e8f9a0b1c2d",
        title="Corregir estilos CSS",
        description="Ajustar el padding del contenedor principal en dispositivos móviles.",
        priority=2,
        complete=True
    ),
    "f1234567-89ab-cdef-0123-456789abcdef": Task(
        id="f1234567-89ab-cdef-0123-456789abcdef",
        title="Reunión técnica",
        description="Definir la arquitectura de microservicios para el nuevo módulo.",
        priority=4,
        complete=False
    ),
    "99887766-5544-3322-1100-aabbccddeeff": Task(
        id="99887766-5544-3322-1100-aabbccddeeff",
        title="Actualizar README",
        description="Incluir instrucciones sobre cómo configurar las variables de entorno.",
        priority=1,
        complete=True
    ),
    "550e8400-e29b-41d4-a716-446655440000": Task(
        id="550e8400-e29b-41d4-a716-446655440000",
        title="Pruebas de integración",
        description="Ejecutar suite de tests en el entorno de staging.",
        priority=3,
        complete=False
    )
}

@router.post("/tasks")
async def createTasks(payload: TasksCreate):
    task_id = str(uuid4()) # Creación del id
    
    task = Task(
        id = task_id, # lo de arriba pues hijito xd
        title = payload.title, # Traemos todos estos por el payload
        description = payload.description,
        priority = payload.priority,
        complete = False
    )
    
    tasks_repertory[task_id] = task # Ahora los meto dentro del diccionario
    return {
        "msg" : "task created",
        "data" : task # Esto se usará siempre, cuando se llama este te mostrará toda la info del Task correspondiente!
    }
    
# 2. GET /tasks/{task_id}
# - Path param: task_id
# - Devuelve la tarea o 404.
@router.get("/tasks/{task_id}") # por path param
async def getTask(task_id: str):
    task = tasks_repertory.get(task_id) # buscaremos si está el id en todo nuestro repertorio
    
    #   Si no está
    if not task:
        raise HTTPException(
            status_code = 404,
            detail = "Task not found in this repository"
        )
    
    # Si lo encuentra    
    return {
        "msg" : "",
        "data" : task
    }
# Tenemos algo con qué buscar y determinar según un id, pero nos vendría bien tener una lista de todos los tasks que tenemos!

@router.get("/tasks_all")
async def getAllTasksAll():
    return {
        "msg": "",
        "data": list(tasks_repertory.values())
    }

# 3. GET /tasks
# - Query params:
# - completed: bool | null
# - min_priority: int | null
# - Filtra tareas según parámetros.

# Retos extra
# - Validar que priority esté entre 1 y 5.
# - Soportar paginación simple: skip y limit (query params).
    # QUÉ SERÁ ESO? 

# Ahora queremos hacer un filtrado según parámetros, los parámetros son si está completado y según una minima prioridad
@router.get("/tasks")
async def getListTaskFiltrado(
    # complete debe ser bool o null, es decir puede ser True/False o ser opcional
    complete: Optional[bool] = Query(default = None), # Si no se ingresa nada referente a esto se asume que es None por defecto
    # El cliente solo puede elegir dentro de las prioridades que ya están establecidas, es decir [1,5] 
    # - Validar que priority esté entre 1 y 5. OK
    min_priority: Optional[int] = Query(default = None, ge = 1, le = 5),
    skip: Optional[int] = Query(default = 0, ge = 0),
    limit: Optional[int] = Query(default = 10)
):
    filtered: list[Task] = [] # Se crea una lista de objetos Tasks y la inicializo vacía
    for task in tasks_repertory.values():
        if complete is not None and task.complete != complete: # Se filtran las que son completadas
            continue
        if min_priority is not None and task.priority < min_priority:
            continue
        filtered.append(task) # append a la lista

    start = skip
    end = start + limit
    
    lista_parcial = filtered[start:end]
    total = len(lista_parcial)
    
    return {
        "msg": "",
        "meta": {
            "total" : total,
            "skip" : skip,
            "limit" : limit
        },
        "data" : lista_parcial
        # "data": filtered
    }

# 4. PATCH /tasks/{task_id}/complete
# - Path param: task_id
# - Marca la tarea como completada.
@router.patch("/tasks/{task_id}/complete")
async def TaskComplete(task_id: str):
    task = tasks_repertory.get(task_id)

    if not task:
        raise HTTPException(
            status_code=404,
            detail="Task not found in this repository"
        )

    task.complete = True # Manipula directamente
    tasks_repertory[task_id] = task # Actualiza la task en el repertorio

    return {
        "msg": "task completed",
        "data": task
    }
