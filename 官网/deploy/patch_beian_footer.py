# -*- coding: utf-8 -*-
"""一次性：全站页脚追加公安备案号（图标在 COS）。"""
import glob
import os

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
OLD = '<a href="https://beian.miit.gov.cn/" target="_blank" rel="nofollow noopener">苏ICP备17037731号</a>'
NEW = (
    OLD
    + ' · <a href="http://www.beian.gov.cn/portal/registerSystemInfo?recordcode=32011502014039"'
    + ' rel="noreferrer" target="_blank" class="beian-link">'
    + '<img src="https://mpfamily-1301068541.cos.ap-shanghai.myqcloud.com/website-z100h/%E5%A4%87%E6%A1%88%E5%9B%BE%E6%A0%87.png"'
    + ' alt="" width="16" height="16">苏公网安备32011502014039号</a>'
)

n = 0
for path in glob.glob(os.path.join(ROOT, "**", "*.html"), recursive=True):
    with open(path, encoding="utf-8") as f:
        s = f.read()
    if OLD in s and NEW not in s:
        with open(path, "w", encoding="utf-8", newline="") as f:
            f.write(s.replace(OLD, NEW))
        n += 1
        print("updated:", os.path.relpath(path, ROOT))
print("done:", n, "files")
