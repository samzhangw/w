# 使用官方的 Python 基礎鏡像
FROM python:3.8-slim

# 設定工作目錄
WORKDIR /app

# 複製當前目錄的內容到工作目錄
COPY . .

# 安裝 Python 依賴
RUN pip install --no-cache-dir -r requirements.txt

# 暴露應用程式的運行端口
EXPOSE 5000

# 設定環境變數
ENV PORT=5000

# 啟動應用程式
CMD ["python", "apps.py"]
