FROM nginx:1.27-alpine

COPY bootstrap.conf /etc/nginx/bootstrap.conf
COPY nginx.conf.j2 /etc/nginx/nginx.conf.j2
COPY 99-bootstrap.sh /docker-entrypoint.d/99-bootstrap.sh
RUN chmod +x /docker-entrypoint.d/99-bootstrap.sh
