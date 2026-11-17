#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ═══════════════════════════════════════════════════════
#  بوابة التدريب — مدرسة MAC العشوائية (كل شيء وهمي وآمن)
#  تشغلها في تيرميكس: python school.py
#  ثم تجرب عليها سكريبت السكانر بماكات عشوائية
#  ── كل ماك عشوائية عندها ~12% فرصة تطلع "حي" (تمثيل)
#     في البوابات الحقيقية: 1 من 30,000 — هنا مسرّعة للتعلم
# ═══════════════════════════════════════════════════════
import json
import hashlib
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse, parse_qs, unquote

PORT = 8899
TOKEN = "SCHOOLTOKEN1234567890ABCDEF"


def _dumps(obj):
    return json.dumps(obj, separators=(",", ":"))


def mac_of(self):
    u = urlparse(self.path)
    q = parse_qs(u.query)
    mac = (q.get("mac") or [""])[0]
    if not mac:
        mac = self.headers.get("Cookie", "")
    mac = unquote(mac)
    if mac.lower().startswith("mac="):
        mac = mac[4:]
    mac = mac.split(";")[0].strip().upper()
    if "%" in mac:
        mac = unquote(mac)
    return mac


def is_active(mac):
    """~12.5% من الماكات تصادف حية — حتمية (نفس الماك = نفس النتيجة)"""
    h = hashlib.md5(mac.encode()).hexdigest()
    return int(h[:8], 16) % 8 == 3


def creds(mac):
    h = hashlib.md5(("c" + mac).encode()).hexdigest()
    return "sim" + h[:6], "P" + h[6:12]


def exp_epoch(mac):
    h = int(hashlib.md5(("e" + mac).encode()).hexdigest()[:6], 16)
    return 1790000000 + (h % 400) * 86400  # بين 2026 و2027


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def _send(self, code, body, headers=None):
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        for k, v in (headers or {}).items():
            self.send_header(k, v)
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        u = urlparse(self.path)
        q = parse_qs(u.query)
        action = (q.get("action") or [""])[0]
        mac = mac_of(self)
        ua = self.headers.get("User-Agent", "")

        # ── Xtream player_api (استدعاءات السكريبت بعد الـHIT) ──
        if u.path == "/player_api.php":
            user = (q.get("username") or [""])[0]
            info = {
                "username": user, "password": (q.get("password") or [""])[0],
                "message": "", "status": "Active",
                "exp_date": str(exp_epoch(mac)), "is_trial": "0",
                "active_cons": "0", "max_connections": "1",
                "created_at": "1730000000",
                "url": "http://127.0.0.1", "port": "8899",
                "timezone": "Africa/Algiers",
            }
            a = (q.get("action") or [""])[0]
            if a == "get_live_streams":
                self._send(200, _dumps([{"stream_id": i, "name": "ch%d" % i} for i in range(1, 43)]).encode()); return
            if a == "get_vod_streams":
                self._send(200, _dumps([{"stream_id": i, "name": "mov%d" % i} for i in range(1, 6)]).encode()); return
            if a == "get_series":
                self._send(200, _dumps([{"series_id": i, "name": "ser%d" % i} for i in range(1, 4)]).encode()); return
            if a == "get_live_categories":
                self._send(200, _dumps([{"category_id": 1, "category_name": "SPORTS"}, {"category_id": 2, "category_name": "NEWS"}]).encode()); return
            if a == "get_vod_categories":
                self._send(200, _dumps([{"category_id": 3, "category_name": "MOVIES"}]).encode()); return
            if a == "get_series_categories":
                self._send(200, _dumps([{"category_id": 4, "category_name": "SERIES"}]).encode()); return
            self._send(200, _dumps({"user_info": info}).encode()); return

        # ── M3U ──
        if u.path == "/get.php":
            user = (q.get("username") or ["sim"])[0]
            pas = (q.get("password") or ["P"])[0]
            body = "#EXTM3U\n#EXTINF:-1,Test Channel\nhttp://127.0.0.1:%d/live/%s/%s/1.ts\n" % (PORT, user, pas)
            self._send(200, body.encode()); return

        # ── Stalker: فقط /c/server/load.php ──
        if not (u.path.endswith("/server/load.php") and "/c/" in u.path):
            self._send(404, b'{"error":"not found"}'); return

        if action == "handshake":
            self._send(200, _dumps({"js": {"token": TOKEN}}).encode()); return

        if action == "get_profile":
            if is_active(mac):
                js = {"id": 12345, "name": "simuser", "status": "Active",
                      "exp_date": "2027-06-15 12:00:00",
                      "last_active": "2026-11-17 00:00:00"}
            else:
                js = {"id": 0, "name": 0, "status": 0,
                      "last_active": "2022-02-18 12:00:00"}
            self._send(200, _dumps({"js": js}).encode()); return

        if action == "get_main_info":
            # الماكات الميتة: بلا مفتاح phone نهائياً (كيف البوابات الحقيقية)
            if is_active(mac):
                js = {"mac": mac, "phone": "June 15, 2027, 12:00 pm"}
                self._send(200, _dumps({"js": js}).encode())
            else:
                self._send(200, _dumps({"js": {}}).encode())
            return

        if action == "get_ordered_list":
            usr, pas = creds(mac)
            self._send(200, _dumps({"js": [{"cmd": "ffmpeg http://127.0.0.1:%d/movie/%s/%s/100.mkv" % (PORT, usr, pas), "id": 100}]}).encode()); return

        if action == "create_link":
            usr, pas = creds(mac)
            cmd = (q.get("cmd") or [""])[0]
            if "movie" in cmd:
                link = "http://127.0.0.1:%d/movie/%s/%s/100.mkv" % (PORT, usr, pas)
            else:
                link = "http://127.0.0.1:%d/live/%s/%s/1.ts" % (PORT, usr, pas)
            self._send(200, _dumps({"js": {"cmd": link, "id": 100}}).encode()); return

        if action == "get_all_channels":
            chans = [{"num": i, "name": "ch%d" % i} for i in range(1, 43)]
            self._send(200, _dumps({"js": chans}).encode()); return

        if action == "get_genres":
            self._send(200, _dumps({"js": [{"id": 1, "title": "SPORTS"}, {"id": 2, "title": "NEWS"}]}).encode()); return

        self._send(404, b'{"error":"bad action"}')


if __name__ == "__main__":
    print("✅ بوابة التدريب تعمل على المنفذ %d — ما تسدش هذا التيرميكس" % PORT, flush=True)
    print("   (وهمية 100% — كل النتائج تمثيل داخل تلفونك)", flush=True)
    ThreadingHTTPServer(("127.0.0.1", PORT), Handler).serve_forever()
