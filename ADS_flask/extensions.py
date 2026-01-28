"""
Flask 扩展实例
统一管理 db、socketio 等扩展，解决循环依赖问题
"""
from flask_sqlalchemy import SQLAlchemy
from flask_socketio import SocketIO

# 数据库实例
db = SQLAlchemy()

# Socket.IO 实例 - 使用 eventlet 作为异步模式
socketio = SocketIO(cors_allowed_origins="*", async_mode='eventlet')


def emit_progress(percentage, message):
    """发送进度更新到所有客户端"""
    socketio.emit('progress', {
        'percentage': percentage,
        'message': message
    })
