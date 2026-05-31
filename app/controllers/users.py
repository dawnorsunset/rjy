import json
import tornado.web
from app.controllers.auth import BaseHandler
from app.models.user import UserRepository
from app.models.permission import RoleRepository


class UsersHandler(BaseHandler):
    def get_current_user(self):
        return self.get_secure_cookie("admin_user")

    @tornado.web.authenticated
    def get(self):
        page_num = int(self.get_argument("page", 1))
        search_key = self.get_argument("keyword", "").strip()
        per_page = 20

        if search_key:
            users_data, total_count = UserRepository.search_users(search_key, page_num, per_page)
        else:
            users_data, total_count = UserRepository.get_all_users_with_roles(page_num, per_page)

        total_pages = (total_count + per_page - 1) // per_page
        all_roles = RoleRepository.get_all_roles()

        self.render(
            "admin-users.html",
            title="账户管理",
            username=self.current_user,
            current_page="user_list",
            users=users_data,
            page=page_num,
            total=total_count,
            total_pages=total_pages,
            keyword=search_key,
            roles=all_roles
        )

    def post(self):
        action_type = self.get_argument("action", "")

        if action_type == "add":
            new_name = (self.get_body_argument("username", "") or "").strip()
            new_pass = self.get_body_argument("password", "")

            if not new_name or not new_pass:
                self.write(json.dumps({"code": 1, "msg": "请输入账号和密码"}))
                return

            if UserRepository.create_user(new_name, new_pass):
                self.write(json.dumps({"code": 0, "msg": "账号创建成功"}))
            else:
                self.write(json.dumps({"code": 1, "msg": "该账号已存在"}))

        elif action_type == "edit":
            uid = int(self.get_body_argument("user_id", 0))
            new_name = (self.get_body_argument("username", "") or "").strip()

            if not uid or not new_name:
                self.write(json.dumps({"code": 1, "msg": "输入信息不完整"}))
                return

            UserRepository.update_user(uid, new_name)
            self.write(json.dumps({"code": 0, "msg": "信息更新成功"}))

        elif action_type == "edit_password":
            uid = int(self.get_body_argument("user_id", 0))
            new_pass = self.get_body_argument("password", "")

            if not uid or not new_pass:
                self.write(json.dumps({"code": 1, "msg": "输入信息不完整"}))
                return

            UserRepository.update_user_password(uid, new_pass)
            self.write(json.dumps({"code": 0, "msg": "密码已更新"}))

        elif action_type == "set_role":
            uid = int(self.get_body_argument("user_id", 0))
            rid = int(self.get_body_argument("role_id", 0))

            if not uid or not rid:
                self.write(json.dumps({"code": 1, "msg": "输入信息不完整"}))
                return

            target_user = UserRepository.get_user_by_id(uid)
            if target_user and target_user["username"] == "admin":
                self.write(json.dumps({"code": 1, "msg": "超级管理员角色不可变更"}))
                return

            UserRepository.set_user_role(uid, rid)
            self.write(json.dumps({"code": 0, "msg": "角色已更新"}))

        elif action_type == "delete":
            uid = int(self.get_body_argument("user_id", 0))
            if uid:
                target_user = UserRepository.get_user_by_id(uid)
                if target_user and target_user["username"] == "admin":
                    self.write(json.dumps({"code": 1, "msg": "超级管理员账号不可删除"}))
                    return

                UserRepository.delete_user(uid)
                self.write(json.dumps({"code": 0, "msg": "已删除该账号"}))
            else:
                self.write(json.dumps({"code": 1, "msg": "请选择要删除的账号"}))

        elif action_type == "batch_delete":
            ids_str = self.get_body_argument("user_ids", "")
            if ids_str:
                ids_list = [int(i) for i in ids_str.split(",")]

                for uid in ids_list:
                    target_user = UserRepository.get_user_by_id(uid)
                    if target_user and target_user["username"] == "admin":
                        self.write(json.dumps({"code": 1, "msg": "超级管理员账号不可删除"}))
                        return

                UserRepository.batch_delete_users(ids_list)
                self.write(json.dumps({"code": 0, "msg": "批量删除完成"}))
            else:
                self.write(json.dumps({"code": 1, "msg": "请选择要删除的账号"}))


class UserAddHandler(BaseHandler):
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
        self.render(
            "admin-user-add.html",
            title="创建新账户",
            username=self.current_user,
            current_page="user_add"
        )
