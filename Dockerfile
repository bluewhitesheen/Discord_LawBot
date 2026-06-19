FROM python:3.11-slim

WORKDIR /app

# 先只複製 dependency file（利用 cache）
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# 再複製 source code
COPY . .

# 避免 Python buffer 問題
ENV PYTHONUNBUFFERED=1

CMD ["python", "LawBot/src/main.py"]

# docker build -t discord_bot .
# docker run -v C:\Users\adl\Desktop\Discord_LawBot:/app discord_bot