from app.models.db import establish_connection


class RoleRepository:
    @staticmethod
    def create_role(role_name: str, role_desc: str = "") -> bool:
        try:
            with establish_connection() as conn:
                conn.execute(
                    "INSERT INTO roles(name, description, is_system) VALUES(?, ?, ?)",
                    (role_name, role_desc, 0)
                )
            return True
        except Exception:
            return False

    @staticmethod
    def get_all_roles():
        with establish_connection() as conn:
            rows = conn.execute(
                "SELECT id, name, description, is_system, created_at FROM roles ORDER BY id"
            ).fetchall()
        return rows

    @staticmethod
    def get_role_by_id(role_id: int):
        with establish_connection() as conn:
            row = conn.execute(
                "SELECT id, name, description, is_system, created_at FROM roles WHERE id = ?",
                (role_id,)
            ).fetchone()
        return row

    @staticmethod
    def update_role(role_id: int, role_name: str, role_desc: str):
        with establish_connection() as conn:
            conn.execute(
                "UPDATE roles SET name = ?, description = ? WHERE id = ?",
                (role_name, role_desc, role_id)
            )

    @staticmethod
    def delete_role(role_id: int) -> bool:
        role_info = RoleRepository.get_role_by_id(role_id)
        if role_info and role_info["is_system"]:
            return False

        with establish_connection() as conn:
            conn.execute("DELETE FROM permissions WHERE role_id = ?", (role_id,))
            conn.execute("DELETE FROM roles WHERE id = ?", (role_id,))
        return True

    @staticmethod
    def get_role_by_name(role_name: str):
        with establish_connection() as conn:
            row = conn.execute(
                "SELECT id, name, description, is_system FROM roles WHERE name = ?",
                (role_name,)
            ).fetchone()
        return row


class FunctionRepository:
    @staticmethod
    def get_all_functions():
        with establish_connection() as conn:
            rows = conn.execute(
                "SELECT id, name, code, parent_id, url, icon, sort_order, is_menu FROM functions ORDER BY sort_order, id"
            ).fetchall()
        return rows

    @staticmethod
    def get_menu_tree():
        with establish_connection() as conn:
            parent_menus = conn.execute(
                "SELECT id, name, code, url, icon, sort_order FROM functions WHERE parent_id = 0 OR parent_id = 1 ORDER BY sort_order, id"
            ).fetchall()

            menus = []
            for parent in parent_menus:
                menu = dict(parent)
                children = conn.execute(
                    "SELECT id, name, code, url, icon FROM functions WHERE parent_id = ? ORDER BY id",
                    (parent["id"],)
                ).fetchall()
                menu["children"] = [dict(child) for child in children] if children else []
                menus.append(menu)

        return menus

    @staticmethod
    def get_function_by_id(func_id: int):
        with establish_connection() as conn:
            row = conn.execute(
                "SELECT id, name, code, parent_id, url, icon, sort_order, is_menu FROM functions WHERE id = ?",
                (func_id,)
            ).fetchone()
        return row

    @staticmethod
    def create_function(func_name: str, func_code: str, parent_id: int = 0, func_url: str = "",
                       func_icon: str = "", sort_val: int = 0, show_menu: int = 1) -> bool:
        try:
            with establish_connection() as conn:
                conn.execute(
                    "INSERT INTO functions(name, code, parent_id, url, icon, sort_order, is_menu) VALUES(?, ?, ?, ?, ?, ?, ?)",
                    (func_name, func_code, parent_id, func_url, func_icon, sort_val, show_menu)
                )
            return True
        except Exception:
            return False

    @staticmethod
    def update_function(func_id: int, func_name: str, func_code: str, parent_id: int = 0,
                       func_url: str = "", func_icon: str = "", sort_val: int = 0, show_menu: int = 1):
        with establish_connection() as conn:
            conn.execute(
                "UPDATE functions SET name = ?, code = ?, parent_id = ?, url = ?, icon = ?, sort_order = ?, is_menu = ? WHERE id = ?",
                (func_name, func_code, parent_id, func_url, func_icon, sort_val, show_menu, func_id)
            )

    @staticmethod
    def delete_function(func_id: int):
        with establish_connection() as conn:
            conn.execute("DELETE FROM permissions WHERE function_id = ?", (func_id,))
            conn.execute("DELETE FROM functions WHERE id = ?", (func_id,))


class PermissionRepository:
    @staticmethod
    def get_permissions_by_role(role_id: int):
        with establish_connection() as conn:
            rows = conn.execute(
                "SELECT function_id FROM permissions WHERE role_id = ?",
                (role_id,)
            ).fetchall()
        return [row["function_id"] for row in rows]

    @staticmethod
    def grant_permission(role_id: int, func_id: int) -> bool:
        try:
            with establish_connection() as conn:
                conn.execute(
                    "INSERT INTO permissions(role_id, function_id) VALUES(?, ?)",
                    (role_id, func_id)
                )
            return True
        except Exception:
            return False

    @staticmethod
    def revoke_permission(role_id: int, func_id: int):
        with establish_connection() as conn:
            conn.execute(
                "DELETE FROM permissions WHERE role_id = ? AND function_id = ?",
                (role_id, func_id)
            )

    @staticmethod
    def save_permissions(role_id: int, func_ids: list):
        with establish_connection() as conn:
            conn.execute("DELETE FROM permissions WHERE role_id = ?", (role_id,))
            for func_id in func_ids:
                try:
                    conn.execute(
                        "INSERT INTO permissions(role_id, function_id) VALUES(?, ?)",
                        (role_id, func_id)
                    )
                except Exception:
                    pass
