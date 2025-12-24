from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, timedelta
from jose import jwt
from passlib.context import CryptContext
import psycopg2
import os
from dotenv import load_dotenv
from pathlib import Path

# =====================================
# LOAD ENV (ISOLATED)
# =====================================
env_path = Path(__file__).resolve().parent / ".env"
load_dotenv(dotenv_path=env_path)

DB_HOST = os.getenv("DB_HOST")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")

JWT_SECRET = os.getenv("JWT_SECRET")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
JWT_EXP_MINUTES = int(os.getenv("JWT_EXP_MINUTES", "30"))

CORS_ORIGINS = os.getenv("CORS_ORIGINS", "*")

# =====================================
# APP SETUP
# =====================================
app = FastAPI()
security = HTTPBearer()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[CORS_ORIGINS],
    allow_methods=["*"],
    allow_headers=["*"],
)

# =====================================
# DATABASE
# =====================================
def get_db():
    return psycopg2.connect(
        host=DB_HOST,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )

# =====================================
# SECURITY HELPERS
# =====================================
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain, hashed):
    return pwd_context.verify(plain, hashed)

def create_token(data: dict):
    expire = datetime.utcnow() + timedelta(minutes=JWT_EXP_MINUTES)
    data.update({"exp": expire})
    return jwt.encode(data, JWT_SECRET, algorithm=JWT_ALGORITHM)

# =====================================
# MODELS
# =====================================
class CompanyLogin(BaseModel):
    company_id: int
    emp_id: Optional[str] = None
    email: Optional[str] = None
    password: str

class CreateUser(BaseModel):
    emp_id: str
    name: str
    email: Optional[str] = None
    password: str
    is_company_admin: bool = False

class UpdateUser(BaseModel):
    name: str
    email: Optional[str] = None
    status: str
    is_company_admin: bool

# =====================================
# AUTH DEPENDENCY
# =====================================
def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    token = credentials.credentials
    payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])

    user_id = payload.get("sub")
    company_id = payload.get("cid")
    session_id = payload.get("sid")

    if not user_id or not company_id or not session_id:
        raise HTTPException(status_code=401, detail="Invalid token")

    conn = get_db()
    cur = conn.cursor()

    cur.execute("""
        SELECT id
        FROM user_sessions
        WHERE id = %s AND user_id = %s AND company_id = %s
    """, (session_id, user_id, company_id))

    session = cur.fetchone()

    if not session:
        cur.close()
        conn.close()
        raise HTTPException(status_code=401)

    cur.execute("""
        SELECT status, is_company_admin
        FROM users
        WHERE id = %s AND company_id = %s
    """, (user_id, company_id))

    user = cur.fetchone()

    cur.close()
    conn.close()

    if not user or user[0] != "active":
        raise HTTPException(status_code=403)

    return {
        "user_id": user_id,
        "company_id": company_id,
        "session_id": session_id,
        "is_company_admin": user[1]
    }

# =====================================
# LOGIN
# =====================================
@app.post("/company/login")
def company_login(data: CompanyLogin, request: Request):
    conn = get_db()
    cur = conn.cursor()

    if not data.emp_id and not data.email:
        raise HTTPException(status_code=400, detail="Either emp_id or email is required")

    cur.execute("""
        SELECT status
        FROM companies
        WHERE id = %s
    """, (data.company_id,))

    company = cur.fetchone()

    if not company or company[0].lower().strip() != "active":
        cur.close()
        conn.close()
        raise HTTPException(status_code=403, detail="Company not active")

    if data.emp_id:
        cur.execute("""
            SELECT id, password_hash, status
            FROM users
            WHERE company_id = %s AND emp_id = %s
        """, (data.company_id, data.emp_id))
    else:
        cur.execute("""
            SELECT id, password_hash, status
            FROM users
            WHERE company_id = %s AND email = %s
        """, (data.company_id, data.email))

    user = cur.fetchone()

    if not user:
        cur.close()
        conn.close()
        raise HTTPException(status_code=401, detail="Invalid credentials")

    user_id, password_hash, status = user

    if status != "active" or not verify_password(data.password, password_hash):
        cur.close()
        conn.close()
        raise HTTPException(status_code=401, detail="Invalid credentials")

    expires_at = datetime.utcnow() + timedelta(minutes=JWT_EXP_MINUTES)

    cur.execute("""
        INSERT INTO user_sessions
        (user_id, company_id, ip_address, user_agent, expires_at)
        VALUES (%s, %s, %s, %s, %s)
        RETURNING id
    """, (
        user_id,
        data.company_id,
        request.client.host,
        request.headers.get("user-agent"),
        expires_at
    ))

    session_id = cur.fetchone()[0]
    conn.commit()
    cur.close()
    conn.close()

    token = create_token({
        "sub": str(user_id),
        "cid": data.company_id,
        "sid": session_id
    })

    return {"access_token": token}

# =====================================
# LOGOUT
# =====================================
@app.post("/company/logout")
def company_logout(current=Depends(get_current_user)):
    conn = get_db()
    cur = conn.cursor()

    cur.execute("""
        DELETE FROM user_sessions
        WHERE id = %s AND user_id = %s
    """, (current["session_id"], current["user_id"]))

    conn.commit()
    cur.close()
    conn.close()

    return {"message": "Logged out successfully"}

