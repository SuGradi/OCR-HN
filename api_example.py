"""
OCR API 调用示例
================

演示如何通过 API 调用 OCR 服务进行文字识别
支持选择本地 PaddleOCR 或 OCR.space 在线服务
"""
import requests
import json
import sys
import os


# API 服务地址
API_URL = "http://localhost:5000/api/ocr"

# OCR 服务类型
OCR_SERVICE_LOCAL = '1'      # 本地 PaddleOCR
OCR_SERVICE_OCRSPACE = '2'   # OCR.space 在线


def ocr_file(file_path: str, ocr_service: str = OCR_SERVICE_LOCAL, save_result: bool = False) -> dict:
    """
    调用 OCR API 识别文件中的文字
    
    参数:
        file_path: 文件路径 (支持 JPG, PNG, JPEG, PDF)
        ocr_service: OCR 服务类型
            - '1': 本地识别 (PaddleOCR)
            - '2': OCR.space (在线)
        save_result: 是否在服务器保存结果文件
    
    返回:
        识别结果字典
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"文件不存在: {file_path}")
    
    with open(file_path, 'rb') as f:
        files = {'file': f}
        data = {
            'ocr_service': ocr_service,
            'save_result': 'true' if save_result else 'false'
        }
        
        response = requests.post(API_URL, files=files, data=data)
        response.raise_for_status()
        
        return response.json()


def main():
    """主函数 - 演示 API 调用"""
    
    # 检查命令行参数
    if len(sys.argv) < 2:
        print("用法: python api_example.py <文件路径> [服务类型]")
        print("")
        print("服务类型:")
        print("  1 - 本地识别 (PaddleOCR) [默认]")
        print("  2 - OCR.space (在线)")
        print("")
        print("示例:")
        print("  python api_example.py invoice.pdf      # 使用本地识别")
        print("  python api_example.py invoice.pdf 2    # 使用 OCR.space")
        sys.exit(1)
    
    file_path = sys.argv[1]
    ocr_service = sys.argv[2] if len(sys.argv) > 2 else OCR_SERVICE_LOCAL
    
    service_name = "OCR.space" if ocr_service == '2' else "本地 PaddleOCR"
    print(f"正在识别文件: {file_path}")
    print(f"使用服务: {service_name}")
    print("-" * 50)
    
    try:
        result = ocr_file(file_path, ocr_service=ocr_service, save_result=False)
        
        if result.get('success'):
            data = result['data']
            
            # 显示使用的服务
            print(f"🔧 OCR 服务: {data.get('ocr_service', service_name)}")
            
            # 显示发票金额 (如果有)
            amount = data.get('invoice_amount', '0')
            if amount != '0':
                print(f"💰 发票金额: ￥{amount}")
            
            # 显示识别统计
            print(f"✅ 识别成功！共 {data['line_count']} 行")
            print("-" * 50)
            
            # 显示识别内容
            print("识别内容:")
            print(data['text'])
            
            # 返回数据供进一步处理
            return data
            
        else:
            print(f"❌ 识别失败: {result.get('error')}")
            return None
            
    except requests.exceptions.ConnectionError:
        print("❌ 连接失败！请确保 OCR 服务正在运行")
        print("   启动命令: python app.py")
        return None
    except Exception as e:
        print(f"❌ 错误: {e}")
        return None


# ============ 更多使用示例 ============

def example_local_ocr():
    """使用本地 PaddleOCR 识别"""
    result = ocr_file("invoice.pdf", ocr_service=OCR_SERVICE_LOCAL)
    print(result['data']['text'])


def example_ocrspace():
    """使用 OCR.space 在线识别"""
    result = ocr_file("invoice.pdf", ocr_service=OCR_SERVICE_OCRSPACE)
    print(result['data']['text'])


def example_get_amount():
    """获取发票金额示例"""
    result = ocr_file("invoice.pdf")
    amount = result['data']['invoice_amount']
    print(f"金额: {amount}")


def example_get_lines():
    """逐行获取内容示例"""
    result = ocr_file("invoice.pdf")
    for i, line in enumerate(result['data']['lines'], 1):
        print(f"{i}: {line}")


def example_batch_process():
    """批量处理示例 - 对比两种服务"""
    import glob
    
    pdf_files = glob.glob("*.pdf")
    for pdf in pdf_files:
        # 使用本地识别
        result1 = ocr_file(pdf, ocr_service=OCR_SERVICE_LOCAL)
        # 使用 OCR.space
        result2 = ocr_file(pdf, ocr_service=OCR_SERVICE_OCRSPACE)
        
        if result1.get('success') and result2.get('success'):
            amount1 = result1['data']['invoice_amount']
            amount2 = result2['data']['invoice_amount']
            print(f"{pdf}: 本地=￥{amount1}, OCR.space=￥{amount2}")


if __name__ == "__main__":
    main()
