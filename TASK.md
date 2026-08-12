# TASK.md — NIKOH Telegram Bot
## Claude / Coding Agent uchun to‘liq implementatsiya spetsifikatsiyasi

> **MUHIM:** Ushbu fayl loyiha uchun asosiy funksional spetsifikatsiya hisoblanadi.
> Botning foydalanuvchi oqimlari yuklangan real bot logi asosida tuziladi.
> Logdagi matn, tugmalar, narxlar va biznes qoidalari imkon qadar aynan saqlanadi.
>
> **ENG MUHIM QOIDA:** Biror talab, texnik qaror, biznes qoidasi yoki noaniq xatti-harakat manbada aniq ko‘rsatilmagan bo‘lsa, Claude o‘zi taxmin qilib implementatsiya qilmasin. Avval foydalanuvchidan aniq savol so‘rasin va javob olmaguncha o‘sha qism bo‘yicha ishni to‘xtatsin.
>
> **“Temporary”, “keyin tuzatamiz”, “shunchaki ishlashi uchun”, “o‘zimcha tanlayman” kabi yondashuvlar taqiqlanadi.**
>
> Maqsad: ishlab chiqarishga tayyor, modulli, test qilinadigan, xavfsiz, qayta tiklanadigan va keyinchalik kengaytirishga qulay bot yaratish.

---

# 1. Agentning ish tartibi

Claude har bir ish sessiyasida quyidagi tartibga qat’iy amal qiladi:

1. Repozitoriyadagi barcha mavjud fayllarni o‘rganadi.
2. Mavjud kod, konfiguratsiya, `.env.example`, migrationlar, testlar va hujjatlarni tekshiradi.
3. Ushbu `TASK.md` bilan amaldagi loyiha holatini solishtiradi.
4. Qarama-qarshilik topilsa, uni o‘zi hal qilmaydi — savol beradi.
5. Zarur arxitektura va biznes savollarini oldindan chiqaradi.
6. Foydalanuvchining javobini kutadi.
7. Faqat tasdiqlangan talab bo‘yicha implementatsiya qiladi.
8. Har bir katta moduldan keyin test yozadi yoki mavjud testlarni yangilaydi.
9. Database schema o‘zgarsa migration yozadi.
10. API / callback / state / payment kabi kritik oqimlarda edge-case testlari bo‘lishi shart.
11. Ish yakunida:
   - nima bajarilgani;
   - nima test qilingani;
   - qaysi savollar ochiq qolganligi;
   - qanday konfiguratsiya kerakligi
   haqida qisqa hisobot beradi.

### Mutlaq taqiqlar

Claude quyidagilarni foydalanuvchi tasdiqisiz qilmasin:

- texnologik stackni almashtirish;
- database tanlash yoki almashtirish;
- payment provider tanlash;
- payment integratsiyasini o‘zi taxmin qilish;
- Telegram channel ID / username / admin IDlarni taxmin qilish;
- tarif yoki narxlarni o‘zgartirish;
- callback/payment success/failure mantiqini taxmin qilish;
- refund siyosatini o‘zgartirish;
- VIP imtiyozlarini o‘zgartirish;
- kanalga post yuborish formatini o‘zboshimchalik bilan o‘zgartirish;
- maxfiylik/qidiruv ko‘rinishini o‘zgartirish;
- profil maydonlarini qo‘shish yoki olib tashlash;
- moderator/admin huquqlarini o‘zi belgilash;
- “placeholder” biznes qoidani production kodiga kiritish;
- “keyin aniqlanadi” bo‘lgan joy uchun jim turib default tanlash.

---

# 2. Mahsulot maqsadi

NIKOH — Telegram ichida nikoh / moslik platformasi.

Asosiy foydalanuvchi imkoniyatlari:

- telefon raqamini tasdiqlash;
- profil / anketa to‘ldirish;
- balansni ko‘rish;
- balansni to‘ldirish;
- tranzaksiyalar tarixini ko‘rish;
- referral orqali ichki bonus olish;
- VIP sotib olish;
- anketa qidirish;
- yashirin anketalarni ko‘rish;
- anketa bo‘yicha so‘rov yuborish;
- kelgan / yuborilgan so‘rovlarni boshqarish;
- chat ochilishi va chatda yozishish;
- lichka (kontakt / private contact) ochish bo‘yicha alohida so‘rov;
- e’lon joylashtirish;
- adminga xabar yuborish;
- bosh menyudan barcha bo‘limlarga kirish.

Asosiy biznes tamoyili:

> Botdagi balans naqd pul emas. U ichki xizmatlardan foydalanish uchun ishlatiladi va kartaga qaytarilmaydi hamda boshqa foydalanuvchiga o‘tkazilmaydi.

---

# 3. Yuklangan real bot logi — asosiy UX manbasi

Quyidagi hujjat real botdagi foydalanuvchi oqimlari, matnlar, tugmalar, tariflar va biznes qoidalarini ko‘rsatadi:

- `Pasted markdown(1).md`

Claude implementatsiya vaqtida aynan shu logdagi oqimni reference sifatida ishlatsin.

Manba fayl nusxasi: `/mnt/data/Pasted markdown(1).md`

**Muhim:** Logda ko‘rsatilmagan narsani “standart Telegram bot” deb taxmin qilib kiritish mumkin emas.

---

# 4. Asosiy menyu

Log bo‘yicha asosiy menyuda quyidagi bo‘limlar mavjud:

