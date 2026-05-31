import tornado.web


class BaseHandler(tornado.web.RequestHandler):
    def get_current_user(self):
        user_name = self.get_secure_cookie("username")
        if not user_name:
            return None
        return user_name.decode('utf-8')


class GuestLoginHandler(BaseHandler):
    def get(self):
        self.render("login.html", title="用户登录入口", error_msg=None)

    def post(self):
        user_name = (self.get_body_argument("username", "") or "").strip()
        pass_word = self.get_body_argument("password", "")

        if not user_name or not pass_word:
            self.set_status(400)
            return self.render("login.html", title="用户登录入口", error_msg="请输入完整的账号信息")

        from app.models.user import UserRepository
        if not UserRepository.verify_user(user_name, pass_word):
            self.set_status(401)
            return self.render("login.html", title="用户登录入口", error_msg="账号或密码不正确")

        self.set_secure_cookie("username", user_name)
        self.redirect("/")


class GuestLogoutHandler(BaseHandler):
    def post(self):
        self.clear_cookie("username")
        self.redirect("/auth/login")


class ManagerLoginHandler(BaseHandler):
    def get_current_user(self):
        admin_name = self.get_secure_cookie("admin_user")
        if admin_name:
            return admin_name.decode('utf-8')
        user_name = self.get_secure_cookie("username")
        if user_name:
            return user_name.decode('utf-8')
        return None

    def get(self):
        self.render("admin-login.html", title="系统管理登录", error_msg=None)

    def post(self):
        user_name = (self.get_body_argument("username", "") or "").strip()
        pass_word = self.get_body_argument("password", "")

        if not user_name or not pass_word:
            self.set_status(400)
            return self.render("admin-login.html", title="系统管理登录", error_msg="请填写用户名和密码")

        if user_name == "system_admin" and pass_word == "sys@2026#admin":
            self.set_secure_cookie("admin_user", user_name)
            self.redirect("/admin/dashboard")
        else:
            self.set_status(401)
            return self.render("admin-login.html", title="系统管理登录", error_msg="登录信息有误，请重试")


class ManagerLogoutHandler(BaseHandler):
    def post(self):
        self.clear_cookie("admin_user")
        self.redirect("/admin/login")


class IndexPageHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        self.redirect("/admin/dashboard")
