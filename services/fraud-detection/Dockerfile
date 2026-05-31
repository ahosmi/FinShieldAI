FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
# Train model at build time so it's available on startup
RUN python models/train_model.py
CMD ["python", "main.py"]
