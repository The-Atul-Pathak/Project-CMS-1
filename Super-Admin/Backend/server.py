from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import psycopg2
from passlib.context import CryptContext
from datetime import datetime, timedelta
from jose import jwt
from fastapi import Request
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional
from psycopg2 import errors
from psycopg2.errors import UniqueViolation


app = FastAPI()
security = HTTPBearer()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

#---------------- MODELS ----------------
class UserLogin(BaseModel):
    admin_id: str
    password: str
class CreateAdmin(BaseModel):
    name: str
    email: str
    password: str
class CompanyCreate(BaseModel):
    company_name: str
    legal_name: Optional[str] = None
    domain: Optional[str] = None
    industry: Optional[str] = None
    employee_size_range: Optional[str] = None
class CompanyContactCreate(BaseModel):
    name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    designation: Optional[str] = None
    is_primary: bool = True
class CompanyUpdate(BaseModel):
    company_name: str
    legal_name: Optional[str] = None
    domain: Optional[str] = None
    industry: Optional[str] = None
    employee_size_range: Optional[str] = None
    status: str
class PlanCreate(BaseModel):
    name: str
    price_monthly: Optional[float] = None
    price_yearly: Optional[float] = None
    max_employees: Optional[int] = None
class PlanUpdate(BaseModel):
    name: str
    price_monthly: Optional[float] = None
    price_yearly: Optional[float] = None
    max_employees: Optional[int] = None
class FeatureCreate(BaseModel):
    code: str
    name: str
    description: Optional[str] = None
class FeatureUpdate(BaseModel):
    code: str
    name: str
    description: Optional[str] = None


#---------------- AUTH HELPERS ----------------

