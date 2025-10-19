from flask import Flask, render_template, request, jsonify
import threading
import time
import collections.abc
import collections
collections.MutableMapping = collections.abc.MutableMapping
from dronekit import connect ,VehicleMode , Command, LocationGlobalRelative , mavutil
import requests
import numpy as np

from config import Config # Config dosyasını import et

app = Flask(__name__)

def oranlama(deger, eski_min, eski_max, yeni_min, yeni_max): # oran orantı
        # Eski aralıktaki değerin normalleştirilmesi
        if deger >= 0 :
            return deger
        else:
            normal_deger = (deger - eski_min) / (eski_max - eski_min)
            # Yeni aralıktaki değerin hesaplanması
            yeni_deger = normal_deger * (yeni_max - yeni_min) + yeni_min
            return abs(yeni_deger) + 180

GROUPS = {
    "acil_destek": [],
    "ihtiyac_dagitimi": [],
    "anons": [],
    "depremzede_durumu": []
}

# Örnek telemetri verisi (bunu Python'dan güncelleyebilirsin)
telemetry_data = {
    "airspeed": 0,
    "altitude": 0,
    "groundspeed": 0,
    "latitude": 40.2376335,
    "longitude": 29.0081634,
    "yaw": 0,
    "pitch": 0,
    "roll": 0,
    "signalQuality": 0,
    "battery": 0
}

@app.route('/')
def home():
    return render_template('yer.html')

@app.route('/api/telemetry', methods=['GET'])
def get_telemetry():
    return jsonify(telemetry_data)

@app.route('/api/telemetry', methods=['POST'])
def update_telemetry():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Veri yok"}), 400
    telemetry_data.update(data)
    return jsonify({"status": "ok"})

@app.route('/api/koordinat_ekle', methods=['POST'])
def koordinat_ekle():
    # Config dosyasından Mavlink host ve portunu al
    API_BASE = f"http://{Config.MAVLINK_HOST}:{Config.MAVLINK_PORT}"
    data = request.get_json()
    if not data or "lat" not in data or "lon" not in data:
        return jsonify({"error": "Eksik veri"}), 400
    if "koordinatlar" not in telemetry_data or not isinstance(telemetry_data["koordinatlar"], list):
        telemetry_data["koordinatlar"] = []
    telemetry_data["koordinatlar"].append({"lat": data["lat"], "lon": data["lon"]})
    response = requests.post(f"{API_BASE}/api/koordinat_ekle", json={"lat": data["lat"], "lon": data["lon"], "set_home": True}, timeout=5)
    print(f"Haritada tıklanan koordinat: lat={data['lat']}, lon={data['lon']}")  # <-- koordinatı yazdır
    return jsonify({"status": "ok", "lat": data["lat"], "lon": data["lon"]})

@app.route('/api/koordinatlar', methods=['GET'])
def get_koordinatlar():
    return jsonify(telemetry_data.get("koordinatlar", []))


def telemetry_loop():
    while True:
        # Config dosyasından ara sunucu IP ve portunu al
        ara_sunucu_ip = f"{Config.MAVLINK_SUNUCU_HOST}:{Config.MAVLINK_SUNUCU_PORT}"
        url = f"http://{ara_sunucu_ip}/api/telemetri_oku"  # <-- endpoint düzeltildi
        try:
            response = requests.get(url, timeout=2)
            if response.status_code == 200:
                try:
                    sonuc = response.json()
                    print(sonuc)
                    telemetry_data.update(sonuc)
                    telemetry_data["yaw"] = oranlama(float(telemetry_data["yaw"]* (180.0 / np.pi)),-180,0,0,180)
                except Exception:
                    print("JSON decode hatası, dönen veri:", response.text)
            else:
                print(f"Sunucu {url} HTTP hata kodu:", response.status_code)
        except Exception as e:
            print(f"Ara sunucuya bağlanılamadı: {e}")
        # Gerekirse diğer alanları da güncelle
        time.sleep(Config.TELEMETRY_UPDATE_INTERVAL_SEC)  # Config'den telemetri güncelleme sıklığını al

if __name__ == '__main__':
    # Sürekli çalışan döngüyü başlat
    t = threading.Thread(target=telemetry_loop, daemon=True)
    t.start()
    # Config dosyasından host ve port bilgisini al
    app.run(debug=True, host=Config.YER_KONTROL_HOST, port=Config.YER_KONTROL_PORT)
