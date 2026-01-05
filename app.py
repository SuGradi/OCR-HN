"""
OCR Web Application - Main Flask Application
Supports image (JPG, PNG, JPEG) and PDF file OCR recognition
"""
import os
import re
import uuid
import logging
import requests
import base64
from datetime import datetime
from flask import Flask, render_template, request, jsonify, send_file
from werkzeug.utils import secure_filename
from PIL import Image
import io

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Import configuration
from config import (Config, ALLOWED_EXTENSIONS, OCR_CONFIG, UPLOAD_FOLDER, 
                    RESULT_FOLDER, OCRSPACE_CONFIG)

# Initialize Flask app
app = Flask(__name__)
app.config.from_object(Config)

# Lazy load PaddleOCR to speed up startup
_ocr_instance = None

def get_ocr():
    """Get or create PaddleOCR instance (lazy loading)"""
    global _ocr_instance
    if _ocr_instance is None:
        logger.info("Initializing PaddleOCR engine...")
        from paddleocr import PaddleOCR
        _ocr_instance = PaddleOCR(**OCR_CONFIG)
        logger.info("PaddleOCR engine initialized successfully")
    return _ocr_instance


def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def get_file_extension(filename):
    """Get file extension in lowercase"""
    return filename.rsplit('.', 1)[1].lower() if '.' in filename else ''


def process_image(image_path):
    """Process a single image with OCR (PaddleOCR 3.x API)"""
    ocr = get_ocr()
    try:
        # Use new predict() API for PaddleOCR 3.x
        result = ocr.predict(image_path)
        if result is None or len(result) == 0:
            return []
        
        # Extract text from OCR result
        # PaddleOCR 3.x returns result in different format
        texts = []
        for item in result:
            if item is None:
                continue
            # Handle new result format
            if hasattr(item, 'rec_texts'):
                # Direct access to recognized texts
                texts.extend(item.rec_texts)
            elif isinstance(item, dict):
                # Dictionary format with 'rec_text' key
                if 'rec_text' in item:
                    texts.append(item['rec_text'])
                elif 'rec_texts' in item:
                    texts.extend(item['rec_texts'])
            elif isinstance(item, list):
                # Legacy format: list of [bbox, (text, score)]
                for line in item:
                    if line and len(line) >= 2:
                        if isinstance(line[1], tuple):
                            texts.append(line[1][0])
                        elif isinstance(line[1], str):
                            texts.append(line[1])
        return texts
    except Exception as e:
        logger.error(f"Error processing image: {str(e)}")
        raise


def process_pdf(pdf_path):
    """Process PDF file - convert to images and OCR each page using PyMuPDF"""
    pdf_document = None
    try:
        import fitz  # PyMuPDF
        
        # Open PDF
        logger.info(f"Converting PDF to images: {pdf_path}")
        pdf_document = fitz.open(pdf_path)
        
        all_texts = []
        total_pages = len(pdf_document)
        
        for i in range(total_pages):
            logger.info(f"Processing page {i + 1}/{total_pages}")
            
            # Get page and convert to image
            page = pdf_document[i]
            # Use higher resolution for better OCR accuracy
            mat = fitz.Matrix(2.0, 2.0)  # 2x zoom = ~144 DPI
            pix = page.get_pixmap(matrix=mat)
            
            # Save image temporarily
            temp_image_path = os.path.join(UPLOAD_FOLDER, f"temp_page_{uuid.uuid4().hex}.png")
            pix.save(temp_image_path)
            
            try:
                # OCR the page
                page_texts = process_image(temp_image_path)
                if page_texts:
                    all_texts.append(f"--- 第 {i + 1} 页 ---")
                    all_texts.extend(page_texts)
            finally:
                # Clean up temp file
                if os.path.exists(temp_image_path):
                    os.remove(temp_image_path)
        
        return all_texts
    except ImportError:
        raise Exception("PDF processing requires PyMuPDF. Please run: pip install pymupdf")
    except Exception as e:
        logger.error(f"Error processing PDF: {str(e)}")
        raise
    finally:
        # Always close the PDF document to release the file lock
        if pdf_document is not None:
            pdf_document.close()


# ==================== 第三方 OCR API 处理 ====================

