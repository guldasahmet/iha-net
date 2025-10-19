from flask import Flask, jsonify, request, render_template, redirect, url_for, flash
from datetime import datetime
import os
import threading
import time
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import or_
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import requests # requests modülü eklendi

# YENİ IMPORT: Yapay Zeka modülümüzü ve yapılandırma dosyamızı içeri aktarıyoruz
from ai_prioritizer import predict_priority
from config import Config # Config dosyasını import et

app = Flask(__name__)

# --- UYGULAMA YAPILANDIRMASI ---
# Ayarları Config sınıfından al
app.config['SECRET_KEY'] = Config.SECRET_KEY
app.config['SQLALCHEMY_DATABASE_URI'] = Config.SQLALCHEMY_DATABASE_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = Config.SQLALCHEMY_TRACK_MODIFICATIONS
db = SQLAlchemy(app)

# --- FLASK-LOGIN YAPILANDIRMASI ---
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login_page'
login_manager.login_message = "Lütfen bu sayfaya erişmek için giriş yapın."
login_manager.login_message_category = "info" # Bu kategori artık JavaScript tarafından kullanılmıyor

# --- VERİTABANI MODELLERİ ---

# 1. RescueRequest Modeli (Yardım Talepleri)
class RescueRequest(db.Model):
    id = db.Column(db.String(50), primary_key=True, unique=True)
    lat = db.Column(db.Float, nullable=False)
    lng = db.Column(db.Float, nullable=False)
    adres = db.Column(db.String(200), nullable=False)
    durum = db.Column(db.String(20), nullable=False, default='bekleniyor')
    oncelik = db.Column(db.String(10), nullable=False, default='medium')
    tarih = db.Column(db.String(50), nullable=False)
    detay = db.Column(db.Text, nullable=True)

    is_active = db.Column(db.Boolean, default=True)
    kurtarilma_tarihi = db.Column(db.String(50), nullable=True)

    def __repr__(self):
        return f"RescueRequest('{self.id}', '{self.adres}', '{self.durum}', Active: {self.is_active})"

    def to_dict(self):
        return {
            "id": self.id,
            "konum": {
                "lat": self.lat,
                "lng": self.lng,
                "adres": self.adres
            },
            "durum": self.durum,
            "oncelik": self.oncelik,
            "tarih": self.tarih,
            "detay": self.detay,
            "is_active": self.is_active,
            "kurtarilma_tarihi": self.kurtarilma_tarihi
        }

# 2. User Modeli (Kullanıcılar ve Rolleri)
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='afad_gorevlisi') # 'admin' veya 'afad_gorevlisi'

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.username}>'

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'role': self.role
        }

# Flask-Login için kullanıcı yükleyici fonksiyonu
@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))

# --- ROL KONTROLÜ İÇİN DECORATOR'LAR ---
from functools import wraps

