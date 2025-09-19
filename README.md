# 🧠 Mental Sağlık Asistanım

AI destekli ruh hali analizi ve öneri sistemi - Kişiselleştirilmiş mental sağlık desteği için modern web uygulaması.

**Yazar:** Mahmut Sibal

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Vue.js](https://img.shields.io/badge/Vue.js-3.x-green.svg)](https://vuejs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.111+-teal.svg)](https://fastapi.tiangolo.com/)

## 📖 Proje Hakkında

Mental Sağlık Asistanım, kullanıcıların duygusal durumlarını analiz eden ve kişiselleştirilmiş öneriler sunan AI destekli bir platformdur. Transformers tabanlı duygu analizi modelleri kullanarak kullanıcıların yazdığı metinleri analiz eder ve ruh hallerine uygun aktiviteler, müzik önerileri ve mental sağlık kaynakları sunar.

### 🎯 Temel Özellikler

- **🤖 AI Destekli Duygu Analizi**: Hugging Face transformers modeliyle gerçek zamanlı metin analizi
- **📊 Ruh Hali Takibi**: Haftalık ve aylık duygu durum trendleri
- **🎵 Spotify Entegrasyonu**: Ruh haline uygun müzik önerileri
- **💬 Sohbet Arayüzü**: Etkileşimli chat deneyimi
- **🚨 Kriz Tespiti**: Acil durum durumlarının otomatik tespiti
- **📱 PWA Desteği**: Mobil uygulama deneyimi
- **🔒 Güvenli Kimlik Doğrulama**: JWT tabanlı kullanıcı yönetimi
- **📈 Veri Görselleştirme**: Chart.js ile detaylı grafik analizi

## 🏗️ Proje Yapısı

```
Mental-Saglik-Asistanim/
├── backend/                 # FastAPI Backend
│   ├── app/
│   │   ├── routers/        # API endpoint'leri
│   │   ├── schemas/        # Pydantic modelleri
│   │   ├── services/       # İş mantığı katmanı
│   │   ├── db/            # MongoDB bağlantısı
│   │   └── core/          # Yapılandırma ve güvenlik
│   ├── scripts/           # Yardımcı scriptler
│   └── requirements.txt   # Python bağımlılıkları
├── frontend/              # Nuxt.js Frontend
│   ├── pages/            # Vue sayfaları
│   ├── components/       # Yeniden kullanılabilir bileşenler
│   ├── stores/           # Pinia state yönetimi
│   └── package.json      # Node.js bağımlılıkları
└── README.md
```

## 🚀 Kurulum

### Gereksinimler

- **Python 3.8+**
- **Node.js 16+**
- **MongoDB 5.0+**
- **Git**

### 1. Projeyi Klonlayın

```bash
git clone https://github.com/MahmutSibal/Mental-Saglik-Asistanim.git
cd Mental-Saglik-Asistanim
```

### 2. Backend Kurulumu

```bash
cd backend

# Sanal ortam oluşturun
python -m venv venv

# Windows için:
venv\Scripts\activate

# Linux/Mac için:
source venv/bin/activate

# Bağımlılıkları yükleyin
pip install -r requirements.txt
```

#### Backend Yapılandırması

`.env` dosyası oluşturun:

```env
MONGODB_URI=mongodb://localhost:27017
MONGODB_DB=mental_health
JWT_SECRET_KEY=your-super-secret-key-here
CORS_ORIGINS=["http://localhost:3000"]

# Spotify API (opsiyonel)
SPOTIFY_CLIENT_ID=your_spotify_client_id
SPOTIFY_CLIENT_SECRET=your_spotify_client_secret

# Hugging Face Model ayarları
HF_MODEL_NAME=j-hartmann/emotion-english-distilroberta-base
HF_TR_EN_MODEL=Helsinki-NLP/opus-mt-tr-en
USE_TR_EN_TRANSLATION=true
```

#### MongoDB Kurulumu

1. [MongoDB Community Server](https://www.mongodb.com/try/download/community) indirin ve kurun
2. MongoDB servisini başlatın:

```bash
# Windows (Servis olarak)
net start MongoDB

# Linux/Mac
sudo systemctl start mongod
```

### 3. Frontend Kurulumu

```bash
cd frontend

# Bağımlılıkları yükleyin
npm install

# Geliştirme sunucusunu başlatın
npm run dev
```

#### Frontend Yapılandırması

`frontend/.env` dosyası (opsiyonel):

```env
NUXT_PUBLIC_API_BASE=http://localhost:8000
```

### 4. Başlangıç Verilerini Yükleyin

```bash
cd backend
python scripts/seed_suggestions.py
```

## 🎮 Kullanım

### Sunucuları Başlatın

**Backend (Terminal 1):**
```bash
cd backend
uvicorn app.main:app --reload --port 8000
```

**Frontend (Terminal 2):**
```bash
cd frontend
npm run dev
```

### Uygulamaya Erişim

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Dokümantasyonu**: http://localhost:8000/docs

### Temel Kullanım Akışı

1. **Kayıt Ol**: `/auth/register` sayfasında hesap oluşturun
2. **Giriş Yap**: `/auth/login` ile sisteme girin
3. **Sohbet Et**: `/chat` sayfasında duygularınızı paylaşın
4. **Analiz Görün**: `/mood` sayfasında ruh hali trendlerinizi inceleyin
5. **Öneriler Al**: Sistem size uygun aktiviteler önerecek

## 🔧 API Endpoints

### Kimlik Doğrulama
- `POST /auth/register` - Kullanıcı kaydı
- `POST /auth/login` - Giriş yapma
- `GET /auth/me` - Kullanıcı bilgileri

### Duygu Analizi
- `POST /analyze` - Metin analizi ve duygu tespiti
- `GET /messages` - Geçmiş analiz sonuçları

### Ruh Hali Takibi
- `GET /mood/weekly` - Haftalık duygu durumu
- `GET /mood/monthly` - Aylık duygu durumu

### Öneriler
- `GET /suggest/{emotion}` - Belirli duyguya özel öneriler
- `GET /spotify/recommendations` - Spotify müzik önerileri

### Kriz Yönetimi
- `GET /crisis` - Acil yardım kaynakları
- `POST /feedback` - Kullanıcı geri bildirimi

## 🛠️ Teknoloji Yığını

### Backend
- **FastAPI**: Modern, hızlı web framework
- **MongoDB**: NoSQL veritabanı
- **Transformers**: Hugging Face AI modelleri
- **PyTorch**: Derin öğrenme framework'ü
- **Motor**: Asenkron MongoDB driver
- **Pydantic**: Veri doğrulama
- **JWT**: Güvenli kimlik doğrulama

### Frontend
- **Nuxt.js 3**: Vue.js meta-framework
- **Vue.js 3**: Progressive JavaScript framework
- **Tailwind CSS**: Utility-first CSS framework
- **Pinia**: State management
- **Chart.js**: Veri görselleştirme
- **PWA**: Progressive Web App desteği

### AI/ML
- **j-hartmann/emotion-english-distilroberta-base**: Duygu analizi modeli
- **Helsinki-NLP/opus-mt-tr-en**: Türkçe-İngilizce çeviri
- **Sentence Transformers**: Metin similarity

## 📊 Veritabanı Şeması

### Users Collection
```javascript
{
  "_id": ObjectId,
  "email": String,
  "password": String (hashed),
  "name": String,
  "created_at": Date,
  "avatar_url": String (optional)
}
```

### Messages Collection
```javascript
{
  "_id": ObjectId,
  "user_id": String,
  "text": String,
  "emotion": String,
  "scores": Object,
  "crisis": Object (optional),
  "timestamp": Date
}
```

### Suggestions Collection
```javascript
{
  "_id": ObjectId,
  "emotion": String,
  "suggestion_texts": [String],
  "category": String,
  "language": String,
  "created_at": Date,
  "updated_at": Date
}
```

## 🔒 Güvenlik

- **CORS** koruması aktif
- **Rate limiting** ile API koruması
- **JWT** tabanlı kimlik doğrulama
- **Bcrypt** ile şifre hashleme
- **Input validation** Pydantic ile
- **SQL injection** koruması (MongoDB)

## 🚀 Üretim Kurulumu

### Docker ile Kurulum

```dockerfile
# Backend Dockerfile örneği
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Environment Variables

Üretim ortamı için gerekli environment variables:

```env
MONGODB_URI=mongodb://production-mongo:27017
JWT_SECRET_KEY=production-secret-key-very-long-and-secure
CORS_ORIGINS=["https://yourdomain.com"]
SPOTIFY_CLIENT_ID=production_spotify_id
SPOTIFY_CLIENT_SECRET=production_spotify_secret
```

## 🧪 Test

```bash
# Backend testleri
cd backend
python -m pytest

# Frontend testleri
cd frontend
npm run test
```

## 📝 Geliştirme Notları

### Yeni Duygu Kategorisi Ekleme

1. `backend/scripts/suggestions.json` dosyasına yeni kategori ekleyin
2. `backend/scripts/seed_suggestions.py` scriptini çalıştırın
3. Frontend'de yeni duygu için önerileri test edin

### Yeni API Endpoint Ekleme

1. `backend/app/routers/` klasöründe yeni router oluşturun
2. `backend/app/schemas/` klasöründe Pydantic modelleri tanımlayın
3. `backend/app/main.py` dosyasında router'ı dahil edin

## 🤝 Katkıda Bulunma

1. Fork'layın
2. Feature branch oluşturun (`git checkout -b feature/amazing-feature`)
3. Commit'leyin (`git commit -m 'Add amazing feature'`)
4. Push'layın (`git push origin feature/amazing-feature`)
5. Pull Request açın

## 📋 Yapılacaklar

- [ ] Çoklu dil desteği genişletme
- [ ] Gelişmiş AI model entegrasyonu
- [ ] Gerçek zamanlı bildirimler
- [ ] Sosyal özellikler (arkadaş ekleme)
- [ ] Profesyonel destek entegrasyonu
- [ ] Mobil uygulama (React Native)

## 📞 İletişim

**Mahmut Sibal**
- GitHub: [@MahmutSibal](https://github.com/MahmutSibal)
- Proje Linki: [https://github.com/MahmutSibal/Mental-Saglik-Asistanim](https://github.com/MahmutSibal/Mental-Saglik-Asistanim)

## 📄 Lisans

Bu proje MIT lisansı altında lisanslanmıştır. Detaylar için [LICENSE](LICENSE) dosyasına bakın.

## 🙏 Teşekkürler

- [Hugging Face](https://huggingface.co/) - AI modelleri
- [FastAPI](https://fastapi.tiangolo.com/) - Backend framework
- [Nuxt.js](https://nuxt.com/) - Frontend framework
- [MongoDB](https://www.mongodb.com/) - Veritabanı
- [Tailwind CSS](https://tailwindcss.com/) - Styling

---

⭐ **Bu projeyi beğendiyseniz yıldız vermeyi unutmayın!**

> Mental sağlık herkesin hakkıdır. Bu proje sadece destek amaçlıdır ve profesyonel tıbbi tavsiyenin yerini tutmaz.