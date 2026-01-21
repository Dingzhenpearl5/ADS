"""
应用配置文件
"""
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 服务器配置
SERVER_HOST = '127.0.0.1'
SERVER_PORT = 5003
SERVER_URL = f'http://{SERVER_HOST}:{SERVER_PORT}'

# 文件上传配置
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
ALLOWED_EXTENSIONS = {'dcm'}
MAX_CONTENT_LENGTH = 50 * 1024 * 1024  # 50MB

# 数据库配置
# 生产环境应使用环境变量: os.environ.get('DATABASE_URL')
SQLALCHEMY_DATABASE_URI = os.environ.get(
    'DATABASE_URL', 
    'mysql+pymysql://root:123456@localhost/ads_db'
)
SQLALCHEMY_TRACK_MODIFICATIONS = False
SQLALCHEMY_ENGINE_OPTIONS = {'pool_recycle': 280}

# 安全配置
SECRET_KEY = os.environ.get('SECRET_KEY', 'your-secret-key-change-in-production')
TOKEN_EXPIRE_HOURS = 24

# 创建必要的目录
def init_directories():
    """初始化必要的目录"""
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
    
    for subdir in ['ct', 'image', 'mask', 'draw']:
        tmp_path = os.path.join(BASE_DIR, 'tmp', subdir)
        if not os.path.exists(tmp_path):
            os.makedirs(tmp_path)
