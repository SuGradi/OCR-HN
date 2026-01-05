# 智能 OCR 文字识别工具

基于 Python 和 PaddleOCR 的在线图片与 PDF 文字识别网页应用，支持网页界面和 API 调用。

![OCR](https://img.shields.io/badge/OCR-PaddleOCR-blue)
![Python](https://img.shields.io/badge/Python-3.9--3.13-green)
![Flask](https://img.shields.io/badge/Flask-2.0+-orange)

## ✨ 功能特点

| 功能 | 说明 |
|------|------|
| 🖼️ 图片识别 | 支持 JPG、PNG、JPEG 格式 |
| 📄 PDF 识别 | 自动逐页识别，合并结果 |
| � 发票金额提取 | 自动识别并提取发票金额 |
| 📋 复制粘贴 | 一键复制识别结果 |
| 💾 导出 TXT | 下载识别结果文件 |
| 🔌 API 接口 | 支持程序调用 |
| 🎨 现代界面 | 深色主题响应式设计 |
| 🌐 多用户 | 支持并发访问 |

---

## 🚀 快速开始

### 环境要求

> ⚠️ **重要**: PaddlePaddle 目前支持 **Python 3.9 - 3.13**

- Python 3.9 - 3.13 (推荐 3.11 或 3.12)
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
├── config.py           # 配置文件
├── api_example.py      # API 调用示例
├── requirements.txt    # Python 依赖
├── README.md           # 说明文档
├── templates/
│   └── index.html      # 前端页面
├── static/
│   ├── css/
│   │   └── style.css   # 样式文件
│   └── js/
│       └── main.js     # 前端脚本
├── uploads/            # 临时上传目录 (自动创建)
└── results/            # 识别结果目录 (自动创建)
```

---

## 💻 使用方法

### 网页界面

1. 打开浏览器访问 `http://localhost:5000`
2. 拖拽或点击选择图片/PDF 文件
3. 点击「开始识别」
4. 查看识别结果和发票金额
5. 复制或下载结果

### API 接口

#### 接口列表

| 端点 | 方法 | 说明 |
|------|------|------|
| `/` | GET | 网页界面 |
| `/api/ocr` | POST | **OCR 识别接口** |
| `/upload` | POST | 网页上传识别 |
| `/download/<filename>` | GET | 下载结果文件 |

#### `/api/ocr` 接口详情

**请求参数:**

| 参数 | 类型 | 必需 | 说明 |
|------|------|------|------|
| `file` | File | ✅ | 图片或 PDF 文件 |
| `save_result` | String | ❌ | 是否保存结果 (`true`/`false`) |

**响应格式:**

```json
{
    "success": true,
    "data": {
        "text": "完整识别文本",
        "lines": ["第1行", "第2行", "..."],
        "line_count": 50,
        "invoice_amount": "186781.00",
        "download_file": "result.txt"
    }
}
```

#### 调用示例

**curl:**
```bash
curl -X POST -F "file=@invoice.pdf" http://localhost:5000/api/ocr
```

**Python:**
```python
import requests

# 识别文件
response = requests.post(
    'http://localhost:5000/api/ocr',
    files={'file': open('invoice.pdf', 'rb')}
)
result = response.json()

# 获取结果
print(result['data']['text'])           # 完整文本
print(result['data']['lines'])          # 逐行数组
print(result['data']['line_count'])     # 行数
print(result['data']['invoice_amount']) # 发票金额
```

**使用示例脚本:**
```bash
python api_example.py invoice.pdf
```

---

## ⚙️ 配置说明

编辑 `config.py` 可修改设置:

| 配置项 | 默认值 | 说明 |
|--------|--------|------|
| `MAX_CONTENT_LENGTH` | 16MB | 最大上传文件大小 |
| `ALLOWED_EXTENSIONS` | jpg, png, pdf | 允许的文件格式 |
| `OCR_CONFIG.lang` | ch | 识别语言 (ch=中英文) |

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

### Docker (可选)

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
**A:** 请确保使用 Python 3.9-3.13 版本，不支持 Python 3.14。

### Q: 首次运行很慢？
**A:** PaddleOCR 首次运行会自动下载模型约 100-300MB，请耐心等待。

### Q: 识别速度慢？
**A:** 默认使用 Mobile 轻量模型，如需更快速度可调整 `config.py` 中的模型设置。

### Q: 如何支持高并发？
**A:** 使用 Waitress 或 Gunicorn 部署，设置多线程/多进程。

---

## 🛠️ 技术栈

| 组件 | 技术 |
|------|------|
| 后端框架 | Flask |
| OCR 引擎 | PaddleOCR |
| PDF 处理 | PyMuPDF |
| 前端 | HTML + CSS + JavaScript |
| 样式 | 原生 CSS (深色主题) |

---

## 📝 更新日志

### v1.0.0 (2026-01-04)
- ✅ 图片和 PDF OCR 识别
- ✅ 发票金额自动提取
- ✅ API 接口支持
- ✅ 现代化深色主题界面
- ✅ 复制和下载功能

---

## 📄 许可证

MIT License
