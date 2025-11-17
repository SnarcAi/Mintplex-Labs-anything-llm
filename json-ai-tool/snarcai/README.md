# SnarcAI Fine-Tuning Kılavuzu

Burak Kumuk'un dijital ikizi - SnarcAI modelini Qwen 2.5 7B üzerine fine-tune etmek için rehber.

## 📋 Sistem Gereksinimleri

✅ **Donanım:**
- GPU: RTX 5080 16GB (mevcut)
- RAM: 128 GB (mevcut)
- Disk: ~50 GB boş alan

✅ **Yazılım:**
- Windows 11 Pro (mevcut)
- Python 3.13.7 (mevcut)
- CUDA 12.x (RTX 5080 için)

## 🚀 Hızlı Başlangıç

### 1. Gerekli Paketleri Yükle

```powershell
# PowerShell'de proje dizinine git
cd C:\Users\Superuser\Projects\anything-llm\json-ai-tool\snarcai

# Virtual environment oluştur (opsiyonel ama önerilen)
python -m venv venv
.\venv\Scripts\Activate.ps1

# Gerekli paketleri yükle
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
pip install transformers>=4.36.0
pip install peft>=0.7.0
pip install datasets>=2.16.0
pip install accelerate>=0.25.0
pip install sentencepiece protobuf
pip install tensorboard
```

### 2. GPU Kontrolü

```powershell
python -c "import torch; print(f'CUDA: {torch.cuda.is_available()}'); print(f'GPU: {torch.cuda.get_device_name(0) if torch.cuda.is_available() else None}')"
```

Çıktı şöyle olmalı:
```
CUDA: True
GPU: NVIDIA GeForce RTX 5080
```

### 3. Training'i Başlat

```powershell
# Fine-tuning başlat (RTX 5080'de ~30-60 dakika)
python finetune_snarcai.py
```

**Varsayılan ayarlar:**
- Model: `C:\Users\Superuser\.cache\huggingface\hub\models--Qwen--Qwen2.5-7B-Instruct\snapshots\a09a35458c702b33eeacc393d103063234e8bc28`
- Dataset: `snarcai_training_dataset.jsonl` (50 örnek)
- Epochs: 5
- Batch size: 2
- LoRA rank: 64
- Learning rate: 1e-4

### 4. Özel Parametrelerle Training

```powershell
# Daha fazla epoch
python finetune_snarcai.py --epochs 10

# Daha büyük batch size (VRAM yeterliyse)
python finetune_snarcai.py --batch-size 4

# Daha yüksek LoRA rank (daha iyi öğrenme)
python finetune_snarcai.py --lora-r 128

# Hepsini birlikte
python finetune_snarcai.py --epochs 10 --batch-size 4 --lora-r 128 --lr 5e-5
```

### 5. Training'i İzle

Training sırasında TensorBoard ile metrikleri izleyebilirsiniz:

```powershell
# Yeni bir PowerShell penceresi aç
tensorboard --logdir=./snarcai-qwen-2.5-7b/logs

# Browser'da aç: http://localhost:6006
```

## 📊 Training Süreci

### Beklenen Süreler (RTX 5080 16GB)

| Epochs | Batch Size | LoRA Rank | Süre (tahmin) | VRAM Kullanımı |
|--------|------------|-----------|---------------|----------------|
| 3      | 2          | 64        | ~20-30 dk     | ~12 GB         |
| 5      | 2          | 64        | ~30-50 dk     | ~12 GB         |
| 10     | 2          | 64        | ~60-90 dk     | ~12 GB         |
| 5      | 4          | 64        | ~20-30 dk     | ~14 GB         |
| 5      | 2          | 128       | ~40-60 dk     | ~13 GB         |

### Training Log Örneği

```
======================================================================
🚀 SnarcAI Fine-Tuning
======================================================================
Device: cuda
GPU: NVIDIA GeForce RTX 5080
VRAM: 16.0 GB
Model: Qwen 2.5 7B Instruct
Dataset: snarcai_training_dataset.jsonl
======================================================================

📦 Model yükleniyor...
   ✓ Tokenizer yüklendi
     Vocab size: 151936
     Pad token: <|endoftext|>

   ✓ Model yüklendi
     Parametreler: 7.62B
     Gradient checkpointing aktif

🔧 LoRA ayarlanıyor...
   ✓ LoRA aktif
     Trainable: 167.77M (2.200%)
     VRAM tasarrufu: ~14.1 GB

📚 Dataset yükleniyor...
   ✓ Dataset yüklendi: 50 örnek
   ✓ Tokenization tamamlandı
     Token uzunlukları:
       Min: 145
       Max: 387
       Ortalama: 234.5

🎓 Training başlıyor...
   Epochs: 5
   Batch size: 2
   Effective batch size: 16
   Total steps: ~15

======================================================================
TRAINING BAŞLADI - RTX 5080'de ~30-60 dakika sürebilir
======================================================================

Step 1/15 | Loss: 2.456 | LR: 1.0e-05
Step 2/15 | Loss: 2.123 | LR: 2.0e-05
...
Step 15/15 | Loss: 0.342 | LR: 1.0e-06

======================================================================
✅ TRAINING TAMAMLANDI!
======================================================================

💾 Model kaydediliyor...
   ✓ Model kaydedildi: ./snarcai-qwen-2.5-7b/final
   ✓ LoRA adapters: ./snarcai-qwen-2.5-7b/lora_adapters
```

## 🧪 Fine-Tuned Modeli Test Et

Training tamamlandıktan sonra modeli test edin:

