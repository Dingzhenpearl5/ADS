"""
直肠肿瘤辅助诊断系统 - 主应用
重构版：使用 Blueprint 模块化组织代码
"""
import logging
from datetime import timedelta
from pathlib import Path

import torch
from flask import Flask, jsonify, redirect, url_for, send_from_directory, make_response, Response
from flask_socketio import emit

import config
from extensions import db, socketio, emit_progress
from routes import register_blueprints
import core.net.unet as net

# 初始化目录
config.init_directories()

# 创建 Flask 应用
app = Flask(__name__)
app.secret_key = config.SECRET_KEY
app.config['UPLOAD_FOLDER'] = config.UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = config.MAX_CONTENT_LENGTH
app.config['SQLALCHEMY_DATABASE_URI'] = config.SQLALCHEMY_DATABASE_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = config.SQLALCHEMY_TRACK_MODIFICATIONS
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = config.SQLALCHEMY_ENGINE_OPTIONS
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = timedelta(seconds=1)
app.model = None

# 初始化扩展
db.init_app(app)
socketio.init_app(app)


# ==================== Socket.IO 事件 ====================

@socketio.on('connect')
def handle_connect():
    print('[Socket] 客户端已连接')
    emit('connected', {'status': 'ok'})


@socketio.on('disconnect')
def handle_disconnect():
    print('[Socket] 客户端已断开')


# ==================== 注册蓝图 ====================
register_blueprints(app)


# ==================== 全局中间件 ====================

@app.after_request
def after_request(response):
    """添加 CORS 头"""
    from flask import request
    origin = request.headers.get('Origin')
    if origin:
        response.headers['Access-Control-Allow-Origin'] = origin
    else:
        response.headers['Access-Control-Allow-Origin'] = '*'
    
    response.headers['Access-Control-Allow-Credentials'] = 'true'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type, X-Requested-With, Authorization'
    return response


@app.errorhandler(413)
def file_too_large(e):
    """处理文件过大错误"""
    return jsonify({
        'status': 0,
        'error': '文件过大，最大支持50MB'
    }), 413


# ==================== 静态文件路由 ====================

@app.route('/')
def hello_world():
    return redirect(url_for('static', filename='./index.html'))


@app.route('/tmp/<path:file>', methods=['GET'])
def show_photo(file):
    """获取临时图像文件"""
    if file is None:
        return jsonify({'status': 0, 'error': '文件路径不能为空'}), 400
    
    image_path = Path(config.BASE_DIR) / 'tmp' / file
    
    if not image_path.exists():
        return jsonify({'status': 0, 'error': '文件不存在'}), 404
    
    with open(image_path, 'rb') as f:
        image_data = f.read()
    
    response = make_response(image_data)
    response.headers['Content-Type'] = 'image/png'
    return response


@app.route("/download", methods=['GET'])
def download_file():
    """下载测试数据文件"""
    file_path = Path(config.BASE_DIR) / 'data' / 'testfile.zip'
    if not file_path.exists():
        return jsonify({'status': 0, 'error': '测试数据文件不存在'}), 404
    return send_from_directory('data', 'testfile.zip', as_attachment=True)


# ==================== 旧接口兼容（无 /api 前缀） ====================