def process_ocrspace(file_path):
    """
    使用 OCR.space API 处理图片/PDF
    
    参数:
        file_path: 文件路径
    返回:
        识别文本列表
    """
    try:
        api_key = OCRSPACE_CONFIG['api_key']
        endpoint = OCRSPACE_CONFIG['endpoint']
        
        # 读取文件
        with open(file_path, 'rb') as f:
            file_data = f.read()
        
        # 获取文件扩展名
        ext = get_file_extension(file_path)
        filename = os.path.basename(file_path)
        
        # 准备请求
        payload = {
            'apikey': api_key,
            'language': OCRSPACE_CONFIG['language'],
            'OCREngine': OCRSPACE_CONFIG['engine'],
            'isOverlayRequired': 'false',
        }
        
        files = {
            'file': (filename, file_data)
        }
        
        logger.info(f"Calling OCR.space API for: {filename}")
        
        # 发送请求
        response = requests.post(
            endpoint,
            files=files,
            data=payload,
            timeout=60
        )
        response.raise_for_status()
        
        result = response.json()
        
        # 检查错误
        if result.get('IsErroredOnProcessing'):
            error_msg = result.get('ErrorMessage', ['Unknown error'])
            raise Exception(f"OCR.space API error: {error_msg}")
        
        # 提取文本
        texts = []
        parsed_results = result.get('ParsedResults', [])
        
        for i, page_result in enumerate(parsed_results):
            if page_result.get('FileParseExitCode') == 1:
                parsed_text = page_result.get('ParsedText', '')
                if parsed_text:
                    # 按行分割
                    lines = [line.strip() for line in parsed_text.split('\n') if line.strip()]
                    if len(parsed_results) > 1:
                        texts.append(f"--- 第 {i + 1} 页 ---")
                    texts.extend(lines)
            else:
                error_msg = page_result.get('ErrorMessage', 'Unknown error')
                logger.warning(f"Page {i + 1} OCR failed: {error_msg}")
        
        logger.info(f"OCR.space extracted {len(texts)} lines")
        return texts
        
    except requests.exceptions.Timeout:
        raise Exception("OCR.space API 请求超时，请稍后重试")
    except requests.exceptions.RequestException as e:
        raise Exception(f"OCR.space API 网络错误: {str(e)}")
    except Exception as e:
        logger.error(f"OCR.space error: {str(e)}")
        raise


def extract_invoice_amount(texts):
    """
    从识别结果中提取发票金额 (价税合计)
    支持多种格式:
    1. (小写)￥xxx.xx 或 (小写）￥xxx.xx
    2. 小写 xxx.xx (同一行)
    3. 小写 后下一行是金额
    4. 独立的大金额行 (>10000，备用)
    
    注意: 多个"小写"匹配时优先选择位置最靠后的 (通常是价税合计)
    返回: 金额字符串，未找到返回 "0"
    """
    xiaoxie_candidates = []  # 小写相关的匹配 (行号, 金额值, 金额字符串)
    other_candidates = []    # 其他匹配 (备用)
    
    for i, text in enumerate(texts):
        # 模式1: (小写)￥xxx.xx 或 (小写）￥xxx.xx
        match = re.search(r'[（\(]小写[）\)]\s*[￥¥]?\s*([\d,]+\.?\d*)', text)
        if match:
            amount = match.group(1).replace(',', '')
            try:
                if float(amount) >= 100:
                    xiaoxie_candidates.append((i, float(amount), amount))
            except ValueError:
                pass
        
        # 模式2: 小写 xxx.xx (同一行，不带括号)
        match = re.search(r'小写\s+(\d[\d,]*\.?\d*)', text)
        if match:
            amount = match.group(1).replace(',', '')
            try:
                if float(amount) >= 100:
                    xiaoxie_candidates.append((i, float(amount), amount))
            except ValueError:
                pass
        
        # 模式3: 如果当前行是"小写"，检查下一行是否是金额
        if text.strip() in ['小写', '(小写)', '（小写）']:
            if i + 1 < len(texts):
                next_line = texts[i + 1].strip()
                # 下一行是纯金额数字
                match = re.match(r'^(\d[\d,]*\.\d{2})$', next_line)
                if match:
                    amount = match.group(1).replace(',', '')
                    try:
                        if float(amount) >= 100:
                            xiaoxie_candidates.append((i, float(amount), amount))
                    except ValueError:
                        pass
        
        # 模式4: 独立的大金额行 (通常 > 10000) - 备用
        match = re.match(r'^(\d{5,}\.?\d*)$', text.strip())
        if match:
            amount = match.group(1)
            try:
                if float(amount) >= 10000:
                    other_candidates.append((i, float(amount), amount))
            except ValueError:
                pass
    
    # 优先选择"小写"相关匹配中位置最靠后的
    if xiaoxie_candidates:
        xiaoxie_candidates.sort(key=lambda x: -x[0])  # 按行号降序
        return xiaoxie_candidates[0][2]
    
    # 如果没有小写匹配，选择其他匹配中位置最靠后的
    if other_candidates:
        other_candidates.sort(key=lambda x: -x[0])
        return other_candidates[0][2]
    
    return "0"


