import os

import SimpleITK as sitk
import cv2
import numpy as np
import torch

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def data_in_one(inputdata):
    if not inputdata.any():
        return inputdata
    inputdata = (inputdata - inputdata.min()) / (inputdata.max() - inputdata.min())
    return inputdata


def pre_process(data_path):
    print(f"[PreProcess] 处理文件: {data_path}")
    
    global test_image, test_mask
    image_list, mask_list, image_data, mask_data = [], [], [], []

    print(f"[PreProcess] 读取DICOM图像...")
    image = sitk.ReadImage(data_path)
    image_array = sitk.GetArrayFromImage(image)
    print(f"[PreProcess] 图像shape: {image_array.shape}")

    print(f"[PreProcess] 提取ROI区域...")
    # ROI_mask = np.zeros(shape=image_array.shape)
    # ROI_mask_mini = np.zeros(shape=(1, 160, 100))
    # ROI_mask_mini[0] = image_array[0][270:430, 200:300]
    # ROI_mask_mini = data_in_one(ROI_mask_mini)
    # ROI_mask[0][270:430, 200:300] = ROI_mask_mini[0]
    
    # 修改为全图输入，并进行CT窗位截断
    img_np = image_array[0].astype(np.float32)
    img_np = np.clip(img_np, -200, 300)
    image_norm = data_in_one(img_np)
    
    # test_image用于后续可视化或其他用途，这里保持一致
    test_image = np.expand_dims(image_norm, axis=0) 
    
    print(f"[PreProcess] 转换为tensor...")
    image_tensor = torch.from_numpy(image_norm).float().unsqueeze(0).unsqueeze(0)
    # shape: (1, 1, 512, 512)
    
    image_data.append(image_tensor)
    file_name = os.path.split(data_path)[1].replace('.dcm', '')

    # 转为图片写入image文件夹
    print(f"[PreProcess] 保存原始图像...")
    image_array = image_array.swapaxes(0, 2)
    image_array = np.rot90(image_array, -1)
    image_array = np.fliplr(image_array).squeeze()
    
    tmp_image_dir = os.path.join(BASE_DIR, 'tmp', 'image')
    if not os.path.exists(tmp_image_dir):
        os.makedirs(tmp_image_dir)
    cv2.imwrite(os.path.join(tmp_image_dir, f'{file_name}.png'), image_array, (cv2.IMWRITE_PNG_COMPRESSION, 0))
    print(f"[PreProcess] 预处理完成")

    return image_data, file_name


def last_process(file_name):
    print(f"[LastProcess] 处理文件: {file_name}")
    
    image_path = os.path.join(BASE_DIR, 'tmp', 'image', f'{file_name}.png')
    mask_path = os.path.join(BASE_DIR, 'tmp', 'mask', f'{file_name}_mask.png')
    
    image = cv2.imread(image_path)
    mask = cv2.imread(mask_path, 0)
    
    print(f"[LastProcess] 查找轮廓...")
    # 兼容不同版本的OpenCV
    # OpenCV 4.x 返回 (contours, hierarchy)
    # OpenCV 3.x 返回 (image, contours, hierarchy)
    result = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if len(result) == 2:
        contours, hierarchy = result
    else:
        _, contours, hierarchy = result
    
    print(f"[LastProcess] 绘制轮廓 (找到{len(contours)}个)...")
    draw = cv2.drawContours(image, contours, -1, (0, 255, 0), 2)
    
    tmp_draw_dir = os.path.join(BASE_DIR, 'tmp', 'draw')
    if not os.path.exists(tmp_draw_dir):
        os.makedirs(tmp_draw_dir)
    output_path = os.path.join(tmp_draw_dir, f'{file_name}.png')
    
    cv2.imwrite(output_path, draw)
    print(f"[LastProcess] 轮廓图保存至: {output_path}")

