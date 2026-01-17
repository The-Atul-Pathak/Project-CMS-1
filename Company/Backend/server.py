from fastapi import FastAPI, Depends, HTTPException, Request, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from typing import Optional, List
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

class ApplyLeave(BaseModel):
    leave_type: str
    start_date: date
    end_date: date
    reason: Optional[str] = None

class ReviewLeave(BaseModel):
    status: str   # Approved | Rejected
    review_notes: Optional[str] = None

class TeamCreate(BaseModel):
    name: str
    description: Optional[str] = None
    manager_id: Optional[int] = None
    member_ids: List[int] = []

class TeamUpdate(BaseModel):
    name: str
    description: Optional[str] = None
    manager_id: Optional[int] = None
    member_ids: List[int] = []

class LeadCreate(BaseModel):
    client_name: str
    contact_email: Optional[str] = None
    contact_phone: Optional[str] = None
    source: Optional[str] = None
    assigned_user_id: int
    next_follow_up_date: Optional[date] = None
    notes: Optional[str] = None

class LeadUpdate(BaseModel):
    status: Optional[str] = None
    assigned_user_id: Optional[int] = None
    next_follow_up_date: Optional[date] = None
    notes: Optional[str] = None

class LeadInteractionCreate(BaseModel):
    interaction_type: str
    description: str
    interaction_at: Optional[datetime] = None

class AssignTeamPayload(BaseModel):
    team_id: int

class CreateProjectPlanning(BaseModel):
    planned_start_date: date
    planned_end_date: date
    description: str
    scope: Optional[str] = None

    milestones: Optional[list] = []
    deliverables: Optional[list] = []

    estimated_budget: Optional[float] = None
    priority: Optional[str] = None

    client_requirements: Optional[str] = None
    risk_notes: Optional[str] = None
    assumptions: Optional[str] = None
    dependencies: Optional[str] = None

    client_review_checkpoints: Optional[list] = []
    internal_notes: Optional[str] = None

class ClientConfirmation(BaseModel):
    client_name: str
    confirmation_notes: Optional[str] = None


class CreateTask(BaseModel):
    title: str
    description: Optional[str] = None
    assigned_to: Optional[int] = None
    start_date: Optional[date] = None
    due_date: Optional[date] = None
    estimated_effort_hours: Optional[int] = None
    cost_impact: Optional[float] = None
    priority: Optional[str] = None
    dependency_task_id: Optional[int] = None

class UpdateTaskStatus(BaseModel):
    status: str  # In Progress | Review | Blocked
    note: Optional[str] = None

class ApproveTask(BaseModel):
    approve: bool



# =====================================
# AUTH DEPENDENCY
# =====================================
def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    token = credentials.credentials
    payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])

    try:
        user_id = int(payload.get("sub"))
        company_id = int(payload.get("cid")) # Good practice to cast this too
    except (ValueError, TypeError):
        raise HTTPException(status_code=401, detail="Invalid token payload")

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

def get_project_and_role(conn, project_id, current):
    cur = conn.cursor()

    # Project + Team + Leader
    cur.execute("""
        SELECT 
            p.id,
            p.status,
            t.manager_id
        FROM projects p
        JOIN teams t ON t.id = p.assigned_team_id
        WHERE p.id = %s AND p.company_id = %s
    """, (project_id, current["company_id"]))

    row = cur.fetchone()
    if not row:
        cur.close()
        raise HTTPException(status_code=404, detail="Project not found")

    project_id, status, leader_id = row

    is_leader = (leader_id == current["user_id"])
    is_admin = current["is_company_admin"]

    cur.close()
    return status, is_leader, is_admin

def get_task_and_project(conn, task_id, current):
    cur = conn.cursor()

    cur.execute("""
        SELECT
            t.id,
            t.status,
            t.assigned_to,
            p.id,
            p.status,
            tm.manager_id
        FROM project_tasks t
        JOIN projects p ON p.id = t.project_id
        JOIN teams tm ON tm.id = p.assigned_team_id
        WHERE t.id = %s AND t.company_id = %s
    """, (task_id, current["company_id"]))

    row = cur.fetchone()
    if not row:
        cur.close()
        raise HTTPException(status_code=404, detail="Task not found")

    (
        task_id,
        task_status,
        assigned_to,
        project_id,
        project_status,
        leader_id
    ) = row

    is_leader = (leader_id == current["user_id"])
    is_assignee = (assigned_to == current["user_id"])
    is_admin = current["is_company_admin"]

    cur.close()
    return task_status, project_status, is_leader, is_assignee, is_admin


# ===============================================================
# ===============================================================
# ===============================================================
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

