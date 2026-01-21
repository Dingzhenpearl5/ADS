"""
用户管理相关路由
"""
import hashlib
import json
from flask import Blueprint, request, jsonify

from models import db, User, Token
from utils import (
    success_response, error_response, paginate_response,
    admin_required, get_pagination_params, log_audit
)

user_bp = Blueprint('user', __name__)


@user_bp.route('/users', methods=['GET', 'OPTIONS'])
@admin_required
def get_users():
    """获取用户列表"""
    if request.method == 'OPTIONS':
        return jsonify({'status': 1})
    
    try:
        page, per_page = get_pagination_params()
        role = request.args.get('role')
        status = request.args.get('status')
        keyword = request.args.get('keyword')
        
        query = User.query
        
        if role:
            query = query.filter_by(role=role)
        if status:
            query = query.filter_by(status=status)
        if keyword:
            query = query.filter(
                db.or_(
                    User.username.like(f'%{keyword}%'),
                    User.name.like(f'%{keyword}%')
                )
            )
        
        query = query.order_by(User.id.desc())
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        
        users = [user.to_dict() for user in pagination.items]
        
        return paginate_response(users, pagination.total, page, per_page)
        
    except Exception as e:
        return error_response(str(e))


@user_bp.route('/users', methods=['POST', 'OPTIONS'])
@admin_required
def create_user():
    """创建用户"""
    if request.method == 'OPTIONS':
        return jsonify({'status': 1})
    
    try:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        name = data.get('name')
        role = data.get('role', 'doctor')
        permissions = data.get('permissions', ['rectum'])
        
        if not username or not password:
            return error_response('用户名和密码不能为空')
        
        if User.query.filter_by(username=username).first():
            return error_response('用户名已存在')
        
        user = User(
            username=username,
            password=hashlib.sha256(password.encode()).hexdigest(),
            name=name or username,
            role=role,
            status='active',
            permissions=json.dumps(permissions)
        )
        db.session.add(user)
        db.session.commit()
        
        log_audit('create', 'user', target=username, 
                  detail={'name': name, 'role': role, 'permissions': permissions})
        
        return success_response({
            'id': user.id,
            'username': user.username,
            'name': user.name,
            'role': user.role,
            'permissions': permissions
        }, '用户创建成功')
        
    except Exception as e:
        db.session.rollback()
        return error_response(str(e))


@user_bp.route('/users/<int:user_id>', methods=['GET', 'OPTIONS'])
@admin_required
def get_user(user_id):
    """获取用户详情"""
    if request.method == 'OPTIONS':
        return jsonify({'status': 1})
    
    try:
        user = User.query.get(user_id)
        if not user:
            return error_response('用户不存在')
        
        return success_response(user.to_dict())
        
    except Exception as e:
        return error_response(str(e))


@user_bp.route('/users/<int:user_id>', methods=['PUT', 'OPTIONS'])
@admin_required
def update_user(user_id):
    """更新用户信息"""
    if request.method == 'OPTIONS':
        return jsonify({'status': 1})
    
    try:
        user = User.query.get(user_id)
        if not user:
            return error_response('用户不存在')
        
        if user.role == 'admin':
            return error_response('不能修改管理员账户')
        
        data = request.get_json()
        
        if 'name' in data:
            user.name = data['name']
        if 'role' in data and data['role'] in ['doctor', 'admin']:
            user.role = data['role']
        if 'password' in data and data['password']:
            user.password = hashlib.sha256(data['password'].encode()).hexdigest()
        if 'permissions' in data:
            user.permissions = json.dumps(data['permissions'])
        
        db.session.commit()
        
        log_audit('update', 'user', target=user.username,
                  detail={'updated_fields': list(data.keys())})
        
        return success_response(message='用户更新成功')
        
    except Exception as e:
        db.session.rollback()
        return error_response(str(e))


@user_bp.route('/users/<int:user_id>/status', methods=['PUT', 'OPTIONS'])
@admin_required
def toggle_user_status(user_id):
    """切换用户状态"""
    if request.method == 'OPTIONS':
        return jsonify({'status': 1})
    
    try:
        user = User.query.get(user_id)
        if not user:
            return error_response('用户不存在')
        
        if user.role == 'admin':
            return error_response('不能禁用管理员账户')
        
        data = request.get_json()
        new_status = data.get('status', 'disabled' if user.status == 'active' else 'active')
        
        user.status = new_status
        db.session.commit()
        
        if new_status == 'disabled':
            Token.query.filter_by(username=user.username).delete()
            db.session.commit()
        
        action = 'disable' if new_status == 'disabled' else 'enable'
        log_audit(action, 'user', target=user.username)
        
        return success_response(
            {'status': new_status},
            f'用户已{"禁用" if new_status == "disabled" else "启用"}'
        )
        
    except Exception as e:
        db.session.rollback()
        return error_response(str(e))


@user_bp.route('/users/<int:user_id>', methods=['DELETE', 'OPTIONS'])
@admin_required
def delete_user(user_id):
    """删除用户"""
    if request.method == 'OPTIONS':
        return jsonify({'status': 1})
    
    try:
        user = User.query.get(user_id)
        if not user:
            return error_response('用户不存在')
        
        if user.role == 'admin':
            return error_response('不能删除管理员账户')
        
        username = user.username
        
        Token.query.filter_by(username=username).delete()
        db.session.delete(user)
        db.session.commit()
        
        log_audit('delete', 'user', target=username)
        
        return success_response(message='用户删除成功')
        
    except Exception as e:
        db.session.rollback()
        return error_response(str(e))


@user_bp.route('/users/<int:user_id>/reset-password', methods=['POST', 'OPTIONS'])
@admin_required
def reset_user_password(user_id):
    """重置用户密码"""
    if request.method == 'OPTIONS':
        return jsonify({'status': 1})
    
    try:
        user = User.query.get(user_id)
        if not user:
            return error_response('用户不存在')
        
        data = request.get_json()
        new_password = data.get('password', '123456')
        
        user.password = hashlib.sha256(new_password.encode()).hexdigest()
        db.session.commit()
        
        Token.query.filter_by(username=user.username).delete()
        db.session.commit()
        
        log_audit('reset_password', 'user', target=user.username)
        
        return success_response(message='密码重置成功')
        
    except Exception as e:
        db.session.rollback()
        return error_response(str(e))
