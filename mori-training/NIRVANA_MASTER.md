# NIRVANA – Final Master Document
(15 Kasım 2025, 23:31 +03 – İstanbul)
Tek dosya. Tek vizyon. Tüm sınırlar zorlanmış hali.
Kopyala-yapıştır yapıp başka AI'lara (Claude, Gemini, Llama-3.1-405B, vs.) direkt verip "bunu geliştir, ekle, eleştir" diyebilirsin.

## 1. İsim ve Tek Cümlelik Varoluş
**NIRVANA**
"2-9 yaş arası çocuğun ömür boyu en iyi arkadaşı ve anne-babanın en büyük kurtarıcısı."

## 2. Karakter
**MORİ** – Sevimli lavanta-mor ayı
- Gözleri içinde sürekli minik yıldız ve kalp patlar
- Sesi: Baba sesi (senin sesin) + hafif büyülü tını
- Enerjisi: %100 playfulness + joyfulness + saf sevgi + gezegen sevgisi

## 3. Yaş Aralığı (kesin)
2-9 yaş (ilk ve tek hedef kitle – 10+ yaş versiyonu sonra gelebilir)

## 4. Zaman Sistemi (gerçek hayatta çalışan tek versiyon)
- Varsayılan: 45 dakika/gün
- Seçenekler: 10 / 20 / 30 / 45 / 60 / 90 dakika
- Ekstra 15 dakika: Çocuk gerçek hayatta bir iyilik yaparsa Mori kendisi verir
- Uyku butonu: Anında kapanır + ninni

## 5. İçerik Havuzu (hepsi yerel, offline, 500+ parça)
1. **Sayı Maceraları** (en önemli)
   - 1'den 100'e sayma
   - Toplama-çıkarma-çarpma oyunları (her zaman kalp ve çiçek patlamalı)
2. **200 adet 10-40 saniyelik faydalı animasyon** (sonsuz kaydırma hissi)
   - "Denize çöp atmayalım"
   - "Arkadaşımıza sarılalım"
   - "Dünya bizim evimiz"
   - "Teşekkür ederim" patlamaları
3. **100 mini masal** (senin sesinle)
4. **50 tekerleme + 30 şarkı**
5. **Sessiz mod** (sadece altyazılı animasyon)

## 6. Teknik Paket (2025 sonu çalışır hali)
- Model: Gemma-2-27B-it → Q4_K_M (18 GB) veya 2026'da Llama-3.1-70B 8-bit
- İlk sürüm için hızlı prototip: **Gemma-2-2B-it + LoRA** (1.6 GB)
- Framework: iPad/Android → MLX veya llama.cpp
- Toplam boyut: 1.6-2.5 GB (tek indirme, sonra %100 offline)
- İlk açılış: <1 saniye
- Cevap gecikmesi: <0.4 saniye

## 7. Güvenlik (demir gibi)
- İlk kurulumdan sonra internet gerekmez
- Kamera/mikrofon asla kaydetmez
- Hiçbir veri dışarı çıkmaz
- Guided Access zorunlu
- Reklam yok, algoritmik bağımlılık tuzağı yok

## 8. Anne-Baba Rüşvetleri
- Tek tıkla 45-90 dakika seç
- Sessiz mod
- Uyku butonu
- Haftalık WhatsApp raporu ("Defne bu hafta 847 sayı saydı, 129 teşekkür etti")

## 9. 10 Haftalık Gerçekçi İnşa Takvimi (RTX 5080 + Local Training)
**Hafta 1** → 20.000 satır 2-9 yaş sevgi/sayı/gezegen sevgisi veri seti
**Hafta 2-4** → Gemma-2-2B LoRA (r=64) + Mori kişiliği fine-tuning (RTX 5080)
**Hafta 5-6** → 500 animasyon + senin sesinle tüm kayıtlar
**Hafta 7-8** → SwiftUI / Android uygulama (tam kod hazır)
**Hafta 9-10** → Defne'de kapalı beta → Mart 2026 lansman

## 10. Anayasanın Değiştirilemez 5 Maddesi
1. Mori asla yalan söylemez (bilimsel konularda)
2. Masalda istediği kadar abartabilir
3. Çocuk da anne-baba da mutlu olacak
4. TikTok/YouTube'u gereksiz kılacak
5. Ömür boyu ücretsiz temel sürüm kalacak

---

## Training Notları (RTX 5080 Özellikleri)
- **GPU**: NVIDIA RTX 5080 16GB VRAM
- **RAM**: 128GB DDR5
- **CPU**: AMD Ryzen 9 9950X (16 core / 32 thread)
- **Storage**: 2TB NVMe SSD
- **OS**: Windows 11 Pro
- **Python**: 3.13.7

### Model Seçimi
1. **Gemma-2-2B-it** (Önerilen) - 2B params, çok dilli, RTX 5080'de rahat
2. **GPT2-Medium** - 774M params, hızlı ama Türkçe zayıf
3. **ytu-ce-cosmos/turkish-gpt2-large** - 774M params, Türkçe özel

### Training Parametreleri (RTX 5080 için optimize)
- Batch size: 8-16 (16GB VRAM için ideal)
- Gradient accumulation: 2-4
- LoRA rank: 64 (kalite için)
- Learning rate: 2e-4
- Epochs: 3-10 (veri boyutuna göre)
- BF16: True (RTX 5080 Tensor Core'lar için)
- Gradient checkpointing: True (bellek tasarrufu)

---

Bu dosya artık tamamdır.
Kopyala, başka AI'lara at, kendin ekle, eleştir, parçala, yeniden yapıştır.
Hepsi burada.

**Sırada ne var?**
"İnşa başlasın"