@app.post("/company/leaves")
def apply_leave(
    data: ApplyLeave,
    current=Depends(get_current_user)
):
    conn = get_db()
    cur = conn.cursor()

    # Basic validation
    if data.end_date < data.start_date:
        cur.close()
        conn.close()
        raise HTTPException(status_code=400, detail="Invalid date range")

    # Calculate total days (simple version)
    total_days = (data.end_date - data.start_date).days + 1

    cur.execute("""
        INSERT INTO leave_requests (
            company_id,
            user_id,
            leave_type,
            start_date,
            end_date,
            total_days,
            reason,
            status
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, 'Pending')
    """, (
        current["company_id"],
        current["user_id"],
        data.leave_type,
        data.start_date,
        data.end_date,
        total_days,
        data.reason
    ))

    conn.commit()
    cur.close()
    conn.close()

    return {"message": "Leave request submitted"}

@app.get("/company/leaves/me")
def get_my_leaves(current=Depends(get_current_user)):
    conn = get_db()
    cur = conn.cursor()

    cur.execute("""
        SELECT
            lr.id,
            lr.leave_type,
            lr.start_date,
            lr.end_date,
            lr.total_days,
            lr.status,
            lr.applied_at,
            lr.review_notes,
            lr.reviewed_at,
            u.name AS reviewed_by_name
        FROM leave_requests lr
        LEFT JOIN users u ON u.id = lr.reviewed_by
        WHERE lr.company_id = %s
        AND lr.user_id = %s
        ORDER BY lr.applied_at DESC
    """, (current["company_id"], current["user_id"]))

    rows = cur.fetchall()
    cur.close()
    conn.close()

    return [
        {
            "id": r[0],
            "leave_type": r[1],
            "start_date": r[2],
            "end_date": r[3],
            "total_days": r[4],
            "status": r[5],
            "applied_at": r[6],
            "review_notes": r[7],
            "reviewed_at": r[8],
            "reviewed_by": r[9]
        }
        for r in rows
    ]

@app.put("/company/leaves/{leave_id}/cancel")
def cancel_my_leave(
    leave_id: int,
    current=Depends(get_current_user)
):
    conn = get_db()
    cur = conn.cursor()

    cur.execute("""
        UPDATE leave_requests
        SET status = 'Cancelled'
        WHERE id = %s
          AND company_id = %s
          AND user_id = %s
          AND status = 'Pending'
    """, (
        leave_id,
        current["company_id"],
        current["user_id"]
    ))

    if cur.rowcount == 0:
        cur.close()
        conn.close()
        raise HTTPException(
            status_code=400,
            detail="Leave cannot be cancelled"
        )

    conn.commit()
    cur.close()
    conn.close()

    return {"message": "Leave cancelled"}

@app.get("/company/leaves")
def get_all_leaves(
    status: Optional[str] = None,
    current=Depends(get_current_user)
):
    conn = get_db()
    cur = conn.cursor()

    query = """
        SELECT
            lr.id,
            u.id AS user_id,
            u.emp_id,
            u.name,
            lr.leave_type,
            lr.start_date,
            lr.end_date,
            lr.total_days,
            lr.reason,
            lr.status,
            lr.applied_at
        FROM leave_requests lr
        JOIN users u ON u.id = lr.user_id
        WHERE lr.company_id = %s
    """
    params = [current["company_id"]]

    if status:
        query += " AND lr.status = %s"
        params.append(status)

    query += " ORDER BY lr.applied_at DESC"

    cur.execute(query, params)
    rows = cur.fetchall()

    cur.close()
    conn.close()

    return [
        {
            "leave_id": r[0],
            "user_id": r[1],
            "emp_id": r[2],
            "name": r[3],
            "leave_type": r[4],
            "start_date": r[5],
            "end_date": r[6],
            "total_days": r[7],
            "reason": r[8],
            "status": r[9],
            "applied_at": r[10]
        }
        for r in rows
    ]

@app.get("/company/leaves/{leave_id}")
def get_leave_detail(
    leave_id: int,
    current=Depends(get_current_user)
):
    conn = get_db()
    cur = conn.cursor()

    cur.execute("""
        SELECT
            lr.id,
            u.id AS user_id,
            u.emp_id,
            u.name,
            lr.leave_type,
            lr.start_date,
            lr.end_date,
            lr.total_days,
            lr.reason,
            lr.status,
            lr.applied_at,
            lr.reviewed_by,
            lr.reviewed_at,
            lr.review_notes
        FROM leave_requests lr
        JOIN users u ON u.id = lr.user_id
        WHERE lr.id = %s
          AND lr.company_id = %s
    """, (leave_id, current["company_id"]))

    row = cur.fetchone()

    if not row:
        cur.close()
        conn.close()
        raise HTTPException(status_code=404, detail="Leave request not found")

    cur.close()
    conn.close()

    return {
        "leave_id": row[0],
        "user_id": row[1],
        "emp_id": row[2],
        "name": row[3],
        "leave_type": row[4],
        "start_date": row[5],
        "end_date": row[6],
        "total_days": row[7],
        "reason": row[8],
        "status": row[9],
        "applied_at": row[10],
        "reviewed_by": row[11],
        "reviewed_at": row[12],
        "review_notes": row[13]
    }

