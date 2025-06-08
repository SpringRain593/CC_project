from db import get_conn

def get_user_by_name(username: str):
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute("SELECT * FROM users WHERE username=%s", (username,))
        return cur.fetchone()

def create_user(username: str, pw_hash: str, role: str = "user"):
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(
            "INSERT INTO users (username, pw_hash, role) VALUES (%s,%s,%s)",
            (username, pw_hash, role)
        )
        return cur.lastrowid

def list_files_by_user(uid):
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute("SELECT file_id,filename,uploaded_at,size_bytes FROM files WHERE user_id=%s", (uid,))
        return cur.fetchall()

def get_user_by_id(uid: int):
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute("SELECT * FROM users WHERE user_id=%s", (uid,))
        return cur.fetchone()

def insert_file(uid, path, fname, size):
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(
            "INSERT INTO files (user_id, file_path, filename, size_bytes) VALUES (%s, %s, %s, %s)",
            (uid, path, fname, size)
        )
        return cur.lastrowid

def get_file(fid, uid):
    with get_conn() as conn, conn.cursor(dictionary=True) as cur:
        cur.execute("SELECT * FROM files WHERE file_id=%s AND user_id=%s", (fid, uid))
        return cur.fetchone()

