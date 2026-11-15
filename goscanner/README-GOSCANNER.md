# ⚡ GO STALKER PRO v2 — النسخة المصلحة

فاحص MACات لبواباتك أنت — v2.1: إصلاحات v2 + 3 إضافات:
- إزالة Accept-Encoding اليدوي (كان يجعل Go يقرأ gzip كنص → «Network Errors» وهمية على البوابات الحقيقية)
- حارس الملفات الشبح (id:0 بلا تاريخ ≠ HIT — البوابات تعطي ملفاً فارغاً لأي MAC)
- طباعة سبب فشل أول 20 MAC (ترى "status code: X" أو السبب الحقيقي)

| العيب | التأثير | الإصلاح |
|---|---|---|
| 🔴 Deadlock: العمال تُشغَّل بعد انتظار القارئ | قائمة >5000 MAC = تجمّد كامل بلا رسالة | العمال أولاً ثم القارئ بالتوازي |
| 🔴 مسار /c غير مُكتشف | بواباتك (…:80/c) تعطي Network Errors للجميع | يجرب base+/c تلقائياً + /c/server/load.php |
| 🟠 HIT وهمي | الرد المقفول (js.msg) كان يُحسب HIT | فحص msg + عدّ القنوات فعلياً (get_all_channels) |
| 🟠 إحصائيات مخدوعة | token not found = Network Error | Auth Failures منفصلة |

## نتائج الاختبار الحي (سيرفر وهمي + 6000 MAC)
- 2 HITs حقيقية: `Expire: 2027-05-03 | Remaining: 168 Days | Channels: 42`
- المقفول: لا يُحسب HIT (Blocked/Invalid: 1)
- 6000 MAC: اكتملت في 8 ثوانٍ — صفر تجمّد

## التشغيل
```bash
go build -o goscanner main.go
./goscanner
# Portal URL: اكتب بوابتك كما هي — بـ/c أو بدونها (يكتشفها تلقائياً)
# Mac List: macs.txt (سطر لكل MAC: 00:1A:79:XX:XX:XX)
# Proxy: n (أو y+ملف بروكسي)
# Threads: 50-200
```
النتائج في `Hits/go_hits.txt`


## v2.2 — إعادة المحاولة عند 429 (Rate-Limit)
- كل الطلبات تعيد المحاولة تلقائياً حتى 3 مرات عند HTTP 429/503 مع احترام ترويسة Retry-After (handshake / get_profile / get_all_channels / player_api / اكتشاف endpoints)
- عند استمرار 429 بعد المحاولات يظهر السبب: `[i] MAC → profile: status code: 429 (rate limited, retried 2 times)`
- البانر يعرض v2.2 للتأكد أن التحديث دخل للهاتف