def save_result(texts, filename):
    """Save OCR result to a text file"""
    result_filename = f"{os.path.splitext(filename)[0]}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    result_path = os.path.join(RESULT_FOLDER, result_filename)
    
    with open(result_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(texts))
    
    return result_filename


@app.route('/')
def index():
    """Render main page"""
    return render_template('index.html')


@app.route('/api-demo')
def api_demo():
    """API 调用示例页面"""
    return render_template('api_demo.html')


@app.route('/upload', methods=['POST'])
def upload_file():
    """Handle file upload and OCR processing"""
    try:
        # Check if file was uploaded
        if 'file' not in request.files:
            return jsonify({
                'success': False,
                'error': '没有选择文件'
            }), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({
                'success': False,
                'error': '没有选择文件'
            }), 400
        
        if not allowed_file(file.filename):
            return jsonify({
                'success': False,
                'error': f'不支持的文件格式。支持的格式: {", ".join(ALLOWED_EXTENSIONS)}'
            }), 400
        
        # Secure the filename and save
        original_filename = secure_filename(file.filename)
        unique_filename = f"{uuid.uuid4().hex}_{original_filename}"
        file_path = os.path.join(UPLOAD_FOLDER, unique_filename)
        file.save(file_path)
        
        logger.info(f"File uploaded: {original_filename}")
        
        try:
            # 获取 OCR 服务选择 (默认使用本地)
            ocr_service = request.form.get('ocr_service', 'local')
            extension = get_file_extension(original_filename)
            
            logger.info(f"Using OCR service: {ocr_service}")
            
            # 根据选择的服务进行处理
            if ocr_service == 'ocrspace':
                # 使用 OCR.space API
                texts = process_ocrspace(file_path)
            else:
                # 使用本地 PaddleOCR
                if extension == 'pdf':
                    texts = process_pdf(file_path)
                else:
                    texts = process_image(file_path)
            
            if not texts:
                return jsonify({
                    'success': True,
                    'text': '',
                    'message': '未能识别出任何文字内容',
                    'download_file': None
                })
            
            # Save result to file
            result_filename = save_result(texts, original_filename)
            
            # 提取发票金额
            invoice_amount = extract_invoice_amount(texts)
            
            return jsonify({
                'success': True,
                'text': '\n'.join(texts),
                'message': f'成功识别 {len(texts)} 行文字',
                'download_file': result_filename,
                'invoice_amount': invoice_amount  # 发票金额
            })
            
        finally:
            # Clean up uploaded file
            if os.path.exists(file_path):
                os.remove(file_path)
                
    except Exception as e:
        logger.error(f"Error during OCR processing: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'识别过程出错: {str(e)}'
        }), 500


@app.route('/download/<filename>')
def download_file(filename):
    """Download OCR result file"""
    try:
        file_path = os.path.join(RESULT_FOLDER, secure_filename(filename))
        if not os.path.exists(file_path):
            return jsonify({
                'success': False,
                'error': '文件不存在'
            }), 404
        
        return send_file(
            file_path,
            as_attachment=True,
            download_name=filename,
            mimetype='text/plain'
        )
    except Exception as e:
        logger.error(f"Error downloading file: {str(e)}")
        return jsonify({
            'success': False,
            'error': '下载失败'
        }), 500


# ==================== API 接口 ====================

