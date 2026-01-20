from core import process, predict, get_feature
import time
import os
import cv2
import numpy as np

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def generate_mock_mask(file_name):
    """生成模拟的mask图像（用于无模型时的测试）"""
    print(f"[Mock] 生成模拟mask...")
    
    # 读取原始图像
    image_path = os.path.join(BASE_DIR, 'tmp', 'image', f'{file_name}.png')
    if os.path.exists(image_path):
        img = cv2.imread(image_path, 0)
        h, w = img.shape
    else:
        h, w = 512, 512
    
    # 创建一个模拟的椭圆形mask（模拟肿瘤区域）
    mask = np.zeros((h, w), dtype=np.uint8)
    center = (w // 2 + 50, h // 2 + 30)  # 稍微偏移中心
    axes = (40, 30)  # 椭圆的轴长
    cv2.ellipse(mask, center, axes, 0, 0, 360, 255, -1)
    
    # 保存mask
    tmp_mask_dir = os.path.join(BASE_DIR, 'tmp', 'mask')
    if not os.path.exists(tmp_mask_dir):
        os.makedirs(tmp_mask_dir)
    mask_path = os.path.join(tmp_mask_dir, f'{file_name}_mask.png')
    cv2.imwrite(mask_path, mask)
    print(f"[Mock] 模拟mask已保存: {mask_path}")


def generate_mock_features():
    """生成模拟的特征数据"""
    return {
        '面积': round(np.random.uniform(800, 1500), 2),
        '周长': round(np.random.uniform(100, 200), 2),
        '重心x': round(np.random.uniform(250, 300), 2),
        '重心y': round(np.random.uniform(280, 320), 2),
        '似圆度': round(np.random.uniform(0.7, 0.95), 4),
        '灰度均值': round(np.random.uniform(100, 150), 2),
        '灰度方差': round(np.random.uniform(20, 50), 2),
        '灰度偏度': round(np.random.uniform(-0.5, 0.5), 4),
        '灰度峰态': round(np.random.uniform(-1, 1), 4),
    }


def c_main(path, model, progress_callback=None):
    """
    主处理函数
    :param path: DCM文件路径
    :param model: 模型对象
    :param progress_callback: 进度回调函数 callback(percentage, message)
    """
    print(f"\n{'='*60}")
    print(f"[Main] 开始处理: {path}")
    start_time = time.time()
    
    def emit(pct, msg):
        if progress_callback:
            progress_callback(pct, msg)
        print(f"[Progress] {pct}% - {msg}")
    
    try:
        # 1. 预处理
        emit(20, '预处理图像...')
        print(f"[Main] Step 1/4: 预处理图像...")
        t1 = time.time()
        image_data = process.pre_process(path)
        print(f"[Main] ✅ 预处理完成 ({time.time()-t1:.2f}秒)")
        
        # 2. 模型预测
        emit(40, '模型推理中...')
        print(f"[Main] Step 2/4: 模型预测...")
        if model is not None:
            t2 = time.time()
            predict.predict(image_data, model)
            print(f"[Main] ✅ 预测完成 ({time.time()-t2:.2f}秒)")
        else:
            print(f"[Main] ⚠️ 模型未加载，使用模拟数据")
            time.sleep(0.5)  # 模拟延迟
            generate_mock_mask(image_data[1])
        
        # 3. 后处理
        emit(70, '后处理生成轮廓...')
        print(f"[Main] Step 3/4: 后处理...")
        t3 = time.time()
        process.last_process(image_data[1])
        print(f"[Main] ✅ 后处理完成 ({time.time()-t3:.2f}秒)")
        
        # 4. 特征提取
        emit(90, '提取特征数据...')
        print(f"[Main] Step 4/4: 特征提取...")
        t4 = time.time()
        if model is not None:
            image_info = get_feature.main(image_data[1])
        else:
            image_info = generate_mock_features()
            print(f"[Main] ⚠️ 使用模拟特征数据")
        print(f"[Main] ✅ 特征提取完成 ({time.time()-t4:.2f}秒)")
        
        total_time = time.time() - start_time
        print(f"[Main] 🎉 全部完成! 总耗时: {total_time:.2f}秒")
        print(f"{'='*60}\n")
        
        return image_data[1] + '.png', image_info
        
    except Exception as e:
        print(f"[Main] ❌ 处理失败: {e}")
        import traceback
        traceback.print_exc()
        raise


if __name__ == '__main__':
    pass