def role_required(allowed_roles):
    def decorator(f):
        @wraps(f)
        @login_required
        def decorated_function(*args, **kwargs):
            if current_user.role not in allowed_roles:
                # flash('Bu sayfaya erişim yetkiniz yok.', 'danger') # Flask flash mesajı yerine JS toast kullanılacak
                return redirect(url_for('login_page'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator

admin_required = role_required(['admin'])
afad_gorevlisi_required = role_required(['admin', 'afad_gorevlisi'])

# --- VERİTABANI OLUŞTURMA VE BAŞLANGIÇ VERİLERİ ---
with app.app_context():
    db.create_all()

    if not RescueRequest.query.first():
        sample_request = RescueRequest(
            id="KRT-001",
            lat=39.0576,
            lng=35.2540,
            adres="Kızılay Mh., Ankara",
            durum="bekleniyor",
            oncelik="high", # Varsayılan olarak yüksek öncelik
            tarih=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            detay="Enkaz altında 2 kişi var"
        )
        db.session.add(sample_request)
        db.session.commit()
        print("Veritabanına başlangıç yardım talebi eklendi: KRT-001")

    # Config'den varsayılan admin kullanıcı adını ve şifresini al
    if not User.query.filter_by(username=Config.DEFAULT_ADMIN_USERNAME).first():
        admin_user = User(username=Config.DEFAULT_ADMIN_USERNAME, role='admin')
        admin_user.set_password(Config.DEFAULT_ADMIN_PASSWORD)
        db.session.add(admin_user)
        db.session.commit()
        print(f"Admin hesabı oluşturuldu: {Config.DEFAULT_ADMIN_USERNAME}/{Config.DEFAULT_ADMIN_PASSWORD}")

    # Config'den varsayılan AFAD görevlisi kullanıcı adını ve şifresini al
    if not User.query.filter_by(username=Config.DEFAULT_AFAD_USERNAME).first():
        afad_user = User(username=Config.DEFAULT_AFAD_USERNAME, role='afad_gorevlisi')
        afad_user.set_password(Config.DEFAULT_AFAD_PASSWORD)
        db.session.add(afad_user)
        db.session.commit()
        print(f"AFAD görevlisi hesabı oluşturuldu: {Config.DEFAULT_AFAD_USERNAME}/{Config.DEFAULT_AFAD_PASSWORD}")


# --- ANA SAYFA VE YÖNLENDİRMELER ---
@app.route('/')
def main_index():
    return render_template('index.html')

@app.route('/depremzede.html')
def depremzede_page():
    return render_template('depremzede.html')

# --- GİRİŞ VE OTURUM YÖNETİMİ ---
@app.route('/login.html', methods=['GET', 'POST'])
def login_page():
    if current_user.is_authenticated:
        if current_user.role == 'admin':
            return redirect(url_for('admin_panel_page'))
        return redirect(url_for('afad_page'))

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        user = User.query.filter_by(username=username).first()

        if user and user.check_password(password):
            login_user(user)
            # flash('Başarıyla giriş yaptınız!', 'success') # Flash mesajı kaldırıldı
            if user.role == 'admin':
                return redirect(url_for('admin_panel_page'))
            return redirect(url_for('afad_page'))
        else:
            flash('Geçersiz kullanıcı adı veya şifre.', 'danger') # Login sayfasında hala flash kullanabiliriz
            return redirect(url_for('login_page'))

    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Başarıyla çıkış yaptınız.', 'success') # Çıkışta hala flash kullanabiliriz
    return redirect(url_for('main_index'))

# --- YETKİLENDİRİLMİŞ SAYFALAR ---
@app.route('/afad.html')
@afad_gorevlisi_required
def afad_page():
    return render_template('afad.html')

@app.route('/admin_panel.html')
@admin_required
def admin_panel_page():
    users = User.query.all()
    return render_template('admin_panel.html', users=users)

# --- AFAD API ENDPOINTS (Veritabanı Kullanımı ve Yetkilendirme) ---
@app.route('/api/veriler', methods=['GET'])
@afad_gorevlisi_required
def get_veriler_protected():
    active_requests = RescueRequest.query.filter_by(is_active=True).order_by(RescueRequest.tarih.asc()).all()
    data = [req.to_dict() for req in active_requests]
    print(f"[{datetime.now()}] API İsteği: /api/veriler - {len(data)} aktif veri döndürüldü")
    return jsonify(data)

@app.route('/api/durum-guncelle', methods=['POST'])
@afad_gorevlisi_required
def durum_guncelle_protected():
    try:
        data = request.get_json()
        rescue_id = data.get('id')
        new_status = data.get('durum')

        print(f"[{datetime.now()}] Durum Güncelleme: {rescue_id} -> {new_status}")

        rescue_req = db.session.get(RescueRequest, rescue_id)
        if not rescue_req:
            return jsonify({
                'success': False,
                'message': f'ID bulunamadı: {rescue_id}'
            }), 404

        old_status = rescue_req.durum
        rescue_req.durum = new_status
        rescue_req.tarih = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        if new_status == 'kurtarildi':
            rescue_req.is_active = False
            rescue_req.kurtarilma_tarihi = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            def remove_rescued_data_from_active_view_async(request_id_to_remove):
                time.sleep(Config.AFAD_DATA_FETCH_INTERVAL_SEC) # Config'den süre al
                print(f"[{datetime.now()}] Kurtarılan veri (ID: {request_id_to_remove}) aktif listeden kalkmak üzere işaretlendi (frontend animasyonu bekleniyor).")
            threading.Thread(target=remove_rescued_data_from_active_view_async, args=(rescue_id,)).start()

        db.session.commit()
        print(f"[{datetime.now()}] Başarılı: {rescue_id} durum değişti {old_status} -> {new_status} (DB'de güncellendi)")

        status_names = {
            'bekleniyor': 'Bekliyor',
            'mudahale': 'Müdahale Ediliyor',
            'kurtarildi': 'Kurtarıldı'
        }

        updated_active_requests = RescueRequest.query.filter_by(is_active=True).order_by(RescueRequest.tarih.asc()).all()
        updated_data = [req.to_dict() for req in updated_active_requests]

        return jsonify({
            'success': True,
            'message': f'{rescue_id} durumu güncellendi: {status_names.get(new_status, new_status)}',
            'data': updated_data
        })

    except Exception as e:
        db.session.rollback()
        print(f"[{datetime.now()}] Hata: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'Hata: {str(e)}'
        }), 500

@app.route('/api/veri-ekle', methods=['POST'])
@afad_gorevlisi_required
def veri_ekle_protected():
    try:
        data = request.get_json()
        return _add_rescue_data_internal(data)
    except Exception as e:
        print(f"[{datetime.now()}] Hata: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'Hata: {str(e)}'
        }), 500

