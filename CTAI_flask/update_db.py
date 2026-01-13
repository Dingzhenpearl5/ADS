"""数据库初始化和更新脚本"""
import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("=" * 60)
print("智医AI 数据库更新工具")
print("=" * 60)

try:
    print("\n[1/3] 导入必要的模块...")
    from app import db, app, User, Token, LoginAttempt
    import datetime
    
    print("✓ 模块导入成功")
    
    print("\n[2/3] 连接数据库并更新表结构...")
    with app.app_context():
        # 创建所有表（如果不存在）
        db.create_all()
        print("✓ 数据库表创建/更新成功")
        
        # 检查 tokens 表结构
        print("\n[3/3] 验证表结构...")
        from sqlalchemy import inspect
        inspector = inspect(db.engine)
        
        # 检查 tokens 表
        tokens_columns = [col['name'] for col in inspector.get_columns('tokens')]
        print(f"✓ tokens 表字段: {', '.join(tokens_columns)}")
        
        if 'expire_time' in tokens_columns:
            print("  ✓ expire_time 字段已存在")
        else:
            print("  ✗ expire_time 字段缺失")
        
        # 检查 login_attempts 表
        if 'login_attempts' in inspector.get_table_names():
            attempts_columns = [col['name'] for col in inspector.get_columns('login_attempts')]
            print(f"✓ login_attempts 表字段: {', '.join(attempts_columns)}")
        else:
            print("  ℹ login_attempts 表将被创建")
        
    print("\n" + "=" * 60)
    print("✓ 数据库更新完成！")
    print("=" * 60)
    
except Exception as e:
    print(f"\n✗ 错误: {e}")
    import traceback
    traceback.print_exc()
    print("\n请手动执行 update_database.sql 文件中的 SQL 语句")