- 👤 Profil
- 💰 Hisobim
- 💸 Hisobni to‘ldirish
- 📜 Tranzaksiyalar tarixi
- 💎 VIP a'zo
- 📨 So‘rov yuborish
- 📢 E‘lon joylashtirish
- 🕵️ Yashirin anketalar
- 🔍 Anketa qidirish
- 💬 Chatlarim
- 📥 Yangi so‘rovlar
- 💸 Pul topish
- 📩 Adminga xabar
- 🏠 Bosh menyu

UI matnlari Unicode/emoji bilan saqlanadi.

---

# 5. /start va birinchi kirish

## Kutilayotgan oqim

Foydalanuvchi `/start` yuborganda:

1. Foydalanuvchining Telegram account ma’lumotlari aniqlanadi.
2. Agar telefon raqami hali tasdiqlanmagan bo‘lsa, bot telefon raqamini kontakt sifatida yuborishni so‘raydi.
3. Raqam tasdiqlangach:
   - welcome message;
   - foydalanuvchiga welcome bonus;
   - referral code/link;
   - profilni to‘ldirishga chaqiriq
   ko‘rsatiladi.

Logdagi real xabar mazmuni:

> NIKOH: Botdan foydalanish uchun telefon raqamingizni kontakt sifatida yuboring

Tasdiqlangandan keyin:

> Telefon raqamingiz tasdiqlandi! @NIKOH_01 kanalining rasmiy botiga xush kelibsiz.
> Hisobingizga 5 000 so‘m bonus qo‘shildi.
> Botning barcha funksiyalaridan to‘liq foydalanish uchun Profil bo‘limini to‘ldiring.

## Welcome bonus

Log bo‘yicha:
- `5 000 so‘m`
- transaction type: `welcome_bonus`

**Muhim:** bonus bir foydalanuvchiga faqat bir marta berilishi kerak.

DB transaction / idempotency bilan himoyalansin.

---

# 6. Valyuta

Log bo‘yicha:

- asosiy valuta: so‘m;
- kurs ko‘rsatkichi: `1$ = 12,100 so‘m`.

Masalan:
`5,000 so‘m ($0.41)`

**ASK USER agar bu kurs statik yoki dinamik ekanligi kerak bo‘lsa.**

Kurs kod ichida hardcode qilinmasin, foydalanuvchi tasdiqlamaguncha konfiguratsiya strategiyasi tanlanmasin.

---

# 7. Balans / Hisobim

`💰 Hisobim` bosilganda foydalanuvchining balansini ko‘rsatish kerak.

Logdagi format:

> 💰 Hisobingiz:
> Balans: 5,000 so‘m ($0.41)
> 1$ = 12,100 so‘m
>
> ⚠️ Hisobdagi mablag‘ kartaga qaytarilmaydi, boshqa foydalanuvchiga o‘tkazilmaydi. Faqat ichki xizmatlarga ishlatiladi.

Balans quyidagilar bilan ishlashi kerak:

- welcome bonus;
- referral bonus;
- deposit;
- deposit bonus;
- service purchase;
- VIP purchase;
- request fee;
- private contact fee;
- refunds.

Har bir balans o‘zgarishi ledger / transaction history orqali kuzatiladigan bo‘lishi kerak.

### Muhim accounting qoidasi

Balansni to‘g‘ridan-to‘g‘ri `balance = balance - x` uslubida nazoratsiz o‘zgartirish mumkin emas.

Atomic transaction va idempotency talab qilinadi.

---

# 8. Tranzaksiyalar tarixi

`📜 Tranzaksiyalar tarixi`

Logda misol:

> 📜 Tranzaksiyalar tarixi:
>
> 📅 2026-08-12 14:32:27
> 💸 5,000 so‘m (welcome_bonus)
> 📝 Yangi foydalanuvchi uchun 5000 so‘m bonus

History kamida quyidagilarni qo‘llashi kerak:

- sana / vaqt;
- summa;
- transaction type;
- description;
- kredit yoki debit ekanligi;
- reference ID;
- xizmat / payment ID bilan bog‘lanish.

**ASK USER:** transaction history pagination kerakmi?  
**ASK USER:** foydalanuvchi refund transactionlarini qanday ko‘rishi kerak?  
**ASK USER:** admin uchun alohida transaction audit kerakmi?

---

# 9. Profil / anketa

## Profil boshlanishi

`👤 Profil`

Log bo‘yicha:

> Tushunmasangiz videoni ko'rishingiz mumkun -->
> https://t.me/nikohboti/9
>
> Jinsingizni tanlang:

Bu help video URL konfiguratsiya orqali boshqarilishi kerak.

## Umumiy qoidalar

Profilni to‘ldirishdan oldin:

- telefon tasdiqlangan bo‘lishi kerak;
- foydalanuvchi 18+ bo‘lishi kerak;
- boshqa majburiy preconditionlar bo‘lsa, ular foydalanuvchidan aniqlashtirilishi kerak.

### Jins

Tugmalar:

- 👨 Erkak
- 👩 Ayol

### Har ikki jins uchun umumiy maydonlar

- Jins
- Yosh
- Bo‘y
- Vazn
- Millat
- Oilaviy holat
- Manzil
- Asli qayerlik
- Namoz va Qur’on o‘qiysizmi
- Nechta til bilasiz
- O‘zingiz haqingizda
- Qarama-qarshi jins uchun talablar
- Anketani kim to‘ldirdi

### Erkaklar uchun logda

- Yosh: 18–99
- Bo‘y: 100–250 sm
- Vazn: 30–200 kg
- Millat
- Oilaviy holat
- Manzil
- Asli qayerlik
- Namoz va Qur’on o‘qiysizmi
- Tillar soni: 1–10
- O‘zingiz haqingizda
- Kelin uchun talablar
- Anketani kim to‘ldirdi

### Ayollar uchun logda qo‘shimcha maydonlar

