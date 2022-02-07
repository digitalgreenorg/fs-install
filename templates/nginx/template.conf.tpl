server {
    listen      80;
    server_name ${PUBLIC_DOMAIN};
    server_tokens off;
    location /.well-known/acme-challenge/ {
        root /var/www/certbot;
    }

    location / {
        return 301 https://$$host$$request_uri;
    }
}

server{
    listen      443 ssl;
    server_name ${PUBLIC_DOMAIN};

    ssl_certificate_key /etc/nginx/cert/private.key;
    ssl_certificate /etc/nginx/cert/public.crt;

    location /be/ {
      proxy_buffering off;
      proxy_pass http://usm:6022/;
    }

    location /cbe/ {
      proxy_buffering off;
      proxy_pass http://fs-steward-api:8002/;
    }

    location / {
        root      /usr/share/nginx/html;
        index     index.html index.htm;
        try_files $uri /index.html;
    }

}