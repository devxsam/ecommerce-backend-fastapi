"""
The CRUD file stands for CREATE, READ, UPDATE, DELETE which acts as the Data Access Layer of appln.
It's purpose is to handle all the direct interactions with the database, not indulging in the specifics
of SQL Alchemy queries from the main appln logic.

Acts as a bridge between the FASTAPI Endpoints and database models.

The file receives Python objects (like the database session and Pydantic schemas) and returns 
SQLAlchemy Model objects (like models.User).

handles database logics.

for example: main -> custom agent check passport
             crud -> immigration officer who records persons entry in database.

crud -> maintainability, testability, highly flexible.

"""
from sqlalchemy.orm import Session
from typing import List, Optional
from . import models, schemas
from auth import utils as auth_util
from .models import UserRole


def get_user(db: Session, user_id: int) -> Optional[models.User]:

    # fetching a single user by id
    # filter applies the where clause which will find the matching rows and first' executes
    # the query and returns the first matching obj.

    db_user = db.query(models.User).filter(
        models.User.user_id == user_id
    ).first()

    return db_user


def get_users(db: Session, skip: int = 0, limit: int = 100) -> List[models.User]:

    # offset(skip) will skip the specified number of rows.
    # limit will restrict the number of rows to be returned and all will give the
    # result as list of models.user object

    db_users = db.query(models.User).offset(skip).limit(limit).all()

    return db_users


def get_user_by_email(db: Session, email: str) -> Optional[models.User]:
    db_user = db.query(models.User).filter(models.User.email == email).first()

    return db_user


def create_user(db: Session, user: schemas.UserCreate) -> models.User:
    safe_password_string = user.password[:72]
    hashed_password = auth_util.hash_password(safe_password_string)

    db_user = models.User(
        email=user.email,
        password_hash=hashed_password,
        first_name=user.first_name,
        last_name=user.last_name,
        phone_number=user.phone_number,
    )

    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    return db_user


def create_user_with_role(
    db: Session, user: schemas.AdminUserCreate, role: UserRole
) -> models.User:
    safe_password_string = user.password[:72]
    hashed_password = auth_util.hash_password(safe_password_string)

    db_user = models.User(
        email=user.email,
        password_hash=hashed_password,
        first_name=user.first_name,
        last_name=user.last_name,
        phone_number=user.phone_number,
        role=role
    )  # Explicitly set the role provided by the admin

    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    return db_user


def get_product(db: Session, product_id: int) -> Optional[models.Product]:
    db_product = db.query(models.Product).filter(
        models.Product.product_id == product_id
    ).first()
    return db_product


def create_product(db: Session, product: schemas.ProductCreate) -> models.Product:
    # We use .model_dump() to convert the Pydantic schema object to a dict
    # This now correctly maps category_name and subcategory_name
    db_product = models.Product(**product.model_dump())

    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product


def get_filtered_products(
    db: Session,
    category: Optional[str] = None,
    subcategory: Optional[str] = None,
    skip: int = 0,
    limit: int = 100
) -> List[models.Product]:
    query = db.query(models.Product)

    if category:
        query = query.filter(
            models.Product.category_name.ilike(f"%{category}%")
        )

    if subcategory:
        query = query.filter(
            models.Product.subcategory_name.ilike(f"%{subcategory}%")
        )

    db_products = query.offset(skip).limit(limit).all()
    return db_products


def get_address(db: Session, address_id: int) -> Optional[models.Address]:
    db_address = db.query(models.Address).filter(
        models.Address.address_id == address_id
    ).first()
    return db_address


def get_addresses_by_user(
    db: Session,
    user_id: int,
    skip: int = 0,
    limit: int = 100
) -> List[models.Address]:
    db_addresses = (
        db.query(models.Address)
        .filter(models.Address.user_id == user_id)
        .offset(skip)
        .limit(limit)
        .all()
    )
    return db_addresses


def create_address(
    db: Session, address: schemas.AddressCreate, user_id: int
) -> models.Address:
    
    # Uses the secure, authenticated user_id passed from main.py to link the address
    db_address = models.Address(
        **address.model_dump(),
        user_id=user_id 
    )

    db.add(db_address)
    db.commit()
    db.refresh(db_address)
    return db_address



def create_order(
    db: Session, order: schemas.OrderCreate, user_id: int
) -> Optional[models.Order | dict]:
    
   
    # for shippingg
    db_shipping_address = db.query(models.Address).filter(
        models.Address.address_id == order.shipping_address_id
    ).first()
    if not db_shipping_address:
        return {"error": f"Shipping Address ID {order.shipping_address_id} not found."}

    # for billing
    db_billing_address = db.query(models.Address).filter(
        models.Address.address_id == order.billing_address_id
    ).first()
    if not db_billing_address:
        return {"error": f"Billing Address ID {order.billing_address_id} not found."}

    # This list will hold the final OrderDetail model objects
    db_details = []
    total_amount = 0.0

    for item in order.items:
        db_product = get_product(db, product_id=item.product_id)

        if not db_product:
            return {"error": f"Product ID {item.product_id} not found."}

        if item.quantity <= 0:
            return {"error": f"Quantity for Product ID {item.product_id} must be positive."}

        item_price = (
            db_product.discount_price
            if db_product.discount_price is not None
            else db_product.price
        )

        line_total = item_price * item.quantity
        total_amount += line_total

        db_detail = models.OrderDetail(
            product_id=item.product_id,
            quantity=item.quantity,
            price_at_purchase=item_price
        )
        db_details.append(db_detail)

    db_order = models.Order(
        user_id=user_id,
        shipping_address_id=order.shipping_address_id,
        billing_address_id=order.billing_address_id,
        total_amount=total_amount,
        # status defaults to OrderStatus.pending as defined in models.py
    )

    db_order.details.extend(db_details)

    db.add(db_order)
    db.commit()
    db.refresh(db_order)

    return db_order


def get_order(db: Session, order_id: int) -> Optional[models.Order]:
    db_order = db.query(models.Order).filter(
        models.Order.order_id == order_id
    ).first()
    return db_order


def get_user_orders(
    db: Session, user_id: int, skip: int = 0, limit: int = 100
) -> List[models.Order]:
    db_orders = (
        db.query(models.Order)
        .filter(models.Order.user_id == user_id)
        .offset(skip)
        .limit(limit)
        .all()
    )
    return db_orders