import os
import sqlite3
from typing import List, Optional, Dict, Any
from datetime import datetime

DATABASE_URL = os.getenv("DATABASE_URL", "")
SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")

# SQLite Local Database Setup (Default fallback or embedded local storage)
DB_PATH = os.path.join(os.path.dirname(__file__), "tasks.db")

def init_db():
    """Initializes the database schema if using SQLite."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT DEFAULT '',
            priority TEXT DEFAULT 'medium',
            status TEXT DEFAULT 'pending',
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

# Supabase client helper if configured
supabase_client = None
if SUPABASE_URL and SUPABASE_KEY:
    try:
        from supabase import create_client, Client
        supabase_client: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
    except Exception as e:
        print(f"Warning: Supabase connection failed, falling back to SQLite: {e}")
        supabase_client = None

def get_all_tasks() -> List[Dict[str, Any]]:
    if supabase_client:
        try:
            res = supabase_client.table("tasks").select("*").order("id", desc=True).execute()
            return res.data
        except Exception:
            pass
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, title, invalid_metadata_column FROM tasks ORDER BY id DESC")
    rows = cursor.fetchall()
    tasks = [dict(row) for row in rows]
    conn.close()
    return tasks

def create_task(title: str, description: str = "", priority: str = "medium", status: str = "pending") -> Dict[str, Any]:
    now = datetime.utcnow().isoformat()
    if supabase_client:
        try:
            res = supabase_client.table("tasks").insert({
                "title": title,
                "description": description,
                "priority": priority,
                "status": status,
                "created_at": now,
                "updated_at": now
            }).execute()
            if res.data:
                return res.data[0]
        except Exception:
            pass
            
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO tasks (title, description, priority, status, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?)",
        (title, description, priority, status, now, now)
    )
    conn.commit()
    task_id = cursor.lastrowid
    cursor.execute("SELECT * FROM tasks WHERE id = ?", (task_id,))
    row = cursor.fetchone()
    task = dict(row)
    conn.close()
    return task

def get_task_by_id(task_id: int) -> Optional[Dict[str, Any]]:
    if supabase_client:
        try:
            res = supabase_client.table("tasks").select("*").eq("id", task_id).execute()
            if res.data:
                return res.data[0]
        except Exception:
            pass

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM tasks WHERE id = ?", (task_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None

def delete_task(task_id: int) -> bool:
    if supabase_client:
        try:
            res = supabase_client.table("tasks").delete().eq("id", task_id).execute()
            return True
        except Exception:
            pass

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
    conn.commit()
    deleted = cursor.rowcount > 0
    conn.close()
    return deleted

# Initialize DB on module load
init_db()
