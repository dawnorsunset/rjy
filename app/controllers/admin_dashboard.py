import tornado.web
from app.controllers.auth import BaseHandler


class AdminDashboardHandler(BaseHandler):
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
        self.render("admin-dashboard.html", title="系统控制中心", username=self.current_user, current_page="dashboard")
