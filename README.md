# 智能 OCR 文字识别工具

基于 Python 的在线图片与 PDF 文字识别网页应用，支持本地 PaddleOCR 和 OCR.space 在线 API。

![OCR](https://img.shields.io/badge/OCR-PaddleOCR-blue)
![OCR.space](https://img.shields.io/badge/OCR-OCR.space-green)
![Python](https://img.shields.io/badge/Python-3.9--3.13-orange)
![Flask](https://img.shields.io/badge/Flask-3.x-red)

## ✨ 功能特点

| 功能 | 说明 |
|------|------|
| 🖼️ 图片识别 | 支持 JPG、PNG、JPEG 格式 |
| 📄 PDF 识别 | 自动逐页识别，合并结果 |
| 💰 发票金额提取 | 自动识别并提取发票金额 |
| � 多引擎支持 | 本地 PaddleOCR + OCR.space 在线 |
| 🔌 API 接口 | 支持程序调用，可选 OCR 引擎 |
| �📋 复制粘贴 | 一键复制识别结果 |
| 💾 导出 TXT | 下载识别结果文件 |
| 🎨 现代界面 | 深色主题响应式设计 |

---

## 🚀 快速开始

### 环境要求

> ⚠️ **重要**: PaddlePaddle 目前支持 **Python 3.9 - 3.13**

- Python 3.9 - 3.13 (推荐 3.11)
- pip >= 20.2.2
- 约 500MB 磁盘空间 (模型文件)

### 安装步骤

```powershell
# 1. 创建虚拟环境 (Windows)
py -3.11 -m venv venv
.\venv\Scripts\Activate.ps1

# 2. 安装依赖
pip install -r requirements.txt

# 3. 启动应用
python app.py
```

访问地址: **http://localhost:5000**

---

## 📁 项目结构

```
OCR/
├── app.py              # Flask 主应用
├── config.py           # 配置文件 (API Key 等)
├── api_example.py      # API 调用示例脚本
├── requirements.txt    # Python 依赖
├── README.md           # 说明文档
├── templates/
│   ├── index.html      # 主页面
│   └── api_demo.html   # API 示例页面
├── static/
│   ├── css/style.css   # 样式文件
│   └── js/main.js      # 前端脚本
├── uploads/            # 临时上传目录 (自动创建)
└── results/            # 识别结果目录 (自动创建)
```

---

## 💻 使用方法

### 网页界面

| 页面 | 地址 | 说明 |
|------|------|------|
| 主页面 | http://localhost:5000 | 上传文件识别 |
| API 示例 | http://localhost:5000/api-demo | API 调用演示 |

1. 打开浏览器访问主页面
2. 选择 OCR 服务 (本地 / OCR.space)
3. 拖拽或点击选择图片/PDF 文件
4. 点击「开始识别」
5. 查看识别结果和发票金额

---

## 🔌 API 接口

### 接口列表

| 端点 | 方法 | 说明 |
|------|------|------|
| `/` | GET | 主页面 |
| `/api-demo` | GET | API 示例页面 |
| `/api/ocr` | POST | **OCR 识别接口** |
| `/upload` | POST | 网页上传识别 |
| `/download/<filename>` | GET | 下载结果文件 |

### `/api/ocr` 接口详情

**请求参数:**

| 参数 | 类型 | 必需 | 说明 |
|------|------|------|------|
| `file` | File | ✅ | 图片或 PDF 文件 |
| `ocr_service` | String | ❌ | `1`=本地 PaddleOCR (默认), `2`=OCR.space |
| `save_result` | String | ❌ | `true`/`false`, 是否保存结果 |

**响应格式:**

```json
{
    "success": true,
    "data": {
        "text": "完整识别文本",
        "lines": ["第1行", "第2行"],
        "line_count": 50,
        "invoice_amount": "186781.00",
        "ocr_service": "本地 PaddleOCR",
        "download_file": "result.txt"
    }
}
```

### 调用示例

**cURL:**
```bash
# 使用本地 PaddleOCR
curl -X POST -F "file=@invoice.pdf" -F "ocr_service=1" http://localhost:5000/api/ocr

# 使用 OCR.space
curl -X POST -F "file=@invoice.pdf" -F "ocr_service=2" http://localhost:5000/api/ocr
```

**Python:**
```python
import requests

response = requests.post(
    'http://localhost:5000/api/ocr',
    files={'file': open('invoice.pdf', 'rb')},
    data={'ocr_service': '2'}  # 使用 OCR.space
)
result = response.json()

print(result['data']['text'])           # 完整文本
print(result['data']['invoice_amount']) # 发票金额
```

**命令行示例脚本:**
```bash
python api_example.py invoice.pdf      # 本地识别
python api_example.py invoice.pdf 2    # OCR.space
```

---

## 🔧 OCR 服务配置

### 本地 PaddleOCR

编辑 `config.py`:

```python
OCR_CONFIG = {
    'lang': 'ch',           # 语言: ch=中英文
    'device': 'cpu',        # 设备: cpu/gpu
    'text_detection_model_name': 'PP-OCRv4_mobile_det',
    'text_recognition_model_name': 'PP-OCRv4_mobile_rec',
}
```

### OCR.space API

编辑 `config.py`:

```python
OCRSPACE_CONFIG = {
    'api_key': 'YOUR_API_KEY',   # 免费申请: https://ocr.space/ocrapi
    'endpoint': 'https://api.ocr.space/parse/image',
    'language': 'chs',           # chs=简体中文, eng=英文
    'engine': '2',               # 1 或 2
}
```

> 💡 免费 API Key 申请: https://ocr.space/ocrapi

---

## ⚙️ 配置说明

| 配置项 | 默认值 | 说明 |
|--------|--------|------|
| `MAX_CONTENT_LENGTH` | 16MB | 最大上传文件大小 |
| `ALLOWED_EXTENSIONS` | jpg, png, pdf | 允许的文件格式 |
| `OCRSPACE_CONFIG.api_key` | - | OCR.space API 密钥 |

---

## 🏭 生产部署

### Windows (Waitress)

```powershell
pip install waitress
waitress-serve --host=0.0.0.0 --port=5000 --threads=4 app:app
```

### Linux (Gunicorn)

```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

### Docker

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY . .
RUN pip install -r requirements.txt
EXPOSE 5000
CMD ["waitress-serve", "--host=0.0.0.0", "--port=5000", "app:app"]
```

---

## ❓ 常见问题

### Q: paddlepaddle 安装失败？
**A:** 请确保使用 Python 3.9-3.13 版本。

### Q: 首次运行很慢？
**A:** PaddleOCR 首次运行会自动下载模型约 100-300MB。

### Q: OCR.space 返回语言错误？
**A:** 检查 `config.py` 中 `OCRSPACE_CONFIG.language` 是否设置正确 (chs/eng)。

### Q: 如何支持高并发？
**A:** 使用 Waitress 或 Gunicorn 部署，设置多线程/多进程。

---

## 🛠️ 技术栈

| 组件 | 技术 |
|------|------|
| 后端框架 | Flask 3.x |
| 本地 OCR | PaddleOCR 3.x |
| 在线 OCR | OCR.space API |
| PDF 处理 | PyMuPDF |
| 前端 | HTML + CSS + JavaScript |

---

## 📝 更新日志

### v1.1.0 (2026-01-05)
- ✅ 新增 OCR.space 在线 API 支持
- ✅ 新增 OCR 服务选择下拉框
- ✅ API 接口支持 `ocr_service` 参数
- ✅ 新增 API 示例页面 `/api-demo`
- ✅ 更新 `api_example.py` 示例脚本

### v1.0.0 (2026-01-04)
- ✅ 图片和 PDF OCR 识别
- ✅ 发票金额自动提取
- ✅ API 接口支持
- ✅ 现代化深色主题界面
- ✅ 复制和下载功能

---

## 📄 许可证

MIT License