@app.put("/company/leaves/{leave_id}/review")
def review_leave(
    leave_id: int,
    data: ReviewLeave,
    current=Depends(get_current_user)
):
    if data.status not in ("Approved", "Rejected"):
        raise HTTPException(status_code=400, detail="Invalid status")

    conn = get_db()
    cur = conn.cursor()

    # Fetch leave (must be Pending)
    cur.execute("""
        SELECT user_id, start_date, end_date, status
        FROM leave_requests
        WHERE id = %s
          AND company_id = %s
    """, (leave_id, current["company_id"]))

    row = cur.fetchone()

    if not row:
        cur.close()
        conn.close()
        raise HTTPException(status_code=404, detail="Leave not found")

    user_id, start_date, end_date, current_status = row

    if current_status != "Pending":
        cur.close()
        conn.close()
        raise HTTPException(
            status_code=400,
            detail="Leave already reviewed"
        )

    # Update leave status
    cur.execute("""
        UPDATE leave_requests
        SET
            status = %s,
            reviewed_by = %s,
            reviewed_at = CURRENT_TIMESTAMP,
            review_notes = %s
        WHERE id = %s
    """, (
        data.status,
        current["user_id"],
        data.review_notes,
        leave_id
    ))

    # ✅ If approved → mark attendance as Leave
    if data.status == "Approved":
        current_date = start_date
        while current_date <= end_date:
            cur.execute("""
                INSERT INTO attendance (
                    company_id,
                    user_id,
                    date,
                    status,
                    marked_by,
                    marked_at
                )
                VALUES (%s, %s, %s, 'Leave', %s, CURRENT_TIMESTAMP)
                ON CONFLICT (company_id, user_id, date)
                DO UPDATE SET
                    status = 'Leave',
                    marked_by = EXCLUDED.marked_by,
                    marked_at = CURRENT_TIMESTAMP
            """, (
                current["company_id"],
                user_id,
                current_date,
                current["user_id"]
            ))
            current_date += timedelta(days=1)

    conn.commit()
    cur.close()
    conn.close()

    return {"message": f"Leave {data.status.lower()} successfully"}

@app.get("/company/teams")
def get_teams(current=Depends(get_current_user)):
    conn = get_db()
    cur = conn.cursor()

    cur.execute("""
        SELECT 
            t.id,
            t.name,
            t.description,
            t.manager_id,
            u.name AS manager_name,
            t.status,
            COUNT(tm.user_id) AS member_count
        FROM teams t
        LEFT JOIN users u ON u.id = t.manager_id
        LEFT JOIN team_members tm ON tm.team_id = t.id
        WHERE t.company_id = %s
        GROUP BY t.id, u.name
        ORDER BY t.created_at DESC
    """, (current["company_id"],))

    rows = cur.fetchall()

    cur.close()
    conn.close()

    return [
        {
            "id": r[0],
            "name": r[1],
            "description": r[2],
            "manager_id": r[3],
            "manager_name": r[4],
            "status": r[5],
            "member_count": r[6]
        }
        for r in rows
    ]

@app.post("/company/teams")
def create_team(
    data: TeamCreate,
    current=Depends(get_current_user)
):
    conn = get_db()
    cur = conn.cursor()

    try:
        cur.execute("""
            INSERT INTO teams (company_id, name, description, manager_id)
            VALUES (%s, %s, %s, %s)
            RETURNING id
        """, (
            current["company_id"],
            data.name,
            data.description,
            data.manager_id
        ))

        team_id = cur.fetchone()[0]

        for user_id in data.member_ids:
            cur.execute("""
                INSERT INTO team_members (team_id, user_id)
                VALUES (%s, %s)
                ON CONFLICT DO NOTHING
            """, (team_id, user_id))

        conn.commit()

    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=400, detail=str(e))

    finally:
        cur.close()
        conn.close()

    return {"message": "Team created", "team_id": team_id}

