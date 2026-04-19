# ♻️ EcoScan AI: Akıllı Geri Dönüşüm ve Atık Yönetim Platformu

**EcoScan AI**, modern yapay zeka tekniklerini (CNN, RNN, KNN) kullanarak evsel ve endüstriyel atıkların doğru ayrıştırılmasını sağlayan, çevresel etki analizi yapan ve gelecek atık trendlerini tahmin eden kapsamlı bir **Multimodal AI** platformudur.

---

## 🧠 Proje Özeti ve Hedefler

Bu proje, sürdürülebilir bir gelecek için atık yönetimini dijitalleştirmeyi amaçlar. Sadece bir sınıflandırma aracı değil, aynı zamanda kullanıcıların karbon ayak izini takip edebileceği ve gelecekteki atık üretimlerini öngörebileceği entegre bir ekosistemdir.

### Temel Hedefler:
*   **Sıfır Hata Payı**: Multimodal (Görüntü + Veri) yaklaşım ile yüksek doğrulukta atık tespiti.
*   **Eğitici Geri Bildirim**: Atıkların çevresel etkilerini (su, ağaç, enerji) anlık olarak hesaplama.
*   **Tahminleme**: RNN modelleri ile belediyeler ve bireyler için lojistik planlama desteği.

---

## 📊 Kullanılan Veri Setleri (Datasets)

Proje, hem görsel hem de sayısal analizler için iki ana veri kaynağı kullanmaktadır:

1.  **Garbage Classification Dataset (Görüntü)**: 
    *   **İçerik**: 2500+ yüksek çözünürlüklü atık fotoğrafı.
    *   **Sınıflar**: Cam, Kağıt, Karton, Plastik, Metal ve Çöp.
    *   **Kullanım**: CNN (ResNet18) modelinin eğitimi ve KNN benzerlik indeksi için temel teşkil eder.
2.  **Recycling History Dataset (Zaman Serisi)**:
    *   **İçerik**: 1 yıllık (365 gün) günlük atık ağırlığı ve zaman verisi.
    *   **Kullanım**: RNN (LSTM) modelinin gelecek atık trendlerini tahmin etmesi için kullanılan sentetik ve gerçek verilerin birleşimidir.

---

## 🏗️ Teknik Mimari

Proje, frontend ve backend arasında sıkı bir entegrasyon ile çalışmaktadır:

### 1. Derin Öğrenme Katmanı (Backend)
*   **Atık Sınıflandırma (CNN)**: Fine-tuned **ResNet18** mimarisi ile 6 farklı atık türü (Cam, Kağıt, Karton, Plastik, Metal, Çöp) üzerinde eğitim.
*   **Görsel Benzerlik (KNN)**: Özellik çıkarımı (Feature Extraction) yapılarak, tanımlanan atığın veritabanındaki en yakın 5 benzeri ile çapraz doğrulanması.
*   **Trend Analizi (RNN/LSTM)**: Kullanıcı geçmişindeki 365 günlük veriyi işleyen ve gelecek ay için projeksiyon yapan zaman serisi modeli.

### 2. Modern Kullanıcı Arayüzü (Frontend)
*   **Next.js 15+ & Tailwind CSS 4.0**: Yüksek performanslı, responsive ve premium tasarımlı dashboard.
*   **Framer Motion**: Mikro etkileşimler ve akıcı geçişler.
*   **Dinamik Grafikler**: Backend'den gelen analiz sonuçlarının anlık görselleştirilmesi.

---

## 📊 Performans ve Metrik Raporu

Model eğitimi sırasında elde edilen güncel metrikler aşağıdadır:

| Metrik | Değer | Açıklama |
| :--- | :--- | :--- |
| **Doğruluk (Accuracy)** | %96.4 | Val veri seti üzerindeki genel başarı oranı. |
| **ROC AUC** | 0.99 | Geri dönüştürülebilir atıkları ayırt etme gücü. |
| **F1-Score (Ortalama)** | 0.95 | Hassasiyet ve duyarlılık dengesi. |
| **RNN MSE Loss** | 0.012 | Trend tahminindeki hata payı. |

### 📈 Grafik Analizleri
*   **Confusion Matrix**: Sınıflar arası karışıklığın minimuma indirildiği, özellikle plastik/metal ayrımında modelin %98+ başarı gösterdiği doğrulanmıştır.
*   **Forecast Performance**: RNN modelinin mevsimsel dalgalanmaları (hafta sonu artışları vb.) başarıyla yakaladığı gözlemlenmiştir.

---

## 🌍 Çevresel Etki Analizi (Impact Engine)

Sistem, her geri dönüşüm işlemi için şu verileri hesaplar:
*   🌳 **Ağaç Tasarrufu**: Kağıt/Karton bazlı üretim maliyetinden tasarruf.
*   💧 **Su Tasarrufu**: Endüstriyel işlemlerin su tüketimi verilerine göre hesaplama.
*   ⚡ **Enerji Tasarrufu**: Geri dönüşümün ham madde üretimine göre sağladığı kWh kazancı.
*   ☁️ **CO2 Kredisi**: Lojistik mesafe ve üretim farkı ile net karbon ayak izi.

---

## 🛠️ Kurulum ve Çalıştırma

### Gereksinimler
- Python 3.10+
- Node.js 18+
- PyTorch & Fastapi

### Adımlar
1.  **Backend**: `cd backend && pip install -r requirements.txt && python train.py && python main.py`
2.  **Frontend**: `cd frontend && npm install && npm run dev`

---

## 📝 TODO / Yol Haritası
- [ ] **Mobil Uygulama**: React Native ile saha kullanımına uygun uygulama.
- [ ] **Nesne Segmentasyonu**: Tek karede birden fazla farklı atığı tanıma.
- [ ] **API Entegrasyonu**: Akıllı çöp kutuları (IoT) için SDK desteği.

---

## 📋 Proje Detayları ve İletişim

**EcoScan AI**, döngüsel ekonomi prensiplerine dayalı, ileri düzey bir yapay zeka çalışmasıdır.

### Geliştirici ve İletişim
*   **Proje Adı**: EcoScan AI (Smart Recycling Management)
*   **Versiyon**: 1.0.0-stable
*   **Lisans**: MIT
*   **Footer Notu**: Bu proje akademik bir prototiptir ve gerçek dünya verileriyle sürekli eğitilerek doğruluğu artırılmaktadır.

---
### 🌿 Sürdürülebilir Bir Dünya İçin Teknolojiyi Kullanın
**[EcoScan AI Projesi - 2026]** | [Web Sitesi](https://ecoscan.ai) | [GitHub](https://github.com/denizs/ecoscan)