- Farzandlar soni: 0–10
- Ro‘mol o‘raysizmi?
- Ko‘chib o‘tishga tayyormisiz?
- 2-likka rozimisiz?
- Qaysi viloyatdan?

### Anketa kim tomonidan to‘ldirildi

Logda:
- O‘zi
- Vakili

### Oila / wali disclaimer

Profil to‘ldirishdan oldin logda diniy/ijtimoiy ogohlantirish berilgan.

Mazmun:

> Bu NIKOH platformasi. Anketani faqat valiyingiz (ota-ona, aka-uka) roziligi bilan to‘ldiring.
> Valiysiz e’lon berish dinimizga va odatimizga zid.
> O‘zingizga va boshqalarga zulm qilmang.
> Profilni to‘ldirish orqali siz maxfiy e’lon joylashtirasiz.
> Raqamingiz va username’ingiz faqat VIP a‘zolarga ko‘rsatilishi mumkin.

**ASK USER:** Ushbu disclaimer uchun foydalanuvchidan explicit “roziman/tasdiqlayman” action kerakmi?

---

# 10. Profil preview / tasdiqlash

Anketa tugagach preview chiqariladi.

Logdagi format:

- Anketa raqami
- Yosh
- Bo‘y
- Vazn
- Millat
- Oilaviy holat
- Manzil
- Asli qayerlik
- Namoz va Qur’on
- Tillar soni
- Bio
- Qarama-qarshi jins uchun talablar
- Bog‘lanish

Ayollar uchun qo‘shimcha maydonlar ham ko‘rsatiladi.

Tugmalar:

- ✅ Tasdiqlash
- ❌ Qayta kiritish

### Muhim

`#None` kabi qiymatlar production’da chiqmasligi kerak.

Anketa ID generatori alohida, unique va race-condition-safe bo‘lishi kerak.

**ASK USER:** Anketa raqami formati qanday bo‘lsin? Masalan `#12345` kabi?  
**ASK USER:** Anketa raqami global sequence bo‘ladimi yoki UUID/short ID ko‘rinishidami?

---

# 11. Profil ko‘rinishi va maxfiylik

Log bo‘yicha:

> Profilingiz saqlandi va maxfiy anketalar bo‘limiga qo‘shildi!
> Hozirda profilingizni faqat VIP A'zolar ko‘ra oladi.

Shuningdek:

- telefon raqami va username oddiy foydalanuvchilarga avtomatik ko‘rsatilmasligi;
- VIP kontentiga alohida ruxsat nazorati;
- maxfiy profil / public ad farqi bo‘lishi kerak.

**ASK USER:** Profilning `private`, `VIP-only`, `public channel post` visibility state-lari aniq qanday bo‘ladi?

---

# 12. So‘rov yuborish

`📨 So‘rov yuborish`

Log:

> Anketa raqamini kiriting:
> (Anketa raqami @Nikoh_01 kanalidan olinadi)

## Jarayon

1. Foydalanuvchi anketa raqamini yuboradi.
2. Tizim anketa mavjudligini tekshiradi.
3. Foydalanuvchi:
   - profilga;
   - jins mosligiga;
   - VIP statusiga;
   - xizmat limitlariga;
   - balansga
   tekshiriladi.
4. To‘lov talab qilinsa balansdan yechiladi.
5. Qarshi tomonga request yuboriladi.

### Request qoidalari — log bo‘yicha

Erkaklar uchun yozilgan instruktsiyada:

1. Kanaldan ayol anketasi tanlanadi.
2. Botda so‘rov yuboriladi.
3. So‘rov pullik.
4. Ayol rad etsa, to‘lovning 80% qaytariladi.
5. Ayol 24 soat ichida javob bermasa, request auto-cancel bo‘ladi va to‘lov 100% qaytariladi.
6. Ayol qabul qilsa, ikkala tomon uchun ma’lum vaqtga chat ochiladi.
7. Chat `💬 Chatlarim` orqali ochiladi.
8. Yozilgan xabarlar boshqa tomonga yetkaziladi.
9. Yozishmalar saqlanadi va admin nazorat qilishi mumkin.
10. Mos kelmasa “Chatni tugatish” orqali chat yakunlanadi.

> Eslatma: To‘lovning yarmi — so‘rov yuborish uchun, qolgan yarmi — lichkani ochish uchun ajratilgan.

### Kritik noaniqliklar

**ASK USER before implementation:**

- Bitta so‘rovning aniq narxi qancha?
- “To‘lovning yarmi request, yarmi lichka” qaysi umumiy summaga nisbatan?
- 80% refund request fee’ning o‘ziga qo‘llanadimi yoki umumiy escrow summasiga?
- 24 soat qaysi eventdan hisoblanadi?
- VIP user uchun request mutlaqo bepulmi yoki boshqa limit bormi?
- Bitta target’ga takroriy request yuborishga qaysi holatlarda ruxsat bor?
- Request expiration’dan oldin ikkala tomon statusini qanday o‘zgartira oladi?

---

# 13. Yangi so‘rovlar

`📥 Yangi so‘rovlar`

Bo‘limda kamida:

- 📩 Kelgan so‘rov
- 📩 Kelgan lichka so‘rovlari
- 📤 Yuborilgan so‘rov
- 📤 Yuborilgan lichka so‘rovlar

Logdagi empty state:

> Hozirda sizga kelgan so‘rovlar yo‘q.
>
> Hozirda sizga kelgan lichka ochish so‘rovlari yo‘q.
>
> Hozirda yuborilgan so‘rovlar yo‘q.
>
> Hozirda yuborilgan lichka ochish so‘rovlari yo‘q.