@app.get("/company/teams/{team_id}")
def get_team(
    team_id: int,
    current=Depends(get_current_user)
):
    conn = get_db()
    cur = conn.cursor()

    cur.execute("""
        SELECT id, name, description, manager_id, status
        FROM teams
        WHERE id = %s AND company_id = %s
    """, (team_id, current["company_id"]))

    team = cur.fetchone()

    if not team:
        cur.close()
        conn.close()
        raise HTTPException(status_code=404, detail="Team not found")

    cur.execute("""
        SELECT u.id, u.name
        FROM team_members tm
        JOIN users u ON u.id = tm.user_id
        WHERE tm.team_id = %s
    """, (team_id,))

    members = cur.fetchall()

    cur.close()
    conn.close()

    return {
        "id": team[0],
        "name": team[1],
        "description": team[2],
        "manager_id": team[3],
        "status": team[4],
        "members": [
            {"user_id": m[0], "name": m[1]} for m in members
        ]
    }

@app.put("/company/teams/{team_id}")
def update_team(
    team_id: int,
    data: TeamUpdate,
    current=Depends(get_current_user)
):
    conn = get_db()
    cur = conn.cursor()

    cur.execute("""
        UPDATE teams
        SET name = %s,
            description = %s,
            manager_id = %s,
            updated_at = CURRENT_TIMESTAMP
        WHERE id = %s AND company_id = %s
    """, (
        data.name,
        data.description,
        data.manager_id,
        team_id,
        current["company_id"]
    ))

    cur.execute("DELETE FROM team_members WHERE team_id = %s", (team_id,))

    for user_id in data.member_ids:
        cur.execute("""
            INSERT INTO team_members (team_id, user_id)
            VALUES (%s, %s)
        """, (team_id, user_id))

    conn.commit()
    cur.close()
    conn.close()

    return {"message": "Team updated"}

@app.delete("/company/teams/{team_id}")
def archive_team(
    team_id: int,
    current=Depends(get_current_user)
):
    conn = get_db()
    cur = conn.cursor()

    cur.execute("""
        UPDATE teams
        SET status = 'Archived',
            updated_at = CURRENT_TIMESTAMP
        WHERE id = %s AND company_id = %s
    """, (team_id, current["company_id"]))

    conn.commit()
    cur.close()
    conn.close()

    return {"message": "Team archived"}

@app.post("/sales/leads")
def create_lead(
    data: LeadCreate,
    user=Depends(get_current_user)
):
    conn = get_db()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO leads (
            company_id,
            client_name,
            contact_email,
            contact_phone,
            source,
            notes,
            assigned_employee_id,
            created_by_user_id,
            next_follow_up_date
        )
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)
        RETURNING id
    """, (
        user["company_id"],
        data.client_name,
        data.contact_email,
        data.contact_phone,
        data.source,
        data.notes,
        data.assigned_user_id,
        user["user_id"],
        data.next_follow_up_date
    ))


    lead_id = cur.fetchone()[0]
    conn.commit()
    cur.close()
    conn.close()

    return {"lead_id": lead_id}

@app.get("/sales/leads")
def get_all_leads(user=Depends(get_current_user)):
    conn = get_db()
    cur = conn.cursor()

    cur.execute("""
        SELECT
            l.id,
            l.client_name,
            l.contact_email,
            l.contact_phone,
            l.status,
            l.next_follow_up_date,
            l.last_interaction_at,
            u.name
        FROM leads l
        JOIN users u ON u.id = l.assigned_employee_id
        WHERE l.company_id = %s
        ORDER BY l.created_at DESC
    """, (user["company_id"],))


    rows = cur.fetchall()
    cur.close()
    conn.close()

    return rows

@app.get("/sales/leads/today")
def todays_followups(user=Depends(get_current_user)):
    conn = get_db()
    cur = conn.cursor()

    cur.execute("""
        SELECT
            id,
            client_name,
            status,
            next_follow_up_date,
            last_interaction_at
        FROM leads
        WHERE company_id = %s
        AND assigned_employee_id = %s
        AND next_follow_up_date = CURRENT_DATE
    """, (
        user["company_id"],
        user["user_id"]
    ))


    data = cur.fetchall()
    cur.close()
    conn.close()

    return data

@app.put("/sales/leads/{lead_id}")
def update_lead(
    lead_id: int,
    data: LeadUpdate,
    user=Depends(get_current_user)
):
    conn = get_db()
    cur = conn.cursor()

    # Fetch current lead state
    cur.execute("""
        SELECT status, project_created
        FROM leads
        WHERE id = %s
    """, (lead_id,))
    lead = cur.fetchone()

    if not lead:
        cur.close()
        conn.close()
        raise HTTPException(status_code=404, detail="Lead not found")

    current_status, project_created = lead

    fields = []
    values = []

    if data.status:
        fields.append("status = %s")
        values.append(data.status)

    if data.assigned_user_id:
        fields.append("assigned_employee_id = %s")
        values.append(data.assigned_user_id)

    if data.next_follow_up_date is not None:
        fields.append("next_follow_up_date = %s")
        values.append(data.next_follow_up_date)

    if data.notes is not None:
        fields.append("notes = %s")
        values.append(data.notes)

    if fields:
        values.append(lead_id)
        cur.execute(f"""
            UPDATE leads
            SET {', '.join(fields)}, updated_at = CURRENT_TIMESTAMP
            WHERE id = %s
        """, tuple(values))

    # 🎯 CREATE PROJECT IF LEAD IS WON
    if (
        data.status == "Won"
        and current_status != "Won"
        and not project_created
    ):
        cur.execute("""
            INSERT INTO projects (
                company_id,
                lead_id,
                project_name
            )
            SELECT company_id, id, client_name
            FROM leads
            WHERE id = %s
        """, (lead_id,))

        cur.execute("""
            UPDATE leads
            SET project_created = TRUE
            WHERE id = %s
        """, (lead_id,))

    conn.commit()
    cur.close()
    conn.close()

    return {"status": "updated"}

@app.post("/sales/leads/{lead_id}/interactions")
def log_interaction(
    lead_id: int,
    data: LeadInteractionCreate,
    user=Depends(get_current_user)
):
    conn = get_db()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO lead_interactions (
            lead_id,
            interaction_type,
            description,
            logged_by_employee_id,
            interaction_at
        )
        VALUES (%s,%s,%s,%s,%s)
    """, (
        lead_id,
        data.interaction_type,
        data.description,
        user["user_id"],
        data.interaction_at or datetime.utcnow()
    ))

    cur.execute("""
        UPDATE leads
        SET last_interaction_at = CURRENT_TIMESTAMP
        WHERE id = %s
    """, (lead_id,))

    conn.commit()
    cur.close()
    conn.close()

    return {"status": "interaction logged"}

