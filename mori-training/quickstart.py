#!/usr/bin/env python3
"""
MORİ Quickstart - Tek Tıkla Başlat
Veri oluştur -> Eğit -> Test (otomatik pipeline)
NIRVANA Projesi
"""

import subprocess
import sys
import os
from pathlib import Path
import argparse


def run_command(cmd, description):
    """Komutu çalıştır ve logla"""
    print("\n" + "="*60)
    print(f"▶️  {description}")
    print("="*60)
    print(f"Komut: {' '.join(cmd)}\n")

    try:
        result = subprocess.run(cmd, check=True)
        print(f"\n✅ {description} - TAMAMLANDI")
        return True
    except subprocess.CalledProcessError as e:
        print(f"\n❌ {description} - BAŞARISIZ")
        print(f"Hata: {e}")
        return False
    except KeyboardInterrupt:
        print(f"\n⚠️  {description} - KULLANICI DURDURDU")
        return False


def check_environment():
    """Ortamı kontrol et"""
    print("\n🔍 Sistem Kontrolü...")

    # Python version
    python_version = sys.version_info
    print(f"  Python: {python_version.major}.{python_version.minor}.{python_version.micro}")

    if python_version < (3, 10):
        print("  ❌ Python 3.10+ gerekli!")
        return False

    # PyTorch & CUDA
    try:
        import torch
        print(f"  PyTorch: {torch.__version__}")

        if torch.cuda.is_available():
            print(f"  ✅ CUDA: {torch.version.cuda}")
            print(f"  ✅ GPU: {torch.cuda.get_device_name(0)}")
            vram = torch.cuda.get_device_properties(0).total_memory / 1024**3
            print(f"  ✅ VRAM: {vram:.1f} GB")

            if vram < 12:
                print("  ⚠️  VRAM 12GB'dan az! Batch size küçük olacak.")
        else:
            print("  ❌ CUDA bulunamadı! GPU gerekli.")
            return False
    except ImportError:
        print("  ❌ PyTorch kurulu değil!")
        print("  Kurulum: pip install torch --index-url https://download.pytorch.org/whl/cu121")
        return False

    # Transformers
    try:
        import transformers
        print(f"  Transformers: {transformers.__version__}")
    except ImportError:
        print("  ❌ Transformers kurulu değil!")
        print("  Kurulum: pip install -r requirements.txt")
        return False

    print("\n✅ Sistem hazır!\n")
    return True


def main():
    """Ana pipeline"""
    parser = argparse.ArgumentParser(
        description="MORİ Quickstart - Otomatik Pipeline",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Kullanım Örnekleri:
  # Tam pipeline (veri + eğitim + test)
  python quickstart.py

  # Sadece 10K veri ile hızlı test
  python quickstart.py --samples 10000 --epochs 3

  # Kendi verin varsa sadece eğitim + test
  python quickstart.py --skip-data

  # GPT2-medium ile hızlı eğitim
  python quickstart.py --model gpt2-medium --epochs 10
        """
    )

    parser.add_argument('--samples', type=int, default=20000,
                        help='Veri seti örnek sayısı (default: 20000)')
    parser.add_argument('--epochs', type=int, default=5,
                        help='Training epochs (default: 5)')
    parser.add_argument('--model', type=str, default='google/gemma-2-2b-it',
                        help='Base model (default: google/gemma-2-2b-it)')
    parser.add_argument('--batch-size', type=int, default=8,
                        help='Batch size (default: 8)')
    parser.add_argument('--skip-data', action='store_true',
                        help='Veri oluşturma adımını atla')
    parser.add_argument('--skip-test', action='store_true',
                        help='Test adımını atla')
    parser.add_argument('--output', type=str, default='./mori-model',
                        help='Model output klasörü')

    args = parser.parse_args()

    print("\n" + "="*60)
    print("🐻 MORİ QUICKSTART - OTOMATIK PİPELİNE")
    print("="*60)
    print(f"Veri: {args.samples:,} örnek")
    print(f"Model: {args.model}")
    print(f"Epochs: {args.epochs}")
    print(f"Batch Size: {args.batch_size}")
    print(f"Output: {args.output}")
    print("="*60)

    # Sistem kontrolü
    if not check_environment():
        print("\n❌ Sistem kontrolü başarısız!")
        return 1

    # Pipeline adımları
    steps_completed = 0
    total_steps = 3 - int(args.skip_data) - int(args.skip_test)

    # 1. Veri oluştur
    if not args.skip_data:
        dataset_file = "mori_dataset.jsonl"

        if Path(dataset_file).exists():
            response = input(f"\n⚠️  {dataset_file} zaten var. Üzerine yaz? (y/n): ")
            if response.lower() != 'y':
                print("Mevcut veri seti kullanılacak.")
            else:
                if not run_command(
                    [sys.executable, "generate_mori_dataset.py",
                     "--samples", str(args.samples),
                     "--output", dataset_file],
                    f"1/{total_steps} - Veri Seti Oluşturma ({args.samples:,} örnek)"
                ):
                    return 1
                steps_completed += 1
        else:
            if not run_command(
                [sys.executable, "generate_mori_dataset.py",
                 "--samples", str(args.samples),
                 "--output", dataset_file],
                f"1/{total_steps} - Veri Seti Oluşturma ({args.samples:,} örnek)"
            ):
                return 1
            steps_completed += 1
    else:
        print("\n⏭️  Veri oluşturma atlandı (--skip-data)")

    # 2. Model eğit
    if not run_command(
        [sys.executable, "train_mori_rtx5080.py",
         "--model", args.model,
         "--epochs", str(args.epochs),
         "--batch-size", str(args.batch_size),
         "--output", args.output],
        f"2/{total_steps} - Model Eğitimi ({args.epochs} epoch)"
    ):
        return 1
    steps_completed += 1

    # 3. Test
    if not args.skip_test:
        if not run_command(
            [sys.executable, "test_mori.py",
             "--model", args.output,
             "--test"],
            f"3/{total_steps} - Model Testi"
        ):
            print("\n⚠️  Test başarısız ama model kullanılabilir!")

        steps_completed += 1
    else:
        print("\n⏭️  Test atlandı (--skip-test)")

    # Başarı mesajı
    print("\n" + "="*60)
    print("🎉 MORİ QUICKSTART TAMAMLANDI!")
    print("="*60)
    print(f"✅ {steps_completed}/{total_steps} adım tamamlandı")
    print(f"\nModel yolu: {Path(args.output).absolute()}")
    print(f"\nŞimdi MORİ ile konuşabilirsin:")
    print(f"  python test_mori.py --model {args.output} --chat")
    print("="*60 + "\n")

    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\n⚠️  Pipeline kullanıcı tarafından durduruldu!")
        sys.exit(1)
