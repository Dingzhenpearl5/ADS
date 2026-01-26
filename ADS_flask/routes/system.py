"""
系统管理相关路由（设置、公告、审计日志、健康检查）
"""
import datetime
import csv
import io
from flask import Blueprint, request, jsonify, Response
from sqlalchemy import text

from extensions import db
from models import SystemSetting, Announcement, AuditLog, User, Token
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


# ==================== 模型管理 ====================

import os
from pathlib import Path
from werkzeug.utils import secure_filename

# 模型文件存放目录
MODELS_DIR = Path(config.BASE_DIR) / 'core' / 'net' / 'models'
ACTIVE_MODEL_LINK = Path(config.BASE_DIR) / 'core' / 'net' / 'model.pth'


def get_model_info(model_path: Path) -> dict:
    """获取模型文件信息"""
    stat = model_path.stat()
    return {
        'name': model_path.stem,
        'filename': model_path.name,
        'size': stat.st_size,
        'size_mb': round(stat.st_size / (1024 * 1024), 2),
        'created_at': datetime.datetime.fromtimestamp(stat.st_ctime).strftime('%Y-%m-%d %H:%M:%S'),
        'modified_at': datetime.datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M:%S'),
    }


@system_bp.route('/models', methods=['GET', 'OPTIONS'])
@admin_required
def get_models():
    """获取所有可用模型列表"""
    if request.method == 'OPTIONS':
        return jsonify({'status': 1})
    
    try:
        # 确保模型目录存在
        MODELS_DIR.mkdir(parents=True, exist_ok=True)
        
        models = []
        
        # 扫描模型目录中的 .pth 文件
        for model_file in MODELS_DIR.glob('*.pth'):
            info = get_model_info(model_file)
            models.append(info)
        
        # 检查旧的 model.pth（兼容性）
        old_model_path = Path(config.BASE_DIR) / 'core' / 'net' / 'model.pth'
        if old_model_path.exists() and old_model_path.is_file():
            # 检查是否已在 models 目录中（通过硬链接或复制）
            old_model_in_list = any(m['filename'] == 'model.pth' for m in models)
            if not old_model_in_list:
                info = get_model_info(old_model_path)
                info['name'] = 'default'
                info['is_legacy'] = True
                models.append(info)
        
        # 按修改时间排序
        models.sort(key=lambda x: x['modified_at'], reverse=True)
        
        return success_response({
            'models': models,
            'models_dir': str(MODELS_DIR)
        })
        
    except Exception as e:
        return error_response(str(e))


@system_bp.route('/models/current', methods=['GET', 'OPTIONS'])
@admin_required
def get_current_model():
    """获取当前使用的模型信息"""
    if request.method == 'OPTIONS':
        return jsonify({'status': 1})
    
    try:
        from flask import current_app
        
        # 获取当前模型设置
        current_model_setting = SystemSetting.query.filter_by(key='current_model').first()
        current_model_name = current_model_setting.value if current_model_setting else 'default'
        
        # 检查模型是否已加载
        model_loaded = current_app.model is not None
        
        # 获取当前模型文件信息
        model_info = None
        model_path = None
        
        if current_model_name == 'default':
            model_path = Path(config.BASE_DIR) / 'core' / 'net' / 'model.pth'
        else:
            model_path = MODELS_DIR / f'{current_model_name}.pth'
        
        if model_path and model_path.exists():
            model_info = get_model_info(model_path)
        
        # 检查设备
        import torch
        device = 'GPU (CUDA)' if torch.cuda.is_available() else 'CPU'
        
        return success_response({
            'current_model': current_model_name,
            'model_loaded': model_loaded,
            'model_info': model_info,
            'device': device
        })
        
    except Exception as e:
        return error_response(str(e))


