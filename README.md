# PlantGuard AI: Akıllı Tarım Teşhis Sistemi (PlantVillage)

Bu proje, **PlantVillage** veri setini kullanarak bitki hastalıklarını multimodal (görsel + iklimsel) yöntemlerle tespit eden gelişmiş bir yapay zeka platformudur.

## 🚀 Özellikler

1.  **Multimodal Derin Öğrenme**: Sadece yaprak fotoğraflarını değil, o andaki sıcaklık ve nem verilerini de analiz ederek daha tutarlı sonuçlar üretir.
2.  **Hibrit Algoritmalar**:
    *   **KNN (K-Nearest Neighbors)**: ResNet18 tarafından çıkarılan özellikler (embeddings) üzerinden görsel benzerlik analizi yapar.
    *   **ANN (Artificial Neural Network)**: Görüntü özellikleri ile iklim verilerini füzyon katmanında birleştirerek son teşhisi koyar.
    *   **RNN (Recurrent Neural Network)**: Zaman serisi (5 günlük veri) üzerinden hastalığın ilerleme riskini tahmin eder.
3.  **Performans Metrikleri**: Confusion Matrix ve ROC Curve ile modelin akademik geçerliliği doğrulanır.

## 📚 Akademik Kaynaklar (Literatür Taraması)

Bu projenin geliştirilmesinde aşağıdaki temel makaleler referans alınmıştır:

1.  **Mohanty, S. P., et al. (2016)**: *"Using Deep Learning for Image-Based Plant Disease Detection"*. (PlantVillage veri setini literatüre kazandıran ve başarım standartlarını belirleyen temel çalışma).
2.  **Multimodal Deep Learning in Agriculture**: Tarımsal verilerin (görüntü + sensör) birleştirilmesinin başarıyı %15-20 oranında artırdığını kanıtlayan çalışmalar.
3.  **Performance Analysis of KNN and CNN**: Özellik çıkarımı (feature extraction) sonrası KNN kullanımının, veri setindeki "benzerlik kümelerini" anlamadaki başarısı üzerine analizler.
4.  **RNN based prediction of crop diseases**: Hava durumu verileri üzerinden zaman serisi analizinin hastalık şiddeti tahminindeki etkinliği.
5.  **Decision Fusion Levels**: Çok modlu sistemlerde veri seviyesinde (data-level) ve karar seviyesinde (decision-level) füzyon teknikleri.

## 🛠️ Kurulum

### Backend
1. Python 3.10+
2. `/data` klasörüne PlantVillage veri setini yerleştirin.
3. `pip install -r requirements.txt` (torch, torchvision, sklearn, matplotlib, fastapi, uvicorn)
4. `python train.py` ile modelleri eğitin.
5. `python main.py` ile API'yi başlatın.

### Frontend
1. `npm install`
2. `npm run dev`

---
*Akademik Proje - 2026*
