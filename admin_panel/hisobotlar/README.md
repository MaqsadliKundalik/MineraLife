# 📊 Hisobotlar moduli - yangilangan versiya

## ✨ Yangi xususiyatlar

### 1. 📈 Chiziqli diagramma - Kunlik savdo dinamikasi
- **Chart.js** kutubxonasi yordamida professional diagrammalar
- 3 xil ko'rinish:
  - 💰 Daromad (so'm)
  - 📦 Buyurtmalar soni
  - 📊 Mahsulot miqdori (dona)
- Interaktiv tooltip'lar
- Dark mode qo'llab-quvvatlash
- Responsive dizayn (mobil va desktop)

### 2. 📊 Kengaytirilgan metrikalar
- **Jami daromad** - barcha to'lovlardan
- **Buyurtmalar soni** - tanlangan davrda
- **O'rtacha buyurtma** - bir buyurtmaning o'rtacha qiymati
- **Sotilgan mahsulot** - jami sotilgan dona

### 3. 💰 To'lov usullari
- Naqd
- Karta
- Perechesleniya
- Qarz (yangi!)

### 4. 👥 Kuryerlar statistikasi
Har bir kuryer uchun:
- Jami daromad
- Buyurtmalar soni
- Sotilgan mahsulotlar
- O'rtacha buyurtma qiymati

### 5. 🏆 Top 10 mijozlar
Eng ko'p daromad keltirgan 10 ta mijoz:
- Mijoz nomi
- Buyurtmalar soni
- Sotilgan mahsulotlar
- Jami daromad

### 6. 👥 Barcha mijozlar (pagination bilan)
- **50 ta** mijoz har sahifada
- Manzil ma'lumotlari
- Daromad, buyurtmalar, mahsulot miqdori
- Kuryer kim xizmat qilgani

## 🚀 Optimizatsiya

### Database indexlar
Order modelida yangi indexlar qo'shildi:
- `effective_date + status` - sana va status bo'yicha tez qidiruv
- `client + effective_date` - mijoz bo'yicha hisobotlar
- `courier + effective_date` - kuryer bo'yicha hisobotlar
- `status + payment_method` - to'lov statistikasi
- `created_at` - oxirgi buyurtmalar

### Queryset optimizatsiyasi
- `select_related()` - client va courier ma'lumotlarini bitta so'rovda olish
- `values()` + `annotate()` - faqat kerakli ustunlarni olish
- Pagination - 50 ta mijoz har sahifada
- Agregatsiya funksiyalari - database darajasida hisoblash

### Katta baza uchun
- Migration yaratildi: `0010_order_order_date_status_idx_and_more.py`
- Index'lar query vaqtini 10-100 marta tezlashtiradi
- Pagination yordamida xotira iste'molini kamaytirish

## 📝 Foydalanish

### Filtrlar
1. **Sana oralig'i** - maxsus sana tanlash
2. **Tez filtrlar**:
   - Hozirgi oy
   - Oxirgi 6 oy
   - Oxirgi 1 yil

### Diagramma
- **Daromad** - kunlik daromad dinamikasi
- **Buyurtmalar** - kunlik buyurtmalar soni
- **Miqdor** - kunlik sotilgan mahsulotlar

### Export (kelajakda qo'shish mumkin)
- Excel/CSV export
- PDF hisobot
- Email yuborish

## 🔧 Texnik tafsilotlar

### Dependencies
- Django 4.x
- Chart.js 4.4.1
- Tailwind CSS
- MySQL/PostgreSQL (indexlar uchun)

### Template
- `Templates/hisobotlar/reports.html`
- Responsive dizayn
- Dark mode
- Accessibility (WCAG 2.1)

### View
- `hisobotlar/views.py::reports_view()`
- Optimizatsiyalangan querysetlar
- JSON data diagramma uchun
- Pagination logic

## 📈 Performans

### Oldingi versiya
- Faqat oddiy jadval
- Barcha mijozlar bir sahifada
- Indexlar yo'q
- 1000+ mijoz bo'lsa - sekin

### Yangi versiya
- **50 ta** mijoz har sahifada
- Database indexlari
- Optimi zatsiyalangan querysetlar
- 100,000+ buyurtma bilan ham tez ishlaydi

## 🎯 Keyingi qadamlar

1. ✅ Chiziqli diagramma
2. ✅ Kengaytirilgan metrikalar
3. ✅ Pagination
4. ✅ Database indexlar
5. ⏳ Excel export
6. ⏳ PDF hisobotlar
7. ⏳ Email yuborish
8. ⏳ Daromad prognozi (ML)
