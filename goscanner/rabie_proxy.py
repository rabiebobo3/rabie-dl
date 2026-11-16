#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ═══════════════════════════════════════════════════════
#  رايبو-بروكسي — بروكسي HTTP/SOCKS-CONNECT بملف واحد
#  بلا مكتبات خارجية — يخدم على Termux والكمبيوتر
#  الاستعمال: python rabie_proxy.py [المنفذ]
#  الافتراضي: 8888
# ═══════════════════════════════════════════════════════
import socket
import threading
import sys
from urllib.parse import urlsplit

PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 8888
LISTEN = ("0.0.0.0", PORT)


def pipe(a, b):
    """ينقل البيانات بين اتصالين حتى ينقطع أحداهما"""
    try:
        while True:
            d = a.recv(65536)
            if not d:
                break
            b.sendall(d)
    except Exception:
        pass
    for x in (a, b):
        try:
            x.close()
        except Exception:
            pass


def handle(client):
    try:
        client.settimeout(20)
        req = b""
        while b"\r\n\r\n" not in req and len(req) < 65536:
            chunk = client.recv(65536)
            if not chunk:
                break
            req += chunk
        if not req:
            return
        line = req.split(b"\r\n")[0].decode("latin1")
        parts = line.split(" ")
        if len(parts) < 2:
            return
        method, url = parts[0], parts[1]
        ver = parts[2] if len(parts) > 2 else "HTTP/1.1"

        if method == "CONNECT":
            # ── HTTPS: نفتح نفق وإيّاه يشفّر بمزاجه ──
            host, port = url.rsplit(":", 1)
            up = socket.create_connection((host, int(port or 443)), timeout=20)
            client.sendall(b"HTTP/1.1 200 Connection Established\r\n\r\n")
            t1 = threading.Thread(target=pipe, args=(client, up), daemon=True)
            t2 = threading.Thread(target=pipe, args=(up, client), daemon=True)
            t1.start(); t2.start()
            t1.join(); t2.join()
        else:
            # ── HTTP عادي: نعيد بناء الطلب ونرسله للسيرفر ──
            u = urlsplit(url)
            host = u.hostname
            port = u.port or 80
            path = (u.path or "/") + (("?" + u.query) if u.query else "")
            head_lines = req.split(b"\r\n\r\n")[0].split(b"\r\n")[1:]
            out = ("%s %s %s\r\n" % (method, path, ver)).encode("latin1")
            for h in head_lines:
                hl = h.decode("latin1", "replace").lower()
                # نرمي ترويسات البروكسي نفسها
                if hl.startswith("proxy-connection") or hl.startswith("proxy-authorization"):
                    continue
                out += h + b"\r\n"
            out += b"\r\n"
            up = socket.create_connection((host, port), timeout=20)
            up.sendall(out)
            body = req.split(b"\r\n\r\n", 1)[1] if b"\r\n\r\n" in req else b""
            if body:
                up.sendall(body)
            pipe(up, client)
    except Exception:
        try:
            client.sendall(b"HTTP/1.1 502 Bad Gateway\r\n\r\n")
        except Exception:
            pass
    finally:
        try:
            client.close()
        except Exception:
            pass


def main():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(LISTEN)
    s.listen(50)
    print("✅ رايبو-بروكسي يعمل على المنفذ %d — Ctrl+C للإيقاف" % PORT, flush=True)
    n = 0
    while True:
        c, addr = s.accept()
        n += 1
        print("[%d] اتصال من %s:%d" % (n, addr[0], addr[1]))
        threading.Thread(target=handle, args=(c,), daemon=True).start()


if __name__ == "__main__":
    main()
