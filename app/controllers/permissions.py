import json
import tornado.web
from app.controllers.auth import BaseHandler
from app.models.permission import RoleRepository, FunctionRepository, PermissionRepository


class PermissionManageHandler(BaseHandler):
    def get_current_user(self):
        admin_name = self.get_secure_cookie("admin_user")
        if admin_name:
            return admin_name.decode('utf-8')
        user_name = self.get_secure_cookie("username")
        if user_name:
            return user_name.decode('utf-8')
        return None

    @tornado.web.authenticated
    def get(self):
        role_id_param = self.get_argument("role_id", None)
        roles_list = RoleRepository.get_all_roles()
        nav_tree = FunctionRepository.get_menu_tree()

        selected_id = None
        granted_perms = []

        if role_id_param:
            selected_id = int(role_id_param)
            granted_perms = PermissionRepository.get_permissions_by_role(selected_id)

        self.render(
            "admin-permissions.html",
            title="权限配置",
            username=self.current_user,
            current_page="permission_manage",
            roles=roles_list,
            menu_tree=nav_tree,
            selected_role_id=selected_id,
            selected_permissions=granted_perms
        )

    def post(self):
        action_type = self.get_argument("action", "")

        if action_type == "save":
            role_id = int(self.get_body_argument("role_id", 0))
            func_ids_str = self.get_body_argument("function_ids", "")

            if not role_id:
                self.write(json.dumps({"code": 1, "msg": "请选择角色"}))
                return

            func_ids = [int(fid) for fid in func_ids_str.split(",") if fid.strip()]

            PermissionRepository.save_permissions(role_id, func_ids)
            self.write(json.dumps({"code": 0, "msg": "权限设置已保存"}))
