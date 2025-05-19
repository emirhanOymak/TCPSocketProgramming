# ⚙️ TCPSocketProgramming

**TCPSocketProgramming**, TCP tabanlı bir istemci-sunucu mimarisi ile dosya transferi yapılabilmesini sağlar.  
PyQt5 ile geliştirilmiş kullanıcı arayüzü sayesinde, kullanıcılar kolayca dosya yükleyebilir, indirebilir, listeleyebilir ve silebilir.

---

## 🚀 Özellikler

- 📤 Dosya yükleme (sunucuya)
- 📥 Dosya indirme (sunucudan)
- 📄 Sunucudaki dosyaları listeleme
- 🗑️ Dosya silme özelliği
- 📊 Progress bar (yükleme ve indirme ilerleme çubuğu)
- 📁 Dosya boyutlarını GUI'de gösterme
- 🧾 İndirilen dosyayı sistemde otomatik açma
- 🎨 Renkli ve kullanıcı dostu arayüz

Gereksinimler:
pip install PyQt5

Kullanım
Sunucuyu başlat: python server_plain.py
-shared/ klasörü otomatik oluşturulur
-Tüm dosyalar bu klasörde tutulur

İstemciyi başlat (GUI): python client_plain_gui.py
-Bağlantı kurulur
-GUI üzerinden işlem yapılabilir

Proje Yapısı

TCPSocketProgramming/
│
├── client_plain_gui.py        → PyQt5 ile hazırlanmış istemci arayüzü
├── server_plain.py            → TCP sunucu uygulaması
├── shared/                    → Sunucu tarafında yüklenen dosyaların klasörü
├── indirilen_<dosya>         → İstemci tarafında indirilen dosyaların isim prefix’i
└── README.md                  → Proje açıklama dosyası


Katkıda bulunmak istersen:
Fork yap 🔱
Yeni bir branch oluştur (feature/yeni-ozellik)
Değişikliklerini yap
Pull Request gönder 📥
