from fastapi import FastAPI
from router import ejercicio1, ejercicio2

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