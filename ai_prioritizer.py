import joblib
import os
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.svm import LinearSVC
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.metrics import classification_report
from sklearn.exceptions import ConvergenceWarning
import warnings

# Yapılandırma dosyasını içeri aktarıyoruz
from config import Config

# Sklearn ConvergenceWarning'ları görmezden gel
warnings.filterwarnings("ignore", category=ConvergenceWarning)

# Türkçe Stop Words Listesi (Ortak ve anlamsız kelimeler)
TURKISH_STOP_WORDS = [
    "a", "acaba", "altı", "altmış", "ama", "amma", "ara", "arada", "artık", "asla", "aslında",
    "az", "bana", "bazen", "bazı", "bazıları", "bazısı", "belki", "ben", "bende", "beni",
    "benim", "beş", "bile", "bin", "bir", "birçok", "biri", "birkaç", "birkez", "birle",
    "böyle", "böylece", "buna", "bunda", "bundan", "bunlar", "bunları", "bunların", "bunu",
    "bunun", "burada", "bütün", "çoğu", "çoğuna", "çoğunu", "çok", "çünkü", "da", "daha",
    "dahi", "de", "defa", "değil", "demek", "diğer", "diye", "doksan", "dokuz", "dört",
    "elli", "en", "filan", "falan", "gene", "geri", "gibi", "hangi", "hangisi", "hani",
    "haricinde", "hariç", "hatta", "hem", "henüz", "her", "herhangi", "herkes", "herkese",
    "herkesi", "herkesin", "hiç", "hiçbir", "hiçbiri", "için", "iki", "ile", "ilk", "işte",
    "itibaren", "itibariyle", "kaç", "kadar", "karşın", "kendi", "kendine", "kendini",
    "kendinin", "kırk", "kim", "kime", "kimi", "kimin", "kimisi", "ki", "konu", "konusu",
    "madem", "mi", "mı", "nasıl", "ne", "neden", "nedense", "nerde", "nereden", "nereye",
    "neler", "neleri", "nelerin", "nesine", "neyse", "niçin", "o", "ona", "ondan", "onlar",
    "onlara", "onlardan", "onları", "onların", "onu", "onun", "otuz", "oysa", "oysaki",
    "pek", "rağmen", "sadece", "sanki", "sekiz", "seksen", "sen", "sende", "seni", "senin",
    "seksen", "sıra", "şimdi", "şöyle", "şu", "şuna", "şunlar", "şunu", "tabii", "tamam",
    "tamamen", "tane", "tek", "toplam", "trilyon", "tüm", "tümü", "üç", "üzere", "var",
    "vardı", "ve", "veya", "ya", "yani", "yedi", "yerine", "yetmiş", "yine", "yirmi", "yoksa",
    "yüz", "zira"
]

# Deprem odaklı örnek mesajlar ve öncelikler
# Yaralanma ve acil sağlık durumları en yüksek öncelikte olacak şekilde düzenlendi.

