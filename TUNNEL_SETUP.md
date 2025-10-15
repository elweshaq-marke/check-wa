# إعداد Cloudflare Tunnel

## ✅ التنل الثابت - Automatic

النظام الآن يشتغل التنل تلقائيًا عند التشغيل!

### 🌐 الرابط العام الثابت:
**https://checkwa.elwe.qzz.io**

### كيف يعمل:
1. عند تشغيل `python run_bot.py` التنل يشتغل تلقائي
2. عند تشغيل التطبيق Desktop والضغط على زر Start، التنل يشتغل تلقائي
3. الـ hostname ثابت: **checkwa.elwe.qzz.io**

## تثبيت Cloudflared (إذا لم يكن مثبت)

### Linux:
```bash
wget https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64
chmod +x cloudflared-linux-amd64
sudo mv cloudflared-linux-amd64 /usr/local/bin/cloudflared
```

### Windows:
قم بتحميل من: https://github.com/cloudflare/cloudflared/releases

## كيف يعمل النظام:

### 1. عند التشغيل المحلي (الحالي):
- الـ API يعمل على localhost:5000
- يمكن الوصول له فقط من السيرفر نفسه
- البوت يعمل ويرسل رسائل للأدمن

### 2. عند تشغيل التنل:
- Cloudflare يعمل tunnel للـ localhost:5000
- يعطيك رابط عام مثل: https://xxx.trycloudflare.com
- يمكن استخدام هذا الرابط من أي مكان
- البوت يظل يعمل عادي

### 3. استخدام البوت:
افتح تيليجرام وابحث عن البوت الخاص بك
أرسل `/start` للبوت
سيظهر لك القائمة:
- ✅ Check Number - فحص رقم
- 📤 Upload Session - رفع جلسة
- 🔐 Create Session - إنشاء جلسة جديدة
- 📊 Statistics - الإحصائيات
- 📡 Server Status - حالة السيرفر

## معلومات التنل:
- **Tunnel ID**: bc9c6f68-4eb3-4a05-a9b3-0a7a842a71e1
- **Token**: eyJhIjoiOGZiYzg1NDYzOGU2MjE4YWRjYWQwMWM5NDA3NDU3MjUiLCJ0IjoiYmM5YzZmNjgtNGViMy00YTA1LWE5YjMtMGE3YTg0MmE3MWUxIiwicyI6Ik9ETmhZMlV3TVRjdE16STFOUzAwTWpabUxXRXhOekV0TkdJd01UTm1aVGM1TnpoayJ9

## ملاحظات مهمة:
1. البوت يرسل إشعارات تلقائية للأدمن عند كل عملية
2. جميع الإحصائيات تُحفظ وتُعرض في البوت
3. يمكن استخدام الواجهة الويب أيضًا على نفس الرابط
4. البوت يعمل فقط للأدمن (ID: 7011309417)
