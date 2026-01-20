-- ============================================================
-- 直肠肿瘤辅助诊断系统 - 数据库初始化脚本
-- 运行此脚本前请确保MySQL服务已启动
-- ============================================================

-- 创建数据库
CREATE DATABASE IF NOT EXISTS ads_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- 使用数据库
USE ads_db;

-- ============================================================
-- 1. 用户表
-- ============================================================
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL COMMENT '用户名',
    password VARCHAR(255) NOT NULL COMMENT '密码(SHA256加密)',
    name VARCHAR(50) COMMENT '姓名',
    role VARCHAR(20) COMMENT '角色: admin/doctor',
    status VARCHAR(20) DEFAULT 'active' COMMENT '状态: active/disabled',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='用户表';

-- ============================================================
-- 2. Token表
-- ============================================================
CREATE TABLE IF NOT EXISTS tokens (
    id INT AUTO_INCREMENT PRIMARY KEY,
    token VARCHAR(100) UNIQUE NOT NULL COMMENT '令牌',
    username VARCHAR(50) NOT NULL COMMENT '用户名',
    login_time DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '登录时间',
    expire_time DATETIME NOT NULL COMMENT '过期时间',
    FOREIGN KEY (username) REFERENCES users(username) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='登录令牌表';

-- ============================================================
-- 3. 登录尝试记录表
-- ============================================================
CREATE TABLE IF NOT EXISTS login_attempts (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL COMMENT '用户名',
    attempt_time DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '尝试时间',
    success TINYINT(1) DEFAULT 0 COMMENT '是否成功',
    ip_address VARCHAR(50) COMMENT 'IP地址'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='登录尝试记录表';

-- ============================================================
-- 4. 患者表
-- ============================================================
CREATE TABLE IF NOT EXISTS patients (
    id INT AUTO_INCREMENT PRIMARY KEY,
    patient_id VARCHAR(50) UNIQUE NOT NULL COMMENT '患者ID',
    name VARCHAR(50) NOT NULL COMMENT '姓名',
    gender VARCHAR(10) COMMENT '性别',
    age INT COMMENT '年龄',
    phone VARCHAR(20) COMMENT '电话',
    part VARCHAR(50) COMMENT '检查部位'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='患者表';

-- ============================================================
-- 5. 诊断记录表
-- ============================================================
CREATE TABLE IF NOT EXISTS diagnosis_records (
    id INT AUTO_INCREMENT PRIMARY KEY,
    patient_id VARCHAR(50) COMMENT '患者ID',
    doctor_username VARCHAR(50) COMMENT '医生用户名',
    
    -- 文件信息
    filename VARCHAR(255) NOT NULL COMMENT '文件名',
    image_url VARCHAR(500) COMMENT '图像URL',
    draw_url VARCHAR(500) COMMENT '标注图URL',
    
    -- 诊断结果
    area FLOAT COMMENT '面积',
    perimeter FLOAT COMMENT '周长',
    features TEXT COMMENT '特征数据(JSON格式)',
    
    -- 医生诊断
    doctor_diagnosis TEXT COMMENT '医生诊断描述',
    doctor_suggestion TEXT COMMENT '治疗建议',
    diagnosis_conclusion VARCHAR(100) COMMENT '诊断结论',
    
    -- 时间信息
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    
    FOREIGN KEY (patient_id) REFERENCES patients(patient_id) ON DELETE SET NULL,
    FOREIGN KEY (doctor_username) REFERENCES users(username) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='诊断记录表';

-- ============================================================
-- 6. 系统设置表
-- ============================================================
CREATE TABLE IF NOT EXISTS system_settings (
    id INT AUTO_INCREMENT PRIMARY KEY,
    `key` VARCHAR(100) UNIQUE NOT NULL COMMENT '设置键',
    value TEXT COMMENT '设置值(JSON格式)',
    description VARCHAR(255) COMMENT '说明',
    category VARCHAR(50) COMMENT '分类: analysis/report/system',
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    updated_by VARCHAR(50) COMMENT '更新人'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='系统设置表';

-- ============================================================
-- 7. 系统公告表
-- ============================================================
CREATE TABLE IF NOT EXISTS announcements (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(200) NOT NULL COMMENT '标题',
    content TEXT NOT NULL COMMENT '内容',
    type VARCHAR(20) DEFAULT 'info' COMMENT '类型: info/warning/success/error',
    priority INT DEFAULT 0 COMMENT '优先级',
    status VARCHAR(20) DEFAULT 'draft' COMMENT '状态: draft/published/archived',
    created_by VARCHAR(50) COMMENT '创建人',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    published_at DATETIME COMMENT '发布时间',
    FOREIGN KEY (created_by) REFERENCES users(username) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='系统公告表';

-- ============================================================
-- 8. 审计日志表
-- ============================================================
CREATE TABLE IF NOT EXISTS audit_logs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) COMMENT '操作用户',
    action VARCHAR(50) NOT NULL COMMENT '操作类型',
    module VARCHAR(50) NOT NULL COMMENT '模块',
    target VARCHAR(255) COMMENT '操作目标',
    detail TEXT COMMENT '详细信息(JSON格式)',
    ip_address VARCHAR(50) COMMENT 'IP地址',
    user_agent VARCHAR(500) COMMENT '浏览器信息',
    status VARCHAR(20) DEFAULT 'success' COMMENT '状态: success/fail',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    FOREIGN KEY (username) REFERENCES users(username) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='审计日志表';

-- ============================================================
-- 初始数据
-- ============================================================

-- 创建管理员账户 (密码: admin123)
INSERT IGNORE INTO users (username, password, name, role) VALUES 
('admin', '240be518fabd2724ddb6f04eeb9d5b07d8213f9e81ef5d1d4f2a8e0c8e8a6c3b', '系统管理员', 'admin');

-- 创建医生账户 (密码: doctor123)
INSERT IGNORE INTO users (username, password, name, role) VALUES 
('zhangwei', 'a665a45920422f9d417e4867efdc4fb8a04a1f3fff1fa07e998e86f7f7a27ae3', '医生张伟', 'doctor'),
('lina', 'a665a45920422f9d417e4867efdc4fb8a04a1f3fff1fa07e998e86f7f7a27ae3', '医生李娜', 'doctor'),
('wangqiang', 'a665a45920422f9d417e4867efdc4fb8a04a1f3fff1fa07e998e86f7f7a27ae3', '医生王强', 'doctor');

-- 初始系统设置
INSERT IGNORE INTO system_settings (`key`, value, description, category, updated_by) VALUES 
('analysis.threshold', '{"良性": 0.6, "恶性": 0.8}', '分析阈值设置', 'analysis', 'system'),
('analysis.features', '["面积", "周长", "圆度", "紧凑度", "偏心率", "等效直径", "主轴长度", "次轴长度"]', '启用的特征列表', 'analysis', 'system'),
('report.template', '{"format": "standard", "includeImages": true, "includeFeatures": true}', '报告模板设置', 'report', 'system'),
('system.sessionTimeout', '3600', '会话超时时间（秒）', 'system', 'system'),
('system.maxUploadSize', '50', '最大上传文件大小（MB）', 'system', 'system'),
('system.autoBackup', '{"enabled": false, "interval": "daily", "retention": 30}', '自动备份设置', 'system', 'system');

-- 初始公告
INSERT IGNORE INTO announcements (title, content, type, priority, status, created_by, published_at) VALUES 
('欢迎使用直肠肿瘤辅助诊断系统', '本系统基于深度学习技术，为医生提供直肠肿瘤影像分析辅助诊断功能。请上传DICOM格式的CT影像进行分析。', 'success', 10, 'published', 'admin', NOW()),
('系统使用说明', '1. 使用医生账号登录系统\n2. 在诊断页面上传患者CT影像（DICOM格式）\n3. 系统自动进行图像分割和特征提取\n4. 查看诊断结果和特征数据\n5. 填写医生诊断意见并保存记录\n6. 在历史记录中查看所有诊断结果', 'info', 9, 'published', 'admin', NOW()),
('数据安全提示', '请注意保护患者隐私信息，所有上传的影像数据仅用于医学诊断目的。系统会自动记录所有操作日志以确保数据安全。', 'warning', 8, 'published', 'admin', NOW());
