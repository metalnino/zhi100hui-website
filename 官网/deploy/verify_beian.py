# -*- coding: utf-8 -*-
import re
import urllib.request

BASE = "https://www.zhi100hui.com"
ICON = "https://mpfamily-1301068541.cos.ap-shanghai.myqcloud.com/website-z100h/%E5%A4%87%E6%A1%88%E5%9B%BE%E6%A0%87.png"

html = urllib.request.urlopen(BASE + "/", timeout=20).read().decode("utf-8", "replace")
ok_beian = "苏公网安备32011502014039号" in html and "32011502014039" in html
ok_link = "beian.gov.cn/portal/registerSystemInfo" in html
print("首页备案号:", "OK" if ok_beian else "FAIL")
print("备案链接:", "OK" if ok_link else "FAIL")

try:
    r = urllib.request.urlopen(ICON, timeout=20)
    print("COS 图标:", r.status, r.getheader("Content-Type", "")[:30])
except Exception as e:
    print("COS 图标: FAIL", e)
