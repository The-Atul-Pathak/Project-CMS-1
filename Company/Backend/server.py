from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, timedelta, date
from jose import jwt
from passlib.context import CryptContext
import psycopg2
import os
from dotenv import load_dotenv
from pathlib import Path
from fastapi.staticfiles import StaticFiles


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
class UpdateUserProfile(BaseModel):

    phone: Optional[str] = None
    alternate_phone: Optional[str] = None

    address_line_1: Optional[str] = None
    address_line_2: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    postal_code: Optional[str] = None
    country: Optional[str] = None

    emergency_contact_name: Optional[str] = None
    emergency_contact_phone: Optional[str] = None
class ChangePassword(BaseModel):
    current_password: str
    new_password: str
class MarkAttendance(BaseModel):
    user_id: int
    date: date
    status: str

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

def get_user_roles(conn, user_id):
    cur = conn.cursor()
    cur.execute("""
        SELECT r.name
        FROM user_roles ur
        JOIN roles r ON r.id = ur.role_id
        WHERE ur.user_id = %s
    """, (user_id,))
    roles = [r[0] for r in cur.fetchall()]
    cur.close()
    return roles

def is_hr_or_admin(conn, user_id, is_company_admin):
    if is_company_admin:
        return True

    roles = get_user_roles(conn, user_id)
    return "HR" in roles

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
            "id": current["user_id"],
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

@app.get("/company/users/{user_id}/profile")
def get_employee_profile(
    user_id: int,
    current=Depends(get_current_user)
):
    conn = get_db()
    cur = conn.cursor()

    # ---- FETCH TARGET USER ----
    cur.execute("""
        SELECT 
            u.id,
            u.emp_id,
            u.name,
            u.email,
            u.status,
            u.is_company_admin,
            c.company_name
        FROM users u
        JOIN companies c ON c.id = u.company_id
        WHERE u.id = %s AND u.company_id = %s
    """, (user_id, current["company_id"]))

    user = cur.fetchone()
    if not user:
        cur.close()
        conn.close()
        raise HTTPException(status_code=404, detail="User not found")

    (
        target_id,
        emp_id,
        name,
        email,
        status,
        is_company_admin,
        company_name
    ) = user

    # ---- PROFILE DATA ----
    cur.execute("""
        SELECT
            phone,
            alternate_phone,
            address_line_1,
            address_line_2,
            city,
            state,
            postal_code,
            country,
            emergency_contact_name,
            emergency_contact_phone
        FROM user_profile_data
        WHERE user_id = %s AND company_id = %s
    """, (target_id, current["company_id"]))

    profile = cur.fetchone()


    # ---- VIEWER ROLES ----
    viewer_roles = get_user_roles(conn, current["user_id"])
    target_roles = get_user_roles(conn, target_id)

    is_self = current["user_id"] == target_id
    is_admin = current["is_company_admin"]
    is_hr = "HR" in viewer_roles

    # ---- PERMISSION CHECK ----
    if not (is_self or is_admin or is_hr):
        cur.close()
        conn.close()
        raise HTTPException(status_code=403, detail="Access denied")

    # ---- FEATURES RESOLUTION (TARGET USER) ----
    if is_company_admin:
        cur.execute("""
            SELECT f.code, f.name
            FROM company_features cf
            JOIN features f ON f.id = cf.feature_id
            WHERE cf.company_id = %s AND cf.enabled = TRUE
        """, (current["company_id"],))
    else:
        cur.execute("""
            SELECT DISTINCT f.code, f.name
            FROM user_roles ur
            JOIN roles r ON r.id = ur.role_id
            JOIN roles_features rf ON rf.role_id = r.id
            JOIN features f ON f.id = rf.feature_id
            JOIN company_features cf ON cf.feature_id = f.id
            WHERE ur.user_id = %s
              AND r.company_id = %s
              AND cf.enabled = TRUE
        """, (target_id, current["company_id"]))

    features = cur.fetchall()

    # ---- ACTIVITY SNAPSHOT (MINIMAL FOR NOW) ----
    cur.execute("""
        SELECT MAX(created_at)
        FROM user_sessions
        WHERE user_id = %s
    """, (target_id,))

    last_login = cur.fetchone()[0]

    cur.close()
    conn.close()

    return {
        "basic": {
            "id": target_id,
            "emp_id": emp_id,
            "name": name,
            "email": email,
            "company": company_name,
            "status": status,
            "is_company_admin": is_company_admin
        },
        "roles": target_roles,
        "features": [
            {"code": f[0], "name": f[1]} for f in features
        ],
        "activity": {
            "last_login": last_login
        },
        "permissions": {
            "can_edit": is_admin or is_hr,
            "can_edit_status": is_admin or is_hr
        },
        "profile": {
            "phone": profile[0] if profile else None,
            "alternate_phone": profile[1] if profile else None,
            "address": {
                "line1": profile[2] if profile else None,
                "line2": profile[3] if profile else None,
                "city": profile[4] if profile else None,
                "state": profile[5] if profile else None,
                "postal_code": profile[6] if profile else None,
                "country": profile[7] if profile else None
            },
            "emergency_contact": {
                "name": profile[8] if profile else None,
                "phone": profile[9] if profile else None
            }
        }

    }

