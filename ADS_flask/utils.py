"""
工具函数模块
"""
import datetime
import json
from functools import wraps
from flask import request, jsonify, g

from extensions import db
from models import Token, AuditLog


# ==================== 统一响应格式 ====================

def success_response(data=None, message='操作成功'):
    """
    统一成功响应格式
    :param data: 返回的数据
    :param message: 提示消息
    :return: JSON响应
    """
    response = {
        'status': 1,
        'message': message
    }
    if data is not None:
        response['data'] = data
    return jsonify(response)


def error_response(error='操作失败', code=200):
    """
    统一错误响应格式
    :param error: 错误信息
    :param code: HTTP状态码，默认200保持向后兼容
    :return: JSON响应
    """
    response = jsonify({
        'status': 0,
        'error': error
    })
    return response, code if code != 200 else 200


def paginate_response(items, total, page, per_page):
    """
    统一分页响应格式
    :param items: 数据列表
    :param total: 总数
    :param page: 当前页
    :param per_page: 每页数量
    :return: JSON响应
    """
    return success_response({
        'list': items,
        'total': total,
        'page': page,
        'per_page': per_page,
        'pages': (total + per_page - 1) // per_page if per_page > 0 else 0
    })


# ==================== 分页参数处理 ====================

def get_pagination_params():
    """
    获取统一的分页参数
    支持 page_size 和 per_page 两种命名，统一返回 per_page
    :return: (page, per_page)
    """
    page = request.args.get('page', 1, type=int)
    # 兼容两种命名
    per_page = request.args.get('per_page', type=int) or \
               request.args.get('page_size', type=int) or 20
    
    # 限制范围
    page = max(1, page)
    per_page = max(1, min(100, per_page))
    
    return page, per_page


# ==================== 认证装饰器 ====================

def get_current_user():
    """从Token获取当前用户"""
    token = request.headers.get('Authorization')
    if token and token.startswith('Bearer '):
        token = token[7:]
    
    if not token:
        return None
    
    token_record = Token.query.filter_by(token=token).first()
    if not token_record:
        return None
    
    if datetime.datetime.now() > token_record.expire_time:
        return None
    
    return token_record.user


def token_required(f):
    """验证Token的装饰器"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # OPTIONS 请求直接通过
        if request.method == 'OPTIONS':
            return jsonify({'status': 1})
        
        token = request.headers.get('Authorization')
        if token and token.startswith('Bearer '):
            token = token[7:]
        
        if not token:
            return error_response('缺少认证Token', 401)
        
        token_record = Token.query.filter_by(token=token).first()
        if not token_record:
            return error_response('Token无效', 401)
        
        if datetime.datetime.now() > token_record.expire_time:
            db.session.delete(token_record)
            db.session.commit()
            return error_response('Token已过期,请重新登录', 401)
        
        # 将用户信息存储到g对象和request
        g.current_user = token_record.user
        request.current_user = token_record.user
        return f(*args, **kwargs)
    
    return decorated_function


def admin_required(f):
    """验证管理员权限的装饰器"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if request.method == 'OPTIONS':
            return jsonify({'status': 1})
        
        token = request.headers.get('Authorization')
        if token and token.startswith('Bearer '):
            token = token[7:]
        
        if not token:
            return error_response('缺少认证Token', 401)
        
        token_record = Token.query.filter_by(token=token).first()
        if not token_record:
            return error_response('Token无效', 401)
        
        if datetime.datetime.now() > token_record.expire_time:
            db.session.delete(token_record)
            db.session.commit()
            return error_response('Token已过期,请重新登录', 401)
        
        if token_record.user.role != 'admin':
            return error_response('需要管理员权限', 403)
        
        g.current_user = token_record.user
        request.current_user = token_record.user
        return f(*args, **kwargs)
    
    return decorated_function


# ==================== 审计日志 ====================

def log_audit(action, module, target=None, detail=None, status='success', username=None):
    """
    记录审计日志
    :param action: 操作类型 (login/logout/create/update/delete/export/upload/view)
    :param module: 模块名称 (auth/settings/announcement/diagnosis/patient/system/user)
    :param target: 操作目标
    :param detail: 详细信息（字典或字符串）
    :param status: 状态 (success/fail)
    :param username: 用户名（如果不传则自动从token获取）
    """
    try:
        if not username:
            user = get_current_user()
            if user:
                username = user.username
        
        # 获取IP地址
        ip_address = request.headers.get('X-Forwarded-For', request.remote_addr)
        if ip_address and ',' in ip_address:
            ip_address = ip_address.split(',')[0].strip()
        
        # 获取User-Agent
        user_agent = request.headers.get('User-Agent', '')[:500]
        
        # 处理detail
        if detail and isinstance(detail, dict):
            detail = json.dumps(detail, ensure_ascii=False)
        
        audit_log = AuditLog(
            username=username,
            action=action,
            module=module,
            target=str(target) if target else None,
            detail=detail,
            ip_address=ip_address,
            user_agent=user_agent,
            status=status
        )
        db.session.add(audit_log)
        db.session.commit()
    except Exception as e:
        print(f"[Audit] 记录审计日志失败: {e}")


# ==================== 文件处理 ====================

def allowed_file(filename, allowed_extensions):
    """检查文件扩展名是否允许"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in allowed_extensions
