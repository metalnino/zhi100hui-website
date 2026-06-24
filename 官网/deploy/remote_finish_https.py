# -*- coding: utf-8 -*-
import os
import sys
import paramiko

HOST = "120.27.118.87"
WEB = "/var/www/zhi100hui"
NGINX_CONF = "/etc/nginx/conf.d/nginx-zhi100hui.conf"

password = os.environ.get("DEPLOY_SSH_PASSWORD")
if not password:
    sys.exit("need DEPLOY_SSH_PASSWORD")

c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect(HOST, username="root", password=password, timeout=30, allow_agent=False, look_for_keys=False)

cmd = r"""
set -e
WEB=/var/www/zhi100hui
if id nginx >/dev/null 2>&1; then chown -R root:nginx "$WEB"; else chown -R root:root "$WEB"; fi
find "$WEB" -type d -exec chmod 755 {} \;
find "$WEB" -type f -exec chmod 644 {} \;
echo '--- index cos ---'
grep -o 'mpfamily[^"]*z100h-brand-logo[^"]*' "$WEB/index.html" | head -1 || echo NONE
echo '--- nginx test ---'
nginx -t
nginx -s reload
echo '--- HTTP 301 ---'
curl -sI http://127.0.0.1/ -H 'Host: www.zhi100hui.com' | head -6
echo '--- HTTPS home ---'
curl -skI https://127.0.0.1/ -H 'Host: www.zhi100hui.com' | head -8
echo '--- COS logo ---'
curl -s -o /dev/null -w '%{http_code}\n' 'https://mpfamily-1301068541.cos.ap-shanghai.myqcloud.com/website-z100h/z100h-brand-logo.png'
curl -s -o /dev/null -w '%{http_code}\n' 'https://mpfamily-1301068541.cos.ap-shanghai.myqcloud.com/website-z100h/z100h-hero-office.jpg'
curl -s -o /dev/null -w '%{http_code}\n' 'https://mpfamily-1301068541.cos.ap-shanghai.myqcloud.com/website-z100h/z100h-favicon.png'
"""

_, stdout, stderr = c.exec_command(cmd, get_pty=True)
out = stdout.read().decode("utf-8", errors="replace")
err = stderr.read().decode("utf-8", errors="replace")
code = stdout.channel.recv_exit_status()
print(out)
if err.strip():
    print(err, file=sys.stderr)
c.close()
sys.exit(code)
