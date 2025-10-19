import requests
import ctypes
import time
import collections.abc
import collections
collections.MutableMapping = collections.abc.MutableMapping
from dronekit import connect, VehicleMode, Command, LocationGlobal, LocationGlobalRelative, mavutil
from flask import Flask, request, jsonify
from flask_cors import CORS

import threading
from config import Config # Config dosyasını import et

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
    "battery": 0,
    "koordinatlar": [  # <-- Nokta koyulacak koordinatlar
        {"lat": 40.237, "lon": 29.008},
        {"lat": 40.238, "lon": 29.009}
        # ...istediğin kadar ekle...
    ] 
}

# Config dosyasından bağlantı string'ini al
vehicle = connect(Config.VEHICLE_CONNECTION_STRING, wait_ready=True, timeout=100) # Araç Bağlantısı # tcp = simülasyon # COMX = Pixhawk
# Config dosyasından ara sunucu IP ve portunu al
ara_sunucu_ip = f"{Config.MAVLINK_SUNUCU_HOST}:{Config.MAVLINK_SUNUCU_PORT}"

# Bu liste artık kullanılmayacak, doğrudan telemetry_data["koordinatlar"] kullanılacak
# koordinatlar = []

app = Flask(__name__)
CORS(app)  # Tüm endpoint'ler için CORS'u aç

@app.route('/api/koordinat_ekle', methods=['POST'])
def koordinat_ekle():
    print("Koordinat ekleme isteği alındı.")
    data = request.get_json()
    if not data or "lat" not in data or "lon" not in data:
        return jsonify({"error": "Eksik veri"}), 400

    # YENİ: Gelen koordinatları doğrudan telemetry_data["koordinatlar"] listesine ekle
    # Eğer telemetry_data["koordinatlar"] mevcut değilse veya liste değilse, oluştur
    if "koordinatlar" not in telemetry_data or not isinstance(telemetry_data["koordinatlar"], list):
        telemetry_data["koordinatlar"] = []
    telemetry_data["koordinatlar"].append({"lat": data["lat"], "lon": data["lon"]})

    print(f"Haritada tıklanan koordinat (mavlink.py): lat={data['lat']}, lon={data['lon']}")

    if data.get("set_home"):
        try:
            # 1. Home konumunu ayarla
            home_location = LocationGlobal(data["lat"], data["lon"], 0)
            vehicle.home_location = home_location
            print(f"Ev konumu ayarlandı: {home_location}")
            if hasattr(vehicle, "flush"):
                vehicle.flush()
            time.sleep(2)

            # 2. GUIDED moduna geç
            vehicle.mode = VehicleMode("RTL")
            vehicle.flush()


        except Exception as e:
            print(f"Home konumu ayarlanırken hata: {e}")
            return jsonify({"error": str(e)}), 500

    if data.get("rtl"):
        try:
            vehicle.mode = VehicleMode("RTL")
            vehicle.flush()
            print("Araç manuel RTL moduna alındı.")
        except Exception as e:
            print(f"RTL komutu gönderilirken hata: {e}")
            return jsonify({"error": str(e)}), 500

    return jsonify({"status": "ok", "lat": data["lat"], "lon": data["lon"]})

@app.route('/api/ag_yay', methods=['POST'])
def ag_yay():
    print("Ağ yayma komutu alındı.")
    try:
        # Burada ağ yayma fonksiyonunu çağıracaksın
        ag_yay_fonksiyonu()
        return jsonify({"status": "ok", "message": "Ağ yayma işlemi başlatıldı"})
    except Exception as e:
        print(f"Ağ yayma hatası: {e}")
        return jsonify({"error": str(e)}), 500

def ag_yay_fonksiyonu():
    # Bu fonksiyonun içini sen dolduracaksın
    upload_mission()
    print("Ağ yayma fonksiyonu çalıştırıldı - içerik boş")


def flask_thread():
    # Config dosyasından host ve port bilgisini al
    app.run(host=Config.MAVLINK_HOST, port=Config.MAVLINK_PORT, debug=False)

def set_home():
    global vehicle
    home_location = vehicle.location.global_relative_frame
    print(f"Ev konumu ayarlandı: {home_location}")
    vehicle.home_location = home_location

# Config dosyasından rota dosyasının yolunu al
aFileName = Config.ROTA_YUKLEME_DOSYASI
waypoints = []

def upload_mission():
    missionlist = readmission()

    cmds = vehicle.commands
    cmds.clear()
    for command in missionlist:
        cmds.add(command)
    vehicle.commands.upload()

    vehicle.commands.next = 0  # göreve baştan başlama / yeni

    time.sleep(1)
    vehicle.mode = VehicleMode("AUTO")

def readmission():
        missionlist=[]
        with open(aFileName) as f:
            for i, line in enumerate(f):
                if i==0:
                    if not line.startswith('QGC WPL 110'):
                        raise Exception('File is not supported WP version')
                else:
                    linearray=line.split('\t')
                    ln_index=int(linearray[0])
                    ln_currentwp=int(linearray[1])
                    ln_frame=int(linearray[2])
                    ln_command=int(linearray[3])
                    ln_param1=float(linearray[4])
                    ln_param2=float(linearray[5])
                    ln_param3=float(linearray[6])
                    ln_param4=float(linearray[7])
                    ln_param5=float(linearray[8])
                    ln_param6=float(linearray[9])
                    ln_param7=float(linearray[10])
                    ln_autocontinue=int(linearray[11].strip())
                    cmd = Command( 0, 0, 0, ln_frame, ln_command, ln_currentwp, ln_autocontinue, ln_param1, ln_param2, ln_param3, ln_param4, ln_param5, ln_param6, ln_param7)
                    missionlist.append(cmd)
                    waypoints.append([ln_param5,ln_param6,100])
        return missionlist


if __name__ == '__main__':
    threading.Thread(target=flask_thread, daemon=True).start()
    while True:

        telemetry_data["airspeed"] = vehicle.airspeed
        telemetry_data["altitude"] = vehicle.location.global_relative_frame.alt
        telemetry_data["groundspeed"] = vehicle.groundspeed
        telemetry_data["latitude"] = vehicle.location.global_frame.lat
        telemetry_data["longitude"] = vehicle.location.global_frame.lon
        telemetry_data["yaw"] = vehicle.attitude.yaw
        telemetry_data["pitch"] = vehicle.attitude.pitch
        telemetry_data["roll"] = vehicle.attitude.roll
        telemetry_data['signalQuality'] = 100
        telemetry_data['battery'] = 100
        telemetry_data["waypoints"] = waypoints
        telemetry_data["flight_mode"] = str(vehicle.mode.name)  # Uçuş modunu ekle

        # Eğer koordinatlar dinamik olacaksa burada güncelleyebilirsin
        # telemetry_data["koordinatlar"] = [{"lat": ..., "lon": ...}, ...]

        url = f"http://{ara_sunucu_ip}/api/telemetri_gonder"
        response = requests.post(url, json=telemetry_data)
        #print(koordinatlar)
        #print(response.status_code)
        # Eğer cevap JSON değilse hata almamak için:
        # try:
        #     sonuc = response.json()
        #     print(sonuc)
        # except Exception:
        #     print("JSON decode hatası, dönen veri:", response.text)
        time.sleep(Config.TELEMETRY_UPDATE_INTERVAL_SEC) # Config'den telemetri güncelleme sıklığını al
