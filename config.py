# config.py

class Config:
    # --- Uygulama Ayarları ---
    APP_HOST = '0.0.0.0'
    APP_PORT = 1856
    SECRET_KEY = 'sizin_cok_gizli_anahtariniz_kimse_tahmin_edemez_lutfen_degistirin'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///site.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # --- Yer Kontrol İstasyonu Ayarları ---
    YER_KONTROL_HOST = '10.15.157.77' # yer_kontrol.py'nin çalıştığı IP adresi
    YER_KONTROL_PORT = 1857

    # --- Mavlink İletişim Ayarları (Drone/Simülatör) ---
    MAVLINK_HOST = '127.0.0.1' # mavlink.py'nin çalıştığı IP adresi
    MAVLINK_PORT = 8001
    VEHICLE_CONNECTION_STRING = "tcp:127.0.0.1:5762" # Dronekit bağlantı adresi (tcp: simülasyon için)
    ROTA_YUKLEME_DOSYASI = "D:/Hackathon/yer_kontrol_yeni/rota.waypoints" # Rota dosyası yolu

    # --- Mavlink Aracı Sunucu Ayarları (mavlink_sunucu.py) ---
    MAVLINK_SUNUCU_HOST = '127.0.0.1'
    MAVLINK_SUNUCU_PORT = 14650

    # --- Yapay Zeka (AI) Ayarları ---
    AI_MODEL_PATH = 'prioritizer_model.joblib'
    AI_VECTORIZER_PATH = 'vectorizer.joblib'
    AI_TRAIN_TEST_SPLIT_SIZE = 0.2
    AI_RANDOM_STATE = 42 # Modelin yeniden üretilebilirliği için
    AI_MAX_FEATURES = 5000 # TfidfVectorizer için kelime sayısı
    AI_NGRAM_RANGE = (1, 3) # N-gram aralığı (1'li ve 2'li, 3'lü kelime grupları)
    AI_MIN_DF = 2 # Minimum doküman sıklığı
    AI_LINEAR_SVC_C = 1.0 # LinearSVC C parametresi
    AI_LINEAR_SVC_MAX_ITER = 5000 # LinearSVC için maksimum iterasyon sayısı (ConvergenceWarning için artırıldı)

    # --- Kullanıcı Yönetimi Ayarları (Başlangıç Admin) ---
    DEFAULT_ADMIN_USERNAME = 'admin'
    DEFAULT_ADMIN_PASSWORD = 'admin123'
    DEFAULT_AFAD_USERNAME = 'afad_gorevlisi'
    DEFAULT_AFAD_PASSWORD = 'afad123'

    # --- Diğer Genel Ayarlar ---
    TELEMETRY_UPDATE_INTERVAL_SEC = 0.5 # Telemetri güncelleme sıklığı (saniye)
    AFAD_DATA_FETCH_INTERVAL_SEC = 3 # AFAD paneli veri çekme sıklığı (saniye)
    ADMIN_STATS_FETCH_INTERVAL_SEC = 10 # Admin paneli istatistik çekme sıklığı (saniye)
    ADMIN_USERS_FETCH_INTERVAL_SEC = 15 # Admin paneli kullanıcı listesi çekme sıklığı (saniye)