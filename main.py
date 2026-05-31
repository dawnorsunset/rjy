import os
import tornado.ioloop
import tornado.web
from tornado.httpserver import HTTPServer

from app.controllers.auth import GuestLoginHandler, GuestLogoutHandler, ManagerLoginHandler, ManagerLogoutHandler, IndexPageHandler
from app.controllers.admin_dashboard import AdminDashboardHandler
from app.controllers.users import UsersHandler, UserAddHandler
from app.controllers.functions import FunctionManageHandler
from app.controllers.roles import RoleManageHandler
from app.controllers.permissions import PermissionManageHandler
from app.models.db import init_db


def create_app():
    app_directory = os.path.dirname(os.path.abspath(__file__))
    config_settings = dict(
        template_path=os.path.join(app_directory, "app", "templates"),
        static_path=os.path.join(app_directory, "app", "static"),
        cookie_secret="cnagentos-secure-key-2026-change-before-deploy",
        login_url="/auth/login",
        xsrf_cookies=True,
        debug=True,
        autoreload=True
    )
    return tornado.web.Application([
            (r"/", IndexPageHandler),
            (r"/auth/login", GuestLoginHandler),
            (r"/auth/logout", GuestLogoutHandler),
            (r"/admin/login", ManagerLoginHandler),
            (r"/admin/logout", ManagerLogoutHandler),
            (r"/admin/dashboard", AdminDashboardHandler),
            (r"/admin/users", UsersHandler),
            (r"/admin/users/add", UserAddHandler),
            (r"/admin/functions", FunctionManageHandler),
            (r"/admin/roles", RoleManageHandler),
            (r"/admin/permissions", PermissionManageHandler)
        ],
        **config_settings
    )


if __name__ == "__main__":
    init_db()
    app_instance = create_app()
    http_server = HTTPServer(app_instance)
    http_server.bind(8088)
    http_server.start(1)
    print("**********服务已启动**********端口: 8088**********", flush=True)
    tornado.ioloop.IOLoop.current().start()