@app.put("/company/users/me/profile")
def update_my_profile(
    data: UpdateUserProfile,
    current=Depends(get_current_user)
):
    conn = get_db()
    cur = conn.cursor()

    # Ensure profile row exists
    cur.execute("""
        SELECT id FROM user_profile_data
        WHERE user_id = %s AND company_id = %s
    """, (current["user_id"], current["company_id"]))

    exists = cur.fetchone()

    if not exists:
        cur.execute("""
            INSERT INTO user_profile_data (user_id, company_id)
            VALUES (%s, %s)
        """, (current["user_id"], current["company_id"]))

    # Update profile
    cur.execute("""
        UPDATE user_profile_data
        SET
            phone = %s,
            alternate_phone = %s,
            address_line_1 = %s,
            address_line_2 = %s,
            city = %s,
            state = %s,
            postal_code = %s,
            country = %s,
            emergency_contact_name = %s,
            emergency_contact_phone = %s,
            updated_at = CURRENT_TIMESTAMP
        WHERE user_id = %s AND company_id = %s
    """, (
        data.phone,
        data.alternate_phone,
        data.address_line_1,
        data.address_line_2,
        data.city,
        data.state,
        data.postal_code,
        data.country,
        data.emergency_contact_name,
        data.emergency_contact_phone,
        current["user_id"],
        current["company_id"]
    ))

    conn.commit()
    cur.close()
    conn.close()

    return {"message": "Profile updated successfully"}

@app.put("/company/users/me/password")
def change_my_password(
    data: ChangePassword,
    current=Depends(get_current_user)
):
    conn = get_db()
    cur = conn.cursor()

    # Fetch current password hash
    cur.execute("""
        SELECT password_hash
        FROM users
        WHERE id = %s AND company_id = %s
    """, (current["user_id"], current["company_id"]))

    row = cur.fetchone()
    if not row:
        cur.close()
        conn.close()
        raise HTTPException(status_code=404)

    password_hash = row[0]

    # Verify old password
    if not verify_password(data.current_password, password_hash):
        cur.close()
        conn.close()
        raise HTTPException(status_code=400, detail="Incorrect current password")

    # Update password
    new_hash = pwd_context.hash(data.new_password)

    cur.execute("""
        UPDATE users
        SET password_hash = %s
        WHERE id = %s AND company_id = %s
    """, (new_hash, current["user_id"], current["company_id"]))

    conn.commit()
    cur.close()
    conn.close()

    return {"message": "Password updated successfully"}

@app.get("/company/attendance")
def get_attendance(date: date, current=Depends(get_current_user)):
    conn = get_db()
    cur = conn.cursor()

    if not is_hr_or_admin(conn, current["user_id"], current["is_company_admin"]):
        cur.close()
        conn.close()
        raise HTTPException(status_code=403, detail="Access denied")

    cur.execute("""
        SELECT
            u.id,
            u.emp_id,
            u.name,
            COALESCE(a.status, 'Unmarked') AS status,
            a.marked_by
        FROM users u
        LEFT JOIN attendance a
          ON a.user_id = u.id
         AND a.date = %s
         AND a.company_id = %s
        WHERE u.company_id = %s
          AND u.status = 'active'
        ORDER BY u.emp_id
    """, (date, current["company_id"], current["company_id"]))

    rows = cur.fetchall()

    cur.close()
    conn.close()

    return [
        {
            "user_id": r[0],
            "emp_id": r[1],
            "name": r[2],
            "status": r[3],
            "marked_by": r[4]
        }
        for r in rows
    ]

