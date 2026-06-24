# -*- coding: utf-8 -*-
"""整理官网图片 → 重命名 → 打包上传 COS（website-z100h/）"""
import json
import shutil
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
WEB = ROOT / "官网"
OUT = ROOT / "cos-upload" / "website-z100h"
ZIP = ROOT / "zhi100hui-cos-images.zip"

COS_BASE = "https://mpfamily-1301068541.cos.ap-shanghai.myqcloud.com/website-z100h"

# 仅打包 HTML 实际引用的图片
FILES = {
    "favicon.png": "z100h-favicon.png",
    "assets/img/og-cover.jpg": "z100h-og-cover.jpg",
    "assets/img/hero-office.jpg": "z100h-hero-office.jpg",
    "assets/img/scene-commercial.jpg": "z100h-scene-commercial.jpg",
    "assets/img/scene-home.jpg": "z100h-scene-home.jpg",
    "assets/img/scene-retail.jpg": "z100h-scene-retail.jpg",
    "assets/img/gaoxin-zhengshu.png": "z100h-cert-gaoxin.png",
    "assets/img/honor-miaomu-fuhuizhang.png": "z100h-cert-miaomu.png",
    "assets/img/patent-fm-108427359.png": "z100h-patent-fm-108427359.png",
    "assets/img/patent-syxx-2018.png": "z100h-patent-syxx-2018.png",
    "assets/img/patent-syxx-214902408.png": "z100h-patent-syxx-214902408.png",
    "assets/img/patent-syxx-219555734.png": "z100h-patent-syxx-219555734.png",
    "assets/img/brand/logo-xiaozhi.png": "z100h-brand-logo.png",
    "assets/img/brand/xiaozhi-t.png": "z100h-brand-mascot.png",
    "assets/img/brand/xiaozhi-pair.jpg": "z100h-brand-mascot-pair.jpg",
}

manifest = []
if OUT.exists():
    shutil.rmtree(OUT.parent)
OUT.mkdir(parents=True)

for src_rel, cos_name in FILES.items():
    src = WEB / src_rel.replace("/", "\\") if "\\" in str(WEB) else WEB / src_rel
    src = WEB / Path(src_rel)
    if not src.is_file():
        raise SystemExit(f"缺失: {src}")
    dst = OUT / cos_name
    shutil.copy2(src, dst)
    url = f"{COS_BASE}/{cos_name}"
    manifest.append({"local": src_rel, "cos_file": cos_name, "url": url})
    print(f"OK  {cos_name}  <=  {src_rel}")

readme = OUT.parent / "README-COS上传.txt"
readme.write_text(
    f"""植百汇官网 · 对象存储图片包
================================
上传到 COS 路径：website-z100h/
访问前缀：{COS_BASE}/

操作：
1. 打开腾讯云 COS 控制台 → 存储桶 mpfamily-1301068541
2. 进入 website-z100h/ 目录
3. 上传 website-z100h/ 文件夹内全部 {len(FILES)} 个文件（可覆盖同名）
4. 确认任意图片浏览器可访问，例如：
   {COS_BASE}/z100h-brand-logo.png

文件清单见 manifest.json
""",
    encoding="utf-8",
)

(OUT.parent / "manifest.json").write_text(
    json.dumps({"base_url": COS_BASE, "files": manifest}, ensure_ascii=False, indent=2),
    encoding="utf-8",
)

if ZIP.exists():
    ZIP.unlink()
with zipfile.ZipFile(ZIP, "w", zipfile.ZIP_DEFLATED) as zf:
    for f in OUT.iterdir():
        zf.write(f, f"website-z100h/{f.name}")
    zf.write(readme, "README-COS上传.txt")
    zf.write(OUT.parent / "manifest.json", "manifest.json")

size_mb = ZIP.stat().st_size / 1024 / 1024
print(f"\n打包完成: {ZIP} ({size_mb:.2f} MB)")
print(f"目录: {OUT}")
