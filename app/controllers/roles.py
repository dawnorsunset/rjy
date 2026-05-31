import json
import tornado.web
from app.controllers.auth import BaseHandler
from app.models.permission import RoleRepository


class RoleManageHandler(BaseHandler):
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
        roles_list = RoleRepository.get_all_roles()
        self.render(
            "admin-roles.html",
            title="角色配置",
            username=self.current_user,
            current_page="role_manage",
            roles=roles_list
        )

    def post(self):
        action_type = self.get_argument("action", "")

        if action_type == "add":
            role_name = (self.get_body_argument("name", "") or "").strip()
            role_desc = (self.get_body_argument("description", "") or "").strip()

            if not role_name:
                self.write(json.dumps({"code": 1, "msg": "请输入角色名称"}))
                return

            if RoleRepository.get_role_by_name(role_name):
                self.write(json.dumps({"code": 1, "msg": "该角色名称已存在"}))
                return

            if RoleRepository.create_role(role_name, role_desc):
                self.write(json.dumps({"code": 0, "msg": "角色创建成功"}))
            else:
                self.write(json.dumps({"code": 1, "msg": "角色创建失败"}))

        elif action_type == "edit":
            role_id = int(self.get_body_argument("role_id", 0))
            role_name = (self.get_body_argument("name", "") or "").strip()
            role_desc = (self.get_body_argument("description", "") or "").strip()

            if not role_id or not role_name:
                self.write(json.dumps({"code": 1, "msg": "输入信息不完整"}))
                return

            role_info = RoleRepository.get_role_by_id(role_id)
            if not role_info:
                self.write(json.dumps({"code": 1, "msg": "角色不存在"}))
                return

            RoleRepository.update_role(role_id, role_name, role_desc)
            self.write(json.dumps({"code": 0, "msg": "角色信息已更新"}))

        elif action_type == "delete":
            role_id = int(self.get_body_argument("role_id", 0))
            if role_id:
                role_info = RoleRepository.get_role_by_id(role_id)
                if role_info and role_info["is_system"]:
                    self.write(json.dumps({"code": 1, "msg": "系统内置角色无法删除"}))
                    return

                if RoleRepository.delete_role(role_id):
                    self.write(json.dumps({"code": 0, "msg": "角色已删除"}))
                else:
                    self.write(json.dumps({"code": 1, "msg": "删除失败"}))
            else:
                self.write(json.dumps({"code": 1, "msg": "请选择要删除的角色"}))