sample_messages = [
    # --- YÜKSEK ÖNCELİKLİ (HIGH PRIORITY) MESAJLAR: Hayati Tehlike / Ciddi Yaralanma / Acil Kurtarma ---
    "depremde enkaz altında kaldım, *yaralıyım*, acil yardım!",
    "binada çöküş var, 3. katta mahsur kaldık, nefes alamıyoruz!",
    "deprem sonrası hamile eşim sancılanıyor, doğum başlayabilir!",
    "çocuk enkaz altında kaldı, sesi geliyor, acil kurtarın!",
    "yaşlı komşum göçük altında, sesi duyuluyor, ekip lazım!",
    "depremde merdivenler çöktü, 4. katta mahsur kaldık!",
    "enkaz altındayız, karanlık, yardım sinyali veremiyoruz!",
    "deprem sonrası doğalgaz kokusu var, patlama tehlikesi!",
    "bina yıkıldı, ailem enkaz altında olabilir, acil arama!",
    "depremde sıkıştım, bacağım kırık, *kan kaybediyorum*!", # Vurgulandı
    "yaşlı baba kalp krizi geçirdi, deprem korkusundan!",
    "enkaz altında bebek ağlaması duyuyoruz, acil ekip!",
    "deprem sonrası asansörde mahsur kaldık, elektrik yok!",
    "çatı çöktü, altında *yaralılar* var, ambulans gerekli!",
    "balkon depremde çöktü, komşum *yaralandı*, acil yardım!",
    "beton parçası düştü, *ağır yaralıyız*, doktor lazım!",
    "deprem sonrası elektrik telleri koptu, çarpılma riski!",
    "duvar çöktü, altında kaldım, *çok ağır yaralıyım*!",
    "çocuğum depremde kayboldu, enkaz alanında arıyorum!",
    "deprem korkusundan diyabet hastası şok geçirdi!",
    "*kan kaybım* çok fazla, deprem yarasından, acil!", # Vurgulandı
    "nefes alamıyorum, göğsüm sıkışıyor, enkaz ağırlığından!",
    "bilinçsiz *yaralı* var, deprem sonrası, nabız zayıf!",
    "kemik kırığı açık, deprem yaralanması, acı çekiyor!",
    "enkaz altında çocuk sesleri, hayat kurtarın!",
    "enkaz altında kaldım, göğüs kafesim sıkıştı, nefes alamıyorum, acil!",
    "bina yan yatmış, her an çökebilir, içeride yaşlılar var!",
    "depremde kimyasal variller devrildi, zehirli gaz yayılıyor, acil tahliye!",
    "artçı sarsıntıda tavan çöktü, çocuğumun üzerine düştü, bilinçsiz!",
    "elektrik trafosu patladı, sokakta açıkta kablolar var, tehlikeli!",
    "enkazdan duman ve alevler yükseliyor, itfaiye acil!",
    "baraj duvarında büyük çatlaklar oluştu, yıkılma tehlikesi var!",
    "göçük altında kaldım, bacağım ezildi, *kan durmuyor*, acil cerrah!", # Vurgulandı
    "depremde hastanenin oksijen tankları patladı, büyük tehlike!",
    "yol yarıldı, araçlar içine düştü, çok sayıda *yaralı* var!",
    "enkaz altında bebek sesi duyuyorum, ama ulaşamıyorum, termal kamera lazım!",
    "deprem sonrası tsunami uyarısı yapıldı, kıyı bölgeleri acil boşaltılmalı!",
    "bina iskeleti zarar görmüş, yıkılmak üzere, içinde insanlar var!",
    "enkazda sıkışan birinin bacağı kopmak üzere, acil tıbbi müdahale!",
    "doğalgaz ana hattı patladı, mahallede büyük gaz sızıntısı var!",
    "artçı depremde kreş binası hasar gördü, çocuklar içerideydi!",
    "enkaz altında kaldım, su basıyor, boğulmak üzereyim!",
    "depremde viyadük çöktü, onlarca araç altında kaldı!",
    "radyoaktif madde taşıyan kamyon devrildi, sızıntı var!",
    "enkaz altında kalp hastası var, pili bitmek üzere, acil!",
    "alevler yükseliyor, yangın büyüyor, bina boşaltılmalı!",
    "çığ düştü, yol kapalı, mahsur kaldık, acil kurtarma!",
    "heyelan riski var, köy boşaltılmalı, evler kayıyor!",
    "patlama sesi duyuldu, kimyasal sızıntı olabilir, maske gerekli!",
    "bina çökmek üzere, içerdeki insanlar tahliye edilmeli, çabuk olun!",
    "*yaralı* çok, *kanaması* var, turnike lazım, doktor nerede?", # Vurgulandı
    "çocuklar panik içinde, nefes almakta zorlanıyorlar, psikolojik destek acil!",
    "doğalgaz borusu patladı, yangın kontrol altına alınamıyor, itfaiye nerede?",
    "enkazdan ağır koku geliyor, kimyasal zehirlenme olabilir, tehlikeli!",
    "yaşlı hastamızın solunum cihazı çalışmıyor, elektrik kesik, jeneratör lazım!",
    "köprü yıkıldı, ulaşım tamamen kesildi, karşıya geçemiyoruz!",
    "enkaz altından çığlık sesleri geliyor, ancak yerini tespit edemiyoruz, dinleme cihazı lazım!",
    "depremde annemin kalbi durdu, ilk yardım bilen var mı?",
    "bölgede salgın hastalık belirtileri var, ateş ve ishal, acil sağlık ekibi!",
    "su şebekesi patladı, her yer su altında, elektrik tehlikesi var!",
    "çocuklar enkaz altında sıkıştı, besinleri ve suları bitmek üzere, acil!",
    "büyük bir kaya parçası evimizin üzerine düştü, ailem içeride, yardıma gelin!",
    "depremde gözüme bir şey kaçtı, kör olabilirim, acil tıbbi yardım!",
    "enkaz altında bilinçsiz yatıyor, darbe almış, kafa travması olabilir!",
    "bina çatladı, her an yıkılabilir, yan binaya sıçrama riski var!",
    "çığ düştü, yollar kapalı, köylerde insanlar mahsur, kar ekipleri lazım!",
    "büyükbaş hayvanlar enkaz altında kaldı, açlık ve susuzluktan ölecekler, yardım edin!",
    "deprem sonrası psikolojik şok, insanlar bayılıyor, tıbbi yardım gerekli!",
    "enkazdan çıkarıldım ama *kötü kanamam* var, acil doktor!", # Yeni senaryo
    "başım *yaralı* ve *kanama* durmuyor, bayılacak gibiyim!", # Yeni senaryo
    "çocuğumun kolu sıkışmış, şişti ve *kanıyor*, çok ağlıyor!", # Yeni senaryo
    "depremde cam kesiği aldım, *kanaması* çok, lütfen yardım edin!", # Yeni senaryo
    "yaşlı hastamız düştü, kafasını vurdu ve *kanıyor*, bilinci kapanıyor!", # Yeni senaryo
    "iç kanamamdan şüpheleniyorum, karın ağrısı ve *kanlı* kusma var!", # Yeni senaryo
    "depremde bacağımda derin bir kesik oluştu, *kanamayı* durduramıyorum!", # Yeni senaryo

    # --- ORTA ÖNCELİKLİ (MEDIUM PRIORITY) MESAJLAR: Sağlık/Barınma/Temel İhtiyaç Sorunları ---
    "deprem sonrası evimiz çatlamış, güvenli mi girmek?",
    "çocuklar deprem korkusundan uyuyamıyor, travma yaşıyor.",
    "yaşlı annem ilaçlarını alamıyor, eczaneler depremde kapandı.",
    "bebek formülü bitti, deprem sonrası market kapalı.",
    "elektrik kesik, diyaliz hastası için jeneratör lazım.",
    "deprem sonrası *hafif yaralanmalar*, pansuman malzemesi gerekli.", # Hafif yaralanma orta öncelik
    "çadırda kalıyoruz, deprem sonrası evimiz hasar gördü.",
    "köpeğimiz depremde *yaralandı*, veteriner bulamıyoruz.", # Hayvan yaralanması orta öncelik
    "arabamız enkaz altında kaldı, içinde önemli eşyalar var.",
    "evimizin duvarında deprem çatlakları, tehlikeli mi?",
    "su arıtma sistemi depremde bozuldu, temiz su yok.",
    "çamaşır yıkayamıyoruz, deprem sonrası hijyen sorunu.",
    "tansiyon hastası baba kriz geçirdi, deprem stresi.",
    "hamile kardeşim kontrole gitmeli, deprem sonrası ulaşım yok.",
    "çocukların aşı zamanı, sağlık ocağı depremde hasar gördü.",
    "böbrek hastası diyaliz olamıyor, merkez kapalı.",
    "astım hastası nefes darlığı, deprem tozu soldu.",
    "şeker hastası insülin bulamıyor, eczane yıkık.",
    "yaşlı anne kalp ilaçları bitti, temin edemiyoruz.",
    "kızım depremde kayboldu, arama ekipleri var mı?",
    "evimizin duvarları çatladı, artçılardan korkuyoruz, çadır lazım.",
    "depremde sular kesildi, mahallede içme suyu sıkıntısı var.",
    "yaşlı komşumuzun ilaçları bitti, eczaneler yıkık, nasıl bulabiliriz?",
    "çadır alanında tuvaletler yetersiz, salgın hastalık riski var.",
    "depremde evcil hayvanımız kayboldu, gören oldu mu?",
    "*hafif yaralıyız*, pansuman ve ağrı kesiciye ihtiyacımız var.", # Hafif yaralanma orta öncelik
    "bebek maması ve temiz bez bulamıyoruz, yardım edin.",
    "deprem sonrası psikolojimiz bozuldu, destek alabileceğimiz bir yer var mı?",
    "evimiz az hasarlı ama elektrikler kesik, jeneratör ihtiyacımız var.",
    "artçı sarsıntılar devam ediyor, güvenli toplanma alanları nerede?",
    "depremde yıkılan evimizden eşyalarımızı çıkarmak için yardım lazım.",
    "çocuklar çok korkuyor, onlar için oyun ve aktivite alanı oluşturulabilir mi?",
    "kronik hastalığım var, düzenli kullanmam gereken ilaçlar enkazda kaldı.",
    "deprem bölgesinde iletişim çok zayıf, yakınlarımla haberleşemiyorum.",
    "yollar kapalı, şehir dışındaki akrabalarımızın yanına gidemiyoruz.",
    "çadırımız su alıyor, daha korunaklı bir barınma yerine ihtiyacımız var.",
    "depremde işyerim yıkıldı, geçim sıkıntısı çekiyorum, ne yapabilirim?",
    "hasar tespit ekipleri ne zaman gelecek, evimizin durumunu öğrenmek istiyoruz.",
    "deprem sonrası salgın hastalık riskine karşı aşı yapılmalı mı?",
    "enkazdan kurtarılanlar için geçici kimlik belgesi nasıl alınır?",
    "mahallemizde içme suyu bitti, tankerle su dağıtımı yapılabilir mi?",
    "bebekler için acil mama ve temiz suya ihtiyacımız var, stoklar tükendi.",
    "konserve gıda ve kuru bakliyat gibi dayanıklı yiyeceklere ihtiyacımız var.",
    "çadır kentteyiz, battaniye ve uyku tulumu eksiğimiz var, geceler soğuk.",
    "evimiz hasarlı, dışarıda kalıyoruz, acil barınma için çadır veya branda lazım.",
    "temel gıda malzemelerimiz (un, şeker, yağ) bitti, yardım bekliyoruz.",
    "yaşlı ve hastalar için özel beslenme ürünleri gerekiyor, bulamıyoruz.",
    "su arıtma tabletlerine veya temiz su kaynaklarına ihtiyacımız var.",
    "çadırımızın fermuarı bozuldu, soğuktan korunamıyoruz, tamir veya yenisi lazım.",
    "toplu yemek dağıtım noktaları nerede, bilgi alabilir miyiz?",
    "hijyen malzemeleri (sabun, tuvalet kağıdı, dezenfektan) tükendi, salgın riski var.",
    "çocuklar için süt ve vitamin takviyesine ihtiyacımız var.",
    "evimizdeki sağlam eşyaları çıkarmak için nakliye ve insan gücüne ihtiyacımız var.",
    "geçici mutfak kurmak için tüp ve ocak gibi malzemeler lazım.",
    "barınma alanımızda aydınlatma yok, gece güvenlik sorunu yaşıyoruz, fener veya lamba lazım.",
    "yakacak odun veya kömüre ihtiyacımız var, ısınamıyoruz.",
    "toplama merkezlerinde erzak dağıtımı ne zaman yapılacak?",
    "evimizdeki gıda stokları bozulmak üzere, soğuk hava deposu veya jeneratör lazım.",
    "çadır kentte yaşayanlar için düzenli sıcak yemek dağıtımı yapılmalı.",
    "acil durum yiyecek paketleri dağıtılıyor mu, nereden alabiliriz?",
    "bölgedeki fırınlar çalışmıyor, ekmek bulmakta zorlanıyoruz.",
    "su depolarımız hasar gördü, onarım için ekip ve malzeme desteği lazım.",
    "çadırların altına sermek için muşamba veya palet gibi malzemeler gerekiyor.",
    "bebekler ve küçük çocuklar için özel gıda (meyve püresi, bisküvi) ihtiyacı var.",
    "toplu barınma alanlarında yatak ve ranza ihtiyacı devam ediyor.",
    "acil yemek pişirmek için portatif ocak veya ısıtıcı lazım.",
    "su şişeleri veya damacana su temini gerekli, şebeke suyu yok.",
    "çocuklar için giysi ve ayakkabıya ihtiyacımız var, eskiyenler var.",
    "evimizdeki camlar kırıldı, rüzgardan korunmak için branda lazım.",
    "yaşlılar için yürüteç veya tekerlekli sandalye eksikliği var.",
    "çadır alanında ateş yakmak güvenli mi, ısınma amaçlı?",
    "temel gıda maddeleri için kupon veya dağıtım noktası nerede?",
    "uyku tulumları ve battaniyeler kirlendi, temizlik imkanı yok.",
    "depremden sonra su boruları patladı, su baskını riski var.",
    "güneş enerjili şarj cihazlarına ihtiyacımız var, telefonlar bitiyor.",
    "toplu barınma yerinde elektrik yok, telefonlarımızı şarj edemiyoruz.",
    "çocuklar için oyun ve aktivite malzemeleri lazım, moral bozukluğu var.",
    "evcil hayvanımız için mama ve su bulamıyoruz, veteriner hekim desteği gerekli.",
    "tuvaletlerde su yok, hijyen sorunu baş gösterdi, acil çözüm lazım.",
    "depremzedeler için ücretsiz ulaşım imkanları var mı?",
    "kıyafetlerimiz kirlendi, çamaşır yıkama imkanı yok, temiz kıyafet ihtiyacı var.",
    "bebekler için ısıtıcı ve sıcak su gerekli, üşüyorlar.",
    "engelli bireyler için erişilebilir barınma alanı ve tuvaletler gerekiyor.",
    "bölgede psikososyal destek ekipleri ne zaman göreve başlayacak?",
    "depremzedeler için ev eşyası yardımı yapılacak mı?",
    "çadır kentte güvenlik görevlileri yeterli mi, hırsızlık olayları oluyor.",
    "yaşlılar için tekerlekli sandalye ve baston eksikliği var.",
    "çocuklar okula gidemiyor, eğitim materyali ve öğretmen desteği lazım.",
    "bölgede internet ve telefon çekmiyor, iletişim kuramıyoruz.",
    "hasar tespiti için başvuru süreci nasıl işliyor, bilgi alabilir miyiz?",
    "yatak ve çarşaf ihtiyacımız var, yerlerde yatıyoruz.",
    "depremden sonra hayvanlarımız kayboldu, onları bulmak için yardım istiyoruz.",
    "kronik hastalık ilaçlarımız bitti, en yakın sağlık merkezi nerede?",
    "çocuklar için oyuncak ve kitap bağışı yapılabilir mi?",
    "çadır alanında ısınma sobası veya elektrikli ısıtıcıya ihtiyacımız var.",
    "kolumda küçük bir çizik var, *kanıyor* ama önemli değil, yine de bakabilir misiniz?", # Yeni senaryo
    "depremde düşerken dizimi çarptım, biraz *kanadı* ama şimdi durdu.", # Yeni senaryo
    "elim kesildi, *hafif kanıyor*, bir yara bandı yeterli olur sanırım.", # Yeni senaryo
    "tırnağım çıktı, biraz *kanadı* ama ciddi değil, dezenfektan lazım.", # Yeni senaryo
    "dişim ağrıyor ve biraz *kanıyor*, diş hekimi ne zaman hizmet verir?", # Yeni senaryo
    "burnum *kanadı* ama geçti, yine de bir kontrol iyi olur.", # Yeni senaryo
    "köpeğimin patisi *hafif kanıyor*, veterinere götürmemiz lazım.", # Yeni senaryo
    "çocuğum düştü, dudağı *kanadı*, panikledik ama ciddi değil gibi.", # Yeni senaryo
    "başıma küçük bir taş düştü, *hafif kanama* var, acil değil.", # Yeni senaryo

    # --- DÜŞÜK ÖNCELİKLİ (LOW PRIORITY) MESAJLAR: Bilgi Talebi / Konfor / Uzun Vadeli Planlama ---
    "deprem sonrası okul ne zaman açılacak?",
    "market ne zaman açılır, deprem sonrası alışveriş?",
    "telefon şebekesi ne zaman düzelir, deprem hasarı?",
    "posta dağıtımı var mı, deprem sonrası hizmet?",
    "bankalar açık mı, deprem sonrası para ihtiyacı?",
    "ulaşım ne zaman normale döner, deprem hasarları?",
    "televizyon yayını gelmiyor, deprem antenları bozdu.",
    "deprem sonrası kayıp eşyalarımı nerede arayabilirim?",
    "gönüllü olmak istiyorum, deprem yardımında nereye?",
    "deprem bağışı yapmak istiyorum, en çok ne lazım?",
    "yiyecek dağıtımı hangi saatlerde, deprem sonrası?",
    "çadır kurma yardımı alabilir miyim, deprem sonrası?",
    "çocuklar için oyun alanı var mı, deprem travması?",
    "berber hizmeti var mı, deprem sonrası hijyen?",
    "kargo servisi çalışıyor mu, deprem sonrası?",
    "araç park yeri sorunu, deprem sonrası geçici alan?",
    "çadır alanında gürültü, deprem sonrası uyku sorunu.",
    "sıcak yemek dağıtımı nerede, deprem yardımı?",
    "çaydanlık, çanak çömlek, deprem sonrası eşya kaybı.",
    "çadır alanında tuvalet temizliği, deprem kampı.",
    "kırtasiye malzemesi, çocuklar deprem sonrası okul.",
    "kitap okumak istiyorum, deprem sonrası kütüphane?",
    "spor yapmak için alan, deprem sonrası aktivite?",
    "namaz kılacak yer var mı, deprem sonrası ibadet?",
    "doğum günü kutlaması, çocuk deprem travması.",
    "internetim kesildi, deprem sonrası iletişim?",
    "wifi bağlantısı kötü, deprem sonrası haberleşme.",
    "radyo çalışmıyor, deprem sonrası haber alma.",
    "telefon kılıfım kayboldu, deprem sonrası kayıp.",
    "çadırımız yırtıldı, deprem sonrası barınak.",
    "deprem sonrası kaybolan evcil hayvanlar için bir merkez kuruldu mu?",
    "artçı sarsıntılar ne kadar daha devam eder, bilgi alabilir miyiz?",
    "gönüllü olarak yardım etmek istiyorum, nereye başvurmalıyım?",
    "depremzedeler için kıyafet ve battaniye bağışı yapmak istiyorum.",
    "çadır kentte internet erişimi var mı, haberleşme için önemli.",
    "deprem sonrası okullar ne zaman açılacak, çocukların eğitimi aksadı.",
    "hasar gören evler için maddi yardım başvurusu nasıl yapılır?",
    "deprem bölgesine ulaşım ne zaman normale döner?",
    "kayıp eşyalarımızı bulabileceğimiz bir kayıp eşya bürosu var mı?",
    "depremzedeler için sıcak yemek dağıtımı nerelerde yapılıyor?",
    "çadır kentte güvenlik nasıl sağlanıyor, endişeliyiz.",
    "deprem sonrası bankalar ve ATM'ler çalışıyor mu?",
    "evimizdeki küçük çatlaklar için tamirat desteği alabilir miyiz?",
    "deprem sigortası poliçem var, hasar başvurusu için ne yapmalıyım?",
    "çocuklar için psikolojik destek veren uzmanlar var mı?",
    "deprem sonrası enkaz kaldırma çalışmaları ne zaman tamamlanır?",
    "bölgedeki marketler ve fırınlar açık mı, temel ihtiyaçlarımızı karşılayamıyoruz.",
    "depremzedeler için geçici iş imkanları sunuluyor mu?",
    "toplu taşıma araçları çalışıyor mu, şehir içinde hareket edemiyoruz.",
    "deprem sonrası elektrik ve su faturaları ertelenecek mi?",
    "deprem sonrası spor salonları ne zaman açılacak?",
    "hobilerime devam etmek için malzeme bulabilir miyim?",
    "depremzedeler için ücretsiz psikolojik danışmanlık var mı?",
    "toplu ulaşım araçları ne zaman tamamen normale döner?",
    "deprem sonrası kültürel etkinlikler düzenlenecek mi?",
    "çocuklar için eğitsel oyunlar nerede bulunabilir?",
    "hasar gören tarihi binaların restorasyonu ne zaman başlar?",
    "uzaktan çalışma imkanları deprem sonrası artar mı?",
    "deprem bölgesi için turizm planları değişecek mi?",
    "telefonumu şarj edecek yer bulamıyorum, halka açık şarj istasyonu var mı?",
    "çadırda sineklerle mücadele için ne yapabiliriz?",
    "deprem sonrası evcil hayvan sahiplenme merkezleri açıldı mı?",
    "toplu taşıma için ek seferler konuldu mu?",
    "deprem sonrası hobi kursları açılacak mı?",
    "yerel haber kanalları ne zaman tam yayına başlar?",
    "internette depremle ilgili doğru bilgiye nereden ulaşabiliriz?",
    "deprem sonrası sosyal medya kullanımı için öneriler var mı?",
    "kitap bağışı yapmak istiyorum, nereye teslim edebilirim?",
    "çocuklar için çizgi film izleyebilecekleri bir yer var mı?",
    "toplu yaşam alanlarında gürültüden rahatsız oluyorum, ne yapabilirim?",
    "deprem sonrası uyku düzenim bozuldu, uyku ilacı almalı mıyım?",
    "telefonumun pili çabuk bitiyor, pil tasarrufu için öneriler var mı?",
    "deprem sonrası psikolojik destek hattı numarası nedir?",
    "bölgede mobil kuaför veya berber hizmeti var mı?",
    "deprem sonrası evcil hayvanımı ne zaman alabilirim?",
    "kayıp kimlik kartımı nasıl çıkarabilirim?",
    "depremzedeler için kıyafet ve ayakkabı yardımı nereden alınır?",
    "depremden etkilenen esnaflar için destek programları var mı?",
    "bölgede banka ve ATM'ler ne zaman tam kapasite çalışır?",
    "deprem sonrası internet kafe açıldı mı, bilgisayar kullanmam gerekiyor?",
    "çadırda soğuktan korunmak için ek battaniye bulabilir miyiz?",
    "çocuklar için psikolojik ilk yardım eğitimi veriliyor mu?",
    "deprem sonrası evcil hayvanlar için barınma imkanları var mı?",
    "toplu taşıma araçlarında doluluk oranı nedir, güvenli mi?",
    "deprem sonrası hobi ve sanat kursları açılacak mı?",
    "yerel televizyon kanalları deprem sonrası özel yayın yapıyor mu?",
    "depremzedeler için iş bulma konusunda yardımcı olan kurumlar var mı?",
    "deprem sonrası yeni ev arayışına nereden başlamalıyım?",
    "bölgedeki kafeler ve restoranlar ne zaman açılacak?",
    "deprem sonrası çocukların okula uyum sağlaması için destekler var mı?",
    "telefon şebekesi ne zaman tam olarak onarılır?",
    "deprem sonrası spor tesisleri kullanıma açıldı mı?",
    "deprem sonrası evimdeki saksı kırıldı, nasıl temizleyebilirim?", # Yeni senaryo
    "depremde şarj aletim kayboldu, yeni bir tane bulabilir miyim?", # Yeni senaryo
    "komşularım evde mi merak ediyorum, bilgi alabilir miyim?", # Yeni senaryo
    "deprem sonrası uyuyamıyorum, basit bir uyku önerisi var mı?", # Yeni senaryo
    "depremle ilgili haberleri nereden takip edebilirim?", # Yeni senaryo
]

