from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    Enum as SQLAlchemyEnum,
    Float,
    Boolean,
    ForeignKey
)
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum

from .database import Base


class UserRole(enum.Enum):
    user = "user"
    admin = "admin"


class User(Base):
    __tablename__ = "users"

    # Primary Key it is.
    user_id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    phone_number = Column(String, nullable=True)

    # Stores user role and given default as user if we dont specify a role.
    role = Column(
        SQLAlchemyEnum(UserRole), nullable=False, default=UserRole.user
    )
    # Tells the databse server to set fields value to current time when new user is created.
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    # Same, but tell DS during updation of row.
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class Product(Base):
    __tablename__ = "product"

    # Primary Key
    product_id = Column(Integer, primary_key=True, index=True)

    category_name = Column(String, index=True, nullable=False)
    subcategory_name = Column(String, index=True, nullable=True)

    name = Column(String, nullable=False)
    description = Column(String, nullable=False)
    brand = Column(String, nullable=True)
    price = Column(Float, nullable=False)
    discount_price = Column(Float, nullable=True)
    is_active = Column(Boolean, default=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class Address(Base):
    __tablename__ = "address"

    # Primary Key
    address_id = Column(Integer, primary_key=True, index=True)

    # foreign key linking user_id from user to address table
    user_id = Column(
        Integer, ForeignKey('users.user_id'), nullable=False, index=True
    )

    address_line1 = Column(String, nullable=False)
    address_line2 = Column(String, nullable=True)
    city = Column(String, nullable=False)
    state = Column(String, nullable=False)
    country = Column(String, nullable=False, default="India")
    postal_code = Column(String, nullable=False)

    # shipping and billing address inform. which will be later linked with order table.
    is_default_shipping = Column(Boolean, default=False)
    is_default_billing = Column(Boolean, default=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    user = relationship("User", backref="addresses")

    """
    backref is a shortcut that automatically creates a new property on the related model, 
    making a one-way relationship bidirectional. This lets you conveniently access the list
    of Address objects from a User object (e.g., user.addresses) without defining it manually.
    """


class OrderStatus(enum.Enum):
    pending = "pending"
    processing = "processing"
    shipped = "shipped"
    delivered = "delivered"
    cancelled = "cancelled"


class Order(Base):
    __tablename__ = "order"

    # Primary Key
    order_id = Column(Integer, primary_key=True, index=True)

    user_id = Column(
        Integer, ForeignKey('users.user_id'), nullable=False, index=True
    )

    shipping_address_id = Column(
        Integer, ForeignKey('address.address_id'), nullable=False
    )
    billing_address_id = Column(
        Integer, ForeignKey('address.address_id'), nullable=False
    )

    order_date = Column(
        DateTime(timezone=True), server_default=func.now(), index=True
    )
    total_amount = Column(Float, nullable=False)
    status = Column(
        SQLAlchemyEnum(OrderStatus),
        nullable=False,
        default=OrderStatus.pending
    )

    user = relationship("User", backref="orders")

    details = relationship(
        "OrderDetail", back_populates="order", cascade="all, delete-orphan"
    )

    shipping_address = relationship(
        "Address", foreign_keys=[shipping_address_id], backref="shipped_orders"
    )
    billing_address = relationship(
        "Address", foreign_keys=[billing_address_id], backref="billed_orders"
    )


class OrderDetail(Base):
    __tablename__ = "order_detail"

    # Primary Key
    order_detail_id = Column(Integer, primary_key=True, index=True)

    order_id = Column(
        Integer, ForeignKey('order.order_id'), nullable=False, index=True
    )

    product_id = Column(
        Integer, ForeignKey('product.product_id'), nullable=False
    )

    quantity = Column(Integer, nullable=False)
    price_at_purchase = Column(Float, nullable=False)

    order = relationship("Order", back_populates="details")
    product = relationship("Product")

    created_at = Column(DateTime(timezone=True), server_default=func.now())