"""
OCR API 调用示例
================

演示如何通过 API 调用 OCR 服务进行文字识别
"""
import requests
import json
import sys
import os


# API 服务地址
API_URL = "http://localhost:5000/api/ocr"


def ocr_file(file_path: str, save_result: bool = False) -> dict:
    """
    调用 OCR API 识别文件中的文字
    
    参数:
        file_path: 文件路径 (支持 JPG, PNG, JPEG, PDF)
        save_result: 是否在服务器保存结果文件
    
    返回:
        识别结果字典
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"文件不存在: {file_path}")
    
    with open(file_path, 'rb') as f:
        files = {'file': f}
        data = {'save_result': 'true' if save_result else 'false'}
        
        response = requests.post(API_URL, files=files, data=data)
        response.raise_for_status()
        
        return response.json()


def main():
    """主函数 - 演示 API 调用"""
    
    # 检查命令行参数
    if len(sys.argv) < 2:
        print("用法: python api_example.py <文件路径>")
        print("示例: python api_example.py invoice.pdf")
        print("      python api_example.py image.jpg")
        sys.exit(1)
    
    file_path = sys.argv[1]
    
    print(f"正在识别文件: {file_path}")
    print("-" * 50)
    
    try:
        result = ocr_file(file_path, save_result=False)
        
        if result.get('success'):
            data = result['data']
            
            # 显示发票金额 (如果有)
            amount = data.get('invoice_amount', '0')
            if amount != '0':
                print(f"📄 发票金额: ￥{amount}")
                print("-" * 50)
            
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

def example_basic():
    """基本调用示例"""
    result = ocr_file("invoice.pdf")
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
    """批量处理示例"""
    import glob
    
    pdf_files = glob.glob("*.pdf")
    for pdf in pdf_files:
        result = ocr_file(pdf)
        if result.get('success'):
            amount = result['data']['invoice_amount']
            print(f"{pdf}: ￥{amount}")


if __name__ == "__main__":
    main()
