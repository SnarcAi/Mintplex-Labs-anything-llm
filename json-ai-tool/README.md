# 🚀 JSON AI Tool - Standalone Python CLI

**Qwen 2.5 7B ile offline JSON işlemleri - AnythingLLM gerektirmez**

---

## ✨ Özellikler

- ✅ **JSON Validation** - Syntax ve schema kontrolü
- 🔧 **Auto-Fix** - Otomatik hata düzeltme (AI veya rule-based)
- 📊 **Analysis** - Detaylı yapı analizi
- 🧬 **Schema Inference** - Otomatik JSON Schema çıkarma
- 🎲 **Data Generation** - Realistic veri üretimi (AI veya template)
- 🔒 **Fully Offline** - Internet gerektirmez
- ⚡ **RTX 5080 Optimized** - GPU hızlandırma

---

## 📦 Kurulum

### 1. Gereksinimler
```bash
pip install torch transformers peft datasets accelerate
```

veya

```bash
pip install -r requirements.txt
```

### 2. Model Kontrolü
Qwen 2.5 7B Instruct modeliniz HF cache'de olmalı:
```
C:\Users\Superuser\.cache\huggingface\hub\models--Qwen--Qwen2.5-7B-Instruct\
```

Tool otomatik bulur. Manuel belirtmek için: `--model /path/to/model`

---

## 🎯 Kullanım

### Temel Komutlar

#### 1. JSON Validation
```bash
# Dosyadan
python json_ai.py validate data.json

# String'den
python json_ai.py validate '{"name": "test", "age": 25}'

# AI olmadan (hızlı)
python json_ai.py validate data.json --no-ai
```

#### 2. JSON Fix (Otomatik Düzeltme)
```bash
# Rule-based (hızlı)
python json_ai.py fix broken.json

# AI ile (daha güçlü)
python json_ai.py fix broken.json --ai

# Örnek
python json_ai.py fix '{"name": "test", "age": 25,}'
```

#### 3. JSON Analysis
```bash
python json_ai.py analyze data.json --pretty
```

#### 4. Data Generation

**AI olmadan (çok hızlı):**
```bash
# 1000 user kaydı
python json_ai.py generate --count 1000 --type user --output users.json

# 500 product kaydı
python json_ai.py generate --count 500 --type product --output products.json
```

**AI ile (daha realistic):**
```bash
python json_ai.py generate --count 100 --type user --output users.json
# (AI otomatik kullanılır)
```

**Template'den:**
```bash
# template.json:
# {
#   "userId": "{{index}}",
#   "email": "user{{index}}@example.com",
#   "uuid": "{{uuid}}",
#   "timestamp": "{{timestamp}}"
# }

python json_ai.py generate --template template.json --count 500 --output data.json
```

---

## 🎓 Fine-Tuning

### 1. Training Dataset Oluştur
```bash
# 4000 örnek (500 x 8 task tipi)
python generate_dataset.py --count 500 --output json_training_dataset.jsonl
```

### 2. Fine-Tune Başlat
```bash
# Varsayılan ayarlarla (RTX 5080 optimize)
python finetune.py --dataset json_training_dataset.jsonl --output qwen-json-assistant

# Custom ayarlarla
python finetune.py \
  --dataset json_training_dataset.jsonl \
  --output my-json-model \
  --epochs 3 \
  --batch-size 4 \
  --lora-r 32 \
  --lr 2e-4
```

**RTX 5080'de beklenen süre:** ~1-2 saat (4000 örnek için)

### 3. Fine-tuned Model Kullan
```bash
python json_ai.py --model ./qwen-json-assistant generate --count 1000
```

---

## ⚙️ Konfigürasyon

### Model Ayarları

**Auto-detect (önerilen):**
```bash
python json_ai.py validate data.json
# HF cache'den otomatik bulur
```

**Manuel path:**
```bash
python json_ai.py --model "C:\Users\...\Qwen2.5-7B-Instruct\snapshots\abc123" validate data.json
```

### AI Kullanımı

**AI aktif (default):**
```bash
python json_ai.py fix broken.json
# Model yüklenir, GPU kullanır
```

**AI kapalı (çok hızlı):**
```bash
python json_ai.py --no-ai validate data.json
# Model yüklenmez, rule-based
```

### Fine-Tuning Ayarları

`finetune.py` içinde:

