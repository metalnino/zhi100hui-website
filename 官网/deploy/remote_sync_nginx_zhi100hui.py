# -*- coding: utf-8 -*-
"""仅同步 nginx-zhi100hui.conf 并 reload — 不碰 default.conf"""
import os
import sys

import paramiko
from scp import SCPClient

HOST = "120.27.118.87"
LOCAL_CONF = os.path.join(os.path.dirname(os.path.abspath(__file__)), "nginx-zhi100hui.conf")
REMOTE_CONF = "/etc/nginx/conf.d/nginx-zhi100hui.conf"


def main():
    password = os.environ.get("DEPLOY_SSH_PASSWORD")
    if not password:
        print("ERROR: set DEPLOY_SSH_PASSWORD", file=sys.stderr)
        sys.exit(1)

    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        paramiko.Transport._preferred_keys = (
            "ssh-ed25519", "ecdsa-sha2-nistp256", "ecdsa-sha2-nistp384",
            "ecdsa-sha2-nistp521", "ssh-rsa",
        )
    except Exception:
        pass
    client.connect(HOST, username="root", password=password, timeout=30,
                   allow_agent=False, look_for_keys=False)

    print(f"Upload {LOCAL_CONF} -> {REMOTE_CONF}")
    with SCPClient(client.get_transport()) as scp:
        scp.put(LOCAL_CONF, REMOTE_CONF)

    cmd = r"""
set -e
echo '--- default.conf untouched ---'
test -f /etc/nginx/conf.d/default.conf && echo 'default.conf: OK'
echo '--- nginx test ---'
nginx -t
nginx -s reload
echo '--- /cities/ redirect ---'
curl -skI https://127.0.0.1/cities/nanjing/ -H 'Host: www.zhi100hui.com' | head -5
echo '--- ca still up ---'
curl -skI https://ca.zhi100hui.com/ | head -3
"""
    _, stdout, stderr = client.exec_command(cmd, get_pty=True)
    out = stdout.read().decode("utf-8", "replace")
    err = stderr.read().decode("utf-8", "replace")
    code = stdout.channel.recv_exit_status()
    print(out)
    if err.strip():
        print(err, file=sys.stderr)
    client.close()
    sys.exit(code)


if __name__ == "__main__":
    main()
