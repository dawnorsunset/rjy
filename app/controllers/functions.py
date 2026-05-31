import json
import tornado.web
from app.controllers.auth import BaseHandler
from app.models.permission import FunctionRepository


class FunctionManageHandler(BaseHandler):
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
        funcs = FunctionRepository.get_all_functions()
        nav_tree = FunctionRepository.get_menu_tree()
        self.render(
            "admin-functions.html",
            title="功能配置",
            username=self.current_user,
            current_page="function_manage",
            functions=funcs,
            menu_tree=nav_tree
        )

    def post(self):
        action_type = self.get_argument("action", "")

        if action_type == "add":
            func_name = (self.get_body_argument("name", "") or "").strip()
            func_code = (self.get_body_argument("code", "") or "").strip()
            parent_id = int(self.get_body_argument("parent_id", 0))
            func_url = self.get_body_argument("url", "").strip()
            func_icon = self.get_body_argument("icon", "").strip()
            sort_val = int(self.get_body_argument("sort_order", 0))
            show_menu = int(self.get_body_argument("is_menu", 1))

            if not func_name or not func_code:
                self.write(json.dumps({"code": 1, "msg": "请输入功能名称和标识"}))
                return

            if FunctionRepository.create_function(func_name, func_code, parent_id, func_url, func_icon, sort_val, show_menu):
                self.write(json.dumps({"code": 0, "msg": "功能添加成功"}))
            else:
                self.write(json.dumps({"code": 1, "msg": "该功能标识已存在"}))

        elif action_type == "edit":
            func_id = int(self.get_body_argument("func_id", 0))
            func_name = (self.get_body_argument("name", "") or "").strip()
            func_code = (self.get_body_argument("code", "") or "").strip()
            parent_id = int(self.get_body_argument("parent_id", 0))
            func_url = self.get_body_argument("url", "").strip()
            func_icon = self.get_body_argument("icon", "").strip()
            sort_val = int(self.get_body_argument("sort_order", 0))
            show_menu = int(self.get_body_argument("is_menu", 1))

            if not func_id or not func_name or not func_code:
                self.write(json.dumps({"code": 1, "msg": "输入信息不完整"}))
                return

            FunctionRepository.update_function(func_id, func_name, func_code, parent_id, func_url, func_icon, sort_val, show_menu)
            self.write(json.dumps({"code": 0, "msg": "功能信息已更新"}))

        elif action_type == "delete":
            func_id = int(self.get_body_argument("func_id", 0))
            if func_id:
                FunctionRepository.delete_function(func_id)
                self.write(json.dumps({"code": 0, "msg": "功能已删除"}))
            else:
                self.write(json.dumps({"code": 1, "msg": "请选择要删除的功能"}))
