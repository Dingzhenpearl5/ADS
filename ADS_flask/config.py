"""
应用配置文件
"""
import os
from pathlib import Path

# 尝试加载 .env 文件
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # python-dotenv 未安装时跳过

BASE_DIR = Path(__file__).resolve().parent

# 服务器配置
SERVER_HOST = os.environ.get('SERVER_HOST', '127.0.0.1')
SERVER_PORT = int(os.environ.get('SERVER_PORT', 5003))
SERVER_URL = f'http://{SERVER_HOST}:{SERVER_PORT}'

# 文件上传配置
UPLOAD_FOLDER = BASE_DIR / 'uploads'
ALLOWED_EXTENSIONS = {'dcm'}
MAX_CONTENT_LENGTH = 50 * 1024 * 1024  # 50MB

# 数据库配置 - 从环境变量读取，提高安全性
SQLALCHEMY_DATABASE_URI = os.environ.get(
    'DATABASE_URL', 
    'mysql+pymysql://root:123456@127.0.0.1/ads_db'
)
SQLALCHEMY_TRACK_MODIFICATIONS = False
SQLALCHEMY_ENGINE_OPTIONS = {'pool_recycle': 280}

# 安全配置 - 从环境变量读取
SECRET_KEY = os.environ.get('SECRET_KEY', 'your-secret-key-change-in-production')
TOKEN_EXPIRE_HOURS = int(os.environ.get('TOKEN_EXPIRE_HOURS', 24))

# DeepSeek AI 配置
DEEPSEEK_API_KEY = os.environ.get('DEEPSEEK_API_KEY', 'sk-3f82874130094b8e96bfcf0184451994') # 这里的 Key 需要用户替换
DEEPSEEK_API_URL = os.environ.get('DEEPSEEK_API_URL', 'https://api.deepseek.com/chat/completions')


def init_directories():
    """初始化必要的目录"""
    UPLOAD_FOLDER.mkdir(parents=True, exist_ok=True)
    
    for subdir in ['ct', 'image', 'mask', 'draw']:
        tmp_path = BASE_DIR / 'tmp' / subdir
        tmp_path.mkdir(parents=True, exist_ok=True)
