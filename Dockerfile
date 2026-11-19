FROM python:3.12-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt && useradd --uid 10001 --create-home chatbot
COPY chatbot ./chatbot
COPY web ./web
COPY run.py .
USER chatbot
EXPOSE 8000
CMD ["python", "run.py", "--host", "0.0.0.0"]
