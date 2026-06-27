# 📊 Gold & Currency Price Collector

سرویسی برای جمع‌آوری قیمت لحظه‌ای طلا و ارز، ذخیره تاریخچه قیمت‌ها در **Upstash Redis** و ارائه API با استفاده از **Flask**.

---

# ✨ امکانات

* دریافت قیمت لحظه‌ای طلا از Chartix
* دریافت نرخ دلار هرات
* ذخیره اطلاعات در Upstash Redis
* API ساده برای دریافت داده‌ها
* اجرای خودکار در پس‌زمینه
* ثبت لاگ و بررسی وضعیت سرویس

---

# 🛠️ تکنولوژی‌ها

* Python 3
* Flask
* Requests
* BeautifulSoup4
* Cloudscraper
* Upstash Redis

---

# 📦 نصب

ابتدا پروژه را Clone کنید:

```bash
git clone https://github.com/EliotAlder3on/chatrix_api.git
cd chatrix_api
```

سپس وابستگی‌ها را نصب کنید:

```bash
pip install -r requirements.txt
```

---

# ⚙️ تنظیم فایل `.env`

در ریشه پروژه یک فایل به نام `.env` ایجاد کنید.

نمونه فایل:

```env
UPSTASH_URL=https://your-upstash.upstash.io
UPSTASH_TOKEN=your_upstash_token
```
---

# 🚀 اجرا

اجرای برنامه بدون ذخیره اطلاعات در Redis:

```bash
python app.py --upstash false
```

اجرای برنامه همراه با ذخیره اطلاعات:

```bash
python app.py --upstash true
```

---

# 📡 API

| Endpoint  | توضیح                              |
| --------- | ---------------------------------- |
| `/health` | بررسی سلامت سرویس                  |
| `/status` | نمایش وضعیت برنامه                 |
| `/prices` | دریافت آخرین قیمت‌ها               |
| `/send`   | فعال یا غیرفعال کردن ارسال اطلاعات |

---

## 📌 Example Response

```json
{
  "AbshodeHazer": "31,450,000",
  "Gold18": "7,120,000",
  "herat_usd": "89,350",
  "ons": "3,345.25"
}
```



# 📜 مجوز

این پروژه تحت مجوز **MIT License** منتشر شده است.