@app.get("/sales/leads/{lead_id}/interactions")
def get_lead_interactions(
    lead_id: int,
    user=Depends(get_current_user)
):
    conn = get_db()
    cur = conn.cursor()

    cur.execute("""
        SELECT
            interaction_type,
            description,
            interaction_at,
            u.name
        FROM lead_interactions li
        JOIN users u ON u.id = li.logged_by_employee_id
        WHERE li.lead_id = %s
        ORDER BY interaction_at DESC
    """, (lead_id,))

    data = cur.fetchall()
    cur.close()
    conn.close()

    return data

@app.get("/company/projects/unassigned")
def get_unassigned_projects(current=Depends(get_current_user)):
    conn = get_db()
    cur = conn.cursor()

    cur.execute("""
        SELECT
            p.id,
            p.project_name,
            l.id AS lead_id,
            l.client_name,
            u.name AS sales_owner,
            l.notes,
            p.created_at
        FROM projects p
        JOIN leads l ON l.id = p.lead_id
        JOIN users u ON u.id = l.assigned_employee_id
        WHERE p.company_id = %s
          AND p.status = 'Unassigned'
        ORDER BY p.created_at ASC
    """, (current["company_id"],))

    rows = cur.fetchall()
    cur.close()
    conn.close()

    return [
        {
            "project_id": r[0],
            "project_name": r[1],
            "lead_id": r[2],
            "client_name": r[3],
            "sales_owner": r[4],
            "notes": r[5],
            "created_at": r[6]
        }
        for r in rows
    ]

@app.post("/company/projects/{project_id}/assign-team")
def assign_team_to_project(
    project_id: int,
    data: AssignTeamPayload,
    current=Depends(get_current_user)
):
    conn = get_db()
    cur = conn.cursor()

    # Ensure project belongs to company and is unassigned
    cur.execute("""
        SELECT id
        FROM projects
        WHERE id = %s
          AND company_id = %s
          AND status = 'Unassigned'
    """, (project_id, current["company_id"]))

    if not cur.fetchone():
        cur.close()
        conn.close()
        raise HTTPException(status_code=404, detail="Project not available for assignment")

    # Assign team
    cur.execute("""
        UPDATE projects
        SET assigned_team_id = %s,
            status = 'Assigned',
            updated_at = CURRENT_TIMESTAMP
        WHERE id = %s
    """, (data.team_id, project_id))

    conn.commit()
    cur.close()
    conn.close()

    return {"message": "Team assigned to project"}

