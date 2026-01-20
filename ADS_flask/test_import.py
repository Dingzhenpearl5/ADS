"""测试导入和语法检查"""
try:
    print("开始导入 app 模块...")
    import app
    print("✓ app 模块导入成功")
    print("✓ 语法检查通过")
    print(f"✓ 服务器配置: {app.SERVER_URL}")
except Exception as e:
    print(f"✗ 错误: {e}")
    import traceback
    traceback.print_exc()
