#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ═══════════════════════════════════════════════════════════════
#  رايبو-بانل — بوابة MAC شخصية في تلفونك (انت المول!)
#  ── بروتوكول Stalker حقيقي (handshake/profile/account_info/itv)
#  ── قنواتك الحقيقية (حمل اشتراكك M3U داخلها بأمر واحد)
#  ── الماكات انت اللي تسجلها — السكريبت والتطبيق يفحصوها ويلاقوها
#
#  الاستعمال (في تيرميكس):
#    python rabie_panel.py                        ← تشغيل البوابة
#    python rabie_panel.py add 00:1A:79:11:22:33            ← تسجيل ماك
#    python rabie_panel.py add 00:1A:79:11:22:33 2027-06-15 ← تسجيل مع تاريخ
#    python rabie_panel.py del 00:1A:79:11:22:33            ← إلغاء تسجيل
#    python rabie_panel.py block 00:1A:79:44:55:66          ← حظر ماك
#    python rabie_panel.py list                             ← عرض المسجلين
#    python rabie_panel.py m3u http://.../get.php?...       ← تحميل قنواتك الحقيقية
# ═══════════════════════════════════════════════════════════════
import os, sys, json, hashlib, datetime, re
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse, parse_qs, unquote, quote
from urllib.request import Request, urlopen

DIR = os.environ.get("RABIE_PANEL_DIR") or "/sdcard/RabiePanel"
PORT = int(os.environ.get("RABIE_PANEL_PORT") or 8899)
F_MACS = os.path.join(DIR, "macs.txt")
F_BLOCK = os.path.join(DIR, "blocked.txt")
F_M3U = os.path.join(DIR, "panel.m3u")
F_EXP = os.path.join(DIR, "expiry.txt")

DEMO = [
    ("Big Buck Bunny", "http://commondatastorage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4"),
    ("Apple Test HLS", "http://devstreaming-cdn.apple.com/videos/streaming/examples/img_bipbop_adv_example_fmp4/master.m3u8"),
    ("Elephants Dream", "http://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ElephantsDream.mp4"),
    ("For Bigger Blazes", "http://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerBlazes.mp4"),
    ("Sintel", "http://commondatastorage.googleapis.com/gtv-videos-bucket/sample/Sintel.mp4"),
    ("Tears of Steel", "http://commondatastorage.googleapis.com/gtv-videos-bucket/sample/TearsOfSteel.mp4"),
]

def ensure():
    os.makedirs(DIR, exist_ok=True)
    for f in (F_MACS, F_BLOCK, F_EXP):
        if not os.path.exists(f):
            open(f, "w").close()
    if not os.path.exists(F_M3U):
        with open(F_M3U, "w", encoding="utf-8") as w:
            w.write("#EXTM3U\n")
            for n, u in DEMO:
                w.write('#EXTINF:-1,%s\n%s\n' % (n, u))

def norm(mac):
    m = mac.strip().upper()
    if not re.match(r"^[0-9A-F]{2}(:[0-9A-F]{2}){5}$", m):
        return None
    return m

def load_lines(path):
    try:
        return [l.strip() for l in open(path, encoding="utf-8") if l.strip()]
    except Exception:
        return []

def macs_active():
    return [m for m in (norm(l.split(",")[0]) or "" for l in load_lines(F_MACS)) if m]

def macs_blocked():
    return [m for m in (norm(l) or "" for l in load_lines(F_BLOCK)) if m]

def expiry_of(mac):
    for l in load_lines(F_EXP):
        if l.upper().startswith(mac + ","):
            return l.split(",", 1)[1].strip()
    return (datetime.date.today() + datetime.timedelta(days=365)).isoformat()

def user_pass(mac):
    h = hashlib.md5(("p" + mac).encode()).hexdigest()
    return "owner" + h[:6], "P" + h[6:12]

def phone_fmt(iso):
    y, m, d = iso.split("-")
    names = ["January","February","March","April","May","June","July","August","September","October","November","December"]
    mi = max(1, min(12, int(m)))
    return "%s %s, %s, 12:00 pm" % (names[mi-1], int(d), y)

def epoch_of(iso):
    try:
        d = datetime.date(*[int(x) for x in iso.split("-")])
        return int(datetime.datetime(d.year, d.month, d.day, 12).timestamp())
    except Exception:
        return int(datetime.datetime.now().timestamp()) + 31536000

def channels():
    """يقرأ panel.m3u → [(رقم، اسم، رابط)]"""
    out = []
    name = None
    try:
        for l in open(F_M3U, encoding="utf-8"):
            l = l.strip()
            if l.startswith("#EXTINF"):
                name = l.split(",", 1)[1] if "," in l else "ch"
            elif l and not l.startswith("#") and name is not None:
                out.append((len(out) + 1, name, l))
                name = None
    except Exception:
        pass
    return out

