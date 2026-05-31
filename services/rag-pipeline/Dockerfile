FROM python:3.11-slim
WORKDIR /app
# Install build deps for faiss-cpu
RUN apt-get update && apt-get install -y gcc g++ && rm -rf /var/lib/apt/lists/*
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
# Pre-download embedding model at build time
RUN python -c "from embeddings import get_embedder; get_embedder()"
EXPOSE 8001
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8001"]
