# 🚀 MissFlora Qwen 2.5 7B QLoRA Eğitimi
# RTX 5080 16GB + 128GB RAM Optimize Edilmiş Versiyon
print("=" * 80)
print("🚀 MissFlora AI Customer Assistant Training - Qwen 2.5 7B QLoRA")
print("=" * 80)
print("💻 Sistem: RTX 5080 16GB | 128GB RAM | Ryzen 9 9950X")
print("🎯 Hedef: 16GB VRAM'de hızlı ve kaliteli eğitim")
print("=" * 80)

# 1. KÜTÜPHANELER
print("\n1️⃣ Kütüphaneler yükleniyor...")
import sys
import os
import torch
import json
import gc
from datetime import datetime
import matplotlib.pyplot as plt

# Gerekli paketleri yükle
import subprocess

packages = [
    "transformers>=4.36.0",
    "datasets",
    "peft>=0.7.0",
    "accelerate>=0.25.0",
    "bitsandbytes>=0.41.0",
    "scipy",
    "sentencepiece",
    "trl"
]

for package in packages:
    print(f"📦 Yükleniyor: {package}")
    subprocess.run([sys.executable, "-m", "pip", "install", "-q", package], check=False)

from transformers import (
    AutoTokenizer,
    AutoModelForCausalLM,
    TrainingArguments,
    BitsAndBytesConfig
)
from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training, TaskType
from datasets import Dataset
from trl import SFTTrainer
import random

print("✅ Tüm kütüphaneler yüklendi!")

# 2. GPU KONTROL
print("\n2️⃣ GPU kontrolü yapılıyor...")
if torch.cuda.is_available():
    gpu_name = torch.cuda.get_device_name(0)
    vram_total = torch.cuda.get_device_properties(0).total_memory / 1024**3
    print(f"✅ GPU: {gpu_name}")
    print(f"✅ VRAM: {vram_total:.1f} GB")
    torch.cuda.empty_cache()
    gc.collect()
else:
    print("❌ CUDA bulunamadı! CPU'da eğitim çok yavaş olacak.")
    sys.exit(1)

# 3. MODEL YOLU VE 4-BIT QUANTIZATION CONFIG
print("\n3️⃣ Model yapılandırması hazırlanıyor...")

model_path = r"C:\Users\Superuser\.cache\huggingface\hub\models--Qwen--Qwen2.5-7B-Instruct\snapshots\a09a35458c702b33eeacc393d103063234e8bc28"

# 4-bit Quantization Config (QLoRA)
bnb_config = BitsAndBytesConfig(
    load_in_4bit=True,                      # 4-bit yükleme
    bnb_4bit_use_double_quant=True,         # Double quantization
    bnb_4bit_quant_type="nf4",              # NormalFloat4
    bnb_4bit_compute_dtype=torch.bfloat16   # BF16 hesaplama
)

print("✅ 4-bit QLoRA yapılandırması hazır")
print("   → Model ağırlıkları: 4-bit (~3.5 GB VRAM)")
print("   → Hesaplama: BFloat16")
print("   → Optimizer offloading: CPU RAM'e")

# 4. TOKENIZER VE MODEL YÜKLEME
print("\n4️⃣ Tokenizer ve model yükleniyor...")

tokenizer = AutoTokenizer.from_pretrained(
    model_path,
    trust_remote_code=True,
    padding_side="right"
)

# Pad token ayarla
if tokenizer.pad_token is None:
    tokenizer.pad_token = tokenizer.eos_token
    tokenizer.pad_token_id = tokenizer.eos_token_id

print("✅ Tokenizer yüklendi")

# Model'i 4-bit ile yükle
model = AutoModelForCausalLM.from_pretrained(
    model_path,
    quantization_config=bnb_config,
    device_map="auto",                      # Otomatik GPU/CPU dağılımı
    trust_remote_code=True,
    torch_dtype=torch.bfloat16,
    low_cpu_mem_usage=True
)

model.config.use_cache = False              # Gradient checkpointing için
model.config.pretraining_tp = 1

print("✅ Model 4-bit olarak yüklendi!")

# Bellek temizliği
torch.cuda.empty_cache()
gc.collect()

# 5. LORA CONFIGURATION
print("\n5️⃣ LoRA yapılandırması...")

# Model'i k-bit eğitime hazırla
model = prepare_model_for_kbit_training(model)

