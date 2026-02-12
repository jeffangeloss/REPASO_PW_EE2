# Ejercicio 5: Mini API de “carrito de compras” (sin pagos)
# Contexto
# API que simula un carrito con productos en memoria.
from uuid import uuid4
from fastapi import APIRouter
from pydantic import BaseModel, Field


router = APIRouter(
    prefix = "",
    tags = ["Ejercicio5"]
)

class Product(BaseModel):
    id : str
    name : str
    price : float = Field(...,ge=1)
    stock : int = Field(...,ge=0)

class ProductCreate(BaseModel):
    name : str
    price : float = Field(...,ge=1)
    stock : int = Field(...,ge=0)

product_history: dict[str,Product] = {}

# 1. POST /products
# - Body (JSON): { "name": str, "price": float (>0), "stock": int (>=0) }
@router.post("/products")
async def createProduct(product: ProductCreate):
    product_id = str(uuid4())
    
    product = Product(
        id = product_id,
        name = product.name,
        price = product.price,
        stock = product.stock
    )
    
    product_history[product_id] = product
    return{
        "msg" : "producto creado",
        "data" : product
    }
    
# 2. POST /cart/{cart_id}/items
# - Path param: cart_id
# - Body (JSON): { "product_id": int, "quantity": int (>0) }
@router.post("/cart/{cart_id}/items")
async def agregarProductosCarrito(cart_id: str):
    pass