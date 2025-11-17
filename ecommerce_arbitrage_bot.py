#!/usr/bin/env python3
"""
E-Ticaret Fiyat Karşılaştırma ve Arbitraj Botu
Amazon, eBay, AliExpress gibi platformlardaki fiyat farklarını bulur
Para kazanma stratejisi: Düşük fiyattan al, yüksek fiyattan sat (Dropshipping/Reselling)
"""

import requests
from bs4 import BeautifulSoup
import json
import time
from datetime import datetime
from typing import List, Dict, Optional
import re
from urllib.parse import quote_plus
import sqlite3
from dataclasses import dataclass
import csv

@dataclass
class Product:
    name: str
    price: float
    platform: str
    url: str
    currency: str = "USD"
    shipping: float = 0.0
    rating: Optional[float] = None
    reviews: Optional[int] = None
    availability: str = "In Stock"

class EcommerceArbitrageBot:
    def __init__(self):
        self.db_name = "arbitrage_opportunities.db"
        self.init_database()
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        self.min_profit_margin = 0.20  # Minimum %20 kar marjı

    def init_database(self):
        """Veritabanını başlat"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS opportunities (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                product_name TEXT,
                buy_platform TEXT,
                buy_price REAL,
                sell_platform TEXT,
                sell_price REAL,
                profit_margin REAL,
                profit_amount REAL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                status TEXT DEFAULT 'new'
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS price_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                product_name TEXT,
                platform TEXT,
                price REAL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        conn.commit()
        conn.close()

    def search_amazon(self, query: str) -> List[Product]:
        """Amazon'da ürün ara (Örnek - gerçek kullanım için Amazon API gerekir)"""
        # NOT: Amazon gerçek scraping için API key gerektirir
        # Bu bir örnek yapıdır
        print(f"  🔍 Amazon'da aranıyor: {query}")

        # Simüle edilmiş sonuçlar (Gerçek uygulamada Amazon Product Advertising API kullanın)
        sample_products = [
            Product(
                name=f"{query} - Premium Quality",
                price=29.99,
                platform="Amazon",
                url=f"https://amazon.com/s?k={quote_plus(query)}",
                rating=4.5,
                reviews=1234
            ),
            Product(
                name=f"{query} - Best Seller",
                price=34.99,
                platform="Amazon",
                url=f"https://amazon.com/s?k={quote_plus(query)}",
                rating=4.7,
                reviews=5678
            )
        ]
        return sample_products

    def search_ebay(self, query: str) -> List[Product]:
        """eBay'de ürün ara (Örnek - gerçek kullanım için eBay API gerekir)"""
        print(f"  🔍 eBay'de aranıyor: {query}")

        # Simüle edilmiş sonuçlar (Gerçek uygulamada eBay Finding API kullanın)
        sample_products = [
            Product(
                name=f"{query} - Used Like New",
                price=22.50,
                platform="eBay",
                url=f"https://ebay.com/sch/i.html?_nkw={quote_plus(query)}",
                rating=4.2,
                reviews=234
            ),
            Product(
                name=f"{query} - Brand New Sealed",
                price=27.99,
                platform="eBay",
                url=f"https://ebay.com/sch/i.html?_nkw={quote_plus(query)}",
                rating=4.6,
                reviews=789
            )
        ]
        return sample_products

    def search_aliexpress(self, query: str) -> List[Product]:
        """AliExpress'de ürün ara"""
        print(f"  🔍 AliExpress'de aranıyor: {query}")

        # Simüle edilmiş sonuçlar (Gerçek uygulamada AliExpress API kullanın)
        sample_products = [
            Product(
                name=f"{query} - Wholesale",
                price=8.99,
                platform="AliExpress",
                url=f"https://aliexpress.com/wholesale?SearchText={quote_plus(query)}",
                shipping=2.50,
                rating=4.3,
                reviews=456
            ),
            Product(
                name=f"{query} - Factory Direct",
                price=12.50,
                platform="AliExpress",
                url=f"https://aliexpress.com/wholesale?SearchText={quote_plus(query)}",
                shipping=3.00,
                rating=4.4,
                reviews=890
            )
        ]
        return sample_products

    def search_trendyol(self, query: str) -> List[Product]:
        """Trendyol'da ürün ara"""
        print(f"  🔍 Trendyol'da aranıyor: {query}")

        # Simüle edilmiş sonuçlar
        sample_products = [
            Product(
                name=f"{query} - Hızlı Kargo",
                price=450.00,  # TRY
                platform="Trendyol",
                url=f"https://trendyol.com/sr?q={quote_plus(query)}",
                currency="TRY",
                rating=4.1,
                reviews=123
            ),
            Product(
                name=f"{query} - Çok Satan",
                price=520.00,
                platform="Trendyol",
                url=f"https://trendyol.com/sr?q={quote_plus(query)}",
                currency="TRY",
                rating=4.5,
                reviews=678
            )
        ]
        return sample_products

    def search_all_platforms(self, query: str) -> Dict[str, List[Product]]:
        """Tüm platformlarda ara"""
        print(f"\n🔎 Ürün aranıyor: '{query}'\n")

        results = {
            'Amazon': self.search_amazon(query),
            'eBay': self.search_ebay(query),
            'AliExpress': self.search_aliexpress(query),
            'Trendyol': self.search_trendyol(query)
        }

        time.sleep(1)  # Rate limiting
        return results

    def calculate_profit(self, buy_price: float, sell_price: float,
                        shipping_cost: float = 0, fees_percent: float = 0.15) -> Dict:
        """Kar hesapla"""
        total_cost = buy_price + shipping_cost
        selling_fees = sell_price * fees_percent  # Platform ücretleri (%15)
        net_profit = sell_price - total_cost - selling_fees
        profit_margin = (net_profit / sell_price) * 100 if sell_price > 0 else 0

        return {
            'total_cost': total_cost,
            'selling_fees': selling_fees,
            'net_profit': net_profit,
            'profit_margin': profit_margin
        }

    def find_arbitrage_opportunities(self, query: str,
                                    min_profit_margin: float = 20.0) -> List[Dict]:
        """Arbitraj fırsatlarını bul"""
        all_products = self.search_all_platforms(query)
        opportunities = []

        # Tüm kombinasyonları kontrol et
        for buy_platform, buy_products in all_products.items():
            for sell_platform, sell_products in all_products.items():
                if buy_platform == sell_platform:
                    continue

                for buy_product in buy_products:
                    for sell_product in sell_products:
                        # Fiyatları normalize et (USD'ye çevir)
                        buy_price_usd = buy_product.price
                        if buy_product.currency == "TRY":
                            buy_price_usd = buy_product.price / 34.0  # Örnek kur

                        sell_price_usd = sell_product.price
                        if sell_product.currency == "TRY":
                            sell_price_usd = sell_product.price / 34.0

                        profit_calc = self.calculate_profit(
                            buy_price_usd,
                            sell_price_usd,
                            buy_product.shipping
                        )

                        if profit_calc['profit_margin'] >= min_profit_margin:
                            opportunity = {
                                'product_name': buy_product.name,
                                'buy_from': buy_platform,
                                'buy_price': buy_product.price,
                                'buy_currency': buy_product.currency,
                                'buy_url': buy_product.url,
                                'sell_on': sell_platform,
                                'sell_price': sell_product.price,
                                'sell_currency': sell_product.currency,
                                'sell_url': sell_product.url,
                                'profit_margin': profit_calc['profit_margin'],
                                'net_profit': profit_calc['net_profit'],
                                'total_cost': profit_calc['total_cost']
                            }
                            opportunities.append(opportunity)

        # Kar marjına göre sırala
        opportunities.sort(key=lambda x: x['profit_margin'], reverse=True)
        return opportunities

    def save_opportunity(self, opportunity: Dict):
        """Fırsatı veritabanına kaydet"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO opportunities
            (product_name, buy_platform, buy_price, sell_platform, sell_price,
             profit_margin, profit_amount)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            opportunity['product_name'],
            opportunity['buy_from'],
            opportunity['buy_price'],
            opportunity['sell_on'],
            opportunity['sell_price'],
            opportunity['profit_margin'],
            opportunity['net_profit']
        ))
        conn.commit()
        conn.close()

    def generate_arbitrage_report(self, opportunities: List[Dict]) -> str:
        """Arbitraj raporu oluştur"""
        report = f"\n{'='*100}\n"
        report += f"E-TİCARET ARBİTRAJ FIRSATLARI RAPORU - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        report += f"{'='*100}\n\n"

        if not opportunities:
            report += "❌ Belirlenen kar marjı kriterlerine uygun fırsat bulunamadı.\n"
            return report

        report += f"✓ Toplam {len(opportunities)} adet kârlı fırsat bulundu!\n\n"

        for i, opp in enumerate(opportunities[:10], 1):  # En iyi 10'u göster
            report += f"\n{'─'*100}\n"
            report += f"FIRSAT #{i} - KAR MARJI: %{opp['profit_margin']:.1f}\n"
            report += f"{'─'*100}\n"
            report += f"📦 Ürün: {opp['product_name'][:60]}\n\n"

            report += f"💰 ALIM BİLGİLERİ:\n"
            report += f"   Platform: {opp['buy_from']}\n"
            report += f"   Fiyat: {opp['buy_price']:.2f} {opp['buy_currency']}\n"
            report += f"   Link: {opp['buy_url']}\n\n"

            report += f"💵 SATIŞ BİLGİLERİ:\n"
            report += f"   Platform: {opp['sell_on']}\n"
            report += f"   Fiyat: {opp['sell_price']:.2f} {opp['sell_currency']}\n"
            report += f"   Link: {opp['sell_url']}\n\n"

            report += f"📊 KAR ANALİZİ:\n"
            report += f"   Net Kar: ${opp['net_profit']:.2f}\n"
            report += f"   Kar Marjı: %{opp['profit_margin']:.1f}\n"
            report += f"   Toplam Maliyet: ${opp['total_cost']:.2f}\n\n"

            report += f"🎯 STRATEJİ:\n"
            report += f"   1. {opp['buy_from']}'dan satın al: {opp['buy_price']:.2f} {opp['buy_currency']}\n"
            report += f"   2. {opp['sell_on']}'da sat: {opp['sell_price']:.2f} {opp['sell_currency']}\n"
            report += f"   3. Kar: ${opp['net_profit']:.2f} (%{opp['profit_margin']:.1f})\n"

        report += f"\n{'='*100}\n"
        report += "💡 ÖNERİLER:\n"
        report += "   • Ürünleri satın almadan önce stok durumunu kontrol edin\n"
        report += "   • Nakliye sürelerini hesaba katın\n"
        report += "   • İade politikalarını inceleyin\n"
        report += "   • Küçük miktarlarla test edin\n"
        report += "   • Platform ücretlerini ve vergileri unutmayın\n"
        report += f"{'='*100}\n"

        return report

    def export_to_csv(self, opportunities: List[Dict], filename: str = "arbitrage_opportunities.csv"):
        """Fırsatları CSV'ye aktar"""
        if not opportunities:
            print("❌ Dışa aktarılacak fırsat yok.")
            return

        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['Sıra', 'Ürün', 'Alım Platform', 'Alım Fiyat',
                         'Satış Platform', 'Satış Fiyat', 'Kar Marjı %', 'Net Kar $']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            writer.writeheader()
            for i, opp in enumerate(opportunities, 1):
                writer.writerow({
                    'Sıra': i,
                    'Ürün': opp['product_name'][:50],
                    'Alım Platform': opp['buy_from'],
                    'Alım Fiyat': f"{opp['buy_price']:.2f} {opp['buy_currency']}",
                    'Satış Platform': opp['sell_on'],
                    'Satış Fiyat': f"{opp['sell_price']:.2f} {opp['sell_currency']}",
                    'Kar Marjı %': f"{opp['profit_margin']:.1f}",
                    'Net Kar $': f"{opp['net_profit']:.2f}"
                })

        print(f"✓ Fırsatlar '{filename}' dosyasına aktarıldı.")

    def monitor_products(self, product_queries: List[str], interval: int = 3600):
        """Ürünleri sürekli izle"""
        print(f"\n🔄 Sürekli izleme başlatıldı (Her {interval//60} dakikada bir)\n")

        try:
            while True:
                for query in product_queries:
                    opportunities = self.find_arbitrage_opportunities(query)

                    if opportunities:
                        print(f"\n🎯 '{query}' için {len(opportunities)} fırsat bulundu!")

                        # En iyi 3'ü göster
                        for opp in opportunities[:3]:
                            print(f"   💰 {opp['buy_from']} → {opp['sell_on']}: "
                                  f"%{opp['profit_margin']:.1f} kar")
                            self.save_opportunity(opp)

                time.sleep(interval)

        except KeyboardInterrupt:
            print("\n\n✓ İzleme durduruldu.")


