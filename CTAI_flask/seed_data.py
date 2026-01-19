"""
数据库测试数据填充脚本
运行此脚本会向数据库添加模拟的患者和诊断记录数据
"""
import sys
import os
import random
import json
from datetime import datetime, timedelta

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("=" * 60)
print("直肠肿瘤辅助诊断系统 - 测试数据填充工具")
print("=" * 60)

try:
    print("\n[1/4] 导入必要的模块...")
    from app import db, app, User, Patient, DiagnosisRecord
    import hashlib
    
    print("✓ 模块导入成功")
    
    # 模拟姓名
    SURNAMES = ['张', '王', '李', '赵', '刘', '陈', '杨', '黄', '周', '吴', 
                '徐', '孙', '马', '朱', '胡', '郭', '何', '高', '林', '郑']
    NAMES = ['伟', '芳', '娜', '秀英', '敏', '静', '丽', '强', '磊', '洋',
             '艳', '勇', '军', '杰', '娟', '涛', '明', '超', '秀兰', '霞',
             '平', '刚', '桂英', '华', '建华', '文', '建国', '建军', '斌', '波']
    
    def random_name():
        return random.choice(SURNAMES) + random.choice(NAMES) + random.choice(['', random.choice(NAMES)])
    
    def random_phone():
        return '1' + str(random.choice([3, 5, 7, 8, 9])) + ''.join([str(random.randint(0, 9)) for _ in range(9)])
    
    # 模拟特征数据
    def generate_features():
        return {
            '面积': round(random.uniform(50, 500), 2),
            '周长': round(random.uniform(20, 100), 2),
            '圆度': round(random.uniform(0.6, 0.95), 3),
            '紧凑度': round(random.uniform(0.7, 0.98), 3),
            '偏心率': round(random.uniform(0.1, 0.8), 3),
            '等效直径': round(random.uniform(8, 25), 2),
            '主轴长度': round(random.uniform(15, 40), 2),
            '次轴长度': round(random.uniform(10, 30), 2)
        }
    
    with app.app_context():
        print("\n[2/4] 创建更多医生用户...")
        
        # 添加更多医生
        doctors_data = [
            ('zhangwei', '医生张伟', 'doctor123'),
            ('lina', '医生李娜', 'doctor123'),
            ('wangqiang', '医生王强', 'doctor123'),
        ]
        
        for username, name, password in doctors_data:
            if not User.query.filter_by(username=username).first():
                user = User(
                    username=username,
                    password=hashlib.sha256(password.encode()).hexdigest(),
                    name=name,
                    role='doctor'
                )
                db.session.add(user)
                print(f"  ✓ 添加医生: {name} ({username})")
        
        db.session.commit()
        
        print("\n[3/4] 创建患者数据...")
        
        # 生成更多患者
        patient_count = Patient.query.count()
        patients_to_add = max(0, 30 - patient_count)  # 确保至少有30个患者
        
        existing_ids = [p.patient_id for p in Patient.query.all()]
        
        for i in range(patients_to_add):
            # 生成唯一的患者ID
            patient_id = f"2024{str(1001 + patient_count + i).zfill(4)}"
            while patient_id in existing_ids:
                patient_id = f"2024{str(random.randint(1000, 9999)).zfill(4)}"
            
            patient = Patient(
                patient_id=patient_id,
                name=random_name(),
                gender=random.choice(['男', '女']),
                age=random.randint(25, 75),
                phone=random_phone(),
                part='直肠'
            )
            db.session.add(patient)
            existing_ids.append(patient_id)
            print(f"  ✓ 添加患者: {patient.name} (ID: {patient_id})")
        
        db.session.commit()
        
        print("\n[4/4] 创建诊断记录...")
        
        # 获取所有患者和医生
        patients = Patient.query.all()
        doctors = User.query.filter_by(role='doctor').all()
        
        # 为每个患者添加1-3条诊断记录
        diagnosis_count = DiagnosisRecord.query.count()
        
        if diagnosis_count < 50:
            records_to_add = 50 - diagnosis_count
            
            for i in range(records_to_add):
                patient = random.choice(patients)
                doctor = random.choice(doctors) if doctors else None
                
                # 随机时间（过去30天内）
                days_ago = random.randint(0, 30)
                hours_ago = random.randint(0, 23)
                minutes_ago = random.randint(0, 59)
                created_at = datetime.now() - timedelta(days=days_ago, hours=hours_ago, minutes=minutes_ago)
                
                features = generate_features()
                
                record = DiagnosisRecord(
                    patient_id=patient.patient_id,
                    doctor_username=doctor.username if doctor else 'doctor',
                    filename=f'{patient.patient_id}.dcm',
                    image_url=f'http://127.0.0.1:5003/tmp/image/{patient.patient_id}.png',
                    draw_url=f'http://127.0.0.1:5003/tmp/draw/{patient.patient_id}.png',
                    area=features['面积'],
                    perimeter=features['周长'],
                    features=json.dumps(features, ensure_ascii=False),
                    created_at=created_at
                )
                db.session.add(record)
                
                if (i + 1) % 10 == 0:
                    print(f"  ✓ 已添加 {i + 1} 条诊断记录...")
            
            db.session.commit()
            print(f"  ✓ 共添加 {records_to_add} 条诊断记录")
        else:
            print(f"  ℹ 已有 {diagnosis_count} 条诊断记录，跳过")
        
        # 统计信息
        print("\n" + "-" * 40)
        print("数据库统计:")
        print(f"  - 用户总数: {User.query.count()}")
        print(f"  - 患者总数: {Patient.query.count()}")
        print(f"  - 诊断记录: {DiagnosisRecord.query.count()}")
        print("-" * 40)
        
    print("\n" + "=" * 60)
    print("✓ 测试数据填充完成！")
    print("=" * 60)
    
except Exception as e:
    print(f"\n✗ 错误: {e}")
    import traceback
    traceback.print_exc()
    print("\n请确保:")
    print("1. MySQL服务已启动")
    print("2. 数据库 'ctai_db' 已创建")
    print("3. 数据库连接信息正确")
