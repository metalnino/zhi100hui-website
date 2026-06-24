# -*- coding: utf-8 -*-
"""
恢复 default.conf（ca.zhi100hui.com 等应用反代），
注释掉与 nginx-zhi100hui.conf 冲突的 www/裸域 server 块（原 bak 第 169–206 行）。
"""
import os
import sys
import paramiko

HOST = "120.27.118.87"
BAK = "/etc/nginx/conf.d/default.conf.bak.20260624"
OUT = "/etc/nginx/conf.d/default.conf"

pwd = os.environ.get("DEPLOY_SSH_PASSWORD")
if not pwd:
    sys.exit("need DEPLOY_SSH_PASSWORD")

c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect(HOST, username="root", password=pwd, timeout=30, allow_agent=False, look_for_keys=False)

cmd = r"""
set -e
BAK=/etc/nginx/conf.d/default.conf.bak.20260624
OUT=/etc/nginx/conf.d/default.conf

# 备份当前（若存在）
test -f "$OUT" && cp -a "$OUT" "${OUT}.before-restore.$(date +%Y%m%d%H%M)"

{
  echo '# 2026-06-24 恢复：应用子域 ca/mp/wx 等（自 default.conf.bak.20260624）'
  echo '# www.zhi100hui.com / zhi100hui.com 静态官网 → nginx-zhi100hui.conf'
  echo ''
  awk '
    NR>=169 && NR<=206 {
      if (NR==169) print "# [zhi100hui-static] 以下块已禁用，官网由 nginx-zhi100hui.conf 提供"
      if ($0 ~ /^[[:space:]]*$/) print "#"
      else print "# " $0
      next
    }
    { print }
  ' "$BAK"
} > "$OUT"

echo '--- commented block preview ---'
sed -n '165,215p' "$OUT" | head -25

nginx -t
nginx -s reload

echo '=== ca HTTPS (expect not 301 to www) ==='
curl -skI https://127.0.0.1/ -H 'Host: ca.zhi100hui.com' | head -8

echo '=== www HTTPS static ==='
curl -skI https://127.0.0.1/ -H 'Host: www.zhi100hui.com' | head -5

echo '=== wx HTTP -> ca redirect ==='
curl -sI http://127.0.0.1/ -H 'Host: wx.zhi100hui.com' | head -5
"""

_, stdout, stderr = c.exec_command(cmd, get_pty=True)
out = stdout.read().decode("utf-8", errors="replace")
err = stderr.read().decode("utf-8", errors="replace")
code = stdout.channel.recv_exit_status()
print(out)
if err.strip():
    print(err, file=sys.stderr)
c.close()
sys.exit(code)
