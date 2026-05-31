import hashlib
import secrets
import sqlite3

from app.models.db import establish_connection


def generate_password_hash(password: str, salt: bytes) -> str:
    dk = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 100_000)
    return dk.hex()


class UserRepository:
    @staticmethod
    def create_user(user_name: str, pass_word: str) -> bool:
        salt_val = secrets.token_bytes(16)
        pass_hash = generate_password_hash(pass_word, salt_val)
        try:
            with establish_connection() as conn:
                conn.execute(
                    "INSERT INTO users(username, password_hash, salt) VALUES(?,?,?)",
                    (user_name, pass_hash, salt_val.hex())
                )
            return True
        except sqlite3.IntegrityError:
            return False

    @staticmethod
    def get_user_by_username(user_name: str):
        with establish_connection() as conn:
            row = conn.execute(
                "SELECT id, username, created_at, role_id FROM users WHERE username = ?",
                (user_name,)
            ).fetchone()
        return row

    @staticmethod
    def get_user_by_id(user_id: int):
        with establish_connection() as conn:
            row = conn.execute(
                "SELECT id, username, created_at, role_id FROM users WHERE id = ?",
                (user_id,)
            ).fetchone()
        return row

    @staticmethod
    def verify_user(user_name: str, pass_word: str) -> bool:
        row = UserRepository.get_user_by_username(user_name)
        if not row:
            return False
        salt_val = bytes.fromhex(row["salt"])
        return generate_password_hash(pass_word, salt_val) == row["password_hash"]

    @staticmethod
    def get_all_users(page_num: int = 1, per_page: int = 20):
        offset_val = (page_num - 1) * per_page
        with establish_connection() as conn:
            rows = conn.execute(
                "SELECT id, username, created_at FROM users ORDER BY id DESC LIMIT ? OFFSET ?",
                (per_page, offset_val)
            ).fetchall()
            total = conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]
        return rows, total

    @staticmethod
    def update_user(user_id: int, user_name: str):
        with establish_connection() as conn:
            conn.execute(
                "UPDATE users SET username = ? WHERE id = ?",
                (user_name, user_id)
            )

    @staticmethod
    def update_user_password(user_id: int, pass_word: str):
        salt_val = secrets.token_bytes(16)
        pass_hash = generate_password_hash(pass_word, salt_val)
        with establish_connection() as conn:
            conn.execute(
                "UPDATE users SET password_hash = ?, salt = ? WHERE id = ?",
                (pass_hash, salt_val.hex(), user_id)
            )

    @staticmethod
    def delete_user(user_id: int):
        with establish_connection() as conn:
            conn.execute("DELETE FROM users WHERE id = ?", (user_id,))

    @staticmethod
    def batch_delete_users(user_ids: list):
        with establish_connection() as conn:
            placeholders = ",".join(["?"] * len(user_ids))
            conn.execute(f"DELETE FROM users WHERE id IN ({placeholders})", user_ids)

    @staticmethod
    def search_users(keyword: str, page_num: int = 1, per_page: int = 20):
        offset_val = (page_num - 1) * per_page
        with establish_connection() as conn:
            rows = conn.execute(
                "SELECT id, username, created_at FROM users WHERE username LIKE ? ORDER BY id DESC LIMIT ? OFFSET ?",
                (f"%{keyword}%", per_page, offset_val)
            ).fetchall()
            total = conn.execute(
                "SELECT COUNT(*) FROM users WHERE username LIKE ?",
                (f"%{keyword}%",)
            ).fetchone()[0]
        return rows, total

    @staticmethod
    def get_all_users_with_roles(page_num: int = 1, per_page: int = 20):
        offset_val = (page_num - 1) * per_page
        with establish_connection() as conn:
            rows = conn.execute(
                """
                SELECT u.id, u.username, u.created_at, r.name as role_name, r.id as role_id
                FROM users u
                LEFT JOIN roles r ON u.role_id = r.id
                ORDER BY u.id DESC
                LIMIT ? OFFSET ?
                """,
                (per_page, offset_val)
            ).fetchall()
            total = conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]
        return rows, total

    @staticmethod
    def set_user_role(user_id: int, role_id: int):
        with establish_connection() as conn:
            conn.execute(
                "UPDATE users SET role_id = ? WHERE id = ?",
                (role_id, user_id)
            )

    @staticmethod
    def get_user_with_role(user_id: int):
        with establish_connection() as conn:
            row = conn.execute(
                """
                SELECT u.id, u.username, u.created_at, r.id as role_id, r.name as role_name
                FROM users u
                LEFT JOIN roles r ON u.role_id = r.id
                WHERE u.id = ?
                """,
                (user_id,)
            ).fetchone()
        return row
