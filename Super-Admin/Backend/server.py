from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import psycopg2
from passlib.context import CryptContext
from datetime import datetime, timedelta
from jose import jwt

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class UserSignup(BaseModel):
    admin_id: str
    password: str

class UserLogin(BaseModel):
    admin_id: str
    password: str

def get_db_connection():
    return psycopg2.connect(
        host="localhost",
        database="CMS",
        user="postgres",
        password="10815"
    )

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(p: str):
    return pwd_context.hash(p)

def verify_password(p: str, h: str):
    return pwd_context.verify(p, h)

SECRET_KEY = "change_this_secret"
ALGORITHM = "HS256"

def create_access_token(data: dict):
    expire = datetime.utcnow() + timedelta(minutes=30)
    data.update({"exp": expire})
    return jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)

# ---------------- SIGNUP ----------------
@app.post("/signup")
def signup(user: UserSignup):
    conn = get_db_connection()
    cur = conn.cursor()

    try:
        cur.execute(
            """
            INSERT INTO platform_admins (name, email, role, password_hash)
            VALUES (%s, %s, %s, %s)
            """,
            (
                user.admin_id,
                f"theatulpathak1@gmail.com",  # temp email
                "SUPER_ADMIN",
                hash_password(user.password)
            )
        )
        conn.commit()
        return {"message": "User created successfully"}

    except psycopg2.errors.UniqueViolation:
        conn.rollback()
        return {"error": "Admin already exists"}

    finally:
        cur.close()
        conn.close()

# ---------------- LOGIN ----------------
@app.post("/login")
def login(user: UserLogin):
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute(
        "SELECT id, password_hash FROM platform_admins WHERE name = %s",
        (user.admin_id,)
    )
    row = cur.fetchone()

    cur.close()
    conn.close()

    if not row:
        return {"error": "Invalid credentials"}

    user_id, password_hash = row

    if not verify_password(user.password, password_hash):
        return {"error": "Invalid credentials"}

    token = create_access_token({"sub": str(user_id)})
    return {"access_token": token}
