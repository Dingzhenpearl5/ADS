import datetime
import logging as rel_log
import os
import shutil
from datetime import timedelta
import hashlib
import uuid

import torch
from flask import *

import core.main
import core.net.unet as net

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
ALLOWED_EXTENSIONS = set(['dcm'])
app = Flask(__name__)
app.secret_key = 'secret!'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

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
    
    user = db.relationship('User', backref=db.backref('tokens', lazy=True))

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


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


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


# ==================== 用户认证接口 ====================

@app.route('/api/login', methods=['POST', 'OPTIONS'])
def login():
    """用户登录接口"""
    if request.method == 'OPTIONS':
        return jsonify({'status': 1})
    
    try:
        data = request.get_json()
        username = data.get('username', '')
        password = data.get('password', '')
        
        print(f"[Login] 用户 {username} 尝试登录")
        
        if not username or not password:
            return jsonify({'status': 0, 'error': '用户名和密码不能为空'})
        
        # 验证用户
        user = User.query.filter_by(username=username).first()
        if not user:
            return jsonify({'status': 0, 'error': '用户名不存在'})
        
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        if user.password != password_hash:
            return jsonify({'status': 0, 'error': '密码错误'})
        
        # 生成token并存入数据库
        token = str(uuid.uuid4())
        new_token = Token(
            token=token,
            username=user.username,
            login_time=datetime.datetime.now()
        )
        db.session.add(new_token)
        db.session.commit()
        
        print(f"[Login] 用户 {username} 登录成功")
        
        return jsonify({
            'status': 1,
            'message': '登录成功',
            'data': {
                'token': token,
                'username': user.username,
                'name': user.name,
                'role': user.role
            }
        })
        
    except Exception as e:
        print(f"[Login] 登录失败: {e}")
        return jsonify({'status': 0, 'error': str(e)})


@app.route('/api/logout', methods=['POST', 'OPTIONS'])
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


@app.route('/api/check-auth', methods=['GET', 'OPTIONS'])
def check_auth():
    """检查登录状态"""
    if request.method == 'OPTIONS':
        return jsonify({'status': 1})
    
    token = request.headers.get('Authorization')
    if token and token.startswith('Bearer '):
        token = token[7:]
    
    if token:
        token_record = Token.query.filter_by(token=token).first()
        if token_record:
            user = token_record.user
            return jsonify({
                'status': 1,
                'data': {
                    'username': user.username,
                    'name': user.name,
                    'role': user.role
                }
            })
    
    return jsonify({'status': 0, 'error': '未登录'})


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
    print(f"\n{'='*60}")
    print(f"[Upload] 收到上传请求")
    
    try:
        file = request.files['file']
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
            
            # 处理图像
            print(f"[Upload] 开始处理图像...")
            pid, image_info = core.main.c_main(image_path, current_app.model)
            
            result = {
                'status': 1,
                'image_url': 'http://127.0.0.1:5003/tmp/image/' + pid,
                'draw_url': 'http://127.0.0.1:5003/tmp/draw/' + pid,
                'image_info': image_info
            }
            print(f"[Upload] 处理成功!")
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



@app.route("/download", methods=['GET'])
def download_file():
    return send_from_directory('data', 'testfile.zip', as_attachment=True)


@app.route('/tmp/<path:file>', methods=['GET'])
def show_photo(file):
    if request.method == 'GET':
        if file is None:
            pass
        else:
            image_path = os.path.join(BASE_DIR, 'tmp', file)
            image_data = open(image_path, "rb").read()
            response = make_response(image_data)
            response.headers['Content-Type'] = 'image/png'
            return response
    else:
        pass


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
        with app.app_context():
            current_app.model = init_model()
        print("[Server] 启动Flask服务器...")
        print("[Server] 服务器地址: http://127.0.0.1:5003")
        app.run(host='127.0.0.1', port=5003, debug=False, use_reloader=False)
    except Exception as e:
        print(f"[Error] Flask启动失败: {e}")
        import traceback
        traceback.print_exc()


