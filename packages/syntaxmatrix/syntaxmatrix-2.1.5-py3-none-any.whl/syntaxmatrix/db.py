from __future__ import annotations
from datetime import datetime
import sqlite3
import time
import os
import json
from werkzeug.utils import secure_filename
from syntaxmatrix.project_root import detect_project_root

_CLIENT_DIR = detect_project_root()
DB_PATH = os.path.join(_CLIENT_DIR, "data", "syntaxmatrix.db")
os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

TEMPLATES_DIR = os.path.join(_CLIENT_DIR, "templates")
os.makedirs(TEMPLATES_DIR, exist_ok=True)

def _to_abs(path_or_rel: str, page_name: str | None = None) -> str:
    """Resolve DB value to an absolute file path under syntaxmatrixdir/templates."""
    val = (path_or_rel or "").replace("\\", "/")

    # Already a relative entry we want (templates/foo.html)
    if val.startswith("templates/"):
        return os.path.join(TEMPLATES_DIR, val.split("/", 1)[-1])

    # If the DB contains an absolute Windows/Linux path, keep using it (back-compat).
    if (":" in val[:3]) or val.startswith("/"):
        return val

    # Fallback: build from the page name if we have it
    from werkzeug.utils import secure_filename
    filename = secure_filename((page_name or "").lower()) + ".html"
    return os.path.join(TEMPLATES_DIR, filename)

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
    """Return {page_name: full_html_string} by resolving each stored path OS-agnostically."""
    conn = sqlite3.connect(DB_PATH)
    rows = conn.execute("SELECT name, content FROM pages").fetchall()
    conn.close()

    pages = {}
    for name, stored in rows:
        abs_path = _to_abs(stored, page_name=name)
        try:
            with open(abs_path, "r", encoding="utf-8") as f:
                pages[name] = f.read()
        except FileNotFoundError:
            pages[name] = f"<p>Missing file for page '{name}'.</p>"
    return pages


def add_page(name, html):
    """Create templates/<slug>.html and store a relative path in the DB."""
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
    """Overwrite file; if title changes, rename file. Always store a relative path."""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    row = cur.execute("SELECT content FROM pages WHERE name = ?", (old_name,)).fetchone()
    if not row:
        conn.close()
        return

    # Resolve existing to absolute, then write the new content
    current_abs = _to_abs(row[0], page_name=old_name)

    new_filename = secure_filename(new_name.lower()) + ".html"
    new_abs = os.path.join(TEMPLATES_DIR, new_filename)
    os.makedirs(os.path.dirname(new_abs), exist_ok=True)

    # If name changed and old file exists, rename; otherwise we’ll just write new
    try:
        if old_name != new_name and os.path.exists(current_abs):
            os.replace(current_abs, new_abs)
    except Exception:
        # If rename fails for any reason, we’ll overwrite/create new_abs below
        pass

    with open(new_abs, "w", encoding="utf-8") as f:
        f.write(html)

    rel_path = f"templates/{new_filename}"
    cur.execute("UPDATE pages SET name = ?, content = ? WHERE name = ?", (new_name, rel_path, old_name))
    conn.commit()
    conn.close()


def delete_page(name):
    """Remove file on disk, then delete the DB row (OS-agnostic resolution)."""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    row = cur.execute("SELECT content FROM pages WHERE name = ?", (name,)).fetchone()
    if row:
        abs_path = _to_abs(row[0], page_name=name)
        if os.path.exists(abs_path):
            try:
                os.remove(abs_path)
            except Exception:
                pass
    cur.execute("DELETE FROM pages WHERE name = ?", (name,))
    conn.commit()
    conn.close()
