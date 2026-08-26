# استقرار درخشا روی VPS + دامنه (ایران)

سازندگان مفهومی: **گروک** × **احمدرضا ایزدی**

## محتویات

```
derakhsha_vps/
├── app.py                 # FastAPI
├── requirements.txt
├── derakhsha/             # موتور (قشر زبان، درخت، یادگیری، کشف واژه، گفتگو)
├── static/
│   ├── index.html         # سایت کاربر
│   └── admin.html         # پنل مدیریت
├── data/                  # حافظه واژگان (ساخته می‌شود)
└── deploy/
    ├── install.sh
    ├── derakhsha.service
    └── nginx.conf
```

## آدرس‌ها بعد از نصب

| مسیر | توضیح |
|------|--------|
| `/` | سایت کاربر (گفتگو) |
| `/admin` | پنل مدیریت |
| `/api/chat` | API گفتگو |
| `/api/health` | سلامت |
| `/docs` | Swagger |

## نصب سریع

```bash
# روی سرور اوبونتو
cd /tmp
# آپلود یا git clone پروژه
cd derakhsha_vps
sudo bash deploy/install.sh
```

کلید ادمین در خروجی install چاپ می‌شود.

## دامنه

1. DNS دامنه `.ir` را به IP سرور بزنید (A record)
2. فایل `deploy/nginx.conf` را ویرایش و `your-domain.ir` را عوض کنید
3. فعال‌سازی nginx:

```bash
sudo cp deploy/nginx.conf /etc/nginx/sites-available/derakhsha
sudo nano /etc/nginx/sites-available/derakhsha   # دامنه
sudo ln -sf /etc/nginx/sites-available/derakhsha /etc/nginx/sites-enabled/
sudo nginx -t && sudo systemctl reload nginx
```

4. SSL (اختیاری با certbot):

```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.ir
```

## متغیرهای محیطی

در `/etc/systemd/system/derakhsha.service`:

- `DERAKHSHA_ADMIN_KEY` — کلید پنل مدیریت
- `PORT` — پیش‌فرض 8000
- `CORS_ORIGINS` — پیش‌فرض `*`

```bash
sudo systemctl restart derakhsha
sudo systemctl status derakhsha
```

## پنل مدیریت

1. باز کنید: `https://your-domain.ir/admin`
2. کلید ادمین را وارد کنید
3. سند/مقاله اضافه کنید، واژه‌های کشف‌شده و شاخه‌ها را ببینید

## موتور (معماری فعال)

- قشر زبان + واژگان فعل/اسم
- درخت دانش
- یادگیری سند
- پیوند گفتگو
- کشف واژه جدید + حافظه + ذخیره درخت
- امتیاز اطمینان و اولویت منبع

## اجرای محلی تست

```bash
cd derakhsha_vps
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
export DERAKHSHA_ADMIN_KEY=test-key
uvicorn app:app --reload --port 8000
```

سایت: http://127.0.0.1:8000  
پنل: http://127.0.0.1:8000/admin (کلید: test-key)

## پنل مدیریت — ورود دانش (نسخه ۱)

### بخش ۱ — دانش کوتاه
- موضوع + کلیدواژه + جمله
- API: `POST /api/admin/learn-seed`
- مناسب تعریف‌ها و نکات کوتاه

### بخش ۲ — متن بلند / کتاب / مقاله
- عنوان + نوع + متن کامل
- API: `POST /api/admin/learn`
- بخش‌بندی، طبقه‌بندی شاخه، کشف واژه جدید

هر دو نیاز به هدر دارند:
`X-Admin-Key: <DERAKHSHA_ADMIN_KEY>`
