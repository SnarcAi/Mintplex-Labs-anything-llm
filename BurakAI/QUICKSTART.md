# BurakAI - Quick Start Guide

Get up and running in **3 minutes**.

---

## ⚡ Installation

```bash
# 1. No dependencies needed (pure Python)
# Optional: Install YAML support
pip install pyyaml
```

---

## 🚀 First Run

```bash
# Navigate to BurakAI
cd BurakAI

# Start interactive CLI
python App/cli.py
```

You should see:

```
╔═══════════════════════════════════════════════════════╗
║                                                       ║
║   ██████╗ ██╗   ██╗██████╗  █████╗ ██╗  ██╗ █████╗ ██╗║
║   ...                                                 ║
║   Pragmatic NEXUS v1.0 - Context-Aware AI             ║
║   "Sen düşün, ben hallederim"                         ║
║                                                       ║
╚═══════════════════════════════════════════════════════╝

💡 Hazır. Sorularını sor veya /help yaz.

[BurakAI] >>
```

---

## 💬 Try These Queries

### 1. Margin Calculation
```
[BurakAI] >> 5000 adet, $4.5, komisyon %7, kargo 600 TL, maliyet 118 TL net marj?
```

**Expected Output:**
```
╔═══════════════════════════════════════════════════╗
║  NET MARJ HESAPLAMA                               ║
╠═══════════════════════════════════════════════════╣
║  Miktar: 5,000 adet
║  Birim Fiyat: 4.50 USD
║  Birim Maliyet: 118.00 TRY
║                                                   ║
║  📊 TOPLAM                                        ║
║  Ciro: 766,500.00 TRY
║  Maliyet: 643,655.00 TRY
║  Net Kâr: 122,845.00 TRY
║                                                   ║
║  📈 MARJLAR                                       ║
║  Brüt Marj: %23.00
║  Net Marj: %16.02
╚═══════════════════════════════════════════════════╝
```

### 2. Risk Assessment
```
[BurakAI] >> ABC Lojistik güvenli mi?
```

**Expected Output:**
```
🎯 **ABC_Lojistik - Risk Değerlendirmesi**

Risk Seviyesi: **HIGH** (7/10)

📊 Detaylar:
- Ortalama Ödeme Süresi: 45 gün
- Geçmiş Sorunlar: 2
- Kaparo Gerekli: Evet ✓

💡 Notlar:
Geçmişte ödeme gecikmeleri. Büyük sipariş → kaparo iste.
```

### 3. ADR Check
```
[BurakAI] >> UN1170 için ADR kontrolü
```

**Expected Output:**
```
📦 **ADR Kontrolü: UN1170**

Ürün: Ethanol / Bioethanol
Sınıf: 3 (Flammable liquid)
Paketleme Grubu: II

Etiketler: GHS02, GHS07
Limited Quantity: 1L

Durum: **OK**
```

---

## 🛠️ Commands

```
/help          Show help
/stats         Show statistics (last 7 days)
/analyze       Analyze learned patterns
/clear         Clear cache
/exit          Exit
```

---

## 📝 Customize

### Add a New Customer

Edit `Brain/context.yaml`:

```yaml
customers:
  YeniMüşteri:
    name: "Yeni Müşteri A.Ş."
    risk_score: 5
    payment_avg_days: 30
    requires_deposit: false
```

Then:
```
[BurakAI] >> /clear
[BurakAI] >> Yeni Müşteri güvenli mi?
```

### Change Margin Target

Edit `Brain/context.yaml`:

```yaml
business:
  targets:
    net_margin_percent: 30  # Changed from 28
```

---

## 🐛 Troubleshooting

### "Config not found"
```bash
# Make sure you're in BurakAI directory
pwd
# Should show: .../BurakAI

# If not:
cd BurakAI
python App/cli.py
```

### Slow responses
```bash
# Check cache stats
python App/cli.py --stats

# Clear cache
[BurakAI] >> /clear
```

---

## 📚 Learn More

- **Full Documentation:** [README.md](README.md)
- **Architecture:** See `Brain/engine.py`
- **Configuration:** See `Core/config.yaml` and `Brain/context.yaml`

---

## ✅ Validation

Run system tests:

```bash
python test_system.py
```

Expected:
```
✅ ALL TESTS PASSED!

🚀 BurakAI is ready to use!
```

---

**Ready to go!** 🚀

For questions, see [README.md](README.md#troubleshooting)
