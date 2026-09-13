FROM nginx:1.27-alpine

# The live config is mounted from the shared `proxy-conf` volume that the controller writes into.
# This baked copy is only the pre-rollout default (100% stable) used before the first render.
COPY nginx.conf.j2 /etc/nginx/nginx.conf.j2