@app.post("/company/attendance")
def mark_attendance(data: MarkAttendance, current=Depends(get_current_user)):
    conn = get_db()
    cur = conn.cursor()

    if not is_hr_or_admin(conn, current["user_id"], current["is_company_admin"]):
        cur.close()
        conn.close()
        raise HTTPException(status_code=403)

    cur.execute("""
        INSERT INTO attendance
            (company_id, user_id, date, status, marked_by, marked_at)
        VALUES (%s, %s, %s, %s, %s, CURRENT_TIMESTAMP)
        ON CONFLICT (company_id, user_id, date)
        DO UPDATE SET
            status = EXCLUDED.status,
            marked_by = EXCLUDED.marked_by,
            marked_at = CURRENT_TIMESTAMP
    """, (
        current["company_id"],
        data.user_id,
        data.date,
        data.status,
        current["user_id"]
    ))

    conn.commit()
    cur.close()
    conn.close()

    return {"message": "Attendance updated"}

@app.get("/company/attendance/summary")
def attendance_summary(date: date, current=Depends(get_current_user)):
    conn = get_db()
    cur = conn.cursor()

    if not is_hr_or_admin(conn, current["user_id"], current["is_company_admin"]):
        cur.close()
        conn.close()
        raise HTTPException(status_code=403)

    cur.execute("""
        SELECT status, COUNT(*)
        FROM attendance
        WHERE company_id = %s AND date = %s
        GROUP BY status
    """, (current["company_id"], date))

    counts = {r[0]: r[1] for r in cur.fetchall()}

    cur.execute("""
        SELECT COUNT(*)
        FROM users
        WHERE company_id = %s AND status = 'active'
    """, (current["company_id"],))

    total = cur.fetchone()[0]

    cur.close()
    conn.close()

    return {
        "present": counts.get("Present", 0),
        "absent": counts.get("Absent", 0),
        "leave": counts.get("Leave", 0),
        "total_employees": total
    }

@app.get("/company/attendance/user/{user_id}/summary")
def employee_attendance_summary(
    user_id: int,
    month: str,   # YYYY-MM
    current=Depends(get_current_user)
):
    conn = get_db()
    cur = conn.cursor()

    if not (
        is_hr_or_admin(conn, current["user_id"], current["is_company_admin"])
        or current["user_id"] == user_id
    ):
        cur.close()
        conn.close()
        raise HTTPException(status_code=403)


    cur.execute("""
        SELECT status, COUNT(*)
        FROM attendance
        WHERE company_id = %s
          AND user_id = %s
          AND TO_CHAR(date, 'YYYY-MM') = %s
        GROUP BY status
    """, (current["company_id"], user_id, month))

    counts = {r[0]: r[1] for r in cur.fetchall()}

    present = counts.get("Present", 0)
    absent = counts.get("Absent", 0)
    leave = counts.get("Leave", 0)
    total = present + absent + leave

    cur.close()
    conn.close()

    return {
        "present": present,
        "absent": absent,
        "leave": leave,
        "attendance_percentage": round((present / total) * 100, 2) if total else 0
    }

@app.get("/company/attendance/user/{user_id}")
def employee_attendance_records(
    user_id: int,
    month: str,
    current=Depends(get_current_user)
):
    conn = get_db()
    cur = conn.cursor()

    if not (
        is_hr_or_admin(conn, current["user_id"], current["is_company_admin"])
        or current["user_id"] == user_id
    ):
        cur.close()
        conn.close()
        raise HTTPException(status_code=403)


    cur.execute("""
        SELECT date, status, marked_by, marked_at
        FROM attendance
        WHERE company_id = %s
          AND user_id = %s
          AND TO_CHAR(date, 'YYYY-MM') = %s
        ORDER BY date DESC
    """, (current["company_id"], user_id, month))

    rows = cur.fetchall()
    cur.close()
    conn.close()

    return [
        {
            "date": r[0],
            "status": r[1],
            "marked_by": r[2],
            "marked_at": r[3]
        }
        for r in rows
    ]


BASE_DIR = Path(__file__).resolve().parent.parent
FRONTEND_DIR = BASE_DIR / "Frontend"

app.mount("/", StaticFiles(directory=FRONTEND_DIR, html=True), name="frontend")