def _add_rescue_data_internal(data):
    """Dahili kullanım için veri ekleme fonksiyonu (Veritabanına ekler)"""
    try:
        last_id_obj = db.session.query(RescueRequest.id).order_by(db.desc(RescueRequest.id)).first()
        if last_id_obj:
            last_id_num = int(last_id_obj[0].split('-')[1])
            new_id_num = last_id_num + 1
        else:
            new_id_num = 1
        new_id = f"KRT-{new_id_num:03d}"

        received_lat = data.get('lat')
        received_lng = data.get('lng')
        # Adres bilgisi artık frontend'den kesinlikle geliyor.
        received_adres = data.get('adres', 'Konum Bilinmiyor') # Varsayılan değer ekleyelim, ne olur ne olmaz

        detay_text = data.get('detay', '')
        predicted_priority = predict_priority(detay_text) # Yapay zeka tahmini burada

        new_request = RescueRequest(
            id=new_id,
            lat=float(received_lat) if received_lat is not None else 40.1885, # Bursa'nın Lat/Lng'i
            lng=float(received_lng) if received_lng is not None else 29.0609, # Bursa'nın Lat/Lng'i
            adres=received_adres,
            durum=data.get('durum', 'bekleniyor'),
            oncelik=predicted_priority, # Yapay zeka tahmini öncelik
            tarih=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            detay=detay_text,
            is_active=True
        )

        db.session.add(new_request)
        db.session.commit()
        print(f"[{datetime.now()}] Dahili yeni veri eklendi (DB): {new_id} (Öncelik: {predicted_priority})")

        # YENİ EKLEME: Mavlink.py'ye koordinatları gönder
        def send_coords_to_mavlink(lat, lng):
            try:
                mavlink_api_url = f"http://{Config.MAVLINK_HOST}:{Config.MAVLINK_PORT}/api/koordinat_ekle" # [cite: 1]
                payload = {"lat": lat, "lon": lng}
                response = requests.post(mavlink_api_url, json=payload, timeout=2) # [cite: 1]
                if response.status_code == 200:
                    print(f"[{datetime.now()}] Konum Mavlink.py'ye başarıyla gönderildi: {lat}, {lng}")
                else:
                    print(f"[{datetime.now()}] Konum Mavlink.py'ye gönderilirken hata: {response.status_code} - {response.text}")
            except requests.exceptions.RequestException as req_err:
                print(f"[{datetime.now()}] Konum Mavlink.py'ye gönderilirken bağlantı hatası: {req_err}")
            except Exception as e:
                print(f"[{datetime.now()}] Konum Mavlink.py'ye gönderilirken beklenmedik hata: {e}")

        # Konum gönderme işlemini ayrı bir thread'de başlat
        threading.Thread(target=send_coords_to_mavlink, args=(new_request.lat, new_request.lng,)).start()

        updated_active_requests = RescueRequest.query.filter_by(is_active=True).order_by(RescueRequest.tarih.asc()).all()
        updated_data = [req.to_dict() for req in updated_active_requests]

        # BURADA DÜZELTME: jsonify() yerine doğrudan dictionary ve status_code döndürüyoruz
        return {
            'success': True,
            'message': f'Yeni veri eklendi: {new_id}',
            'data': updated_data,
            'request_id': new_id
        }, 200

    except Exception as e:
        db.session.rollback()
        print(f"[{datetime.now()}] Hata (veri ekleme): {str(e)}")
        # BURADA DÜZELTME: jsonify() yerine doğrudan dictionary ve status_code döndürüyoruz
        return {
            'success': False,
            'message': f'Hata: {str(e)}'
        }, 500

