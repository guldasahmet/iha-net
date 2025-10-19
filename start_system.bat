@echo off
echo AFAD Arama Kurtarma Sistemi başlatılıyor...
echo.
echo Her bir servis yeni bir komut istemi penceresinde başlatılıyor.
echo Lütfen bu pencereleri kapatmayın.

:: echo Gerekli gereksinimler indiriliyor.
:: start cmd /k "pip install -r requirements.txt"

echo app.py başlatılıyor...
start cmd /k "python app.py"

:: ai_prioritizer.py'yi başlat (Yapay Zeka modeli eğitimi/yüklemesi için)
:: Bu betik genellikle bir kez çalışıp model dosyalarını oluşturur veya yükler.
:: Eger modeli manuel olarak eğitmek veya yüklemek isterseniz, bu satirdaki '::' isaretlerini kaldirin.
:: echo ai_prioritizer.py başlatılıyor (eğitim/yükleme için)...
:: start cmd /k "python ai_prioritizer.py"

start cmd /k python -m http.server 8000

echo mavlink_sunucu.py başlatılıyor...
start cmd /k "python mavlink_sunucu.py"

echo mavlink.py başlatılıyor...
start cmd /k "python mavlink.py"

echo yer_kontrol.py başlatılıyor...
start cmd /k "python yer_kontrol.py"

echo.
echo Tum servisler baslatildi.
echo Sistemin web arayuzune erismek icin:
echo Genel Giris: http://[app_host]:[app_port]/ (Orn: http://0.0.0.0:1856/)
echo Depremzede Sayfasi: http://[app_host]:[app_port]/depremzede.html
echo Gorevli Girisi: http://[app_host]:[app_port]/login.html
echo AFAD Yonetim Paneli: http://[app_host]:[app_port]/afad.html
echo Admin Paneli: http://[app_host]:[app_port]/admin_panel.html
echo.
echo Yer Kontrol Istasyonu (Drone Telemetrisi): http://[yer_kontrol_host]:[yer_kontrol_port]/
echo (Orn: http://10.15.189.243:5000/)
echo.
echo Servisleri durdurmak icin her bir komut istemi penceresini tek tek kapatabilirsiniz.
echo.
echo Bu pencereyi kapatmak icin bir tusa basin...
pause > nul