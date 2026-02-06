import SimpleITK as sitk
import cv2
import numpy as np
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

np.set_printoptions(suppress=True)

# 精简后的核心特征：仅保留对诊断有实际意义的 5 项
FEATURE_LABELS = {
    'area':      '肿瘤面积',
    'perimeter': '肿瘤周长',
    'ellipse':   '似圆度',
    'mean':      '灰度均值',
    'std':       '灰度标准差',
}


def _get_geometry_feature(mask_array):
    """从分割 mask 中提取形态特征：面积、周长、似圆度"""
    result = cv2.findContours(mask_array.copy(), cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    contours = result[0] if len(result) == 2 else result[1]

    best_area = 0
    best_perimeter = 0
    best_ellipse = 0

    for c in contours:
        a = cv2.contourArea(c)
        p = cv2.arcLength(c, True)
        if a > best_area:
            best_area = a
            best_perimeter = round(p, 4)
            try:
                (_, _), (MA, ma), _ = cv2.fitEllipse(c)
                best_ellipse = round(ma - MA, 4)
            except Exception:
                best_ellipse = 0

    return best_area, best_perimeter, best_ellipse


def _get_gray_feature(image_array, mask_array):
    """从 ROI 区域提取灰度统计特征：均值、标准差"""
    index = np.nonzero(mask_array)
    roi_values = image_array[index]
    return round(float(np.mean(roi_values)), 4), round(float(np.std(roi_values)), 4)


def get_feature(ct_path, mask_path):
    """
    提取肿瘤核心特征（精简版）

    Returns:
        dict | None: 特征字典，未检测到肿瘤时返回 None
    """
    mask_array = cv2.imread(mask_path, 0)
    image = sitk.ReadImage(ct_path)
    image_array = sitk.GetArrayFromImage(image)[0, :, :]

    index = np.nonzero(mask_array)
    if not index[0].any():
        return None

    # 形态特征
    area, perimeter, ellipse = _get_geometry_feature(mask_array)

    # 灰度特征
    gray_mean, gray_std = _get_gray_feature(image_array, mask_array)

    return {
        'area':      area,
        'perimeter': perimeter,
        'ellipse':   ellipse,
        'mean':      gray_mean,
        'std':       gray_std,
    }


def main(pid):
    """
    主入口：根据 pid 提取特征并返回带中文标签的结果
    """
    ct_path = os.path.join(BASE_DIR, 'tmp', 'ct', f'{pid}.dcm')
    mask_path = os.path.join(BASE_DIR, 'tmp', 'mask', f'{pid}_mask.png')

    features = get_feature(ct_path, mask_path)

    if features is None:
        print(f"⚠️ 未检测到肿瘤: {pid}")
        return {'status': 'no_tumor', 'message': '未检测到肿瘤区域'}

    # 附加中文标签，格式: {key: [中文名, 数值]}
    result = {}
    for key, value in features.items():
        result[key] = [FEATURE_LABELS[key], value]

    return result


if __name__ == '__main__':
    pass
