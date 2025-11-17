#!/usr/bin/env python3
"""
MORİ Test & Inference Script
Eğitilmiş MORİ modelini test et ve konuş!
NIRVANA Projesi - Lavanta-mor ayı MORİ
"""

import torch
from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
from peft import PeftModel
import argparse
from pathlib import Path
import warnings

warnings.filterwarnings('ignore')


class MoriChat:
    """MORİ ile sohbet arayüzü"""

    def __init__(self, model_path: str, use_lora: bool = True):
        """
        Args:
            model_path: MORİ model klasörü
            use_lora: LoRA adapterlerini yükle (varsayılan: True)
        """
        self.model_path = model_path
        self.use_lora = use_lora
        self.device = "cuda" if torch.cuda.is_available() else "cpu"

        print("\n" + "="*60)
        print("🐻 MORİ - Lavanta-Mor Ayı Arkadaşın!")
        print("="*60)
        print(f"Device: {self.device}")

        if self.device == "cuda":
            print(f"GPU: {torch.cuda.get_device_name(0)}")
            print(f"VRAM: {torch.cuda.get_device_properties(0).total_memory / 1024**3:.1f} GB")

        self.load_model()

    def load_model(self):
        """Model ve tokenizer yükle"""
        print(f"\n📦 Model yükleniyor: {self.model_path}")

        # Tokenizer
        self.tokenizer = AutoTokenizer.from_pretrained(
            self.model_path,
            trust_remote_code=True,
        )

        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token

        print(f"✓ Tokenizer yüklendi")

        # Model
        self.model = AutoModelForCausalLM.from_pretrained(
            self.model_path,
            device_map="auto",
            torch_dtype=torch.bfloat16 if self.device == "cuda" else torch.float32,
            trust_remote_code=True,
        )

        # LoRA adapters varsa yükle
        lora_path = Path(self.model_path) / "lora_adapters"
        if self.use_lora and lora_path.exists():
            print(f"🔧 LoRA adapters yükleniyor...")
            self.model = PeftModel.from_pretrained(self.model, str(lora_path))
            print(f"✓ LoRA adapters yüklendi")

        self.model.eval()

        print(f"✓ Model yüklendi ve hazır!")
        print("="*60 + "\n")

    def generate_response(
        self,
        user_input: str,
        max_new_tokens: int = 200,
        temperature: float = 0.8,
        top_p: float = 0.9,
        top_k: int = 50,
    ) -> str:
        """
        Kullanıcı girdisine MORİ cevabı üret

        Args:
            user_input: Kullanıcı sorusu/mesajı
            max_new_tokens: Maksimum token sayısı
            temperature: Yaratıcılık (0.0-1.0, yüksek = daha yaratıcı)
            top_p: Nucleus sampling
            top_k: Top-k sampling

        Returns:
            MORİ'nin cevabı
        """
        # System prompt
        system_prompt = (
            "Sen MORİ'sin, 2-9 yaş arası çocukların en sevimli arkadaşı lavanta-mor ayısın. "
            "Her zaman sevgi dolu, eğlenceli, eğitici ve cesaretlendirici cevaplar verirsin. "
            "Bol emoji kullanırsın."
        )

        # Prompt oluştur (model tipine göre)
        if "gemma" in self.model_path.lower():
            # Gemma chat formatı
            messages = [
                {"role": "user", "content": f"{system_prompt}\n\n{user_input}"}
            ]

            try:
                prompt = self.tokenizer.apply_chat_template(
                    messages,
                    tokenize=False,
                    add_generation_prompt=True
                )
            except:
                # Fallback
                prompt = f"<bos><start_of_turn>user\n{system_prompt}\n\n{user_input}<end_of_turn>\n<start_of_turn>model\n"
        else:
            # GPT2 formatı
            prompt = f"### Instruction: {system_prompt}\n\n### Input: {user_input}\n\n### Response:"

        # Tokenize
        inputs = self.tokenizer(prompt, return_tensors="pt").to(self.device)

        # Generate
        with torch.no_grad():
            outputs = self.model.generate(
                **inputs,
                max_new_tokens=max_new_tokens,
                temperature=temperature,
                top_p=top_p,
                top_k=top_k,
                do_sample=True,
                pad_token_id=self.tokenizer.pad_token_id,
                eos_token_id=self.tokenizer.eos_token_id,
            )

        # Decode
        full_output = self.tokenizer.decode(outputs[0], skip_special_tokens=True)

        # Response'u ayıkla
        if "gemma" in self.model_path.lower():
            # Gemma formatında son model cevabını al
            if "<start_of_turn>model" in full_output:
                response = full_output.split("<start_of_turn>model")[-1].strip()
                if "<end_of_turn>" in response:
                    response = response.split("<end_of_turn>")[0].strip()
            else:
                response = full_output.replace(prompt, "").strip()
        else:
            # GPT2 formatında ### Response: sonrasını al
            if "### Response:" in full_output:
                response = full_output.split("### Response:")[-1].strip()
            else:
                response = full_output.replace(prompt, "").strip()

        return response

    def chat(self):
        """İnteraktif sohbet modu"""
        print("💬 MORİ ile Sohbet!")
        print("   (Çıkmak için 'exit' veya 'çıkış' yazın)\n")

        while True:
            try:
                user_input = input("🧒 Sen: ").strip()

                if not user_input:
                    continue

                if user_input.lower() in ['exit', 'quit', 'çıkış', 'q']:
                    print("\n🐻 MORİ: Görüşmek üzere tatlım! Seni çok seviyorum! ❤️✨\n")
                    break

                print("🐻 MORİ: ", end="", flush=True)
                response = self.generate_response(user_input)
                print(response + "\n")

            except KeyboardInterrupt:
                print("\n\n🐻 MORİ: Hoşça kal canım! 💕\n")
                break
            except Exception as e:
                print(f"\n❌ Hata: {e}\n")

    def test_samples(self):
        """Örnek testler çalıştır"""
        test_cases = [
            "Mori, 5 artı 3 kaç eder?",
            "Üzgünüm Mori",
            "Denize çöp atsak olur mu?",
            "Paylaşmak neden önemli?",
            "Bana bir masal anlatır mısın?",
            "1'den 10'a kadar sayar mısın?",
            "Dişlerimi fırçalamalı mıyım?",
            "Korkuyorum Mori",
            "Ağaçları neden korumalıyız?",
            "Teşekkür etmeliyim değil mi?",
        ]

        print("🧪 Test Örnekleri Çalıştırılıyor...\n")
        print("="*60)

        for i, test in enumerate(test_cases, 1):
            print(f"\n[{i}/{len(test_cases)}] Çocuk: {test}")
            print(f"🐻 MORİ: ", end="", flush=True)

            response = self.generate_response(test)
            print(response)

            print("-"*60)

        print("\n✅ Tüm testler tamamlandı!\n")


