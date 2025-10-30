"""
This file defines the pydantic data schemas for the application.
It does: data validation, serliazation, and api documentation.

It defines the exact shape of the data that your api will accept from a client and the shape of data that 
your api will send back to a client.

"""

from datetime import datetime
from typing import Optional, List
from enum import Enum as PyEnum

from pydantic import BaseModel, EmailStr

from .models import UserRole


# ------------------ User Schemas ------------------

class UserBase(BaseModel):
    email: EmailStr
    first_name: str
    last_name: str
    phone_number: Optional[str] = None


class UserCreate(UserBase):
    password: str


class User(UserBase):
    user_id: int
    role: UserRole
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:

        # This allows Pydantic to read data from ORM objects

        from_attributes = True


class AdminUserCreate(UserBase):
    password: str
    role: UserRole


# ------------------ Product Schemas ------------------

class ProductBase(BaseModel):
    name: str
    description: str
    brand: Optional[str] = None
    price: float
    discount_price: Optional[float] = None
    is_active: Optional[bool] = True

    category_name: str
    subcategory_name: Optional[str] = None

    class Config:
        from_attributes = True


class ProductCreate(ProductBase):
    pass


class Product(ProductBase):

    # Add product_id back here for the response model

    product_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# ------------------ Address Schemas ------------------

class AddressBase(BaseModel):
    address_line1: str
    address_line2: Optional[str] = None
    city: str
    state: str
    country: str = "India"
    postal_code: str
    is_default_shipping: Optional[bool] = False
    is_default_billing: Optional[bool] = False

    class Config:
        from_attributes = True


class AddressCreate(AddressBase):
    pass


class Address(AddressBase):
    address_id: int
    user_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# ------------------ OrderDetail Schemas ------------------

class OrderDetailBase(BaseModel):
    product_id: int
    quantity: int


class OrderDetailCreate(OrderDetailBase):
    pass


class OrderDetail(OrderDetailBase):
    order_detail_id: int
    order_id: int  # Links back to the parent order
    price_at_purchase: float
    created_at: datetime

    class Config:
        from_attributes = True


# ------------------ Order Schemas ------------------

class OrderCreate(BaseModel):
   
    shipping_address_id: int
    billing_address_id: int

    # The list of items being purchased
    items: List[OrderDetailCreate]  # Uses the list of line items defined above


class OrderStatusSchema(str, PyEnum):
    pending = "pending"
    processing = "processing"
    shipped = "shipped"
    delivered = "delivered"
    cancelled = "cancelled"


class Order(BaseModel):
    order_id: int
    user_id: int
    shipping_address_id: int
    billing_address_id: int
    order_date: datetime
    total_amount: float
    status: OrderStatusSchema

    # Include the list of line items in the response

    details: List[OrderDetail]

    class Config:
        from_attributes = True