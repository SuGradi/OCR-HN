/**
 * OCR Web Application - Main JavaScript
 * Handles file upload, OCR processing, and result display
 */

document.addEventListener('DOMContentLoaded', function () {
    // DOM Elements
    const uploadArea = document.getElementById('uploadArea');
    const fileInput = document.getElementById('fileInput');
    const fileInfo = document.getElementById('fileInfo');
    const fileName = document.getElementById('fileName');
    const fileSize = document.getElementById('fileSize');
    const removeFile = document.getElementById('removeFile');
    const uploadBtn = document.getElementById('uploadBtn');
    const progressContainer = document.getElementById('progressContainer');
    const progressFill = document.getElementById('progressFill');
    const progressText = document.getElementById('progressText');
    const resultSection = document.getElementById('resultSection');
    const resultStats = document.getElementById('resultStats');
    const resultText = document.getElementById('resultText');
    const copyBtn = document.getElementById('copyBtn');
    const downloadBtn = document.getElementById('downloadBtn');
    const errorMessage = document.getElementById('errorMessage');
    const errorText = document.getElementById('errorText');
    const toast = document.getElementById('toast');
    const toastText = document.getElementById('toastText');

    // State
    let selectedFile = null;
    let downloadFileName = null;

    // Allowed file types
    const allowedTypes = ['image/jpeg', 'image/png', 'image/jpg', 'application/pdf'];
    const allowedExtensions = ['jpg', 'jpeg', 'png', 'pdf'];

    // Utility Functions
    function formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }

    function getFileExtension(filename) {
        return filename.split('.').pop().toLowerCase();
    }

    function isValidFile(file) {
        const ext = getFileExtension(file.name);
        return allowedExtensions.includes(ext) || allowedTypes.includes(file.type);
    }

    function showError(message) {
        errorText.textContent = message;
        errorMessage.style.display = 'flex';
        setTimeout(() => {
            errorMessage.style.display = 'none';
        }, 5000);
    }

    function hideError() {
        errorMessage.style.display = 'none';
    }

    function showToast(message) {
        toastText.textContent = message;
        toast.classList.add('show');
        setTimeout(() => {
            toast.classList.remove('show');
        }, 3000);
    }

    function resetUI() {
        selectedFile = null;
        downloadFileName = null;
        fileInput.value = '';
        fileInfo.style.display = 'none';
        uploadBtn.disabled = true;
        progressContainer.style.display = 'none';
        progressFill.style.width = '0%';
        resultSection.style.display = 'none';
        uploadArea.style.display = 'block';
        hideError();
    }

    function setFileInfo(file) {
        selectedFile = file;
        fileName.textContent = file.name;
        fileSize.textContent = formatFileSize(file.size);
        fileInfo.style.display = 'flex';
        uploadBtn.disabled = false;
        hideError();
    }

    // Drag and Drop
    uploadArea.addEventListener('click', () => fileInput.click());

    uploadArea.addEventListener('dragover', (e) => {
        e.preventDefault();
        uploadArea.classList.add('dragover');
    });

    uploadArea.addEventListener('dragleave', (e) => {
        e.preventDefault();
        uploadArea.classList.remove('dragover');
    });

    uploadArea.addEventListener('drop', (e) => {
        e.preventDefault();
        uploadArea.classList.remove('dragover');

        const files = e.dataTransfer.files;
        if (files.length > 0) {
            handleFileSelect(files[0]);
        }
    });

    // File Input Change
    fileInput.addEventListener('change', (e) => {
        if (e.target.files.length > 0) {
            handleFileSelect(e.target.files[0]);
        }
    });

    function handleFileSelect(file) {
        // Validate file
        if (!isValidFile(file)) {
            showError('不支持的文件格式。请上传 JPG、PNG 或 PDF 文件。');
            return;
        }

        // Check file size (16MB max)
        if (file.size > 16 * 1024 * 1024) {
            showError('文件过大。最大支持 16MB。');
            return;
        }

        setFileInfo(file);
    }

    // Remove File
    removeFile.addEventListener('click', (e) => {
        e.stopPropagation();
        resetUI();
    });

    // Upload and OCR
    uploadBtn.addEventListener('click', async () => {
        if (!selectedFile) return;

        // Disable button and show progress
        uploadBtn.disabled = true;
        uploadArea.style.display = 'none';
        progressContainer.style.display = 'block';
        resultSection.style.display = 'none';
        hideError();

        // Simulate initial progress
        let progress = 0;
        const progressInterval = setInterval(() => {
            progress += Math.random() * 10;
            if (progress > 90) progress = 90;
            progressFill.style.width = progress + '%';
        }, 500);

        // Create form data
        const formData = new FormData();
        formData.append('file', selectedFile);

        // 添加 OCR 服务选择
        const ocrService = document.getElementById('ocrService').value;
        formData.append('ocr_service', ocrService);

        try {
            const serviceName = ocrService === 'ocrspace' ? 'OCR.space' : '本地 PaddleOCR';
            progressText.textContent = `正在使用 ${serviceName} 识别...`;

            const response = await fetch('/upload', {
                method: 'POST',
                body: formData
            });

            clearInterval(progressInterval);
            progressFill.style.width = '100%';
            progressText.textContent = '识别完成！';

            const data = await response.json();

            if (data.success) {
                // Show result
                setTimeout(() => {
                    progressContainer.style.display = 'none';
                    resultSection.style.display = 'block';
                    resultText.value = data.text || '';
                    resultStats.textContent = data.message || '';
                    downloadFileName = data.download_file;

                    // 显示发票金额
                    const invoiceAmountCard = document.getElementById('invoiceAmountCard');
                    const invoiceAmount = document.getElementById('invoiceAmount');
                    if (data.invoice_amount && data.invoice_amount !== '0') {
                        invoiceAmount.textContent = '￥' + data.invoice_amount;
                        invoiceAmountCard.style.display = 'flex';
                    } else {
                        invoiceAmount.textContent = '￥0';
                        invoiceAmountCard.style.display = 'none';
                    }

                    // Enable/disable download button
                    downloadBtn.disabled = !downloadFileName;

                    // Reset file info for new upload
                    fileInfo.style.display = 'none';
                    uploadArea.style.display = 'block';
                    selectedFile = null;
                    fileInput.value = '';
                    uploadBtn.disabled = true;
                }, 500);
            } else {
                throw new Error(data.error || '识别失败');
            }
        } catch (error) {
            clearInterval(progressInterval);
            progressContainer.style.display = 'none';
            uploadArea.style.display = 'block';
            fileInfo.style.display = 'flex';
            uploadBtn.disabled = false;
            showError(error.message || '识别过程中发生错误，请重试');
        }
    });

    // Copy Text
    copyBtn.addEventListener('click', async () => {
        const text = resultText.value;
        if (!text) {
            showToast('没有可复制的内容');
            return;
        }

        try {
            await navigator.clipboard.writeText(text);
            showToast('已复制到剪贴板');
        } catch (err) {
            // Fallback for older browsers
            resultText.select();
            document.execCommand('copy');
            showToast('已复制到剪贴板');
        }
    });

    // Download Result
    downloadBtn.addEventListener('click', () => {
        if (!downloadFileName) {
            showToast('没有可下载的文件');
            return;
        }

        window.location.href = '/download/' + encodeURIComponent(downloadFileName);
    });

    // Keyboard shortcuts
    document.addEventListener('keydown', (e) => {
        // Ctrl+V to paste (if relevant)
        // Ctrl+C to copy result
        if (e.ctrlKey && e.key === 'c' && resultSection.style.display !== 'none') {
            // Let the default copy behavior work on selected text
        }
    });
});
