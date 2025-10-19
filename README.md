# 🚁 İHA-NET: Afet Durumlarında Drone Destekli Kablosuz İletişim ve Arama Kurtarma Sistemi

<div align="center">

[![Demo Video](https://img.shields.io/badge/Demo-YouTube-red?style=for-the-badge&logo=youtube)](https://youtu.be/JWqFQJuuc9o)
[![Python](https://img.shields.io/badge/Python-3.8+-blue?style=for-the-badge&logo=python)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-2.3.3-green?style=for-the-badge&logo=flask)](https://flask.palletsprojects.com/)
[![AI](https://img.shields.io/badge/AI-Scikit--Learn-orange?style=for-the-badge)](https://scikit-learn.org/)

**Deprem bölgelerinde iletişim köprüsü kuran, yapay zeka destekli arama kurtarma sistemi**

[Demo Videosu](https://youtu.be/JWqFQJuuc9o) | [Kurulum](#-hızlı-başlangıç) | [Kullanım](#-kullanım-senaryosu)

</div>

---

## 🎯 Proje Hakkında

**İHA-NET**, deprem ve afet durumlarında **iletişim altyapısının çökmesi** sonucu ortaya çıkan haberleşme kopukluğunu çözmek için geliştirilmiş bir sistemdir.

### 💡 Nasıl Çalışır?

**Drone üzerinden WiFi ağı yayarak**, GSM ve internet olmayan bölgelerde:

1. 🚁 **Drone** afet bölgesinde WiFi hotspot yayını yapar
2. 📱 **Depremzedeler** → Bu WiFi'ye bağlanıp telefondan yardım çağırır
3. 🚑 **AFAD Görevlileri** → Aynı ağdan depremzedelerin konumlarını gerçek zamanlı görür
4. 🤖 **Yapay Zeka** → Yardım taleplerini aciliyet durumuna göre otomatik sıralar (yaralanma, enkaz, vs.)

> **💡 Senaryo**: Deprem sonrası GSM şebekeleri çöktü. Drone afet bölgesine gelip WiFi yayınlar. Enkaz altındaki kişi telefonuyla bu ağa bağlanır, konumunu işaretler ve "Enkaz altındayım, bacağım kırık" diye yazar. Sistem yapay zeka ile bunu **YÜKSEK ÖNCELİK** olarak işaretler ve AFAD ekipleri haritada hemen görür.

---

## 🌟 Ana Özellikler

| Özellik | Açıklama |
|---------|----------|
| 📡 **Drone WiFi Hotspot** | Altyapı olmayan bölgelerde kablosuz ağ |
| 🗺️ **Harita Tabanlı Sistem** | Depremzede konumları haritada anlık takip |
| 🤖 **AI Önceliklendirme** | Yaralanma, enkaz gibi durumlara göre otomatik sıralama |
| 🚁 **MAVLink Drone Kontrol** | Gerçek drone veya simülasyon desteği |
| 📊 **Canlı Telemetri** | Drone konumu, batarya, hız, yükseklik takibi |
| 👥 **Rol Bazlı Erişim** | Admin, AFAD Görevlisi, Depremzede rolleri |
| 🔒 **Güvenli Oturum** | Flask-Login ile kimlik doğrulama |

---

## 📸 Ekran Görüntüleri

<div align="center">

### Depremzede Yardım Çağırma Sayfası
![Depremzede Arayüzü](assets/depremzede_screenshot.png)
*Depremzedeler WiFi'ye bağlanıp haritadan konumlarını işaretler ve yardım çağırır*

---

### AFAD Yönetim Paneli
![AFAD Panel](assets/afad_panel_screenshot.png)
*AFAD görevlileri tüm talepleri haritada görür, öncelik sırasına göre müdahale eder*

---

### Admin Paneli
![Admin Panel](assets/admin_paneli.jpeg)
*Kullanıcı yönetimi, sistem istatistikleri ve rol atama*

---

### Yer Kontrol İstasyonu
![Yer Kontrol](assets/yer_kontrol_screenshot.png)
*Drone telemetrisi: GPS, hız, batarya, yükseklik, rota takibi*

</div>

> 📁 **Not**: Ekran görüntülerini `assets/` klasörüne ekleyebilirsiniz.

---

## 🏗️ Sistem Mimarisi

```
                    ┌─────────────────────────────────┐
                    │  🚁 DRONE (WiFi Hotspot)       │
                    │     + MAVLink İletişim          │
                    └────────────┬────────────────────┘
                                 │ WiFi Yayını
                ┌────────────────┴────────────────┐
                │                                 │
        📱 Depremzede                    🚑 AFAD Görevlisi
    (Yardım Çağırır)                  (Müdahale Eder)
                │                                 │
                └────────────────┬────────────────┘
                                 │
                    ┌────────────▼────────────┐
                    │  Flask Web Uygulaması   │
                    │   (app.py - Port 1856)  │
                    └────────────┬────────────┘
                                 │
            ┌────────────────────┼────────────────────┐
            │                    │                    │
       ┌────▼─────┐       ┌──────▼──────┐      ┌────▼────────┐
       │Veritabanı│       │   Yapay     │      │  MAVLink    │
       │ SQLite   │       │   Zeka      │      │  Kontrol    │
       └──────────┘       └─────────────┘      └─────────────┘
```

---

## ⚡ Hızlı Başlangıç

### 1️⃣ Gereksinimleri Yükleyin

```powershell
# Tek komutla tüm paketleri yükle
pip install Flask==2.3.3 Flask-SQLAlchemy Flask-Login scikit-learn dronekit requests joblib numpy PyQt5
```

### 2️⃣ AI Modelini Eğitin (İlk Çalıştırma)

```powershell
python ai_prioritizer.py
```

Bu komut:
- ✅ `prioritizer_model.joblib` dosyası oluşturur
- ✅ `vectorizer.joblib` dosyası oluşturur
- ✅ Model performans raporu gösterir (~%92 doğruluk)

### 3️⃣ Sistemi Başlatın

#### **Kolay Yol (Otomatik):**
```powershell
start_system.bat
```
> 4 ayrı terminal penceresi açar ve tüm servisleri başlatır.

#### **Manuel Yol:**
```powershell
# Terminal 1 - Telemetri Ara Sunucu
python mavlink_sunucu.py

# Terminal 2 - Drone Kontrol
python mavlink.py

# Terminal 3 - Yer Kontrol İstasyonu
python yer_kontrol.py

# Terminal 4 - Ana Uygulama
python app.py
```

### 4️⃣ Tarayıcıda Açın

| Sayfa | URL | Açıklama |
|-------|-----|----------|
| 🏠 **Ana Sayfa** | http://localhost:1856/ | Genel bilgi ve yönlendirme |
| 📱 **Depremzede** | http://localhost:1856/depremzede.html | Yardım çağırma sayfası |
| 🔐 **Görevli Girişi** | http://localhost:1856/login.html | AFAD/Admin girişi |
| 🗺️ **AFAD Paneli** | http://localhost:1856/afad.html | Yönetim paneli (giriş sonrası) |
| 👑 **Admin Paneli** | http://localhost:1856/admin_panel.html | Kullanıcı yönetimi (admin) |
| 🛩️ **Yer Kontrol** | http://10.15.157.77:1857/ | Drone telemetrisi |

#### Varsayılan Hesaplar:
```
👑 Admin        → Kullanıcı: admin           Şifre: admin123
🚑 AFAD         → Kullanıcı: afad_gorevlisi  Şifre: afad123
```

> ⚠️ **Güvenlik**: İlk girişten sonra şifreleri mutlaka değiştirin!

---

## 📱 Kullanım Senaryosu

### 👤 Depremzede (Yardım Çağırma)

1. 📡 Telefondan **drone'un WiFi ağına bağlan**
2. 🌐 Tarayıcıda `http://[drone_ip]:1856/depremzede.html` adresine git
3. 📍 Haritadan **konumunu işaretle**
4. ✍️ Durumunu açıkla:
   - *"Enkaz altında kaldım, bacağım kırık, kan kaybediyorum"*
   - *"Çocuklar mahsur kaldı, yardım edin"*
   - *"Yaşlı annem ilaç bulamıyor"*
5. 📢 **"Yardım Çağır"** butonuna bas
6. ✅ Yapay zeka otomatik öncelik atar ve AFAD'ı bilgilendirir

### 🚑 AFAD Görevlisi (Müdahale)

1. 🔐 `http://[drone_ip]:1856/login.html` adresinden **giriş yap**
2. 🗺️ AFAD panelinde **tüm yardım taleplerini haritada gör**
   - 🔴 Kırmızı = Yüksek Öncelik (hayati tehlike)
   - 🟡 Sarı = Orta Öncelik (sağlık, barınma)
   - 🟢 Yeşil = Düşük Öncelik (bilgi talebi)
3. 🎯 Bir talebi seç → **"Müdahale Ediliyor"** işaretle
4. 🚗 Olay yerine ulaş → **"Kurtarıldı"** olarak işaretle
5. ✅ Sistem otomatik arşivler (3 saniye sonra listeden kaybolur)

### 👑 Admin (Kullanıcı Yönetimi)

1. 🔐 Admin hesabıyla giriş yap
2. 👥 Yeni AFAD görevlisi ekle veya mevcut kullanıcıları düzenle
3. 📊 Sistem istatistiklerini görüntüle
   - Toplam talep sayısı
   - Aktif talepler
   - Kurtarılanlar
   - Yüksek öncelikli vakalar

---

## 🤖 Yapay Zeka Önceliklendirme

AI, yardım mesajlarını **anlam analizi** yaparak otomatik öncelik atar:

| Öncelik | Durum | Örnek Mesajlar |
|---------|-------|----------------|
| 🔴 **HIGH** | Hayati tehlike, ciddi yaralanma, enkaz altı | *"Enkaz altındayım, kan kaybediyorum"*<br>*"Çocuk boğuluyor, acil yardım!"*<br>*"Hamile eşim sancılanıyor"* |
| 🟡 **MEDIUM** | Sağlık sorunu, barınma, temel ihtiyaç | *"Kronik hastayım, ilaçlarım bitti"*<br>*"Çadır alanında yerimiz yok"*<br>*"Bebek maması bulamıyoruz"* |
| 🟢 **LOW** | Bilgi talebi, konfor, uzun vadeli | *"Su dağıtımı ne zaman başlar?"*<br>*"Okul ne zaman açılır?"*<br>*"Wifi bağlantısı kötü"* |

### 📊 Model Detayları:
- **Algoritma**: TF-IDF + Linear SVC (Support Vector Classification)
- **Eğitim Verisi**: 280+ Türkçe deprem senaryosu
- **Doğruluk**: ~%92 (F1 Weighted Score)
- **Dil**: Türkçe stop-words filtreleme
- **Özellik**: N-gram (1-3 kelime grupları) analizi

---

## 🎥 Demo Video

<div align="center">

[![İHA-NET Demo Video](https://img.youtube.com/vi/JWqFQJuuc9o/maxresdefault.jpg)](https://youtu.be/JWqFQJuuc9o)

### 🎬 [YouTube'da İzle](https://youtu.be/JWqFQJuuc9o)

**Video İçeriği:**
- ✅ Drone WiFi ağı kurulumu ve bağlantı
- ✅ Depremzede yardım çağırma süreci
- ✅ AFAD panelinde müdahale yönetimi
- ✅ Gerçek zamanlı harita takibi
- ✅ AI önceliklendirme gösterimi
- ✅ Yer kontrol istasyonu telemetri izleme

</div>

---

## 📂 Proje Yapısı

```
iha-net/
│
├── 📄 app.py                      # Ana Flask web uygulaması (Port: 1856)
├── ⚙️ config.py                   # Tüm sistem yapılandırma ayarları
├── 🤖 ai_prioritizer.py           # Yapay zeka önceliklendirme modülü
├── 🚁 mavlink.py                  # Drone kontrol servisi (Port: 8001)
├── 📡 mavlink_sunucu.py           # Telemetri ara sunucu (Port: 14650)
├── 🖥️ yer_kontrol.py              # Yer kontrol web arayüzü (Port: 1857)
├── 🛤️ rota_yukleme.py             # Drone waypoint yükleme modülü
├── 📋 requirements.txt            # Python bağımlılıkları
├── ▶️ start_system.bat            # Otomatik sistem başlatma scripti
├── 🗺️ rota.waypoints              # Drone rota dosyası
│
├── 🧠 AI Model Dosyaları
│   ├── prioritizer_model.joblib   # Eğitilmiş sınıflandırma modeli
│   └── vectorizer.joblib          # TF-IDF vektörleyici
│
├── 💾 instance/
│   └── site.db                    # SQLite veritabanı (otomatik oluşur)
│
├── 🌐 templates/                  # HTML şablonları
│   ├── index.html                 # Ana sayfa
│   ├── depremzede.html            # Yardım çağırma sayfası
│   ├── login.html                 # Giriş sayfası
│   ├── afad.html                  # AFAD yönetim paneli
│   ├── admin_panel.html           # Admin paneli
│   ├── yer.html                   # Yer kontrol arayüzü
│   └── old_templates/             # Eski versiyonlar (yedek)
│
└── 📸 assets/                     # Ekran görüntüleri ve medya
    ├── depremzede_screenshot.png
    ├── afad_panel_screenshot.png
    ├── admin_screenshot.png
    └── yer_kontrol_screenshot.png
```

---

## ⚙️ Yapılandırma (`config.py`)

Tüm sistem ayarları `config.py` dosyasında merkezi olarak yönetilir:

```python
# 🌐 Uygulama Ayarları
APP_HOST = '0.0.0.0'              # Tüm ağ arayüzlerinden erişim
APP_PORT = 1856                   # Ana web uygulaması portu

# 🔐 Güvenlik
SECRET_KEY = 'your_secret_key'    # Flask session key (DEĞİŞTİRİN!)

# 🚁 Drone Bağlantısı
VEHICLE_CONNECTION_STRING = "tcp:127.0.0.1:5762"  # Simülasyon için
# VEHICLE_CONNECTION_STRING = "COM3"              # Gerçek Pixhawk için

# 📡 WiFi Ağ Ayarları
YER_KONTROL_HOST = '10.15.157.77'  # Drone'un yayınladığı WiFi IP
YER_KONTROL_PORT = 1857            # Yer kontrol portu

# 🗺️ Rota Dosyası
ROTA_YUKLEME_DOSYASI = "rota.waypoints"  # Mission Planner/QGC formatı

# 👥 Varsayılan Hesaplar
DEFAULT_ADMIN_USERNAME = 'admin'
DEFAULT_ADMIN_PASSWORD = 'admin123'        # ⚠️ DEĞİŞTİRİN!
DEFAULT_AFAD_USERNAME = 'afad_gorevlisi'
DEFAULT_AFAD_PASSWORD = 'afad123'          # ⚠️ DEĞİŞTİRİN!
```

### Önemli Notlar:

1. **Gerçek Kullanım**: `YER_KONTROL_HOST`'u drone WiFi IP'sine göre değiştirin
2. **Güvenlik**: `SECRET_KEY` ve tüm şifreleri üretimde mutlaka değiştirin
3. **Drone Bağlantısı**:
   - Simülasyon: `tcp:127.0.0.1:5762`
   - Gerçek Pixhawk: `COM3` (Windows) veya `/dev/ttyUSB0` (Linux)

---

## 🔧 Sorun Giderme

### ❌ Paket Kurulum Hataları

**Hata**: `"sklearn' PyPI package is deprecated"`
```powershell
# ✅ Doğru komut
pip install scikit-learn

# ❌ Yanlış komut (kullanmayın)
pip install sklearn
```

**Hata**: `ModuleNotFoundError: No module named 'xyz'`
```powershell
pip install xyz
# veya tümünü tekrar yükle
pip install -r requirements.txt
```

---

### ❌ Port Kullanımda Hatası

**Hata**: `OSError: [WinError 10048] Only one usage of each socket address`

```powershell
# Port 1856'yı kullanan işlemi bul
netstat -ano | findstr :1856

# İşlemi sonlandır (PID'yi yukarıdaki komuttan alın)
taskkill /PID <PID> /F
```

---

### ❌ Drone Bağlanamıyor

**Hata**: `Connection error: tcp:127.0.0.1:5762`

**Çözüm 1 - Simülasyon İçin:**
- ArduPilot SITL'in çalıştığından emin olun
- Mission Planner veya QGroundControl başlatın

**Çözüm 2 - Gerçek Drone İçin:**
```python
# config.py dosyasında değiştirin
VEHICLE_CONNECTION_STRING = "COM3"  # veya /dev/ttyUSB0
```

---

### ❌ Veritabanı Bozulması

```powershell
# Veritabanını sıfırla
Remove-Item instance\site.db -Force

# Uygulamayı tekrar başlat (otomatik oluşturur)
python app.py
```

---

### ❌ AI Modeli Yüklenmiyor

**Hata**: `[AI] Model yüklenemedi. Varsayılan öncelik 'high' atandı.`

```powershell
# Eski model dosyalarını sil
Remove-Item prioritizer_model.joblib -Force
Remove-Item vectorizer.joblib -Force

# Modeli yeniden eğit
python ai_prioritizer.py
```

---

### ❌ Yer Kontrol Bağlanamıyor

1. **IP Adresini Kontrol Edin:**
```python
# config.py
YER_KONTROL_HOST = '0.0.0.0'  # Tüm arayüzlerden erişim için
```

2. **Firewall Kuralı Ekleyin:**
```powershell
New-NetFirewallRule -DisplayName "Yer Kontrol" -Direction Inbound -LocalPort 1857 -Protocol TCP -Action Allow
```

3. **Kendi IP'nizi Öğrenin:**
```powershell
ipconfig
# IPv4 Address'i not alın
```

---

## 🛡️ Güvenlik ve Üretim Notları

### ⚠️ Üretim Ortamı İçin Mutlaka Yapın:

1. **Şifreleri Değiştirin**
```python
# config.py
DEFAULT_ADMIN_PASSWORD = 'guclu_sifre_123!'
DEFAULT_AFAD_PASSWORD = 'baska_guclu_sifre_456!'
```

2. **Secret Key Oluşturun**
```python
import secrets
SECRET_KEY = secrets.token_hex(32)
# Çıktıyı config.py'ye kopyalayın
```

3. **Debug Modunu Kapatın**
```python
# app.py, yer_kontrol.py, mavlink_sunucu.py
app.run(debug=False, host=host_ip, port=port_num)
```

4. **HTTPS Kullanın**
- SSL sertifikası ekleyin
- Let's Encrypt ücretsiz sertifika sağlar

5. **Düzenli Yedek Alın**
```powershell
# Veritabanı yedeği
Copy-Item instance\site.db backups\site_$(Get-Date -Format 'yyyyMMdd_HHmmss').db
```

6. **Firewall Ayarları**
- Sadece gerekli portları açın (1856, 1857, 8001, 14650)
- IP whitelist kullanın

---

## 🤝 Katkıda Bulunma ve Geliştirme

Bu proje **afet yönetimi** için açık kaynak olarak geliştirilmiştir.

### Geliştirme Fikirleri:

- 📱 **Mobil Uygulama**: React Native / Flutter ile iOS/Android versiyonu
- 🔔 **Push Bildirimler**: WebSocket ile gerçek zamanlı uyarılar
- 🌐 **Çoklu Dil Desteği**: İngilizce, Arapça eklenebilir
- 📶 **Offline Mod**: İnternet kesilse bile çalışabilir
- 🗺️ **3D Harita**: Cesium.js ile 3 boyutlu görselleştirme
- 📊 **Gelişmiş AI**: BERT / GPT modelleri ile daha iyi analiz
- 🎤 **Sesli Mesaj**: Yazamayanlar için sesli yardım çağrısı
- 📸 **Fotoğraf Yükleme**: Durumu görsel olarak paylaşma

### Kod Katkısı:

1. Fork yapın
2. Feature branch oluşturun (`git checkout -b feature/YeniOzellik`)
3. Commit atın (`git commit -m 'Yeni özellik: XYZ'`)
4. Push yapın (`git push origin feature/YeniOzellik`)
5. Pull Request açın

---

## 📄 Lisans

Bu proje **eğitim ve afet yönetimi** amaçlı geliştirilmiştir. Ticari kullanım için lütfen iletişime geçin.

---

## 📞 İletişim ve Destek

- 🎬 **Demo Video**: [YouTube](https://youtu.be/JWqFQJuuc9o)
- 📧 **Destek**: GitHub Issues
- 🌐 **Dokümantasyon**: Bu README dosyası

---

## 🏆 Teknoloji Stack

| Katman | Teknoloji |
|--------|-----------|
| **Backend** | Flask 2.3.3, Python 3.8+ |
| **Veritabanı** | SQLite (SQLAlchemy ORM) |
| **Yapay Zeka** | Scikit-Learn (TF-IDF + SVM) |
| **Drone İletişim** | DroneKit, MAVLink |
| **Frontend** | HTML5, CSS3, JavaScript, Leaflet.js |
| **Harita** | OpenStreetMap, Leaflet |
| **Kimlik Doğrulama** | Flask-Login |
| **GUI (Yer Kontrol)** | PyQt5 |

---

<div align="center">

## 🚁 **Hayat Kurtarır - Sorumlu Kullanın**

*Bu sistem deprem bölgelerinde iletişim köprüsü kurarak, yapay zeka desteğiyle arama kurtarma ekiplerinin daha hızlı ve etkili müdahale etmesini sağlar.*

### 🌟 [Demo Videoyu İzle](https://youtu.be/JWqFQJuuc9o) 🌟

---

**Geliştirici:** İHA-NET Ekibi  
**Tarih:** 2025  
**Versiyon:** 1.0.0

[![Made with ❤️ for Humanity](https://img.shields.io/badge/Made%20with-%E2%9D%A4%EF%B8%8F-red?style=for-the-badge)](https://github.com)

</div>
