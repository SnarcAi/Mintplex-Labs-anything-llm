#!/usr/bin/env python3
"""
JSON AI Fine-Tuning Script
Qwen 2.5 7B için LoRA ile JSON task'larında fine-tuning
RTX 5080 optimize
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
class FineTuneConfig:
    """Fine-tuning konfigürasyonu"""
    # Model
    base_model_path: str = None
    output_dir: str = "./qwen-json-assistant"

    # Dataset
    dataset_path: str = "./json_training_dataset.jsonl"
    max_seq_length: int = 2048

    # LoRA
    lora_r: int = 32  # Rank
    lora_alpha: int = 64
    lora_dropout: float = 0.05
    lora_target_modules: list = field(default_factory=lambda: ["q_proj", "k_proj", "v_proj", "o_proj"])

    # Training
    num_epochs: int = 3
    batch_size: int = 4  # RTX 5080 16GB için optimize
    gradient_accumulation_steps: int = 4  # Effective batch = 16
    learning_rate: float = 2e-4
    warmup_steps: int = 100
    save_steps: int = 500
    logging_steps: int = 10

    # Optimization
    fp16: bool = False
    bf16: bool = True  # RTX 5080 için bf16 daha iyi
    gradient_checkpointing: bool = True
    optim: str = "adamw_torch"  # veya "adamw_8bit" için daha az VRAM


class JSONFineTuner:
    def __init__(self, config: FineTuneConfig):
        self.config = config
        self.tokenizer = None
        self.model = None
        self.device = "cuda" if torch.cuda.is_available() else "cpu"

        print(f"🚀 Fine-Tuning Başlıyor")
        print(f"   Device: {self.device}")
        if self.device == "cuda":
            print(f"   GPU: {torch.cuda.get_device_name(0)}")
            print(f"   VRAM: {torch.cuda.get_device_properties(0).total_memory / 1024**3:.1f} GB")

    def auto_detect_model(self):
        """HF cache'den Qwen modelini bul"""
        cache_dir = Path.home() / ".cache" / "huggingface" / "hub"
        qwen_dirs = list(cache_dir.glob("models--Qwen--Qwen2.5-7B-Instruct"))

        if qwen_dirs:
            snapshots = list(qwen_dirs[0].glob("snapshots/*"))
            if snapshots:
                return str(snapshots[-1])

        return None

    def load_model(self):
        """Model ve tokenizer yükle"""
        model_path = self.config.base_model_path

        if not model_path:
            model_path = self.auto_detect_model()
            if not model_path:
                raise ValueError("❌ Model bulunamadı! --model parametresi ile path verin")

        print(f"📦 Model yükleniyor: {model_path}")

        # Tokenizer
        self.tokenizer = AutoTokenizer.from_pretrained(
            model_path,
            trust_remote_code=True,
            padding_side="right"  # Training için
        )

        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token

        # Model
        self.model = AutoModelForCausalLM.from_pretrained(
            model_path,
            device_map="auto",
            torch_dtype=torch.bfloat16 if self.config.bf16 else torch.float16,
            trust_remote_code=True,
        )

        # Gradient checkpointing
        if self.config.gradient_checkpointing:
            self.model.gradient_checkpointing_enable()
            self.model.enable_input_require_grads()

        print(f"✓ Model yüklendi")
        print(f"   Parametreler: {self.model.num_parameters() / 1e9:.2f}B")

    def setup_lora(self):
        """LoRA konfigürasyonu"""
        print(f"🔧 LoRA ayarlanıyor (rank={self.config.lora_r})")

        lora_config = LoraConfig(
            r=self.config.lora_r,
            lora_alpha=self.config.lora_alpha,
            target_modules=self.config.lora_target_modules,
            lora_dropout=self.config.lora_dropout,
            bias="none",
            task_type="CAUSAL_LM"
        )

        self.model = get_peft_model(self.model, lora_config)

        trainable_params = sum(p.numel() for p in self.model.parameters() if p.requires_grad)
        all_params = sum(p.numel() for p in self.model.parameters())

        print(f"✓ LoRA aktif")
        print(f"   Trainable: {trainable_params / 1e6:.2f}M ({100 * trainable_params / all_params:.2f}%)")

    def prepare_dataset(self):
        """Dataset hazırla"""
        print(f"📚 Dataset yükleniyor: {self.config.dataset_path}")

        if not Path(self.config.dataset_path).exists():
            raise FileNotFoundError(f"❌ Dataset bulunamadı: {self.config.dataset_path}")

        dataset = load_dataset('json', data_files=self.config.dataset_path, split='train')

        print(f"✓ Dataset yüklendi: {len(dataset)} örnek")

        # Tokenize
        def tokenize_function(examples):
            # Qwen chat format
            prompts = []
            for instruction, input_text, output in zip(
                examples['instruction'],
                examples['input'],
                examples['output']
            ):
                messages = [
                    {"role": "system", "content": "You are a JSON expert assistant."},
                    {"role": "user", "content": f"{instruction}\n\n{input_text}"},
                    {"role": "assistant", "content": output}
                ]

                prompt = self.tokenizer.apply_chat_template(
                    messages,
                    tokenize=False,
                    add_generation_prompt=False
                )
                prompts.append(prompt)

            # Tokenize
            tokenized = self.tokenizer(
                prompts,
                truncation=True,
                max_length=self.config.max_seq_length,
                padding=False,  # Dynamic padding
                return_tensors=None
            )

            # Labels = input_ids için causal LM
            tokenized["labels"] = tokenized["input_ids"].copy()

            return tokenized

        print("🔄 Tokenization yapılıyor...")
        tokenized_dataset = dataset.map(
            tokenize_function,
            batched=True,
            remove_columns=dataset.column_names,
            desc="Tokenizing"
        )

        print(f"✓ Tokenization tamamlandı")

        return tokenized_dataset

    def train(self, dataset):
        """Training başlat"""
        print(f"🎓 Training başlıyor...")
        print(f"   Epochs: {self.config.num_epochs}")
        print(f"   Batch size: {self.config.batch_size}")
        print(f"   Effective batch: {self.config.batch_size * self.config.gradient_accumulation_steps}")
        print(f"   Learning rate: {self.config.learning_rate}")

        training_args = TrainingArguments(
            output_dir=self.config.output_dir,
            num_train_epochs=self.config.num_epochs,
            per_device_train_batch_size=self.config.batch_size,
            gradient_accumulation_steps=self.config.gradient_accumulation_steps,
            learning_rate=self.config.learning_rate,
            warmup_steps=self.config.warmup_steps,
            logging_steps=self.config.logging_steps,
            save_steps=self.config.save_steps,
            save_total_limit=3,
            fp16=self.config.fp16,
            bf16=self.config.bf16,
            optim=self.config.optim,
            gradient_checkpointing=self.config.gradient_checkpointing,
            logging_dir=f"{self.config.output_dir}/logs",
            report_to="none",  # TensorBoard istemiyorsanız
            remove_unused_columns=False,
        )

        # Data collator
        data_collator = DataCollatorForSeq2Seq(
            tokenizer=self.tokenizer,
            model=self.model,
            padding=True
        )

        # Trainer
        trainer = Trainer(
            model=self.model,
            args=training_args,
            train_dataset=dataset,
            data_collator=data_collator,
        )

        # Train!
        print("\n" + "="*60)
        print("TRAINING BAŞLADI - RTX 5080'de ~1-2 saat sürebilir")
        print("="*60 + "\n")

        trainer.train()

        print("\n✓ Training tamamlandı!")

        # Save
        print(f"💾 Model kaydediliyor: {self.config.output_dir}")
        trainer.save_model(self.config.output_dir)
        self.tokenizer.save_pretrained(self.config.output_dir)

        print(f"✓ Model kaydedildi: {self.config.output_dir}")

        # Save LoRA adapters separately
        lora_path = f"{self.config.output_dir}/lora_adapters"
        self.model.save_pretrained(lora_path)
        print(f"✓ LoRA adapters kaydedildi: {lora_path}")

    def run(self):
        """Tam pipeline"""
        self.load_model()
        self.setup_lora()
        dataset = self.prepare_dataset()
        self.train(dataset)

        print("\n" + "="*60)
        print("🎉 FİNE-TUNING TAMAMLANDI!")
        print("="*60)
        print(f"\nModel kullanımı:")
        print(f"  python json_ai.py --model {self.config.output_dir} generate --count 100")


def main():
    parser = argparse.ArgumentParser(description="Qwen 2.5 7B JSON Fine-Tuning")

    parser.add_argument('--model', help='Base model path (default: auto-detect)')
    parser.add_argument('--dataset', default='./json_training_dataset.jsonl', help='Training dataset')
    parser.add_argument('--output', default='./qwen-json-assistant', help='Output directory')
    parser.add_argument('--epochs', type=int, default=3, help='Training epochs')
    parser.add_argument('--batch-size', type=int, default=4, help='Batch size')
    parser.add_argument('--lora-r', type=int, default=32, help='LoRA rank')
    parser.add_argument('--lr', type=float, default=2e-4, help='Learning rate')

    args = parser.parse_args()

    config = FineTuneConfig(
        base_model_path=args.model,
        dataset_path=args.dataset,
        output_dir=args.output,
        num_epochs=args.epochs,
        batch_size=args.batch_size,
        lora_r=args.lora_r,
        learning_rate=args.lr
    )

    tuner = JSONFineTuner(config)
    tuner.run()


if __name__ == "__main__":
    main()
