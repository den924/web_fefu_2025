FROM nginx:alpine

RUN rm -rf /etc/nginx/conf.d/*

COPY nginx.conf /etc/nginx/conf.d/default.conf
# Health check

HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \

    CMD wget --no-verbose --tries=1 --spider http://localhost/ || exit 1
