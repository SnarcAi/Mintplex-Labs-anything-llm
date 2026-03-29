# 🚀 MissFlora Qwen 2.5 7B QLoRA Eğitimi - Kullanım Kılavuzu

## 📋 Sistem Gereksinimleri
✅ Sisteminiz mükemmel şekilde uyumlu!
- ✅ RTX 5080 16GB VRAM
- ✅ 128GB DDR5 RAM (Optimizer offloading için)
- ✅ Ryzen 9 9950X (16 core - veri işleme)
- ✅ 2TB NVMe SSD (Model ve checkpoint kaydetme)
- ✅ Python 3.13.7
- ✅ Windows 11 Pro

## 🎯 Optimizasyonlar

### 16GB VRAM'de Nasıl Çalışıyor?

| Teknik | Açıklama | VRAM Tasarrufu |
|--------|----------|----------------|
| **QLoRA 4-bit** | Model ağırlıkları 4-bit'e indirildi | 14GB → 3.5GB |
| **8-bit Optimizer** | AdamW optimizer 8-bit + CPU offload | 14GB → 0GB (RAM'de) |
| **Gradient Checkpointing** | Aktivasyonlar yeniden hesaplanıyor | ~2GB tasarruf |
| **Gradient Accumulation (16)** | Virtual batch size artırıldı | 0GB (eğitim kalitesi arttı) |

**Sonuç:** Toplam VRAM kullanımı ~6-8 GB (16GB'niz fazlasıyla yeterli!)

## 📦 Kurulum

### Adım 1: Gerekli kütüphaneleri yükle
```bash
cd C:\Users\Superuser
python -m pip install --upgrade pip
python -m pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
python -m pip install transformers datasets peft accelerate bitsandbytes scipy sentencepiece trl
```

### Adım 2: CUDA kontrol
```python
import torch
print(torch.cuda.is_available())  # True olmalı
print(torch.cuda.get_device_name(0))  # RTX 5080 görünmeli
```

## 🏃‍♂️ Eğitimi Başlat

```bash
cd C:\Users\Superuser
python missflora_qwen_training.py
```

## ⏰ Beklenen Süre

| Konfigürasyon | Tahmini Süre | Açıklama |
|---------------|--------------|----------|
| **5 epoch** (script varsayılan) | **2-4 saat** | Hızlı prototip test |
| **10 epoch** | **4-8 saat** | Dengeli kalite |
| **20 epoch** | **8-16 saat** | Yüksek kalite |
| **50 epoch** | **20-40 saat** | Maksimum kalite |

**Script'teki `num_train_epochs=5` satırını değiştirerek epoch sayısını artırabilirsiniz.**

## 📊 VRAM/RAM Kullanımı (Canlı İzleme)

### GPU VRAM İzleme (Terminal 1)
```bash
nvidia-smi -l 1
```

### RAM İzleme (Task Manager)
- Ctrl+Shift+Esc → Performance → Memory
- **Beklenen RAM kullanımı:** 20-40 GB (Optimizer offloading)

## 🧪 Eğitim Sonrası Test

Eğitim bittikten sonra script otomatik test yapar. Manuel test için:

```python
from peft import AutoPeftModelForCausalLM
from transformers import AutoTokenizer
import torch

# Model yükle
model_path = "./missflora-qwen-final-YYYYMMDD_HHMMSS"  # Eğitim çıktı klasörü
model = AutoPeftModelForCausalLM.from_pretrained(
    model_path,
    device_map="auto",
    torch_dtype=torch.bfloat16
)
tokenizer = AutoTokenizer.from_pretrained(model_path)

# Test et
def ask_missflora(question):
    messages = [
        {"role": "system", "content": "Sen MissFlora müşteri hizmetleri asistanısın."},
        {"role": "user", "content": question}
    ]

    text = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
    inputs = tokenizer(text, return_tensors="pt").to(model.device)

    outputs = model.generate(
        **inputs,
        max_new_tokens=256,
        temperature=0.7,
        top_p=0.9,
        do_sample=True
    )

    response = tokenizer.decode(outputs[0][inputs['input_ids'].shape[1]:], skip_special_tokens=True)
    return response

# Kullan
print(ask_missflora("MissFlora Nem Alıcı ne kadar dayanır?"))
```

## 🌐 Web Entegrasyonu (missflora.com.tr)

Sonraki adım için `web_integration.py` dosyasına bakın.

## 🔧 Sorun Giderme

### ❌ "CUDA out of memory"
**Çözüm 1:** Batch size'ı azalt
```python
per_device_train_batch_size=1  # Zaten 1, daha azaltılamaz
```

**Çözüm 2:** Gradient accumulation artır
```python
gradient_accumulation_steps=32  # 16 → 32
```

**Çözüm 3:** LoRA rank azalt
```python
r=32  # 64 → 32 (daha az parametre)
```

### ❌ "Out of memory (RAM)"
128GB RAM'iniz olduğu için bu sorun yaşanmamalı. Ama olursa:
- Diğer programları kapatın
- Windows sanal belleği artırın (pagefile)

### ❌ Eğitim çok yavaş
**Normal hız:** ~1-2 dakika/step (gradient accumulation=16)

**Hızlandırma:**
- `dataloader_num_workers=4` (2 → 4)
- `gradient_accumulation_steps=8` (16 → 8, ama kalite düşer)

### ❌ Loss düşmüyor
- Learning rate artır: `2e-4` → `5e-4`
- Epoch artır: `5` → `10+`
- Dataset kalitesini kontrol et

## 📈 Performans İyileştirme

### Daha Kaliteli Eğitim
```python
num_train_epochs=20                    # 5 → 20
learning_rate=1e-4                     # 2e-4 → 1e-4 (daha stabil)
lora_r=128                             # 64 → 128 (daha fazla parametre)
```

### Daha Hızlı Eğitim
```python
num_train_epochs=3                     # 5 → 3
gradient_accumulation_steps=8          # 16 → 8
lora_r=32                              # 64 → 32
```

## 💾 Model Kaydetme ve Yükleme

### Kaydetme (Otomatik)
Script otomatik kaydediyor:
- `./missflora-qwen-final-YYYYMMDD_HHMMSS/` klasörüne

### Yükleme
```python
from peft import AutoPeftModelForCausalLM
model = AutoPeftModelForCausalLM.from_pretrained("./missflora-qwen-final-YYYYMMDD_HHMMSS")
```

## 🎓 Eğitim Parametreleri Açıklaması

| Parametre | Değer | Açıklama |
|-----------|-------|----------|
| `num_train_epochs` | 5 | Kaç kez tüm dataset üzerinden geçilecek |
| `per_device_train_batch_size` | 1 | Her adımda kaç örnek (VRAM sınırı) |
| `gradient_accumulation_steps` | 16 | Virtual batch = 1×16 = 16 |
| `learning_rate` | 2e-4 | Öğrenme hızı (QLoRA için yüksek) |
| `lora_r` | 64 | LoRA rank (yüksek = kaliteli ama yavaş) |
| `lora_alpha` | 128 | LoRA alpha (genelde r×2) |

## 📞 Destek

Sorun yaşarsanız:
1. `training_loss.png` grafiğini kontrol edin
2. `logs/` klasöründeki logları inceleyin
3. GitHub Issues açın veya help@missflora.net

## 🎉 Başarı Kriterleri

✅ Loss 2.0'ın altına düştü
✅ Test sorulara doğru cevap veriyor
✅ Türkçe dilbilgisi doğru
✅ MissFlora markasını doğru tanıyor

**Şimdi eğitime başlayabilirsiniz! 🚀**
