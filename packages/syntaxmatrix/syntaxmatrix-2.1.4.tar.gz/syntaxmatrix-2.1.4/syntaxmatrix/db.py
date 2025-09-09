# syntaxmatrix/db.py
from datetime import datetime
import sqlite3
import time
import os
import json
from werkzeug.utils import secure_filename
from syntaxmatrix.project_root import detect_project_root

from pathlib import Path

_CLIENT_DIR = detect_project_root()
DB_PATH = os.path.join(_CLIENT_DIR, "data", "syntaxmatrix.db")
TEMPLATES_DIR = os.path.join(_CLIENT_DIR, "templates")
os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
os.makedirs(TEMPLATES_DIR, exist_ok=True)

def _rel_to_templates(path: str) -> str:
    """
    Convert any absolute path (Windows or Linux) to a POSIX-style relative
    'templates/<filename>.html'. If no 'templates' segment is found, use just the filename.
    """
    p = Path(path)
    parts = list(p.parts)
    if "templates" in parts:
        idx = parts.index("templates")
        rel = Path(*parts[idx:])  # starts with 'templates'
    else:
        rel = Path("templates") / p.name
    return str(rel).replace("\\", "/")

def _abs_from_rel(rel: str) -> str:
    """
    Build an absolute path inside the mounted bucket from a stored relative path.
    Accepts either 'templates/foo.html' or 'foo.html' (we'll fix up the latter).
    """
    rel = (rel or "").replace("\\", "/")
    if rel.startswith("templates/"):
        rel = rel[len("templates/"):]
    return str(Path(TEMPLATES_DIR) / rel)

def migrate_page_paths_to_relative():
    """
    One-off normaliser: if 'pages.content' holds absolute Windows/Linux paths,
    rewrite them to 'templates/<filename>.html'. Idempotent and safe to run at import.
    """
    import sqlite3
    try:
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        rows = cur.execute("SELECT name, content FROM pages").fetchall()
    except Exception:
        # Table may not exist yet; nothing to do.
        return
    updated = 0
    for name, content in rows:
        if not content:
            continue
        looks_abs = (":" in content[:3]) or content.startswith("/") or ("\\" in content)
        if looks_abs:
            rel = _rel_to_templates(content)
            if rel != content:
                cur.execute("UPDATE pages SET content = ? WHERE name = ?", (rel, name))
                updated += 1
    conn.commit()
    conn.close()
    return updated

# Run normalisation once per import (safe if empty / no-op)
try:
    migrate_page_paths_to_relative()
except Exception:
    pass


# ***************************************
# Pages Table Functions
# ***************************************
def init_db():
    conn = sqlite3.connect(DB_PATH)
    
    conn.execute("""
        CREATE TABLE IF NOT EXISTS pages (
            name TEXT PRIMARY KEY,
            content TEXT
        )
    """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS askai_cells (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT,
            question TEXT,
            output TEXT,
            code TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()
    conn.close()
    

def get_pages():
    """Return {page_name: full_html_string} by opening each stored relative path under templates/."""
    conn = sqlite3.connect(DB_PATH)
    rows = conn.execute("SELECT name, content FROM pages").fetchall()
    conn.close()

    pages = {}
    for name, rel in rows:
        abs_path = _abs_from_rel(rel or "")
        try:
            with open(abs_path, "r", encoding="utf-8") as f:
                pages[name] = f.read()
        except FileNotFoundError:
            pages[name] = f"<p>Missing file for page '{name}'.</p>"
    return pages


def add_page(name, html):
    """Create templates/<filename>.html, store a POSIX-style relative path in the DB."""
    filename = secure_filename(name.lower()) + ".html"
    abs_path = os.path.join(TEMPLATES_DIR, filename)

    with open(abs_path, "w", encoding="utf-8") as f:
        f.write(html)

    rel_path = f"templates/{filename}"
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("INSERT INTO pages (name, content) VALUES (?, ?)", (name, rel_path))
    conn.commit()
    conn.close()


def update_page(old_name, new_name, html):
    """Overwrite the file; rename it (and DB row) if the title changes, storing a relative path."""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    row = cur.execute("SELECT content FROM pages WHERE name = ?", (old_name,)).fetchone()
    if not row:
        conn.close()
        return

    rel = row[0] or ""
    abs_path = _abs_from_rel(rel)

    # Rename file if page title changes
    if old_name != new_name:
        new_filename = secure_filename(new_name.lower()) + ".html"
        new_abs_path = os.path.join(TEMPLATES_DIR, new_filename)
        os.makedirs(os.path.dirname(new_abs_path), exist_ok=True)
        try:
            os.rename(abs_path, new_abs_path)
        except FileNotFoundError:
            # If original file is missing, we’ll create the new one fresh below.
            pass
        abs_path = new_abs_path
        rel = f"templates/{new_filename}"

    # Write updated HTML
    with open(abs_path, "w", encoding="utf-8") as f:
        f.write(html)

    cur.execute("UPDATE pages SET name = ?, content = ? WHERE name = ?", (new_name, rel, old_name))
    conn.commit()
    conn.close()


def delete_page(name):
    """Remove the file on disk, then delete the DB row."""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    row = cur.execute("SELECT content FROM pages WHERE name = ?", (name,)).fetchone()
    if row:
        abs_path = _abs_from_rel(row[0] or "")
        if os.path.exists(abs_path):
            try:
                os.remove(abs_path)
            except Exception:
                pass
    cur.execute("DELETE FROM pages WHERE name = ?", (name,))
    conn.commit()
    conn.close()


def add_askai_cell(session_id, question, output, code):
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        "INSERT INTO askai_cells (session_id, question, output, code) VALUES (?, ?, ?, ?)",
        (session_id, question, output, code)
    )
    conn.commit()
    conn.close()

def get_askai_cells(session_id, limit=15):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT question, output, code FROM askai_cells WHERE session_id = ? ORDER BY id DESC LIMIT ?",
        (session_id, limit)
    )
    cells = [{"question": q, "output": o, "code": c} for q, o, c in cursor.fetchall()]
    conn.close()
    return cells

