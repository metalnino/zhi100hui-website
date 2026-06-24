# -*- coding: utf-8 -*-
import os, sys, paramiko

pwd = os.environ.get("DEPLOY_SSH_PASSWORD")
if not pwd:
    sys.exit("need DEPLOY_SSH_PASSWORD")

c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect("120.27.118.87", username="root", password=pwd, timeout=30, allow_agent=False, look_for_keys=False)

cmd = r"""
wc -l /etc/nginx/conf.d/default.conf.bak.20260624
grep -n 'server_name.*zhi100hui\|server_name.*www\.zhi100hui' /etc/nginx/conf.d/default.conf.bak.20260624
echo '--- lines 165-220 ---'
sed -n '165,220p' /etc/nginx/conf.d/default.conf.bak.20260624
echo '--- lines 390-450 ---'
sed -n '390,450p' /etc/nginx/conf.d/default.conf.bak.20260624
"""
_, o, _ = c.exec_command(cmd, get_pty=True)
print(o.read().decode("utf-8", errors="replace"))
c.close()
