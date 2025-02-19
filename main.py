from fastapi import FastAPI, Request, Form, HTTPException, status
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from typing import List, Optional
from pydantic import BaseModel
from fastapi.staticfiles import StaticFiles


app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static") # Para servir archivos estáticos (CSS, JS)
templates = Jinja2Templates(directory="templates") # Configura Jinja2 para buscar plantillas en la carpeta 'templates'

# Simulación de base de datos en memoria (para simplificar el ejemplo)
tareas_db = []
tarea_id_counter = 1

class Tarea(BaseModel):
    id: int
    titulo: str
    completada: bool = False


# --- Endpoints ---

@app.get("/", response_class=HTMLResponse)
async def inicio(request: Request):
    """Endpoint para la página principal que muestra la lista de tareas."""
    return templates.TemplateResponse("index.html", {"request": request, "tareas": tareas_db})

@app.get("/tareas", response_class=HTMLResponse)
async def listar_tareas(request: Request):
    """Endpoint que devuelve solo la lista de tareas como fragmento HTML."""
    return templates.TemplateResponse("task_list.html", {"request": request, "tareas": tareas_db})

@app.post("/tareas", response_class=HTMLResponse)
async def crear_tarea(request: Request, titulo: str = Form(...)):
    """Endpoint para crear una nueva tarea."""
    global tarea_id_counter
    nueva_tarea = Tarea(id=tarea_id_counter, titulo=titulo)
    tareas_db.append(nueva_tarea)
    tarea_id_counter += 1
    return templates.TemplateResponse("task_list.html", {"request": request, "tareas": tareas_db})

@app.put("/tareas/{tarea_id}", response_class=HTMLResponse)
async def actualizar_tarea(request: Request, tarea_id: int, titulo: Optional[str] = Form(None), completada: Optional[bool] = Form(None)):
    """Endpoint para actualizar una tarea existente."""
    tarea = next((t for t in tareas_db if t.id == tarea_id), None)
    if tarea is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tarea no encontrada")

    if titulo is not None:
        tarea.titulo = titulo
    if completada is not None:
        tarea.completada = completada == 'true' # Recibimos 'true'/'false' como string desde el formulario

    return templates.TemplateResponse("task_list.html", {"request": request, "tareas": tareas_db})


@app.delete("/tareas/{tarea_id}", response_class=HTMLResponse)
async def borrar_tarea(request: Request, tarea_id: int):
    """Endpoint para borrar una tarea."""
    global tareas_db
    tareas_db = [tarea for tarea in tareas_db if tarea.id != tarea_id]
    return templates.TemplateResponse("task_list.html", {"request": request, "tareas": tareas_db})

# --- Fin Endpoints ---