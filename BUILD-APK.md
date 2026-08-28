# ساخت APK اپ درخشا — راهنمای کامل

## چرا اینجا APK ساخته نشد؟
- برای ساخت APK به **Android SDK** و **Android Studio** نیاز است (در سرور فعلی موجود نیست).
- برای PWABuilder باید اپ روی یک آدرس **HTTPS عمومی** باشد (مثل GitHub Pages).
- دسترسی به اکانت GitHub شما برای publish وجود ندارد.

---

## روش پیشنهادی A — PWABuilder (ساده‌ترین، بدون نصب Android Studio)

### مرحله ۱: انتشار روی GitHub Pages
1. برو به https://github.com/new
2. نام ریپو مثلاً: `DerakhshaAI` یا `derakhsha-app`
3. همه فایل‌های داخل این پوشه را آپلود کن (به‌جز `node_modules` اگر بود)
4. Settings → Pages → Source: Deploy from branch → `main` / root
5. آدرس نهایی چیزی شبیه این می‌شود:
   `https://YOUR_USERNAME.github.io/DerakhshaAI/`

### مرحله ۲: تبدیل به APK
1. برو به **https://www.pwabuilder.com**
2. همان آدرس GitHub Pages را وارد کن
3. Package for stores → Android → Generate
4. Package name: `com.derakhsha.app`
5. App name: `درخشا`
6. Download — فایل APK/AAB را بگیر

---

## روش پیشنهادی B — Capacitor + Android Studio (کنترل بیشتر)

روی کامپیوتر خودت (ویندوز/مک/لینوکس):

```bash
# 1. نصب Node.js از nodejs.org اگر نداری

# 2. داخل پوشه اپ
cd derakhsha-webapp

npm init -y
npm install @capacitor/core @capacitor/cli @capacitor/android

npx cap init "درخشا" com.derakhsha.app --web-dir .
# اگر capacitor.config.json از قبل هست، init را رد کن

npx cap add android
npx cap sync
npx cap open android
```

در Android Studio:
- Build → Build Bundle(s) / APK(s) → Build APK(s)
- خروجی: `android/app/build/outputs/apk/debug/app-debug.apk`

---

## اطلاعات آماده برای فرم‌ها

| فیلد | مقدار پیشنهادی |
|------|----------------|
| App name | درخشا |
| Package / Application ID | com.derakhsha.app |
| Theme color | #09090b |
| Background | #09090b |
| Start URL | ./index.html |
| Display | standalone |
| Icons | icon-192.png و icon-512.png (داخل پوشه) |

---

## بعد از گرفتن APK
- روی گوشی: Settings → امنیت → نصب از منابع ناشناس را روشن کن
- فایل APK را باز کن و نصب کن

برای انتشار در بازار / مایکت / گوگل‌پلی باید نسخه **Release امضاشده** بسازی.
