FROM python:3.9-slim

WORKDIR /app

# Install curl for healthcheck
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# 개발 환경을 위한 --reload 옵션 추가
CMD ["uvicorn", "main:app", "--reload", "--host", "0.0.0.0", "--port", "8000"]