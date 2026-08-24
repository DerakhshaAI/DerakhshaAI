# موتور درخشا — Railway

هوش مصنوعی فارسی با معماری درخت دانش  
**گروک × احمدرضا ایزدی**

## ساختار

```
derakhsha_engine/
├── app.py                 # FastAPI
├── requirements.txt
├── Procfile
├── railway.json
├── derakhsha/
│   ├── language.py        # قشر زبان
│   ├── tree.py            # درخت دانش
│   ├── dialogue.py        # پیوند گفتگو
│   └── engine.py          # موتور اصلی
└── static/index.html      # فرانت (اختیاری)
```

## API

| متد | مسیر | کار |
|-----|------|-----|
| GET | `/api/health` | سلامت |
| POST | `/api/chat` | گفتگو |
| POST | `/api/learn` | یادگیری سند |
| POST | `/api/analyze` | فقط تحلیل زبان |
| GET | `/api/branches` | شاخه‌های درخت |
| GET | `/api/tree` | کل درخت |
| GET | `/docs` | Swagger |

### نمونه chat

```bash
curl -X POST https://YOUR-APP.up.railway.app/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message":"درخشا چیست؟","session_id":"u1"}'
```

### نمونه learn

```bash
curl -X POST https://YOUR-APP.up.railway.app/api/learn \
  -H "Content-Type: application/json" \
  -d '{"title":"خواب","body":"خواب منظم تمرکز را افزایش می‌دهد.","doc_type":"یادداشت","keywords":["خواب","تمرکز"]}'
```

## استقرار روی Railway

1. مخزن GitHub بساز و این پوشه را push کن
2. در [railway.app](https://railway.app) → New Project → Deploy from GitHub
3. متغیر `PORT` را Railway خودش می‌دهد
4. دامنه عمومی را فعال کن

## اجرای محلی

```bash
pip install -r requirements.txt
uvicorn app:app --reload --port 8000
```

باز کن: http://localhost:8000/docs

## لایه‌های موتور

1. قشر زبان — نوع جمله، نقش، کلیدواژه، لحن
2. درخت دانش — شاخه و گره و برگ
3. یادگیری — سند → گره DOC
4. پیوند گفتگو — session و ماهیت جمله
5. اعتماد و مسیر پاسخ — tree / clarify / learn
