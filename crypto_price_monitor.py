#!/usr/bin/env python3
"""
Kripto Para Fiyat İzleme ve Alarm Sistemi
Bu kod kripto para fiyatlarını izler ve belirli fiyat seviyelerine ulaştığında alarm verir.
Para kazanma stratejisi: Düşükten al, yüksekten sat fırsatlarını yakalamak
"""

import requests
import time
import json
from datetime import datetime
from typing import Dict, List, Optional
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

class CryptoPriceMonitor:
    def __init__(self):
        self.base_url = "https://api.coingecko.com/api/v3"
        self.alerts = {}
        self.price_history = {}

    def get_crypto_price(self, crypto_id: str = "bitcoin") -> Optional[float]:
        """Belirli bir kripto paranın güncel fiyatını al"""
        try:
            url = f"{self.base_url}/simple/price"
            params = {
                'ids': crypto_id,
                'vs_currencies': 'usd,try',
                'include_24hr_change': 'true',
                'include_market_cap': 'true'
            }
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            if crypto_id in data:
                return {
                    'usd': data[crypto_id].get('usd', 0),
                    'try': data[crypto_id].get('try', 0),
                    'change_24h': data[crypto_id].get('usd_24h_change', 0),
                    'market_cap': data[crypto_id].get('usd_market_cap', 0)
                }
            return None
        except Exception as e:
            print(f"Fiyat alınırken hata: {e}")
            return None

    def get_top_gainers(self, limit: int = 10) -> List[Dict]:
        """En çok yükselen kripto paraları bul (trading fırsatları)"""
        try:
            url = f"{self.base_url}/coins/markets"
            params = {
                'vs_currency': 'usd',
                'order': 'price_change_percentage_24h_desc',
                'per_page': limit,
                'page': 1,
                'sparkline': False,
                'price_change_percentage': '24h'
            }
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            gainers = []
            for coin in data:
                gainers.append({
                    'id': coin['id'],
                    'name': coin['name'],
                    'symbol': coin['symbol'].upper(),
                    'price': coin['current_price'],
                    'change_24h': coin['price_change_percentage_24h'],
                    'volume': coin['total_volume'],
                    'market_cap': coin['market_cap']
                })
            return gainers
        except Exception as e:
            print(f"En çok yükselenler alınırken hata: {e}")
            return []

    def get_top_losers(self, limit: int = 10) -> List[Dict]:
        """En çok düşen kripto paraları bul (alım fırsatları)"""
        try:
            url = f"{self.base_url}/coins/markets"
            params = {
                'vs_currency': 'usd',
                'order': 'price_change_percentage_24h_asc',
                'per_page': limit,
                'page': 1,
                'sparkline': False,
                'price_change_percentage': '24h'
            }
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            losers = []
            for coin in data:
                losers.append({
                    'id': coin['id'],
                    'name': coin['name'],
                    'symbol': coin['symbol'].upper(),
                    'price': coin['current_price'],
                    'change_24h': coin['price_change_percentage_24h'],
                    'volume': coin['total_volume'],
                    'market_cap': coin['market_cap']
                })
            return losers
        except Exception as e:
            print(f"En çok düşenler alınırken hata: {e}")
            return []

    def set_price_alert(self, crypto_id: str, target_price: float, alert_type: str = "above"):
        """Fiyat alarmı ayarla (above: üstüne çıkarsa, below: altına düşerse)"""
        self.alerts[crypto_id] = {
            'target_price': target_price,
            'alert_type': alert_type,
            'created_at': datetime.now().isoformat()
        }
        print(f"✓ Alarm ayarlandı: {crypto_id} - ${target_price} ({alert_type})")

    def check_alerts(self) -> List[Dict]:
        """Alarmları kontrol et"""
        triggered_alerts = []
        for crypto_id, alert in self.alerts.items():
            price_data = self.get_crypto_price(crypto_id)
            if price_data:
                current_price = price_data['usd']

                if alert['alert_type'] == 'above' and current_price >= alert['target_price']:
                    triggered_alerts.append({
                        'crypto': crypto_id,
                        'current_price': current_price,
                        'target_price': alert['target_price'],
                        'type': 'SATIŞ FIRSATI',
                        'message': f"{crypto_id.upper()} hedef fiyatı aştı! Satış zamanı olabilir."
                    })
                elif alert['alert_type'] == 'below' and current_price <= alert['target_price']:
                    triggered_alerts.append({
                        'crypto': crypto_id,
                        'current_price': current_price,
                        'target_price': alert['target_price'],
                        'type': 'ALIM FIRSATI',
                        'message': f"{crypto_id.upper()} hedef fiyatın altına düştü! Alım zamanı olabilir."
                    })

        return triggered_alerts

    def find_arbitrage_opportunities(self, min_volume: float = 1000000) -> List[Dict]:
        """Arbitraj fırsatlarını bul (farklı borsalar arası fiyat farkları)"""
        # Basit bir volatilite ve hacim analizi
        opportunities = []
        top_coins = ['bitcoin', 'ethereum', 'cardano', 'solana', 'polkadot']

        for coin in top_coins:
            price_data = self.get_crypto_price(coin)
            if price_data and abs(price_data['change_24h']) > 5:  # %5'ten fazla değişim
                opportunities.append({
                    'coin': coin,
                    'price': price_data['usd'],
                    'change': price_data['change_24h'],
                    'recommendation': 'AL' if price_data['change_24h'] < -5 else 'SAT'
                })

        return opportunities

    def generate_trading_report(self, cryptocurrencies: List[str] = None) -> str:
        """Trading raporu oluştur"""
        if cryptocurrencies is None:
            cryptocurrencies = ['bitcoin', 'ethereum', 'binancecoin', 'cardano', 'solana']

        report = f"\n{'='*80}\n"
        report += f"KRİPTO PARA TRADİNG RAPORU - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        report += f"{'='*80}\n\n"

        # En çok yükselenler
        report += "🚀 EN ÇOK YÜKSELENLER (Satış Fırsatları):\n"
        report += "-" * 80 + "\n"
        gainers = self.get_top_gainers(5)
        for i, coin in enumerate(gainers, 1):
            report += f"{i}. {coin['name']} ({coin['symbol']})\n"
            report += f"   Fiyat: ${coin['price']:,.2f} | Değişim: +{coin['change_24h']:.2f}%\n"
            report += f"   Hacim: ${coin['volume']:,.0f} | Piyasa Değeri: ${coin['market_cap']:,.0f}\n\n"

        # En çok düşenler
        report += "\n📉 EN ÇOK DÜŞENLER (Alım Fırsatları):\n"
        report += "-" * 80 + "\n"
        losers = self.get_top_losers(5)
        for i, coin in enumerate(losers, 1):
            report += f"{i}. {coin['name']} ({coin['symbol']})\n"
            report += f"   Fiyat: ${coin['price']:,.2f} | Değişim: {coin['change_24h']:.2f}%\n"
            report += f"   Hacim: ${coin['volume']:,.0f} | Piyasa Değeri: ${coin['market_cap']:,.0f}\n\n"

        # Detaylı analiz
        report += "\n📊 DETAYLI ANALİZ:\n"
        report += "-" * 80 + "\n"
        for crypto in cryptocurrencies:
            price_data = self.get_crypto_price(crypto)
            if price_data:
                report += f"\n{crypto.upper()}:\n"
                report += f"  USD: ${price_data['usd']:,.2f}\n"
                report += f"  TRY: ₺{price_data['try']:,.2f}\n"
                report += f"  24s Değişim: {price_data['change_24h']:.2f}%\n"

                # Trading tavsiyesi
                if price_data['change_24h'] > 10:
                    report += f"  ⚠️  TAVSİYE: Kâr realizasyonu düşünülebilir (yüksek artış)\n"
                elif price_data['change_24h'] < -10:
                    report += f"  💰 TAVSİYE: Alım fırsatı olabilir (düşük fiyat)\n"
                else:
                    report += f"  📊 TAVSİYE: Bekle ve gözle (normal dalgalanma)\n"

        report += "\n" + "="*80 + "\n"
        report += "⚠️  UYARI: Bu rapor yalnızca bilgilendirme amaçlıdır. Yatırım tavsiyesi değildir.\n"
        report += "="*80 + "\n"

        return report

    def monitor_continuously(self, interval: int = 60, cryptocurrencies: List[str] = None):
        """Sürekli fiyat izleme (interval: saniye)"""
        print(f"🔄 Sürekli izleme başlatıldı (Her {interval} saniyede bir güncelleme)\n")
        print("Durdurmak için Ctrl+C'ye basın\n")

        if cryptocurrencies is None:
            cryptocurrencies = ['bitcoin', 'ethereum', 'binancecoin']

        try:
            while True:
                print(f"\n{'='*80}")
                print(f"Güncelleme Zamanı: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                print(f"{'='*80}\n")

                for crypto in cryptocurrencies:
                    price_data = self.get_crypto_price(crypto)
                    if price_data:
                        emoji = "🟢" if price_data['change_24h'] > 0 else "🔴"
                        print(f"{emoji} {crypto.upper():<12} | ${price_data['usd']:>12,.2f} | "
                              f"₺{price_data['try']:>12,.2f} | "
                              f"{price_data['change_24h']:>+7.2f}%")

                # Alarmları kontrol et
                triggered = self.check_alerts()
                if triggered:
                    print("\n🔔 ALARM! TRADİNG FIRSATLARI:")
                    for alert in triggered:
                        print(f"  ⚡ {alert['message']}")
                        print(f"     Mevcut: ${alert['current_price']:,.2f} | Hedef: ${alert['target_price']:,.2f}")

                time.sleep(interval)

        except KeyboardInterrupt:
            print("\n\n✓ İzleme durduruldu.")


def main():
    """Ana program"""
    monitor = CryptoPriceMonitor()

    print("""
    ╔══════════════════════════════════════════════════════════════╗
    ║       KRİPTO PARA FİYAT İZLEME VE ALARM SİSTEMİ            ║
    ║                  Para Kazanma Aracı #1                      ║
    ╚══════════════════════════════════════════════════════════════╝
    """)

    # Örnek alarmlar ayarla
    print("\n📋 Örnek alarmlar ayarlanıyor...\n")
    monitor.set_price_alert('bitcoin', 100000, 'above')  # Bitcoin $100k üstüne çıkarsa
    monitor.set_price_alert('ethereum', 3000, 'below')    # Ethereum $3000 altına düşerse

    # Trading raporu oluştur
    report = monitor.generate_trading_report()
    print(report)

    # Raporu kaydet
    with open('crypto_trading_report.txt', 'w', encoding='utf-8') as f:
        f.write(report)
    print("\n✓ Rapor 'crypto_trading_report.txt' dosyasına kaydedildi.\n")

    # Sürekli izleme başlat
    choice = input("Sürekli fiyat izlemeyi başlatmak ister misiniz? (e/h): ")
    if choice.lower() == 'e':
        monitor.monitor_continuously(interval=30)  # 30 saniyede bir güncelle


if __name__ == "__main__":
    main()
