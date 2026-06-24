# -*- coding: utf-8 -*-
import os
import paramiko

HOST = "120.27.118.87"
password = os.environ.get("DEPLOY_SSH_PASSWORD")
if not password:
    raise SystemExit("need DEPLOY_SSH_PASSWORD")

c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect(HOST, username="root", password=password, timeout=30, allow_agent=False, look_for_keys=False)

fix = """
WEB=/var/www/zhi100hui
ls -la $WEB/ | head -15
test -f $WEB/index.html && echo INDEX_OK || echo INDEX_MISSING
test -f $WEB/guanyu/index.html && echo GUANYU_OK || echo GUANYU_MISSING
if id nginx >/dev/null 2>&1; then
  chown -R root:nginx $WEB
else
  echo NO_NGINX_USER using root:root
  chown -R root:root $WEB
fi
find $WEB -type d -exec chmod 755 {} \\;
find $WEB -type f -exec chmod 644 {} \\;
echo DONE_PERMS
ls -la $WEB/guanyu/ $WEB/css/ $WEB/assets/fonts/ | head -20
"""
_, stdout, stderr = c.exec_command(fix, get_pty=True)
print(stdout.read().decode("utf-8", errors="replace"))
err = stderr.read().decode("utf-8", errors="replace")
if err.strip():
    print(err)
c.close()