@app.get("/company/teams/{team_id}/details")
def get_team_details(team_id: int, current=Depends(get_current_user)):
    conn = get_db()
    cur = conn.cursor()

    # 1️⃣ Get Team Info + Manager
    cur.execute("""
        SELECT
            t.id,
            t.name,
            t.description,
            u.name AS manager_name
        FROM teams t
        LEFT JOIN users u ON u.id = t.manager_id
        WHERE t.id = %s
          AND t.company_id = %s
    """, (team_id, current["company_id"]))

    team = cur.fetchone()

    if not team:
        cur.close()
        conn.close()
        raise HTTPException(status_code=404, detail="Team not found")

    team_info = {
        "id": team[0],
        "name": team[1],
        "description": team[2],
        "manager_name": team[3]
    }

    # 2️⃣ Get Team Members
    cur.execute("""
        SELECT
            u.id,
            u.name,
            u.email
        FROM team_members tm
        JOIN users u ON u.id = tm.user_id
        WHERE tm.team_id = %s
    """, (team_id,))

    members = [
        {
            "id": r[0],
            "name": r[1],
            "email": r[2]
        }
        for r in cur.fetchall()
    ]

    # 3️⃣ Get Projects Assigned to This Team
    cur.execute("""
        SELECT
            p.id,
            p.project_name,
            l.client_name,
            p.status,
            p.created_at
        FROM projects p
        LEFT JOIN leads l ON l.id = p.lead_id
        WHERE p.assigned_team_id = %s
          AND p.company_id = %s
    """, (team_id, current["company_id"]))

    projects = [
        {
            "id": r[0],
            "project_name": r[1],
            "client_name": r[2],
            "status": r[3],
            "created_at": r[4]
        }
        for r in cur.fetchall()
    ]

    cur.close()
    conn.close()

    return {
        "team": team_info,
        "members": members,
        "projects": projects
    }

@app.get("/projects")
def list_projects(current=Depends(get_current_user)):
    conn = get_db()
    cur = conn.cursor()

    cur.execute("""
        SELECT
            p.id,
            p.project_name,
            p.status,
            t.name AS team_name,
            u.name AS leader_name
        FROM projects p
        JOIN teams t ON t.id = p.assigned_team_id
        JOIN users u ON u.id = t.manager_id
        WHERE p.company_id = %s
        ORDER BY p.created_at DESC
    """, (current["company_id"],))

    projects = cur.fetchall()
    cur.close()
    conn.close()

    return [
        {
            "id": p[0],
            "project_name": p[1],
            "status": p[2],
            "team": p[3],
            "leader": p[4]
        }
        for p in projects
    ]

@app.get("/projects/{project_id}")
def get_project_details(project_id: int, current=Depends(get_current_user)):
    conn = get_db()
    cur = conn.cursor()

    cur.execute("""
        SELECT
            p.id,
            p.project_name,
            p.status,
            t.name,
            u.name
        FROM projects p
        JOIN teams t ON t.id = p.assigned_team_id
        JOIN users u ON u.id = t.manager_id
        WHERE p.id = %s AND p.company_id = %s
    """, (project_id, current["company_id"]))

    project = cur.fetchone()
    if not project:
        cur.close()
        conn.close()
        raise HTTPException(status_code=404)

    cur.execute("""
        SELECT
            planned_start_date,
            planned_end_date,
            description,
            scope,
            milestones,
            deliverables,
            estimated_budget,
            priority,
            client_requirements,
            risk_notes,
            assumptions,
            dependencies,
            client_review_checkpoints,
            internal_notes
        FROM project_planning
        WHERE project_id = %s
    """, (project_id,))

    planning = cur.fetchone()

    cur.close()
    conn.close()

    return {
        "project": {
            "id": project[0],
            "name": project[1],
            "status": project[2],
            "team": project[3],
            "leader": project[4]
        },
        "planning": planning
    }