sample_priorities = [
    # YÜKSEK ÖNCELİKLİ (HIGH PRIORITY) MESAJLAR (70 + 7 = 77 adet)
    "high", "high", "high", "high", "high", "high", "high", "high", "high", "high",
    "high", "high", "high", "high", "high", "high", "high", "high", "high", "high",
    "high", "high", "high", "high", "high",
    "high", "high", "high", "high", "high", "high", "high", "high", "high", "high",
    "high", "high", "high", "high", "high", "high", "high", "high", "high", "high",
    "high", "high", "high", "high", "high", "high", "high", "high", "high", "high",
    "high", "high", "high", "high", "high", "high", "high", "high", "high", "high",
    "high", "high", "high", "high", "high",
    "high", "high", "high", "high", "high", "high", "high", # Yeni senaryolar

    # ORTA ÖNCELİKLİ (MEDIUM PRIORITY) MESAJLAR (100 + 9 = 109 adet)
    "medium", "medium", "medium", "medium", "medium", "medium", "medium", "medium", "medium", "medium",
    "medium", "medium", "medium", "medium", "medium", "medium", "medium", "medium", "medium", "medium",
    "medium", "medium", "medium", "medium", "medium", "medium", "medium", "medium", "medium", "medium",
    "medium", "medium", "medium", "medium", "medium", "medium", "medium", "medium", "medium", "medium",
    "medium", "medium", "medium", "medium", "medium", "medium", "medium", "medium", "medium", "medium",
    "medium", "medium", "medium", "medium", "medium", "medium", "medium", "medium", "medium", "medium",
    "medium", "medium", "medium", "medium", "medium", "medium", "medium", "medium", "medium", "medium",
    "medium", "medium", "medium", "medium", "medium",
    "medium", "medium", "medium", "medium", "medium", "medium", "medium", "medium", "medium", "medium",
    "medium", "medium", "medium", "medium", "medium", "medium", "medium", "medium", "medium", "medium",
    "medium", "medium", "medium", "medium", "medium",
    "medium", "medium", "medium", "medium", "medium", "medium", "medium", "medium", "medium", # Yeni senaryolar

    # DÜŞÜK ÖNCELİKLİ (LOW PRIORITY) MESAJLAR (90 + 5 = 95 adet)
    "low", "low", "low", "low", "low", "low", "low", "low", "low", "low",
    "low", "low", "low", "low", "low", "low", "low", "low", "low", "low",
    "low", "low", "low", "low", "low", "low", "low", "low", "low", "low",
    "low", "low", "low", "low", "low", "low", "low", "low", "low", "low",
    "low", "low", "low", "low", "low", "low", "low", "low", "low", "low",
    "low", "low", "low", "low", "low", "low", "low", "low", "low", "low",
    "low", "low", "low", "low", "low",
    "low", "low", "low", "low", "low", "low", "low", "low", "low", "low",
    "low", "low", "low", "low", "low", "low", "low", "low", "low", "low",
    "low", "low", "low", "low", "low",
    "low", "low", "low", "low", "low", # Yeni senaryolar
]


