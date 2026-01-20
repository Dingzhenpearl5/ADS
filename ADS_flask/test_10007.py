import requests
import os

# 获取当前脚本所在目录
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
file_path = os.path.join(BASE_DIR, 'uploads', '10007.dcm')

if not os.path.exists(file_path):
    print(f"错误: 文件不存在 {file_path}")
else:
    with open(file_path, 'rb') as f:
        r = requests.post('http://127.0.0.1:5003/upload', 
                         files={'file': ('10007.dcm', f, 'application/dicom')})
        print('STATUS:', r.status_code)
        try:
            print('RESPONSE:', r.json())
        except:
            print('RESPONSE:', r.text)
