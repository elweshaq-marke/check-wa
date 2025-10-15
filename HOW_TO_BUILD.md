# كيفية بناء ملف EXE

## 🤖 طريقة 1: GitHub Actions (أوتوماتيك)

عند رفع الكود على GitHub، الـ workflow يشتغل تلقائيًا ويبني ملف exe.

### الخطوات:
1. **Push الكود على GitHub:**
   ```bash
   git add .
   git commit -m "Build desktop app"
   git push origin main
   ```

2. **اذهب لـ GitHub Repository** → تبويب **Actions**

3. **انتظر اكتمال Build**

4. **حمّل ملف EXE:**
   - اضغط على الـ workflow المكتمل
   - في قسم "Artifacts" حمّل:
     - `WhatsAppChecker-Windows.exe` (لـ Windows)
     - `WhatsAppChecker-Linux` (لـ Linux)

## 💻 طريقة 2: Build يدوي (Local)

### Windows:
```bash
# ثبت PyInstaller
pip install pyinstaller

# اعمل Build
pyinstaller --onefile --windowed ^
  --name "WhatsAppChecker" ^
  --add-data "whatsapp_server.js;." ^
  --add-data "api_server.py;." ^
  --add-data "telegram_bot.py;." ^
  --add-data "static;static" ^
  desktop_app.py

# الملف هيكون في: dist/WhatsAppChecker.exe
```

### Linux:
```bash
# ثبت PyInstaller
pip install pyinstaller

# اعمل Build
pyinstaller --onefile \
  --name "WhatsAppChecker" \
  --add-data "whatsapp_server.js:." \
  --add-data "api_server.py:." \
  --add-data "telegram_bot.py:." \
  --add-data "static:static" \
  desktop_app.py

# الملف هيكون في: dist/WhatsAppChecker
```

## 📦 متطلبات التشغيل

**لا يوجد! 🎉**

البرنامج يحمل ويثبت كل شيء تلقائيًا:
- ✅ Node.js (portable version)
- ✅ cloudflared (للتنل)

## 🚀 تشغيل الملف

1. **Windows:**
   - Double-click على `WhatsAppChecker.exe`

2. **Linux:**
   ```bash
   chmod +x WhatsAppChecker
   ./WhatsAppChecker
   ```

## 📝 ملاحظات مهمة

- الملف exe يحتوي على:
  - Desktop App (Flet GUI)
  - WhatsApp Server
  - API Server
  - Telegram Bot
  - Static files (web interface)

- **التنل** يحتاج cloudflared مثبت منفصل
- **Node.js** يجب أن يكون مثبت على الجهاز المستهدف
- **الجلسات** تُحفظ في مجلد `auth_info_baileys`

## 🔧 إضافة أيقونة (اختياري)

```bash
pyinstaller --onefile --windowed \
  --name "WhatsAppChecker" \
  --icon="icon.ico" \
  --add-data "whatsapp_server.js:." \
  desktop_app.py
```