Har bir status uchun explicit state machine ishlatilishi kerak.

Tavsiya etilgan state nomlari (foydalanuvchi tasdig‘isiz final biznes qarori sifatida qabul qilinmasin):

- pending
- accepted
- rejected
- expired
- cancelled
- refunded
- completed

---

# 14. Chatlar

`💬 Chatlarim`

Empty state:

> Sizda faol chatlar yo‘q.

Accept qilingan requestdan keyin:

- ikki tomon uchun chat session yaratiladi;
- chat vaqt chegarasiga ega bo‘lishi kerak;
- barcha xabarlar DBga saqlanadi;
- admin audit uchun ko‘rishi mumkin.

### Xabarlar

Asosiy requirement:
- foydalanuvchi A yuborgan xabar B ga yuboriladi;
- B javobi A ga yuboriladi;
- Telegram ID lar foydalanuvchilarga to‘g‘ridan-to‘g‘ri berilmaydi;
- bot vositachi sifatida ishlaydi.

**ASK USER:**
- Chat qancha vaqt ochiq turadi?
- Qaysi message turlari ruxsat etiladi? (`text`, `photo`, `video`, `document`, voice, etc.)
- Admin barcha xabarlarni real-time ko‘radimi?
- So‘z filtri / moderation kerakmi?
- Chat tugatilgandan keyin tarix foydalanuvchiga ko‘rinadimi?

---

# 15. Lichka / private contact

Log:

> Agar fikrlaringiz mos kelsa, 🔓 Lichkani ochish tugmasi orqali rasm yuborish yoki olish imkoniyati bo‘ladi.
> (Lichkani ochish pullik)
> Ayol tasdiqlasa, sizga lichkasi ochiladi.
> Agar spamda bo‘lsangiz, avval premium oling.

Bu funksiya alohida state machine bo‘lishi kerak.

**ASK USER:**
- “Lichka” nimani anglatadi: username, phone number, Telegram contact, photo exchange yoki boshqa narsa?
- Lichkani kim birinchi so‘raydi?
- Kim tasdiqlaydi?
- Narxi qancha?
- VIP uchun tekinmi?
- “Spamda bo‘lsangiz, avval premium oling” texnik jihatdan nimani anglatadi?
- Telegram spam statusini qanday aniqlash kerak?
- Lichka ochilgandan keyin qaysi ma’lumotlar ko‘rsatiladi?

---

# 16. VIP

`💎 VIP a'zo`

Logdagi VIP imkoniyatlari:

- barcha so‘rovlar va lichka ochish bepul;
- xos kanali va maxfiy anketalar kanaliga a'zolik;
- so‘rovlar va chatlar uchun ko‘proq limit;
- anketalarni maxsus filtrlar bilan qidirish.

### Tariflar

Log bo‘yicha:

- 1 kun: `249,000 so‘m`
- 1 hafta: `449,000 so‘m`
- 1 oy: `990,000 so‘m`

### Yetarli mablag‘ bo‘lmasa

Misol:

> Balansingizda yetarli mablag‘ yo‘q!
> Joriy balans: 5,000 so‘m
> Kerakli summa: 249,000 so‘m
> Iltimos, hisobingizni to‘ldiring.

### VIP status

DBda kamida:

- plan;
- started_at;
- expires_at;
- active/inactive;
- purchase transaction;
- source/payment reference.

**ASK USER:**
- VIP sotib olinganda kanalga avtomatik qo‘shish kerakmi?
- VIP tugaganda kanaldan avtomatik chiqarish kerakmi?
- VIP sotib olish bir necha marta amalga oshirilsa muddat uzaytiriladimi yoki yangi period boshlanadimi?
- Expiry timezone?
- VIP plan narxlari kelajakda admin paneldan o‘zgaradimi?
- VIP “ko‘proq limit” uchun aniq limitlar nechta?

---

# 17. Hisobni to‘ldirish

`💸 Hisobni to‘ldirish`

Log:

> Quyidagi to‘lov usullaridan birini tanlang.
> Har bir usul uchun minimal summa va bonuslar haqida ma'lumot tanlaganingizdan so‘ng ko‘rsatiladi.

### Deposit bonuslari

- 300,000 so‘mdan yuqori: 10%
- 500,000 so‘mdan yuqori: 15%
- 1,000,000 so‘mdan yuqori: 20%

Log misollari:

- 300,000 → 330,000
- 500,000 → 575,000
- 1,000,000 → 1,200,000

### Uzcard

Log bo‘yicha:

- Payment method: Uzcard
- Currency: UZS
- Minimum: 50,000 so‘m

**CRITICAL — DO NOT GUESS:**

To‘lov provideri, API, merchant, callback URL, signature verification, reconciliation, timeout, duplicate callback handling, refund mechanism, payment confirmation va payment statuslar manbada aniqlanmagan.

**ASK USER:**
- Qaysi payment provider ishlatiladi?
- Provider API dokumentatsiyasi bormi?
- Uzcard native API yoki agregator?
- Admin qo‘lda tasdiqlaydimi yoki avtomatik?
- Payment invoice necha daqiqa amal qiladi?
- Callback/webhook bormi?
- Bir payment uchun duplicate callback qanday handling qilinadi?
- Bonus qachon beriladi: payment success callbackdan keyinmi yoki admin approve’dan keyinmi?
- Chegara aynan `>=`mi yoki `>`mi?
- 300,000 / 500,000 / 1,000,000 uchun threshold semantics aniq tasdiqlansin.

### Payment accounting

Har bir payment:

- pending;
- paid;
- failed;
- expired;
- cancelled;
- refunded

