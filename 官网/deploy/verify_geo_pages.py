# -*- coding: utf-8 -*-
import urllib.request

BASE = "https://www.zhi100hui.com"
paths = [
    "/changjing/",
    "/changjing/bangong/",
    "/changjing/shangchang/",
    "/changjing/jiudian/",
    "/changjing/jiating/",
    "/zhinan/",
    "/zhinan/zubai-vs-goumai/",
    "/zhinan/bangong-yusuan/",
    "/zhinan/zhihui-zubai/",
]
ok = 0
for p in paths:
    try:
        r = urllib.request.urlopen(BASE + p, timeout=20)
        print(f"OK {r.status} {p}")
        ok += 1
    except Exception as e:
        print(f"FAIL {p} {e}")
print(f"done: {ok}/{len(paths)}")
