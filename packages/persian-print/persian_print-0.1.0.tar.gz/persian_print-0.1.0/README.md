# کتابخانه Persian Print

یک کتابخانه پایتون برای چاپ آسان متن فارسی با قابلیت‌های پیشرفته و نصب خودکار وابستگی‌ها.

## ویژگی‌ها

- چاپ صحیح متن فارسی با پشتیبانی از راست به چپ (RTL)
- رنگی کردن و استایل‌دهی به متن (پررنگ، زیرخط‌دار، رنگ پس‌زمینه)
- نصب خودکار وابستگی‌ها بر اساس سیستم عامل (مناسب برای VS Code و Termux)
- API ساده و کاربرپسند برای توسعه‌دهندگان

## نصب

برای نصب کتابخانه، می‌توانید از pip استفاده کنید:

```bash
pip install persian_print
```

**توجه:** این کتابخانه به صورت خودکار وابستگی‌های `arabic-reshaper` و `python-bidi` را در صورت نیاز نصب می‌کند.

## مثال‌های استفاده

### چاپ متن فارسی ساده

برای چاپ متن فارسی، کافیست از تابع `print_persian` استفاده کنید:

```python
from persian_print import print_persian

print_persian("سلام دنیا! این یک متن فارسی است.")
print_persian("چاپ فارسی آسان شد!")
```

### چاپ متن رنگی و استایل‌دار

تابع `colored_print` به شما امکان می‌دهد متن را با رنگ‌های مختلف، استایل‌های (مانند پررنگ یا زیرخط‌دار) و حتی رنگ پس‌زمینه چاپ کنید.

**رنگ‌ها:** `black`, `red`, `green`, `yellow`, `blue`, `magenta`, `cyan`, `white`, `reset`
**استایل‌ها:** `normal`, `bold`, `underline`
**رنگ‌های پس‌زمینه:** `black`, `red`, `green`, `yellow`, `blue`, `magenta`, `cyan`, `white`, `default`

```python
from persian_print import colored_print

# چاپ متن قرمز
colored_print("این یک متن قرمز است.", color="red")

# چاپ متن سبز و پررنگ
colored_print("این یک متن سبز و پررنگ است.", color="green", style="bold")

# چاپ متن آبی با پس‌زمینه زرد و زیرخط‌دار
colored_print("متن آبی با پس‌زمینه زرد و زیرخط‌دار.", color="blue", background="yellow", style="underline")

# ترکیب چند ویژگی
colored_print("ترکیب رنگ، استایل و پس‌زمینه.", color="white", background="magenta", style="bold")
```

### مثال کامل

```python
from persian_print import print_persian, colored_print

print_persian("به کتابخانه Persian Print خوش آمدید!")
print_persian("این کتابخانه به شما کمک می‌کند تا متن فارسی را به راحتی در ترمینال چاپ کنید.")

print("\n--- مثال‌های رنگی کردن متن ---")
colored_print("متن قرمز", color="red")
colored_print("متن سبز و پررنگ", color="green", style="bold")
colored_print("متن آبی با پس‌زمینه زرد", color="blue", background="yellow")
colored_print("متن زیرخط‌دار", style="underline")
colored_print("متن پررنگ و زیرخط‌دار", style="bold", style="underline")
colored_print("متن سفید با پس‌زمینه آبی", color="white", background="blue")

print("\n--- تست راست به چپ (RTL) ---")
print_persian("سلام، چگونه اید؟")
print_persian("این یک جمله فارسی برای تست RTL است.")
colored_print("متن فارسی رنگی", color="cyan")
```

## توسعه و مشارکت

اگر مایل به مشارکت در توسعه این کتابخانه هستید، می‌توانید به [مخزن گیت‌هاب](https://github.com/manus-ai/persian_print) مراجعه کنید.

## مجوز

این پروژه تحت مجوز MIT منتشر شده است. برای جزئیات بیشتر به فایل `LICENSE` مراجعه کنید.


