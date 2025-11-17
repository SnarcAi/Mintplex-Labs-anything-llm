# 🐻 MORİ - Fine-Tuning Guide
## Lavanta-Mor Ayı: 2-9 Yaş Çocuklar İçin Türkçe AI Arkadaş

**NIRVANA Projesi - MORİ Eğitim Kılavuzu**
*RTX 5080 16GB - Windows 11 Pro - Python 3.13.7*

---

## 📋 İçindekiler

1. [Sistem Gereksinimleri](#sistem-gereksinimleri)
2. [Kurulum](#kurulum)
3. [Hızlı Başlangıç](#hızlı-başlangıç)
4. [Adım Adım Eğitim](#adım-adım-eğitim)
5. [Model Kullanımı](#model-kullanımı)
6. [Teknik Detaylar](#teknik-detaylar)
7. [Sorun Giderme](#sorun-giderme)
8. [SSS](#sss)

---

## 🖥️ Sistem Gereksinimleri

### Minimum (Test için)
- **GPU**: NVIDIA RTX 3060 12GB veya üzeri
- **RAM**: 32GB
- **Disk**: 50GB boş alan
- **OS**: Windows 10/11
- **Python**: 3.10+

### Önerilen (Production için)
- **GPU**: NVIDIA RTX 5080 16GB ✅
- **RAM**: 128GB DDR5 ✅
- **CPU**: AMD Ryzen 9 9950X (16 core) ✅
- **Disk**: 2TB NVMe SSD ✅
- **OS**: Windows 11 Pro ✅
- **Python**: 3.13.7 ✅
- **Power**: 1050W PSU ✅

> **Not**: Yukarıdaki "Önerilen" sistem, projenin geliştirildiği gerçek sistemdir.

---

## 📦 Kurulum

### 1. Python Ortamı Hazırlama

```bash
# Virtual environment oluştur (önerilen)
python -m venv mori_env

# Aktifleştir (Windows)
mori_env\Scripts\activate

# Aktifleştir (Linux/Mac)
source mori_env/bin/activate
```

### 2. CUDA ve PyTorch Kurulumu

```bash
# PyTorch + CUDA 12.1 (RTX 5080 için)
pip install torch --index-url https://download.pytorch.org/whl/cu121

# CUDA kontrolü
python -c "import torch; print(f'CUDA: {torch.cuda.is_available()}'); print(f'GPU: {torch.cuda.get_device_name(0) if torch.cuda.is_available() else \"N/A\"}')"
```

**Çıktı şöyle olmalı:**
```
CUDA: True
GPU: NVIDIA GeForce RTX 5080
```

### 3. Gerekli Paketleri Yükle

```bash
pip install -r requirements.txt
```

**Paketler:**
- `transformers` - Hugging Face modelleri
- `datasets` - Veri yönetimi
- `peft` - LoRA adapters
- `accelerate` - Distributed training
- `tqdm` - Progress bars
- `tensorboard` - Training görselleştirme

---

## 🚀 Hızlı Başlangıç

### 3 Adımda MORİ Eğitimi

```bash
# 1. Veri seti oluştur (20K örnek, ~3 dakika)
python generate_mori_dataset.py --samples 20000

# 2. Model eğit (5 epoch, ~2-3 saat RTX 5080'de)
python train_mori_rtx5080.py --epochs 5

# 3. Test et
python test_mori.py --model ./mori-model --chat
```

**İşte bu kadar!** ✨

---

## 📚 Adım Adım Eğitim

### Adım 1: Veri Seti Oluşturma

MORİ için Türkçe konuşma veri seti oluşturun:

```bash
python generate_mori_dataset.py --samples 20000 --output mori_dataset.jsonl
```

**Parametreler:**
- `--samples`: Örnek sayısı (default: 20000)
- `--output`: Çıktı dosya adı (default: mori_dataset.jsonl)

**Kategoriler:**
- 📊 Matematik (%30) - Sayma, toplama, çıkarma, çarpma
- 💕 Duygusal Destek (%25) - Üzgün, kızgın, korkmuş, mutlu
- 🌍 Çevre Bilinci (%15) - Doğa sevgisi, çöp, geri dönüşüm
- 🤝 Sosyal Beceriler (%15) - Paylaşmak, empati, teşekkür
- 📖 Masallar (%10) - Hikayeler, maceralar
- 🪥 Yaşam Becerileri (%5) - Diş fırçalama, uyku, temizlik

**Çıktı:**
```
✅ Veri Seti Oluşturuldu!
   Dosya: mori_dataset.jsonl
   Toplam: 20,000 örnek
   Boyut: 8.45 MB

📊 Kategori Dağılımı:
   math              6,000 ( 30.0%)
   emotion           5,000 ( 25.0%)
   environment       3,000 ( 15.0%)
   social            3,000 ( 15.0%)
   story             2,000 ( 10.0%)
   life_skills       1,000 (  5.0%)
```

### Adım 2: Model Eğitimi

#### Temel Kullanım (Gemma-2-2B ile)

```bash
python train_mori_rtx5080.py
```

Bu komut:
- ✅ Gemma-2-2B-it modelini indirir (~5GB)
- ✅ LoRA ile fine-tuning yapar (r=64)
- ✅ 5 epoch eğitir (~2-3 saat RTX 5080'de)
- ✅ `./mori-model` klasörüne kaydeder

#### Gelişmiş Kullanım

```bash
# 10 epoch, daha yüksek kalite
python train_mori_rtx5080.py --epochs 10

# Özel dataset ile
python train_mori_rtx5080.py --dataset my_custom_dataset.jsonl

# GPT2-medium ile (daha hızlı ama Türkçe daha zayıf)
python train_mori_rtx5080.py --model gpt2-medium --epochs 10

# Daha yüksek LoRA rank (daha iyi kalite, daha uzun süre)
python train_mori_rtx5080.py --lora-r 128 --epochs 10

# Tüm parametrelerle
python train_mori_rtx5080.py \
  --model google/gemma-2-2b-it \
  --dataset mori_dataset.jsonl \
  --output ./mori-model \
  --epochs 5 \
  --batch-size 8 \
  --lora-r 64 \
  --lr 2e-4 \
  --max-length 512
```

**Parametreler:**

| Parametre | Varsayılan | Açıklama |
|-----------|------------|----------|
| `--model` | `google/gemma-2-2b-it` | Base model |
| `--dataset` | `mori_dataset.jsonl` | Training dataset |
| `--output` | `./mori-model` | Model kayıt yeri |
| `--epochs` | `5` | Epoch sayısı |
| `--batch-size` | `8` | Batch size (RTX 5080 için 8-16 ideal) |
| `--lora-r` | `64` | LoRA rank (64-128 önerilir) |
| `--lr` | `2e-4` | Learning rate |
| `--max-length` | `512` | Maksimum token uzunluğu |

#### Model Seçenekleri

**1. Gemma-2-2B-it** (Önerilen ✅)
```bash
python train_mori_rtx5080.py --model google/gemma-2-2b-it
```
- ✅ En iyi Türkçe kalitesi
- ✅ 2B parametreli, modern
- ✅ RTX 5080'de rahat çalışır
- ⏱️ Eğitim: ~2-3 saat (5 epoch)

**2. GPT2-Medium**
```bash
python train_mori_rtx5080.py --model gpt2-medium --epochs 10
```
- ⚡ Çok hızlı (~1 saat)
- ⚠️ Türkçe biraz zayıf
- 💾 Küçük model (774M params)

**3. Turkish-GPT2-Large**
```bash
python train_mori_rtx5080.py --model ytu-ce-cosmos/turkish-gpt2-large --epochs 10
```
- 🇹🇷 Türkçe'ye özel
- 💾 774M params
- ⏱️ ~1-2 saat

### Adım 3: Training İzleme

#### TensorBoard ile Görselleştirme

```bash
# TensorBoard başlat (yeni terminal)
tensorboard --logdir ./mori-model/logs

# Tarayıcıda aç: http://localhost:6006
```

#### Training Çıktısı

```
🐻 MORİ FINE-TUNING - RTX 5080 OPTIMIZE
============================================================
Device: cuda
GPU: NVIDIA GeForce RTX 5080
VRAM: 16.0 GB
CUDA: 12.1
PyTorch: 2.5.0
✅ RTX 5080 tespit edildi - Optimal ayarlar aktif!
============================================================

📦 Model yükleniyor: google/gemma-2-2b-it
✓ Tokenizer yüklendi
  Vocab size: 256,000
  Pad token: <pad>

✓ Model yüklendi
  Parametreler: 2.61B
  Model tipi: torch.bfloat16
✓ Gradient checkpointing aktif

🔧 LoRA ayarlanıyor...
  Rank (r): 64
  Alpha: 128
  Dropout: 0.05
✓ LoRA aktif
  Trainable parametreler: 84.93M (3.26%)
  VRAM tasarrufu: ~4.9 GB

📚 Dataset yükleniyor: mori_dataset.jsonl
✓ Dataset yüklendi: 20,000 örnek

🔄 Tokenization yapılıyor...
✓ Tokenization tamamlandı
  Toplam örnek: 20,000
  Ortalama token: 145
  Max token: 512

============================================================
🎓 TRAINING BAŞLIYOR
============================================================
Epochs: 5
Batch size: 8
Gradient accumulation: 4
Effective batch size: 32
Learning rate: 0.0002
Warmup ratio: 0.03
LR scheduler: cosine
Precision: BF16
Gradient checkpointing: True
============================================================

Epoch 1/5:
[████████████████████] 625/625 [45:23<00:00, 0.23it/s]
Loss: 1.234 | LR: 0.00018

Epoch 2/5:
[████████████████████] 625/625 [45:12<00:00, 0.23it/s]
Loss: 0.876 | LR: 0.00015

...

✅ Training tamamlandı!
⏱️  Toplam süre: 2:31:45

💾 Model kaydediliyor: ./mori-model
✓ Model kaydedildi
  Base + LoRA: ./mori-model
  Sadece LoRA: ./mori-model/lora_adapters
  Toplam boyut: 5.23 GB

============================================================
🎉 MORİ FINE-TUNING TAMAMLANDI!
============================================================
```

---

## 🎮 Model Kullanımı

### Test Örnekleri Çalıştır

```bash
python test_mori.py --model ./mori-model --test
```

**Çıktı:**
```
🧪 Test Örnekleri Çalıştırılıyor...

[1/10] Çocuk: Mori, 5 artı 3 kaç eder?
🐻 MORİ: Hadi patlatalım! 💥 5 + 3 = 8 çiçek açtı! 🌸🌸🌸🌸🌸🌸🌸🌸 Sen harikasın! ❤️✨

[2/10] Çocuk: Üzgünüm Mori
🐻 MORİ: Gel buraya minik yıldızım, sana sarılayım... 🤗 Bu duygular normal, ama şimdi birlikte gülümseyeceğiz! Sen en güçlü çocuksun! 🌟❤️

[3/10] Çocuk: Denize çöp atsak olur mu?
🐻 MORİ: Asla çöp atmayalım doğaya! 🌍 Balıklar ve ağaçlar bize sarılıyor, biz de onlara sarılalım! Sen minik kahramansın! 🦸❤️

...
```

### İnteraktif Sohbet Modu

```bash
python test_mori.py --model ./mori-model --chat
```

```
💬 MORİ ile Sohbet!
   (Çıkmak için 'exit' veya 'çıkış' yazın)

🧒 Sen: Merhaba Mori!
🐻 MORİ: Merhaba tatlı yavrum! 🐻💜 Bugün nasılsın? Hadi birlikte eğlenelim! ✨

🧒 Sen: 7 + 5 kaç eder?
🐻 MORİ: Yaşasın! 🎉 7 artı 5 eşittir 12! Matematik sihirbazısın! 🌸🌸🌸🌸🌸🌸🌸🌸🌸🌸🌸🌸 ✨

🧒 Sen: Bana bir masal anlatır mısın?
🐻 MORİ: Bir varmış bir yokmuş... 📖✨ Evvel zaman içinde, sayılar diyarında bir macera başlamış! Rakam 7 ile rakam 3 birlikte yola çıkmışlar... Ve 10 olmuşlar! 🎉 Çünkü birlikte her şey daha güzel! 💕

🧒 Sen: çıkış
🐻 MORİ: Görüşmek üzere tatlım! Seni çok seviyorum! ❤️✨
```

### Tek Soru Testi

```bash
python test_mori.py --model ./mori-model --prompt "Ağaçları neden korumalıyız?"
```

```
🧒 Soru: Ağaçları neden korumalıyız?
🐻 MORİ: Ağaçlar bizim arkadaşımız! 🌳 Onlar bize temiz hava veriyor! 💨 Ağaç dikelim, dünyayı güzelleştirelim! 🌱✨ Sen harika bir çevrecisin! 💚
```

### Parametrelerle Oyna

```bash
# Daha yaratıcı cevaplar (yüksek temperature)
python test_mori.py --model ./mori-model --chat --temperature 0.9

# Daha uzun cevaplar
python test_mori.py --model ./mori-model --chat --max-tokens 300

# Daha tutarlı cevaplar (düşük temperature)
python test_mori.py --model ./mori-model --chat --temperature 0.5
```

---

## 🔧 Teknik Detaylar

### Model Mimarisi

```
Base Model: Gemma-2-2B-it (2.6B parameters)
├── Embedding Layer (256K vocab)
├── 26x Transformer Blocks
│   ├── Multi-Head Attention (q, k, v, o projections)
│   ├── MLP (gate, up, down projections)
│   └── LayerNorm
└── LM Head

+ LoRA Adapters (r=64)
  ├── q_proj: 64 rank adapters
  ├── k_proj: 64 rank adapters
  ├── v_proj: 64 rank adapters
  ├── o_proj: 64 rank adapters
  ├── gate_proj: 64 rank adapters
  ├── up_proj: 64 rank adapters
  └── down_proj: 64 rank adapters

Total: 2.6B base + 85M trainable = 2.685B
Trainable: 3.26% (only LoRA weights)
```

### Training Pipeline

```
1. Dataset Loading
   ├── Load JSONL file (20K samples)
   ├── Parse instruction/input/output
   └── Shuffle & split

2. Tokenization
   ├── Apply chat template (Gemma format)
   ├── Tokenize to input_ids
   ├── Truncate to max_length (512)
   └── Create labels for causal LM

3. DataLoader
   ├── Batch size: 8
   ├── Gradient accumulation: 4
   ├── Dynamic padding (collator)
   └── Effective batch: 32

4. Optimization
   ├── Optimizer: AdamW (torch)
   ├── LR: 2e-4 (cosine schedule)
   ├── Warmup: 3% of steps
   ├── Weight decay: 0.01
   └── Gradient clipping: 1.0

5. Training Loop
   ├── Forward pass (BF16)
   ├── Compute loss (cross-entropy)
   ├── Backward pass
   ├── Gradient accumulation
   ├── Optimizer step
   └── LR scheduler step

6. Checkpointing
   ├── Save every 500 steps
   ├── Keep last 3 checkpoints
   └── Final model + LoRA adapters
```

### Bellek Kullanımı (RTX 5080 16GB)

| Bileşen | VRAM |
|---------|------|
| Base model (BF16) | ~5.2 GB |
| LoRA adapters | ~0.3 GB |
| Optimizer states | ~0.6 GB |
| Gradients | ~0.3 GB |
| Activations (batch=8) | ~4.0 GB |
| Gradient checkpointing tasarrufu | ~-2.0 GB |
| **Toplam** | **~8.4 GB** |
| **Kalan VRAM** | **~7.6 GB** |

> ✅ RTX 5080 16GB için **rahat çalışır**, %50'den az VRAM kullanımı.

### Eğitim Süresi Tahmini

| Konfigürasyon | RTX 5080 | RTX 4090 | RTX 3090 |
|---------------|----------|----------|----------|
| 20K, 5 epoch, batch=8 | ~2.5 saat | ~3 saat | ~4.5 saat |
| 50K, 5 epoch, batch=8 | ~6 saat | ~7.5 saat | ~11 saat |
| 100K, 10 epoch, batch=8 | ~24 saat | ~30 saat | ~44 saat |

---

## 🐛 Sorun Giderme

### CUDA Out of Memory Hatası

```
RuntimeError: CUDA out of memory
```

**Çözüm 1**: Batch size'ı düşür
```bash
python train_mori_rtx5080.py --batch-size 4
```

**Çözüm 2**: Gradient accumulation artır (aynı effective batch)
```bash
python train_mori_rtx5080.py --batch-size 4 --gradient-accumulation 8
```

**Çözüm 3**: Max length kısalt
```bash
python train_mori_rtx5080.py --max-length 256
```

### Model İndirme Hatası

```
HTTPError: 403 Forbidden
```

**Çözüm**: Hugging Face token ile login
```bash
pip install huggingface_hub
huggingface-cli login
```

### Windows Multiprocessing Hatası

```
RuntimeError: DataLoader worker exited unexpectedly
```

**Çözüm**: `num_proc` parametresini kaldır veya 0 yap
```python
# generate_mori_dataset.py içinde:
num_proc=1  # veya sil
```

### TensorBoard Açılmıyor

```bash
# Port değiştir
tensorboard --logdir ./mori-model/logs --port 6007
```

---

## ❓ SSS (Sık Sorulan Sorular)

### 1. Hangi GPU'ya ihtiyacım var?

**Minimum**: RTX 3060 12GB
**Önerilen**: RTX 5080 16GB veya RTX 4090 24GB

### 2. CPU ile eğitim yapabilir miyim?

Teknik olarak evet ama **çok yavaş**. RTX 5080'de 2.5 saat süren eğitim, CPU'da **3-5 gün** sürebilir. GPU şart!

### 3. Kaç veri ile başlamalıyım?

- **Test için**: 5K-10K örnek
- **Prototip için**: 20K örnek ✅
- **Production için**: 50K-100K örnek

### 4. LoRA rank'i nasıl seçmeliyim?

- **r=32**: Hızlı, düşük kalite
- **r=64**: Dengeli, önerilen ✅
- **r=128**: Yüksek kalite, yavaş

### 5. Eğitim ne kadar sürer?

RTX 5080 ile:
- 20K veri, 5 epoch: **~2.5 saat**
- 50K veri, 5 epoch: **~6 saat**
- 100K veri, 10 epoch: **~24 saat**

### 6. Model dosyası ne kadar yer kaplar?

- Gemma-2-2B + LoRA: **~5.2 GB**
- Sadece LoRA adapters: **~340 MB**
- GPT2-medium + LoRA: **~1.8 GB**

### 7. MORİ'yi mobil uygulamaya nasıl entegre ederim?

1. **Quantization**: GGUF formatına çevir (llama.cpp)
2. **Model boyutunu küçült**: 4-bit quantization (~1.3 GB)
3. **iOS**: MLX framework kullan
4. **Android**: llama.cpp + JNI

Detaylı kılavuz: `DEPLOYMENT.md` (yakında)

### 8. Veri setini nasıl özelleştiririm?

`generate_mori_dataset.py` dosyasını düzenle:
```python
# Yeni kategori ekle
self.custom_prompts = [
    "Yeni soru 1",
    "Yeni soru 2",
]

# Cevap fonksiyonu yaz
def _generate_custom_response(self, prompt: str) -> str:
    return "MORİ'nin özel cevabı! ✨"
```

### 9. Başka dilde (İngilizce, Arapça, vb.) eğitebilir miyim?

Evet! Sadece veri setini o dilde oluştur:
```python
# generate_mori_dataset.py içinde
self.math_prompts = [
    "Mori, what is {a} plus {b}?",
    "{a} + {b} = ?",
    ...
]
```

### 10. MORİ'yi ticari projede kullanabilir miyim?

- ✅ Gemma-2 lisansı: Ticari kullanım OK ([Gemma Terms](https://ai.google.dev/gemma/terms))
- ✅ MORİ veri seti: Açık kaynak (MIT)
- ✅ Bu repo: MIT License

---

## 🎯 Performans Optimizasyonu

### RTX 5080 için En İyi Ayarlar

```bash
python train_mori_rtx5080.py \
  --model google/gemma-2-2b-it \
  --epochs 5 \
  --batch-size 12 \
  --gradient-accumulation 3 \
  --lora-r 64 \
  --lr 2e-4 \
  --max-length 512
```

Bu ayarlar:
- ✅ Effective batch = 36 (ideal)
- ✅ VRAM kullanımı: ~11 GB (%68)
- ✅ Training hızı: ~2 saat
- ✅ Model kalitesi: Mükemmel

### Hız vs Kalite Dengesi

| Konfigürasyon | Süre | Kalite | VRAM |
|---------------|------|--------|------|
| **Hızlı** (r=32, batch=16) | 1.5 saat | ⭐⭐⭐ | 9 GB |
| **Dengeli** (r=64, batch=12) | 2 saat | ⭐⭐⭐⭐ | 11 GB |
| **Kaliteli** (r=128, batch=8) | 3.5 saat | ⭐⭐⭐⭐⭐ | 13 GB |

---

## 📊 Beklenen Sonuçlar

### Training Metrikleri

Başarılı bir eğitimde:
- **İlk epoch loss**: ~2.5-3.0
- **Son epoch loss**: ~0.5-0.8
- **Overfitting**: Loss 0.3'ün altına düşmemeli
- **Learning rate**: Cosine decay ile smooth düşmeli

### Qualitative Değerlendirme

İyi bir MORİ modeli:
- ✅ Matematik sorularına doğru cevap verir (5+3=8)
- ✅ Duygusal destek içerikli, sevimli konuşur
- ✅ Bol emoji kullanır ama aşırıya kaçmaz
- ✅ Çocuk diline uygun, basit cümleler kurar
- ✅ Her cevap pozitif ve cesaretlendirici

Kötü sinyaller:
- ❌ Matematik hatası (5+3=9)
- ❌ Emoji kullanmıyor veya çok fazla
- ❌ Karmaşık, yetişkin dili
- ❌ Negatif, korkutucu ifadeler
- ❌ İngilizce karışması

---

## 🚀 Sonraki Adımlar

1. **Veri Artırma**: 100K örneğe çıkar
2. **Multimodal**: Görsel + metin desteği ekle
3. **Ses Entegrasyonu**: TTS ile MORİ'ye ses ver
4. **Mobil Deployment**: iOS/Android uygulaması
5. **A/B Testing**: Çocuklar ile gerçek testler

---

## 📞 Destek & Katkı

- **Issues**: [GitHub Issues](https://github.com/yourusername/mori-training/issues)
- **Discord**: [NIRVANA Community](https://discord.gg/nirvana)
- **Email**: support@nirvana-ai.com

---

## 📄 Lisans

MIT License - Ticari kullanım dahil tüm haklar saklıdır.

**MORİ Projesi © 2025 NIRVANA**

---

## 🙏 Teşekkürler

- **Gemma Team** - Base model
- **Hugging Face** - Transformers & PEFT
- **PyTorch Team** - Framework
- **Defne** - İlk beta tester 💕

---

**MORİ ile mutlu eğitimler!** 🐻💜✨
