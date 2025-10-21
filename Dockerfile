FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app_enhanced.py .
COPY templates/ templates/

EXPOSE 5000

CMD ["python", "app_enhanced.py"]