def days_left(iso):
    try:
        d = datetime.date(*[int(x) for x in iso.split("-")])
        return (d - datetime.date.today()).days
    except Exception:
        return 0

# ───── أوامر الإدارة ─────
def cmd_add(argv):
    m = norm(argv[0]) if argv else None
    if not m:
        print("❌ ماك غالط — مثال: python rabie_panel.py add 00:1A:79:11:22:33 [2027-06-15]")
        return
    exp = norm_date(argv[1]) if len(argv) > 1 else expiry_of(m)
    if exp is None:
        print("❌ التاريخ غالط — مثال: 2027-06-15")
        return
    ensure()
    cur = [l for l in load_lines(F_MACS) if norm(l.split(",")[0]) != m]
    cur.append(m)
    open(F_MACS, "w").write("\n".join(cur) + "\n")
    ex = [l for l in load_lines(F_EXP) if not l.upper().startswith(m + ",")]
    ex.append(m + "," + exp)
    open(F_EXP, "w").write("\n".join(ex) + "\n")
    print("✅ سجلّيت الماك %s — ينتهي %s (باقي %d يوم)" % (m, exp, days_left(exp)))

def norm_date(s):
    try:
        datetime.date(*[int(x) for x in s.split("-")])
        return s
    except Exception:
        return None

def cmd_del(argv):
    m = norm(argv[0]) if argv else None
    if not m:
        print("❌ مثال: python rabie_panel.py del 00:1A:79:11:22:33")
        return
    ensure()
    cur = [l for l in load_lines(F_MACS) if norm(l.split(",")[0]) != m]
    open(F_MACS, "w").write("\n".join(cur) + "\n")
    print("🗑️ ألغيت الماك %s — توا يبقى «ميت» في الفحص" % m)

def cmd_block(argv):
    m = norm(argv[0]) if argv else None
    if not m:
        print("❌ مثال: python rabie_panel.py block 00:1A:79:44:55:66")
        return
    ensure()
    cur = set(load_lines(F_BLOCK)) | {m}
    open(F_BLOCK, "w").write("\n".join(sorted(cur)) + "\n")
    print("⛔ حظرت الماك %s — يظهر «محجوب» عند الفحص" % m)

def cmd_list():
    ensure()
    act, blk, chs = macs_active(), macs_blocked(), channels()
    print("📋 المسجلين (%d):" % len(act))
    for m in act:
        print("   ✅ %s — ينتهي %s" % (m, expiry_of(m)))
    for m in blk:
        print("   ⛔ %s — محجوب" % m)
    print("📺 القنوات: %d (من panel.m3u)" % len(chs))

def cmd_m3u(argv):
    url = argv[0] if argv else ""
    if not url.startswith("http"):
        print("❌ مثال: python rabie_panel.py m3u http://host:80/get.php?username=..&password=..")
        return
    ensure()
    print("⏳ جاري تحميل قنواتك...")
    req = Request(url, headers={"User-Agent": "okhttp/4.7.1"})
    data = urlopen(req, timeout=60).read()
    open(F_M3U, "wb").write(data)
    n = len(channels())
    print("✅ رحمت %d قناة حقيقية في بوابتك — شغل البوابة وافحصها" % n)

