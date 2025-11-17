#!/usr/bin/env python3
"""
SnarcAI Fine-Tuning Script
Qwen 2.5 7B için LoRA ile SnarcAI fine-tuning
RTX 5080 16GB için optimize edilmiş
"""

import os
import json
import torch
from pathlib import Path
from dataclasses import dataclass, field
from typing import Optional
from transformers import (
    AutoTokenizer,
    AutoModelForCausalLM,
    TrainingArguments,
    Trainer,
    DataCollatorForSeq2Seq
)
from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training
from datasets import load_dataset
import argparse


@dataclass
class SnarcAIConfig:
    """SnarcAI Fine-tuning konfigürasyonu"""
    # Model
    base_model_path: str = r"C:\Users\Superuser\.cache\huggingface\hub\models--Qwen--Qwen2.5-7B-Instruct\snapshots\a09a35458c702b33eeacc393d103063234e8bc28"
    output_dir: str = "./snarcai-qwen-2.5-7b"

    # Dataset
    dataset_path: str = "./snarcai_training_dataset.jsonl"
    max_seq_length: int = 2048

    # LoRA - RTX 5080 için optimize
    lora_r: int = 64  # Rank - daha yüksek = daha iyi öğrenme
    lora_alpha: int = 128  # 2x rank
    lora_dropout: float = 0.05
    lora_target_modules: list = field(default_factory=lambda: [
        "q_proj", "k_proj", "v_proj", "o_proj",
        "gate_proj", "up_proj", "down_proj"  # MLP layers da ekle
    ])

    # Training - SnarcAI için optimize
    num_epochs: int = 5  # Daha fazla epoch, daha iyi öğrenme
    batch_size: int = 2  # RTX 5080 16GB için güvenli
    gradient_accumulation_steps: int = 8  # Effective batch = 16
    learning_rate: float = 1e-4  # Daha düşük LR, daha stabil
    warmup_ratio: float = 0.1  # İlk %10'da warmup
    max_grad_norm: float = 1.0  # Gradient clipping
    save_steps: int = 50
    logging_steps: int = 5

    # Optimization - RTX 5080
    fp16: bool = False
    bf16: bool = True  # RTX 5080 için bf16 ideal
    gradient_checkpointing: bool = True
    optim: str = "adamw_torch"

    # Evaluation
    eval_steps: int = 50
    save_total_limit: int = 3


