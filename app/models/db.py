import os
import sqlite3


def _get_project_root():
    return os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir))


DATABASE_PATH = os.path.join(_get_project_root(), "database", "app_data.db")


def establish_connection():
    os.makedirs(os.path.dirname(DATABASE_PATH), exist_ok=True)
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def setup_database():
    with establish_connection() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS users(
                id integer PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                password_hash TEXT NOT NULL,
                salt TEXT NOT NULL,
                role_id INTEGER DEFAULT 1,
                created_at TEXT NOT NULL DEFAULT(datetime('now')),
                FOREIGN KEY(role_id) REFERENCES roles(id)
            )
            """
        )

        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS roles(
                id integer PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                description TEXT DEFAULT '',
                is_system INTEGER DEFAULT 0,
                created_at TEXT NOT NULL DEFAULT(datetime('now'))
            )
            """
        )

        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS functions(
                id integer PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                code TEXT NOT NULL UNIQUE,
                parent_id INTEGER DEFAULT 0,
                url TEXT DEFAULT '',
                icon TEXT DEFAULT '',
                sort_order INTEGER DEFAULT 0,
                is_menu INTEGER DEFAULT 1,
                created_at TEXT NOT NULL DEFAULT(datetime('now')),
                FOREIGN KEY(parent_id) REFERENCES functions(id)
            )
            """
        )

        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS permissions(
                id integer PRIMARY KEY AUTOINCREMENT,
                role_id INTEGER NOT NULL,
                function_id INTEGER NOT NULL,
                created_at TEXT NOT NULL DEFAULT(datetime('now')),
                FOREIGN KEY(role_id) REFERENCES roles(id),
                FOREIGN KEY(function_id) REFERENCES functions(id),
                UNIQUE(role_id, function_id)
            )
            """
        )

        cursor = conn.execute("PRAGMA table_info(users)")
        columns = [row[1] for row in cursor.fetchall()]
        if "created_at" not in columns:
            conn.execute("ALTER TABLE users ADD COLUMN created_at TEXT DEFAULT NULL")
            conn.execute("UPDATE users SET created_at = datetime('now') WHERE created_at IS NULL")
            conn.execute("ALTER TABLE users RENAME TO users_old")
            conn.execute(
                """
                CREATE TABLE users(
                    id integer PRIMARY KEY AUTOINCREMENT,
                    username TEXT NOT NULL UNIQUE,
                    password_hash TEXT NOT NULL,
                    salt TEXT NOT NULL,
                    role_id INTEGER DEFAULT 1,
                    created_at TEXT NOT NULL DEFAULT(datetime('now')),
                    FOREIGN KEY(role_id) REFERENCES roles(id)
                )
                """
            )
            conn.execute(
                "INSERT INTO users(id, username, password_hash, salt, created_at) "
                "SELECT id, username, password_hash, salt, created_at FROM users_old"
            )
            conn.execute("DROP TABLE users_old")

        cursor = conn.execute("PRAGMA table_info(users)")
        columns = [row[1] for row in cursor.fetchall()]
        if "role_id" not in columns:
            conn.execute("ALTER TABLE users ADD COLUMN role_id INTEGER DEFAULT 1")

        _initialize_default_entries(conn)


def _initialize_default_entries(conn):
    cursor = conn.execute("SELECT id FROM roles WHERE name = ?", ("超级管理员",))
    row = cursor.fetchone()
    if not row:
        conn.execute(
            "INSERT INTO roles(name, description, is_system) VALUES(?, ?, ?)",
            ("超级管理员", "系统最高权限角色，拥有全部操作权限", 1)
        )

    default_funcs = [
        (1, "控制台", "dashboard", "/admin/dashboard", "fa fa-home", 0, 1),
        (1, "账户管理", "user_manage", "", "fa fa-users", 1, 1),
        (1, "功能配置", "function_manage", "", "fa fa-cogs", 2, 1),
        (1, "角色配置", "role_manage", "", "fa fa-user-tag", 3, 1),
        (1, "权限配置", "permission_manage", "", "fa fa-lock", 4, 1),
        (1, "数字员工", "digital_staff", "", "fa fa-robot", 5, 1),
        (1, "模型引擎", "model_engine", "", "fa fa-brain", 6, 1),
        (1, "瞭望监控", "watch_manage", "", "fa fa-eye", 7, 1),
        (1, "数据中心", "data_warehouse", "", "fa fa-database", 8, 1),
        (1, "数据大屏", "data_screen", "", "fa fa-chart-bar", 9, 1),
        (1, "系统设置", "system_settings", "", "fa fa-cog", 10, 1),
        (2, "账户列表", "user_list", "/admin/users", "", 0, 1),
        (2, "新建账户", "user_add", "/admin/users/add", "", 1, 1),
    ]

    for func in default_funcs:
        parent_id, name, code, url, icon, sort_order, is_menu = func
        cursor = conn.execute("SELECT id FROM functions WHERE code = ?", (code,))
        if not cursor.fetchone():
            conn.execute(
                "INSERT INTO functions(name, code, parent_id, url, icon, sort_order, is_menu) VALUES(?, ?, ?, ?, ?, ?, ?)",
                (name, code, parent_id, url, icon, sort_order, is_menu)
            )

    role_cursor = conn.execute("SELECT id FROM roles WHERE name = ?", ("超级管理员",))
    role_id = role_cursor.fetchone()[0]

    func_cursor = conn.execute("SELECT id FROM functions")
    for func_row in func_cursor.fetchall():
        func_id = func_row[0]
        try:
            conn.execute(
                "INSERT INTO permissions(role_id, function_id) VALUES(?, ?)",
                (role_id, func_id)
            )
        except sqlite3.IntegrityError:
            pass
