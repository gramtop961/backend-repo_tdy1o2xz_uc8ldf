import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from bson import ObjectId

from database import db, create_document, get_documents
from schemas import Product, Order

app = FastAPI(title="Nova Clothing API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def read_root():
    return {"message": "Nova Clothing API is running"}


@app.get("/test")
def test_database():
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": []
    }
    try:
        if db is not None:
            response["database"] = "✅ Available"
            response["database_name"] = db.name if hasattr(db, 'name') else "✅ Connected"
            response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
            response["connection_status"] = "Connected"
            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️ Connected but Error: {str(e)[:50]}"
        else:
            response["database"] = "⚠️ Available but not initialized"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:50]}"

    response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
    response["database_name"] = "✅ Set" if os.getenv("DATABASE_NAME") else "❌ Not Set"

    return response


# Utility to convert ObjectId to string
class ProductOut(BaseModel):
    id: str
    title: str
    description: Optional[str]
    price: float
    category: str
    brand: str
    images: List[str]
    sizes: List[str]
    colors: List[str]
    in_stock: bool
    stock_qty: int
    rating: float
    tags: List[str]


@app.get("/api/products", response_model=List[ProductOut])
def list_products(category: Optional[str] = None, q: Optional[str] = None, limit: int = 50):
    if db is None:
        raise HTTPException(status_code=500, detail="Database not configured")
    filter_dict = {}
    if category:
        filter_dict["category"] = category
    if q:
        # Simple search by title or tags
        filter_dict["$or"] = [
            {"title": {"$regex": q, "$options": "i"}},
            {"tags": {"$regex": q, "$options": "i"}},
        ]
    docs = get_documents("product", filter_dict, limit)
    result = []
    for d in docs:
        d["id"] = str(d.get("_id"))
        d.pop("_id", None)
        result.append(ProductOut(**d))
    return result


@app.post("/api/products", status_code=201)
def create_product(product: Product):
    if db is None:
        raise HTTPException(status_code=500, detail="Database not configured")
    product_id = create_document("product", product)
    return {"id": product_id}


@app.get("/api/products/{product_id}", response_model=ProductOut)
def get_product(product_id: str):
    if db is None:
        raise HTTPException(status_code=500, detail="Database not configured")
    try:
        doc = db["product"].find_one({"_id": ObjectId(product_id)})
        if not doc:
            raise HTTPException(status_code=404, detail="Product not found")
        doc["id"] = str(doc.get("_id"))
        doc.pop("_id", None)
        return ProductOut(**doc)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid product id")


# Orders
@app.post("/api/orders", status_code=201)
def create_order(order: Order):
    if db is None:
        raise HTTPException(status_code=500, detail="Database not configured")
    order_id = create_document("order", order)
    return {"id": order_id}


@app.get("/api/seed", summary="Seed sample products for Nova")
def seed_products():
    if db is None:
        raise HTTPException(status_code=500, detail="Database not configured")
    if db["product"].count_documents({}) > 0:
        return {"seeded": False, "message": "Products already exist"}

    sample_products = [
        {
            "title": "Nova Essential Tee",
            "description": "Ultra-soft cotton tee with a tailored fit.",
            "price": 24.99,
            "category": "T-Shirts",
            "brand": "Nova",
            "images": [
                "https://images.unsplash.com/photo-1541099649105-f69ad21f3246?q=80&w=1200&auto=format&fit=crop",
            ],
            "sizes": ["S","M","L","XL"],
            "colors": ["Black","White","Navy"],
            "in_stock": True,
            "stock_qty": 150,
            "rating": 4.6,
            "tags": ["tee","cotton","basic"]
        },
        {
            "title": "Nova Performance Hoodie",
            "description": "Lightweight hoodie for everyday comfort.",
            "price": 49.99,
            "category": "Hoodies",
            "brand": "Nova",
            "images": [
                "https://images.unsplash.com/photo-1520975693415-1f3f1a1c9b70?q=80&w=1200&auto=format&fit=crop",
            ],
            "sizes": ["S","M","L","XL"],
            "colors": ["Charcoal","Olive"],
            "in_stock": True,
            "stock_qty": 90,
            "rating": 4.7,
            "tags": ["hoodie","performance"]
        },
        {
            "title": "Nova Classic Cap",
            "description": "Adjustable cap with embroidered Nova logo.",
            "price": 19.99,
            "category": "Accessories",
            "brand": "Nova",
            "images": [
                "https://images.unsplash.com/photo-1548883354-7622d2c61d1d?q=80&w=1200&auto=format&fit=crop",
            ],
            "sizes": ["One Size"],
            "colors": ["Black","Khaki"],
            "in_stock": True,
            "stock_qty": 120,
            "rating": 4.4,
            "tags": ["cap","hat"]
        },
    ]

    for p in sample_products:
        db["product"].insert_one(p)

    return {"seeded": True, "count": len(sample_products)}


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
