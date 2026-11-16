import os
import sys
import re
import json
import datetime
import requests
from urllib.parse import urlparse, parse_qs
from requests.packages.urllib3.exceptions import InsecureRequestWarning

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

if sys.platform.startswith("win"):
    import ctypes
    M3U_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "M3U")
    SAVE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "results")
else:
    M3U_DIR = "/storage/emulated/0/M3U"
    SAVE_DIR = "/storage/emulated/0/results"

os.makedirs(SAVE_DIR, exist_ok=True)
os.makedirs(M3U_DIR, exist_ok=True)


def parse_m3u_url(m3u_url):
    m3u_url = m3u_url.strip().strip('"').strip("'")
    if not m3u_url.startswith("http"):
        m3u_url = "http://" + m3u_url
    parsed = urlparse(m3u_url)
    params = parse_qs(parsed.query)
    username = params.get("username", [None])[0]
    password = params.get("password", [None])[0]
    hostname = parsed.hostname
    scheme = parsed.scheme
    port = parsed.port or (80 if scheme == "http" else 443)
    server = f"{hostname}:{port}" if parsed.port else hostname
    return server, hostname, port, scheme, username, password, m3u_url


def get_player_api(server, port, username, password, scheme="http"):
    for proto in [scheme, "http", "https"]:
        url = f"{proto}://{server}/player_api.php?username={username}&password={password}"
        try:
            resp = requests.get(url, timeout=10, verify=False, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"})
            if resp.status_code == 200:
                try:
                    return resp.json()
                except json.JSONDecodeError:
                    return resp.text
        except requests.RequestException:
            pass
    return None


def get_content_list(server, username, password, action, scheme="http"):
    for proto in [scheme, "http", "https"]:
        url = f"{proto}://{server}/player_api.php?username={username}&password={password}&action={action}"
        try:
            resp = requests.get(url, timeout=15, verify=False, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"})
            if resp.status_code == 200:
                data = resp.json()
                if isinstance(data, list):
                    return data
                if isinstance(data, dict):
                    return data.get("data", data)
        except:
            pass
    return []


def get_content_count(server, username, password, action, scheme="http"):
    items = get_content_list(server, username, password, action, scheme)
    return len(items)


def format_date(timestamp):
    try:
        ts = int(timestamp)
        if ts == 0:
            return "Unlimited"
        return datetime.datetime.fromtimestamp(ts).strftime("%Y-%m-%d %H:%M:%S")
    except:
        return str(timestamp)


def check_m3u_url(m3u_url):
    server, hostname, port, scheme, username, password, raw_url = parse_m3u_url(m3u_url)
    if not username or not password:
        print("  [!] Could not extract username/password from URL")
        return None

    print(f"  Server: {server}")
    print(f"  Username: {username}")
    print(f"  Password: {password}")

    data = get_player_api(server, port, username, password, scheme)
    if data is None:
        print("  [!] Failed to connect to player_api.php")
        return None

    user_info = {}
    server_info = {}
    if isinstance(data, dict):
        user_info = data.get("user_info", data)
        server_info = data.get("server_info", {})
    elif isinstance(data, str):
        if '"status":"Active"' in data or '"status": "Active"' in data:
            user_info = {"status": "Active"}
        else:
            print("  [!] Invalid response from server")
            return None

    status = user_info.get("status", "N/A")
    exp_date = user_info.get("exp_date", "0")
    max_conn = user_info.get("max_connections", "N/A")
    active_cons = user_info.get("active_cons", "N/A")
    created_at = user_info.get("created_at", "0")
    auth = user_info.get("auth", 1)
    is_trial = user_info.get("is_trial", "0")

    sv_url = server_info.get("url", hostname)
    sv_port = server_info.get("port", str(port))
    https_port = server_info.get("https_port", "N/A")
    rtmp_port = server_info.get("rtmp_port", "N/A")
    protocol = server_info.get("server_protocol", "N/A")
    timezone = server_info.get("timezone", "N/A")
    time_now = server_info.get("time_now", "N/A")

    live_categories = get_content_list(server, username, password, "get_live_categories", scheme)
    live_channels = get_content_list(server, username, password, "get_live_streams", scheme)
    live_count = len(live_channels)
    vod_count = get_content_count(server, username, password, "get_vod_streams", scheme)
    series_count = get_content_count(server, username, password, "get_series", scheme)

    base = f"{scheme}://{server}"
    m3u_link = f"{base}/get.php?username={username}&password={password}&type=m3u_plus"
    m3u_link_hd = f"{base}/get.php?username={username}&password={password}&type=m3u_plus&output=ts"

    result = {
        "url": raw_url,
        "server": server,
        "hostname": hostname,
        "port": port,
        "username": username,
        "password": password,
        "status": status,
        "auth": auth,
        "is_trial": is_trial,
        "created_at": format_date(created_at),
        "exp_date": format_date(exp_date),
        "max_connections": max_conn,
        "active_cons": active_cons,
        "server_url": sv_url if sv_url else hostname,
        "server_port": sv_port,
        "https_port": https_port,
        "rtmp_port": rtmp_port,
        "protocol": protocol,
        "timezone": timezone,
        "time_now": time_now,
        "live_categories": live_categories,
        "live_channels": live_channels,
        "live_count": live_count,
        "vod_count": vod_count,
        "series_count": series_count,
        "m3u_link": m3u_link,
        "m3u_link_hd": m3u_link_hd,
    }
    return result


def display_result(r):
    status_icon = "ACTIVE" if r["status"] == "Active" else "INACTIVE"
    print(f"\n{'='*60}")
    print(f"  M3U Account Details")
    print(f"{'='*60}")
    print(f"  Status      : {status_icon}")
    print(f"  Username    : {r['username']}")
    print(f"  Password    : {r['password']}")
    print(f"  Server      : {r['server']}")
    print(f"  Created     : {r['created_at']}")
    print(f"  Expires     : {r['exp_date']}")
    print(f"  Max Conns   : {r['max_connections']}")
    print(f"  Active Conns: {r['active_cons']}")
    print(f"  Auth        : {r['auth']}")
    print(f"  Trial       : {r['is_trial']}")
    print(f"{'─'*60}")
    print(f"  Server URL  : {r['server_url']}")
    print(f"  Server Port : {r['server_port']}")
    print(f"  HTTPS Port  : {r['https_port']}")
    print(f"  RTMP Port   : {r['rtmp_port']}")
    print(f"  Protocol    : {r['protocol']}")
    print(f"  Timezone    : {r['timezone']}")
    print(f"  Server Time : {r['time_now']}")
    print(f"{'─'*60}")
    print(f"  Live TV     : {r['live_count']}")
    print(f"  VOD         : {r['vod_count']}")
    print(f"  Series      : {r['series_count']}")
    print(f"{'─'*60}")
    keywords = ["IN ", "IN-", "IND", "ASIA", "INDIA", "AS "]
    if r["live_categories"]:
        cats = []
        for cat in r["live_categories"]:
            if isinstance(cat, dict):
                cats.append(cat)
            elif isinstance(cat, str):
                cats.append({"category_name": cat, "category_id": ""})
        filtered = [cat for cat in cats if any(k.lower() in cat.get("category_name", "").lower() for k in keywords)]
        if filtered:
            print(f"  Matched Groups ({len(filtered)}):")
            for cat in filtered:
                name = cat.get("category_name", "?")
                cid = cat.get("category_id", "")
                print(f"    [{cid}] {name}")
        else:
            print(f"  Channel Groups: (no matches)")
        print(f"  (Total groups: {len(r['live_categories'])})")
    else:
        print(f"  Channel Groups: (none)")
    print(f"{'─'*60}")
    print(f"  M3U Link    : {r['m3u_link']}")
    print(f"  M3U HD Link : {r['m3u_link_hd']}")
    print(f"{'='*60}\n")


def save_result(r):
    safe = re.sub(r'[\\/*?:"<>|]', "_", f"{r['hostname']}_{r['username']}")
    filename = os.path.join(SAVE_DIR, f"{safe}.txt")
    with open(filename, "w", encoding="utf-8") as f:
        f.write(f"M3U Account Details\n")
        f.write(f"{'='*60}\n")
        f.write(f"URL         : {r['url']}\n")
        f.write(f"Status      : {r['status']}\n")
        f.write(f"Username    : {r['username']}\n")
        f.write(f"Password    : {r['password']}\n")
        f.write(f"Server      : {r['server']}\n")
        f.write(f"Created     : {r['created_at']}\n")
        f.write(f"Expires     : {r['exp_date']}\n")
        f.write(f"Max Conns   : {r['max_connections']}\n")
        f.write(f"Active Conns: {r['active_cons']}\n")
        f.write(f"Auth        : {r['auth']}\n")
        f.write(f"Trial       : {r['is_trial']}\n")
        f.write(f"{'─'*60}\n")
        f.write(f"Server URL  : {r['server_url']}\n")
        f.write(f"Server Port : {r['server_port']}\n")
        f.write(f"HTTPS Port  : {r['https_port']}\n")
        f.write(f"RTMP Port   : {r['rtmp_port']}\n")
        f.write(f"Protocol    : {r['protocol']}\n")
        f.write(f"Timezone    : {r['timezone']}\n")
        f.write(f"Server Time : {r['time_now']}\n")
        f.write(f"{'─'*60}\n")
        f.write(f"Live TV     : {r['live_count']}\n")
        f.write(f"VOD         : {r['vod_count']}\n")
        f.write(f"Series      : {r['series_count']}\n")
        keywords = ["IN ", "IN-", "IND", "ASIA", "INDIA", "AS "]
        cats = [{"category_name": c, "category_id": ""} if isinstance(c, str) else c for c in r["live_categories"] if isinstance(c, (dict, str))]
        filtered = [cat for cat in cats if any(k.lower() in cat.get("category_name", "").lower() for k in keywords)]
        f.write(f"{'─'*60}\n")
        f.write(f"Matched Channel Groups:\n")
        for cat in filtered:
            name = cat.get("category_name", "?")
            cid = cat.get("category_id", "")
            f.write(f"  [{cid}] {name}\n")
        f.write(f"{'─'*60}\n")
        f.write(f"M3U Link    : {r['m3u_link']}\n")
        f.write(f"M3U HD Link : {r['m3u_link_hd']}\n")
        f.write(f"{'='*60}\n")
    print(f"  [Saved to {filename}]")


def extract_m3u_urls(text):
    pattern = re.compile(
        r'(https?://[^\s\'">]+?(?:username|user)=[^\s\'">]+?(?:password|pass|passwd)=[^\s\'">]+)',
        re.IGNORECASE
    )
    return [m.group(1) for m in pattern.finditer(text)]


def load_split_format_from_file():
    if not os.path.isdir(M3U_DIR):
        print(f"[!] Directory not found: {M3U_DIR}")
        return []

    txt_files = [f for f in os.listdir(M3U_DIR) if f.endswith(".txt")]
    if not txt_files:
        print(f"[!] No .txt files found in {M3U_DIR}")
        return []

    print(f"\nFiles in {M3U_DIR}:")
    for i, fname in enumerate(txt_files, 1):
        print(f"  {i}. {fname}")
    print()

    while True:
        try:
            choice = input("Select file number (0 to cancel): ").strip()
            if choice == "0":
                return []
            idx = int(choice) - 1
            if 0 <= idx < len(txt_files):
                break
            else:
                print(f"Enter 1-{len(txt_files)}")
        except ValueError:
            print("Enter a valid number")

    filepath = os.path.join(M3U_DIR, txt_files[idx])
    with open(filepath, "r", encoding="utf-8") as f:
        lines = [line.strip() for line in f]

    urls = []
    current_server = None
    current_user = None
    current_pass = None

    for line in lines:
        if not line or line.startswith("#"):
            continue
        lower = line.lower()
        if lower.startswith("http"):
            if current_server and current_user and current_pass:
                urls.append(f"{current_server}/get.php?username={current_user}&password={current_pass}&type=m3u_plus")
            current_server = line.rstrip("/")
            current_user = None
            current_pass = None
        elif lower.startswith("user") or lower.startswith("username"):
            current_user = line.split("=", 1)[1].strip() if "=" in line else None
        elif lower.startswith("pass") or lower.startswith("password") or lower.startswith("passwd"):
            current_pass = line.split("=", 1)[1].strip() if "=" in line else None

    if current_server and current_user and current_pass:
        urls.append(f"{current_server}/get.php?username={current_user}&password={current_pass}&type=m3u_plus")

    print(f"  Parsed {len(urls)} M3U URL(s) from {txt_files[idx]}")
    return urls


def load_urls_from_file():
    if not os.path.isdir(M3U_DIR):
        print(f"[!] Directory not found: {M3U_DIR}")
        return []

    txt_files = [f for f in os.listdir(M3U_DIR) if f.endswith(".txt")]
    if not txt_files:
        print(f"[!] No .txt files found in {M3U_DIR}")
        return []

    print(f"\nFiles in {M3U_DIR}:")
    for i, fname in enumerate(txt_files, 1):
        print(f"  {i}. {fname}")
    print()

    while True:
        try:
            choice = input("Select file number (0 to cancel): ").strip()
            if choice == "0":
                return []
            idx = int(choice) - 1
            if 0 <= idx < len(txt_files):
                break
            else:
                print(f"Enter 1-{len(txt_files)}")
        except ValueError:
            print("Enter a valid number")

    filepath = os.path.join(M3U_DIR, txt_files[idx])
    with open(filepath, "r", encoding="utf-8") as f:
        raw = f.read()
    urls = extract_m3u_urls(raw)
    print(f"  Loaded {len(urls)} URL(s) from {txt_files[idx]}")
    return urls


def is_valid_m3u_url(url):
    return bool(extract_m3u_urls(url))


def main():
    if sys.platform.startswith("win"):
        ctypes.windll.kernel32.SetConsoleTitleW("M3U URL Checker")
    else:
        sys.stdout.write("\x1b]2;M3U URL Checker\x07")
    print("M3U URL Checker")
    print("=" * 40)

    while True:
        print("\nSource:")
        print("  1. Enter URL(s) directly")
        print("  2. Load M3U URLs from file in ../M3U/")
        print("  3. Load server+user/pass file from ../M3U/")
        print("  4. Exit")
        choice = input("Choice (1-4): ").strip()

        urls = []
        if choice == "1":
            print("\nEnter M3U URL(s) (one per line, empty line to finish):")
            while True:
                line = input().strip()
                if not line:
                    break
                found = extract_m3u_urls(line)
                if found:
                    urls.extend(found)
                else:
                    print(f"  [!] No valid M3U URL found in: {line[:60]}")
        elif choice == "2":
            urls = load_urls_from_file()
            if not urls:
                continue
        elif choice == "3":
            urls = load_split_format_from_file()
            if not urls:
                continue
        elif choice == "4":
            print("Exiting.")
            break
        else:
            print("Invalid choice")
            continue

        if not urls:
            print("No URLs to check.")
            continue

        print(f"\nChecking {len(urls)} URL(s)...")
        results = []
        for i, url in enumerate(urls, 1):
            print(f"\n[{i}/{len(urls)}] Checking: {url[:80]}...")
            r = check_m3u_url(url)
            if r:
                display_result(r)
                results.append(r)
            else:
                print("  [No result]\n")

        if results:
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            summary_file = os.path.join(SAVE_DIR, f"summary_{timestamp}.txt")
            with open(summary_file, "w", encoding="utf-8") as f:
                for r in results:
                    f.write(f"URL         : {r['url']}\n")
                    f.write(f"Status      : {r['status']}\n")
                    f.write(f"Username    : {r['username']}\n")
                    f.write(f"Password    : {r['password']}\n")
                    f.write(f"Server      : {r['server']}\n")
                    f.write(f"Created     : {r['created_at']}\n")
                    f.write(f"Expires     : {r['exp_date']}\n")
                    f.write(f"Max Conns   : {r['max_connections']}\n")
                    f.write(f"Active Conns: {r['active_cons']}\n")
                    f.write(f"Live TV     : {r['live_count']}\n")
                    f.write(f"VOD         : {r['vod_count']}\n")
                    f.write(f"Series      : {r['series_count']}\n")
                    keywords = ["IN ", "IN-", "IND", "ASIA", "INDIA", "AS "]
                    cats = [{"category_name": c, "category_id": ""} if isinstance(c, str) else c for c in r["live_categories"] if isinstance(c, (dict, str))]
                    filtered = [cat for cat in cats if any(k.lower() in cat.get("category_name", "").lower() for k in keywords)]
                    f.write(f"{'─'*60}\n")
                    f.write(f"Matched Channel Groups:\n")
                    for cat in filtered:
                        name = cat.get("category_name", "?")
                        cid = cat.get("category_id", "")
                        f.write(f"  [{cid}] {name}\n")
                    f.write(f"{'─'*60}\n")
                    f.write(f"M3U Link    : {r['m3u_link']}\n")
                    f.write(f"{'='*60}\n")
            print(f"\n[+] All {len(results)} result(s) saved to {summary_file}")
        else:
            print("\n[!] No valid results to save.")

        again = input("\nCheck another set? (y/n): ").strip().lower()
        if again != "y":
            print("Exiting.")
            break


if __name__ == "__main__":
    main()
