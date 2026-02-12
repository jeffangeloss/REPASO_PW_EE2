from fastapi import FastAPI
from router import ejercicio1, ejercicio2, ejercicio3, ejercicio4, ejercicio5

app = FastAPI()

origin = ["*"]

# Con esto pruebo si mi servidor funciona!
@app.get("/")
async def root():
    return {
        "msg" : "Servidor"
    }

app.include_router(ejercicio1.router)
app.include_router(ejercicio2.router)
app.include_router(ejercicio3.router)
app.include_router(ejercicio4.router)
app.include_router(ejercicio5.router)
