import datetime
import logging as rel_log
import os
import shutil
from datetime import timedelta
import hashlib
import uuid

import torch
from flask import *
from flask_socketio import SocketIO, emit

import core.main
import core.net.unet as net

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# 服务器配置（方便部署时修改）
SERVER_HOST = '127.0.0.1'
SERVER_PORT = 5003
SERVER_URL = f'http://{SERVER_HOST}:{SERVER_PORT}'

# 创建 tmp 子目录
for subdir in ['ct', 'image', 'mask', 'draw']:
    tmp_path = os.path.join(BASE_DIR, 'tmp', subdir)
    if not os.path.exists(tmp_path):
        os.makedirs(tmp_path)

ALLOWED_EXTENSIONS = set(['dcm'])
app = Flask(__name__)
app.secret_key = 'secret!'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 限制上传文件最大50MB
app.model = None

# ==================== Socket.IO 配置 ====================
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

@socketio.on('connect')
def handle_connect():
    print('[Socket] 客户端已连接')
    emit('connected', {'status': 'ok'})

@socketio.on('disconnect')
def handle_disconnect():
    print('[Socket] 客户端已断开')

# ==================== 数据库配置 ====================
from flask_sqlalchemy import SQLAlchemy

# 请修改为您本地MySQL数据库的实际连接信息
# 格式: mysql+pymysql://用户名:密码@主机:端口/数据库名
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:123456@localhost/ctai_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {'pool_recycle': 280}

db = SQLAlchemy(app)

# 用户模型
class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    name = db.Column(db.String(50))
    role = db.Column(db.String(20))

# Token模型
class Token(db.Model):
    __tablename__ = 'tokens'
    id = db.Column(db.Integer, primary_key=True)
    token = db.Column(db.String(100), unique=True, nullable=False)
    username = db.Column(db.String(50), db.ForeignKey('users.username'), nullable=False)
    login_time = db.Column(db.DateTime, default=datetime.datetime.now)
    expire_time = db.Column(db.DateTime, nullable=False)  # Token过期时间
    
    user = db.relationship('User', backref=db.backref('tokens', lazy=True))

# 登录失败记录模型
class LoginAttempt(db.Model):
    __tablename__ = 'login_attempts'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=False)
    attempt_time = db.Column(db.DateTime, default=datetime.datetime.now)
    success = db.Column(db.Boolean, default=False)
    ip_address = db.Column(db.String(50))

# 病人模型
class Patient(db.Model):
    __tablename__ = 'patients'
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.String(50), unique=True, nullable=False)
    name = db.Column(db.String(50), nullable=False)
    gender = db.Column(db.String(10))
    age = db.Column(db.Integer)
    phone = db.Column(db.String(20))
    part = db.Column(db.String(50))

# 诊断记录模型（扩展功能）
class DiagnosisRecord(db.Model):
    """保存每次诊断的历史记录，便于追溯和统计"""
    __tablename__ = 'diagnosis_records'
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.String(50), db.ForeignKey('patients.patient_id'), nullable=True)
    doctor_username = db.Column(db.String(50), db.ForeignKey('users.username'), nullable=True)
    
    # 文件信息
    filename = db.Column(db.String(255), nullable=False)
    image_url = db.Column(db.String(500))
    draw_url = db.Column(db.String(500))
    
    # 诊断结果
    area = db.Column(db.Float)  # 面积
    perimeter = db.Column(db.Float)  # 周长
    features = db.Column(db.Text)  # JSON格式存储所有特征
    
    # 医生诊断记录
    doctor_diagnosis = db.Column(db.Text)  # 医生的诊断描述
    doctor_suggestion = db.Column(db.Text)  # 医生的治疗建议
    diagnosis_conclusion = db.Column(db.String(100))  # 诊断结论（如：良性/恶性/待观察）
    
    # 时间信息
    created_at = db.Column(db.DateTime, default=datetime.datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now)
    
    # 关系
    patient = db.relationship('Patient', backref=db.backref('diagnoses', lazy=True))
    doctor = db.relationship('User', backref=db.backref('diagnoses', lazy=True))

# 系统设置模型
class SystemSetting(db.Model):
    """系统配置存储"""
    __tablename__ = 'system_settings'
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(100), unique=True, nullable=False)  # 设置项的键
    value = db.Column(db.Text)  # 设置项的值（JSON格式存储复杂值）
    description = db.Column(db.String(255))  # 设置项说明
    category = db.Column(db.String(50))  # 分类：analysis/report/system
    updated_at = db.Column(db.DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now)
    updated_by = db.Column(db.String(50))  # 最后修改人

