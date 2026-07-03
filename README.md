# Yandex Hisobot Bot

Operatorlaringizning kunlik ish natijalarini yig'ib, sizga (admin) avtomatik va so'rov bo'yicha hisobot beradigan Telegram bot.

## Bot qanday ishlaydi

1. Har kuni belgilangan vaqtda (standart: 20:00) bot barcha operatorlarga ketma-ket savollar yuboradi:
   - Nechta mijoz bilan ishladi
   - Nechta blok olib tashlandi
   - Nechta reyting tiklandi
   - Nechta drayver ulandi
   - Nechta texosmotr/gaz sertifikat ishlandi
2. Operator har savolga son bilan javob beradi, bot keyingisiga o'tadi.
3. Har kuni 21:00 da sizga (admin) barcha operatorlar bo'yicha umumiy hisobot avtomatik yuboriladi — kim nechta ish qilgani va jami.
4. Istalgan vaqtda `/hisobot` yozsangiz, o'sha kunlik hisobotni darhol ko'rasiz.
5. `/hisobot_hafta` — so'nggi 7 kunlik umumiy va operatorlar kesimidagi statistika.
6. `/operatorlar` — ro'yxatdagi barcha operatorlarni ko'rsatadi.

Operator hisobot topshirmasa, admin hisobotida "Hisobot topshirmaganlar" qismida ismi ko'rinadi.

## O'rnatish

### 1. Talablar
- Python 3.10 yoki undan yuqori versiyasi
- Kompyuter yoki server (masalan VPS), doimiy internetga ulangan bo'lishi kerak, chunki bot doim ishlab turishi lozim

### 2. Botni BotFather orqali yaratish
1. Telegramda [@BotFather](https://t.me/BotFather) ga o'ting
2. `/newbot` yozing, nom va username bering
3. Sizga TOKEN beriladi (masalan: `123456:ABC-DEF...`) — buni saqlab qo'ying

### 3. O'z Telegram ID raqamingizni bilish
1. [@userinfobot](https://t.me/userinfobot) ga `/start` yozing
2. U sizga ID raqamingizni beradi (masalan: `987654321`)

### 4. Kodni sozlash
`config.py` faylini oching va quyidagilarni to'ldiring:

```python
BOT_TOKEN = "SIZNING_TOKENINGIZ"
ADMIN_CHAT_ID = 987654321  # sizning ID raqamingiz
REGISTRATION_CODE = "zoxa2026"  # operatorlar uchun maxfiy kod, xohlasangiz o'zgartiring
```

Savollar ro'yxatini ham shu faylda o'zgartirishingiz mumkin (`QUESTIONS`).

### 5. Kutubxonalarni o'rnatish

Terminalda loyiha papkasida:

```bash
pip install -r requirements.txt
```

### 6. Botni ishga tushirish

```bash
python bot.py
```

Konsolda "Bot ishga tushdi..." degan xabarni ko'rsangiz, hammasi ishlayapti.

Botni doimiy ishlab turishi uchun (masalan VPS'da), `screen`, `tmux` yoki `systemd` xizmatidan foydalanishni tavsiya qilaman — aks holda terminal yopilganda bot ham to'xtaydi.

## Operatorlarni ro'yxatga qo'shish

1. Operatorga bot username'ini bering (masalan `@sizning_botingiz`)
2. Operator botga `/start` yozadi
3. Bot undan maxfiy kodni so'raydi — operator `config.py` dagi `REGISTRATION_CODE` ni kiritadi
4. Keyin ism-familiyasini yozadi
5. Shu bilan operator ro'yxatga qo'shiladi va har kuni avtomatik savol oladi

## Ma'lumotlar qayerda saqlanadi

Barcha hisobotlar va operatorlar ro'yxati `hisobot.db` (SQLite) faylida saqlanadi — bu bot ishga tushgan papkada avtomatik yaratiladi. Faylni zaxira nusxalab (backup) turishni tavsiya qilaman.

## Kengaytirish g'oyalari

- Oylik hisobot buyrug'i qo'shish (`/hisobot_oy`)
- Excel (.xlsx) formatida hisobot eksport qilish
- Bir nechta admin qo'shish
- Har bir xizmat turi bo'yicha alohida narx/daromad hisoblash
