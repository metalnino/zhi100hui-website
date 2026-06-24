import os, sys, paramiko
c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect("120.27.118.87", username="root", password=os.environ["DEPLOY_SSH_PASSWORD"], timeout=30, allow_agent=False, look_for_keys=False)
_, o, _ = c.exec_command("cat /etc/nginx/conf.d/nginx-zhi100hui.conf; echo '---'; curl -sI -H 'Host: zhi100hui.com' http://127.0.0.1/guanyu/ | head -3", get_pty=True)
sys.stdout.buffer.write(o.read())
c.close()
