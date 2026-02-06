"""
数据库模型定义
"""
import datetime
import json
from extensions import db


class User(db.Model):
    """用户模型"""
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    name = db.Column(db.String(50))
    role = db.Column(db.String(20))
    status = db.Column(db.String(20), default='active')  # active/disabled
    permissions = db.Column(db.Text)  # JSON数组：允许访问的诊断模块
    created_at = db.Column(db.DateTime, default=datetime.datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now)
    
    def get_permissions(self):
        """获取权限列表"""
        try:
            return json.loads(self.permissions) if self.permissions else ['rectum']
        except:
            return ['rectum']
    
    def to_dict(self, include_permissions=True):
        """转换为字典"""
        data = {
            'id': self.id,
            'username': self.username,
            'name': self.name,
            'role': self.role,
            'status': self.status or 'active',
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None,
            'updated_at': self.updated_at.strftime('%Y-%m-%d %H:%M:%S') if self.updated_at else None
        }
        if include_permissions:
            data['permissions'] = self.get_permissions()
        return data


class Token(db.Model):
    """Token模型"""
    __tablename__ = 'tokens'
    id = db.Column(db.Integer, primary_key=True)
    token = db.Column(db.String(100), unique=True, nullable=False)
    username = db.Column(db.String(50), db.ForeignKey('users.username'), nullable=False)
    login_time = db.Column(db.DateTime, default=datetime.datetime.now)
    expire_time = db.Column(db.DateTime, nullable=False)
    
    user = db.relationship('User', backref=db.backref('tokens', lazy=True))


class LoginAttempt(db.Model):
    """登录失败记录模型"""
    __tablename__ = 'login_attempts'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=False)
    attempt_time = db.Column(db.DateTime, default=datetime.datetime.now)
    success = db.Column(db.Boolean, default=False)
    ip_address = db.Column(db.String(50))


class Patient(db.Model):
    """病人模型"""
    __tablename__ = 'patients'
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.String(50), unique=True, nullable=False)
    name = db.Column(db.String(50), nullable=False)
    gender = db.Column(db.String(10))
    age = db.Column(db.Integer)
    phone = db.Column(db.String(20))
    part = db.Column(db.String(50))
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'patient_id': self.patient_id,
            'name': self.name,
            'gender': self.gender,
            'age': self.age,
            'phone': self.phone,
            'part': self.part
        }


class DiagnosisRecord(db.Model):
    """诊断记录模型"""
    __tablename__ = 'diagnosis_records'
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.String(50), db.ForeignKey('patients.patient_id'), nullable=True)
    doctor_username = db.Column(db.String(50), db.ForeignKey('users.username'), nullable=True)
    
    # 文件信息
    filename = db.Column(db.String(255), nullable=False)
    image_url = db.Column(db.String(500))
    draw_url = db.Column(db.String(500))
    
    # 诊断结果
    area = db.Column(db.Float)
    perimeter = db.Column(db.Float)
    features = db.Column(db.Text)  # JSON格式
    
    # 医生诊断记录
    doctor_diagnosis = db.Column(db.Text)
    doctor_suggestion = db.Column(db.Text)
    diagnosis_conclusion = db.Column(db.String(100))
    
    # 时间信息
    created_at = db.Column(db.DateTime, default=datetime.datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now)
    
    # 关系
    patient = db.relationship('Patient', backref=db.backref('diagnoses', lazy=True))
    doctor = db.relationship('User', backref=db.backref('diagnoses', lazy=True))
    
    def to_dict(self, include_patient=False):
        """转换为字典"""
        # 解析 features JSON
        features_data = json.loads(self.features) if self.features else {}

        # 从 [中文名, 数值] 格式或直接数值中提取
        def _val(d, key):
            v = d.get(key, 0)
            if isinstance(v, list):
                return v[1] if len(v) > 1 else v[0]
            return v

        normalized_features = {
            'area': _val(features_data, 'area'),
            'perimeter': _val(features_data, 'perimeter'),
            'ellipse': _val(features_data, 'ellipse'),
            'mean': _val(features_data, 'mean'),
            'std': _val(features_data, 'std'),
        }
        
        data = {
            'id': self.id,
            'patient_id': self.patient_id,
            'doctor_username': self.doctor_username,
            'doctor': self.doctor.name if self.doctor else self.doctor_username,  # 前端显示用
            'filename': self.filename,
            'image_url': self.image_url,
            'draw_url': self.draw_url,
            'original_url': self.image_url,  # 前端兼容别名
            'mask_url': self.draw_url,       # 前端兼容别名
            'area': self.area,
            'perimeter': self.perimeter,
            'features': normalized_features,
            'doctor_diagnosis': self.doctor_diagnosis,
            'doctor_suggestion': self.doctor_suggestion,
            'diagnosis_conclusion': self.diagnosis_conclusion,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None,
            'updated_at': self.updated_at.strftime('%Y-%m-%d %H:%M:%S') if self.updated_at else None
        }
        if include_patient and self.patient:
            data['patient_name'] = self.patient.name
        return data


class SystemSetting(db.Model):
    """系统设置模型"""
    __tablename__ = 'system_settings'
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(100), unique=True, nullable=False)
    value = db.Column(db.Text)
    description = db.Column(db.String(255))
    category = db.Column(db.String(50))
    updated_at = db.Column(db.DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now)
    updated_by = db.Column(db.String(50))
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'key': self.key,
            'value': self.value,
            'description': self.description,
            'category': self.category,
            'updated_at': self.updated_at.strftime('%Y-%m-%d %H:%M:%S') if self.updated_at else None,
            'updated_by': self.updated_by
        }


class Announcement(db.Model):
    """系统公告模型"""
    __tablename__ = 'announcements'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    type = db.Column(db.String(20), default='info')
    priority = db.Column(db.Integer, default=0)
    status = db.Column(db.String(20), default='draft')
    created_by = db.Column(db.String(50), db.ForeignKey('users.username'))
    created_at = db.Column(db.DateTime, default=datetime.datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now)
    published_at = db.Column(db.DateTime)
    
    author = db.relationship('User', backref=db.backref('announcements', lazy=True))
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'title': self.title,
            'content': self.content,
            'type': self.type,
            'priority': self.priority,
            'status': self.status,
            'created_by': self.created_by,
            'author_name': self.author.name if self.author else None,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None,
            'updated_at': self.updated_at.strftime('%Y-%m-%d %H:%M:%S') if self.updated_at else None,
            'published_at': self.published_at.strftime('%Y-%m-%d %H:%M:%S') if self.published_at else None
        }


class AuditLog(db.Model):
    """审计日志模型"""
    __tablename__ = 'audit_logs'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), db.ForeignKey('users.username'), nullable=True)
    action = db.Column(db.String(50), nullable=False)
    module = db.Column(db.String(50), nullable=False)
    target = db.Column(db.String(255))
    detail = db.Column(db.Text)
    ip_address = db.Column(db.String(50))
    user_agent = db.Column(db.String(500))
    status = db.Column(db.String(20), default='success')
    created_at = db.Column(db.DateTime, default=datetime.datetime.now)
    
    user = db.relationship('User', backref=db.backref('audit_logs', lazy=True))
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'username': self.username,
            'user_name': self.user.name if self.user else None,
            'action': self.action,
            'module': self.module,
            'target': self.target,
            'detail': self.detail,
            'ip_address': self.ip_address,
            'user_agent': self.user_agent,
            'status': self.status,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None
        }
