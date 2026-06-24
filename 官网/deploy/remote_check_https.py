# -*- coding: utf-8 -*-
import os, sys, paramiko
c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect("120.27.118.87", username="root", password=os.environ["DEPLOY_SSH_PASSWORD"], timeout=30, allow_agent=False, look_for_keys=False)
cmd = """
echo '=== nginx-zhi100hui.conf ==='
cat /etc/nginx/conf.d/nginx-zhi100hui.conf
echo '=== listen 80 ==='
grep -rn 'listen 80' /etc/nginx/conf.d/
echo '=== curl external ==='
curl -sI http://www.zhi100hui.com/ | head -8
curl -skI https://www.zhi100hui.com/ | head -8
curl -skI https://zhi100hui.com/ | head -5
"""
_, o, _ = c.exec_command(cmd, get_pty=True)
sys.stdout.buffer.write(o.read())
c.close()
