# -*- coding: utf-8 -*-
import re
import urllib.request

home = "https://www.zhi100hui.com/"
r = urllib.request.urlopen(home)
html = r.read().decode("utf-8")
print(f"HTTPS homepage: {r.status}")

cos = sorted(set(re.findall(r"https://mpfamily[^\s\"'<>]+", html)))
print(f"COS refs in homepage: {len(cos)}")
for u in cos[:8]:
    st = urllib.request.urlopen(u).status
    print(f"  {st} {u.split('/')[-1]}")

print("HTTP redirect test:")
req = urllib.request.Request("http://www.zhi100hui.com/", method="HEAD")
try:
    urllib.request.urlopen(req)
except urllib.error.HTTPError as e:
    print(f"  {e.code} Location: {e.headers.get('Location')}")