# =====================================
# HOME
# =====================================
@app.get("/company/me")
def get_company_home(current=Depends(get_current_user)):
    conn = get_db()
    cur = conn.cursor()

    cur.execute("""
        SELECT 
            u.emp_id,
            u.name,
            u.email,
            u.is_company_admin,
            c.company_name
        FROM users u
        JOIN companies c ON c.id = u.company_id
        WHERE u.id = %s AND u.company_id = %s
    """, (current["user_id"], current["company_id"]))

    user = cur.fetchone()

    if not user:
        cur.close()
        conn.close()
        raise HTTPException(status_code=404, detail="User not found")

    emp_id, name, email, is_company_admin, company_name = user

    cur.execute("""
        SELECT f.code, f.name
        FROM company_features cf
        JOIN features f ON cf.feature_id = f.id
        WHERE cf.company_id = %s AND cf.enabled = TRUE
        ORDER BY f.name
    """, (current["company_id"],))

    features = cur.fetchall()

    cur.close()
    conn.close()

    return {
        "user": {
            "emp_id": emp_id,
            "name": name,
            "email": email,
            "company": company_name,
            "is_company_admin": is_company_admin
        },
        "features": [
            {"code": f[0], "name": f[1]} for f in features
        ]
    }

# =====================================
# USERS
# =====================================
@app.get("/company/users")
def list_users(current=Depends(get_current_user)):
    if not current["is_company_admin"]:
        raise HTTPException(status_code=403)

    conn = get_db()
    cur = conn.cursor()

    cur.execute("""
        SELECT id, emp_id, name, email, status, is_company_admin, created_at
        FROM users
        WHERE company_id = %s
        ORDER BY created_at DESC
    """, (current["company_id"],))

    users = cur.fetchall()
    cur.close()
    conn.close()

    return [
        {
            "id": u[0],
            "emp_id": u[1],
            "name": u[2],
            "email": u[3],
            "status": u[4],
            "is_company_admin": u[5],
            "created_at": u[6]
        } for u in users
    ]

@app.post("/company/users")
def add_user(data: CreateUser, current=Depends(get_current_user)):
    if not current["is_company_admin"]:
        raise HTTPException(status_code=403)

    conn = get_db()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO users
        (company_id, emp_id, name, email, password_hash, is_company_admin)
        VALUES (%s, %s, %s, %s, %s, %s)
    """, (
        current["company_id"],
        data.emp_id,
        data.name,
        data.email,
        pwd_context.hash(data.password),
        data.is_company_admin
    ))

    conn.commit()
    cur.close()
    conn.close()

    return {"message": "User created successfully"}

@app.put("/company/users/{user_id}")
def update_user(user_id: int, data: UpdateUser, current=Depends(get_current_user)):
    if not current["is_company_admin"]:
        raise HTTPException(status_code=403)

    conn = get_db()
    cur = conn.cursor()

    cur.execute("""
        UPDATE users
        SET name = %s,
            email = %s,
            status = %s,
            is_company_admin = %s
        WHERE id = %s AND company_id = %s
    """, (
        data.name,
        data.email,
        data.status,
        data.is_company_admin,
        user_id,
        current["company_id"]
    ))

    if cur.rowcount == 0:
        cur.close()
        conn.close()
        raise HTTPException(status_code=404)

    conn.commit()
    cur.close()
    conn.close()

    return {"message": "User updated"}

# =====================================
# USER SESSIONS
# =====================================
@app.get("/company/user-sessions")
def get_all_user_sessions(current=Depends(get_current_user)):
    if not current["is_company_admin"]:
        raise HTTPException(status_code=403)

    conn = get_db()
    cur = conn.cursor()

    cur.execute("""
        SELECT
            s.id,
            u.name,
            u.emp_id,
            s.ip_address,
            s.user_agent,
            s.created_at,
            s.expires_at
        FROM user_sessions s
        JOIN users u ON u.id = s.user_id
        WHERE u.company_id = %s
        ORDER BY s.created_at DESC
    """, (current["company_id"],))

    rows = cur.fetchall()
    cur.close()
    conn.close()

    return [
        {
            "session_id": r[0],
            "name": r[1],
            "emp_id": r[2],
            "ip_address": r[3],
            "user_agent": r[4],
            "login_at": r[5],
            "expires_at": r[6]
        }
        for r in rows
    ]

@app.delete("/company/user-sessions/{session_id}")
def terminate_user_session(session_id: int, current=Depends(get_current_user)):
    if not current["is_company_admin"]:
        raise HTTPException(status_code=403)

    conn = get_db()
    cur = conn.cursor()

    cur.execute("""
        DELETE FROM user_sessions
        USING users
        WHERE user_sessions.id = %s
          AND user_sessions.user_id = users.id
          AND users.company_id = %s
    """, (session_id, current["company_id"]))

    if cur.rowcount == 0:
        cur.close()
        conn.close()
        raise HTTPException(status_code=404)

    conn.commit()
    cur.close()
    conn.close()

    return {"message": "Session terminated"}
