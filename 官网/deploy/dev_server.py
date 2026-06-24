# -*- coding: utf-8 -*-
"""本地预览服务器：模拟线上 nginx 的"干净 URL + 根绝对路径"。
用法： python 官网/deploy/dev_server.py  然后浏览器打开 http://localhost:8080
（直接双击 index.html 会因为根绝对资源路径而样式丢失，必须用本服务器或 nginx 预览）
"""
import http.server, socketserver, os
from urllib.parse import urlparse, unquote

WEB = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # 官网 目录
PORT = 8080

class Handler(http.server.SimpleHTTPRequestHandler):
    def translate_path(self, path):
        p = unquote(urlparse(path).path)
        if p == "/":
            return os.path.join(WEB, "index.html")
        rel = p.lstrip("/")
        full = os.path.join(WEB, rel)
        # /guanyu/ 或 /guanyu -> guanyu.html
        if p.endswith("/") or os.path.isdir(full):
            cand = os.path.join(WEB, rel.rstrip("/") + ".html")
            if os.path.isfile(cand):
                return cand
        if not os.path.splitext(full)[1]:
            cand = full + ".html"
            if os.path.isfile(cand):
                return cand
        return full

Handler.extensions_map.update({".svg": "image/svg+xml"})

os.chdir(WEB)
# 多线程，避免浏览器 keep-alive 长连接把单线程服务器卡死
httpd = http.server.ThreadingHTTPServer(("127.0.0.1", PORT), Handler)
httpd.daemon_threads = True
print(f"serving {WEB} at http://localhost:{PORT}  (Ctrl+C to stop)")
httpd.serve_forever()
