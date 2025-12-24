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

class UpdateUserWithRoles(BaseModel):
    name: str
    email: Optional[str] = None
    status: str
    is_company_admin: bool
    role_ids: list[int] = []


class CreateUserWithRoles(CreateUser):
    role_ids: Optional[list[int]] = []

class CreateUserWithRoles(BaseModel):
    emp_id: str
    name: str
    email: Optional[str] = None
    password: str
    is_company_admin: bool = False
    role_ids: list[int] = []

class CreateRole(BaseModel):
    name: str
    description: Optional[str] = None
    feature_ids: list[int]

class UpdateRole(BaseModel):
    name: str
    description: Optional[str] = None
    feature_ids: list[int]


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
# HOME (DYNAMIC PERMISSIONS)
# =====================================
@app.get("/company/me")
def get_company_home(current=Depends(get_current_user)):
    conn = get_db()
    cur = conn.cursor()

    # ---- USER INFO ----
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

    row = cur.fetchone()
    if not row:
        cur.close()
        conn.close()
        raise HTTPException(status_code=404)

    emp_id, name, email, is_admin, company_name = row

    # ---- FEATURES RESOLUTION ----
    if is_admin:
        # Admin → all enabled company features
        cur.execute("""
            SELECT f.id, f.code, f.name
            FROM company_features cf
            JOIN features f ON f.id = cf.feature_id
            WHERE cf.company_id = %s AND cf.enabled = TRUE
        """, (current["company_id"],))
    else:
        # Normal user → roles → features (filtered by company_features)
        cur.execute("""
            SELECT DISTINCT f.id, f.code, f.name
            FROM user_roles ur
            JOIN roles r ON r.id = ur.role_id
            JOIN roles_features rf ON rf.role_id = r.id
            JOIN features f ON f.id = rf.feature_id
            JOIN company_features cf ON cf.feature_id = f.id
            WHERE ur.user_id = %s
              AND r.company_id = %s
              AND cf.enabled = TRUE
        """, (current["user_id"], current["company_id"]))

    features = cur.fetchall()
    feature_ids = [f[0] for f in features]

    # ---- PAGES FROM FEATURES ----
    pages = []
    if feature_ids:
        cur.execute("""
            SELECT DISTINCT page_code, page_name, route
            FROM feature_bundle_pages
            WHERE feature_id = ANY(%s)
            ORDER BY page_name
        """, (feature_ids,))
        pages = cur.fetchall()

    # ---- ROLES (ONLY FOR NON-ADMIN) ----
    roles = []
    if not is_admin:
        cur.execute("""
            SELECT r.name
            FROM user_roles ur
            JOIN roles r ON r.id = ur.role_id
            WHERE ur.user_id = %s
        """, (current["user_id"],))
        roles = [r[0] for r in cur.fetchall()]

    cur.close()
    conn.close()

    return {
        "user": {
            "emp_id": emp_id,
            "name": name,
            "email": email,
            "company": company_name,
            "is_company_admin": is_admin
        },
        "roles": roles,
        "features": [
            {"code": f[1], "name": f[2]} for f in features
        ],
        "pages": [
            {"code": p[0], "name": p[1], "route": p[2]} for p in pages
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
        SELECT 
            u.id, u.emp_id, u.name, u.email, u.status,
            u.is_company_admin,
            COALESCE(array_agg(r.name) FILTER (WHERE r.name IS NOT NULL), '{}')
        FROM users u
        LEFT JOIN user_roles ur ON ur.user_id = u.id
        LEFT JOIN roles r ON r.id = ur.role_id
        WHERE u.company_id = %s
        GROUP BY u.id
        ORDER BY u.created_at DESC
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
            "roles": u[6]
        }
        for u in users
    ]