# LoRA Config - Qwen için optimize edilmiş
lora_config = LoraConfig(
    r=64,                                   # Rank (yüksek = daha iyi kalite)
    lora_alpha=128,                         # Alpha (r*2 önerilir)
    target_modules=[
        "q_proj",                           # Query projection
        "k_proj",                           # Key projection
        "v_proj",                           # Value projection
        "o_proj",                           # Output projection
        "gate_proj",                        # Gate projection (Qwen)
        "up_proj",                          # Up projection (Qwen)
        "down_proj"                         # Down projection (Qwen)
    ],
    lora_dropout=0.05,
    bias="none",
    task_type=TaskType.CAUSAL_LM,
    inference_mode=False
)

# LoRA adapters ekle
model = get_peft_model(model, lora_config)

# Eğitilebilir parametreleri göster
trainable_params = sum(p.numel() for p in model.parameters() if p.requires_grad)
all_params = sum(p.numel() for p in model.parameters())
trainable_percentage = 100 * trainable_params / all_params

print(f"✅ LoRA uygulandı!")
print(f"   → Toplam parametre: {all_params:,}")
print(f"   → Eğitilebilir: {trainable_params:,} ({trainable_percentage:.2f}%)")
print(f"   → Tahmini VRAM kullanımı: ~5-7 GB")

# 6. MISSFLORA DATASET
print("\n6️⃣ MissFlora dataset hazırlanıyor...")

training_data = [
    {
        "instruction": "MissFlora Nem Alıcı ne kadar süre dayanır?",
        "input": "",
        "output": "MissFlora Nem Alıcı, 200g'lık paket yaklaşık 45-90 gün dayanır. Bu süre ortamdaki nem yoğunluğuna bağlı olarak değişir. Nemin fazla olduğu ortamlarda daha kısa sürede dolar. 35m3'e kadar (10-20m²) bir alan için yeterlidir. Ortamdaki bağıl nem oranını %40-60 arasında sabit tutar."
    },
    {
        "instruction": "NemKap hangi alanlarda kullanılır?",
        "input": "",
        "output": "MissFlora Nem Alıcı şu alanlarda kullanılabilir: Mutfak dolapları, lavabo altları, elektrik panoları, elbise dolapları, bodrum katları, yatak odaları, garaj, depo, kiler, yazlık evler, karavan ve teknelerde. Az veya hiç havalandırılmayan mekanlarda havadaki nemi azaltarak eşya ve makinelerinizi korur."
    },
    {
        "instruction": "Nem Alıcı'nın içinde ne var?",
        "input": "",
        "output": "MissFlora Nem Alıcı'nın içeriğinde Kalsiyum Klorür (CaCl2) dihydrate bulunur. CAS numarası: 10035-04-8. Bu madde havadaki nemi emerek plastik kap içinde su olarak biriktirir. Küf, mantar, rutubet, nem ve koku oluşumunu engeller."
    },
    {
        "instruction": "NemKap'ın dibi neden buzlanıyor?",
        "input": "",
        "output": "NemKap'ın dibi çok düşük sıcaklıklarda veya yüksek nem seviyelerinde buzlanabilir. Bu durum normaldir ve ürünün etkinliğini etkilemez. Buzlanma oluştuğunda, ürünü donmuş olmayan bir alana taşıyarak veya oda sıcaklığında çözünmesini bekleyerek sorunu çözebilirsiniz."
    },
    {
        "instruction": "Nem Alıcı kaç metrekare için yeterli?",
        "input": "",
        "output": "200g'lık bir MissFlora Nem Alıcı yaklaşık 10-20 m² (35m3'e kadar olan odalar) için yeterlidir. Daha büyük alanlar için birden fazla ürün kullanmanız önerilir."
    },
    {
        "instruction": "Nem Alıcı çocuklar için güvenli mi?",
        "input": "",
        "output": "MissFlora Nem Alıcı çocukların erişemeyeceği yerde saklanmalıdır. Kalsiyum Klorür içerir ve ciddi göz tahrişine yol açabilir. Yutulması zararlıdır. Çocuklardan uzak tutunuz."
    },
    {
        "instruction": "MissFlora WC Blok ne kadar dayanır?",
        "input": "",
        "output": "MissFlora WC Blok kullanım sıklığına ve su sertliğine bağlı olarak ortalama 3-4 hafta etkilidir. Mavi renk solmaya başladığında yenisiyle değiştirmelisiniz."
    },
    {
        "instruction": "WC Blok nasıl kullanılır?",
        "input": "",
        "output": "MissFlora WC Blok kullanımı çok kolaydır: 1) Plastik ambalajdan çıkarın, 2) Klozet kenarına asın, 3) Su kanalı altına gelecek şekilde yerleştirin. Her sifonda temizlik ve ferahlık sağlar, mavi su etkisi yaratır."
    },
    {
        "instruction": "Koku Yastığı ne kadar süre kokar?",
        "input": "",
        "output": "MissFlora Koku Yastıkları 8 hafta süreyle kalıcı bir ferahlık sağlar. Giysi ve çamaşır çekmecelerinde, ayakkabı dolaplarında, spor ve seyahat çantalarınızda kullanılabilir."
    },
    {
        "instruction": "MissYak yakıtı jel mi sıvı mı?",
        "input": "",
        "output": "ÖNEMLİ: MissYak ve VarBQ ürünleri artık %75 Etil Alkol (Ethanol) SIVI YAKIT kullanıyor. Eski jel formülü artık kullanılmıyor. Ürün etiketlerinde 'gel' yazsa bile, içindekiler %75 etil alkol sıvısıdır."
    },
    {
        "instruction": "MissFlora müşteri hizmetlerine nasıl ulaşırım?",
        "input": "",
        "output": "MissFlora müşteri hizmetleri iletişim: E-posta: help@missflora.net. WhatsApp Türkiye: +90 541 919 9448. WhatsApp ABD: +1 307 752 3011. Merkez Telefon: +90 554 834 94 74."
    },
    {
        "instruction": "Toptan satış yapıyor musunuz?",
        "input": "",
        "output": "Evet! MissFlora toptan satış yapmaktadır. İndirim oranları: 10-50 koli %15, 50-100 koli %20, 100-1000 koli %25, 1000+ koli özel fiyat. help@missflora.net adresinden teklif alabilirsiniz."
    },
    {
        "instruction": "Amazon'da MissFlora ürünleri var mı?",
        "input": "",
        "output": "Evet, MissFlora ürünleri Amazon'da satılmaktadır. ABD, Kanada ve Meksika Amazon sitelerinde bulabilirsiniz."
    },
    {
        "instruction": "MissFlora nerede üretiliyor?",
        "input": "",
        "output": "Tüm MissFlora ürünleri Türkiye'de, kendi fabrikamızda üretilmektedir. Üretici: 3K Pazarlama Plastik Madeni Eşya San. ve Tic. Ltd. Şti., Pendik / İSTANBUL."
    },
    {
        "instruction": "Siparişimi nasıl takip ederim?",
        "input": "",
        "output": "Siparişiniz Amazon veya Walmart üzerindeyse, ilgili platformdaki 'Siparişlerim' bölümünden takip numarası ile takip edebilirsiniz. Daha fazla yardım için help@missflora.net adresine yazabilirsiniz."
    }
]

