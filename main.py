from fastapi import FastAPI, HTTPException, status, Request
from pydantic import BaseModel, EmailStr
import logging
import time
import psycopg2
from psycopg2 import errors
from psycopg2.extras import RealDictCursor
import os
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)

logger = logging.getLogger(__name__)

app = FastAPI()

DATABASE_URL = os.getenv("DATABASE_URL")

@app.get("/db-test")
def db_test():
    conn = None

    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT 1;")
        result = cur.fetchone()
        conn.close()
        return {"status": "connected", "result": result}
    except Exception as e:
        return {"status": "error", "detail": str(e)}
    finally:
        if conn:
            conn.close()

def get_connection():
    return psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)

class User(BaseModel):
    id: int
    name: str
    email: EmailStr

class UserCreate(BaseModel):
    name: str
    email: EmailStr

class UserUpdate(BaseModel):
    name: str | None = None
    email: EmailStr | None = None

class UserSignup(BaseModel):
    name: str | None = None



@app.middleware("http")
async def log_request_time(request: Request, call_next):
    start_time = time.time()

    response = await call_next(request)

    duration = time.time() - start_time

    logger.info(
        f"{request.method} {request.url.path} completed in {duration:.4f}s"
    )

    return response

@app.get("/")
def root():
    return {"message": "DevOS API running"}

@app.get("/users/{user_id}")
def get_user(user_id: int):
    logger.info(f"Fetching user id={user_id}")
    conn = None

    try:
        conn = get_connection()
        cur = conn.cursor()
        query = ("SELECT * FROM users WHERE id = %s;")
        values = (user_id,)
        cur.execute(query, values)
        result = cur.fetchone()
        if result is None:
            logger.warning(f"User id={user_id} not found")
            raise HTTPException(status_code=404, detail="User not found")
        else:
            logger.info(f"User id={user_id} fetched successfully")
            return result
    except psycopg2.Error:
        raise HTTPException(status_code=500, detail="Internal server error.")
    finally:
        if conn:
            conn.close()


@app.put("/users/{user_id}")
def update_user(user_id: int, payload: UserUpdate):
    logger.info(f"Updating user id={user_id}")
    conn = None
    try:
        updates = payload.model_dump(exclude_unset=True)
        if not updates:
            raise HTTPException(status_code=400, detail="No fields provided for update")

        conn = get_connection()
        cur = conn.cursor()

        set_clauses = []
        values = []

        if "name" in updates:
            set_clauses.append("name = %s")
            values.append(updates["name"])

        if "email" in updates:
            set_clauses.append("email = %s")
            values.append(updates["email"])

        values.append(user_id)

        query = f"""
            UPDATE users
            SET {", ".join(set_clauses)}
            WHERE id = %s
            RETURNING *;
        """

        cur.execute(query, tuple(values))
        result = cur.fetchone()

        if result is None:
            logger.warning(f"Update failed — user id={user_id} not found")
            raise HTTPException(status_code=404, detail="User not found")

        conn.commit()
        logger.info(f"User id={user_id} updated successfully")
        return result

    except errors.UniqueViolation:
        raise HTTPException(status_code=409, detail="Email already in use.")
    except psycopg2.Error:
        raise HTTPException(status_code=500, detail="Internal server error.")
    finally:
        if conn:
            conn.close()

@app.post("/users", status_code=status.HTTP_201_CREATED)
def create_user(payload: UserCreate):
    logger.info(f"Creating user with email={payload.email}")
    conn = None

    try:
        conn = get_connection()
        cur = conn.cursor()
        insert_query = ("INSERT INTO users (name, email) VALUES (%s, %s) RETURNING *;")
        values = (payload.name, payload.email)
        cur.execute(insert_query, values)
        result = cur.fetchone()
        conn.commit()
        logger.info(f"User created successfully id={result['id']}")
        return result
    except errors.UniqueViolation:
        raise HTTPException(status_code=409, detail="Email already in use.")
    except psycopg2.Error:
        raise HTTPException(status_code=500, detail="Internal server error.")
    finally:
        if conn:
            conn.close()



@app.get("/users")
def list_users():
    logger.info("Listing all users")
    conn = None

    try:
        conn = get_connection()
        cur = conn.cursor()
        query = "SELECT * FROM users ORDER BY id;"
        cur.execute(query)
        results = cur.fetchall()

        logger.info(f"Listed {len(results)} users successfully")
        return results

    except psycopg2.Error:
        raise HTTPException(status_code=500, detail="Internal server error.")
    finally:
        if conn:
            conn.close()


@app.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: int):
    logger.info(f"Attempting to delete user id={user_id}")
    conn = None

    try:
        conn = get_connection()
        cur = conn.cursor()
        query = "DELETE FROM users WHERE id = %s RETURNING *;"
        values = (user_id,)
        cur.execute(query, values)
        result = cur.fetchone()

        if result is None:
            logger.warning(f"Delete failed — user id={user_id} not found")
            raise HTTPException(status_code=404, detail="User not found")

        conn.commit()
        logger.info(f"User id={user_id} deleted successfully")
        return None

    except psycopg2.Error:
        raise HTTPException(status_code=500, detail="Internal server error.")
    finally:
        if conn:
            conn.close()
