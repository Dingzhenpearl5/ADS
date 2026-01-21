"""
系统管理相关路由（设置、公告、审计日志、健康检查）
"""
import datetime
import csv
import io
from flask import Blueprint, request, jsonify, Response
from sqlalchemy import text

from models import db, SystemSetting, Announcement, AuditLog, User, Token
from utils import (
    success_response, error_response, paginate_response,
    admin_required, get_pagination_params, log_audit, get_current_user
)
import config

system_bp = Blueprint('system', __name__)


# ==================== 健康检查 ====================

@system_bp.route('/health', methods=['GET'])
def health_check():
    """健康检查接口"""
    from flask import current_app
    model_status = '已加载' if current_app.model is not None else '未加载(模拟模式)'
    
    try:
        db.session.execute(text('SELECT 1'))
        db_status = '正常'
    except:
        db_status = '异常'
    
    return success_response({
        'server': config.SERVER_URL,
        'model': model_status,
        'database': db_status,
        'version': '1.0.0'
    }, '服务运行正常')


# ==================== 系统设置 ====================

@system_bp.route('/settings', methods=['GET', 'OPTIONS'])
@admin_required
def get_settings():
    """获取所有系统设置"""
    if request.method == 'OPTIONS':
        return jsonify({'status': 1})
    
    try:
        settings = SystemSetting.query.all()
        
        result = {
            'analysis': [],
            'report': [],
            'system': []
        }
        
        for setting in settings:
            item = setting.to_dict()
            if setting.category in result:
                result[setting.category].append(item)
        
        return success_response(result)
        
    except Exception as e:
        return error_response(str(e))


@system_bp.route('/settings', methods=['POST'])
@admin_required
def update_settings():
    """更新系统设置"""
    try:
        data = request.get_json()
        if not data or 'settings' not in data:
            return error_response('缺少设置数据')
        
        user = get_current_user()
        username = user.username if user else 'unknown'
        
        settings = data['settings']
        updated_count = 0
        
        for key, value in settings.items():
            setting = SystemSetting.query.filter_by(key=key).first()
            if setting:
                setting.value = str(value)
                setting.updated_by = username
                updated_count += 1
            else:
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
        
        log_audit('update', 'settings', 
                  detail={'updated_count': updated_count, 'keys': list(settings.keys())})
        
        return success_response(message=f'成功更新 {updated_count} 项设置')
        
    except Exception as e:
        db.session.rollback()
        return error_response(str(e))


@system_bp.route('/settings/<key>', methods=['GET'])
def get_setting(key):
    """获取单个设置项"""
    try:
        setting = SystemSetting.query.filter_by(key=key).first()
        if not setting:
            return error_response('设置项不存在')
        
        return success_response({
            'key': setting.key,
            'value': setting.value,
            'description': setting.description
        })
        
    except Exception as e:
        return error_response(str(e))


@system_bp.route('/settings/reset', methods=['POST'])
@admin_required
def reset_settings():
    """重置设置为默认值"""
    try:
        data = request.get_json()
        category = data.get('category') if data else None
        
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
        
        user = get_current_user()
        username = user.username if user else 'unknown'
        
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
        
        log_audit('reset', 'settings', 
                  detail={'category': category or 'all', 'reset_count': reset_count})
        
        return success_response(message=f'成功重置 {reset_count} 项设置')
        
    except Exception as e:
        db.session.rollback()
        return error_response(str(e))


# ==================== 审计日志 ====================

@system_bp.route('/audit-logs', methods=['GET', 'OPTIONS'])
@admin_required
def get_audit_logs():
    """获取审计日志列表"""
    if request.method == 'OPTIONS':
        return jsonify({'status': 1})
    
    try:
        page, per_page = get_pagination_params()
        username = request.args.get('username')
        action = request.args.get('action')
        module = request.args.get('module')
        status = request.args.get('status')
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        keyword = request.args.get('keyword')
        
        query = AuditLog.query
        
        if username:
            query = query.filter(AuditLog.username.like(f'%{username}%'))
        if action:
            query = query.filter_by(action=action)
        if module:
            query = query.filter_by(module=module)
        if status:
            query = query.filter_by(status=status)
        if start_date:
            try:
                start = datetime.datetime.strptime(start_date, '%Y-%m-%d')
                query = query.filter(AuditLog.created_at >= start)
            except:
                pass
        if end_date:
            try:
                end = datetime.datetime.strptime(end_date, '%Y-%m-%d') + datetime.timedelta(days=1)
                query = query.filter(AuditLog.created_at < end)
            except:
                pass
        if keyword:
            query = query.filter(
                db.or_(
                    AuditLog.target.like(f'%{keyword}%'),
                    AuditLog.detail.like(f'%{keyword}%')
                )
            )
        
        query = query.order_by(AuditLog.created_at.desc())
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        
        logs = [log.to_dict() for log in pagination.items]
        
        return paginate_response(logs, pagination.total, page, per_page)
        
    except Exception as e:
        return error_response(str(e))


