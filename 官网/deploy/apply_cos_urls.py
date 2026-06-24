# -*- coding: utf-8 -*-
"""将官网 HTML 中本地图片路径替换为 COS 绝对 URL"""
from pathlib import Path

COS = "https://mpfamily-1301068541.cos.ap-shanghai.myqcloud.com/website-z100h"

REPLACEMENTS = [
    ("https://www.zhi100hui.com/assets/img/og-cover.jpg", f"{COS}/z100h-og-cover.jpg"),
    ("https://www.zhi100hui.com/favicon.png", f"{COS}/z100h-favicon.png"),
    ("/assets/img/brand/logo-xiaozhi.png", f"{COS}/z100h-brand-logo.png"),
    ("/assets/img/brand/xiaozhi-t.png", f"{COS}/z100h-brand-mascot.png"),
    ("/assets/img/brand/xiaozhi-pair.jpg", f"{COS}/z100h-brand-mascot-pair.jpg"),
    ("/assets/img/hero-office.jpg", f"{COS}/z100h-hero-office.jpg"),
    ("/assets/img/scene-commercial.jpg", f"{COS}/z100h-scene-commercial.jpg"),
    ("/assets/img/scene-home.jpg", f"{COS}/z100h-scene-home.jpg"),
    ("/assets/img/scene-retail.jpg", f"{COS}/z100h-scene-retail.jpg"),
    ("/assets/img/gaoxin-zhengshu.png", f"{COS}/z100h-cert-gaoxin.png"),
    ("/assets/img/honor-miaomu-fuhuizhang.png", f"{COS}/z100h-cert-miaomu.png"),
    ("/assets/img/patent-fm-108427359.png", f"{COS}/z100h-patent-fm-108427359.png"),
    ("/assets/img/patent-syxx-2018.png", f"{COS}/z100h-patent-syxx-2018.png"),
    ("/assets/img/patent-syxx-214902408.png", f"{COS}/z100h-patent-syxx-214902408.png"),
    ("/assets/img/patent-syxx-219555734.png", f"{COS}/z100h-patent-syxx-219555734.png"),
    ("/favicon.png", f"{COS}/z100h-favicon.png"),
]

WEB = Path(__file__).resolve().parents[1]
html_files = list(WEB.rglob("*.html"))
changed = 0
for fp in html_files:
    text = fp.read_text(encoding="utf-8")
    orig = text
    for old, new in REPLACEMENTS:
        text = text.replace(old, new)
    if text != orig:
        fp.write_text(text, encoding="utf-8")
        changed += 1
        print(f"updated: {fp.relative_to(WEB)}")

print(f"\n共更新 {changed} 个 HTML 文件")
