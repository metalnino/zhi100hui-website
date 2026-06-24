# -*- coding: utf-8 -*-
import os, sys, paramiko

HOST = "120.27.118.87"
pwd = os.environ.get("DEPLOY_SSH_PASSWORD")
if not pwd:
    sys.exit("need DEPLOY_SSH_PASSWORD")

c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect(HOST, username="root", password=pwd, timeout=30, allow_agent=False, look_for_keys=False)

cmd = r"""
echo '=== conf.d listing ==='
ls -la /etc/nginx/conf.d/
echo ''
echo '=== grep ca.zhi100hui in all nginx ==='
grep -rn 'ca\.zhi100hui' /etc/nginx/ 2>/dev/null || echo 'NO_MATCH'
echo ''
echo '=== grep zhi100hui in conf.d ==='
grep -rn 'zhi100hui' /etc/nginx/conf.d/ 2>/dev/null
echo ''
echo '=== default.conf.bak server_name blocks ==='
grep -n 'server_name\|listen\|proxy_pass\|root ' /etc/nginx/conf.d/default.conf.bak.20260624 2>/dev/null | head -60
echo ''
echo '=== full default.conf.bak (first 120 lines) ==='
head -120 /etc/nginx/conf.d/default.conf.bak.20260624 2>/dev/null
echo ''
echo '=== curl ca.zhi100hui.com locally ==='
curl -sI -H 'Host: ca.zhi100hui.com' http://127.0.0.1/ 2>&1 | head -10
curl -skI -H 'Host: ca.zhi100hui.com' https://127.0.0.1/ 2>&1 | head -10
echo ''
echo '=== nginx -T server_name summary ==='
nginx -T 2>/dev/null | grep -E '^\s*(listen|server_name)' | head -40
"""

_, o, e = c.exec_command(cmd, get_pty=True)
out = o.read().decode("utf-8", errors="replace")
print(out)
if e.read().strip():
    print(e.read(), file=sys.stderr)
c.close()
