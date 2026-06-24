# -*- coding: utf-8 -*-
import os, paramiko
c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect('120.27.118.87', username='root', password=os.environ['DEPLOY_SSH_PASSWORD'], timeout=30, allow_agent=False, look_for_keys=False)
cmd = """
echo '=== jtyjt.conf ==='
cat /etc/nginx/conf.d/jtyjt.conf 2>/dev/null
echo '=== qrcode ==='
find /etc/nginx/conf.d/qrcode -type f -exec echo '--- {} ---' \\; -exec cat {} \\; 2>/dev/null | head -80
echo '=== nginx-zhi100hui.conf ==='
cat /etc/nginx/conf.d/nginx-zhi100hui.conf
echo '=== curl with Host ==='
curl -sI -H 'Host: www.zhi100hui.com' http://127.0.0.1/ | head -8
curl -sI -H 'Host: www.zhi100hui.com' http://127.0.0.1/guanyu/ | head -8
curl -s -o /dev/null -w 'css:%{http_code}\n' -H 'Host: www.zhi100hui.com' http://127.0.0.1/css/style.css
grep -n 'include\|server {' /etc/nginx/nginx.conf | head -30
"""
_, o, _ = c.exec_command(cmd, get_pty=True)
text = o.read().decode('utf-8', errors='replace')
import sys
sys.stdout.buffer.write(text.encode('utf-8', errors='replace'))
c.close()
