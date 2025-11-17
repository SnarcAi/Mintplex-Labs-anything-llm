#!/usr/bin/env python3
"""
MORİ Fine-Tuning Script - RTX 5080 Optimize
2-9 yaş çocuklar için Türkçe konuşma modeli
NIRVANA Projesi - Lavanta-mor ayı MORİ

Sistem Gereksinimleri:
- GPU: NVIDIA RTX 5080 16GB (veya benzer)
- RAM: 128GB DDR5
- Python: 3.13.7
- Windows 11 Pro
"""

import os
import json
import torch
import warnings
from pathlib import Path
from dataclasses import dataclass, field
from typing import Optional, List
from transformers import (
    AutoTokenizer,
    AutoModelForCausalLM,
    TrainingArguments,
    Trainer,
    DataCollatorForLanguageModeling,
    TrainerCallback,
)
from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training
from datasets import load_dataset
import argparse
from datetime import datetime

warnings.filterwarnings('ignore')


@dataclass
class MoriTrainingConfig:
    """MORİ Fine-Tuning Konfigürasyonu"""

    # Model seçimi
    base_model_name: str = "google/gemma-2-2b-it"  # Varsayılan: Gemma-2-2B
    # Alternatifler:
    # - "gpt2-medium" (774M params, hızlı ama Türkçe zayıf)
    # - "ytu-ce-cosmos/turkish-gpt2-large" (774M params, Türkçe özel)

    output_dir: str = "./mori-model"

    # Dataset
    dataset_path: str = "./mori_dataset.jsonl"
    max_seq_length: int = 512  # MORİ kısa cevaplar veriyor

    # LoRA - RTX 5080 için optimize
    lora_r: int = 64  # Rank (kalite için yüksek)
    lora_alpha: int = 128  # Alpha (genelde 2*r)
    lora_dropout: float = 0.05
    lora_target_modules: List[str] = field(default_factory=lambda: [
        "q_proj", "k_proj", "v_proj", "o_proj",  # Attention
        "gate_proj", "up_proj", "down_proj"      # MLP (Gemma için)
    ])

    # Training - RTX 5080 16GB için optimal
    num_epochs: int = 5
    batch_size: int = 8  # RTX 5080 16GB için ideal
    gradient_accumulation_steps: int = 4  # Effective batch = 32
    learning_rate: float = 2e-4
    warmup_ratio: float = 0.03  # İlk %3'ü warmup
    max_grad_norm: float = 1.0
    weight_decay: float = 0.01

    # Optimization
    bf16: bool = True  # RTX 5080 Tensor Core için BF16
    fp16: bool = False  # BF16 kullanıyorsak FP16 kapalı
    gradient_checkpointing: bool = True  # Bellek tasarrufu
    optim: str = "adamw_torch"  # Optimizer
    lr_scheduler_type: str = "cosine"  # Learning rate scheduler

    # Logging & Saving
    logging_steps: int = 10
    save_steps: int = 500
    save_total_limit: int = 3
    evaluation_strategy: str = "no"  # Sadece training

    # Seed for reproducibility
    seed: int = 42


