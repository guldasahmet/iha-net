# Sunucu ara bağlantısı
# iki yer kontrol istasyonunun haberleşmesi ve telemetri verilerini alması için bir Flask uygulaması oluşturulmuştur.
import requests
import ctypes
from flask import Flask, request, jsonify

from config import Config # Config dosyasını import et

app = Flask(__name__)

# GET : Veri almak için
# POST : Veri göndermek için

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

kilitlenme_bilgisi_gonderildi = False

@app.route('/api/telemetri_gonder', methods=['POST'])
def telemetri_gonder(): # Yardımcı YKİ telemetri bilgisini buraya yollayacak
    global telemetry_data
    try:
        data = request.json
        if data is None:
            return 'JSON verisi bulunamadı', 400

        # Telemetri verilerini güncelle
        telemetry_data.update(data)
        print(data)
        print("Telemetri Verisi Alındı:")
        #print(telemetry_data)

        return 'Veri alındı', 200

    except Exception as e:
        print(f'Hata: {e}')
        return 'Bir hata oluştu', 500


@app.route('/api/telemetri_oku', methods=['GET'])
def get_telemetri_bilgisi():
    global telemetry_data

    if telemetry_data is None:
        response = jsonify("None")
        return response, 200

    # Veriyi döndür ve ardından sıfırla
    response = jsonify(telemetry_data)
    return response, 200

if __name__ == '__main__':
    # Config dosyasından host ve port bilgisini al
    app.run(host=Config.MAVLINK_SUNUCU_HOST, port=Config.MAVLINK_SUNUCU_PORT, debug=True)