kabi holatlarga ega bo‘lishi mumkin, lekin final state diagram foydalanuvchi bilan tasdiqlanadi.

---

# 18. Referral / Pul topish

`💸 Pul topish`

Log:

> Do‘stlaringizni taklif qilib, pul toping!
> Har bir chaqirilgan foydalanuvchi uchun 3,000 so‘m bonus oling!

Ko‘rsatiladi:

- chaqirilgan do‘stlar soni;
- jami bonus;
- har bir do‘st uchun: `3,000 so‘m`;
- referral link.

Misol:
`https://t.me/Nikoh_uzbot?start=IO7R`

### Referral security

Referral uchun:

- unique code;
- inviter;
- invited user;
- created_at;
- attribution source;
- reward transaction;
- reward status

saqlansin.

**ASK USER:**
- Bonus aynan qaysi eventda beriladi?
  - `/start` bo‘lganda?
  - phone verificationdan keyin?
  - profile completiondan keyin?
  - birinchi paymentdan keyin?
- Self-referral qanday bloklanadi?
- Bitta Telegram user faqat bir marta referral qilinadimi?
- Oldin `/start` qilib keyin referral link orqali kirsa nima bo‘ladi?
- Bir referral reward uchun minimum activity bormi?

---

# 19. E'lon joylashtirish

`📢 E‘lon joylashtirish`

Tur:

- 🌟 Maxsus e'lon joylashtirish
- 📢 Oddiy e'lon joylashtirish

## Username sharti

Log bo‘yicha har ikki e'lon turi uchun:

- Telegram username mavjud bo‘lishi kerak.

Aks holda:

> Hurmatli foydalanuvchi! E‘lon joylashtirish uchun Telegram’da foydalanuvchi nomi (@username) o‘rnatishingiz zarur...

Help image:
`https://t.me/nikohboti/8`

### E'lon turi

**ASK USER:**
- Oddiy e’lon narxi?
- Maxsus e’lon narxi?
- E'lon muddati?
- Bir kunda nechta e'lon?
- Approval admin orqali bo‘ladimi?
- Post qaysi kanalga yuboriladi?
- Post formatlari qanday?
- Rasm/video talab qilinadimi?
- Profil ma’lumotlari avtomatik post qilinadimi?
- Edit / delete imkoniyati bormi?
- VIP uchun chegirma yoki bepulmi?

---

# 20. Kanalga e’lon / profil chiqarish

Logda `@Nikoh_01` kanali va `@nikohboti` help kanali tilga olingan.

**MUHIM:** Kanal username’lari logdan olingan bo‘lsa ham, real deploymentdagi exact channel IDs, bot permissions va admin role’lar konfiguratsiya orqali beriladi.

Claude quyidagilarni hardcode qilmasin:

- channel numeric ID;
- bot token;
- admin IDs;
- payment secret;
- API secret.

`.env.example` yozilsin.

---

# 21. Anketa qidirish

`🔍 Anketa qidirish`

Log bo‘yicha balans minimal:

> Bu funksiyadan foydalanish uchun kamida 6000 so‘m kerak.

**ASK USER:**
- Qidiruv narxi `6000`mi?
- 6000 so‘m bir search uchunmi yoki access fee?
- VIP uchun bepulmi?
- Qaysi filterlar mavjud?
- Filtrlar:
  - gender
  - age
  - height
  - weight
  - location
  - native origin
  - marital status
  - children
  - hijab
  - relocation
  - religious practice
  - languages
  - etc.
  - bularning qaysilari tasdiqlanadi?
- Natijalar paginationi qancha?
- Sorting qanday?

---

# 22. Yashirin anketalar

`🕵️ Yashirin anketalar`

Log:

> Balansingizda yetarli mablag‘ yo‘q!
> Joriy balans: 5,000 so‘m
> Bu funksiyadan foydalanish uchun kamida 6000 so‘m kerak.

**ASK USER:**
- 6000 so‘m access fee ekanligini tasdiqlang.
- Bu bir marta to‘lanadimi yoki session/kun uchunmi?
- VIP barcha yashirin anketalarni ko‘ra oladimi?
- Yashirin anketalarda telefon/username qachon ko‘rinadi?
- Qaysi profil statuslari private bo‘lishi mumkin?

---

# 23. Adminga xabar

`📩 Adminga xabar`

Flow:

1. User tugmani bosadi.
2. Bot:
   > Adminga yubormoqchi bo‘lgan xabaringizni kiriting:
3. User xabar yuboradi.
4. Admin / supportga yetkaziladi.

**ASK USER:**
- Xabar faqat textmi?
- Photo/document/voice mumkinmi?
- Admin javobini userga qaytarish kerakmi?
- Ticket system kerakmi?
- Ticket ID kerakmi?
- Barcha adminlar ko‘radimi yoki bitta support chat?

---

# 24. Moderatsiya

Logda:

> Barcha yozishmalar saqlanadi va admin tomonidan nazorat qilinadi.
> Iltimos, nojo‘ya va behayo so‘zlar yozmang.

Demak moderation architecture kerak.

**ASK USER:**
- Keyword blacklist kerakmi?
- AI moderation kerakmi?
- Manual admin moderation yetarlimi?
- Moderation alert kimga yuboriladi?
- User bloklanishi / warning / suspension state’lari kerakmi?
- Report tugmasi kerakmi?

---

# 25. Foydalanuvchi statuslari

Kamida quyidagi holatlar ko‘rib chiqilsin:

- unverified_phone
- verified
- profile_incomplete
- profile_complete
- active
- blocked
- suspended
- vip_active
- vip_expired

**ASK USER:** final user state machine tasdiqlansin.

---

