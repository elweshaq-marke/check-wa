# WhatsApp Number Checker API

نظام متكامل لفحص أرقام WhatsApp مع واجهة سطح المكتب وبوت تيليجرام.

## ✨ المميزات

- ✅ فحص أرقام WhatsApp (مسجل/غير مسجل)
- 📤 رفع جلسة WhatsApp موجودة
- 🔐 إنشاء جلسة جديدة بـ Pairing Code
- 🤖 بوت تيليجرام للتحكم والإشعارات
- 🌐 واجهة ويب
- 💻 تطبيق سطح المكتب (Flet)
- 📊 إحصائيات في الوقت الفعلي
- 🌍 رابط عام ثابت (Cloudflare Tunnel)

## 🚀 التشغيل السريع

### الطريقة 1: تطبيق سطح المكتب
```bash
python desktop_app.py
```
اضغط زر "Start" وكل شيء يعمل تلقائيًا!

### الطريقة 2: عبر الطرفية
```bash
python run_bot.py
```

## 📦 ما يحدث تلقائيًا عند التشغيل:

1. ✅ تحميل Node.js (إذا لم يكن مثبت)
2. ✅ تحميل cloudflared (للتنل)
3. ✅ تشغيل WhatsApp Server
4. ✅ تشغيل API Server
5. ✅ تشغيل Cloudflare Tunnel → https://checkwa.elwe.qzz.io
6. ✅ تشغيل Telegram Bot

## 🤖 البوت على تيليجرام

**الأدمن:** 7011309417

**الأوامر:**
- `/start` - القائمة الرئيسية
- ✅ فحص رقم
- 📤 رفع جلسة
- 🔐 إنشاء جلسة
- 📊 الإحصائيات
- 📡 حالة السيرفر

## 🌐 الرابط العام الثابت

**https://checkwa.elwe.qzz.io**

الرابط ده ثابت ويشتغل تلقائيًا مع البرنامج.

## 📡 API Endpoints

### POST /check
فحص رقم WhatsApp
```json
{
  "phoneNumber": "+1234567890"
}
```

### POST /create-session
إنشاء جلسة جديدة
```json
{
  "phoneNumber": "+1234567890"
}
```

### POST /upload-session
رفع ملف جلسة

### GET /stats
الإحصائيات

### GET /whatsapp-status
حالة الاتصال

## 🏗️ بناء ملف EXE

### GitHub Actions (تلقائي):
```bash
git push origin main
```
ثم حمّل الملف من تبويب Actions.

### يدوي:
```bash
pyinstaller --onefile --windowed \
  --name "WhatsAppChecker" \
  --add-data "whatsapp_server.js:." \
  --add-data "api_server.py:." \
  --add-data "telegram_bot.py:." \
  --add-data "setup_dependencies.py:." \
  --add-data "static:static" \
  desktop_app.py
```

## 📁 بنية المشروع

```
├── whatsapp_server.js       # سيرفر WhatsApp (Node.js + Baileys)
├── api_server.py            # API Server (FastAPI)
├── telegram_bot.py          # بوت تيليجرام
├── desktop_app.py           # تطبيق سطح المكتب (Flet)
├── setup_dependencies.py    # تحميل وتثبيت المتطلبات تلقائيًا
├── run_bot.py              # تشغيل كل شيء
├── static/                 # واجهة الويب
└── .github/workflows/      # GitHub Actions
```

## 🔧 المتطلبات

**يتم تحميلها تلقائيًا:**
- Node.js (portable)
- cloudflared

**Python packages:**
- flet
- fastapi
- uvicorn
- python-telegram-bot
- aiohttp
- python-multipart
- qrcode
- pillow

## 🔐 الأمان

- جميع الأسرار والتوكنات مدمجة بأمان
- الجلسات محفوظة محليًا في `auth_info_baileys/`
- البوت يعمل فقط للأدمن المحدد

## 📝 ملاحظات

- البرنامج يحمل كل المتطلبات تلقائيًا عند أول تشغيل
- التنل الثابت يشتغل تلقائي
- البوت يرسل إشعارات لكل عملية
- الإحصائيات تُحفظ في الذاكرة وتُعاد عند كل تشغيل

## 📞 الدعم

للتواصل عبر تيليجرام: 7011309417

---

Made with ❤️ for WhatsApp number verification
