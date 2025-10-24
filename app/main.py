"""
This file is responsible for handling HTTP requests. It has decorators to define the URL paths and HTTP methods they respond to.

It calls the functions from the CRUD layer.

"""
from typing import List, Optional

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from . import crud, models, schemas
from .database import get_db, engine
from auth import utils as auth_util


models.Base.metadata.create_all(bind=engine)


# This app object is what we will use to define all our API routes.
app = FastAPI()


@app.post("/token", tags=["Authentication"])
def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    user = crud.get_user_by_email(db, email=form_data.username)

    login_password = form_data.password[:72]

    if not user or not auth_util.verify_password(
        login_password, user.password_hash
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = auth_util.create_access_token(data={"user_id": user.user_id})

    return {"access_token": access_token, "token_type": "bearer"}


@app.post(
    "/users/",
    response_model=schemas.User,
    tags=["Users"],
    status_code=status.HTTP_201_CREATED
)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_email(db, email=user.email)

    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    new_user = crud.create_user(db=db, user=user)

    return new_user


# returning here the list of object and also adding the safety.
@app.get("/users/", response_model=List[schemas.User], tags=["Users"])
def read_users(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_admin: models.User = Depends(auth_util.get_current_admin_user)
):
    users = crud.get_users(db, skip=skip, limit=limit)
    return users


@app.get("/users/me", response_model=schemas.User, tags=["Users"])
def read_users_me(
    current_user: models.User = Depends(auth_util.get_current_user)
):
    return current_user


@app.get("/users/{user_id}", response_model=schemas.User, tags=["Users"])
def read_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth_util.get_current_user)
):
    db_user = crud.get_user(db, user_id=user_id)

    if db_user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    return db_user


@app.post(
    "/admin/users/",
    response_model=schemas.User,
    tags=["Admin"],
    status_code=status.HTTP_201_CREATED
)
def create_user_by_admin(
    user: schemas.AdminUserCreate,  # Expects email, password, AND role
    db: Session = Depends(get_db),

    current_admin: models.User = Depends(auth_util.get_current_admin_user)
):

    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    new_user = crud.create_user_with_role(db=db, user=user, role=user.role)

    return new_user


@app.post(
    "/products/",
    response_model=schemas.Product,
    tags=["Products"],
    status_code=status.HTTP_201_CREATED
)
def create_product(
    product: schemas.ProductCreate,
    db: Session = Depends(get_db),
    current_admin_user: models.User = Depends(auth_util.get_current_admin_user)
):
    return crud.create_product(db=db, product=product)


@app.get("/products/", response_model=List[schemas.Product], tags=["Products"])
def read_products(
    category: Optional[str] = None,
    subcategory: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    products = crud.get_filtered_products(
        db,
        category=category,
        subcategory=subcategory,
        skip=skip,
        limit=limit
    )
    return products


@app.get("/products/{product_id}", response_model=schemas.Product, tags=["Products"])
def read_product(
    product_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth_util.get_current_user)
):
    db_product = crud.get_product(db, product_id=product_id)
    if db_product is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    return db_product


@app.post(
    "/addresses/",
    response_model=schemas.Address,
    tags=["Addresses"],
    status_code=status.HTTP_201_CREATED
)
def create_user_address(
    address: schemas.AddressCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth_util.get_current_user),
    current_admin_user: models.User = Depends(
        auth_util.get_current_admin_user
    )
):
    db_address = crud.create_address(db=db, address=address)

    # Check if the CRUD function returned None (meaning user_id was invalid)
    if db_address is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {address.user_id} not found."
        )

    return db_address


@app.get(
    "/users/{user_id}/addresses/",
    response_model=List[schemas.Address],
    tags=["Addresses"]
)
def read_user_addresses(
    user_id: int,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth_util.get_current_user)
):
    addresses = crud.get_addresses_by_user(
        db, user_id=user_id, skip=skip, limit=limit
    )
    return addresses


@app.get("/addresses/{address_id}", response_model=schemas.Address, tags=["Addresses"])
def read_address(
    address_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth_util.get_current_user)
):
    db_address = crud.get_address(db, address_id=address_id)
    if db_address is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Address not found"
        )
    return db_address


@app.get("/orders/{order_id}", response_model=schemas.Order, tags=["Orders"])
def read_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth_util.get_current_user)
):
    db_order = crud.get_order(db, order_id=order_id)
    if db_order is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    return db_order


@app.get(
    "/users/{user_id}/orders/",
    response_model=List[schemas.Order],
    tags=["Orders"]
)
def read_user_orders(
    user_id: int,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth_util.get_current_user)
):
    orders = crud.get_user_orders(
        db, user_id=user_id, skip=skip, limit=limit
    )
    return orders


@app.post(
    "/orders/",
    response_model=schemas.Order,
    tags=["Orders"],
    status_code=status.HTTP_201_CREATED
)
def place_order(
    order: schemas.OrderCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth_util.get_current_user)
):

    """
    Only accessible to authenticated users.
    """

    # You might also want to ensure order.user_id matches current_user.user_id here
    # for security, but the main point is the dependency check.

    result = crud.create_order(db=db, order=order)

    if isinstance(result, dict) and 'error' in result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=result['error']
        )

    return result