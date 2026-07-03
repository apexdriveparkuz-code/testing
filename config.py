# config.py
# Bu yerga o'z sozlamalaringizni kiriting

import os

# BotFather'dan olgan tokeningiz.
# Xohlasangiz to'g'ridan-to'g'ri shu yerga yozing, yoki muhit o'zgaruvchisi orqali bering.
BOT_TOKEN = os.environ.get("8885989965:AAFD4Y1khFsfl_Zz2QCAfUVOcSNi5fAzRUE")

# Sizning (admin) Telegram chat ID raqamingiz.
# Buni bilish uchun @userinfobot ga /start yozing, u sizga ID beradi.
ADMIN_CHAT_ID = int(os.environ.get("7164104117", "0"))

# Operatorlar ro'yxatga qo'shilish uchun kiritadigan maxfiy kod.
# Operator botga /start yozganda shu kodni so'raymiz - shunchaki tasodifiy odam
# ro'yxatga yozilib olmasligi uchun.
REGISTRATION_CODE = os.environ.get("REG_CODE", "zoxa2026")

# Har kuni operatorlarga savollar avtomatik yuboriladigan vaqt (24 soatlik, server vaqti bo'yicha)
DAILY_QUESTION_HOUR = 20
DAILY_QUESTION_MINUTE = 0

# Har kuni adminga umumiy hisobot avtomatik yuboriladigan vaqt
DAILY_REPORT_HOUR = 21
DAILY_REPORT_MINUTE = 0

# Vaqt zonasi (Toshkent)
TIMEZONE = "Asia/Tashkent"

# Operatorlarga har kuni beriladigan savollar.
# Har birining formati: (kalit_nomi, savol_matni)
# Xohlasangiz shu ro'yxatni o'zgartirib, savol qo'shishingiz/o'chirishingiz mumkin.
QUESTIONS = [
    ("mijoz", "📋 Bugun jami nechta mijoz bilan ishladingiz?"),
    ("block", "🔓 Nechta Yandex bloki olib tashlandi?"),
    ("reyting", "⭐ Nechta reyting tiklandi?"),
    ("drayver", "🚕 Nechta yangi drayver Yandexga ulandi (ZIPPY TAXI)?"),
    ("texosmotr", "🛠 Nechta texosmotr/gaz sertifikat ishlandi?"),
]
