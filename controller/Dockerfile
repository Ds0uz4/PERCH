FROM python:3.11-slim

# docker CLI: the controller signals `nginx -s reload` in the proxy container over the mounted
# socket after rendering a new weight config.
RUN apt-get update && apt-get install -y --no-install-recommends docker.io \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .

CMD ["python", "-u", "main.py"]