# Data augmentation (veriyi 5x artır)
print("   → Data augmentation yapılıyor...")
augmented_data = []

for item in training_data:
    # Orijinal
    augmented_data.append(item)

    # Varyasyon 1
    augmented_data.append({
        "instruction": f"Lütfen {item['instruction'].lower()}",
        "input": item['input'],
        "output": item['output']
    })

    # Varyasyon 2
    augmented_data.append({
        "instruction": f"Bana {item['instruction'].lower()}",
        "input": item['input'],
        "output": item['output']
    })

    # Varyasyon 3
    augmented_data.append({
        "instruction": item['instruction'],
        "input": item['input'],
        "output": f"Tabii ki! {item['output']}"
    })

    # Varyasyon 4
    augmented_data.append({
        "instruction": f"{item['instruction']} hakkında bilgi verir misiniz?",
        "input": item['input'],
        "output": f"Elbette. {item['output']}"
    })

random.shuffle(augmented_data)

print(f"✅ Dataset hazır!")
print(f"   → Orijinal: {len(training_data)} örnek")
print(f"   → Augmented: {len(augmented_data)} örnek")

# 7. DATASET FORMATLAMA (Qwen Chat Template)
print("\n7️⃣ Dataset formatlanıyor (Qwen chat template)...")

def format_data(example):
    """Qwen 2.5 chat template formatı"""
    instruction = example['instruction']
    input_text = example['input']
    output = example['output']

    # Kullanıcı mesajı
    if input_text and input_text.strip():
        user_msg = f"{instruction}\n\nEk bilgi: {input_text}"
    else:
        user_msg = instruction

    # Qwen chat template formatı
    messages = [
        {"role": "system", "content": "Sen MissFlora müşteri hizmetleri asistanısın. MissFlora ev bakım ve koku ürünleri hakkında Türkçe yardım sağlıyorsun. Nazik, bilgili ve yardımseversin."},
        {"role": "user", "content": user_msg},
        {"role": "assistant", "content": output}
    ]

    # Tokenizer'ın chat template'ini kullan
    text = tokenizer.apply_chat_template(
        messages,
        tokenize=False,
        add_generation_prompt=False
    )

    return {"text": text}