# 26. Balans xavfsizligi

Balans uchun quyidagilar majburiy:

- DB transaction;
- atomic updates;
- idempotency;
- duplicate callback protection;
- immutable transaction ledger;
- negative balance prevention;
- audit trail;
- refund transaction yaratish;
- original transaction bilan refund bog‘lash.

Hech qachon:

```text
read balance
calculate new balance
write balance
```

kabi race-conditionli oqimni transactionlarsiz ishlatmang.

---

# 27. Request state machine

Tavsiya etiladigan model:

```text
PENDING
  ├── ACCEPTED ──> CHAT_ACTIVE
  │                  └── CHAT_ENDED
  │
  ├── REJECTED ──> PARTIAL_REFUND
  │
  ├── EXPIRED ──> FULL_REFUND
  │
  └── CANCELLED ──> policy-defined refund
```

**Bu faqat konseptual namuna.**
Refund siyosati foydalanuvchi tomonidan tasdiqlanmaguncha final biznes qoidasi sifatida qabul qilinmasin.

---

# 28. Telegram security

Quyidagilar majburiy:

- bot token `.env`da;
- secretlar source controlga kiritilmaydi;
- webhook secret verification;
- admin authorization;
- callback_data tamper protection;
- user identity server-side tekshiriladi;
- callback query faqat tegishli userga tegishli ekanligi tekshiriladi;
- IDOR’ni oldini olish;
- sensitive info boshqa userga sizib chiqmasligi.

---

# 29. Privacy / PII

Bot quyidagi sensitive ma’lumotlar bilan ishlashi mumkin:

- phone;
- username;
- profile;
- location;
- age;
- marital status;
- religious practice;
- private chat messages.

Claude quyidagilarni alohida ko‘rib chiqishi shart:

- kim nimani ko‘ra oladi;
- DB access;
- admin access;
- logsdagi PII;
- error message’larda PII;
- backup;
- retention;
- deletion.

**ASK USER:**
- User account/profileni o‘chirish kerakmi?
- Chat history qancha saqlanadi?
- Profile deletion bilan transaction history o‘chiriladimi yoki anonymize qilinadimi?
- Adminlar nimani ko‘ra oladi?
- Audit log retention muddati?

---

# 30. Database

Final database texnologiyasi user tomonidan tasdiqlanmaguncha tanlanmasin.

Lekin ma’lumotlar modeli kamida quyidagi domainlarni qamrab olishi kerak:

### Users
- id
- telegram_user_id
- phone
- username
- first_name
- last_name
- language
- created_at
- updated_at
- verified_at
- status

### Profiles
- id
- user_id
- gender
- age
- height
- weight
- nationality
- marital_status
- location
- original_location
- region
- religion/prayer flag
- languages_count
- children_count
- hijab
- relocation
- second_wife_policy
- bio
- partner_requirements
- filled_by
- visibility
- created_at
- updated_at

### Balances / ledger
- wallet
- transactions
- transaction references
- transaction type
- amount
- before_balance
- after_balance
- description
- created_at

### Referrals
- referral code
- inviter
- invited
- reward
- status
- timestamps

### Payments
- payment id
- user
- provider
- amount
- bonus
- gross credited
- status
- external reference
- idempotency key
- timestamps

### VIP
- plan
- price
- purchased_at
- started_at
- expires_at
- status
- payment reference

### Profiles / ads
- ad type
- profile
- price
- status
- published message/channel reference
- approval status
- timestamps

### Requests
- sender
- receiver
- profile
- request type
- charged amount
- request portion
- private-contact portion
- status
- expires_at
- response_at
- refund amount
- created_at
- updated_at

### Chats
- request id
- participant A
- participant B
- status
- started_at
- expires_at
- ended_at

### Messages
- chat id
- sender
- receiver
- Telegram message reference
- message type
- content reference
- created_at
- moderation status

### Admin / audit
- actor
- action
- target
- metadata
- timestamp

**Bu schema konseptual.**
Final schema user tasdig‘isiz kodga “locked” qilinmasin.

---

# 31. Architecture talabi

Arxitektura modular bo‘lishi kerak.

Domainlar bir-biriga spaghetti tarzda bog‘lanmasin.

Kamida quyidagi qatlamlar bo‘lishi kutiladi:

- Telegram handlers / routers
- FSM / state management
- application services
- domain/business logic
- repositories / DB
- payment provider adapter
- notification adapter
- moderation service
- scheduled jobs
- config
- observability
- tests

Agar boshqa arxitektura tanlansa, Claude sababini tushuntirsin va user bilan tasdiqlasin.

---

# 32. FSM / dialog oqimlari

Profil, payment, request, admin message kabi ko‘p bosqichli flowlar explicit FSM bilan qurilsin.

Misol:

```text
PROFILE_START
 -> WAIT_GENDER
 -> WAIT_AGE
 -> WAIT_HEIGHT
 -> WAIT_WEIGHT
 -> ...
 -> PREVIEW
 -> CONFIRM / RESTART
```

Noto‘g‘ri input:

- foydalanuvchiga tushunarli xato;
- state yo‘qolmasligi;
- retry;
- cancel;
- back navigation
qo‘llab-quvvatlansin.

**ASK USER:** Har bir flowda “⬅️ Orqaga” tugmasi kerakmi?

---

# 33. Validation

Logdagi range’lar server-side validate qilinadi.

Misollar:

- age: 18–99
- height: 100–250
- weight: 30–200
- languages: 1–10
- children: 0–10

Frontend/button validation yetarli emas.

Input sanitization, Unicode handling va uzunlik limitlari ham server-side bo‘lsin.

