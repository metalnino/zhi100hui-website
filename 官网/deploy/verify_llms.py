# -*- coding: utf-8 -*-
import urllib.request

for url in [
    "https://www.zhi100hui.com/llms.txt",
    "https://zhi100hui.com/llms.txt",
]:
    req = urllib.request.Request(url, headers={"User-Agent": "LLM-Test"})
    r = urllib.request.urlopen(req, timeout=15)
    body = r.read().decode("utf-8")
    ct = r.headers.get("Content-Type", "")
    ok = body.startswith("# 植百汇") and "text/html" not in ct.lower()
    print(f"{url}")
    print(f"  status={r.status} type={ct} valid={ok} len={len(body)}")
    print(f"  head: {body.splitlines()[0]}")
    print()
