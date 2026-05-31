from app.models.user import UserRepository
from app.models.permission import RoleRepository

print("正在创建测试用户...")

if UserRepository.create_user("demo_user", "demo@2026#pass"):
    print("[OK] 测试用户创建成功：demo_user / demo@2026#pass")
else:
    print("[FAIL] 测试用户已存在")

if UserRepository.create_user("test_account", "test@2026#pass"):
    print("[OK] 用户创建成功：test_account / test@2026#pass")
else:
    print("[FAIL] 用户已存在")

super_admin = RoleRepository.get_role_by_name("超级管理员")
if super_admin:
    print(f"[OK] 超级管理员角色 ID: {super_admin['id']}")
    test_user = UserRepository.get_user_by_username("demo_user")
    if test_user:
        UserRepository.set_user_role(test_user['id'], super_admin['id'])
        print("[OK] 已将 demo_user 用户设置为超级管理员")

print("\n初始化完成！")
print("=" * 50)
print("登录方式 1 - 后台管理员：http://localhost:8088/admin/login")
print("  账号：system_admin / sys@2026#admin")
print("=" * 50)
print("登录方式 2 - 前台用户：http://localhost:8088/auth/login")
print("  账号：demo_user / demo@2026#pass")
print("  账号：test_account / test@2026#pass")
print("=" * 50)
