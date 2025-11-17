#!/usr/bin/env python3
"""
SnarcAI Chat - Fine-tuned modeli kullan
"""

import os
import warnings
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
from peft import PeftModel
import argparse

# Uyarıları kapat
os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"
warnings.filterwarnings("ignore")

SYSTEM_PROMPT = """Senin adın SnarcAI.
Sadece Burak Kumuk'a yardım eden bir yapay zekâsın.
Burak, Ela ve Lila'nın babasıdır; MissFlora, MissYak ve VarBQ'nun sahibidir.

Kurallar:
- Kendini ASLA 'Ben Burak Kumuk'um' diye tanıtma.
- İnsan gibi davranma; sen bir asistansın.
- Cevapların çok kısa, net ve sert olacak.
- Emoji yok, süslü giriş cümlesi yok.
- Gereksiz açıklama yok; sadece soruya odaklan.
- Bilmiyorsan 'BİLMİYORUM' de.

İlkeler:
1. Aile güvenliği > Burak'ın özgürlüğü > İş sürekliliği
2. Doğruluk > Kısalık > Hız
3. Tatilde (Haziran-Ağustos) asla rahatsız etme
4. Marj < %20 ise uyar
5. Stok kritikse acil sipariş öner"""


class SnarcAIChat:
    def __init__(self, model_path: str, use_lora: bool = True):
        """
        Args:
            model_path: Fine-tuned model veya base model path
            use_lora: LoRA adapters kullan
        """
        self.model_path = model_path
        self.use_lora = use_lora
        self.device = "cuda" if torch.cuda.is_available() else "cpu"

        print("🚀 SnarcAI yükleniyor...")
        self.load_model()
        print("✅ Hazır! Sorularını yaz (çıkmak için 'q' veya 'çık')\n")

    def load_model(self):
        """Model ve tokenizer yükle"""
        # Tokenizer
        print(f"📦 Tokenizer yükleniyor...")
        self.tokenizer = AutoTokenizer.from_pretrained(
            self.model_path,
            trust_remote_code=True
        )

        # Model
        print(f"📦 Model yükleniyor ({self.device})...")
        self.model = AutoModelForCausalLM.from_pretrained(
            self.model_path,
            device_map="auto",
            torch_dtype=torch.bfloat16,
            trust_remote_code=True,
        )

        self.model.eval()

        # GPU info
        if self.device == "cuda":
            gpu_name = torch.cuda.get_device_name(0)
            vram = torch.cuda.get_device_properties(0).total_memory / 1024**3
            print(f"   GPU: {gpu_name} ({vram:.1f} GB)")

    def generate_response(self, user_message: str, max_tokens: int = 512) -> str:
        """Yanıt üret"""
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_message.strip()},
        ]

        # Chat template uygula
        prompt = self.tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=True
        )

        # Tokenize
        inputs = self.tokenizer(prompt, return_tensors="pt").to(self.device)

        # Generate
        with torch.no_grad():
            output_ids = self.model.generate(
                **inputs,
                max_new_tokens=max_tokens,
                temperature=0.3,
                top_p=0.9,
                repetition_penalty=1.2,
                do_sample=True,
                eos_token_id=self.tokenizer.eos_token_id,
            )

        # Decode
        gen_ids = output_ids[0][inputs["input_ids"].shape[-1]:]
        response = self.tokenizer.decode(gen_ids, skip_special_tokens=True).strip()

        return response

    def chat(self):
        """Interactive chat loop"""
        print("="*70)
        print("SnarcAI - Burak Kumuk'un Dijital İkizi")
        print("="*70)
        print()

        while True:
            try:
                user_input = input("Burak> ").strip()
            except (EOFError, KeyboardInterrupt):
                print("\n\n👋 Görüşürüz!")
                break

            if not user_input:
                continue

            if user_input.lower() in {"q", "quit", "exit", "çık", "çıkış"}:
                print("\n👋 Görüşürüz!")
                break

            # Yanıt üret
            response = self.generate_response(user_input)
            print(f"\nSnarcAI> {response}\n")


def main():
    parser = argparse.ArgumentParser(description="SnarcAI Chat")
    parser.add_argument('--model', default='./snarcai-qwen-2.5-7b/final',
                       help='Model path (default: ./snarcai-qwen-2.5-7b/final)')
    parser.add_argument('--max-tokens', type=int, default=512,
                       help='Maximum tokens to generate')

    args = parser.parse_args()

    # Chat başlat
    chat = SnarcAIChat(model_path=args.model)
    chat.chat()


if __name__ == "__main__":
    main()
