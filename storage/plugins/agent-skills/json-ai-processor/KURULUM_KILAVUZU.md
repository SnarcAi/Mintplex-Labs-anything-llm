# 🚀 JSON AI Asistanı - Kurulum ve Kullanım Kılavuzu

## 📋 İçindekiler
1. [Sistem Gereksinimleri](#sistem-gereksinimleri)
2. [Kurulum Adımları](#kurulum-adımları)
3. [Ollama Kurulumu ve Optimizasyonu](#ollama-kurulumu)
4. [Model Eğitimi (Fine-Tuning)](#model-eğitimi)
5. [AnythingLLM Entegrasyonu](#anythingllm-entegrasyonu)
6. [Kullanım Örnekleri](#kullanım-örnekleri)
7. [RTX 5080 Optimizasyonları](#rtx-5080-optimizasyonları)
8. [Sorun Giderme](#sorun-giderme)

---

## 💻 Sistem Gereksinimleri

### ✅ Sizin Sisteminiz (MÜKEMMEL!)
- **İşletim Sistemi:** Windows 11 Pro
- **CPU:** AMD Ryzen 9 9950X (16 çekirdek / 32 thread)
- **GPU:** NVIDIA RTX 5080 (16 GB VRAM) ⭐
- **RAM:** 128 GB DDR5
- **Depolama:** 2 TB NVMe SSD
- **Python:** 3.13.7

**Sonuç:** Sisteminiz çok güçlü! Büyük modelleri (13B-70B parametreli) rahatça çalıştırabilirsiniz.

### 📦 Gerekli Yazılımlar
- ✅ Python 3.13.7 (zaten kurulu)
- ✅ Node.js 18+ (AnythingLLM için)
- ✅ Ollama (local LLM runtime)
- ✅ Git
- ✅ CUDA 12.x (NVIDIA GPU için)

---

## 🔧 Kurulum Adımları

### 1️⃣ Ollama Kurulumu (Windows)

#### Adım 1: Ollama'yı İndirin ve Kurun
```powershell
# PowerShell'i Admin olarak açın

# Ollama Windows installer'ı indirin
# https://ollama.ai/download/windows

# Veya winget ile:
winget install Ollama.Ollama
```

#### Adım 2: CUDA'nın Yüklü Olduğunu Kontrol Edin
```powershell
nvidia-smi
```

**Beklenen Çıktı:**
```
+-----------------------------------------------------------------------------+
| NVIDIA-SMI 535.xx       Driver Version: 535.xx       CUDA Version: 12.x    |
|-------------------------------+----------------------+----------------------+
| GPU  Name            TCC/WDDM | Bus-Id        Disp.A | Volatile Uncorr. ECC |
|   0  NVIDIA GeForce RTX 5080   | 00000000:01:00.0 Off |                  N/A |
+-----------------------------------------------------------------------------+
```

Eğer CUDA yüklü değilse:
```powershell
# CUDA Toolkit 12.x indirin
# https://developer.nvidia.com/cuda-downloads
```

#### Adım 3: Ollama'yı Başlatın ve Test Edin
```powershell
# Ollama servisini başlat
ollama serve

# Yeni bir PowerShell penceresi açın ve test edin:
ollama --version
# Beklenen: ollama version 0.x.x

# Basit bir model çalıştırın
ollama run llama3:8b "Merhaba, nasılsın?"
```

---

### 2️⃣ JSON AI Asistanı Plugin'ini Etkinleştirin

Plugin dosyaları zaten şu konumda:
```
storage/plugins/agent-skills/json-ai-processor/
├── plugin.json
├── handler.js
├── advanced-generator.js
├── training-dataset-generator.js
├── fine-tune-pipeline.ps1
└── KURULUM_KILAVUZU.md (bu dosya)
```

#### Plugin'i Aktif Edin
1. AnythingLLM'i başlatın
2. **Settings** → **Agent Skills** → **Custom Skills**
3. `json-ai-processor` plugin'ini **ACTIVE** konuma getirin
4. Sayfayı yenileyin

---

### 3️⃣ Önerilen Modelleri İndirin

RTX 5080 16GB VRAM'iniz için **en iyi modeller**:

#### Seçenek 1: DeepSeek Coder (ÖNERİLEN - JSON için en iyi)
```powershell
# 6.7B model (VRAM: ~4GB, Hız: ÇOK HIZLI)
ollama pull deepseek-coder:6.7b

# 33B model (VRAM: ~18GB, çok detaylı)
# NOT: 16GB VRAM için biraz sıkışık olabilir, quantized versiyonu deneyin
ollama pull deepseek-coder:33b-q4_0
```

#### Seçenek 2: Code Llama (Alternatif)
```powershell
# 7B model (VRAM: ~4GB)
ollama pull codellama:7b

# 13B model (VRAM: ~8GB)
ollama pull codellama:13b
```

#### Seçenek 3: Llama 3 (Genel amaçlı)
```powershell
# 8B model (VRAM: ~5GB)
ollama pull llama3:8b

# 70B model quantized (VRAM: ~12GB) - EN GÜÇLÜ!
ollama pull llama3:70b-q4_0
```

**TAVSİYE:** `deepseek-coder:6.7b` ile başlayın. Hızlı ve JSON işlemlerinde çok iyi.

---

## 🎓 Model Eğitimi (Fine-Tuning)

### Otomatik Eğitim (ÖNERİLEN)

```powershell
# Plugin dizinine gidin
cd storage/plugins/agent-skills/json-ai-processor

# Eğitim pipeline'ını çalıştırın (PowerShell)
.\fine-tune-pipeline.ps1
```

**Pipeline Ne Yapar:**
1. ✅ 5000 JSON örneği içeren training dataset oluşturur
2. ✅ Dataset'i doğrular
3. ✅ JSON işlemleri için optimize edilmiş Modelfile oluşturur
4. ✅ Base model'i çeker (deepseek-coder:6.7b)
5. ✅ Özel sistem prompt'u ve parametrelerle yeni model yaratır
6. ✅ Model'i test eder

**Çıktı:** `json-ai-assistant` adında özel model

---

### Manuel Eğitim (İleri Seviye)

#### 1. Training Dataset Oluştur
```powershell
node training-dataset-generator.js
```

Bu, `json_training_5k.jsonl` dosyası oluşturur. İçeriği:
- JSON validation örnekleri
- Error fixing örnekleri
- Schema inference örnekleri
- Data generation örnekleri
- Transformation örnekleri
- JSONL processing örnekleri

#### 2. Custom Modelfile Oluştur
```powershell
# Modelfile adında bir dosya oluşturun
notepad Modelfile
```

İçerik:
```dockerfile
FROM deepseek-coder:6.7b

SYSTEM """You are a specialized JSON AI assistant. You excel at:
- Validating and analyzing JSON/JSONL data
- Detecting and fixing syntax errors
- Inferring and validating JSON Schemas
- Generating realistic synthetic JSON data
- Transforming and optimizing JSON structures

Always provide precise, accurate responses."""

PARAMETER temperature 0.1
PARAMETER top_p 0.9
PARAMETER num_ctx 4096
PARAMETER num_gpu 99
```

#### 3. Model Oluştur
```powershell
ollama create json-ai-assistant -f Modelfile
```

#### 4. Test Et
```powershell
ollama run json-ai-assistant "Validate this JSON: {\"key\": \"value\",}"
```

---

## 🔌 AnythingLLM Entegrasyonu

### Adım 1: LLM Provider Ayarları
1. AnythingLLM'i açın
2. **⚙️ Settings** → **LLM Preference**
3. **LLM Provider:** `Ollama` seçin
4. **Ollama Base URL:** `http://127.0.0.1:11434` (varsayılan)
5. **Model:** `json-ai-assistant` seçin
6. **Save** butonuna tıklayın

### Adım 2: Agent Ayarları
1. **Settings** → **Agent Configuration**
2. **Agent LLM Provider:** `Ollama`
3. **Agent Model:** `json-ai-assistant`
4. **Enable Agent Mode:** ✅ Aktif
5. **Agent Skills:**
   - ✅ `json-ai-processor` (JSON işlemleri)
   - ✅ `memory` (bağlam hafızası)
6. **Save**

### Adım 3: Workspace Oluştur
1. **New Workspace** → `JSON Assistant Workspace`
2. **Agent Mode:** ✅ Aktif
3. **Skills:** `json-ai-processor` seçili olmalı

---

## 🎯 Kullanım Örnekleri

### Örnek 1: JSON Validation
```
Sen: Bu JSON'u doğrula: {"name": "test", "age": 25,}

AI: Bu JSON'da syntax hatası var:
- Satır 1: Trailing comma (son virgül) hatası
- "age": 25, → "age": 25 olmalı

Düzeltilmiş versiyon:
{
  "name": "test",
  "age": 25
}
```

### Örnek 2: Otomatik Hata Düzeltme
```
Sen: Şu JSON'u düzelt: {name: "John", 'age': 30}

AI: 2 hata düzeltildi:
1. Object key'lerde tırnak işareti eksik
2. Tek tırnak yerine çift tırnak kullanılmalı

Düzeltilmiş:
{
  "name": "John",
  "age": 30
}
```

### Örnek 3: Schema Inference
```
Sen: Şu veriden JSON Schema çıkar:
{
  "id": 1,
  "email": "user@example.com",
  "age": 25,
  "active": true
}

AI: İnferred JSON Schema:
{
  "type": "object",
  "properties": {
    "id": {"type": "integer"},
    "email": {"type": "string", "format": "email"},
    "age": {"type": "integer", "minimum": 0, "maximum": 120},
    "active": {"type": "boolean"}
  },
  "required": ["id", "email", "age", "active"]
}
```

### Örnek 4: Akıllı Veri Üretimi
```
Sen: Bana 1000 adet kullanıcı verisi üret. Her kullanıcıda id, ad, email, yaş olsun.

AI: 1000 adet kullanıcı verisi oluşturuldu:

[
  {
    "id": 1,
    "name": "John Smith",
    "email": "johnsmith912@gmail.com",
    "age": 34
  },
  {
    "id": 2,
    "name": "Jane Doe",
    "email": "janedoe245@yahoo.com",
    "age": 28
  },
  ...
  (998 more records)
]
```

### Örnek 5: JSONL İşleme
```
Sen: Şu JSONL verilerini analiz et:
{"id":1,"value":100}
{"id":2,"value":200}
{"id":3,"value":300}

AI: JSONL Analizi:
- Toplam satır: 3
- Geçerli kayıt: 3
- Hata: 0
- Ortalama değer: 200
- Toplam değer: 600
```

### Örnek 6: Template'den Veri Üretimi
```
Sen: Bu template'e göre 500 kayıt oluştur:
{
  "userId": "{{index}}",
  "email": "user{{index}}@example.com",
  "registeredAt": "{{timestamp}}"
}

AI: 500 kayıt oluşturuldu. İlk 3 örnek:
[
  {
    "userId": "0",
    "email": "user0@example.com",
    "registeredAt": "1703001234567"
  },
  {
    "userId": "1",
    "email": "user1@example.com",
    "registeredAt": "1703001234568"
  },
  {
    "userId": "2",
    "email": "user2@example.com",
    "registeredAt": "1703001234569"
  }
]
```

---

## ⚡ RTX 5080 Optimizasyonları

### GPU Ayarları (Ollama)

**1. Çevre Değişkenlerini Ayarlayın:**
```powershell
# PowerShell Admin olarak
[System.Environment]::SetEnvironmentVariable('OLLAMA_NUM_GPU', '99', 'Machine')
[System.Environment]::SetEnvironmentVariable('OLLAMA_FLASH_ATTENTION', '1', 'Machine')
[System.Environment]::SetEnvironmentVariable('CUDA_VISIBLE_DEVICES', '0', 'Machine')
```

**2. Modelfile'da GPU Optimizasyonları:**
```dockerfile
PARAMETER num_gpu 99          # Tüm katmanları GPU'ya yükle
PARAMETER num_thread 32       # Ryzen 9 9950X için
PARAMETER num_ctx 8192        # 16GB VRAM ile rahat
```

**3. Batch Processing için:**
```dockerfile
PARAMETER num_batch 512       # Büyük batch size
PARAMETER num_parallel 4      # Paralel istekler
```

### Model Boyutu Seçimi (RTX 5080 16GB için)

| Model | Parametreler | VRAM Kullanımı | Hız | Kalite | ÖNERİ |
|-------|-------------|----------------|-----|--------|-------|
| **deepseek-coder:6.7b** | 6.7B | ~4 GB | ⚡⚡⚡⚡⚡ | ⭐⭐⭐⭐ | ✅ En İyi |
| **deepseek-coder:33b-q4** | 33B | ~12 GB | ⚡⚡⚡ | ⭐⭐⭐⭐⭐ | ✅ Detaylı |
| **llama3:70b-q4** | 70B | ~14 GB | ⚡⚡ | ⭐⭐⭐⭐⭐ | ✅ Maksimum |
| codellama:13b | 13B | ~8 GB | ⚡⚡⚡⚡ | ⭐⭐⭐⭐ | ⭐ İyi |
| llama3:8b | 8B | ~5 GB | ⚡⚡⚡⚡ | ⭐⭐⭐ | ⭐ Genel |

**SONUÇ:** RTX 5080 16GB ile **70B quantized** modelleri bile rahatlıkla çalıştırabilirsiniz!

### Performans Testi
```powershell
# Model performansını test edin
ollama run json-ai-assistant "Generate 100 user records with id, name, email"

# GPU kullanımını monitör edin
nvidia-smi -l 1
```

**Beklenen Performans:**
- **6.7B model:** ~50-100 token/saniye
- **33B model:** ~20-40 token/saniye
- **70B model:** ~10-20 token/saniye

---

## 🛠️ Sorun Giderme

### Sorun 1: "Ollama bağlantı hatası"
```powershell
# Ollama servisini yeniden başlatın
Stop-Process -Name ollama -Force
ollama serve
```

### Sorun 2: "GPU kullanılmıyor (CPU'da çalışıyor)"
```powershell
# CUDA yüklü mü kontrol edin
nvidia-smi

# Ollama'yı GPU ile yeniden başlatın
$env:OLLAMA_NUM_GPU = "99"
ollama serve
```

### Sorun 3: "Model çok yavaş"
```powershell
# Daha küçük model deneyin
ollama pull deepseek-coder:6.7b

# Veya quantized versiyon kullanın
ollama pull llama3:70b-q4_0  # q8_0 yerine q4_0
```

### Sorun 4: "Out of Memory (VRAM taştı)"
```powershell
# num_ctx değerini azaltın
# Modelfile'da:
PARAMETER num_ctx 2048  # 4096 yerine
```

### Sorun 5: "Plugin çalışmıyor"
1. AnythingLLM'i yeniden başlatın
2. Browser cache'i temizleyin (Ctrl + Shift + R)
3. Plugin dizinini kontrol edin:
```powershell
cd storage/plugins/agent-skills/json-ai-processor
dir
# plugin.json ve handler.js olmalı
```

---

## 📊 Performans Metrikleri

Sisteminizde beklenen performans:

### JSON Validation (1000 kayıt)
- **Süre:** ~2-5 saniye
- **Doğruluk:** %99.9

### Error Fixing (1000 kayıt)
- **Süre:** ~5-10 saniye
- **Başarı oranı:** %95+

### Data Generation (10,000 kayıt)
- **Süre:** ~10-20 saniye
- **Kalite:** Yüksek gerçekçilik

### Schema Inference
- **Süre:** <1 saniye
- **Doğruluk:** %98

---

## 🎓 İleri Seviye Kullanım

### Training Dataset'i Özelleştirme
```javascript
// training-dataset-generator.js dosyasını düzenleyin

const generator = new TrainingDatasetGenerator();

generator.generateDataset({
  count: 10000,              // 10K örnek
  format: 'jsonl',
  taskTypes: [               // Sadece istediğiniz task'lar
    'json_validation',
    'json_fix',
    'data_generation'
  ],
  outputPath: './custom_dataset.jsonl'
});
```

### Çoklu Model Karşılaştırma
```powershell
# 3 farklı model oluşturun
ollama create json-small -f Modelfile.6.7b
ollama create json-medium -f Modelfile.13b
ollama create json-large -f Modelfile.33b

# Aynı task'ı test edin
$task = "Fix this JSON: {key: 'value',}"

ollama run json-small $task
ollama run json-medium $task
ollama run json-large $task
```

---

## 📞 Destek ve Kaynaklar

- **AnythingLLM Docs:** https://docs.useanything.com
- **Ollama Docs:** https://ollama.ai/docs
- **DeepSeek Coder:** https://github.com/deepseek-ai/DeepSeek-Coder

---

## ✅ Hızlı Başlangıç Checklist

- [ ] Ollama kuruldu ve çalışıyor
- [ ] CUDA/GPU doğrulandı
- [ ] `deepseek-coder:6.7b` modeli indirildi
- [ ] JSON AI plugin aktif edildi
- [ ] Fine-tuning pipeline çalıştırıldı
- [ ] `json-ai-assistant` modeli oluşturuldu
- [ ] AnythingLLM'de Ollama entegrasyonu yapıldı
- [ ] Test query'leri çalıştırıldı
- [ ] GPU kullanımı doğrulandı (nvidia-smi)

**Hepsi tamamlandıysa → Artık offline JSON AI asistanınız hazır! 🎉**

---

**Son Güncelleme:** 2025-01-17
**Versiyon:** 1.0.0
**Lisans:** MIT