@app.post("/company/users")
def add_user(data: CreateUserWithRoles, current=Depends(get_current_user)):
    if not current["is_company_admin"]:
        raise HTTPException(status_code=403)

    conn = get_db()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO users
        (company_id, emp_id, name, email, password_hash, is_company_admin)
        VALUES (%s, %s, %s, %s, %s, %s)
        RETURNING id
    """, (
        current["company_id"],
        data.emp_id,
        data.name,
        data.email,
        pwd_context.hash(data.password),
        data.is_company_admin
    ))

    user_id = cur.fetchone()[0]

    # Assign roles ONLY if not admin
    if not data.is_company_admin and data.role_ids:
        for role_id in data.role_ids:
            cur.execute("""
                INSERT INTO user_roles (user_id, role_id)
                VALUES (%s, %s)
            """, (user_id, role_id))

    conn.commit()
    cur.close()
    conn.close()

    return {"message": "User created successfully"}


@app.put("/company/users/{user_id}")
def update_user(
    user_id: int,
    data: UpdateUserWithRoles,
    current=Depends(get_current_user)
):
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

    # 🔴 IMPORTANT PART
    # Always reset roles
    cur.execute("DELETE FROM user_roles WHERE user_id = %s", (user_id,))

    # Reassign roles only if NOT admin
    if not data.is_company_admin:
        for role_id in data.role_ids:
            cur.execute("""
                INSERT INTO user_roles (user_id, role_id)
                VALUES (%s, %s)
            """, (user_id, role_id))

    conn.commit()
    cur.close()
    conn.close()

    return {"message": "User updated successfully"}


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

@app.get("/company/roles")
def list_roles(current=Depends(get_current_user)):
    if not current["is_company_admin"]:
        raise HTTPException(status_code=403)

    conn = get_db()
    cur = conn.cursor()

    cur.execute("""
        SELECT
            r.id,
            r.name,
            r.description,
            COALESCE(array_agg(f.code) FILTER (WHERE f.code IS NOT NULL), '{}') AS features
        FROM roles r
        LEFT JOIN roles_features rf ON rf.role_id = r.id
        LEFT JOIN features f ON f.id = rf.feature_id
        WHERE r.company_id = %s
        GROUP BY r.id
        ORDER BY r.name
    """, (current["company_id"],))

    rows = cur.fetchall()
    cur.close()
    conn.close()

    return [
        {
            "id": r[0],
            "name": r[1],
            "description": r[2],
            "features": r[3]
        }
        for r in rows
    ]

@app.post("/company/roles")
def create_role(data: CreateRole, current=Depends(get_current_user)):
    if not current["is_company_admin"]:
        raise HTTPException(status_code=403)

    conn = get_db()
    cur = conn.cursor()

    # Validate features belong to company subscription
    cur.execute("""
        SELECT feature_id
        FROM company_features
        WHERE company_id = %s AND enabled = TRUE
    """, (current["company_id"],))

    allowed_features = {r[0] for r in cur.fetchall()}

    if not set(data.feature_ids).issubset(allowed_features):
        cur.close()
        conn.close()
        raise HTTPException(
            status_code=400,
            detail="One or more features are not enabled for this company"
        )

    # Create role
    cur.execute("""
        INSERT INTO roles (company_id, name, description)
        VALUES (%s, %s, %s)
        RETURNING id
    """, (
        current["company_id"],
        data.name,
        data.description
    ))

    role_id = cur.fetchone()[0]

    # Assign features to role
    for feature_id in data.feature_ids:
        cur.execute("""
            INSERT INTO roles_features (role_id, feature_id)
            VALUES (%s, %s)
        """, (role_id, feature_id))

    conn.commit()
    cur.close()
    conn.close()

    return {"message": "Role created successfully"}

@app.put("/company/roles/{role_id}")
def update_role(role_id: int, data: UpdateRole, current=Depends(get_current_user)):
    if not current["is_company_admin"]:
        raise HTTPException(status_code=403)

    conn = get_db()
    cur = conn.cursor()

    # Ensure role belongs to company
    cur.execute("""
        SELECT id FROM roles
        WHERE id = %s AND company_id = %s
    """, (role_id, current["company_id"]))

    if not cur.fetchone():
        cur.close()
        conn.close()
        raise HTTPException(status_code=404, detail="Role not found")

    # Validate features
    cur.execute("""
        SELECT feature_id
        FROM company_features
        WHERE company_id = %s AND enabled = TRUE
    """, (current["company_id"],))

    allowed_features = {r[0] for r in cur.fetchall()}

    if not set(data.feature_ids).issubset(allowed_features):
        cur.close()
        conn.close()
        raise HTTPException(
            status_code=400,
            detail="Invalid feature assignment"
        )

    # Update role
    cur.execute("""
        UPDATE roles
        SET name = %s,
            description = %s
        WHERE id = %s
    """, (
        data.name,
        data.description,
        role_id
    ))

    # Reset role features
    cur.execute("DELETE FROM roles_features WHERE role_id = %s", (role_id,))

    for feature_id in data.feature_ids:
        cur.execute("""
            INSERT INTO roles_features (role_id, feature_id)
            VALUES (%s, %s)
        """, (role_id, feature_id))

    conn.commit()
    cur.close()
    conn.close()

    return {"message": "Role updated successfully"}

@app.delete("/company/roles/{role_id}")
def delete_role(role_id: int, current=Depends(get_current_user)):
    if not current["is_company_admin"]:
        raise HTTPException(status_code=403)

    conn = get_db()
    cur = conn.cursor()

    # Prevent deleting role in use
    cur.execute("""
        SELECT 1 FROM user_roles WHERE role_id = %s LIMIT 1
    """, (role_id,))

    if cur.fetchone():
        cur.close()
        conn.close()
        raise HTTPException(
            status_code=400,
            detail="Role is assigned to users"
        )

    cur.execute("""
        DELETE FROM roles
        WHERE id = %s AND company_id = %s
    """, (role_id, current["company_id"]))

    if cur.rowcount == 0:
        cur.close()
        conn.close()
        raise HTTPException(status_code=404)

    conn.commit()
    cur.close()
    conn.close()

    return {"message": "Role deleted successfully"}

@app.get("/company/feature-bundles")
def get_company_feature_bundles(current=Depends(get_current_user)):
    if not current["is_company_admin"]:
        raise HTTPException(status_code=403)

    conn = get_db()
    cur = conn.cursor()

    cur.execute("""
        SELECT f.id, f.code, f.name
        FROM company_features cf
        JOIN features f ON f.id = cf.feature_id
        WHERE cf.company_id = %s
          AND cf.enabled = TRUE
        ORDER BY f.name
    """, (current["company_id"],))

    rows = cur.fetchall()
    cur.close()
    conn.close()

    return [
        {
            "id": r[0],
            "code": r[1],
            "name": r[2]
        }
        for r in rows
    ]