@app.route('/api/veri-sil/<rescue_id>', methods=['DELETE'])
@afad_gorevlisi_required
def veri_sil_protected(rescue_id):
    try:
        rescue_req = db.session.get(RescueRequest, rescue_id)
        if not rescue_req:
            return jsonify({
                'success': False,
                'message': f'ID bulunamadı: {rescue_id}'
            }), 404

        rescue_req.is_active = False
        db.session.commit()

        print(f"[{datetime.now()}] Veri pasif hale getirildi: {rescue_id}")

        updated_active_requests = RescueRequest.query.filter_by(is_active=True).order_by(RescueRequest.tarih.asc()).all()
        updated_data = [req.to_dict() for req in updated_active_requests]

        return jsonify({
            'success': True,
            'message': f'{rescue_id} pasif hale getirildi',
            'data': updated_data
        })

    except Exception as e:
        db.session.rollback()
        print(f"[{datetime.now()}] Hata: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'Hata: {str(e)}'
        }), 500

@app.route('/api/istatistik', methods=['GET'])
@afad_gorevlisi_required
def istatistik_protected():
    try:
        total_requests = RescueRequest.query.count()
        active_requests = RescueRequest.query.filter_by(is_active=True).count()
        total_users = User.query.count()
        # Yeni İstatistikler
        high_priority_requests = RescueRequest.query.filter_by(is_active=True, oncelik='high').count()
        rescued_requests = RescueRequest.query.filter_by(is_active=False, durum='kurtarildi').count()


        stats = {
            'total_rescue_requests': total_requests,
            'active_rescue_requests': active_requests,
            'total_users': total_users,
            'high_priority_requests': high_priority_requests, # Yeni
            'rescued_requests': rescued_requests # Yeni
        }

        print(f"[{datetime.now()}] İstatistikler istendi: {stats}")
        return jsonify(stats)

    except Exception as e:
        print(f"[{datetime.now()}] Hata: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'Hata: {str(e)}'
        }), 500

# --- DEPREMZEDE YARDIM TALEBİ ENDPOINT'İ (Yapay Zeka Entegrasyonu) ---
@app.route('/api/yardim_talebi', methods=['POST'])
def yardim_talebi_al():
    try:
        data = request.get_json()
        not_text = data.get("not", "").strip()

        if not not_text:
            return jsonify({"success": False, "message": "Yardım notu boş olamaz."}), 400

        lat = data.get('lat')
        lng = data.get('lng')

        predicted_priority = predict_priority(not_text)
        print(f"[{datetime.now()}] Depremzede mesajı için yapay zeka öncelik tahmini: {predicted_priority}")

        ilan_data = {
            "lat": lat,
            "lng": lng,
            "adres": data.get('adres', 'Depremzede Bildirimi (Konum Bilinmiyor)'),
            "oncelik": predicted_priority,
            "detay": not_text
        }

        response_dict, status_code = _add_rescue_data_internal(ilan_data)

        if status_code == 200:
            return jsonify({
                "success": True,
                "message": "Yardım çağrınız başarıyla iletildi! Arama kurtarma ekipleri bilgilendirildi.",
                "request_id": response_dict.get('request_id')
            }), 200
        else:
            return jsonify({"success": False, "message": response_dict.get('message', 'Yardım talebi oluşturulurken bir hata oluştu.')}), status_code

    except Exception as e:
        print(f"[{datetime.now()}] Depremzede yardım talebi hatası: {str(e)}")
        return jsonify({"success": False, "message": f'Hata: {str(e)}'}), 500

