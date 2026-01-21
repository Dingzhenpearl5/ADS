"""
患者相关路由
"""
from flask import Blueprint, request, jsonify

from models import db, Patient
from utils import success_response, error_response, paginate_response, get_pagination_params, log_audit

patient_bp = Blueprint('patient', __name__)


@patient_bp.route('/patient', methods=['GET', 'OPTIONS'])
def get_patient():
    """获取病人信息"""
    if request.method == 'OPTIONS':
        return jsonify({'status': 1})

    patient_id = request.args.get('id')
    
    if patient_id:
        patient = Patient.query.filter_by(patient_id=patient_id).first()
    else:
        patient = Patient.query.first()

    if patient:
        return success_response({
            'patient_id': patient.patient_id,
            'name': patient.name,
            'gender': patient.gender,
            'age': patient.age,
            'phone': patient.phone,
            'part': patient.part,
            # 保持向后兼容的中文键名
            'ID': patient.patient_id,
            '姓名': patient.name,
            '性别': patient.gender,
            '年龄': str(patient.age) if patient.age else '',
            '电话': patient.phone,
            '部位': patient.part
        })
    return error_response('未找到该病人信息')


@patient_bp.route('/patients', methods=['GET', 'OPTIONS'])
def get_patients():
    """获取患者列表"""
    if request.method == 'OPTIONS':
        return jsonify({'status': 1})
    
    try:
        page, per_page = get_pagination_params()
        keyword = request.args.get('keyword')
        
        query = Patient.query
        
        if keyword:
            query = query.filter(
                db.or_(
                    Patient.patient_id.like(f'%{keyword}%'),
                    Patient.name.like(f'%{keyword}%'),
                    Patient.phone.like(f'%{keyword}%')
                )
            )
        
        query = query.order_by(Patient.id.desc())
        
        total = query.count()
        patients = query.offset((page - 1) * per_page).limit(per_page).all()
        
        patient_list = [patient.to_dict() for patient in patients]
        
        return paginate_response(patient_list, total, page, per_page)
        
    except Exception as e:
        return error_response(str(e))


@patient_bp.route('/patients', methods=['POST', 'OPTIONS'])
def create_patient():
    """创建患者"""
    if request.method == 'OPTIONS':
        return jsonify({'status': 1})
    
    try:
        data = request.get_json()
        
        patient_id = data.get('patient_id')
        name = data.get('name')
        
        if not patient_id or not name:
            return error_response('患者ID和姓名不能为空')
        
        if Patient.query.filter_by(patient_id=patient_id).first():
            return error_response('患者ID已存在')
        
        patient = Patient(
            patient_id=patient_id,
            name=name,
            gender=data.get('gender'),
            age=data.get('age'),
            phone=data.get('phone'),
            part=data.get('part', '直肠')
        )
        db.session.add(patient)
        db.session.commit()
        
        log_audit('create', 'patient', target=patient_id)
        
        return success_response(patient.to_dict(), '患者创建成功')
        
    except Exception as e:
        db.session.rollback()
        return error_response(str(e))


@patient_bp.route('/patients/<string:patient_id>', methods=['GET', 'OPTIONS'])
def get_patient_detail(patient_id):
    """获取患者详情"""
    if request.method == 'OPTIONS':
        return jsonify({'status': 1})
    
    try:
        patient = Patient.query.filter_by(patient_id=patient_id).first()
        if not patient:
            return error_response('患者不存在')
        
        return success_response(patient.to_dict())
        
    except Exception as e:
        return error_response(str(e))


@patient_bp.route('/patients/<string:patient_id>', methods=['PUT', 'OPTIONS'])
def update_patient(patient_id):
    """更新患者信息"""
    if request.method == 'OPTIONS':
        return jsonify({'status': 1})
    
    try:
        patient = Patient.query.filter_by(patient_id=patient_id).first()
        if not patient:
            return error_response('患者不存在')
        
        data = request.get_json()
        
        if 'name' in data:
            patient.name = data['name']
        if 'gender' in data:
            patient.gender = data['gender']
        if 'age' in data:
            patient.age = data['age']
        if 'phone' in data:
            patient.phone = data['phone']
        if 'part' in data:
            patient.part = data['part']
        
        db.session.commit()
        
        log_audit('update', 'patient', target=patient_id)
        
        return success_response(patient.to_dict(), '患者信息更新成功')
        
    except Exception as e:
        db.session.rollback()
        return error_response(str(e))


@patient_bp.route('/patients/<string:patient_id>', methods=['DELETE', 'OPTIONS'])
def delete_patient(patient_id):
    """删除患者"""
    if request.method == 'OPTIONS':
        return jsonify({'status': 1})
    
    try:
        patient = Patient.query.filter_by(patient_id=patient_id).first()
        if not patient:
            return error_response('患者不存在')
        
        db.session.delete(patient)
        db.session.commit()
        
        log_audit('delete', 'patient', target=patient_id)
        
        return success_response(message='患者删除成功')
        
    except Exception as e:
        db.session.rollback()
        return error_response(str(e))