```powershell
python snarcai_chat.py
```

### Test Soruları

```
Burak> WC blok 40g için maliyet hesapla: PP 28g (0.08TL/g), parfüm 12g (1.2TL/g)

SnarcAI> PP: 28g × 0.08 = 2.24TL
Parfüm: 12g × 1.2 = 14.40TL
Ambalaj: 0.45TL
İşçilik: 0.15TL
Toplam: 17.24TL/adet

---

Burak> Maliyet 25TL, hedef %30 marj. Satış fiyatı?

SnarcAI> Fiyat = 25 ÷ 0.70 = 35.71TL

---

Burak> Stok 3000, kritik eşik 5000. Ne yapmalıyım?

SnarcAI> Stok kritik seviyede. Acil sipariş ver.
```

## 📁 Dosya Yapısı

```
snarcai/
├── README.md                          # Bu dosya
├── anayasa_v2.3.json                  # SnarcAI anayasası
├── prepare_dataset.py                 # Dataset oluşturucu
├── snarcai_training_dataset.jsonl    # Training dataset (50 örnek)
├── finetune_snarcai.py               # Fine-tuning script
├── snarcai_chat.py                   # Inference script
└── snarcai-qwen-2.5-7b/              # Output (training sonrası)
    ├── final/                         # Fine-tuned model
    │   ├── config.json
    │   ├── model.safetensors
    │   └── tokenizer.json
    ├── lora_adapters/                 # Sadece LoRA weights
    │   └── adapter_model.safetensors
    └── logs/                          # TensorBoard logs
        └── events.out.tfevents.*
```

## ⚙️ Parametreleri Anlama

### LoRA Parametreleri

- **lora_r (rank):** LoRA matrix'in rank'i
  - Düşük (8-16): Hızlı, az bellek, daha az öğrenme kapasitesi
  - Orta (32-64): Dengeli ⭐ (önerilen)
  - Yüksek (128-256): Yavaş, daha fazla bellek, daha iyi öğrenme

- **lora_alpha:** Rank ile birlikte çalışır
  - Genellikle rank × 2 olarak ayarlanır
  - Örnek: rank=64 → alpha=128

- **lora_target_modules:** Hangi layer'lar eğitilecek
  - `q_proj, k_proj, v_proj, o_proj`: Attention layers (minimum)
  - `+ gate_proj, up_proj, down_proj`: MLP layers da (daha iyi)

### Training Parametreleri

- **num_epochs:** Dataset üzerinde kaç tur eğitim
  - 3-5: Hızlı test ⭐
  - 10-20: Production quality
  - 50+: Overfitting riski

- **batch_size:** Bir seferde kaç örnek
  - RTX 5080 16GB için: 2-4 (gradient accumulation ile 16 effective)

- **learning_rate:** Öğrenme hızı
  - 1e-4: İyi başlangıç ⭐
  - 5e-5: Daha stabil
  - 2e-4: Daha hızlı (dikkatli)

- **gradient_accumulation_steps:** Effective batch size artırır
  - batch_size=2, grad_acc=8 → effective_batch=16

## 🔧 Sorun Giderme

### CUDA Out of Memory

```
RuntimeError: CUDA out of memory
```

**Çözüm:**
1. Batch size azalt: `--batch-size 1`
2. LoRA rank azalt: `--lora-r 32`
3. Max seq length azalt: `--max-seq-length 1024`

### Model Yükleme Hatası

```
FileNotFoundError: Model bulunamadı
```

**Çözüm:**
Model path'ini manuel ver:
```powershell
python finetune_snarcai.py --model "C:\Users\Superuser\.cache\huggingface\hub\models--Qwen--Qwen2.5-7B-Instruct\snapshots\a09a35458c702b33eeacc393d103063234e8bc28"
```

### Yavaş Training

**Optimizasyonlar:**
1. Batch size artır (VRAM yeterse): `--batch-size 4`
2. Gradient checkpointing kapat (daha fazla VRAM kullanır ama hızlı)
3. Float16 kullan (bf16 yerine, RTX 5080'de minimal fark)

## 📈 İleri Seviye: Daha Fazla Data

Eğer daha iyi sonuçlar istiyorsanız, dataset'i genişletin:

```powershell
# prepare_dataset.py'yi düzenle, daha fazla örnek ekle
# Hedef: 200-500 örnek

python prepare_dataset.py

# Yeni dataset ile train et
python finetune_snarcai.py --epochs 10
```

## 🎯 Sonraki Adımlar

1. ✅ Training tamamlandı
2. 🧪 Modeli test et (`snarcai_chat.py`)
3. 📊 Sonuçları değerlendir
4. 🔄 Gerekirse dataset'i genişlet ve tekrar train et
5. 🚀 Production'a al

## 💡 İpuçları

- **İlk training'i küçük yapın:** Epochs=3, batch=2 ile test edin
- **TensorBoard kullanın:** Loss grafiğini izleyin
- **Checkpointleri saklayın:** Her 50 step'te kaydedilir
- **Overfitting'i önleyin:** Loss çok düşerse epoch azaltın
- **GPU sıcaklığını izleyin:** MSI Afterburner vs kullanın

## 🆘 Destek

Sorun yaşarsanız:
1. Training log'unu kontrol edin
2. VRAM kullanımını nvidia-smi ile kontrol edin
3. Dataset'i kontrol edin (format doğru mu?)

---

**SnarcAI v2.3** - Burak Kumuk için özel AI asistanı
Qwen 2.5 7B üzerine fine-tuned
