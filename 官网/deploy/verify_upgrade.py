# -*- coding: utf-8 -*-
"""上线后检查：页面、COS 城市图、导航、ca 子域"""
import re
import urllib.error
import urllib.request
import xml.etree.ElementTree as ET

BASE = "https://www.zhi100hui.com"
COS = "https://mpfamily-1301068541.cos.ap-shanghai.myqcloud.com/website-z100h"
CITIES = ["nanjing", "shanghai", "suzhou", "hangzhou", "shenzhen", "wuhan", "hefei", "guangzhou"]

issues = []
passed = []


def check_url(url):
    try:
        r = urllib.request.urlopen(url, timeout=20)
        return True, r.status, r.getheader("Content-Type", "")[:50]
    except urllib.error.HTTPError as e:
        return False, e.code, str(e.reason)
    except Exception as e:
        return False, "ERR", str(e)[:80]


def ok(label):
    passed.append(label)


def fail(label, detail=""):
    issues.append((label, detail))


print("=== 1. 核心页面 ===")
for path in ["/", "/chengshi/", "/chengshi/nanjing/", "/ai.txt", "/llms.txt", "/sitemap.xml"]:
    good, st, info = check_url(BASE + path)
    flag = "OK" if good else "FAIL"
    print(f"  [{flag}] {st}  {path}")
    if good:
        ok(f"页面 {path}")
    else:
        fail(f"页面 {path}", str(st))

print("\n=== 2. COS 城市配图 (8张) ===")
cos_ok = 0
for c in CITIES:
    url = f"{COS}/z100h-city-{c}.jpg"
    good, st, _ = check_url(url)
    flag = "OK" if good else "FAIL"
    print(f"  [{flag}] z100h-city-{c}.jpg -> {st}")
    if good:
        cos_ok += 1
    else:
        fail(f"COS 城市图 {c}", str(st))
print(f"  汇总: {cos_ok}/8")

print("\n=== 3. 首页导航与城市入口 ===")
html = urllib.request.urlopen(BASE + "/", timeout=20).read().decode("utf-8", "replace")
if re.search(r'href="/chengshi/"[^>]*>服务城市', html):
    print("  [OK] 顶栏「服务城市」-> /chengshi/")
    ok("顶栏服务城市链接")
else:
    print("  [FAIL] 顶栏未指向 /chengshi/")
    fail("顶栏服务城市链接")

chips = len(re.findall(r'href="/chengshi/[a-z]+/"', html))
print(f"  [OK] 首页城市 chip: {chips} 个" if chips >= 8 else f"  [FAIL] chip 仅 {chips} 个")
if chips >= 8:
    ok("首页城市 chip")
else:
    fail("首页城市 chip", str(chips))

print("\n=== 4. 南京页 banner（应走 COS）===")
nj = urllib.request.urlopen(BASE + "/chengshi/nanjing/", timeout=20).read().decode("utf-8", "replace")
m = re.search(r'page-banner.*?src="([^"]+)"', nj, re.S)
if m:
    img = m.group(1)
    good, st, _ = check_url(img)
    on_cos = "mpfamily" in img and "z100h-city-nanjing" in img
    print(f"  src: {img}")
    print(f"  [{'OK' if on_cos else 'WARN'}] 引用 COS URL")
    print(f"  [{'OK' if good else 'FAIL'}] banner HTTP {st}")
    if on_cos and good:
        ok("南京 banner COS")
    else:
        fail("南京 banner", img)
else:
    fail("南京 banner", "未找到 img")

print("\n=== 5. sitemap ===")
sm = urllib.request.urlopen(BASE + "/sitemap.xml", timeout=20).read()
root = ET.fromstring(sm)
ns = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}
locs = [e.text for e in root.findall(".//sm:loc", ns)]
city_urls = [u for u in locs if "/chengshi/" in u]
print(f"  总 URL: {len(locs)}  |  chengshi: {len(city_urls)}")
if len(city_urls) >= 9:
    ok("sitemap 城市 URL")
else:
    fail("sitemap 城市 URL", str(len(city_urls)))

print("\n=== 6. ca 子域（应用不能炸）===")
try:
    req = urllib.request.Request("https://ca.zhi100hui.com/", method="HEAD")
    urllib.request.urlopen(req, timeout=15)
    print("  [OK] ca 200")
    ok("ca.zhi100hui.com")
except urllib.error.HTTPError as e:
    if e.code in (200, 301, 302, 303, 307, 308):
        print(f"  [OK] ca HTTP {e.code}")
        ok("ca.zhi100hui.com")
    else:
        print(f"  [FAIL] ca HTTP {e.code}")
        fail("ca.zhi100hui.com", str(e.code))
except Exception as e:
    print(f"  [FAIL] {e}")
    fail("ca.zhi100hui.com", str(e))

print("\n" + "=" * 40)
if issues:
    print(f"结论: 有 {len(issues)} 项需关注")
    for label, detail in issues:
        print(f"  - {label}: {detail}")
else:
    print(f"结论: 全部通过 ({len(passed)} 项检查 OK)")