@app.route('/api/ocr', methods=['POST'])
def api_ocr():
    """
    API 接口：OCR 文字识别
    
    请求方式: POST
    Content-Type: multipart/form-data
    
    参数:
        file: 文件 (必需) - 支持 JPG, PNG, JPEG, PDF
        ocr_service: OCR 服务 (可选, 默认 1)
            - 1: 本地识别 (PaddleOCR)
            - 2: OCR.space (在线)
        save_result: 是否保存结果文件 (可选, 默认 false)
    
    返回 JSON:
    {
        "success": true/false,
        "data": {
            "text": "识别的完整文本",
            "lines": ["第1行", "第2行", ...],
            "line_count": 行数,
            "invoice_amount": "发票金额 (如有)",
            "ocr_service": "使用的 OCR 服务",
            "download_file": "结果文件名 (如果 save_result=true)"
        },
        "error": "错误信息 (如果失败)"
    }
    
    示例调用 (curl):
    curl -X POST -F "file=@invoice.pdf" -F "ocr_service=1" http://localhost:5000/api/ocr
    
    示例调用 (Python requests):
    import requests
    response = requests.post('http://localhost:5000/api/ocr', 
                             files={'file': open('invoice.pdf', 'rb')},
                             data={'ocr_service': '2'})  # 使用 OCR.space
    result = response.json()
    """
    try:
        # 检查文件
        if 'file' not in request.files:
            return jsonify({
                'success': False,
                'error': '缺少 file 参数'
            }), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({
                'success': False,
                'error': '未选择文件'
            }), 400
        
        if not allowed_file(file.filename):
            return jsonify({
                'success': False,
                'error': f'不支持的文件格式。支持: {", ".join(ALLOWED_EXTENSIONS)}'
            }), 400
        
        # 获取 OCR 服务选择 (1=本地, 2=OCR.space)
        ocr_service_param = request.form.get('ocr_service', '1')
        if ocr_service_param == '2':
            ocr_service = 'ocrspace'
            ocr_service_name = 'OCR.space'
        else:
            ocr_service = 'local'
            ocr_service_name = '本地 PaddleOCR'
        
        # 是否保存结果
        save_result_file = request.form.get('save_result', 'false').lower() == 'true'
        
        # 保存文件
        original_filename = secure_filename(file.filename)
        unique_filename = f"{uuid.uuid4().hex}_{original_filename}"
        file_path = os.path.join(UPLOAD_FOLDER, unique_filename)
        file.save(file_path)
        
        logger.info(f"API OCR request: {original_filename}, service: {ocr_service_name}")
        
        try:
            # 根据选择的服务进行处理
            extension = get_file_extension(original_filename)
            
            if ocr_service == 'ocrspace':
                # 使用 OCR.space API
                texts = process_ocrspace(file_path)
            else:
                # 使用本地 PaddleOCR
                if extension == 'pdf':
                    texts = process_pdf(file_path)
                else:
                    texts = process_image(file_path)
            
            # 提取发票金额
            invoice_amount = extract_invoice_amount(texts) if texts else "0"
            
            # 构建响应数据
            response_data = {
                'text': '\n'.join(texts) if texts else '',
                'lines': texts if texts else [],
                'line_count': len(texts) if texts else 0,
                'invoice_amount': invoice_amount,
                'ocr_service': ocr_service_name
            }
            
            # 可选保存结果文件
            if save_result_file and texts:
                result_filename = save_result(texts, original_filename)
                response_data['download_file'] = result_filename
            
            return jsonify({
                'success': True,
                'data': response_data
            })
            
        finally:
            # 清理临时文件
            if os.path.exists(file_path):
                os.remove(file_path)
                
    except Exception as e:
        logger.error(f"API OCR error: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.errorhandler(413)
def too_large(e):
    """Handle file too large error"""
    return jsonify({
        'success': False,
        'error': '文件过大，最大支持 16MB'
    }), 413


@app.errorhandler(500)
def server_error(e):
    """Handle server error"""
    return jsonify({
        'success': False,
        'error': '服务器内部错误，请稍后重试'
    }), 500


if __name__ == '__main__':
    logger.info("Starting OCR Web Application...")
    logger.info("Access the application at: http://localhost:5000")
    # Run with host='0.0.0.0' for network access
    app.run(host='0.0.0.0', port=5000, debug=True)
