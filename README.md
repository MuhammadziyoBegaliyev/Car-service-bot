# 🚗 Avtoservis Telegram Bot

## 📌 Loyihaga umumiy qarash
Avtoservis Bot — bu foydalanuvchilar uchun avtomobil xizmatlarini tez va qulay topishga yordam beruvchi **Telegram bot**. Loyiha **Python 3.12+**, **Aiogram 3** va **SQLite (SQLAlchemy)** texnologiyalari yordamida yaratilgan.  
Bot yordamida foydalanuvchilar avtoservis, moyka, yoqilg‘i yetkazib berish yoki bloklashga qarshi tizim xizmatlarini qidirishi mumkin. Adminlar esa foydalanuvchi so‘rovlarini tezkor qabul qilib boshqaradi.

## 🚀 Asosiy funksiyalar
- 🔧 **Avtoservis filtr**: elektrchi, kuzov, motorchi, vulkanizatsiya va boshqa xizmatlar.  
- 📍 **Geolokatsiya qidiruvi**: foydalanuvchiga eng yaqin 3 ta xizmatni topadi (**Haversine algoritmi**).  
- 📞 **Qo‘ng‘iroq tugmasi**: telefon raqamni kontakt sifatida yuboradi.  
- 🗺️ **Lokatsiya yuborish**: xizmat manzilini xaritada ko‘rsatadi.  
- ⛽️ **Yoqilg‘i yetkazib berish**: turini tanlab buyurtma qilish.  
- 🧽 **Avtomoyka xizmatlari**.  
- 🛡️ **Bloklashga qarshi tizim**.  
- 🤝 **Hamkorlik**: kompaniyalar ma’lumot yuborib murojaat qiladi.  
- 🌐 **Ikki tilli interfeys**: O‘zbek va Rus.  

## ⚙️ Texnologiyalar
- Python 3.12+  
- Aiogram 3  
- SQLite + SQLAlchemy (Async)  
- Haversine algoritmi  

## 📂 Loyihaning tuzilishi
```
avtoservis_bot/
│── app.py
│── handlers/ # asosiy logika
│── states/ # FSM state-lar
│── keyboards/ # Reply va Inline klaviaturalar
│── database/ # SQLite ORM modellari
│── utils/ # yordamchi funksiyalar
│── .env # maxfiy sozlamalar
```



## 💡 Afzalliklar
- Foydalanuvchilar uchun: vaqtni tejaydi, kerakli xizmatni Telegram ichida topish.  
- Adminlar uchun: so‘rovlarni boshqarish, yangi xizmat qo‘shish imkoniyati.  

---

✍️ **Muallif:** [Muhammadziyo Begaliyev](https://github.com/MuhammadziyoBegaliyev)  
📄 Litsenziya: MIT  

---

![Banner](banner.gif)
![Avtoservis Bot Banner](banner.gif)