def main():
    """Ana fonksiyon"""
    parser = argparse.ArgumentParser(
        description="MORİ Test & Chat Interface",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Kullanım Örnekleri:
  # İnteraktif sohbet modu
  python test_mori.py --model ./mori-model --chat

  # Test örneklerini çalıştır
  python test_mori.py --model ./mori-model --test

  # Tek soru sor
  python test_mori.py --model ./mori-model --prompt "5+3 kaç eder?"

  # Daha yaratıcı cevaplar (yüksek temperature)
  python test_mori.py --model ./mori-model --chat --temperature 0.9
        """
    )

    parser.add_argument('--model', type=str, required=True,
                        help='MORİ model klasörü (örn: ./mori-model)')
    parser.add_argument('--chat', action='store_true',
                        help='İnteraktif sohbet modu')
    parser.add_argument('--test', action='store_true',
                        help='Test örneklerini çalıştır')
    parser.add_argument('--prompt', type=str,
                        help='Tek bir prompt test et')
    parser.add_argument('--temperature', type=float, default=0.8,
                        help='Temperature (0.0-1.0, default: 0.8)')
    parser.add_argument('--max-tokens', type=int, default=200,
                        help='Maksimum token sayısı (default: 200)')
    parser.add_argument('--no-lora', action='store_true',
                        help='LoRA adapters kullanma')

    args = parser.parse_args()

    # Model kontrolü
    if not Path(args.model).exists():
        print(f"❌ Model bulunamadı: {args.model}")
        print(f"\nÖnce modeli eğitin:")
        print(f"  python train_mori_rtx5080.py")
        return

    # MORİ yükle
    mori = MoriChat(args.model, use_lora=not args.no_lora)

    # Mod seç
    if args.chat:
        mori.chat()
    elif args.test:
        mori.test_samples()
    elif args.prompt:
        print(f"🧒 Soru: {args.prompt}")
        print(f"🐻 MORİ: ", end="", flush=True)
        response = mori.generate_response(
            args.prompt,
            max_new_tokens=args.max_tokens,
            temperature=args.temperature
        )
        print(response + "\n")
    else:
        print("❌ Bir mod seçin: --chat, --test, veya --prompt")
        print("   Yardım için: python test_mori.py --help")


if __name__ == "__main__":
    main()