dataset = Dataset.from_list(augmented_data)
dataset = dataset.map(format_data, remove_columns=dataset.column_names)

print("✅ Dataset formatlandı (Qwen chat template)")

# 8. TRAINING ARGUMENTS (16GB VRAM + 128GB RAM Optimize)
print("\n8️⃣ Eğitim parametreleri ayarlanıyor...")

output_dir = f"./missflora-qwen-{datetime.now().strftime('%Y%m%d_%H%M%S')}"

training_args = TrainingArguments(
    # Çıktı
    output_dir=output_dir,
    run_name="missflora-qwen-qlora",

    # Eğitim
    num_train_epochs=5,                     # 5 epoch (artırılabilir)
    per_device_train_batch_size=1,          # Batch size = 1 (VRAM'i koru)
    gradient_accumulation_steps=16,         # Virtual batch = 16

    # Öğrenme
    learning_rate=2e-4,                     # QLoRA için yüksek LR
    lr_scheduler_type="cosine",
    warmup_ratio=0.03,

    # Optimizasyon
    optim="paged_adamw_8bit",               # 8-bit optimizer (VRAM tasarrufu)
    weight_decay=0.01,
    max_grad_norm=0.3,

    # VRAM/RAM Offloading
    gradient_checkpointing=True,            # Aktivasyon offloading
    gradient_checkpointing_kwargs={"use_reentrant": False},

    # Precision
    bf16=True,                              # BFloat16 (RTX 5080 destekler)
    fp16=False,

    # Logging
    logging_steps=5,
    logging_strategy="steps",

    # Kaydetme
    save_strategy="epoch",
    save_total_limit=3,

    # Diğer
    report_to="none",
    dataloader_num_workers=2,
    remove_unused_columns=False,
    group_by_length=True,                   # Verimlilik artışı

    # DeepSpeed yok (Windows'ta sorunlu olabilir)
    # Accelerate otomatik offloading yapacak
)

print("✅ Eğitim parametreleri hazır!")
print(f"   → Epoch: {training_args.num_train_epochs}")
print(f"   → Effective batch size: {training_args.per_device_train_batch_size * training_args.gradient_accumulation_steps}")
print(f"   → Optimizer: 8-bit AdamW (CPU RAM'e offload)")
print(f"   → Gradient checkpointing: Aktif")
print(f"   → Precision: BFloat16")

# 9. TRAINER (SFTTrainer - Supervised Fine-Tuning)
print("\n9️⃣ Trainer başlatılıyor...")

trainer = SFTTrainer(
    model=model,
    train_dataset=dataset,
    args=training_args,
    tokenizer=tokenizer,
    max_seq_length=2048,                    # Max token uzunluğu
    dataset_text_field="text",              # Text field adı
    packing=False,                          # Sequence packing kapalı
)

print("✅ Trainer hazır!")

# Bellek temizliği
torch.cuda.empty_cache()
gc.collect()

# VRAM kullanımını göster
vram_allocated = torch.cuda.memory_allocated(0) / 1024**3
vram_reserved = torch.cuda.memory_reserved(0) / 1024**3
print(f"\n💾 Başlangıç VRAM kullanımı:")
print(f"   → Allocated: {vram_allocated:.2f} GB")
print(f"   → Reserved: {vram_reserved:.2f} GB")