class MoriTrainer:
    """MORİ model eğitim sınıfı"""

    def __init__(self, config: MoriTrainingConfig):
        self.config = config
        self.tokenizer = None
        self.model = None
        self.device = "cuda" if torch.cuda.is_available() else "cpu"

        # GPU kontrolü
        self._check_gpu()

    def _check_gpu(self):
        """GPU kontrolü ve bilgi"""
        print("\n" + "="*60)
        print("🐻 MORİ FINE-TUNING - RTX 5080 OPTIMIZE")
        print("="*60)
        print(f"Device: {self.device}")

        if self.device == "cuda":
            gpu_name = torch.cuda.get_device_name(0)
            vram_total = torch.cuda.get_device_properties(0).total_memory / 1024**3
            print(f"GPU: {gpu_name}")
            print(f"VRAM: {vram_total:.1f} GB")
            print(f"CUDA: {torch.version.cuda}")
            print(f"PyTorch: {torch.__version__}")

            # RTX 5080 kontrolü
            if "5080" in gpu_name:
                print("✅ RTX 5080 tespit edildi - Optimal ayarlar aktif!")
            elif vram_total < 12:
                print("⚠️  VRAM 12GB'dan az - Batch size düşürülmeli!")
                self.config.batch_size = 4
        else:
            print("❌ GPU bulunamadı! CPU ile eğitim çok yavaş olacak!")
            raise RuntimeError("GPU gerekli! CUDA kurulumunu kontrol edin.")

        print("="*60 + "\n")

    def load_model_and_tokenizer(self):
        """Model ve tokenizer yükle"""
        print(f"📦 Model yükleniyor: {self.config.base_model_name}")

        # Tokenizer
        self.tokenizer = AutoTokenizer.from_pretrained(
            self.config.base_model_name,
            trust_remote_code=True,
            use_fast=True,
        )

        # Padding token ayarla
        if self.tokenizer.pad_token is None:
            if self.tokenizer.eos_token:
                self.tokenizer.pad_token = self.tokenizer.eos_token
            else:
                self.tokenizer.add_special_tokens({'pad_token': '[PAD]'})

        print(f"✓ Tokenizer yüklendi")
        print(f"  Vocab size: {len(self.tokenizer):,}")
        print(f"  Pad token: {self.tokenizer.pad_token}")

        # Model
        print(f"\n📦 Base model yükleniyor...")
        self.model = AutoModelForCausalLM.from_pretrained(
            self.config.base_model_name,
            device_map="auto",
            torch_dtype=torch.bfloat16 if self.config.bf16 else torch.float16,
            trust_remote_code=True,
        )

        # Token embedding resize (eğer pad token eklenmiş)
        if len(self.tokenizer) > self.model.config.vocab_size:
            self.model.resize_token_embeddings(len(self.tokenizer))

        print(f"✓ Model yüklendi")
        total_params = sum(p.numel() for p in self.model.parameters())
        print(f"  Parametreler: {total_params / 1e9:.2f}B")
        print(f"  Model tipi: {self.model.dtype}")

        # Gradient checkpointing
        if self.config.gradient_checkpointing:
            self.model.gradient_checkpointing_enable()
            self.model.enable_input_require_grads()
            print(f"✓ Gradient checkpointing aktif")

    def setup_lora(self):
        """LoRA adapterleri ekle"""
        print(f"\n🔧 LoRA ayarlanıyor...")
        print(f"  Rank (r): {self.config.lora_r}")
        print(f"  Alpha: {self.config.lora_alpha}")
        print(f"  Dropout: {self.config.lora_dropout}")
        print(f"  Target modules: {', '.join(self.config.lora_target_modules)}")

        lora_config = LoraConfig(
            r=self.config.lora_r,
            lora_alpha=self.config.lora_alpha,
            target_modules=self.config.lora_target_modules,
            lora_dropout=self.config.lora_dropout,
            bias="none",
            task_type="CAUSAL_LM"
        )

        self.model = get_peft_model(self.model, lora_config)

        # Trainable parametreler
        trainable = sum(p.numel() for p in self.model.parameters() if p.requires_grad)
        total = sum(p.numel() for p in self.model.parameters())

        print(f"✓ LoRA aktif")
        print(f"  Trainable parametreler: {trainable / 1e6:.2f}M ({100 * trainable / total:.2f}%)")
        print(f"  VRAM tasarrufu: ~{(total - trainable) * 2 / 1024**3:.1f} GB")

    def prepare_dataset(self):
        """Veri setini hazırla ve tokenize et"""
        print(f"\n📚 Dataset yükleniyor: {self.config.dataset_path}")

        if not Path(self.config.dataset_path).exists():
            raise FileNotFoundError(
                f"❌ Dataset bulunamadı: {self.config.dataset_path}\n"
                f"Önce veri oluşturun: python generate_mori_dataset.py"
            )

        # JSONL dosyasını yükle
        dataset = load_dataset('json', data_files=self.config.dataset_path, split='train')

        print(f"✓ Dataset yüklendi: {len(dataset):,} örnek")

        # Örnek göster
        print(f"\n🎯 Dataset Örneği:")
        sample = dataset[0]
        print(f"  Instruction: {sample['instruction'][:100]}...")
        print(f"  Input: {sample['input']}")
        print(f"  Output: {sample['output'][:100]}...")

        # Tokenization fonksiyonu
        def tokenize_function(examples):
            """Her örneği tokenize et"""
            conversations = []

            for instruction, input_text, output in zip(
                examples['instruction'],
                examples['input'],
                examples['output']
            ):
                # Gemma chat formatı
                if "gemma" in self.config.base_model_name.lower():
                    messages = [
                        {"role": "user", "content": f"{instruction}\n\n{input_text}"},
                        {"role": "assistant", "content": output}
                    ]

                    # Chat template uygula
                    try:
                        text = self.tokenizer.apply_chat_template(
                            messages,
                            tokenize=False,
                            add_generation_prompt=False
                        )
                    except:
                        # Fallback: manuel format
                        text = f"<bos><start_of_turn>user\n{instruction}\n\n{input_text}<end_of_turn>\n<start_of_turn>model\n{output}<end_of_turn><eos>"

                else:  # GPT2 formatı
                    text = f"### Instruction: {instruction}\n\n### Input: {input_text}\n\n### Response: {output}{self.tokenizer.eos_token}"

                conversations.append(text)

            # Tokenize
            tokenized = self.tokenizer(
                conversations,
                truncation=True,
                max_length=self.config.max_seq_length,
                padding=False,  # Dynamic padding ile batch'te padding yapılacak
                return_tensors=None
            )

            # Labels = input_ids (causal LM için)
            tokenized["labels"] = tokenized["input_ids"].copy()

            return tokenized

        print(f"\n🔄 Tokenization yapılıyor...")
        tokenized_dataset = dataset.map(
            tokenize_function,
            batched=True,
            remove_columns=dataset.column_names,
            desc="Tokenizing",
            num_proc=4  # Paralel işlem (Windows'da dikkatli kullanın)
        )

        print(f"✓ Tokenization tamamlandı")
        print(f"  Toplam örnek: {len(tokenized_dataset):,}")

        # Token istatistikleri
        token_lengths = [len(x) for x in tokenized_dataset['input_ids']]
        print(f"  Ortalama token: {sum(token_lengths) / len(token_lengths):.0f}")
        print(f"  Max token: {max(token_lengths)}")
        print(f"  Min token: {min(token_lengths)}")

        return tokenized_dataset

    def train(self, dataset):
        """Model eğitimi"""
        print(f"\n" + "="*60)
        print("🎓 TRAINING BAŞLIYOR")
        print("="*60)
        print(f"Epochs: {self.config.num_epochs}")
        print(f"Batch size: {self.config.batch_size}")
        print(f"Gradient accumulation: {self.config.gradient_accumulation_steps}")
        print(f"Effective batch size: {self.config.batch_size * self.config.gradient_accumulation_steps}")
        print(f"Learning rate: {self.config.learning_rate}")
        print(f"Warmup ratio: {self.config.warmup_ratio}")
        print(f"LR scheduler: {self.config.lr_scheduler_type}")
        print(f"Precision: {'BF16' if self.config.bf16 else 'FP16'}")
        print(f"Gradient checkpointing: {self.config.gradient_checkpointing}")
        print("="*60 + "\n")

        # Training arguments
        training_args = TrainingArguments(
            output_dir=self.config.output_dir,
            num_train_epochs=self.config.num_epochs,
            per_device_train_batch_size=self.config.batch_size,
            gradient_accumulation_steps=self.config.gradient_accumulation_steps,
            learning_rate=self.config.learning_rate,
            warmup_ratio=self.config.warmup_ratio,
            max_grad_norm=self.config.max_grad_norm,
            weight_decay=self.config.weight_decay,
            logging_steps=self.config.logging_steps,
            save_steps=self.config.save_steps,
            save_total_limit=self.config.save_total_limit,
            evaluation_strategy=self.config.evaluation_strategy,
            fp16=self.config.fp16,
            bf16=self.config.bf16,
            optim=self.config.optim,
            lr_scheduler_type=self.config.lr_scheduler_type,
            gradient_checkpointing=self.config.gradient_checkpointing,
            logging_dir=f"{self.config.output_dir}/logs",
            report_to="tensorboard",  # TensorBoard logging
            seed=self.config.seed,
            dataloader_num_workers=0,  # Windows için 0 önerilir
            remove_unused_columns=False,
            load_best_model_at_end=False,
        )

        # Data collator - dynamic padding
        data_collator = DataCollatorForLanguageModeling(
            tokenizer=self.tokenizer,
            mlm=False  # Causal LM
        )

        # Trainer
        trainer = Trainer(
            model=self.model,
            args=training_args,
            train_dataset=dataset,
            data_collator=data_collator,
        )

        # Training başlat
        start_time = datetime.now()
        print(f"⏰ Başlangıç: {start_time.strftime('%Y-%m-%d %H:%M:%S')}\n")

        try:
            trainer.train()
            print(f"\n✅ Training tamamlandı!")
        except KeyboardInterrupt:
            print(f"\n⚠️  Training kullanıcı tarafından durduruldu!")
        except Exception as e:
            print(f"\n❌ Training hatası: {e}")
            raise

        end_time = datetime.now()
        duration = end_time - start_time
        print(f"⏰ Bitiş: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"⏱️  Toplam süre: {duration}")

        # Model kaydet
        print(f"\n💾 Model kaydediliyor: {self.config.output_dir}")
        trainer.save_model(self.config.output_dir)
        self.tokenizer.save_pretrained(self.config.output_dir)

        # LoRA adapters ayrı kaydet
        lora_path = Path(self.config.output_dir) / "lora_adapters"
        self.model.save_pretrained(lora_path)

        print(f"✓ Model kaydedildi")
        print(f"  Base + LoRA: {self.config.output_dir}")
        print(f"  Sadece LoRA: {lora_path}")

        # Disk kullanımı
        total_size = sum(
            f.stat().st_size for f in Path(self.config.output_dir).rglob('*') if f.is_file()
        )
        print(f"  Toplam boyut: {total_size / 1024**3:.2f} GB")

    def run(self):
        """Tam training pipeline"""
        self.load_model_and_tokenizer()
        self.setup_lora()
        dataset = self.prepare_dataset()
        self.train(dataset)

        print("\n" + "="*60)
        print("🎉 MORİ FINE-TUNING TAMAMLANDI!")
        print("="*60)
        print(f"\nModel kullanımı:")
        print(f"  python test_mori.py --model {self.config.output_dir}")
        print(f"\nModel yolu: {Path(self.config.output_dir).absolute()}")
        print("="*60 + "\n")


def main():
    """Ana fonksiyon"""
    parser = argparse.ArgumentParser(
        description="MORİ Fine-Tuning - RTX 5080 Optimize",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Kullanım Örnekleri:
  # Varsayılan ayarlarla (Gemma-2-2B, 5 epoch, 20K veri)
  python train_mori_rtx5080.py

  # Özel dataset ile
  python train_mori_rtx5080.py --dataset my_dataset.jsonl

  # GPT2-medium ile
  python train_mori_rtx5080.py --model gpt2-medium --epochs 10

  # Daha yüksek kalite için (daha uzun sürer)
  python train_mori_rtx5080.py --lora-r 128 --epochs 10
        """
    )

    parser.add_argument('--model', type=str, default='google/gemma-2-2b-it',
                        help='Base model (default: google/gemma-2-2b-it)')
    parser.add_argument('--dataset', type=str, default='mori_dataset.jsonl',
                        help='Training dataset path')
    parser.add_argument('--output', type=str, default='./mori-model',
                        help='Output directory')
    parser.add_argument('--epochs', type=int, default=5,
                        help='Training epochs (default: 5)')
    parser.add_argument('--batch-size', type=int, default=8,
                        help='Batch size (default: 8 for RTX 5080)')
    parser.add_argument('--lora-r', type=int, default=64,
                        help='LoRA rank (default: 64)')
    parser.add_argument('--lr', type=float, default=2e-4,
                        help='Learning rate (default: 2e-4)')
    parser.add_argument('--max-length', type=int, default=512,
                        help='Max sequence length (default: 512)')

    args = parser.parse_args()

    # Config oluştur
    config = MoriTrainingConfig(
        base_model_name=args.model,
        dataset_path=args.dataset,
        output_dir=args.output,
        num_epochs=args.epochs,
        batch_size=args.batch_size,
        lora_r=args.lora_r,
        learning_rate=args.lr,
        max_seq_length=args.max_length,
    )

    # Trainer oluştur ve çalıştır
    trainer = MoriTrainer(config)
    trainer.run()


if __name__ == "__main__":
    main()
