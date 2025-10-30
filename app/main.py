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


@app.post("/login", tags=["Login Authentication"])
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    
    """Authenticates a user and returns a JWT access token."""

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
    "/signup/",
    response_model=schemas.User,
    tags=["Users"],
    status_code=status.HTTP_201_CREATED
) 


def signup(user: schemas.UserCreate, db: Session = Depends(get_db)):

    """
    Registers a new regular user account. **Unauthenticated Access.**
    """

    db_user = crud.get_user_by_email(db, email=user.email)

    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    new_user = crud.create_user(db=db, user=user)

    return new_user


# returning here the list of object and also adding the safety.
@app.get("/users", response_model=List[schemas.User], tags=["Users"])
def read_users(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_admin: models.User = Depends(auth_util.get_current_admin_user)
):
    
    """
    Retrieves a list of all user accounts. **Requires Admin Privileges.**
    """

    users = crud.get_users(db, skip=skip, limit=limit)
    return users


@app.get("/profile", response_model=schemas.User, tags=["Users"])
def read_my_profile(
    current_user: models.User = Depends(auth_util.get_current_user)
):
    """Retrieves the details of the currently authenticated user's profile. **Only accessible to authenticated users.**"""
    
    return current_user


@app.get("/users/{user_id}/", response_model=schemas.User, tags=["Users"])
def read_user_by_id(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth_util.get_current_admin_user)
):
    
    """Retrieves a specific user's details by ID. **Only accessible to authenticated ADMINS.** (User must be the Admin)."""
    db_user = crud.get_user(db, user_id=user_id)

    if db_user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    return db_user


@app.post(
    "/admin/users",
    response_model=schemas.User,
    tags=["Admin"],
    status_code=status.HTTP_201_CREATED
)
def Admin_Signup_by_Authenticated_Admin(
    user: schemas.AdminUserCreate,  # Expects email, password, AND role
    db: Session = Depends(get_db),

    current_admin: models.User = Depends(auth_util.get_current_admin_user)
):
    """
    Creates a new user account with a specified role (user/admin). **Requires Admin Privileges.**
    """

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
    
    """Creates a new product listing. **Requires Admin Privileges.**"""


    return crud.create_product(db=db, product=product)


@app.get("/products/", response_model=List[schemas.Product], tags=["Products"])
def search_any_product(
    category: Optional[str] = None,
    subcategory: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    
    """Retrieves a list of products, optionally filtered by category or subcategory. **Unauthenticated Access.**"""

    products = crud.get_filtered_products(
        db,
        category=category,
        subcategory=subcategory,
        skip=skip,
        limit=limit
    )
    return products


@app.get("/products/{product_id}", response_model=schemas.Product, tags=["Products"])
def find_a_product_by_id(
    product_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth_util.get_current_admin_user)
):
    
    """Retrieves the details for a single product by ID. **Only accessible to authenticated users.**"""

    db_product = crud.get_product(db, product_id=product_id)
    if db_product is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    return db_product


@app.post(
    "/addresses",
    response_model=schemas.Address,
    tags=["Addresses"],
    status_code=status.HTTP_201_CREATED
)
def Add_user_address(
    address: schemas.AddressCreate, 
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth_util.get_current_user)
    
):
    
    """Adds a new address for the specified user. **Only accessible to authenticated users.**"""

    # FIX: Pass the securely obtained user_id to the CRUD function
    db_address = crud.create_address(
        db=db, 
        address=address,
        user_id=current_user.user_id 
    )

    if db_address is None:
        # The error handling must now reflect the CRUD function's inability to create the address
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Could not create address."
        )

    return db_address


@app.get(
    "/users/{user_id}/addresses",
    response_model=List[schemas.Address],
    tags=["Addresses"]
)
def read_user_addresses(
    user_id: int,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth_util.get_current_admin_user)
):
    
    """Retrieves a list of addresses belonging to a specific user. **Requires Admin Privileges.**"""
    addresses = crud.get_addresses_by_user(
        db, user_id=user_id, skip=skip, limit=limit
    )
    return addresses


@app.get("/addresses", response_model=List[schemas.Address], tags=["Addresses"])
def list_my_addresses(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth_util.get_current_user)
):
    """
    Retrieves a list of all addresses belonging to the currently authenticated user.
    Uses the user_id from the authentication token.
    """
    addresses = crud.get_addresses_by_user(
        db, user_id=current_user.user_id, skip=skip, limit=limit
    )
    return addresses


@app.get("/orders", response_model=List[schemas.Order], tags=["Orders"])
def list_my_orders( # New function for listing all user orders
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    # The current_user dependency automatically gets the user_id from the token
    current_user: models.User = Depends(auth_util.get_current_user)
):
    
    # We pass the user_id from the authenticated user directly to CRUD
    orders = crud.get_user_orders(
        db, 
        user_id=current_user.user_id, 
        skip=skip, 
        limit=limit
    )
    return orders


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
    current_user: models.User = Depends(auth_util.get_current_admin_user)
):
    
    """Retrieves a list of orders placed by any specific user ID. **Requires Admin Privileges.**"""

    orders = crud.get_user_orders(
        db, user_id=user_id, skip=skip, limit=limit
    )
    return orders


@app.post(
    "/checkout",
    response_model=schemas.Order,
    tags=["Orders"],
    status_code=status.HTTP_201_CREATED
)
def checkout(
    order: schemas.OrderCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth_util.get_current_user)
):

    """
    Places a new order using the items and addresses provided. 
    The user ID is automatically inferred from the authentication token.
    **Only accessible to authenticated users.**
    """

    result = crud.create_order(db=db, order=order,  user_id=current_user.user_id )

    if isinstance(result, dict) and 'error' in result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=result['error']
        )

    return result