MODEL_PATH = Config.AI_MODEL_PATH # Config'den model yolu al
VECTORIZER_PATH = Config.AI_VECTORIZER_PATH # Config'den vektörleyici yolu al
model = None
vectorizer = None

def train_and_save_model(messages, priorities):
    """
    Metin sınıflandırma modelini (TfidfVectorizer + LinearSVC) eğitir ve kaydeder.
    Optimum hiperparametreleri bulmak için GridSearchCV kullanır.
    """
    if not messages or not priorities or len(messages) != len(priorities):
        print("[AI] Uyarı: Eğitim veri seti geçersiz veya boş. Model eğitilemiyor.")
        return False
    print("[AI] Model eğitiliyor ve hiperparametreler optimize ediliyor...")
    try:
        # Metin işleme ve sınıflandırma için bir Pipeline oluşturulur
        pipeline = Pipeline([
            ('vectorizer', TfidfVectorizer(
                lowercase=True,
                stop_words=TURKISH_STOP_WORDS
            )),
            ('classifier', LinearSVC(class_weight='balanced', max_iter=Config.AI_LINEAR_SVC_MAX_ITER)) # max_iter Config'den alındı
        ])

        # GridSearchCV için parametre aralıkları
        param_grid = {
            'vectorizer__ngram_range': [Config.AI_NGRAM_RANGE], # Config'den alındı
            'vectorizer__max_features': [Config.AI_MAX_FEATURES], # Config'den alındı
            'vectorizer__min_df': [Config.AI_MIN_DF], # Config'den alındı
            'classifier__C': [Config.AI_LINEAR_SVC_C] # Config'den alındı
        }

        # GridSearchCV ile en iyi parametreleri bul
        grid_search = GridSearchCV(pipeline, param_grid, cv=5, n_jobs=-1, verbose=1, scoring='f1_weighted')
        grid_search.fit(messages, priorities)

        text_classifier = grid_search.best_estimator_
        print(f"[AI] En iyi parametreler: {grid_search.best_params_}")
        print(f"[AI] En iyi F1 Skoru (Weighted): {grid_search.best_score_:.4f}")

        # Eğitilmiş pipeline ve vektörleyici disk üzerine kaydedilir
        joblib.dump(text_classifier, MODEL_PATH)
        joblib.dump(text_classifier.named_steps['vectorizer'], VECTORIZER_PATH)
        print("[AI] Model ve vektörleyici başarıyla kaydedildi.")
        return True
    except Exception as e:
        print(f"[AI] Model eğitimi veya hiperparametre optimizasyonu sırasında hata oluştu: {e}")
        return False

