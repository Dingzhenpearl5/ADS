"""
DeepSeek AI 分析模块
"""
import requests
import json
import config

def analyze_diagnosis(image_features, risk_level="未知"):
    """
    使用 DeepSeek API 分析诊断结果
    
    Args:
        image_features (dict): 图像特征数据
        risk_level (str): 初步风险等级
        
    Returns:
        dict: AI分析结果
    """
    if not config.DEEPSEEK_API_KEY:
        return {
            "error": "未配置 DeepSeek API Key",
            "conclusion": "无法进行AI分析",
            "description": "请在配置文件中设置 DEEPSEEK_API_KEY"
        }

    # 构建提示词
    prompt = f"""
    你是一个专业的直肠肿瘤辅助诊断AI助手。请根据以下CT影像分析特征，生成一份专业的医疗诊断分析报告。
    
    **影像特征数据:**
    - 肿瘤面积: {image_features.get('面积', '未知')} 像素
    - 肿瘤周长: {image_features.get('周长', '未知')} 像素
    - 似圆度: {image_features.get('似圆度', '未知')} (越接近1越圆)
    - 灰度均值: {image_features.get('灰度均值', '未知')}
    - 灰度方差: {image_features.get('灰度方差', '未知')}
    
    **请生成以下 JSON 格式的回复 (不要包含 markdown 格式):**
    {{
        "conclusion": "简短的诊断结论 (如: 疑似直肠恶性肿瘤)",
        "riskLevel": "风险等级 (低/中/高)",
        "confidence": "置信度数值 (0-100)",
        "description": "详细的病情描述 (100-200字，分析形态、密度等特征)",
        "suggestions": ["建议1", "建议2", "建议3"]
    }}
    """

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {config.DEEPSEEK_API_KEY}"
    }

    payload = {
        "model": "deepseek-chat",
        "messages": [
            {"role": "system", "content": "你是一个严谨的医疗辅助诊断AI，输出必须是合法的JSON格式。"},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.3
    }

    try:
        response = requests.post(config.DEEPSEEK_API_URL, headers=headers, json=payload, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            content = result['choices'][0]['message']['content']
            
            # 清理可能的 markdown 标记
            content = content.replace('```json', '').replace('```', '').strip()
            
            return json.loads(content)
        else:
            print(f"[DeepSeek] API Error: {response.text}")
            return {
                "conclusion": "AI分析服务暂时不可用",
                "riskLevel": "未知",
                "description": f"API请求失败: {response.status_code}",
                "suggestions": ["请稍后重试"]
            }
            
    except Exception as e:
        print(f"[DeepSeek] Exception: {e}")
        return {
            "conclusion": "AI分析发生错误",
            "riskLevel": "未知",
            "description": f"系统错误: {str(e)}",
            "suggestions": ["联系管理员检查日志"]
        }