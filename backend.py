import streamlit as st
import hashlib
from sqlalchemy import text

# ==========================================
# Connexion PostgreSQL (Neon)
# ==========================================

conn = st.connection(
    "postgresql",
    type="sql"
)

# ==========================================
# Création des tables
# ==========================================

with conn.session as s:

    # Table users
    s.execute(text("""
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            name TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    """))

    # Table tasks
    s.execute(text("""
        CREATE TABLE IF NOT EXISTS tasks (
            id SERIAL PRIMARY KEY,
            description TEXT NOT NULL,
            status BOOLEAN DEFAULT FALSE,
            user_id INTEGER REFERENCES users(id)
        )
    """))

    s.commit()

# ==========================================
# Fonctions
# ==========================================

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def create_user(username, password):
    try:
        with conn.session as s:
            s.execute(
                text("""
                    INSERT INTO users (name, password)
                    VALUES (:name, :password)
                """),
                {
                    "name": username,
                    "password": hash_password(password)
                }
            )
            s.commit()
        return True
    except:
        return False

def login_user(username, password):

    user = conn.query(
        """
        SELECT id
        FROM users
        WHERE name = :name
        AND password = :password
        """,
        params={
            "name": username,
            "password": hash_password(password)
        },
        ttl=0
    )

    if len(user) > 0:
        return int(user.iloc[0]["id"])

    return None

def add_task(user_id, task):

    with conn.session as s:
        s.execute(
            text("""
                INSERT INTO tasks (description, status, user_id)
                VALUES (:description, :status, :user_id)
            """),
            {
                "description": task,
                "status": False,
                "user_id": user_id
            }
        )
        s.commit()

def get_tasks(user_id):
    return conn.query(
        """
        SELECT id, description, status
        FROM tasks
        WHERE user_id = :user_id
        ORDER BY id
        """,
        params={
            "user_id": user_id
        },
        ttl=0
    )


def mark_done(task_id):

    with conn.session as s:
        s.execute(
            text("""
                UPDATE tasks
                SET status = TRUE
                WHERE id = :id
            """),
            {"id": task_id}
        )
        s.commit()

def delete_task(task_id):
    with conn.session as s:
        s.execute(
            text("""
                DELETE FROM tasks
                WHERE id = :id
            """),
            {"id": task_id}
        )
        s.commit()