# ───── السيرفر (بروتوكول Stalker) ─────
class Handler(BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def _json(self, code, obj):
        b = json.dumps(obj, separators=(",", ":")).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(b)))
        self.end_headers()
        self.wfile.write(b)

    def _mac(self, q):
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

    def do_GET(self):
        u = urlparse(self.path)
        q = parse_qs(u.query)
        action = (q.get("action") or [""])[0]
        mac = self._mac(q)
        chs = channels()

        # ── /live/user/pass/ID.ts → تحويل للقناة الحقيقية (302) ──
        if u.path.startswith("/live/"):
            parts = u.path.split("/")
            if len(parts) >= 5:
                try:
                    cid = int(parts[4].split(".")[0].split("_")[0])
                except Exception:
                    cid = 1
                url = next((x[2] for x in chs if x[0] == cid), chs[0][2] if chs else None)
                if url:
                    self.send_response(302)
                    self.send_header("Location", url)
                    self.send_header("Content-Length", "0")
                    self.end_headers()
                    return
            self.send_response(404); self.end_headers(); return

        # ── M3U Plus (قنواتك الحقيقية) ──
        if u.path == "/get.php":
            usr = (q.get("username") or ["owner"])[0]
            b = "#EXTM3U\n".encode()
            for num, nm, url in chs:
                b += ('#EXTINF:-1 tvg-id="%d" group-title="RabiePanel",%s\n%s\n' % (num, nm, url)).encode()
            self.send_response(200)
            self.send_header("Content-Type", "audio/x-mpegurl")
            self.send_header("Content-Length", str(len(b)))
            self.end_headers()
            self.wfile.write(b)
            return

        # ── Xtream player_api (للتحقق من اليوزر/الباس المستخرجين) ──
        if u.path == "/player_api.php":
            a = (q.get("action") or [""])[0]
            exp_iso = expiry_of(macs_active()[0]) if macs_active() else expiry_of("00:00:00:00:00:00")
            info = {"username": (q.get("username") or ["owner"])[0],
                    "password": (q.get("password") or ["x"])[0],
                    "message": "", "status": "Active",
                    "exp_date": str(epoch_of(exp_iso)), "is_trial": "0",
                    "active_cons": "0", "max_connections": "1",
                    "created_at": "1730000000",
                    "url": "http://127.0.0.1", "port": str(PORT),
                    "timezone": "Africa/Algiers"}
            if a == "get_live_streams":
                self._json(200, [{"stream_id": n, "name": nm} for n, nm, _ in chs]); return
            if a == "get_vod_streams":
                self._json(200, []); return
            if a == "get_series":
                self._json(200, []); return
            if a == "get_live_categories":
                self._json(200, [{"category_id": 1, "category_name": "RabiePanel"}]); return
            if a == "get_vod_categories":
                self._json(200, []); return
            if a == "get_series_categories":
                self._json(200, []); return
            self._json(200, {"user_info": info}); return

        # ── Stalker: فقط /c/server/load.php ──
        if not (u.path.endswith("/server/load.php") and "/c/" in u.path):
            self._json(404, {"error": "not found"}); return

        if action == "handshake":
            self._json(200, {"js": {"token": "PANELTOKEN" + "0" * 20}}); return

        blk, act = macs_blocked(), macs_active()
        if action == "get_profile":
            if mac in blk:
                js = {"id": 0, "name": 0, "status": 0, "msg": "Your subscription is blocked!"}
            elif mac in act:
                js = {"id": 12345, "name": "paneluser", "status": "Active",
                      "exp_date": "%s 12:00:00" % expiry_of(mac),
                      "last_active": "2026-11-17 00:00:00"}
            else:
                js = {"id": 0, "name": 0, "status": 0,
                      "last_active": "2022-02-18 12:00:00"}
            self._json(200, {"js": js}); return

        if action == "get_main_info":
            if mac in act and mac not in blk:
                self._json(200, {"js": {"mac": mac, "phone": phone_fmt(expiry_of(mac))}})
            else:
                self._json(200, {"js": {}})
            return

        usr, pas = user_pass(mac or "00:00:00:00:00:00")
        if action == "get_ordered_list":
            self._json(200, {"js": [{"cmd": "ffmpeg http://127.0.0.1:%d/movie/%s/%s/1.mkv" % (PORT, usr, pas), "id": 1}]}); return

        if action == "create_link":
            cmd = (q.get("cmd") or [""])[0]
            m = re.search(r"/ch/(\d+)", cmd)
            cid = int(m.group(1)) if m else 1
            link = "ffmpeg http://127.0.0.1:%d/live/%s/%s/%d.ts" % (PORT, usr, pas, cid)
            self._json(200, {"js": {"cmd": link, "id": cid}}); return

        if action == "get_all_channels":
            self._json(200, {"js": [{"ch_id": str(n), "num": str(n), "name": nm,
                                     "cmd": "ffmpeg http://localhost/ch/%d_" % n} for n, nm, _ in chs]}); return

        if action == "get_genres":
            self._json(200, {"js": [{"id": 1, "title": "RabiePanel"}, {"id": 2, "title": "MyChannels"}]}); return

        self._json(404, {"error": "bad action"})


def main():
    argv = [a for a in sys.argv[1:]]
    if not argv:
        ensure()
        act, chs = macs_active(), channels()
        print("✅ بوابتك الشخصية تعمل على المنفذ %d — ما تسدش هذا التيرميكس" % PORT, flush=True)
        print("   📺 القنوات: %d · ✅ الماكات المسجلة: %d" % (len(chs), len(act)), flush=True)
        print("   فحصها من السكريبت: PANEL = 127.0.0.1:%d" % PORT, flush=True)
        ThreadingHTTPServer(("0.0.0.0", PORT), Handler).serve_forever()
        return
    c, rest = argv[0], argv[1:]
    if c == "add": cmd_add(rest)
    elif c == "del": cmd_del(rest)
    elif c == "block": cmd_block(rest)
    elif c == "list": cmd_list()
    elif c == "m3u": cmd_m3u(rest)
    else:
        print("الأوامر: add / del / block / list / m3u — أو بلا أوامر = تشغيل البوابة")

if __name__ == "__main__":
    main()