# --- ADMİN PANELİ API ENDPOINTS ---
@app.route('/api/admin/users', methods=['GET'])
@admin_required
def get_users():
    users = User.query.all()
    # Kullanıcılar to_dict ile döndürüldüğünde, eğer veritabanında son_giris_tarihi gibi alanlar varsa,
    # bunlar da to_dict metoduna eklenerek frontend'e gönderilebilir. Şimdilik sadece ID, username, role var.
    return jsonify([user.to_dict() for user in users])

@app.route('/api/admin/register_user', methods=['POST'])
@admin_required
def register_user():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    role = data.get('role', 'afad_gorevlisi')

    if not username or not password:
        return jsonify({'success': False, 'message': 'Kullanıcı adı ve şifre boş bırakılamaz.'}), 400

    if User.query.filter_by(username=username).first():
        return jsonify({'success': False, 'message': 'Bu kullanıcı adı zaten mevcut.'}), 409

    new_user = User(username=username, role=role)
    new_user.set_password(password)

    try:
        db.session.add(new_user)
        db.session.commit()
        return jsonify({'success': True, 'message': f'{username} kullanıcısı başarıyla kaydedildi.', 'user': new_user.to_dict()}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'Kullanıcı kaydı sırasında hata: {str(e)}'}), 500

@app.route('/api/admin/delete_user/<int:user_id>', methods=['DELETE'])
@admin_required
def delete_user(user_id):
    user_to_delete = db.session.get(User, user_id)
    if not user_to_delete:
        return jsonify({'success': False, 'message': 'Kullanıcı bulunamadı.'}), 404

    # Kendi hesabını silmeyi engelle
    if user_to_delete.id == current_user.id:
        return jsonify({'success': False, 'message': 'Kendi hesabınızı silemezsiniz.'}), 403

    # Son admin hesabını silmeyi engelle
    if user_to_delete.role == 'admin' and User.query.filter_by(role='admin').count() == 1:
        return jsonify({'success': False, 'message': 'Sistemde en az bir admin hesabı bulunmalıdır.'}), 403

    try:
        db.session.delete(user_to_delete)
        db.session.commit()
        return jsonify({'success': True, 'message': f'{user_to_delete.username} kullanıcısı silindi.'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'Kullanıcı silinirken hata: {str(e)}'}), 500

@app.route('/api/admin/update_user/<int:user_id>', methods=['PUT'])
@admin_required
def update_user(user_id):
    user_to_update = db.session.get(User, user_id)
    if not user_to_update:
        return jsonify({'success': False, 'message': 'Kullanıcı bulunamadı.'}), 404

    data = request.get_json()
    new_role = data.get('role')
    new_password = data.get('password')

    # Kendi hesabının rolünü düşürmeyi veya tek adminse rolünü değiştirmeyi engelle
    if user_to_update.id == current_user.id and new_role and new_role != 'admin':
        return jsonify({'success': False, 'message': 'Kendi yöneticilik rolünüzü değiştiremez veya düşüremezsiniz.'}), 403

    # Eğer değiştirilmek istenen rol admin ise ve sistemde başka admin yoksa
    if new_role == 'afad_gorevlisi' and user_to_update.role == 'admin' and User.query.filter_by(role='admin').count() == 1:
         return jsonify({'success': False, 'message': 'Sistemde en az bir admin hesabı bulunmalıdır.'}), 403

    try:
        if new_role:
            user_to_update.role = new_role
        if new_password: # Şifre boş değilse güncelle
            user_to_update.set_password(new_password)

        db.session.commit()
        return jsonify({'success': True, 'message': f'{user_to_update.username} kullanıcısı başarıyla güncellendi.'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'Kullanıcı güncellenirken hata: {str(e)}'}), 500


