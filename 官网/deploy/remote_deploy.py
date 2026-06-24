# -*- coding: utf-8 -*-
"""一次性远程部署：上传 zip 并解压到 /var/www/zhi100hui"""
import os
import sys
import paramiko
from scp import SCPClient

HOST = "120.27.118.87"
USER = "root"
ZIP_LOCAL = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "zhi100hui-deploy.zip",
)
ZIP_REMOTE = "/root/zhi100hui-deploy.zip"
WEB_ROOT = "/var/www/zhi100hui"


def main():
    password = os.environ.get("DEPLOY_SSH_PASSWORD")
    if not password:
        print("ERROR: set DEPLOY_SSH_PASSWORD env var", file=sys.stderr)
        sys.exit(1)
    if not os.path.isfile(ZIP_LOCAL):
        print(f"ERROR: zip not found: {ZIP_LOCAL}", file=sys.stderr)
        sys.exit(1)

    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    # 兼容老服务器 OpenSSH（仅 ssh-rsa 主机密钥）
    try:
        paramiko.Transport._preferred_keys = (
            "ssh-ed25519",
            "ecdsa-sha2-nistp256",
            "ecdsa-sha2-nistp384",
            "ecdsa-sha2-nistp521",
            "ssh-rsa",
        )
    except Exception:
        pass
    print(f"Connecting to {HOST}...")
    client.connect(
        HOST,
        username=USER,
        password=password,
        timeout=30,
        allow_agent=False,
        look_for_keys=False,
    )

    print(f"Uploading {ZIP_LOCAL} -> {ZIP_REMOTE} ...")
    with SCPClient(client.get_transport(), progress=progress) as scp:
        scp.put(ZIP_LOCAL, ZIP_REMOTE)

    commands = f"""
set -e
mkdir -p {WEB_ROOT}
cd {WEB_ROOT}
if ! command -v unzip >/dev/null 2>&1; then yum install -y unzip; fi
unzip -o {ZIP_REMOTE}
chown -R root:nginx {WEB_ROOT}
find {WEB_ROOT} -type d -exec chmod 755 {{}} \\;
find {WEB_ROOT} -type f -exec chmod 644 {{}} \\;
echo '--- ls web root ---'
ls -la {WEB_ROOT}
echo '--- sample ---'
ls -la {WEB_ROOT}/guanyu/ {WEB_ROOT}/css/ {WEB_ROOT}/assets/fonts/ 2>/dev/null || true
"""
    print("Running remote unzip + permissions...")
    stdin, stdout, stderr = client.exec_command(commands, get_pty=True)
    out = stdout.read().decode("utf-8", errors="replace")
    err = stderr.read().decode("utf-8", errors="replace")
    code = stdout.channel.recv_exit_status()
    print(out)
    if err.strip():
        print(err, file=sys.stderr)
    client.close()
    if code != 0:
        print(f"Remote command failed: exit {code}", file=sys.stderr)
        sys.exit(code)
    print("DONE: files deployed to", WEB_ROOT)


def progress(filename, size, sent):
    pct = int(sent / size * 100) if size else 0
    if sent == size or pct % 20 == 0:
        print(f"  upload {pct}%")


if __name__ == "__main__":
    main()