**ASK USER:** Matn maydonlari uchun maksimal character countlar nechta?

---

# 34. Error handling

Barcha kritik oqimlarda:

- user-friendly message;
- internal structured error;
- log correlation ID;
- retry policy;
- idempotency;
- fallback behavior

bo‘lishi kerak.

Internal exception stack trace userga yuborilmasin.

---

# 35. Background jobs / scheduler

Quyidagi tasklar ehtimol background scheduler talab qiladi:

- 24 soatlik request expiry;
- automatic refund;
- VIP expiry;
- payment timeout;
- stale payment reconciliation;
- notification delivery;
- channel posting retries.

**ASK USER:** Qaysi scheduler / infrastructure ishlatiladi?

---

# 36. Notificationlar

Kerak bo‘lishi mumkin:

- new request;
- request accepted;
- request rejected;
- request expired;
- refund completed;
- VIP activated;
- VIP expiring;
- payment success;
- payment failed;
- admin reply;
- chat closed.

Final notification matrix user bilan tasdiqlanadi.

---

# 37. Admin panel / admin bot

Logdan admin monitoring talabi ko‘rinadi, lekin admin UI aniqlanmagan.

**ASK USER BEFORE IMPLEMENTATION:**

- Web admin panel kerakmi?
- Alohida admin Telegram bot kerakmi?
- Adminlar nechta?
- Rolelar:
  - superadmin
  - moderator
  - support
  - finance
  kabi rollar kerakmi?
- Payment approval admin orqali bo‘ladimi?
- Profile/ad approval admin orqali bo‘ladimi?
- Chat moderation qayerda bo‘ladi?
- User ban/unban kerakmi?
- Manual balance adjustment kerakmi?
- Audit log paneli kerakmi?

---

# 38. Configuration

Kamida:

```env
BOT_TOKEN=
BOT_USERNAME=
BOT_ADMIN_IDS=
DATABASE_URL=

PRIMARY_CHANNEL_ID=
HELP_CHANNEL_USERNAME=

PAYMENT_PROVIDER=
PAYMENT_API_KEY=
PAYMENT_SECRET=
PAYMENT_CALLBACK_URL=

USD_UZS_RATE=
WELCOME_BONUS_UZS=5000
REFERRAL_BONUS_UZS=3000

VIP_1_DAY_UZS=249000
VIP_1_WEEK_UZS=449000
VIP_1_MONTH_UZS=990000

SEARCH_MIN_BALANCE_UZS=6000
HIDDEN_PROFILE_MIN_BALANCE_UZS=6000
UZCARD_MIN_DEPOSIT_UZS=50000
```

**Muhim:** Nomi va existence’ini user bilan tasdiqlanmagan secret/configlar “required” sifatida productionga qotirib qo‘yilmasin.

---

# 39. Localization

Log o‘zbek tilida.

Default language:
- Uzbek

**ASK USER:**
- Cyrillic Uzbek ham kerakmi?
- Russian kerakmi?
- English kerakmi?
- User language automatic aniqlanadimi?

Textlar kod ichiga tartibsiz sochib yuborilmasin; localization layer ishlatish tavsiya etiladi.

---

# 40. UX talablar

Bot:

- tushunarli;
- mobile-friendly;
- katta va aniq reply keyboard;
- callback buttonlar xavfsiz;
- har bir flowda cancel/back strategiyasi;
- empty states;
- insufficient balance states;
- success states;
- error states;
- retry states
ga ega bo‘lsin.

Logdagi matnlar avvalgi UX reference hisoblanadi.

---

# 41. Idempotency

Quyidagilar idempotent bo‘lishi shart:

- welcome bonus;
- referral reward;
- payment callback;
- VIP purchase;
- request charge;
- refund;
- webhook processing;
- channel publication;
- scheduled expiration.

Duplicate Telegram update yoki webhook xavfsiz qayta ishlanishi kerak.

---

# 42. Testing

Minimal test qatlamlari:

## Unit tests

- balance calculations;
- deposit bonus;
- referral reward;
- request fee;
- refund logic;
- VIP expiry;
- validators;
- profile rules;
- permission checks.

## Integration tests

- Telegram update → handler → service → DB;
- payment callback;
- request accept/reject;
- chat relay;
- admin message;
- referral.

## End-to-end scenarios

Kamida:

1. Yangi user → phone verification → welcome bonus.
2. Profil to‘ldirish → preview → confirm.
3. Profilni qayta kiritish.
4. Balansni ko‘rish.
5. Transaction history.
6. Referral.
7. Deposit.
8. Deposit bonus.
9. VIP purchase.
10. Yetarli balance bo‘lmasligi.
11. Request yuborish.
12. Request reject + refund.
13. Request expire + refund.
14. Request accept → chat.
15. Chat end.
16. Lichka request.
17. E'lon joylashtirish.
18. Username yo‘q holati.
19. Yashirin profil access control.
20. Qidiruv access control.
21. Admin message.
22. Duplicate payment callback.
23. Duplicate referral event.
24. Blocked user.
25. Invalid input / cancel / restart.

---

# 43. Acceptance criteria

Feature “tayyor” deb hisoblanishi uchun:

- [ ] Functional requirementlar bajarilgan.
- [ ] Business rulelar user tomonidan tasdiqlangan.
- [ ] No critical requirement guessed.
- [ ] DB migrationlar bor.
- [ ] Tests mavjud.
- [ ] Error handling mavjud.
- [ ] Idempotency tekshirilgan.
- [ ] Authorization tekshirilgan.
- [ ] Sensitive data logging qilinmagan.
- [ ] `.env.example` mavjud.
- [ ] README / setup instruction mavjud.
- [ ] Production configuration documented.
- [ ] Background jobs documented.
- [ ] Payment flow tested.
- [ ] Refund flow tested.
- [ ] Telegram callback security tekshirilgan.
- [ ] Edge cases test qilingan.
- [ ] Lint/typecheck/test muvaffaqiyatli o‘tgan.
- [ ] Manual smoke test bajarilgan.

