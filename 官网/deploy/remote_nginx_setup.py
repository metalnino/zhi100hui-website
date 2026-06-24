# -*- coding: utf-8 -*-
"""远程配置 nginx：HTTP 先上线，conf 名 nginx-zhi100hui.conf"""
import os
import sys
import paramiko
from scp import SCPClient

HOST = "120.27.118.87"
USER = "root"
SRC_CONF = os.path.join(os.path.dirname(__file__), "nginx-zhi100hui.conf")
WEB_DEPLOY = "/var/www/zhi100hui/deploy/nginx-zhi100hui.conf"
NGINX_CONF = "/etc/nginx/conf.d/nginx-zhi100hui.conf"

# 尚无 SSL：先启用 HTTP 版（证书下来后换 deploy 里 HTTPS 版）
HTTP_CONF = r"""# zhi100hui.com · HTTP（SSL 申请中）
# 裸域 301 → www，路径不变；与 HTTPS 上线后逻辑一致

server {
    listen 80;
    server_name zhi100hui.com;
    return 301 http://www.zhi100hui.com$request_uri;
}

server {
    listen 80;
    server_name www.zhi100hui.com;

    root  /var/www/zhi100hui;
    index index.html;
    charset utf-8;

    gzip on;
    gzip_comp_level 5;
    gzip_min_length 1024;
    gzip_types text/plain text/css application/javascript application/json image/svg+xml;

    location / {
        try_files $uri $uri/ =404;
    }

    location ~* \.(css|js|png|jpe?g|webp|gif|svg|ico|woff2?)$ {
        expires 30d;
        add_header Cache-Control "public";
        access_log off;
    }

    add_header X-Content-Type-Options nosniff;
    add_header X-Frame-Options SAMEORIGIN;

    error_page 404 = @notfound;
    location @notfound {
        try_files /404.html =404;
    }
}
"""


def main():
    password = os.environ.get("DEPLOY_SSH_PASSWORD")
    if not password:
        print("ERROR: set DEPLOY_SSH_PASSWORD", file=sys.stderr)
        sys.exit(1)

    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(HOST, username=USER, password=password, timeout=30, allow_agent=False, look_for_keys=False)

    # 更新网站目录里的 HTTPS 模板（证书下来后用）
    if os.path.isfile(SRC_CONF):
        with SCPClient(client.get_transport()) as scp:
            scp.put(SRC_CONF, WEB_DEPLOY)
        print(f"Updated template: {WEB_DEPLOY}")

    sftp = client.open_sftp()
    with sftp.file(NGINX_CONF, "w") as f:
        f.write(HTTP_CONF)
    sftp.close()
    print(f"Wrote active config: {NGINX_CONF} (HTTP)")

    cmd = r"""
set -e
cd /etc/nginx/conf.d
# 切勿禁用 default.conf！其中含 ca.zhi100hui.com 等应用反代（见 DEPLOY.md §6.3）
rm -f zhi100hui.conf nginx-legacy.conf 2>/dev/null || true
echo '--- conf.d ---'
ls -la /etc/nginx/conf.d/
nginx -t
nginx -s reload
echo '--- curl ---'
curl -sI -H 'Host: zhi100hui.com' http://127.0.0.1/guanyu/ | head -5
curl -sI -H 'Host: www.zhi100hui.com' http://127.0.0.1/ | head -5
curl -sI -H 'Host: www.zhi100hui.com' http://127.0.0.1/guanyu/ | head -5
curl -s -o /dev/null -w 'css:%{http_code}\n' -H 'Host: www.zhi100hui.com' http://127.0.0.1/css/style.css
"""
    _, stdout, stderr = client.exec_command(cmd, get_pty=True)
    out = stdout.read().decode("utf-8", errors="replace")
    err = stderr.read().decode("utf-8", errors="replace")
    code = stdout.channel.recv_exit_status()
    print(out)
    if err.strip():
        print(err, file=sys.stderr)
    client.close()
    if code != 0:
        sys.exit(code)
    print("DONE: nginx-zhi100hui.conf active (HTTP). After SSL, switch to HTTPS template in deploy/")


if __name__ == "__main__":
    main()
