# -*- coding: utf-8 -*-
import os, sys, paramiko
c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect("120.27.118.87", username="root", password=os.environ["DEPLOY_SSH_PASSWORD"], timeout=30, allow_agent=False, look_for_keys=False)
cmd = r"""
grep -n 'server_name.*ca.zhi100hui' /etc/nginx/conf.d/default.conf
echo '=== SNI resolve local ==='
curl -skI --resolve ca.zhi100hui.com:443:127.0.0.1 https://ca.zhi100hui.com/ | head -10
echo '=== external ca ==='
curl -skI https://ca.zhi100hui.com/ --connect-timeout 10 | head -10
"""
_, o, _ = c.exec_command(cmd, get_pty=True)
sys.stdout.buffer.write(o.read())
c.close()