@system_bp.route('/audit-logs/stats', methods=['GET', 'OPTIONS'])
@admin_required
def get_audit_stats():
    """获取审计日志统计信息"""
    if request.method == 'OPTIONS':
        return jsonify({'status': 1})
    
    try:
        total = AuditLog.query.count()
        
        today = datetime.datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        today_count = AuditLog.query.filter(AuditLog.created_at >= today).count()
        
        module_stats = db.session.query(
            AuditLog.module, 
            db.func.count(AuditLog.id)
        ).group_by(AuditLog.module).all()
        
        action_stats = db.session.query(
            AuditLog.action, 
            db.func.count(AuditLog.id)
        ).group_by(AuditLog.action).all()
        
        seven_days_ago = today - datetime.timedelta(days=6)
        daily_stats = db.session.query(
            db.func.date(AuditLog.created_at).label('date'),
            db.func.count(AuditLog.id)
        ).filter(
            AuditLog.created_at >= seven_days_ago
        ).group_by(
            db.func.date(AuditLog.created_at)
        ).all()
        
        active_users = db.session.query(
            AuditLog.username,
            db.func.count(AuditLog.id).label('count')
        ).filter(
            AuditLog.created_at >= seven_days_ago,
            AuditLog.username.isnot(None)
        ).group_by(
            AuditLog.username
        ).order_by(
            db.func.count(AuditLog.id).desc()
        ).limit(10).all()
        
        return success_response({
            'total': total,
            'today_count': today_count,
            'module_stats': [{'module': m, 'count': c} for m, c in module_stats],
            'action_stats': [{'action': a, 'count': c} for a, c in action_stats],
            'daily_stats': [{'date': str(d), 'count': c} for d, c in daily_stats],
            'active_users': [{'username': u, 'count': c} for u, c in active_users]
        })
        
    except Exception as e:
        return error_response(str(e))


@system_bp.route('/audit-logs/export', methods=['GET', 'OPTIONS'])
@admin_required
def export_audit_logs():
    """导出审计日志"""
    if request.method == 'OPTIONS':
        return jsonify({'status': 1})
    
    try:
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        query = AuditLog.query
        
        if start_date:
            try:
                start = datetime.datetime.strptime(start_date, '%Y-%m-%d')
                query = query.filter(AuditLog.created_at >= start)
            except:
                pass
        if end_date:
            try:
                end = datetime.datetime.strptime(end_date, '%Y-%m-%d') + datetime.timedelta(days=1)
                query = query.filter(AuditLog.created_at < end)
            except:
                pass
        
        logs = query.order_by(AuditLog.created_at.desc()).limit(10000).all()
        
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(['ID', '用户名', '操作类型', '模块', '目标', '详情', 'IP地址', '状态', '时间'])
        
        for log in logs:
            writer.writerow([
                log.id,
                log.username or '',
                log.action,
                log.module,
                log.target or '',
                log.detail or '',
                log.ip_address or '',
                log.status,
                log.created_at.strftime('%Y-%m-%d %H:%M:%S') if log.created_at else ''
            ])
        
        output.seek(0)
        
        log_audit('export', 'audit', detail=f'导出审计日志 {len(logs)} 条')
        
        return Response(
            output.getvalue().encode('utf-8-sig'),
            mimetype='text/csv',
            headers={
                'Content-Disposition': f'attachment; filename=audit_logs_{datetime.datetime.now().strftime("%Y%m%d")}.csv'
            }
        )
        
    except Exception as e:
        return error_response(str(e))


# ==================== 系统公告 ====================