def get_current_admin(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

    admin_id = payload.get("sub")
    session_id = payload.get("sid")

    if not admin_id or not session_id:
        raise HTTPException(status_code=401, detail="Invalid token")

    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute(
        "SELECT id, role FROM platform_admins WHERE id = %s",
        (admin_id,)
    )
    admin = cur.fetchone()

    cur.close()
    conn.close()

    if not admin:
        raise HTTPException(status_code=401)

    return {
        "id": admin[0],
        "role": admin[1],
        "session_id": session_id
    }

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

# ---------------- LOGIN ----------------
@app.post("/login")
def login(user: UserLogin, request: Request):
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute(
        "SELECT id, password_hash FROM platform_admins WHERE name = %s",
        (user.admin_id,)
    )
    row = cur.fetchone()

    if not row:
        return {"error": "Invalid credentials"}

    user_id, password_hash = row

    if not verify_password(user.password, password_hash):
        return {"error": "Invalid credentials"}

    expires_at = datetime.utcnow() + timedelta(minutes=30)

    cur.execute(
        """
        INSERT INTO platform_sessions (admin_id, ip_address, user_agent, expires_at)
        VALUES (%s, %s, %s, %s)
        RETURNING id
        """,
        (
            user_id,
            request.client.host,
            request.headers.get("user-agent"),
            expires_at
        )
    )

    session_id = cur.fetchone()[0]
    conn.commit()
    cur.close()
    conn.close()

    token = create_access_token({
        "sub": str(user_id),
        "sid": session_id
    })

    return {"access_token": token}

#---------------- ADMIN MANAGEMENT ----------------

@app.post("/admins")
def add_admin(
    admin: CreateAdmin,
    current=Depends(get_current_admin)
):
    if current["role"] != "SUPER_ADMIN":
        raise HTTPException(status_code=403, detail="Not allowed")

    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute(
        """
        INSERT INTO platform_admins (name, email, role, password_hash)
        VALUES (%s, %s, %s, %s)
        """,
        (
            admin.name,
            admin.email,
            "SUPPORT",
            hash_password(admin.password)
        )
    )

    conn.commit()
    cur.close()
    conn.close()

    return {"message": "Admin added successfully"}

@app.get("/admins")
def list_admins(current=Depends(get_current_admin)):
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("SELECT id, name, email, role FROM platform_admins")
    admins = cur.fetchall()

    cur.close()
    conn.close()

    return admins

@app.delete("/admins/{admin_id}")
def remove_admin(
    admin_id: int,
    current=Depends(get_current_admin)
):
    # Only SUPER_ADMIN can delete
    if current["role"] != "SUPER_ADMIN":
        raise HTTPException(status_code=403, detail="Not allowed")

    # Cannot delete yourself
    if current["id"] == admin_id:
        raise HTTPException(status_code=400, detail="Cannot delete yourself")

    conn = get_db_connection()
    cur = conn.cursor()

    # Get role of admin being deleted
    cur.execute(
        "SELECT role FROM platform_admins WHERE id = %s",
        (admin_id,)
    )
    row = cur.fetchone()

    if not row:
        cur.close()
        conn.close()
        raise HTTPException(status_code=404, detail="Admin not found")

    role_to_delete = row[0]

    # If deleting SUPER_ADMIN → check count
    if role_to_delete == "SUPER_ADMIN":
        cur.execute(
            "SELECT COUNT(*) FROM platform_admins WHERE role = 'SUPER_ADMIN'"
        )
        super_admin_count = cur.fetchone()[0]

        if super_admin_count <= 1:
            cur.close()
            conn.close()
            raise HTTPException(
                status_code=400,
                detail="Cannot delete the last SUPER_ADMIN"
            )

    # Safe to delete
    cur.execute(
        "DELETE FROM platform_admins WHERE id = %s",
        (admin_id,)
    )
    conn.commit()

    cur.close()
    conn.close()

    return {"message": "Admin removed successfully"}

@app.post("/logout")
def logout(current=Depends(get_current_admin)):
    admin_id = current["id"]
    session_id = current["session_id"]

    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute(
        "DELETE FROM platform_sessions WHERE id = %s AND admin_id = %s",
        (session_id, admin_id)
    )

    conn.commit()
    cur.close()
    conn.close()

    return {"message": "Logged out successfully"}

@app.post("/companies")
def add_company(
    company: CompanyCreate,
    contact: CompanyContactCreate,
    current=Depends(get_current_admin)
):
    if current["role"] not in ["SUPER_ADMIN", "SUPPORT"]:
        raise HTTPException(status_code=403)

    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute(
        """
        INSERT INTO companies
        (company_name, legal_name, domain, industry, employee_size_range)
        VALUES (%s, %s, %s, %s, %s)
        RETURNING id
        """,
        (
            company.company_name,
            company.legal_name,
            company.domain,
            company.industry,
            company.employee_size_range
        )
    )
    company_id = cur.fetchone()[0]

    cur.execute(
        """
        INSERT INTO company_contacts
        (company_id, name, email, phone, designation, is_primary)
        VALUES (%s, %s, %s, %s, %s, %s)
        """,
        (
            company_id,
            contact.name,
            contact.email,
            contact.phone,
            contact.designation,
            contact.is_primary
        )
    )

    conn.commit()
    cur.close()
    conn.close()

    return {"message": "Company added successfully", "company_id": company_id}

@app.get("/companies")
def list_companies(current=Depends(get_current_admin)):
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT id, company_name, industry, status, onboarding_status, created_at
        FROM companies
        ORDER BY created_at DESC
    """)
    companies = cur.fetchall()

    cur.close()
    conn.close()
    return companies

@app.get("/companies/{company_id}")
def get_company(company_id: int, current=Depends(get_current_admin)):
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT id, company_name, legal_name, domain,
               industry, employee_size_range, status
        FROM companies
        WHERE id = %s
    """, (company_id,))

    company = cur.fetchone()
    cur.close()
    conn.close()

    if not company:
        raise HTTPException(status_code=404, detail="Company not found")

    return {
        "id": company[0],
        "company_name": company[1],
        "legal_name": company[2],
        "domain": company[3],
        "industry": company[4],
        "employee_size_range": company[5],
        "status": company[6],
    }


@app.put("/companies/{company_id}")
def update_company(
    company_id: int,
    company: CompanyUpdate,
    current=Depends(get_current_admin)
):
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute(
        """
        UPDATE companies
        SET company_name = %s,
            legal_name = %s,
            domain = %s,
            industry = %s,
            employee_size_range = %s,
            status = %s,
            updated_at = CURRENT_TIMESTAMP
        WHERE id = %s
        """,
        (
            company.company_name,
            company.legal_name,
            company.domain,
            company.industry,
            company.employee_size_range,
            company.status,
            company_id
        )
    )

    if cur.rowcount == 0:
        raise HTTPException(status_code=404, detail="Company not found")

    conn.commit()
    cur.close()
    conn.close()

    return {"message": "Company updated successfully"}

