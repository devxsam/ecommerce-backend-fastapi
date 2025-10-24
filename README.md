# 🛒 FastAPI E-commerce Backend API

This project is the secure and flexible backend foundation for a complete e-commerce application. It uses **FastAPI** (for high performance), **SQLAlchemy** (to manage the database), and **Alembic** (for safe database updates).

The goal of this API is to manage the essential components of an online store: **Users**, **Products**, **Orders**, and **Authentication**.

---

## 🗺️ Core E-commerce Components (What This API Will Manage)

This backend is designed around standard e-commerce features:

| Component | Description | Example Data Managed | 
| :--- | :--- | :--- | 
| **User Management** | Handles account creation, secure login, and user profile information (like name and email). | User IDs, Email, Hashed Passwords. | 
| **Products** | Stores all items available for sale, including descriptions, inventory, and pricing. | Product Name, Price, Stock Quantity, Description. | 
| **Orders** | Tracks customer purchases, managing the items bought, total cost, and order status (e.g., pending, shipped). | Order ID, Date Placed, Total Amount, Items List. | 
| **Authentication** | Provides secure token-based login (**JWT**) so only authorized users can place orders or manage products. | Access Tokens, Login Verification. | 

---

## 🔒 Security: How to Keep Your Secrets Safe

A secure backend must keep its sensitive connection details private. This section explains the mandatory step to set up your database and security keys locally.

### 1. Setting Up Your Secret `.env` File

Since this repository is public, you **must not** put your database link or security keys directly into any code file.

We use a special file named **`.env`** to store these secrets locally. 

**Action:** Create a new file named **`.env`** in the main project folder.

**Content of `.env`:**

```
This is the full link your application uses to connect to your database.
Replace the placeholder with your actual database link.
DATABASE_URL="<YOUR_ACTUAL_DATABASE_CONNECTION_STRING>"

This is a secret code used to encrypt and verify user login tokens (JWT).
You must generate a very long, complex, and random code here for security!
SECRET_KEY="<YOUR_SECRET_JWT_KEY>"

Standard settings for security tokens
ALGORITHM="HS256" ACCESS_TOKEN_EXPIRE_MINUTES=30
```

## 🚀 Setting Up Your Project to Run Locally

### 1. Get the Project and Install Dependencies

First, download the project files and install the required Python libraries inside a virtual environment (`venv`).

```
# Get the files
git clone [https://github.com/devxsam/ecommerce-backend-fastapi](https://github.com/devxsam/ecommerce-backend-fastapi)
cd ecommerce-backend-fastapi
```

```
# Activate the virtual environment and install packages
# In Windows (PowerShell): ./venv/Scripts/Activate.ps1
# In Linux or macOS: source venv/bin/activate

pip install -r requirements.txt
```


---

# 2. Prepare the Database (Alembic)
Alembic is the tool that reads your Python database structure and creates the necessary tables in your database.

1. Verify: Confirm that your DATABASE_URL is correctly added to your local .env file.

2. Run the Setup: This command builds all the initial tables (like the user table).

```
alembic upgrade head
```

3. Start the Server
Use Uvicorn to run the API. The --reload setting means the server will instantly restart whenever you save changes to your Python code.

```
uvicorn app.main:app --reload
```

## 🔗 Documentation and Database Updates

Once the server is running, you can access the interactive documentation at ( http://127.0.0.1:8000/docs ).

If you update your database models (in app/models.py):

1. Generate Script:

```

alembic revision --autogenerate -m "description_of_new_feature"
```
2. Apply Changes:


```
alembic upgrade head
```
## 📁 Project Folder Breakdown

```
ecommerce-backend-fastapi/
├── alembic/                      # Tools and scripts for updating the database structure.
├── app/
│   ├── crud.py                   # Code that performs all database actions (Create, Read, Update, Delete).
│   ├── database.py               # Sets up the database connection.
│   ├── main.py                   # The main file defining all API paths and endpoints.
│   ├── models.py                 # Defines the structure of data in the database.
│   └── schemas.py                # Defines the strict format for data entering and leaving the API.
├── auth/
│   └── utils.py                  # Code that handles user login and authentication tokens.
├── .env                          
├── .gitignore                    
└── requirements.txt              # List of all Python libraries needed for the project.

```