@system_bp.route('/announcements', methods=['GET', 'OPTIONS'])
def get_announcements():
    """获取公告列表"""
    if request.method == 'OPTIONS':
        return jsonify({'status': 1})
    
    try:
        user = get_current_user()
        is_admin = user and user.role == 'admin'
        
        status = request.args.get('status')
        page, per_page = get_pagination_params()
        
        query = Announcement.query
        
        if status:
            query = query.filter_by(status=status)
        elif not is_admin:
            query = query.filter_by(status='published')
        
        query = query.order_by(Announcement.priority.desc(), Announcement.created_at.desc())
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        
        announcements = [ann.to_dict() for ann in pagination.items]
        
        return success_response({
            'items': announcements,
            'list': announcements,  # 兼容两种格式
            'total': pagination.total,
            'page': page,
            'per_page': per_page
        })
        
    except Exception as e:
        return error_response(str(e))


@system_bp.route('/announcements', methods=['POST', 'OPTIONS'])
@admin_required
def create_announcement():
    """创建公告"""
    try:
        data = request.get_json()
        if not data:
            return error_response('缺少数据')
        
        title = data.get('title')
        content = data.get('content')
        
        if not title or not content:
            return error_response('标题和内容不能为空')
        
        user = get_current_user()
        username = user.username if user else 'unknown'
        
        announcement = Announcement(
            title=title,
            content=content,
            type=data.get('type', 'info'),
            priority=data.get('priority', 0),
            status=data.get('status', 'draft'),
            created_by=username
        )
        
        if data.get('status') == 'published':
            announcement.published_at = datetime.datetime.now()
        
        db.session.add(announcement)
        db.session.commit()
        
        log_audit('create', 'announcement', target=announcement.id, detail={'title': title})
        
        return success_response({'id': announcement.id}, '公告创建成功')
        
    except Exception as e:
        db.session.rollback()
        return error_response(str(e))


@system_bp.route('/announcements/<int:id>', methods=['GET'])
def get_announcement(id):
    """获取单个公告详情"""
    try:
        announcement = Announcement.query.get(id)
        if not announcement:
            return error_response('公告不存在')
        
        return success_response(announcement.to_dict())
        
    except Exception as e:
        return error_response(str(e))


@system_bp.route('/announcements/<int:id>', methods=['PUT', 'OPTIONS'])
@admin_required
def update_announcement(id):
    """更新公告"""
    try:
        announcement = Announcement.query.get(id)
        if not announcement:
            return error_response('公告不存在')
        
        data = request.get_json()
        if not data:
            return error_response('缺少数据')
        
        if 'title' in data:
            announcement.title = data['title']
        if 'content' in data:
            announcement.content = data['content']
        if 'type' in data:
            announcement.type = data['type']
        if 'priority' in data:
            announcement.priority = data['priority']
        
        db.session.commit()
        
        log_audit('update', 'announcement', target=id, detail={'title': announcement.title})
        
        return success_response(message='公告更新成功')
        
    except Exception as e:
        db.session.rollback()
        return error_response(str(e))


@system_bp.route('/announcements/<int:id>/publish', methods=['POST', 'OPTIONS'])
@admin_required
def publish_announcement(id):
    """发布公告"""
    try:
        announcement = Announcement.query.get(id)
        if not announcement:
            return error_response('公告不存在')
        
        announcement.status = 'published'
        announcement.published_at = datetime.datetime.now()
        db.session.commit()
        
        log_audit('publish', 'announcement', target=id, detail={'title': announcement.title})
        
        return success_response(message='公告已发布')
        
    except Exception as e:
        db.session.rollback()
        return error_response(str(e))


@system_bp.route('/announcements/<int:id>/archive', methods=['POST', 'OPTIONS'])
@admin_required
def archive_announcement(id):
    """下架公告"""
    try:
        announcement = Announcement.query.get(id)
        if not announcement:
            return error_response('公告不存在')
        
        announcement.status = 'archived'
        db.session.commit()
        
        log_audit('archive', 'announcement', target=id, detail={'title': announcement.title})
        
        return success_response(message='公告已下架')
        
    except Exception as e:
        db.session.rollback()
        return error_response(str(e))


@system_bp.route('/announcements/<int:id>', methods=['DELETE', 'OPTIONS'])
@admin_required
def delete_announcement(id):
    """删除公告"""
    try:
        announcement = Announcement.query.get(id)
        if not announcement:
            return error_response('公告不存在')
        
        title = announcement.title
        db.session.delete(announcement)
        db.session.commit()
        
        log_audit('delete', 'announcement', target=id, detail={'title': title})
        
        return success_response(message='公告已删除')
        
    except Exception as e:
        db.session.rollback()
        return error_response(str(e))