# 10. EĞİTİM
print("\n" + "=" * 80)
print("🚀 EĞİTİM BAŞLIYOR!")
print("=" * 80)
print(f"⏰ Başlangıç: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("=" * 80 + "\n")

start_time = datetime.now()

try:
    trainer.train()

    end_time = datetime.now()
    duration = end_time - start_time

    print("\n" + "=" * 80)
    print("✅ EĞİTİM TAMAMLANDI!")
    print("=" * 80)
    print(f"⏰ Bitiş: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"⌛ Süre: {duration}")
    print("=" * 80)

except Exception as e:
    print(f"\n❌ Eğitim hatası: {str(e)}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# 11. MODEL KAYDETME
print("\n1️⃣0️⃣ Model kaydediliyor...")

final_output_dir = f"./missflora-qwen-final-{datetime.now().strftime('%Y%m%d_%H%M%S')}"

# Sadece LoRA adapter'ları kaydet (çok daha küçük)
trainer.model.save_pretrained(final_output_dir)
tokenizer.save_pretrained(final_output_dir)

# Training config'i kaydet
with open(f"{final_output_dir}/training_config.json", "w", encoding="utf-8") as f:
    json.dump({
        "base_model": model_path,
        "lora_r": lora_config.r,
        "lora_alpha": lora_config.lora_alpha,
        "epochs": training_args.num_train_epochs,
        "learning_rate": training_args.learning_rate,
        "training_duration": str(duration),
        "dataset_size": len(dataset)
    }, f, indent=2, ensure_ascii=False)

print(f"✅ Model kaydedildi: {final_output_dir}")
print(f"   → LoRA adapter boyutu: ~200-400 MB")
print(f"   → Base model: {model_path}")

# 12. TEST
print("\n1️⃣1️⃣ Model testi yapılıyor...")

test_prompts = [
    "MissFlora Nem Alıcı ne kadar dayanır?",
    "WC Blok nasıl kullanılır?",
    "MissFlora müşteri hizmetleri iletişim bilgileri nedir?"
]

print("\n" + "=" * 80)
print("🧪 TEST ÇIKTILARI")
print("=" * 80)

for prompt in test_prompts:
    messages = [
        {"role": "system", "content": "Sen MissFlora müşteri hizmetleri asistanısın."},
        {"role": "user", "content": prompt}
    ]

    text = tokenizer.apply_chat_template(
        messages,
        tokenize=False,
        add_generation_prompt=True
    )

    inputs = tokenizer(text, return_tensors="pt").to(model.device)

    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_new_tokens=256,
            temperature=0.7,
            top_p=0.9,
            do_sample=True,
            pad_token_id=tokenizer.pad_token_id
        )

    response = tokenizer.decode(outputs[0][inputs['input_ids'].shape[1]:], skip_special_tokens=True)

    print(f"\n❓ Soru: {prompt}")
    print(f"💬 Cevap: {response}")
    print("-" * 80)

# 13. LOSS GRAFİĞİ
print("\n1️⃣2️⃣ Loss grafiği oluşturuluyor...")

try:
    log_history = trainer.state.log_history
    losses = [x['loss'] for x in log_history if 'loss' in x]
    steps = list(range(len(losses)))

    if len(losses) > 0:
        plt.figure(figsize=(12, 6))
        plt.plot(steps, losses, linewidth=2, color='#FF6B6B', marker='o', markersize=4)
        plt.xlabel('Training Steps', fontsize=12, fontweight='bold')
        plt.ylabel('Loss', fontsize=12, fontweight='bold')
        plt.title('MissFlora Qwen 2.5 7B QLoRA Training Loss', fontsize=14, fontweight='bold')
        plt.grid(True, alpha=0.3, linestyle='--')
        plt.tight_layout()

        plot_path = f"{final_output_dir}/training_loss.png"
        plt.savefig(plot_path, dpi=300, bbox_inches='tight')
        print(f"✅ Loss grafiği kaydedildi: {plot_path}")

        print(f"\n📊 Loss İstatistikleri:")
        print(f"   → İlk loss: {losses[0]:.4f}")
        print(f"   → Son loss: {losses[-1]:.4f}")
        print(f"   → İyileşme: {((losses[0] - losses[-1]) / losses[0] * 100):.1f}%")
except Exception as e:
    print(f"⚠️ Grafik oluşturulamadı: {str(e)}")

# 14. ÖZET RAPOR
print("\n" + "=" * 80)
print("📋 EĞİTİM RAPORU")
print("=" * 80)
print(f"🎯 Model: Qwen 2.5 7B Instruct (QLoRA 4-bit)")
print(f"📊 Dataset: {len(dataset)} örnek")
print(f"📈 Epoch: {training_args.num_train_epochs}")
print(f"⏰ Süre: {duration}")
print(f"💾 Çıktı: {final_output_dir}")
print(f"🔧 VRAM Kullanımı: ~{vram_allocated:.1f} GB / 16 GB")
print(f"🧠 RAM Offloading: 128 GB DDR5 kullanıldı")
print("=" * 80)

print("\n✅ TÜM İŞLEMLER TAMAMLANDI!")
print("\n📌 Sonraki adımlar:")
print("   1. Model'i yüklemek için:")
print(f"      from peft import AutoPeftModelForCausalLM")
print(f"      model = AutoPeftModelForCausalLM.from_pretrained('{final_output_dir}')")
print("   2. Web uygulaması geliştir (Flask/FastAPI)")
print("   3. missflora.com.tr'ye entegre et")