def init_db():
    """初始化数据库：创建表并添加默认用户"""
    with app.app_context():
        try:
            # 创建表
            db.create_all()
            
            # 检查并添加默认管理员
            if not User.query.filter_by(username='admin').first():
                admin = User(
                    username='admin',
                    password=hashlib.sha256('123456'.encode()).hexdigest(),
                    name='管理员',
                    role='admin'
                )
                db.session.add(admin)
                print("[DB] 已创建默认管理员账号: admin")
            
            # 检查并添加默认医生用户
            if not User.query.filter_by(username='doctor').first():
                doctor = User(
                    username='doctor',
                    password=hashlib.sha256('doctor123'.encode()).hexdigest(),
                    name='医生用户',
                    role='doctor'
                )
                db.session.add(doctor)
                print("[DB] 已创建默认医生账号: doctor")
            
            # 检查并添加默认病人
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
                print("[DB] 已创建默认病人信息: 李明")

            # 初始化默认系统设置
            default_settings = [
                # 数据分析参数
                {'key': 'analysis_threshold', 'value': '1000', 'description': '面积阈值(像素)，超过此值判定为需关注', 'category': 'analysis'},
                {'key': 'analysis_circularity_threshold', 'value': '0.7', 'description': '圆度阈值，低于此值可能为异常形态', 'category': 'analysis'},
                {'key': 'analysis_min_area', 'value': '100', 'description': '最小有效面积(像素)，小于此值忽略', 'category': 'analysis'},
                {'key': 'analysis_confidence_threshold', 'value': '0.5', 'description': '模型置信度阈值', 'category': 'analysis'},
                
                # 报告内容设置
                {'key': 'report_show_area', 'value': 'true', 'description': '报告中显示面积', 'category': 'report'},
                {'key': 'report_show_perimeter', 'value': 'true', 'description': '报告中显示周长', 'category': 'report'},
                {'key': 'report_show_circularity', 'value': 'true', 'description': '报告中显示圆度', 'category': 'report'},
                {'key': 'report_show_eccentricity', 'value': 'true', 'description': '报告中显示离心率', 'category': 'report'},
                {'key': 'report_show_intensity', 'value': 'true', 'description': '报告中显示灰度信息', 'category': 'report'},
                {'key': 'report_show_histogram', 'value': 'true', 'description': '报告中显示灰度直方图', 'category': 'report'},
                {'key': 'report_hospital_name', 'value': '直肠肿瘤辅助诊断中心', 'description': '报告中显示的医院名称', 'category': 'report'},
                {'key': 'report_footer_text', 'value': '本报告仅供临床参考，最终诊断以医生意见为准', 'description': '报告页脚提示文字', 'category': 'report'},
                
                # 系统设置
                {'key': 'system_max_upload_size', 'value': '50', 'description': '最大上传文件大小(MB)', 'category': 'system'},
                {'key': 'system_session_timeout', 'value': '24', 'description': 'Token有效期(小时)', 'category': 'system'},
                {'key': 'system_auto_backup', 'value': 'false', 'description': '是否启用自动备份', 'category': 'system'},
            ]
            
            for setting in default_settings:
                if not SystemSetting.query.filter_by(key=setting['key']).first():
                    new_setting = SystemSetting(
                        key=setting['key'],
                        value=setting['value'],
                        description=setting['description'],
                        category=setting['category'],
                        updated_by='system'
                    )
                    db.session.add(new_setting)
            print("[DB] 已初始化系统设置")

            db.session.commit()
            print("[DB] 数据库初始化完成")
        except Exception as e:
            print(f"[DB] 数据库初始化失败: {e}")
            print("提示: 请确保MySQL服务已启动，且数据库 'ctai_db' 已存在")

werkzeug_logger = rel_log.getLogger('werkzeug')
werkzeug_logger.setLevel(rel_log.ERROR)

# 解决缓存刷新问题
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = timedelta(seconds=1)


# 添加header解决跨域
@app.after_request
def after_request(response):
    # 获取请求的 Origin
    origin = request.headers.get('Origin')
    if origin:
        response.headers['Access-Control-Allow-Origin'] = origin
    else:
        response.headers['Access-Control-Allow-Origin'] = '*'
        
    response.headers['Access-Control-Allow-Credentials'] = 'true'
    response.headers['Access-Control-Allow-Methods'] = 'POST, GET, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type, X-Requested-With, Authorization'
    return response


# 处理文件过大的错误
@app.errorhandler(413)
def file_too_large(e):
    return jsonify({
        'status': 0,
        'error': '文件过大，最大支持50MB'
    }), 413


