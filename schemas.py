"""
Database Schemas

Nova Clothing - Ecommerce collections using Pydantic models.
Each Pydantic model maps to a MongoDB collection using the lowercase class name.
"""

from pydantic import BaseModel, Field
from typing import List, Optional

class Product(BaseModel):
    """
    Products collection schema
    Collection name: "product"
    """
    title: str = Field(..., description="Product title")
    description: Optional[str] = Field(None, description="Detailed description of the product")
    price: float = Field(..., ge=0, description="Price in USD")
    category: str = Field(..., description="Product category, e.g., 'T-Shirts', 'Hoodies'")
    brand: str = Field("Nova", description="Brand name")
    images: List[str] = Field(default_factory=list, description="List of image URLs")
    sizes: List[str] = Field(default_factory=lambda: ["XS","S","M","L","XL"], description="Available sizes")
    colors: List[str] = Field(default_factory=list, description="Available color names")
    in_stock: bool = Field(True, description="Whether product is in stock")
    stock_qty: int = Field(50, ge=0, description="Total stock quantity")
    rating: float = Field(4.5, ge=0, le=5, description="Average rating")
    tags: List[str] = Field(default_factory=list, description="Search tags")

class OrderItem(BaseModel):
    product_id: str = Field(..., description="Referenced product _id as string")
    title: str
    price: float
    quantity: int = Field(..., ge=1)
    size: Optional[str] = None
    color: Optional[str] = None
    image: Optional[str] = None

class Customer(BaseModel):
    name: str
    email: str
    phone: Optional[str] = None
    address_line1: str
    address_line2: Optional[str] = None
    city: str
    state: str
    postal_code: str
    country: str = Field("US")

class Order(BaseModel):
    """
    Orders collection schema
    Collection name: "order"
    """
    items: List[OrderItem]
    customer: Customer
    subtotal: float = Field(..., ge=0)
    shipping: float = Field(0, ge=0)
    total: float = Field(..., ge=0)
    status: str = Field("pending", description="pending | paid | shipped | delivered | cancelled")
    notes: Optional[str] = None
