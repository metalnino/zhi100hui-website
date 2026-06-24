# -*- coding: utf-8 -*-
"""上传 SSL 证书 + 切换 nginx HTTPS + 部署网站 + 验证 COS 图片"""
import os
import sys
import paramiko
from scp import SCPClient

HOST = "120.27.118.87"
USER = "root"
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SSL_DIR = os.path.join(ROOT, "ssl-zhi100hui")
CERT_LOCAL = os.path.join(SSL_DIR, "zhi100hui.com.pem")
KEY_LOCAL = os.path.join(SSL_DIR, "zhi100hui.com.key")
ZIP_LOCAL = os.path.join(ROOT, "zhi100hui-deploy.zip")
NGINX_CONF_LOCAL = os.path.join(os.path.dirname(__file__), "nginx-zhi100hui.conf")

SSL_REMOTE_DIR = "/etc/nginx/ssl"
CERT_REMOTE = f"{SSL_REMOTE_DIR}/zhi100hui.com.crt"
KEY_REMOTE = f"{SSL_REMOTE_DIR}/zhi100hui.com.key"
NGINX_CONF = "/etc/nginx/conf.d/nginx-zhi100hui.conf"
WEB_DEPLOY = "/var/www/zhi100hui/deploy/nginx-zhi100hui.conf"
ZIP_REMOTE = "/root/zhi100hui-deploy.zip"
WEB_ROOT = "/var/www/zhi100hui"

COS_SAMPLES = [
    "https://mpfamily-1301068541.cos.ap-shanghai.myqcloud.com/website-z100h/z100h-brand-logo.png",
    "https://mpfamily-1301068541.cos.ap-shanghai.myqcloud.com/website-z100h/z100h-hero-office.jpg",
    "https://mpfamily-1301068541.cos.ap-shanghai.myqcloud.com/website-z100h/z100h-favicon.png",
]


def connect():
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
    client.connect(HOST, username=USER, password=password, timeout=30,
                   allow_agent=False, look_for_keys=False)
    return client


def read_https_conf():
    """从 nginx-zhi100hui.conf 提取 HTTPS 生效段（三个 server 块）"""
    text = open(NGINX_CONF_LOCAL, encoding="utf-8").read()
    start = text.find("# --- HTTP：80 → HTTPS")
    end = text.find("# ============================================================\n# 纯 HTTP 版")
    if start == -1 or end == -1:
        print("ERROR: cannot parse nginx-zhi100hui.conf", file=sys.stderr)
        sys.exit(1)
    return text[start:end].strip() + "\n"


def run(client, cmd, label=""):
    if label:
        print(f"\n=== {label} ===")
    _, stdout, stderr = client.exec_command(cmd, get_pty=True)
    out = stdout.read().decode("utf-8", errors="replace")
    err = stderr.read().decode("utf-8", errors="replace")
    code = stdout.channel.recv_exit_status()
    print(out)
    if err.strip():
        print(err, file=sys.stderr)
    if code != 0:
        print(f"FAILED exit {code}", file=sys.stderr)
        sys.exit(code)
    return out


def main():
    for p in (CERT_LOCAL, KEY_LOCAL, ZIP_LOCAL, NGINX_CONF_LOCAL):
        if not os.path.isfile(p):
            print(f"ERROR: missing {p}", file=sys.stderr)
            sys.exit(1)

    client = connect()
    print(f"Connected to {HOST}")

    with SCPClient(client.get_transport()) as scp:
        print("Uploading SSL certificate and key...")
        scp.put(CERT_LOCAL, "/root/zhi100hui.com.pem")
        scp.put(KEY_LOCAL, "/root/zhi100hui.com.key")
        print(f"Uploading {ZIP_LOCAL}...")
        scp.put(ZIP_LOCAL, ZIP_REMOTE)
        scp.put(NGINX_CONF_LOCAL, WEB_DEPLOY)

    https_conf = read_https_conf()
    sftp = client.open_sftp()
    run(client, f"mkdir -p {SSL_REMOTE_DIR}", "Install SSL files")
    run(client, f"""
set -e
mv -f /root/zhi100hui.com.pem {CERT_REMOTE}
mv -f /root/zhi100hui.com.key {KEY_REMOTE}
chmod 644 {CERT_REMOTE}
chmod 600 {KEY_REMOTE}
ls -la {SSL_REMOTE_DIR}/
openssl x509 -in {CERT_REMOTE} -noout -subject -dates 2>/dev/null || true
""", "Verify cert")

    with sftp.file(NGINX_CONF, "w") as f:
        f.write(https_conf)
    sftp.close()
    print(f"Wrote HTTPS config: {NGINX_CONF}")

    run(client, f"""
set -e
mkdir -p {WEB_ROOT}
cd {WEB_ROOT}
if ! command -v unzip >/dev/null 2>&1; then yum install -y unzip; fi
unzip -o {ZIP_REMOTE} || test -f {WEB_ROOT}/index.html
if id nginx >/dev/null 2>&1; then chown -R root:nginx {WEB_ROOT} || chown -R root:root {WEB_ROOT}; else chown -R root:root {WEB_ROOT}; fi
find {WEB_ROOT} -type d -exec chmod 755 {{}} \\;
find {WEB_ROOT} -type f -exec chmod 644 {{}} \\;
echo '--- grep COS in index ---'
grep -o 'mpfamily[^\"]*z100h-brand-logo[^\"]*' {WEB_ROOT}/index.html | head -1 || echo 'COS_URL_NOT_FOUND'
""", "Deploy website zip")

    cos_urls = " ".join(COS_SAMPLES)
    run(client, f"""
set -e
cd /etc/nginx/conf.d
rm -f zhi100hui.conf nginx-legacy.conf 2>/dev/null || true
nginx -t
nginx -s reload
echo '--- HTTP redirect ---'
curl -sI http://127.0.0.1/ -H 'Host: www.zhi100hui.com' | head -6
echo '--- HTTPS homepage ---'
curl -skI https://127.0.0.1/ -H 'Host: www.zhi100hui.com' | head -8
echo '--- HTTPS guanyu ---'
curl -skI https://127.0.0.1/guanyu/ -H 'Host: www.zhi100hui.com' | head -5
echo '--- apex redirect ---'
curl -skI https://127.0.0.1/ -H 'Host: zhi100hui.com' | grep -i location || true
echo '--- COS images ---'
for u in {cos_urls}; do
  code=$(curl -s -o /dev/null -w '%{{http_code}}' "$u")
  echo "$code $u"
done
echo '--- homepage img tag ---'
curl -sk https://127.0.0.1/ -H 'Host: www.zhi100hui.com' | grep -o 'mpfamily[^\"]*z100h-brand-logo[^\"]*' | head -1 || echo 'NO_COS_IN_HTML'
""", "Reload nginx and verify")

    client.close()
    print("\nDONE: HTTPS live at https://www.zhi100hui.com/")


if __name__ == "__main__":
    main()
