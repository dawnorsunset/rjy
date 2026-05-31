# cnAgentOS 项目说明

## 项目概述
基于 Tornado 框架的 RBAC 后台管理系统

## 技术栈
- Web 框架: Tornado
- 数据库: SQLite
- 前端: Bootstrap 5.3.8 + FontAwesome 5.15.4

## 目录结构
```
cnAgentOS/
├── main.py                 # 应用入口
├── init_test_data.py       # 测试数据初始化脚本
├── app/
│   ├── controllers/        # 控制器层
│   │   ├── auth.py         # 认证相关 (登录/登出)
│   │   ├── admin_dashboard.py
│   │   ├── users.py        # 用户管理
│   │   ├── functions.py    # 功能菜单管理
│   │   ├── roles.py        # 角色管理
│   │   └── permissions.py   # 权限管理
│   ├── models/             # 数据模型层
│   │   ├── db.py           # 数据库连接
│   │   ├── user.py         # 用户仓储
│   │   └── permission.py   # 角色/功能/权限仓储
│   ├── templates/          # HTML 模板
│   └── static/             # 静态资源
└── database/               # SQLite 数据库目录
```

## 启动服务
```bash
cd cnAgentOS
python main.py
```
服务地址: http://localhost:8088

## 测试账号
| 登录入口 | 账号 | 密码 |
|---------|------|------|
| 后台管理员 | system_admin | sys@2026#admin |
| 前台用户 | demo_user | demo@2026#pass |
| 前台用户 | test_account | test@2026#pass |

## 路由列表
| 路径 | 说明 |
|------|------|
| / | 首页 |
| /auth/login | 用户登录 |
| /auth/logout | 用户登出 |
| /admin/login | 管理员登录 |
| /admin/logout | 管理员登出 |
| /admin/dashboard | 管理后台首页 |
| /admin/users | 用户管理 |
| /admin/users/add | 添加用户 |
| /admin/functions | 功能菜单管理 |
| /admin/roles | 角色管理 |
| /admin/permissions | 权限管理 |

## 数据库表结构
- **users**: 用户表 (id, username, password_hash, salt, role_id, created_at)
- **roles**: 角色表 (id, name, description, is_system, created_at)
- **functions**: 功能菜单表 (id, name, code, parent_id, url, icon, sort_order, is_menu, created_at)
- **permissions**: 权限关联表 (id, role_id, function_id, created_at)

## 初始化测试数据
```bash
python init_test_data.py
```

## 安全配置
- Cookie 密钥: `cnagentos-secure-key-2026-change-before-deploy`
- 密码加密: PBKDF2-SHA256 (100000 iterations)
- 启用 XSRF 保护

## 注意事项
1. 部署前请修改 `cookie_secret` 和数据库路径
2. `.venv/` 和 `venv/` 为 Python 虚拟环境目录，无需上传
3. `database/app_data.db` 为 SQLite 数据库文件，应定期备份