def allowed_file(filename):
    """检查文件扩展名是否允许"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# 验证token的装饰器
def token_required(f):
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if token and token.startswith('Bearer '):
            token = token[7:]
        
        if not token:
            return jsonify({'status': 0, 'error': '未登录'}), 401
            
        # 查库验证token
        token_record = Token.query.filter_by(token=token).first()
        if not token_record:
            return jsonify({'status': 0, 'error': '登录已过期'}), 401
            
        return f(*args, **kwargs)
    return decorated


@app.route('/')
def hello_world():
    return redirect(url_for('static', filename='./index.html'))


# ==================== 辅助函数 ====================

def success_response(data=None, message='操作成功'):
    """统一成功响应格式"""
    return jsonify({
        'status': 1,
        'message': message,
        'data': data
    })

def error_response(error='操作失败', code=400):
    """统一错误响应格式"""
    return jsonify({
        'status': 0,
        'error': error
    }), code


# ==================== 系统接口 ====================

@app.route('/api/health', methods=['GET'])
def health_check():
    """
    健康检查接口
    用于检测服务是否正常运行
    返回: 服务状态、模型状态、数据库状态
    """
    model_status = '已加载' if app.model is not None else '未加载(模拟模式)'
    
    # 检查数据库连接
    try:
        db.session.execute('SELECT 1')
        db_status = '正常'
    except:
        db_status = '异常'
    
    return jsonify({
        'status': 1,
        'message': '服务运行正常',
        'data': {
            'server': SERVER_URL,
            'model': model_status,
            'database': db_status,
            'version': '1.0.0'
        }
    })


# ==================== 用户认证接口 ====================
from functools import wraps

def token_required(f):
    """验证Token的装饰器"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # OPTIONS 请求直接通过（预检请求）
        if request.method == 'OPTIONS':
            return jsonify({'status': 1})
        
        token = request.headers.get('Authorization')
        if token and token.startswith('Bearer '):
            token = token[7:]
        
        if not token:
            return jsonify({'status': 0, 'error': '缺少认证Token'}), 401
        
        # 验证Token是否存在且未过期
        token_record = Token.query.filter_by(token=token).first()
        if not token_record:
            return jsonify({'status': 0, 'error': 'Token无效'}), 401
        
        # 检查Token是否过期
        if datetime.datetime.now() > token_record.expire_time:
            db.session.delete(token_record)
            db.session.commit()
            return jsonify({'status': 0, 'error': 'Token已过期,请重新登录'}), 401
        
        # 将用户信息传递给路由函数
        request.current_user = token_record.user
        return f(*args, **kwargs)
    
    return decorated_function

@app.route('/api/login', methods=['POST', 'OPTIONS'])
def login():
    """用户登录接口"""
    if request.method == 'OPTIONS':
        return jsonify({'status': 1})
    
    try:
        data = request.get_json()
        username = data.get('username', '')
        password = data.get('password', '')
        ip_address = request.remote_addr
        
        print(f"[Login] 用户 {username} 从 {ip_address} 尝试登录")
        
        if not username or not password:
            return jsonify({'status': 0, 'error': '用户名和密码不能为空'})
        
        # 检查登录失败次数(15分钟内)
        fifteen_minutes_ago = datetime.datetime.now() - datetime.timedelta(minutes=15)
        failed_attempts = LoginAttempt.query.filter(
            LoginAttempt.username == username,
            LoginAttempt.success == False,
            LoginAttempt.attempt_time > fifteen_minutes_ago
        ).count()
        
        if failed_attempts >= 5:
            return jsonify({'status': 0, 'error': '登录失败次数过多,请15分钟后再试'})
        
        # 验证用户
        user = User.query.filter_by(username=username).first()
        if not user:
            # 记录失败
            db.session.add(LoginAttempt(username=username, success=False, ip_address=ip_address))
            db.session.commit()
            return jsonify({'status': 0, 'error': '用户名或密码错误'})
        
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        if user.password != password_hash:
            # 记录失败
            db.session.add(LoginAttempt(username=username, success=False, ip_address=ip_address))
            db.session.commit()
            return jsonify({'status': 0, 'error': '用户名或密码错误'})
        
        # 生成token并存入数据库(24小时有效期)
        token = str(uuid.uuid4())
        expire_time = datetime.datetime.now() + datetime.timedelta(hours=24)
        new_token = Token(
            token=token,
            username=user.username,
            login_time=datetime.datetime.now(),
            expire_time=expire_time
        )
        db.session.add(new_token)
        
        # 记录成功登录
        db.session.add(LoginAttempt(username=username, success=True, ip_address=ip_address))
        db.session.commit()
        
        print(f"[Login] 用户 {username} 登录成功")
        
        return jsonify({
            'status': 1,
            'message': '登录成功',
            'data': {
                'token': token,
                'username': user.username,
                'name': user.name,
                'role': user.role,
                'expire_time': expire_time.strftime('%Y-%m-%d %H:%M:%S')
            }
        })
        
    except Exception as e:
        print(f"[Login] 登录失败: {e}")
        return jsonify({'status': 0, 'error': str(e)})


