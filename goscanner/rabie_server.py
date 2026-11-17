#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ═══════════════════════════════════════════════════════════════
#  رايبو-سيرفر — سيرفر IPTV خاص بك من العدم (في تلفونك!)
#  ── روابطك انت → قوائم M3U + حساب Xtream (يوزر/باس)
#  ── تحطها في أي مشغل: RabieTV2 / Smarters / VLC / XCIPTV...
#  ── وحتى أي واحد في نفس الواي-فاي يقدر يتصل بيها
#
#  الاستعمال (في تيرميكس):
#    python rabie_server.py                          ← تشغيل السيرفر
#    python rabie_server.py setuser MyUser MyPass    ← حسابك (يوزر/باس)
#    python rabie_server.py add "اسم القناة" http://رابط
#    python rabie_server.py file /sdcard/Download/my.m3u   ← حمّل قنواتك من ملف
#    python rabie_server.py list                     ← القنوات
#    python rabie_server.py del 3                    ← امسح قناة رقم 3
# ═══════════════════════════════════════════════════════════════
import os, sys, json, datetime
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse, parse_qs, unquote

DIR = os.environ.get("RABIE_SERVER_DIR") or "/sdcard/RabieServer"
PORT = int(os.environ.get("RABIE_SERVER_PORT") or 8899)
F_CH = os.path.join(DIR, "channels.txt")   # اسم|رابط (سطر لكل قناة)
F_CFG = os.path.join(DIR, "config.txt")    # يوزر|باس

DEMO = [
    ("Big Buck Bunny", "http://commondatastorage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4"),
    ("Apple HLS Test", "http://devstreaming-cdn.apple.com/videos/streaming/examples/img_bipbop_adv_example_fmp4/master.m3u8"),
    ("Elephants Dream", "http://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ElephantsDream.mp4"),
    ("For Bigger Blazes", "http://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerBlazes.mp4"),
    ("Sintel", "http://commondatastorage.googleapis.com/gtv-videos-bucket/sample/Sintel.mp4"),
    ("Tears of Steel", "http://commondatastorage.googleapis.com/gtv-videos-bucket/sample/TearsOfSteel.mp4"),
]

def ensure():
    try:
        os.makedirs(DIR, exist_ok=True)
    except Exception:
        home = os.path.expanduser("~/.rabieserver")
        os.makedirs(home, exist_ok=True)
        return home
    return DIR

def ddir():
    global DIR
    if not os.path.isdir(DIR):
        DIR = ensure()
    return DIR

def fp(name):
    return os.path.join(ddir(), name)

def creds():
    lines = []
    try:
        lines = [l.strip() for l in open(fp("config.txt"), encoding="utf-8") if l.strip()]
    except Exception:
        pass
    if not lines:
        return "rabie", "1234"
    p = lines[0].split("|")
    return (p[0] or "rabie"), (p[1] if len(p) > 1 else "1234")

def channels():
    out = []
    try:
        for l in open(fp("channels.txt"), encoding="utf-8"):
            l = l.strip()
            if not l or "|" not in l:
                continue
            nm, url = l.split("|", 1)
            out.append((len(out) + 1, nm.strip(), url.strip()))
    except Exception:
        pass
    return out

def save_channels(chs):
    with open(fp("channels.txt"), "w", encoding="utf-8") as w:
        for _, nm, url in chs:
            w.write(nm + "|" + url + "\n")

# ───── الأوامر ─────
def cmd_setuser(a):
    if len(a) < 2:
        print("❌ مثال: python rabie_server.py setuser MyUser MyPass"); return
    ddir()
    open(fp("config.txt"), "w").write(a[0] + "|" + a[1] + "\n")
    print("✅ حسابك: يوزر=%s باس=%s — استعملهم في أي مشغل Xtream" % (a[0], a[1]))

def cmd_add(a):
    if len(a) < 2:
        print('❌ مثال: python rabie_server.py add "اسم القناة" http://رابط'); return
    ddir()
    chs = channels()
    chs.append((0, a[0], a[1]))
    save_channels(chs)
    print("✅ زدت القناة «%s» — المجموع: %d" % (a[0], len(chs)))

def cmd_file(a):
    if not a or not a[0].startswith("/"):
        print("❌ مثال: python rabie_server.py file /sdcard/Download/my.m3u"); return
    src = a[0]
    if not os.path.exists(src):
        print("❌ الملف ما كاينش: " + src); return
    chs = channels()
    n0 = len(chs)
    nm = None
    for l in open(src, encoding="utf-8", errors="replace"):
        l = l.strip()
        if l.startswith("#EXTINF"):
            nm = l.split(",", 1)[1].strip() if "," in l else None
        elif l and not l.startswith("#") and nm:
            chs.append((0, nm, l)); nm = None
    save_channels(chs)
    print("✅ رحمت %d قناة من الملف — المجموع: %d" % (len(chs) - n0, len(chs)))

def cmd_del(a):
    if not a or not a[0].isdigit():
        print("❌ مثال: python rabie_server.py del 3"); return
    chs = channels()
    i = int(a[0])
    if i < 1 or i > len(chs):
        print("❌ ما كاينش قناة بهذا الرقم"); return
    gone = chs.pop(i - 1)
    save_channels(chs)
    print("🗑️ مسحت «%s» — المجموع: %d" % (gone[1], len(chs)))

