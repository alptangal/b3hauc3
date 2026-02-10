# Dùng image nhẹ
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy requirements trước để tận dụng cache
COPY requirements.txt .

# Cài đặt dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy toàn bộ code
COPY . .

# Expose port (Hugging Face dùng biến $PORT)
EXPOSE 7860

# Chạy bằng gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:7860", "app:app"]
