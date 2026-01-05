"""
OCR Web Application Configuration
"""
import os

# Base directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Upload configuration
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
RESULT_FOLDER = os.path.join(BASE_DIR, 'results')
MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size

# Allowed file extensions
ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'pdf'}

# OCR configuration (PaddleOCR 3.x - 性能优化版)
# 使用 Mobile 轻量模型，速度快，精度足够
OCR_CONFIG = {
    'use_doc_orientation_classify': False,  # 关闭文档方向检测
    'use_doc_unwarping': False,             # 关闭文档去畸变
    'use_textline_orientation': False,      # 关闭文字行方向检测 (加速)
    'lang': 'ch',                           # 中英文
    'device': 'cpu',                        # CPU 模式
    # 使用 Mobile 轻量模型替代 Server 模型
    'text_detection_model_name': 'PP-OCRv4_mobile_det',
    'text_recognition_model_name': 'PP-OCRv4_mobile_rec',
}

# Flask configuration
class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'ocr-web-app-secret-key-2024'
    MAX_CONTENT_LENGTH = MAX_CONTENT_LENGTH
    UPLOAD_FOLDER = UPLOAD_FOLDER
    RESULT_FOLDER = RESULT_FOLDER

# Ensure directories exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(RESULT_FOLDER, exist_ok=True)

# ==================== 第三方 OCR API 配置 ====================

# OCR.space API 配置
OCRSPACE_CONFIG = {
    'api_key': os.environ.get('OCRSPACE_API_KEY') or 'K87544821288957',
    'endpoint': 'https://api.ocr.space/parse/image',
    'language': 'chs',  # 简体中文
    'engine': '2',      # OCR Engine 2
}

# 可用的 OCR 服务列表
OCR_SERVICES = {
    'local': {
        'name': '本地识别 (PaddleOCR)',
        'description': '使用本地 PaddleOCR 引擎，无需网络'
    },
    'ocrspace': {
        'name': 'OCR.space (在线)',
        'description': '使用 OCR.space 在线 API'
    }
}