@app.route('/api/refresh-token', methods=['POST', 'OPTIONS'])
@token_required
def refresh_token():
    """刷新Token接口"""
    if request.method == 'OPTIONS':
        return jsonify({'status': 1})
    
    try:
        old_token = request.headers.get('Authorization')
        if old_token and old_token.startswith('Bearer '):
            old_token = old_token[7:]
        
        # 删除旧token
        old_token_record = Token.query.filter_by(token=old_token).first()
        if old_token_record:
            username = old_token_record.username
            db.session.delete(old_token_record)
            
            # 生成新token(24小时有效期)
            new_token = str(uuid.uuid4())
            expire_time = datetime.datetime.now() + datetime.timedelta(hours=24)
            token_record = Token(
                token=new_token,
                username=username,
                login_time=datetime.datetime.now(),
                expire_time=expire_time
            )
            db.session.add(token_record)
            db.session.commit()
            
            print(f"[Token] 用户 {username} 刷新了Token")
            
            return jsonify({
                'status': 1,
                'message': 'Token刷新成功',
                'data': {
                    'token': new_token,
                    'expire_time': expire_time.strftime('%Y-%m-%d %H:%M:%S')
                }
            })
        
        return jsonify({'status': 0, 'error': 'Token不存在'})
        
    except Exception as e:
        print(f"[Token] 刷新失败: {e}")
        return jsonify({'status': 0, 'error': str(e)})


@app.route('/api/check-auth', methods=['GET', 'OPTIONS'])
@token_required
def check_auth():
    """检查认证状态"""
    if request.method == 'OPTIONS':
        return jsonify({'status': 1})
    
    try:
        user = request.current_user
        return jsonify({
            'status': 1,
            'data': {
                'username': user.username,
                'name': user.name,
                'role': user.role
            }
        })
    except Exception as e:
        print(f"[Auth] 验证失败: {e}")
        return jsonify({'status': 0, 'error': str(e)})


@app.route('/api/logout', methods=['POST', 'OPTIONS'])
@token_required
def logout():
    """用户登出接口"""
    if request.method == 'OPTIONS':
        return jsonify({'status': 1})
    
    try:
        token = request.headers.get('Authorization')
        if token and token.startswith('Bearer '):
            token = token[7:]
        
        if token:
            token_record = Token.query.filter_by(token=token).first()
            if token_record:
                username = token_record.username
                db.session.delete(token_record)
                db.session.commit()
                print(f"[Logout] 用户 {username} 已登出")
        
        return jsonify({'status': 1, 'message': '登出成功'})
        
    except Exception as e:
        return jsonify({'status': 0, 'error': str(e)})


@app.route('/api/patient', methods=['GET', 'OPTIONS'])
def get_patient():
    """获取病人信息"""
    if request.method == 'OPTIONS':
        return jsonify({'status': 1})

    patient_id = request.args.get('id')
    
    if patient_id:
        patient = Patient.query.filter_by(patient_id=patient_id).first()
    else:
        # 如果没有提供ID，默认返回第一个（可选）
        patient = Patient.query.first()

    if patient:
        return jsonify({
            'status': 1,
            'data': {
                'ID': patient.patient_id,
                '姓名': patient.name,
                '性别': patient.gender,
                '年龄': str(patient.age),
                '电话': patient.phone,
                '部位': patient.part
            }
        })
    return jsonify({'status': 0, 'error': '未找到该病人信息'})


# ==================== 业务接口 ====================


