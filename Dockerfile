# 使用 Python 基礎映像
FROM python:3.11-slim

# 設置工作目錄
WORKDIR /app

# 複製當前目錄下的所有文件到容器內的工作目錄
COPY . /app

# 安裝所需的 Python 庫
RUN pip install --no-cache-dir -r requirements.txt

# 啟動 Discord 機器人
CMD ["python", "LawBot/src/Bot.py"]