def main():
    """Ana program"""
    bot = EcommerceArbitrageBot()

    print("""
    ╔══════════════════════════════════════════════════════════════════╗
    ║      E-TİCARET FİYAT KARŞILAŞTIRMA VE ARBİTRAJ BOTU            ║
    ║                   Para Kazanma Aracı #2                         ║
    ║                                                                  ║
    ║  Farklı platformlar arasında fiyat farkları bulur              ║
    ║  Dropshipping ve Reselling için ideal!                         ║
    ╚══════════════════════════════════════════════════════════════════╝
    """)

    # Örnek ürün aramaları
    sample_products = [
        "wireless earbuds",
        "smart watch",
        "phone case",
        "laptop stand",
        "bluetooth speaker"
    ]

    print("\n🎯 ÖNERİLEN ÜRÜN KATEGORİLERİ:")
    for i, product in enumerate(sample_products, 1):
        print(f"   {i}. {product}")

    # Kullanıcıdan ürün seç
    print("\n" + "="*70)
    choice = input("Aramak istediğiniz ürünü girin (veya Enter'a basın): ").strip()

    if not choice:
        choice = sample_products[0]  # Varsayılan

    print(f"\n🔍 '{choice}' için arbitraj fırsatları aranıyor...\n")

    # Fırsatları bul
    opportunities = bot.find_arbitrage_opportunities(choice, min_profit_margin=15.0)

    # Rapor oluştur
    report = bot.generate_arbitrage_report(opportunities)
    print(report)

    # Raporu kaydet
    if opportunities:
        report_file = f"arbitrage_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report)
        print(f"\n✓ Rapor '{report_file}' dosyasına kaydedildi.")

        # CSV'ye aktar
        bot.export_to_csv(opportunities)

        # Fırsatları veritabanına kaydet
        for opp in opportunities:
            bot.save_opportunity(opp)
        print(f"✓ {len(opportunities)} fırsat veritabanına kaydedildi.\n")


if __name__ == "__main__":
    main()