@app.post("/plans")
def create_plan(plan: PlanCreate, current=Depends(get_current_admin)):
    if current["role"] != "SUPER_ADMIN":
        raise HTTPException(status_code=403)

    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO plans (name, price_monthly, price_yearly, max_employees)
        VALUES (%s, %s, %s, %s)
    """, (plan.name, plan.price_monthly, plan.price_yearly, plan.max_employees))

    conn.commit()
    cur.close()
    conn.close()

    return {"message": "Plan created"}

@app.get("/plans")
def list_plans(current=Depends(get_current_admin)):
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT id, name, price_monthly, price_yearly, max_employees, created_at
        FROM plans
        ORDER BY id
    """)
    plans = cur.fetchall()

    cur.close()
    conn.close()
    return plans

@app.post("/features")
def create_feature(feature: FeatureCreate, current=Depends(get_current_admin)):
    if current["role"] not in ["SUPER_ADMIN", "SUPPORT"]:
        raise HTTPException(status_code=403)

    conn = get_db_connection()
    cur = conn.cursor()

    try:
        cur.execute(
            """
            INSERT INTO features (code, name, description)
            VALUES (%s, %s, %s)
            """,
            (feature.code, feature.name, feature.description)
        )
        conn.commit()

    except errors.UniqueViolation:
        conn.rollback()
        raise HTTPException(
            status_code=400,
            detail=f"Feature with code '{feature.code}' already exists"
        )

    finally:
        cur.close()
        conn.close()

    return {"message": "Feature added successfully"}


@app.get("/features")
def list_features(current=Depends(get_current_admin)):
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT id, code, name, description
        FROM features
        ORDER BY id
    """)
    features = cur.fetchall()

    cur.close()
    conn.close()
    return features

@app.put("/plans/{plan_id}")
def update_plan(
    plan_id: int,
    plan: PlanUpdate,
    current=Depends(get_current_admin)
):
    if current["role"] != "SUPER_ADMIN":
        raise HTTPException(status_code=403)

    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("""
        UPDATE plans
        SET name = %s,
            price_monthly = %s,
            price_yearly = %s,
            max_employees = %s
        WHERE id = %s
    """, (
        plan.name,
        plan.price_monthly,
        plan.price_yearly,
        plan.max_employees,
        plan_id
    ))

    if cur.rowcount == 0:
        raise HTTPException(status_code=404, detail="Plan not found")

    conn.commit()
    cur.close()
    conn.close()

    return {"message": "Plan updated successfully"}

@app.delete("/plans/{plan_id}")
def delete_plan(
    plan_id: int,
    current=Depends(get_current_admin)
):
    if current["role"] != "SUPER_ADMIN":
        raise HTTPException(status_code=403)

    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("DELETE FROM plans WHERE id = %s", (plan_id,))

    if cur.rowcount == 0:
        raise HTTPException(status_code=404, detail="Plan not found")

    conn.commit()
    cur.close()
    conn.close()

    return {"message": "Plan deleted successfully"}

@app.put("/features/{feature_id}")
def update_feature(
    feature_id: int,
    feature: FeatureUpdate,
    current=Depends(get_current_admin)
):
    if current["role"] not in ["SUPER_ADMIN", "SUPPORT"]:
        raise HTTPException(status_code=403)

    conn = get_db_connection()
    cur = conn.cursor()

    try:
        cur.execute(
            """
            UPDATE features
            SET code = %s,
                name = %s,
                description = %s
            WHERE id = %s
            """,
            (
                feature.code,
                feature.name,
                feature.description,
                feature_id
            )
        )

        if cur.rowcount == 0:
            raise HTTPException(status_code=404, detail="Feature not found")

        conn.commit()

    except UniqueViolation:
        conn.rollback()
        raise HTTPException(
            status_code=400,
            detail="Feature code already exists"
        )

    except psycopg2.Error:
        conn.rollback()
        raise HTTPException(
            status_code=500,
            detail="Database error"
        )

    finally:
        cur.close()
        conn.close()

    return {"message": "Feature updated successfully"}


@app.delete("/features/{feature_id}")
def delete_feature(
    feature_id: int,
    current=Depends(get_current_admin)
):
    if current["role"] != "SUPER_ADMIN":
        raise HTTPException(status_code=403)

    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("DELETE FROM features WHERE id = %s", (feature_id,))

    if cur.rowcount == 0:
        raise HTTPException(status_code=404, detail="Feature not found")

    conn.commit()
    cur.close()
    conn.close()

    return {"message": "Feature deleted successfully"}