```python
class FineTuneConfig:
    batch_size: int = 4           # VRAM'e göre ayarlayın
    gradient_accumulation_steps: int = 4  # Effective batch = 16
    lora_r: int = 32              # 16-64 arası (büyük = daha güçlü ama yavaş)
    learning_rate: float = 2e-4   # 1e-4 ile 5e-4 arası
    num_epochs: int = 3           # 2-5 arası
```

**RTX 5080 16GB için önerilen:**
- `batch_size = 4` (gradient_accumulation = 4 ile effective 16)
- `lora_r = 32` veya 64
- `bf16 = True` (fp16 yerine)

---

## 📊 Performans

### İnference Hızı (RTX 5080)

| İşlem | AI Kapalı | AI Aktif |
|-------|-----------|----------|
| Validate (1000 kayıt) | <1s | N/A |
| Fix (100 kayıt) | <1s | ~10s |
| Generate (1000 kayıt) | ~2s | ~30s |
| Analysis | <1s | ~5s |

### Fine-Tuning (RTX 5080 16GB)

| Dataset Size | Epochs | Time | VRAM Usage |
|--------------|--------|------|------------|
| 1000 examples | 3 | ~20 min | ~10 GB |
| 4000 examples | 3 | ~1.5 hr | ~12 GB |
| 10000 examples | 3 | ~4 hr | ~14 GB |

---

## 🛠️ Troubleshooting

### "CUDA out of memory"
```bash
# finetune.py'de batch_size'ı düşürün:
python finetune.py --batch-size 2  # 4 yerine
```

### "Model bulunamadı"
```bash
# Manuel path verin:
python json_ai.py --model "C:\Users\Superuser\.cache\huggingface\hub\models--Qwen--Qwen2.5-7B-Instruct\snapshots\..." validate data.json
```

### "Çok yavaş"
```bash
# AI'ı kapatın:
python json_ai.py --no-ai validate data.json
# veya
# Template-based generation kullanın (AI yerine)
```

---

## 📚 Örnekler

### Örnek 1: 10K User Kaydı Üret (AI olmadan)
```bash
python json_ai.py generate --count 10000 --type user --output users_10k.json --no-ai
# ~3 saniye, AI yüklenmez
```

### Örnek 2: Broken JSON Düzelt (AI ile)
```bash
echo '{"name": "test", "age": 25,}' | python json_ai.py fix - --ai
```

### Örnek 3: JSON Analiz + Pretty Print
```bash
python json_ai.py analyze complex_data.json --pretty > analysis.json
```

### Örnek 4: Fine-tune + Test
```bash
# 1. Dataset oluştur
python generate_dataset.py --count 500

# 2. Fine-tune
python finetune.py --epochs 3

# 3. Test et
python json_ai.py --model ./qwen-json-assistant generate --count 100
```

---

## 🔧 İleri Seviye

### Custom Task Type Ekle

`json_ai.py` içinde:

```python
def _generate_basic(self, count: int, data_type: str):
    # ...
    elif data_type == "my_custom_type":
        record = {
            "id": i + 1,
            "custom_field": "value",
            # ...
        }
```

### Fine-tuning Dataset'ini Özelleştir

`generate_dataset.py` içinde yeni task fonksiyonları ekleyin:

```python
def gen_my_custom_task(self) -> Dict:
    return {
        "instruction": "Do something specific",
        "input": "...",
        "output": "..."
    }
```

---

## 📝 Dosya Yapısı

```
json-ai-tool/
├── json_ai.py              # Ana CLI tool
├── finetune.py             # Fine-tuning script
├── generate_dataset.py     # Dataset generator
├── requirements.txt        # Python dependencies
├── README.md               # Bu dosya
└── examples/
    ├── template.json       # Örnek template
    └── test_data.json      # Test verisi
```

---

## 🎉 Hızlı Başlangıç (3 Adım)

```bash
# 1. Install
pip install -r requirements.txt

# 2. Test (AI olmadan - hızlı)
python json_ai.py validate '{"test": true}' --no-ai

# 3. Generate data
python json_ai.py generate --count 1000 --type user --output users.json --no-ai
```

**Hepsi bu! AnythingLLM gerektirmez, standalone çalışır.**

---

**License:** MIT
**Python:** 3.13+
**GPU:** RTX 5080 16GB için optimize edildi