def load_model():
    """
    Kaydedilmiş modeli ve vektörleyiciyi yükler.
    Model bulunamazsa veya yüklenemezse yeniden eğitir.
    """
    global model, vectorizer
    if model is None or vectorizer is None: # Model hafızada yoksa yükle veya eğit
        if os.path.exists(MODEL_PATH) and os.path.exists(VECTORIZER_PATH):
            print(f"[AI] Model ve vektörleyici '{MODEL_PATH}' ve '{VECTORIZER_PATH}' konumundan yükleniyor...")
            try:
                model = joblib.load(MODEL_PATH)
                vectorizer = joblib.load(VECTORIZER_PATH)
                print("[AI] Model ve vektörleyici başarıyla yüklendi.")
            except Exception as e:
                print(f"[AI] Model yükleme sırasında hata oluştu: {e}. Yeniden eğitmeyi deniyorum.")
                if train_and_save_model(sample_messages, sample_priorities):
                    model = joblib.load(MODEL_PATH)
                    vectorizer = joblib.load(VECTORIZER_PATH)
                else:
                    print("[AI] Yeni model de eğitilemedi, lütfen veri setini kontrol edin.")
                    return None, None
        else:
            print("[AI] Kaydedilmiş model bulunamadı, model eğitiliyor...")
            if train_and_save_model(sample_messages, sample_priorities):
                model = joblib.load(MODEL_PATH)
                vectorizer = joblib.load(VECTORIZER_PATH)
            else:
                print("[AI] Model eğitilemedi, lütfen veri setini kontrol edin.")
                return None, None
    return model, vectorizer

