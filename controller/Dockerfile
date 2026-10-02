FROM python:3.11-slim

# docker CLI: after rendering nginx.conf the controller runs
# `docker exec perch-proxy nginx -s reload` over the mounted socket.
RUN apt-get update && apt-get install -y --no-install-recommends docker.io \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY controller/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY controller/ .
COPY proxy/nginx.conf.j2 /app/nginx.conf.j2

CMD ["python", "-u", "main.py"]