@system_bp.route('/models/switch', methods=['POST', 'OPTIONS'])
@admin_required
def switch_model():
    """切换当前使用的模型"""
    if request.method == 'OPTIONS':
        return jsonify({'status': 1})
    
    try:
        from flask import current_app
        import torch
        import core.net.unet as net
        
        data = request.get_json()
        model_name = data.get('model_name')
        
        if not model_name:
            return error_response('请指定模型名称')
        
        # 确定模型路径
        if model_name == 'default':
            model_path = Path(config.BASE_DIR) / 'core' / 'net' / 'model.pth'
        else:
            model_path = MODELS_DIR / f'{model_name}.pth'
        
        if not model_path.exists():
            return error_response(f'模型文件不存在: {model_name}')
        
        # 加载新模型
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        new_model = net.Unet(1, 1).to(device)
        
        if torch.cuda.is_available():
            new_model.load_state_dict(torch.load(str(model_path)))
        else:
            new_model.load_state_dict(torch.load(str(model_path), map_location='cpu'))
        
        new_model.eval()
        
        # 更新应用的模型
        current_app.model = new_model
        
        # 保存当前模型设置到数据库
        user = get_current_user()
        username = user.username if user else 'unknown'
        
        setting = SystemSetting.query.filter_by(key='current_model').first()
        if setting:
            setting.value = model_name
            setting.updated_by = username
        else:
            setting = SystemSetting(
                key='current_model',
                value=model_name,
                category='model',
                description='当前使用的诊断模型',
                updated_by=username
            )
            db.session.add(setting)
        
        db.session.commit()
        
        log_audit('switch', 'model', target=model_name, 
                  detail={'model_path': str(model_path)})
        
        return success_response(
            {'model_name': model_name, 'model_path': str(model_path)},
            message=f'已成功切换到模型: {model_name}'
        )
        
    except Exception as e:
        db.session.rollback()
        return error_response(f'切换模型失败: {str(e)}')


@system_bp.route('/models/upload', methods=['POST', 'OPTIONS'])
@admin_required
def upload_model():
    """上传新模型文件"""
    if request.method == 'OPTIONS':
        return jsonify({'status': 1})
    
    try:
        if 'file' not in request.files:
            return error_response('没有选择文件')
        
        file = request.files['file']
        if file.filename == '':
            return error_response('没有选择文件')
        
        # 检查文件扩展名
        if not file.filename.endswith('.pth'):
            return error_response('仅支持 .pth 格式的模型文件')
        
        # 获取自定义模型名称
        model_name = request.form.get('model_name', '').strip()
        if not model_name:
            model_name = Path(file.filename).stem
        
        # 安全的文件名
        safe_filename = secure_filename(f'{model_name}.pth')
        
        # 确保目录存在
        MODELS_DIR.mkdir(parents=True, exist_ok=True)
        
        # 保存文件
        save_path = MODELS_DIR / safe_filename
        
        # 如果同名文件已存在，添加时间戳
        if save_path.exists():
            timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
            safe_filename = f'{model_name}_{timestamp}.pth'
            save_path = MODELS_DIR / safe_filename
        
        file.save(str(save_path))
        
        # 验证模型文件
        try:
            import torch
            import core.net.unet as net
            
            device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
            test_model = net.Unet(1, 1).to(device)
            
            if torch.cuda.is_available():
                test_model.load_state_dict(torch.load(str(save_path)))
            else:
                test_model.load_state_dict(torch.load(str(save_path), map_location='cpu'))
            
            del test_model  # 释放内存
            
        except Exception as e:
            # 删除无效的模型文件
            save_path.unlink()
            return error_response(f'模型文件无效: {str(e)}')
        
        user = get_current_user()
        log_audit('upload', 'model', target=safe_filename,
                  detail={'size_mb': round(save_path.stat().st_size / (1024 * 1024), 2)})
        
        return success_response({
            'filename': safe_filename,
            'model_name': Path(safe_filename).stem,
            'size_mb': round(save_path.stat().st_size / (1024 * 1024), 2)
        }, message='模型上传成功')
        
    except Exception as e:
        return error_response(f'上传失败: {str(e)}')


@system_bp.route('/models/<model_name>', methods=['DELETE', 'OPTIONS'])
@admin_required
def delete_model(model_name):
    """删除模型文件"""
    if request.method == 'OPTIONS':
        return jsonify({'status': 1})
    
    try:
        if model_name == 'default':
            return error_response('不能删除默认模型')
        
        # 检查是否是当前使用的模型
        current_model_setting = SystemSetting.query.filter_by(key='current_model').first()
        if current_model_setting and current_model_setting.value == model_name:
            return error_response('不能删除当前正在使用的模型，请先切换到其他模型')
        
        model_path = MODELS_DIR / f'{model_name}.pth'
        if not model_path.exists():
            return error_response(f'模型不存在: {model_name}')
        
        # 删除文件
        model_path.unlink()
        
        log_audit('delete', 'model', target=model_name)
        
        return success_response(message=f'模型 {model_name} 已删除')
        
    except Exception as e:
        return error_response(f'删除失败: {str(e)}')