def predict_priority(text_detail):
    """
    Verilen metin için öncelik tahmini yapar.
    """
    current_model, _ = load_model()
    if current_model is None:
        print(f"[AI] Model yüklenemedi. Varsayılan öncelik 'high' atandı.")
        return "high" # Model yüklenemezse kritik durum kabul edilebilir
    if not text_detail or not isinstance(text_detail, str):
        print(f"[AI] Boş veya geçersiz metin. Varsayılan öncelik 'high' atandı.")
        return "high" # Boş metinler de potansiyel tehlike işareti olabilir

    print(f"[AI] Öncelik tahmin ediliyor: '{text_detail[:50]}...'")
    prediction = current_model.predict([text_detail])[0]
    print(f"[AI] Tahmin edilen öncelik: {prediction}")
    return prediction

def evaluate_model():
    """
    Modelin performansını değerlendirir ve bir rapor sunar.
    """
    print("[AI] Model değerlendirilmeye başlanıyor...")
    if len(sample_messages) != len(sample_priorities) or not sample_messages:
        print("[AI] Uyarı: Değerlendirme için eğitim veri seti geçersiz veya boş. Değerlendirme atlanıyor.")
        return

    # Eğitim ve test setlerini stratify ederek dengeli bir dağılım sağlanır
    X_train, X_test, y_train, y_test = train_test_split(
        sample_messages, sample_priorities,
        test_size=Config.AI_TRAIN_TEST_SPLIT_SIZE, # Config'den alındı
        random_state=Config.AI_RANDOM_STATE, # Config'den alındı
        stratify=sample_priorities
    )

    # Değerlendirme için yeni bir pipeline oluşturulur ve eğitilir
    current_model, _ = load_model()
    if current_model:
        predictions = current_model.predict(X_test)
        print("\n[AI] Model Değerlendirme Raporu:")
        print(classification_report(y_test, predictions, zero_division=0))
        print("[AI] Model değerlendirmesi tamamlandı.")
    else:
        print("[AI] Model yüklenemediği için değerlendirme yapılamadı.")