@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    """上传CT图像接口 - 仅上传和预处理，不进行预测"""
    print(f"\n{'='*60}")
    print(f"[Upload] 收到上传请求")
    
    try:
        # 检查是否有文件
        if 'file' not in request.files:
            return jsonify({'status': 0, 'error': '未选择文件'})
        
        file = request.files['file']
        
        # 检查文件名是否为空
        if file.filename == '':
            return jsonify({'status': 0, 'error': '未选择文件'})
        
        print(f"[Upload] 文件名: {file.filename}")
        print(f"[Upload] 时间: {datetime.datetime.now()}")
        
        if file and allowed_file(file.filename):
            # 保存文件
            src_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            print(f"[Upload] 保存到: {src_path}")
            file.save(src_path)
            
            # 复制到临时目录
            tmp_ct_dir = os.path.join(BASE_DIR, 'tmp', 'ct')
            shutil.copy(src_path, tmp_ct_dir)
            image_path = os.path.join(tmp_ct_dir, file.filename)
            
            # 仅进行预处理，生成预览图
            print(f"[Upload] 预处理图像...")
            from core import process
            image_data = process.pre_process(image_path)
            pid = image_data[1]  # 文件名（不含扩展名）
            
            result = {
                'status': 1,
                'image_url': f'{SERVER_URL}/tmp/image/{pid}.png',
                'message': '上传成功，请点击开始诊断'
            }
            print(f"[Upload] 上传成功!")
            print(f"{'='*60}\n")
            return jsonify(result)
        else:
            print(f"[Upload] 文件格式不支持")
            return jsonify({'status': 0, 'error': '仅支持.dcm文件'})
            
    except Exception as e:
        print(f"[Upload] 处理失败: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'status': 0, 'error': str(e)})


def emit_progress(percentage, message):
    """发送进度更新到所有客户端"""
    socketio.emit('progress', {
        'percentage': percentage,
        'message': message
    })


@app.route('/api/predict', methods=['POST', 'OPTIONS'])
def predict_image():
    """AI预测接口 - 对已上传的图像进行预测分析"""
    if request.method == 'OPTIONS':
        return jsonify({'status': 1})
    
    print(f"\n{'='*60}")
    print(f"[Predict] 收到预测请求")
    
    try:
        data = request.get_json()
        image_url = data.get('imageUrl', '')
        
        # 从URL中提取文件名
        # image_url 格式: http://127.0.0.1:5003/tmp/image/xxx.png
        if '/tmp/image/' in image_url:
            filename = image_url.split('/tmp/image/')[-1].replace('.png', '')
        else:
            return jsonify({'status': 0, 'error': '无效的图像URL'})
        
        print(f"[Predict] 处理文件: {filename}")
        emit_progress(10, '正在准备分析...')
        
        # 检查原始dcm文件是否存在
        dcm_path = os.path.join(BASE_DIR, 'tmp', 'ct', f'{filename}.dcm')
        if not os.path.exists(dcm_path):
            socketio.emit('error', '原始图像文件不存在')
            return jsonify({'status': 0, 'error': '原始图像文件不存在'})
        
        # 执行预测（带进度回调）
        print(f"[Predict] 开始AI分析...")
        pid, image_info = core.main.c_main(dcm_path, app.model, emit_progress)
        
        emit_progress(100, '分析完成')
        
        result = {
            'status': 1,
            'image_url': f'{SERVER_URL}/tmp/image/{pid}',
            'draw_url': f'{SERVER_URL}/tmp/draw/{pid}',
            'image_info': image_info
        }
        
        # 保存诊断记录到数据库
        record_id = None
        try:
            import json
            # 从请求中获取可选的患者ID和医生信息
            patient_id = data.get('patientId')
            token = request.headers.get('Authorization')
            doctor_username = None
            if token and token.startswith('Bearer '):
                token_record = Token.query.filter_by(token=token[7:]).first()
                if token_record:
                    doctor_username = token_record.username
            
            record = DiagnosisRecord(
                patient_id=patient_id,
                doctor_username=doctor_username,
                filename=f'{filename}.dcm',
                image_url=result['image_url'],
                draw_url=result['draw_url'],
                area=image_info.get('面积', 0),
                perimeter=image_info.get('周长', 0),
                features=json.dumps(image_info, ensure_ascii=False)
            )
            db.session.add(record)
            db.session.commit()
            record_id = record.id
            print(f"[Predict] 诊断记录已保存，ID: {record.id}")
        except Exception as save_err:
            print(f"[Predict] 保存诊断记录失败: {save_err}")
        
        # 添加诊断记录ID到返回结果
        result['record_id'] = record_id
        
        # 通过 Socket 发送结果
        socketio.emit('result', {
            'url2': result['draw_url'],
            'feature_list': image_info,
            'area': image_info.get('面积', 0),
            'perimeter': image_info.get('周长', 0),
            'record_id': record_id
        })
        
        print(f"[Predict] 预测完成!")
        print(f"{'='*60}\n")
        return jsonify(result)
        
    except Exception as e:
        print(f"[Predict] 预测失败: {e}")
        socketio.emit('error', str(e))
        import traceback
        traceback.print_exc()
        return jsonify({'status': 0, 'error': str(e)})


# ==================== 扩展接口（诊断历史/统计） ====================

@app.route('/api/diagnosis/history', methods=['GET', 'OPTIONS'])
def get_diagnosis_history():
    """
    获取诊断历史记录
    参数:
        - patient_id: 可选，按患者ID筛选
        - page: 页码，默认1
        - page_size: 每页数量，默认10
    """
    if request.method == 'OPTIONS':
        return jsonify({'status': 1})
    
    try:
        patient_id = request.args.get('patient_id')
        page = int(request.args.get('page', 1))
        page_size = int(request.args.get('page_size', 10))
        
        query = DiagnosisRecord.query.order_by(DiagnosisRecord.created_at.desc())
        
        if patient_id:
            query = query.filter_by(patient_id=patient_id)
        
        # 分页
        total = query.count()
        records = query.offset((page - 1) * page_size).limit(page_size).all()
        
        history_list = []
        for record in records:
            import json
            history_list.append({
                'id': record.id,
                'patient_id': record.patient_id,
                'doctor': record.doctor_username,
                'filename': record.filename,
                'image_url': record.image_url,
                'draw_url': record.draw_url,
                'area': record.area,
                'perimeter': record.perimeter,
                'features': json.loads(record.features) if record.features else {},
                'created_at': record.created_at.strftime('%Y-%m-%d %H:%M:%S') if record.created_at else None
            })
        
        return jsonify({
            'status': 1,
            'data': {
                'total': total,
                'page': page,
                'page_size': page_size,
                'list': history_list
            }
        })
        
    except Exception as e:
        return jsonify({'status': 0, 'error': str(e)})


@app.route('/api/diagnosis/<int:record_id>', methods=['GET', 'OPTIONS'])
def get_diagnosis_detail(record_id):
    """获取单条诊断记录详情"""
    if request.method == 'OPTIONS':
        return jsonify({'status': 1})
    
    try:
        record = DiagnosisRecord.query.get(record_id)
        if not record:
            return jsonify({'status': 0, 'error': '记录不存在'}), 404
        
        import json
        return jsonify({
            'status': 1,
            'data': {
                'id': record.id,
                'patient_id': record.patient_id,
                'patient_name': record.patient.name if record.patient else None,
                'patient_gender': record.patient.gender if record.patient else None,
                'patient_age': record.patient.age if record.patient else None,
                'patient_phone': record.patient.phone if record.patient else None,
                'doctor': record.doctor_username,
                'doctor_name': record.doctor.name if record.doctor else None,
                'filename': record.filename,
                'image_url': record.image_url,
                'draw_url': record.draw_url,
                'area': record.area,
                'perimeter': record.perimeter,
                'features': json.loads(record.features) if record.features else {},
                'doctor_diagnosis': record.doctor_diagnosis,
                'doctor_suggestion': record.doctor_suggestion,
                'diagnosis_conclusion': record.diagnosis_conclusion,
                'created_at': record.created_at.strftime('%Y-%m-%d %H:%M:%S') if record.created_at else None,
                'updated_at': record.updated_at.strftime('%Y-%m-%d %H:%M:%S') if record.updated_at else None
            }
        })
        
    except Exception as e:
        return jsonify({'status': 0, 'error': str(e)})


@app.route('/api/diagnosis/<int:record_id>/record', methods=['POST', 'OPTIONS'])
@token_required
def save_doctor_record(record_id):
    """
    保存医生的诊断记录
    参数:
        - doctor_diagnosis: 医生的诊断描述
        - doctor_suggestion: 医生的治疗建议
        - diagnosis_conclusion: 诊断结论（良性/恶性/待观察等）
    """
    if request.method == 'OPTIONS':
        return jsonify({'status': 1})
    
    try:
        record = DiagnosisRecord.query.get(record_id)
        if not record:
            return jsonify({'status': 0, 'error': '诊断记录不存在'}), 404
        
        data = request.get_json()
        
        # 更新医生诊断记录
        if 'doctor_diagnosis' in data:
            record.doctor_diagnosis = data['doctor_diagnosis']
        if 'doctor_suggestion' in data:
            record.doctor_suggestion = data['doctor_suggestion']
        if 'diagnosis_conclusion' in data:
            record.diagnosis_conclusion = data['diagnosis_conclusion']
        
        # 更新医生信息（如果之前没有）
        if not record.doctor_username and hasattr(request, 'current_user'):
            record.doctor_username = request.current_user.username
        
        db.session.commit()
        
        print(f"[Diagnosis] 诊断记录 {record_id} 已更新医生记录")
        
        return jsonify({
            'status': 1,
            'message': '诊断记录保存成功',
            'data': {
                'id': record.id,
                'doctor_diagnosis': record.doctor_diagnosis,
                'doctor_suggestion': record.doctor_suggestion,
                'diagnosis_conclusion': record.diagnosis_conclusion,
                'updated_at': record.updated_at.strftime('%Y-%m-%d %H:%M:%S') if record.updated_at else None
            }
        })
        
    except Exception as e:
        print(f"[Diagnosis] 保存医生记录失败: {e}")
        return jsonify({'status': 0, 'error': str(e)})


@app.route('/api/statistics', methods=['GET', 'OPTIONS'])
def get_statistics():
    """
    获取系统统计数据
    用于首页展示或数据分析
    """
    if request.method == 'OPTIONS':
        return jsonify({'status': 1})
    
    try:
        # 统计数据
        total_diagnoses = DiagnosisRecord.query.count()
        total_patients = Patient.query.count()
        total_users = User.query.count()
        
        # 今日诊断数
        today = datetime.datetime.now().date()
        today_start = datetime.datetime.combine(today, datetime.time.min)
        today_diagnoses = DiagnosisRecord.query.filter(
            DiagnosisRecord.created_at >= today_start
        ).count()
        
        # 最近7天每日诊断数（用于图表）
        daily_stats = []
        for i in range(6, -1, -1):
            day = today - timedelta(days=i)
            day_start = datetime.datetime.combine(day, datetime.time.min)
            day_end = datetime.datetime.combine(day, datetime.time.max)
            count = DiagnosisRecord.query.filter(
                DiagnosisRecord.created_at >= day_start,
                DiagnosisRecord.created_at <= day_end
            ).count()
            daily_stats.append({
                'date': day.strftime('%m-%d'),
                'count': count
            })
        
        # 计算平均准确率（基于诊断记录中的特征数据）
        # 这里使用模拟的准确率计算，实际可根据业务逻辑调整
        avg_accuracy = 93.5  # 默认值
        if total_diagnoses > 0:
            # 基于诊断数量动态调整准确率展示（模拟）
            avg_accuracy = min(95.0, 90.0 + (total_diagnoses * 0.01))
        
        # 计算平均诊断用时（分钟）- 模拟数据
        avg_time = 3.2  # 默认平均用时
        
        # 获取最近诊断记录
        recent_records = DiagnosisRecord.query.order_by(
            DiagnosisRecord.created_at.desc()
        ).limit(5).all()
        
        recent_diagnoses = []
        for record in recent_records:
            patient_name = '未知患者'
            part = '直肠'
            if record.patient:
                patient_name = record.patient.name
                part = record.patient.part or '直肠'
            
            # 计算时间差
            if record.created_at:
                time_diff = datetime.datetime.now() - record.created_at
                if time_diff.days > 0:
                    time_str = f"{time_diff.days}天前"
                elif time_diff.seconds < 3600:
                    time_str = f"{time_diff.seconds // 60}分钟前"
                else:
                    time_str = f"{time_diff.seconds // 3600}小时前"
            else:
                time_str = '未知'
            
            recent_diagnoses.append({
                'id': record.id,
                'patientName': patient_name,
                'part': part,
                'time': time_str,
                'status': '已完成'
            })
        
        return jsonify({
            'status': 1,
            'data': {
                'total_diagnoses': total_diagnoses,
                'total_patients': total_patients,
                'total_users': total_users,
                'today_diagnoses': today_diagnoses,
                'daily_stats': daily_stats,
                'avg_accuracy': round(avg_accuracy, 1),
                'avg_time': avg_time,
                'recent_diagnoses': recent_diagnoses
            }
        })
        
    except Exception as e:
        return jsonify({'status': 0, 'error': str(e)})


# ==================== 系统设置 API ====================

def admin_required(f):
    """管理员权限装饰器"""
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if token and token.startswith('Bearer '):
            token = token[7:]
        
        if not token:
            return jsonify({'status': 0, 'error': '未登录'}), 401
            
        # 查库验证token并检查角色
        token_record = Token.query.filter_by(token=token).first()
        if not token_record:
            return jsonify({'status': 0, 'error': '登录已过期'}), 401
        
        # 检查是否是管理员
        user = User.query.filter_by(username=token_record.username).first()
        if not user or user.role != 'admin':
            return jsonify({'status': 0, 'error': '需要管理员权限'}), 403
            
        return f(*args, **kwargs)
    return decorated


@app.route('/api/settings', methods=['GET', 'OPTIONS'])
@admin_required
def get_settings():
    """获取所有系统设置"""
    if request.method == 'OPTIONS':
        return jsonify({'status': 1})
    
    try:
        settings = SystemSetting.query.all()
        
        # 按分类组织设置
        result = {
            'analysis': [],
            'report': [],
            'system': []
        }
        
        for setting in settings:
            item = {
                'key': setting.key,
                'value': setting.value,
                'description': setting.description,
                'category': setting.category,
                'updated_at': setting.updated_at.strftime('%Y-%m-%d %H:%M:%S') if setting.updated_at else None,
                'updated_by': setting.updated_by
            }
            if setting.category in result:
                result[setting.category].append(item)
        
        return jsonify({
            'status': 1,
            'data': result
        })
        
    except Exception as e:
        return jsonify({'status': 0, 'error': str(e)})


@app.route('/api/settings', methods=['POST'])
@admin_required
def update_settings():
    """更新系统设置"""
    try:
        data = request.get_json()
        if not data or 'settings' not in data:
            return jsonify({'status': 0, 'error': '缺少设置数据'})
        
        # 获取当前用户
        token = request.headers.get('Authorization')
        if token and token.startswith('Bearer '):
            token = token[7:]
        token_record = Token.query.filter_by(token=token).first()
        username = token_record.username if token_record else 'unknown'
        
        settings = data['settings']
        updated_count = 0
        
        for key, value in settings.items():
            setting = SystemSetting.query.filter_by(key=key).first()
            if setting:
                setting.value = str(value)
                setting.updated_by = username
                updated_count += 1
            else:
                # 如果设置不存在，创建新的
                new_setting = SystemSetting(
                    key=key,
                    value=str(value),
                    category=data.get('category', 'system'),
                    description=data.get('descriptions', {}).get(key, ''),
                    updated_by=username
                )
                db.session.add(new_setting)
                updated_count += 1
        
        db.session.commit()
        
        return jsonify({
            'status': 1,
            'message': f'成功更新 {updated_count} 项设置'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 0, 'error': str(e)})


@app.route('/api/settings/<key>', methods=['GET'])
def get_setting(key):
    """获取单个设置项（公开接口，用于前端获取配置）"""
    try:
        setting = SystemSetting.query.filter_by(key=key).first()
        if not setting:
            return jsonify({'status': 0, 'error': '设置项不存在'})
        
        return jsonify({
            'status': 1,
            'data': {
                'key': setting.key,
                'value': setting.value,
                'description': setting.description
            }
        })
        
    except Exception as e:
        return jsonify({'status': 0, 'error': str(e)})


@app.route('/api/settings/reset', methods=['POST'])
@admin_required
def reset_settings():
    """重置设置为默认值"""
    try:
        data = request.get_json()
        category = data.get('category') if data else None
        
        # 默认设置值
        defaults = {
            'analysis_threshold': '1000',
            'analysis_circularity_threshold': '0.7',
            'analysis_min_area': '100',
            'analysis_confidence_threshold': '0.5',
            'report_show_area': 'true',
            'report_show_perimeter': 'true',
            'report_show_circularity': 'true',
            'report_show_eccentricity': 'true',
            'report_show_intensity': 'true',
            'report_show_histogram': 'true',
            'report_hospital_name': '直肠肿瘤辅助诊断中心',
            'report_footer_text': '本报告仅供临床参考，最终诊断以医生意见为准',
            'system_max_upload_size': '50',
            'system_session_timeout': '24',
            'system_auto_backup': 'false',
        }
        
        # 获取当前用户
        token = request.headers.get('Authorization')
        if token and token.startswith('Bearer '):
            token = token[7:]
        token_record = Token.query.filter_by(token=token).first()
        username = token_record.username if token_record else 'unknown'
        
        query = SystemSetting.query
        if category:
            query = query.filter_by(category=category)
        
        settings = query.all()
        reset_count = 0
        
        for setting in settings:
            if setting.key in defaults:
                setting.value = defaults[setting.key]
                setting.updated_by = username
                reset_count += 1
        
        db.session.commit()
        
        return jsonify({
            'status': 1,
            'message': f'成功重置 {reset_count} 项设置'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 0, 'error': str(e)})


@app.route("/download", methods=['GET'])
def download_file():
    """下载测试数据文件"""
    file_path = os.path.join(BASE_DIR, 'data', 'testfile.zip')
    if not os.path.exists(file_path):
        return jsonify({'status': 0, 'error': '测试数据文件不存在'}), 404
    return send_from_directory('data', 'testfile.zip', as_attachment=True)


@app.route('/tmp/<path:file>', methods=['GET'])
def show_photo(file):
    """获取临时图像文件（原图/mask/轮廓图）"""
    if file is None:
        return jsonify({'status': 0, 'error': '文件路径不能为空'}), 400
    
    image_path = os.path.join(BASE_DIR, 'tmp', file)
    
    if not os.path.exists(image_path):
        return jsonify({'status': 0, 'error': '文件不存在'}), 404
    
    # 使用 with 语句确保文件正确关闭
    with open(image_path, 'rb') as f:
        image_data = f.read()
    
    response = make_response(image_data)
    response.headers['Content-Type'] = 'image/png'
    return response


# 加载真实的UNet模型
def init_model():
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = net.Unet(1, 1).to(device)
    
    model_path = os.path.join(BASE_DIR, "core", "net", "model.pth")
    if not os.path.exists(model_path):
        print(f"[Error] 模型文件未找到: {model_path}")
        print("请确保已将训练好的模型复制到此路径")
        raise FileNotFoundError(f"模型文件不存在: {model_path}")
    
    if torch.cuda.is_available():
        model.load_state_dict(torch.load(model_path))
        print(f"[Model] 模型已加载 (GPU): {model_path}")
    else:
        model.load_state_dict(torch.load(model_path, map_location='cpu'))
        print(f"[Model] 模型已加载 (CPU): {model_path}")
    
    model.eval()
    return model


if __name__ == '__main__':
    try:
        import logging
        logging.basicConfig(level=logging.INFO)
        
        # 初始化数据库
        init_db()
        
        print("[Init] 开始初始化模型...")
        try:
            app.model = init_model()
        except Exception as e:
            print(f"[Warning] 模型初始化失败: {e}")
            print("提示: 系统将以无模型模式运行，部分功能可能不可用")
            app.model = None
            
        print("[Server] 启动Flask-SocketIO服务器...")
        print(f"[Server] 服务器地址: {SERVER_URL}")
        print("[Server] Socket.IO 已启用")
        socketio.run(app, host=SERVER_HOST, port=SERVER_PORT, debug=False, use_reloader=False)
    except Exception as e:
        print(f"[Error] Flask启动失败: {e}")
        import traceback
        traceback.print_exc()


