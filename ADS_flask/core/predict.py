"""
CT图像预测模块
纯函数设计，避免全局变量，确保线程安全
"""
from pathlib import Path
import cv2
import torch
import numpy as np

BASE_DIR = Path(__file__).resolve().parent.parent

# CUDA 和线程配置
import os
os.environ["CUDA_VISIBLE_DEVICES"] = "0"
torch.set_num_threads(4)
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
torch.cuda.empty_cache()

# 二值化阈值
THRESHOLD = 0.5


def predict(dataset, model):
    """
    使用模型进行预测
    
    Args:
        dataset: 包含图像数据和文件名的元组 ((tensor,), filename)
        model: PyTorch 模型
        
    Returns:
        dict: 包含 mask_path, mask_array, img_y 的结果字典
    """
    print(f"[Predict] 开始预测...")
    
    try:
        with torch.no_grad():
            print(f"[Predict] 准备数据...")
            x = dataset[0][0].to(device)
            file_name = dataset[1]
            print(f"[Predict] 文件名: {file_name}, 输入shape: {x.shape}")

            # 打印输入数值范围
            x_min = float(x.min().cpu().numpy())
            x_max = float(x.max().cpu().numpy())
            print(f"[Predict] 输入范围: min={x_min}, max={x_max}")

            print(f"[Predict] 开始模型推理...")
            y = model(x)
            print(f"[Predict] 推理完成，输出shape: {y.shape}")

            # 打印输出统计信息
            y_min = float(y.min().cpu().numpy())
            y_max = float(y.max().cpu().numpy())
            print(f"[Predict] 输出范围: min={y_min}, max={y_max}")

            print(f"[Predict] 后处理中...")
            img_y = torch.squeeze(y).cpu().numpy()
            
            # 根据输出范围选择二值化方式
            if y_max <= 1.0:
                bin_mask = (img_y >= THRESHOLD).astype('uint8')
            else:
                bin_mask = (img_y != 0).astype('uint8')

            # 将二值掩码扩展到0-255
            mask_array = (bin_mask * 255).astype('uint8')

            # 打印唯一值以确认是否有正例
            unique_vals = np.unique(mask_array)
            print(f"[Predict] mask 唯一值: {unique_vals}")

            # 保存 mask 文件
            tmp_mask_dir = BASE_DIR / 'tmp' / 'mask'
            tmp_mask_dir.mkdir(parents=True, exist_ok=True)
            mask_path = tmp_mask_dir / f'{file_name}_mask.png'
            
            cv2.imwrite(str(mask_path), mask_array, [cv2.IMWRITE_PNG_COMPRESSION, 0])
            
            # ========== 新增：生成热力图 (Heatmap) ==========
            # 将概率图映射到 0-255
            heatmap_norm = (img_y * 255).astype(np.uint8)
            # 应用伪彩色 (JET colormap: 蓝色=低概率, 红色=高概率)
            heatmap_color = cv2.applyColorMap(heatmap_norm, cv2.COLORMAP_JET)
            
            # 保存热力图
            tmp_heatmap_dir = BASE_DIR / 'tmp' / 'heatmap'
            tmp_heatmap_dir.mkdir(parents=True, exist_ok=True)
            heatmap_path = tmp_heatmap_dir / f'{file_name}_heatmap.png'
            
            cv2.imwrite(str(heatmap_path), heatmap_color)
            print(f"[Predict] 🔥 热力图已生成: {heatmap_path}")
            # ===============================================

            print(f"[Predict] ✅ 预测完成，mask保存至: {mask_path}")
            
            # 返回结果字典
            return {
                'mask_path': str(mask_path),
                'heatmap_path': str(heatmap_path),
                'mask_array': mask_array,
                'img_y': img_y,
                'file_name': file_name
            }
            
    except Exception as e:
        print(f"[Predict] ❌ 预测失败: {e}")
        import traceback
        traceback.print_exc()
        raise


if __name__ == '__main__':
    pass