if __name__ == '__main__':
    # Veri setlerinin uzunluklarını kontrol et ve eşleşmiyorsa hata ver
    if len(sample_messages) != len(sample_priorities):
        print(f"[AI] Hata: 'sample_messages' ({len(sample_messages)}) ve 'sample_priorities' ({len(sample_priorities)}) listelerinin uzunlukları eşleşmiyor!")
        print("[AI] Lütfen veri setinizi kontrol edin ve eksik öncelikleri ekleyin veya fazla mesajları çıkarın.")
    else:
        # Model yükle veya eğit
        load_model()
        # Modeli değerlendir
        evaluate_model()
        print("\n" + "="*30 + "\n[AI] Tahmin Örnekleri:\n" + "="*30)
        # Örnek tahminler yap
        print(f"Acil durum: '{predict_priority('enkaz altındayız, sesimizi duyan var mı?')}'")
        print(f"Acil durum: '{predict_priority('hamile eşim sancılanıyor, acil yardım!')}'")
        print(f"Acil durum: '{predict_priority('çocuk boğuluyor, sağlık ekibi lazım!')}'")
        print(f"Orta durum: '{predict_priority('çadırımız yırtıldı, yenisi lazım.')}'")
        print(f"Orta durum: '{predict_priority('bebek bezi bitti, yardım edin.')}'")
        print(f"Düşük durum: '{predict_priority('radyo çalışmıyor, haber alamıyoruz.')}'")
        print(f"Düşük durum: '{predict_priority('telefon kılıfım kayboldu.')}'")
        print(f"Acil durum: '{predict_priority('binamız yıkıldı, acil kurtarma ekipleri!')}'")
        print(f"Orta durum: '{predict_priority('ilaçlarım bitti, kronik hastayım.')}'")
        print(f"Düşük durum: '{predict_priority('wifi bağlantısı kötü.')}'")
        print(f"Orta durum (yeni): '{predict_priority('yemek ve suya acil ihtiyacımız var, erzak bitti.')}'")
        print(f"Orta durum (yeni): '{predict_priority('çadırda yer kalmadı, dışarıda kalıyoruz.')}'")
        print(f"Düşük durum (yeni): '{predict_priority('depremzedeler için hayvan barınağı açılacak mı?')}'")
        print(f"Yüksek durum (yeni): '{predict_priority('bina yan yatmış, her an çökebilir, içeride yaşlılar var!')}'")
        print(f"Orta durum (yeni): '{predict_priority('mahallemizde içme suyu bitti, tankerle su dağıtımı yapılabilir mi?')}'")
        print(f"Düşük durum (yeni): '{predict_priority('internette depremle ilgili doğru bilgiye nereden ulaşabiliriz?')}'")
        print(f"Yüksek durum (yeni): '{predict_priority('enkazdan çıkarıldım ama kötü kanamam var, acil doktor!')}'")
        print(f"Orta durum (yeni): '{predict_priority('kolumda küçük bir çizik var, kanıyor ama önemli değil, yine de bakabilir misiniz?')}'")
        print(f"Yüksek durum (yeni): '{predict_priority('başım yaralı ve kanama durmuyor, bayılacak gibiyim!')}'")
        print(f"Orta durum (yeni): '{predict_priority('dişim ağrıyor ve biraz kanıyor, diş hekimi ne zaman hizmet verir?')}'")
        print(f"Yüksek durum (yeni): '{predict_priority('depremde bacağımda derin bir kesik oluştu, kanamayı durduramıyorum!')}'")
