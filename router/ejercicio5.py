# Ejercicio 5: Mini API de “carrito de compras” (sin pagos)
# API que simula un carrito con productos en memoria.

from typing import Optional
from uuid import uuid4
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

router = APIRouter(prefix="", tags=["Ejercicio5"])


# =========================
# MODELOS
# =========================
class Product(BaseModel):
    id: str
    name: str
    price: float = Field(..., gt=0)   # > 0
    stock: int = Field(..., ge=0)     # >= 0

class ProductCreate(BaseModel):
    name: str
    price: float = Field(..., gt=0)
    stock: int = Field(..., ge=0)

class CartItemCreate(BaseModel):
    product_id: str
    quantity: int = Field(..., gt=0)

class CartItemView(BaseModel):
    product_id: str
    name: str
    price_unit: float
    quantity: int
    subtotal: float

class CartView(BaseModel):
    id: str
    items: list[CartItemView]
    total: float


# =========================
# MEMORIA
# =========================
product_history: dict[str, Product] = {
    "11111111-1111-1111-1111-111111111111": Product(
        id="11111111-1111-1111-1111-111111111111",
        name="Mouse Gamer",
        price=79.90,
        stock=10
    ),
    "22222222-2222-2222-2222-222222222222": Product(
        id="22222222-2222-2222-2222-222222222222",
        name="Teclado Mecánico",
        price=199.00,
        stock=5
    ),
}

# carts[cart_id] = { product_id: quantity }
cart_history: dict[str, dict[str, int]] = {}


# =========================
# HELPERS (para no repetir)
# =========================
def get_product_or_404(product_id: str):
    product = product_history.get(product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product

def get_cart_or_create(cart_id: str):
    if cart_id not in cart_history:
        cart_history[cart_id] = {}
    return cart_history[cart_id]

def build_cart(cart_id: str):
    cart = cart_history.get(cart_id)
    if cart is None:
        raise HTTPException(status_code=404, detail="Cart not found")

    items = []
    total = 0.0

    for pid, qty in cart.items():
        prod = get_product_or_404(pid)
        subtotal = prod.price * qty
        total += subtotal

        items.append(
            CartItemView(
                product_id=pid,
                name=prod.name,
                price_unit=prod.price,
                quantity=qty,
                subtotal=subtotal
            )
        )

    return CartView(
        id=cart_id,
        items=items,
        total=round(total, 2)
    )


# =========================
# ENDPOINTS
# =========================

# 1) POST /products
@router.post("/products")
async def create_product(payload: ProductCreate):
    product_id = str(uuid4())

    product = Product(
        id=product_id,
        name=payload.name,
        price=payload.price,
        stock=payload.stock
    )

    product_history[product_id] = product
    return {"msg": "producto creado", "data": product}


# 4) GET /products
# Query params: max_price (float|null), in_stock (bool|null)
@router.get("/products")
async def list_products(
    max_price: Optional[float] = Query(default=None, gt=0),
    in_stock: Optional[bool] = Query(default=None),
):
    result = []

    for p in product_history.values():
        if max_price is not None and p.price > max_price:
            continue
        if in_stock is True and p.stock <= 0:
            continue
        if in_stock is False and p.stock > 0:
            continue
        result.append(p)

    return {"msg": "", "data": result}


# 2) POST /cart/{cart_id}/items
# Body: { product_id: str, quantity: int (>0) }
@router.post("/cart/{cart_id}/items")
async def add_item(cart_id: str, payload: CartItemCreate):
    product = get_product_or_404(payload.product_id)

    # Validar stock
    if product.stock < payload.quantity:
        raise HTTPException(status_code=400, detail="Stock insuficiente")

    cart = get_cart_or_create(cart_id)

    # Acumular cantidad
    cart[payload.product_id] = cart.get(payload.product_id, 0) + payload.quantity

    # Reservar stock (descontar)
    product.stock -= payload.quantity
    product_history[product.id] = product

    return {"msg": "item agregado al carrito", "data": build_cart(cart_id)}


# 3) GET /cart/{cart_id}
@router.get("/cart/{cart_id}")
async def get_cart(cart_id: str):
    return {"msg": "", "data": build_cart(cart_id)}


# EXTRA (reto): DELETE /cart/{cart_id}/items/{product_id}
@router.delete("/cart/{cart_id}/items/{product_id}")
async def delete_item(cart_id: str, product_id: str):
    cart = cart_history.get(cart_id)
    if cart is None:
        raise HTTPException(status_code=404, detail="Cart not found")

    qty = cart.get(product_id)
    if qty is None:
        raise HTTPException(status_code=404, detail="Item not found in cart")

    # Devolver stock
    product = get_product_or_404(product_id)
    product.stock += qty
    product_history[product_id] = product

    # Eliminar item
    del cart[product_id]

    # Si queda vacío, borrar carrito (opcional)
    if len(cart) == 0:
        del cart_history[cart_id]
        return {"msg": "item eliminado, carrito vacío", "data": {"id": cart_id, "items": [], "total": 0}}

    return {"msg": "item eliminado del carrito", "data": build_cart(cart_id)}