@app.route('/upload', methods=['GET', 'POST'])
def upload_file_compat():
    """兼容旧的上传接口（无认证）"""
    from routes.diagnosis import upload_file
    # 绕过认证直接调用核心逻辑
    import datetime
    import shutil
    from flask import request
    from utils import allowed_file, error_response, success_response
    from core import process
    
    print(f"\n{'='*60}")
    print(f"[Upload] 收到上传请求（兼容接口）")
    
    try:
        if 'file' not in request.files:
            return error_response('未选择文件')
        
        file = request.files['file']
        
        if file.filename == '':
            return error_response('未选择文件')
        
        print(f"[Upload] 文件名: {file.filename}")
        
        if file and allowed_file(file.filename, config.ALLOWED_EXTENSIONS):
            src_path = Path(config.UPLOAD_FOLDER) / file.filename
            file.save(str(src_path))
            
            tmp_ct_dir = Path(config.BASE_DIR) / 'tmp' / 'ct'
            shutil.copy(str(src_path), str(tmp_ct_dir))
            image_path = tmp_ct_dir / file.filename
            
            image_data = process.pre_process(str(image_path))
            pid = image_data[1]
            
            # 返回旧格式（直接返回 status 和 image_url）
            return jsonify({
                'status': 1,
                'image_url': f'{config.SERVER_URL}/tmp/image/{pid}.png',
                'message': '上传成功，请点击开始诊断'
            })
        else:
            return jsonify({'status': 0, 'error': '仅支持.dcm文件'})
            
    except Exception as e:
        print(f"[Upload] 处理失败: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'status': 0, 'error': str(e)})


# ==================== 数据库初始化 ====================

def init_db():
    """初始化数据库"""
    import hashlib
    from models import User, Patient, SystemSetting
    
    with app.app_context():
        try:
            db.create_all()
            
            # 创建默认管理员
            if not User.query.filter_by(username='admin').first():
                admin = User(
                    username='admin',
                    password=hashlib.sha256('123456'.encode()).hexdigest(),
                    name='管理员',
                    role='admin',
                    permissions='["rectum","lung","liver","brain","breast","stomach"]'
                )
                db.session.add(admin)
                print("[DB] 已创建默认管理员账号: admin")
            
            # 创建默认医生
            if not User.query.filter_by(username='doctor').first():
                doctor = User(
                    username='doctor',
                    password=hashlib.sha256('doctor123'.encode()).hexdigest(),
                    name='医生用户',
                    role='doctor',
                    permissions='["rectum"]'
                )
                db.session.add(doctor)
                print("[DB] 已创建默认医生账号: doctor")
            
            # 创建默认患者
            if not Patient.query.filter_by(patient_id='20190001').first():
                patient = Patient(
                    patient_id='20190001',
                    name='李明',
                    gender='男',
                    age=29,
                    phone='13220986785',
                    part='直肠'
                )
                db.session.add(patient)
                print("[DB] 已创建默认病人信息")

            # 初始化系统设置
            default_settings = [
                {'key': 'analysis_threshold', 'value': '1000', 'description': '面积阈值(像素)', 'category': 'analysis'},
                {'key': 'analysis_circularity_threshold', 'value': '0.7', 'description': '圆度阈值', 'category': 'analysis'},
                {'key': 'analysis_min_area', 'value': '100', 'description': '最小有效面积', 'category': 'analysis'},
                {'key': 'analysis_confidence_threshold', 'value': '0.5', 'description': '模型置信度阈值', 'category': 'analysis'},
                {'key': 'report_show_area', 'value': 'true', 'description': '报告中显示面积', 'category': 'report'},
                {'key': 'report_show_perimeter', 'value': 'true', 'description': '报告中显示周长', 'category': 'report'},
                {'key': 'report_show_circularity', 'value': 'true', 'description': '报告中显示圆度', 'category': 'report'},
                {'key': 'report_hospital_name', 'value': '直肠肿瘤辅助诊断中心', 'description': '医院名称', 'category': 'report'},
                {'key': 'report_footer_text', 'value': '本报告仅供临床参考，最终诊断以医生意见为准', 'description': '报告页脚', 'category': 'report'},
                {'key': 'system_max_upload_size', 'value': '50', 'description': '最大上传大小(MB)', 'category': 'system'},
                {'key': 'system_session_timeout', 'value': '24', 'description': 'Token有效期(小时)', 'category': 'system'},
            ]
            
            for setting in default_settings:
                if not SystemSetting.query.filter_by(key=setting['key']).first():
                    db.session.add(SystemSetting(
                        key=setting['key'],
                        value=setting['value'],
                        description=setting['description'],
                        category=setting['category'],
                        updated_by='system'
                    ))
            
            db.session.commit()
            print("[DB] 数据库初始化完成")
            
        except Exception as e:
            print(f"[DB] 数据库初始化失败: {e}")
            print("提示: 请确保MySQL服务已启动，且数据库 'ads_db' 已存在")


# ==================== 模型初始化 ====================

def init_model():
    """加载 UNet 模型"""
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = net.Unet(1, 1).to(device)
    
    model_path = os.path.join(config.BASE_DIR, "core", "net", "model.pth")
    if not os.path.exists(model_path):
        print(f"[Error] 模型文件未找到: {model_path}")
        raise FileNotFoundError(f"模型文件不存在: {model_path}")
    
    if torch.cuda.is_available():
        model.load_state_dict(torch.load(model_path))
        print(f"[Model] 模型已加载 (GPU): {model_path}")
    else:
        model.load_state_dict(torch.load(model_path, map_location='cpu'))
        print(f"[Model] 模型已加载 (CPU): {model_path}")
    
    model.eval()
    return model


# ==================== 日志配置 ====================

logging.basicConfig(level=logging.INFO)
werkzeug_logger = logging.getLogger('werkzeug')
werkzeug_logger.setLevel(logging.ERROR)


# ==================== 启动入口 ====================

if __name__ == '__main__':
    try:
        # 初始化数据库
        init_db()
        
        # 初始化模型
        print("[Init] 开始初始化模型...")
        try:
            app.model = init_model()
        except Exception as e:
            print(f"[Warning] 模型初始化失败: {e}")
            print("提示: 系统将以无模型模式运行")
            app.model = None
        
        # 启动服务器
        print("[Server] 启动Flask-SocketIO服务器...")
        print(f"[Server] 服务器地址: {config.SERVER_URL}")
        print("[Server] Socket.IO 已启用")
        socketio.run(
            app, 
            host=config.SERVER_HOST, 
            port=config.SERVER_PORT, 
            debug=False, 
            use_reloader=False
        )
        
    except Exception as e:
        print(f"[Error] Flask启动失败: {e}")
        import traceback
        traceback.print_exc()