@app.post("/projects/{project_id}/planning")
def save_project_planning(
    project_id: int,
    data: CreateProjectPlanning,
    current=Depends(get_current_user)
):
    conn = get_db()

    status, is_leader, is_admin = get_project_and_role(conn, project_id, current)

    if not is_leader:
        raise HTTPException(status_code=403, detail="Only leader can plan project")

    if status not in ["Assigned", "Planned"]:
        raise HTTPException(status_code=400, detail="Planning is locked")

    cur = conn.cursor()

    cur.execute("""
        INSERT INTO project_planning (
            project_id, company_id,
            planned_start_date, planned_end_date,
            description, scope,
            milestones, deliverables,
            estimated_budget, priority,
            client_requirements, risk_notes,
            assumptions, dependencies,
            client_review_checkpoints, internal_notes
        )
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
        ON CONFLICT (project_id) DO UPDATE SET
            planned_start_date = EXCLUDED.planned_start_date,
            planned_end_date = EXCLUDED.planned_end_date,
            description = EXCLUDED.description,
            scope = EXCLUDED.scope,
            milestones = EXCLUDED.milestones,
            deliverables = EXCLUDED.deliverables,
            estimated_budget = EXCLUDED.estimated_budget,
            priority = EXCLUDED.priority,
            client_requirements = EXCLUDED.client_requirements,
            risk_notes = EXCLUDED.risk_notes,
            assumptions = EXCLUDED.assumptions,
            dependencies = EXCLUDED.dependencies,
            client_review_checkpoints = EXCLUDED.client_review_checkpoints,
            internal_notes = EXCLUDED.internal_notes,
            updated_at = CURRENT_TIMESTAMP
    """, (
        project_id,
        current["company_id"],
        data.planned_start_date,
        data.planned_end_date,
        data.description,
        data.scope,
        data.milestones,
        data.deliverables,
        data.estimated_budget,
        data.priority,
        data.client_requirements,
        data.risk_notes,
        data.assumptions,
        data.dependencies,
        data.client_review_checkpoints,
        data.internal_notes
    ))

    cur.execute("""
        UPDATE projects
        SET status = 'Planned'
        WHERE id = %s
    """, (project_id,))

    conn.commit()
    cur.close()
    conn.close()

    return {"message": "Project planning saved"}

@app.post("/projects/{project_id}/start")
def start_project(project_id: int, current=Depends(get_current_user)):
    conn = get_db()

    status, is_leader, _ = get_project_and_role(conn, project_id, current)

    if not is_leader:
        raise HTTPException(status_code=403)

    if status != "Planned":
        raise HTTPException(status_code=400, detail="Project must be planned first")

    cur = conn.cursor()

    cur.execute("""
        UPDATE projects
        SET status = 'In Progress', updated_at = CURRENT_TIMESTAMP
        WHERE id = %s
    """, (project_id,))

    cur.execute("""
        INSERT INTO project_status_logs
        (project_id, company_id, old_status, new_status, changed_by)
        VALUES (%s,%s,%s,%s,%s)
    """, (
        project_id,
        current["company_id"],
        "Planned",
        "In Progress",
        current["user_id"]
    ))

    conn.commit()
    cur.close()
    conn.close()

    return {"message": "Project started"}

@app.get("/projects/{project_id}/tasks")
def list_project_tasks(project_id: int, current=Depends(get_current_user)):
    conn = get_db()
    cur = conn.cursor()

    # Ensure project belongs to company
    cur.execute("""
        SELECT id FROM projects
        WHERE id = %s AND company_id = %s
    """, (project_id, current["company_id"]))

    if not cur.fetchone():
        cur.close()
        conn.close()
        raise HTTPException(status_code=404)

    cur.execute("""
        SELECT
            t.id,
            t.title,
            t.status,
            u.name,
            t.priority,
            t.due_date
        FROM project_tasks t
        LEFT JOIN users u ON u.id = t.assigned_to
        WHERE t.project_id = %s
        ORDER BY t.created_at
    """, (project_id,))

    tasks = cur.fetchall()
    cur.close()
    conn.close()

    return [
        {
            "id": t[0],
            "title": t[1],
            "status": t[2],
            "assigned_to": t[3],
            "priority": t[4],
            "due_date": t[5]
        }
        for t in tasks
    ]

@app.post("/projects/{project_id}/tasks")
def create_task(
    project_id: int,
    data: CreateTask,
    current=Depends(get_current_user)
):
    conn = get_db()
    status, is_leader, _ = get_project_and_role(conn, project_id, current)

    if not is_leader:
        raise HTTPException(status_code=403)

    if status != "In Progress":
        raise HTTPException(status_code=400, detail="Project not active")

    cur = conn.cursor()

    cur.execute("""
        INSERT INTO project_tasks (
            project_id,
            company_id,
            title,
            description,
            assigned_to,
            created_by,
            start_date,
            due_date,
            estimated_effort_hours,
            cost_impact,
            priority,
            dependency_task_id,
            status
        )
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,'Active')
    """, (
        project_id,
        current["company_id"],
        data.title,
        data.description,
        data.assigned_to,
        current["user_id"],
        data.start_date,
        data.due_date,
        data.estimated_effort_hours,
        data.cost_impact,
        data.priority,
        data.dependency_task_id
    ))

    conn.commit()
    cur.close()
    conn.close()

    return {"message": "Task created"}