---

# 44. “ASK USER FIRST” protokoli

Claude quyidagi holatlardan birortasiga duch kelsa, kod yozishni davom ettirmasdan savol beradi:

### Business
- narx noaniq;
- refund noaniq;
- expiry noaniq;
- permission noaniq;
- eligibility noaniq;
- VIP rule noaniq.

### Technical
- stack noaniq;
- payment provider noaniq;
- deployment noaniq;
- DB noaniq;
- hosting noaniq;
- webhook noaniq;
- admin architecture noaniq.

### UX
- tugma noma’lum;
- matn noma’lum;
- navigation noma’lum;
- back/cancel noma’lum.

### Security/privacy
- qaysi data kimga ko‘rinishi noma’lum;
- retention noaniq;
- moderation noaniq;
- admin access noaniq.

### Integrations
- channel ID noaniq;
- payment credentials yo‘q;
- provider API noma’lum;
- external service noma’lum.

Savol formati:

```text
BLOCKER — implementatsiyadan oldin aniqlashtirish kerak

1. Savol...
2. Savol...
3. Savol...

Nega kerak:
- ...
```

Bir vaqtning o‘zida 20 ta mayda savol bermaslikka harakat qilinsin; qaror uchun kerak bo‘ladigan savollar guruhlab berilsin.

---

# 45. Claude uchun qat’iy “DO NOT GUESS” qoida

Quyidagi pattern taqiqlanadi:

```text
"Menimcha foydalanuvchi shuni xohlagan."
"Standart holatda ..."
"Odatda Telegram botlarda ..."
"Keyin o‘zgartirish mumkin."
```

Buning o‘rniga:

```text
"Bu talab manbada aniqlanmagan.
Implementatsiyani davom ettirishdan oldin quyidagini aniqlashtiring: ..."
```

---

# 46. Ishni bosqichlarga bo‘lish

Claude barcha botni bir yo‘la yozib tashlamasin.

Tavsiya etilgan bosqichlar:

## Phase 0 — Discovery
- repo audit;
- source log audit;
- architecture options;
- blocker questions.

## Phase 1 — Foundation
- project setup;
- config;
- logging;
- database;
- migrations;
- user model;
- Telegram bootstrap.

## Phase 2 — Identity
- `/start`;
- contact verification;
- user state;
- welcome bonus;
- referral foundation.

## Phase 3 — Profile
- gender;
- profile FSM;
- validation;
- preview;
- confirmation;
- visibility.

## Phase 4 — Wallet
- balance;
- ledger;
- transactions;
- deposit infrastructure.

## Phase 5 — VIP
- plans;
- purchase;
- expiry;
- permissions.

## Phase 6 — Discovery
- search;
- hidden profiles;
- filters;
- permissions.

## Phase 7 — Requests
- request;
- accept/reject;
- expiration;
- refunds;
- notifications.

## Phase 8 — Chat
- relay;
- storage;
- moderation;
- end chat.

## Phase 9 — Private contact
- separate workflow;
- payment;
- approval;
- reveal rules.

## Phase 10 — Ads
- username check;
- ad creation;
- ordinary/special;
- channel publication;
- moderation.

## Phase 11 — Admin
- moderation;
- finance;
- user management;
- audit.

## Phase 12 — Hardening
- security;
- idempotency;
- tests;
- performance;
- observability;
- deployment.

**Har bir phase oldidan blocker savollar aniqlanadi.**

---

# 47. Definition of Done

Loyiha faqat quyidagi holatda “complete” deb e’lon qilinsin:

1. Barcha asosiy user flowlar ishlaydi.
2. Barcha kritik biznes qoidalar tasdiqlangan.
3. Payment va refundlar transactional.
4. Request expiry ishlaydi.
5. VIP expiry ishlaydi.
6. Referral reward duplicate bo‘lmaydi.
7. Sensitive data access control bilan himoyalangan.
8. Admin monitoring mavjud.
9. Chat xabarlari to‘g‘ri relay qilinadi.
10. Channel postlar idempotent.
11. Tests green.
12. Type/lint/check green.
13. Deployment documented.
14. Monitoring/logging mavjud.
15. Ochiq blockerlar yo‘q.

---

# 48. Claude uchun birinchi javob protokoli

Claude ushbu `TASK.md`ni o‘qigandan keyin darhol kod yozishni boshlamasin.

Birinchi javob:

### 1. Repo audit
Qaysi fayllar va texnologiyalar borligini qisqacha aytsin.

### 2. Specification audit
Qaysi talablar aniq ekanini va qaysilari noaniqligini ko‘rsatsin.

### 3. Blocker questions
Faqat implementatsiyani to‘sib turgan eng muhim savollarni bersin.

### 4. Proposed implementation plan
Foydalanuvchi tasdiqlagach bajariladigan bosqichlarni ko‘rsatsin.

### 5. WAIT
Javob olmaguncha kritik biznes qarorlar bo‘yicha kod yozmasin.

---

# 49. Yakuniy prinsip

Bu loyiha “tezroq kod yozish” loyihasi emas.

Maqsad:

> **Talabni to‘liq aniqlash → arxitekturani kelishish → bosqichma-bosqich implementatsiya → test → audit → production.**

Har qanday noaniqlikda:
**STOP → ASK USER → WAIT → IMPLEMENT.**