class SnarcAIFineTuner:
    def __init__(self, config: SnarcAIConfig):
        self.config = config
        self.tokenizer = None
        self.model = None
        self.device = "cuda" if torch.cuda.is_available() else "cpu"

        print("=" * 70)
        print("🚀 SnarcAI Fine-Tuning")
        print("=" * 70)
        print(f"Device: {self.device}")
        if self.device == "cuda":
            print(f"GPU: {torch.cuda.get_device_name(0)}")
            print(f"VRAM: {torch.cuda.get_device_properties(0).total_memory / 1024**3:.1f} GB")
        print(f"Model: Qwen 2.5 7B Instruct")
        print(f"Dataset: {config.dataset_path}")
        print("=" * 70)

    def load_model(self):
        """Model ve tokenizer yükle"""
        print(f"\n📦 Model yükleniyor...")
        print(f"   Path: {self.config.base_model_path}")

        # Tokenizer
        self.tokenizer = AutoTokenizer.from_pretrained(
            self.config.base_model_path,
            trust_remote_code=True,
            padding_side="right",  # Training için sağdan padding
            use_fast=True
        )

        # Pad token ayarla
        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token
            self.tokenizer.pad_token_id = self.tokenizer.eos_token_id

        print(f"   ✓ Tokenizer yüklendi")
        print(f"     Vocab size: {len(self.tokenizer)}")
        print(f"     Pad token: {self.tokenizer.pad_token}")

        # Model
        print(f"\n📦 Model yükleniyor (bf16)...")
        self.model = AutoModelForCausalLM.from_pretrained(
            self.config.base_model_path,
            device_map="auto",
            torch_dtype=torch.bfloat16 if self.config.bf16 else torch.float16,
            trust_remote_code=True,
            use_cache=False  # Gradient checkpointing için
        )

        # Gradient checkpointing
        if self.config.gradient_checkpointing:
            self.model.gradient_checkpointing_enable()
            self.model.enable_input_require_grads()
            print(f"   ✓ Gradient checkpointing aktif")

        params = sum(p.numel() for p in self.model.parameters())
        print(f"   ✓ Model yüklendi")
        print(f"     Parametreler: {params / 1e9:.2f}B")

    def setup_lora(self):
        """LoRA konfigürasyonu"""
        print(f"\n🔧 LoRA ayarlanıyor...")
        print(f"   Rank: {self.config.lora_r}")
        print(f"   Alpha: {self.config.lora_alpha}")
        print(f"   Target modules: {', '.join(self.config.lora_target_modules)}")

        lora_config = LoraConfig(
            r=self.config.lora_r,
            lora_alpha=self.config.lora_alpha,
            target_modules=self.config.lora_target_modules,
            lora_dropout=self.config.lora_dropout,
            bias="none",
            task_type="CAUSAL_LM",
            inference_mode=False
        )

        self.model = get_peft_model(self.model, lora_config)

        trainable_params = sum(p.numel() for p in self.model.parameters() if p.requires_grad)
        all_params = sum(p.numel() for p in self.model.parameters())

        print(f"   ✓ LoRA aktif")
        print(f"     Trainable: {trainable_params / 1e6:.2f}M ({100 * trainable_params / all_params:.3f}%)")
        print(f"     VRAM tasarrufu: ~{(all_params - trainable_params) * 2 / 1024**3:.1f} GB")

    def prepare_dataset(self):
        """Dataset hazırla ve tokenize et"""
        print(f"\n📚 Dataset yükleniyor...")
        print(f"   Path: {self.config.dataset_path}")

        if not Path(self.config.dataset_path).exists():
            raise FileNotFoundError(f"❌ Dataset bulunamadı: {self.config.dataset_path}")

        # JSONL formatında yükle
        dataset = load_dataset('json', data_files=self.config.dataset_path, split='train')
        print(f"   ✓ Dataset yüklendi: {len(dataset)} örnek")

        # İlk örneği göster
        print(f"\n   İlk örnek:")
        first_example = dataset[0]
        print(f"     Messages: {len(first_example['messages'])} mesaj")
        for msg in first_example['messages']:
            role = msg['role']
            content = msg['content'][:100] + "..." if len(msg['content']) > 100 else msg['content']
            print(f"       [{role}]: {content}")

        # Tokenize
        def tokenize_function(examples):
            """Qwen chat template kullanarak tokenize et"""
            texts = []

            for messages in examples['messages']:
                # Qwen chat template
                text = self.tokenizer.apply_chat_template(
                    messages,
                    tokenize=False,
                    add_generation_prompt=False
                )
                texts.append(text)

            # Tokenize
            tokenized = self.tokenizer(
                texts,
                truncation=True,
                max_length=self.config.max_seq_length,
                padding=False,  # Dynamic padding
                return_tensors=None
            )

            # Labels = input_ids (causal LM)
            tokenized["labels"] = [
                input_ids.copy() for input_ids in tokenized["input_ids"]
            ]

            return tokenized

        print(f"\n🔄 Tokenization yapılıyor...")
        tokenized_dataset = dataset.map(
            tokenize_function,
            batched=True,
            remove_columns=dataset.column_names,
            desc="Tokenizing",
            num_proc=1  # Windows'ta 1 kullan
        )

        print(f"   ✓ Tokenization tamamlandı")
        print(f"     Toplam örnek: {len(tokenized_dataset)}")

        # İstatistikler
        lengths = [len(x) for x in tokenized_dataset["input_ids"]]
        print(f"     Token uzunlukları:")
        print(f"       Min: {min(lengths)}")
        print(f"       Max: {max(lengths)}")
        print(f"       Ortalama: {sum(lengths) / len(lengths):.1f}")

        return tokenized_dataset

    def train(self, dataset):
        """Training başlat"""
        print(f"\n🎓 Training başlıyor...")
        print(f"   Epochs: {self.config.num_epochs}")
        print(f"   Batch size: {self.config.batch_size}")
        print(f"   Gradient accumulation: {self.config.gradient_accumulation_steps}")
        print(f"   Effective batch size: {self.config.batch_size * self.config.gradient_accumulation_steps}")
        print(f"   Learning rate: {self.config.learning_rate}")
        print(f"   Total steps: ~{len(dataset) * self.config.num_epochs // (self.config.batch_size * self.config.gradient_accumulation_steps)}")

        training_args = TrainingArguments(
            output_dir=self.config.output_dir,
            num_train_epochs=self.config.num_epochs,
            per_device_train_batch_size=self.config.batch_size,
            gradient_accumulation_steps=self.config.gradient_accumulation_steps,
            learning_rate=self.config.learning_rate,
            warmup_ratio=self.config.warmup_ratio,
            max_grad_norm=self.config.max_grad_norm,
            logging_steps=self.config.logging_steps,
            save_steps=self.config.save_steps,
            save_total_limit=self.config.save_total_limit,
            fp16=self.config.fp16,
            bf16=self.config.bf16,
            optim=self.config.optim,
            gradient_checkpointing=self.config.gradient_checkpointing,
            logging_dir=f"{self.config.output_dir}/logs",
            report_to="tensorboard",
            remove_unused_columns=False,
            dataloader_num_workers=0,  # Windows için 0
            save_safetensors=True,
            lr_scheduler_type="cosine",
        )

        # Data collator
        data_collator = DataCollatorForSeq2Seq(
            tokenizer=self.tokenizer,
            model=self.model,
            padding=True,
            pad_to_multiple_of=8  # Performans için
        )

        # Trainer
        trainer = Trainer(
            model=self.model,
            args=training_args,
            train_dataset=dataset,
            data_collator=data_collator,
        )

        # Train!
        print("\n" + "="*70)
        print("TRAINING BAŞLADI")
        print("RTX 5080'de ~30-60 dakika sürebilir")
        print("="*70 + "\n")

        trainer.train()

        print("\n" + "="*70)
        print("✅ TRAINING TAMAMLANDI!")
        print("="*70)

        # Save
        print(f"\n💾 Model kaydediliyor...")
        final_path = f"{self.config.output_dir}/final"
        trainer.save_model(final_path)
        self.tokenizer.save_pretrained(final_path)
        print(f"   ✓ Model kaydedildi: {final_path}")

        # Save LoRA adapters
        lora_path = f"{self.config.output_dir}/lora_adapters"
        self.model.save_pretrained(lora_path)
        print(f"   ✓ LoRA adapters: {lora_path}")

        return trainer

    def run(self):
        """Tam pipeline"""
        try:
            self.load_model()
            self.setup_lora()
            dataset = self.prepare_dataset()
            trainer = self.train(dataset)

            print("\n" + "="*70)
            print("🎉 SnarcAI FİNE-TUNING TAMAMLANDI!")
            print("="*70)
            print(f"\nModel kullanımı:")
            print(f"  1. Inference için:")
            print(f"     python snarcai_chat.py")
            print(f"\n  2. Merge için (opsiyonel):")
            print(f"     python merge_lora.py")
            print("="*70)

            return True

        except Exception as e:
            print(f"\n❌ Hata: {e}")
            import traceback
            traceback.print_exc()
            return False


def main():
    parser = argparse.ArgumentParser(description="SnarcAI Fine-Tuning")

    parser.add_argument('--model', help='Base model path', default=None)
    parser.add_argument('--dataset', default='./snarcai_training_dataset.jsonl', help='Training dataset')
    parser.add_argument('--output', default='./snarcai-qwen-2.5-7b', help='Output directory')
    parser.add_argument('--epochs', type=int, default=5, help='Training epochs')
    parser.add_argument('--batch-size', type=int, default=2, help='Batch size')
    parser.add_argument('--lora-r', type=int, default=64, help='LoRA rank')
    parser.add_argument('--lr', type=float, default=1e-4, help='Learning rate')

    args = parser.parse_args()

    # Config oluştur
    config = SnarcAIConfig(
        base_model_path=args.model or SnarcAIConfig.base_model_path,
        dataset_path=args.dataset,
        output_dir=args.output,
        num_epochs=args.epochs,
        batch_size=args.batch_size,
        lora_r=args.lora_r,
        learning_rate=args.lr
    )

    # Fine-tune!
    tuner = SnarcAIFineTuner(config)
    success = tuner.run()

    return 0 if success else 1


if __name__ == "__main__":
    exit(main())
