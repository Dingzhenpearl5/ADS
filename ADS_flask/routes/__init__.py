"""
路由模块初始化
"""
from routes.auth import auth_bp
from routes.diagnosis import diagnosis_bp
from routes.patient import patient_bp
from routes.system import system_bp
from routes.user import user_bp

def register_blueprints(app):
    """注册所有蓝图"""
    app.register_blueprint(auth_bp, url_prefix='/api')
    app.register_blueprint(diagnosis_bp, url_prefix='/api')
    app.register_blueprint(patient_bp, url_prefix='/api')
    app.register_blueprint(system_bp, url_prefix='/api')
    app.register_blueprint(user_bp, url_prefix='/api')