@app.post("/projects/{project_id}/tasks/suggest")
def suggest_task(
    project_id: int,
    data: CreateTask,
    current=Depends(get_current_user)
):
    conn = get_db()
    status, is_leader, _ = get_project_and_role(conn, project_id, current)

    if is_leader:
        raise HTTPException(status_code=400, detail="Leader should create task directly")

    if status != "In Progress":
        raise HTTPException(status_code=400)

    cur = conn.cursor()

    cur.execute("""
        INSERT INTO project_tasks (
            project_id,
            company_id,
            title,
            description,
            created_by,
            status
        )
        VALUES (%s,%s,%s,%s,%s,'Pending Approval')
    """, (
        project_id,
        current["company_id"],
        data.title,
        data.description,
        current["user_id"]
    ))

    conn.commit()
    cur.close()
    conn.close()

    return {"message": "Task suggestion submitted"}

@app.post("/tasks/{task_id}/approve")
def approve_task(
    task_id: int,
    data: ApproveTask,
    current=Depends(get_current_user)
):
    conn = get_db()
    task_status, project_status, is_leader, _, _ = get_task_and_project(
        conn, task_id, current
    )

    if not is_leader:
        raise HTTPException(status_code=403)

    if task_status != "Pending Approval":
        raise HTTPException(status_code=400)

    cur = conn.cursor()

    if data.approve:
        cur.execute("""
            UPDATE project_tasks
            SET status = 'Active'
            WHERE id = %s
        """, (task_id,))
    else:
        cur.execute("""
            UPDATE project_tasks
            SET status = 'Rejected'
            WHERE id = %s
        """, (task_id,))

    conn.commit()
    cur.close()
    conn.close()

    return {"message": "Task decision recorded"}

@app.post("/tasks/{task_id}/status")
def update_task_status(
    task_id: int,
    data: UpdateTaskStatus,
    current=Depends(get_current_user)
):
    conn = get_db()
    task_status, project_status, _, is_assignee, _ = get_task_and_project(
        conn, task_id, current
    )

    if not is_assignee:
        raise HTTPException(status_code=403)

    if project_status != "In Progress":
        raise HTTPException(status_code=400)

    cur = conn.cursor()

    cur.execute("""
        UPDATE project_tasks
        SET status = %s, updated_at = CURRENT_TIMESTAMP
        WHERE id = %s
    """, (data.status, task_id))

    cur.execute("""
        INSERT INTO task_updates
        (task_id, company_id, updated_by, update_type, old_status, new_status, note)
        VALUES (%s,%s,%s,'status_change',%s,%s,%s)
    """, (
        task_id,
        current["company_id"],
        current["user_id"],
        task_status,
        data.status,
        data.note
    ))

    conn.commit()
    cur.close()
    conn.close()

    return {"message": "Task updated"}

@app.post("/tasks/{task_id}/complete")
def complete_task(task_id: int, current=Depends(get_current_user)):
    conn = get_db()
    task_status, _, is_leader, _, _ = get_task_and_project(
        conn, task_id, current
    )

    if not is_leader:
        raise HTTPException(status_code=403)

    cur = conn.cursor()

    cur.execute("""
        UPDATE project_tasks
        SET status = 'Done', updated_at = CURRENT_TIMESTAMP
        WHERE id = %s
    """, (task_id,))

    conn.commit()
    cur.close()
    conn.close()

    return {"message": "Task marked as done"}

@app.post("/projects/{project_id}/complete")
def complete_project(project_id: int, current=Depends(get_current_user)):
    conn = get_db()

    status, is_leader, _ = get_project_and_role(conn, project_id, current)

    if not is_leader:
        raise HTTPException(status_code=403, detail="Only leader can complete project")

    if status != "In Progress":
        raise HTTPException(status_code=400, detail="Project not in progress")

    cur = conn.cursor()

    # Check if any task is not Done
    cur.execute("""
        SELECT COUNT(*)
        FROM project_tasks
        WHERE project_id = %s
          AND company_id = %s
          AND status != 'Done'
    """, (project_id, current["company_id"]))

    remaining = cur.fetchone()[0]

    if remaining > 0:
        cur.close()
        conn.close()
        raise HTTPException(
            status_code=400,
            detail="All tasks must be completed before ending project"
        )

    # Update project status
    cur.execute("""
        UPDATE projects
        SET status = 'Completed', updated_at = CURRENT_TIMESTAMP
        WHERE id = %s
    """, (project_id,))

    # Log status change
    cur.execute("""
        INSERT INTO project_status_logs
        (project_id, company_id, old_status, new_status, changed_by)
        VALUES (%s,%s,%s,%s,%s)
    """, (
        project_id,
        current["company_id"],
        "In Progress",
        "Completed",
        current["user_id"]
    ))

    conn.commit()
    cur.close()
    conn.close()

    return {"message": "Project completed successfully"}






BASE_DIR = Path(__file__).resolve().parent.parent
FRONTEND_DIR = BASE_DIR / "Frontend"

app.mount("/", StaticFiles(directory=FRONTEND_DIR, html=True), name="frontend")