@app.route('/api/admin/db_stats', methods=['GET'])
@admin_required
def get_db_stats():
    total_requests = RescueRequest.query.count()
    active_requests = RescueRequest.query.filter_by(is_active=True).count()
    total_users = User.query.count()
    # Yeni İstatistikler
    high_priority_requests = RescueRequest.query.filter_by(is_active=True, oncelik='high').count()
    rescued_requests = RescueRequest.query.filter_by(is_active=False, durum='kurtarildi').count()


    stats = {
        'total_rescue_requests': total_requests,
        'active_rescue_requests': active_requests,
        'total_users': total_users,
        'high_priority_requests': high_priority_requests,
        'rescued_requests': rescued_requests
    }

    print(f"[{datetime.now()}] İstatistikler istendi: {stats}")
    return jsonify(stats)


# --- UYGULAMA BAŞLATMA ---
if __name__ == '__main__':
    host_ip = Config.APP_HOST # Config'den host bilgisini al
    port_num = Config.APP_PORT # Config'den port bilgisini al

    print("=" * 60)
    print("🚑 ARAMA KURTARMA VE DEPREMZEDE SİSTEMİ BAŞLATILIYOR...")
    print("=" * 60)
    print(f"🌐 Genel Giriş Sayfası: http://{host_ip}:{port_num}/")
    print(f"🤝 Depremzede Yardım Çağır: http://{host_ip}:{port_num}/depremzede.html")
    print(f"🔐 Görevli Girişi: http://{host_ip}:{port_num}/login.html")
    print(f"⚙️ AFAD Yönetim Paneli (Giriş Sonrası): http://{host_ip}:{port_num}/afad.html")
    print(f"👑 Admin Paneli (Admin Girişi Sonrası): http://{host_ip}:{port_num}/admin_panel.html")
    print()
    print("📊 API Endpoints (Giriş Gerektirenler belirtilmiştir):")
    print("   GET    /api/veriler          - Tüm aktif verileri getir (Giriş Gerekli)")
    print("   POST   /api/durum-guncelle   - Durum güncelle (Giriş Gerekli)")
    print("   POST   /api/veri-ekle        - Yeni veri ekle (Giriş Gerekli)")
    print("   DELETE /api/veri-sil/<id>    - Veri sil (pasif hale getirir) (Giriş Gerekli)")
    print("   GET    /api/istatistik       - İstatistikleri getir (Giriş Gerekli)")
    print("   POST   /api/yardim_talebi    - Depremzededen yardım talebi al (Giriş Gerekmez)")
    print("   GET    /api/admin/users      - Tüm kullanıcıları getir (Admin Gerekli)")
    print("   POST   /api/admin/register_user - Yeni kullanıcı kaydet (Admin Gerekli)")
    print("   DELETE /api/admin/delete_user/<id> - Kullanıcı sil (Admin Gerekli)")
    print("   PUT    /api/admin/update_user/<id> - Kullanıcı bilgilerini güncelle (Admin Gerekli) (YENİ)")
    print("   GET    /api/admin/db_stats   - Veritabanı istatistikleri (Admin Gerekli)")
    print("=" * 60)

    templates_dir = os.path.join(os.path.dirname(__file__), 'templates')
    required_html_files = ['index.html', 'depremzede.html', 'login.html', 'afad.html', 'admin_panel.html']

    if not os.path.exists(templates_dir):
        print(f"❌ UYARI: 'templates' klasörü bulunamadı! Lütfen '{templates_dir}' dizinini oluşturun.")
    else:
        for filename in required_html_files:
            path = os.path.join(templates_dir, filename)
            if os.path.exists(path):
                print(f"✅ templates/{filename} dosyası bulundu")
            else:
                print(f"❌ UYARI: templates/{filename} dosyası bulunamadı! Lütfen '{templates_dir}' klasörünün içinde olduğundan emin olun.")

    print("=" * 60)
    print(f"Sunucu başlatılıyor... (IP: {host_ip}, Port: {port_num})")
    print("=" * 60)

    app.run(debug=True, host=host_ip, port=port_num)