def cmd_list():
    chs = channels()
    u, p = creds()
    print("📺 القنوات (%d):" % len(chs))
    for n, nm, url in chs:
        print("   %d. %s" % (n, nm))
    print("🔑 الحساب: %s / %s" % (u, p))

# ───── السيرفر ─────
class Handler(BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def _send(self, code, body, ctype="application/json", extra=None):
        b = body if isinstance(body, bytes) else body.encode()
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(b)))
        for k, v in (extra or {}).items():
            self.send_header(k, v)
        self.end_headers()
        self.wfile.write(b)

    def _j(self, code, obj):
        self._send(code, json.dumps(obj, separators=(",", ":")))

    def _auth(self, q):
        u, p = creds()
        return (q.get("username") or [""])[0] == u and (q.get("password") or [""])[0] == p

    def do_GET(self):
        u = urlparse(self.path)
        q = parse_qs(u.query)
        chs = channels()
        CU, CP = creds()

        # ── Xtream player_api (للمشغلات: RabieTV2 / Smarters / XCIPTV) ──
        if u.path == "/player_api.php" or u.path == "/panel_api.php":
            if not self._auth(q):
                self._j(200, {"user_info": {"status": "Disabled", "auth": 0}}); return
            a = (q.get("action") or [""])[0]
            exp = str(int(datetime.datetime(2028, 1, 1).timestamp()))
            info = {"username": CU, "password": CP, "message": "Rabie Server",
                    "status": "Active", "exp_date": exp, "is_trial": "0",
                    "active_cons": "0", "max_connections": "2",
                    "created_at": "1730000000", "max_active_connections": "2",
                    "allowed_output_formats": ["m3u8", "ts", "rtmp"],
                    "url": "http://127.0.0.1", "port": str(PORT),
                    "timezone": "Africa/Algiers"}
            if a == "get_live_streams":
                self._j(200, [{"stream_id": n, "name": nm, "stream_icon": "",
                               "category_id": "1", "direct_source": url} for n, nm, url in chs]); return
            if a == "get_vod_streams":
                self._j(200, []); return
            if a == "get_series":
                self._j(200, []); return
            if a == "get_live_categories":
                self._j(200, [{"category_id": "1", "category_name": "RabieServer"}]); return
            if a == "get_vod_categories" or a == "get_series_categories":
                self._j(200, []); return
            self._j(200, {"user_info": info, "server_info": {
                "url": "http://127.0.0.1", "port": str(PORT),
                "timezone": "Africa/Algiers", "https_port": None}}); return

        # ── M3U (للمشغلات: VLC وأي مشغل ياخذ رابط قائمة) ──
        if u.path == "/get.php" or u.path == "/playlist.m3u":
            if not self._auth(q):
                self._send(403, "wrong username/password\n", "text/plain"); return
            host = self.headers.get("Host", "127.0.0.1:%d" % PORT)
            b = "#EXTM3U\n"
            for n, nm, url in chs:
                b += '#EXTINF:-1 tvg-id="%d" group-title="RabieServer",%s\n' % (n, nm)
                b += "http://%s/live/%s/%s/%d.ts\n" % (host, CU, CP, n)
            self._send(200, b, "audio/x-mpegurl"); return

        # ── البث: /live/يوزر/باس/رقم.ts → تحويل للرابط الحقيقي ──
        if u.path.startswith("/live/") or u.path.startswith("/movie/"):
            parts = u.path.split("/")
            if len(parts) >= 5 and parts[2] == CU and parts[3] == CP:
                try:
                    cid = int(parts[4].split(".")[0].split("_")[0])
                except Exception:
                    cid = 1
                url = next((x[2] for x in chs if x[0] == cid), None)
                if url:
                    self.send_response(302)
                    self.send_header("Location", url)
                    self.send_header("Content-Length", "0")
                    self.end_headers()
                    return
            self._send(403, "denied\n", "text/plain"); return

        self._send(404, '{"error":"not found"}')

def main():
    argv = sys.argv[1:]
    if not argv:
        ensure()
        chs, (u, p) = channels(), creds()
        print("✅ سيرفرك يعمل على المنفذ %d — ما تسدش هذا التيرميكس" % PORT, flush=True)
        print("   📺 القنوات: %d · 🔑 الحساب: %s / %s" % (len(chs), u, p), flush=True)
        print("   📋 رابط القائمة: http://127.0.0.1:%d/get.php?username=%s&password=%s" % (PORT, u, p), flush=True)
        print("   🎛️ تسجيل Xtream في المشغل: السيرفر 127.0.0.1:%d + اليوزر والباس" % PORT, flush=True)
        ThreadingHTTPServer(("0.0.0.0", PORT), Handler).serve_forever()
        return
    c, rest = argv[0], argv[1:]
    if c == "setuser": cmd_setuser(rest)
    elif c == "add": cmd_add(rest)
    elif c == "file": cmd_file(rest)
    elif c == "del": cmd_del(rest)
    elif c == "list": cmd_list()
    else:
        print("الأوامر: setuser / add / file / del / list — أو بلا أوامر = تشغيل السيرفر")

if __name__ == "__main__":
    main()
