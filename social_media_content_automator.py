#!/usr/bin/env python3
"""
Otomatik İçerik Üretici ve Sosyal Medya Planlayıcı
Sosyal medya içerikleri oluşturur, planlar ve yayınlar
Para kazanma stratejisi: Sosyal medya yönetimi hizmeti, affiliate marketing, sponsorlu içerik
"""

import json
import random
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import sqlite3
from dataclasses import dataclass, asdict
import hashlib
import os

@dataclass
class ContentPost:
    id: str
    platform: str
    content: str
    hashtags: List[str]
    scheduled_time: datetime
    status: str = "pending"  # pending, published, failed
    engagement_score: float = 0.0
    category: str = ""
    image_prompt: Optional[str] = None

class SocialMediaContentAutomator:
    def __init__(self):
        self.db_name = "social_media_content.db"
        self.init_database()

        # İçerik şablonları
        self.content_templates = {
            'motivation': [
                "🌟 Başarı, küçük çabaların tekrarıdır. Her gün biraz daha ileri! #motivasyon",
                "💪 Hedefinize odaklanın, süreç kendini gösterir. #başarı",
                "✨ Bugün, dünün hayalini kuranın bugünü. Harekete geç! #ilham",
                "🎯 Başarı bir gece olmuyor, ama her gece ona bir adım daha yaklaşıyorsun. #azim",
            ],
            'business': [
                "💼 E-ticarette başarının sırrı: Doğru ürün + Doğru fiyat + Harika hizmet #eticaret",
                "📊 Pazarlama stratejinizi gözden geçirin. Veriler size yolu gösterir. #dijitalpazarlama",
                "🚀 Startup kurmak isteyenlere: Başlamak için mükemmel anı beklemeyin. #girisimcilik",
                "💡 İnovasyonun anahtarı: Müşteri sorunlarını dinlemek ve çözmek. #inovasyon",
            ],
            'tech': [
                "🤖 Yapay zeka sadece gelecek değil, şimdi. İşinize nasıl entegre edebilirsiniz? #ai",
                "💻 Yazılım öğrenmek isteyenlere: Python ile başlayın, sınır yoktur. #kodlama",
                "🔐 Siber güvenlik 2024'te daha kritik. Şifrenizi son ne zaman değiştirdiniz? #guvenlik",
                "📱 Mobil uygulamanız var mı? Yoksa müşterilerinizin %60'ını kaybediyorsunuz. #mobiluygulama",
            ],
            'finance': [
                "💰 Pasif gelir akışları oluşturmanın 5 yolu [Link] #pasifgelir",
                "📈 Borsaya yatırım yapmadan önce bilmeniz gerekenler. #yatirim",
                "💳 Finansal özgürlüğe giden yol: Gelir - Gider = Tasarruf + Yatırım #finans",
                "🏦 Kripto para portföy çeşitlendirmesi neden önemli? #kripto",
            ],
            'lifestyle': [
                "☕ Sabah rutininiz gününüzü belirler. Siz nasıl başlıyorsunuz? #yasam",
                "🧘 Mental sağlık fiziksel sağlık kadar önemli. Kendinize zaman ayırın. #wellness",
                "📚 Bu ay okumanız gereken 3 kitap [Liste] #kitap",
                "🎨 Yaratıcılığınızı artırmanın bilimsel yolları. #yaraticilik",
            ]
        }

        # Popüler hashtag'ler
        self.popular_hashtags = {
            'general': ['#keşfet', '#viral', '#trending', '#takipçi', '#sosyalmedya'],
            'business': ['#girişimci', '#iş', '#başarı', '#para', '#kazanç'],
            'tech': ['#teknoloji', '#yazılım', '#yapayZeka', '#inovasyon', '#dijital'],
            'finance': ['#finans', '#yatırım', '#borsa', '#kripto', '#paraKazanma']
        }

        # En iyi paylaşım saatleri (saat bazında)
        self.best_posting_times = {
            'Instagram': [9, 12, 18, 21],
            'Twitter': [8, 12, 17, 20],
            'LinkedIn': [7, 12, 17, 18],
            'Facebook': [9, 13, 15, 19],
            'TikTok': [6, 10, 19, 22]
        }

    def init_database(self):
        """Veritabanını başlat"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS posts (
                id TEXT PRIMARY KEY,
                platform TEXT,
                content TEXT,
                hashtags TEXT,
                scheduled_time DATETIME,
                status TEXT,
                engagement_score REAL,
                category TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS analytics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                post_id TEXT,
                likes INTEGER DEFAULT 0,
                comments INTEGER DEFAULT 0,
                shares INTEGER DEFAULT 0,
                views INTEGER DEFAULT 0,
                click_through_rate REAL DEFAULT 0.0,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (post_id) REFERENCES posts(id)
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS content_ideas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                category TEXT,
                idea TEXT,
                keywords TEXT,
                potential_score REAL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        conn.commit()
        conn.close()

    def generate_post_id(self, content: str) -> str:
        """Benzersiz post ID oluştur"""
        timestamp = datetime.now().isoformat()
        unique_string = f"{content}{timestamp}"
        return hashlib.md5(unique_string.encode()).hexdigest()[:12]

    def generate_content(self, category: str, count: int = 5) -> List[str]:
        """Belirli bir kategoride içerik oluştur"""
        if category not in self.content_templates:
            category = random.choice(list(self.content_templates.keys()))

        templates = self.content_templates[category]
        return random.sample(templates, min(count, len(templates)))

    def generate_trending_hashtags(self, category: str, count: int = 5) -> List[str]:
        """Trending hashtag'ler oluştur"""
        category_tags = self.popular_hashtags.get(category, self.popular_hashtags['general'])
        general_tags = self.popular_hashtags['general']

        all_tags = list(set(category_tags + general_tags))
        return random.sample(all_tags, min(count, len(all_tags)))

    def create_content_post(self, platform: str, category: str,
                          custom_content: Optional[str] = None,
                          scheduled_time: Optional[datetime] = None) -> ContentPost:
        """İçerik postu oluştur"""
        if custom_content:
            content = custom_content
        else:
            content = self.generate_content(category, 1)[0]

        hashtags = self.generate_trending_hashtags(category, 5)
        post_id = self.generate_post_id(content)

        if not scheduled_time:
            # En iyi paylaşım saatini seç
            best_hours = self.best_posting_times.get(platform, [9, 12, 18])
            next_hour = random.choice(best_hours)
            scheduled_time = datetime.now().replace(hour=next_hour, minute=0, second=0)

            # Gelecekteki bir zamana ayarla
            if scheduled_time <= datetime.now():
                scheduled_time += timedelta(days=1)

        # Görsel prompt oluştur
        image_prompt = self.generate_image_prompt(category)

        post = ContentPost(
            id=post_id,
            platform=platform,
            content=content,
            hashtags=hashtags,
            scheduled_time=scheduled_time,
            category=category,
            image_prompt=image_prompt
        )

        return post

    def generate_image_prompt(self, category: str) -> str:
        """Görsel oluşturma için AI prompt oluştur"""
        prompts = {
            'motivation': "Inspirational sunrise over mountains, vibrant colors, professional photography",
            'business': "Modern office workspace, minimalist design, professional setting",
            'tech': "Futuristic technology, digital interface, blue and purple tones",
            'finance': "Financial charts and graphs, stock market, professional business theme",
            'lifestyle': "Aesthetic lifestyle flat lay, natural lighting, instagram style"
        }
        return prompts.get(category, "Professional social media post background")

    def create_content_calendar(self, days: int = 7, posts_per_day: int = 3,
                               platforms: List[str] = None) -> List[ContentPost]:
        """İçerik takvimi oluştur"""
        if platforms is None:
            platforms = ['Instagram', 'Twitter', 'LinkedIn']

        calendar = []
        categories = list(self.content_templates.keys())

        for day in range(days):
            for post_num in range(posts_per_day):
                platform = random.choice(platforms)
                category = random.choice(categories)

                # Zamanlamayı ayarla
                base_time = datetime.now() + timedelta(days=day)
                best_hours = self.best_posting_times.get(platform, [9, 12, 18])
                hour = best_hours[post_num % len(best_hours)]
                scheduled_time = base_time.replace(hour=hour, minute=0, second=0)

                post = self.create_content_post(platform, category, scheduled_time=scheduled_time)
                calendar.append(post)

        return calendar

    def save_post(self, post: ContentPost):
        """Postu veritabanına kaydet"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO posts
            (id, platform, content, hashtags, scheduled_time, status, engagement_score, category)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            post.id,
            post.platform,
            post.content,
            ','.join(post.hashtags),
            post.scheduled_time.isoformat(),
            post.status,
            post.engagement_score,
            post.category
        ))
        conn.commit()
        conn.close()

    def get_scheduled_posts(self, days: int = 7) -> List[ContentPost]:
        """Planlanmış postları getir"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()

        start_date = datetime.now()
        end_date = start_date + timedelta(days=days)

        cursor.execute('''
            SELECT id, platform, content, hashtags, scheduled_time, status,
                   engagement_score, category
            FROM posts
            WHERE scheduled_time BETWEEN ? AND ?
            ORDER BY scheduled_time
        ''', (start_date.isoformat(), end_date.isoformat()))

        posts = []
        for row in cursor.fetchall():
            post = ContentPost(
                id=row[0],
                platform=row[1],
                content=row[2],
                hashtags=row[3].split(',') if row[3] else [],
                scheduled_time=datetime.fromisoformat(row[4]),
                status=row[5],
                engagement_score=row[6],
                category=row[7]
            )
            posts.append(post)

        conn.close()
        return posts

    def generate_content_ideas(self, niche: str, count: int = 10) -> List[Dict]:
        """Belirli bir niş için içerik fikirleri oluştur"""
        ideas_database = {
            'ecommerce': [
                "Satışları artıran 10 ürün açıklaması örneği",
                "Müşteri yorumlarını nasıl artırırsınız?",
                "Dropshipping ile ilk ayda ne kadar kazanılır?",
                "En çok satan ürün kategorileri 2024",
                "Abandoned cart'ları kurtarmanın 5 yolu",
            ],
            'crypto': [
                "Başlangıç için en iyi 5 kripto para",
                "Kripto cüzdan güvenliği rehberi",
                "Staking ile pasif gelir nasıl elde edilir?",
                "DeFi nedir ve nasıl kullanılır?",
                "NFT oluşturma ve satma rehberi",
            ],
            'affiliate': [
                "Affiliate marketing ile ilk 1000$ nasıl kazanılır",
                "En yüksek komisyon veren programlar",
                "Instagram'da affiliate satış stratejileri",
                "Amazon Associates başarı hikayeleri",
                "Email marketing ile affiliate gelir artırma",
            ],
            'freelance': [
                "Freelance olarak ilk müşterinizi bulma",
                "Upwork profil optimizasyonu",
                "Saatlik ücretinizi nasıl belirlersiniz?",
                "Freelance yazarlar için niş seçimi",
                "Passive income için dijital ürünler",
            ]
        }

        ideas = ideas_database.get(niche, ideas_database['ecommerce'])
        selected_ideas = random.sample(ideas, min(count, len(ideas)))

        return [
            {
                'idea': idea,
                'category': niche,
                'keywords': self.extract_keywords(idea),
                'potential_score': random.uniform(6.5, 9.5)
            }
            for idea in selected_ideas
        ]

    def extract_keywords(self, text: str) -> List[str]:
        """Metinden anahtar kelimeler çıkar"""
        # Basit keyword extraction
        common_words = ['ile', 'için', 'nasıl', 've', 'bir', 'ne', 'kadar', 'en']
        words = text.lower().split()
        keywords = [w for w in words if w not in common_words and len(w) > 3]
        return keywords[:5]

    def generate_report(self, calendar: List[ContentPost]) -> str:
        """İçerik takvimi raporu oluştur"""
        report = f"\n{'='*100}\n"
        report += f"SOSYAL MEDYA İÇERİK TAKVİMİ - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        report += f"{'='*100}\n\n"

        report += f"📊 ÖZET:\n"
        report += f"   Toplam Post Sayısı: {len(calendar)}\n"

        # Platform dağılımı
        platforms = {}
        categories = {}
        for post in calendar:
            platforms[post.platform] = platforms.get(post.platform, 0) + 1
            categories[post.category] = categories.get(post.category, 0) + 1

        report += f"\n   Platform Dağılımı:\n"
        for platform, count in sorted(platforms.items(), key=lambda x: x[1], reverse=True):
            report += f"      • {platform}: {count} post\n"

        report += f"\n   Kategori Dağılımı:\n"
        for category, count in sorted(categories.items(), key=lambda x: x[1], reverse=True):
            report += f"      • {category}: {count} post\n"

        # Günlük plan
        report += f"\n\n{'─'*100}\n"
        report += "📅 GÜNLÜK İÇERİK PLANI:\n"
        report += f"{'─'*100}\n"

        current_date = None
        for post in sorted(calendar, key=lambda x: x.scheduled_time):
            post_date = post.scheduled_time.date()

            if post_date != current_date:
                current_date = post_date
                report += f"\n📆 {post.scheduled_time.strftime('%d %B %Y, %A')}\n"
                report += "─" * 100 + "\n"

            report += f"\n⏰ {post.scheduled_time.strftime('%H:%M')} - {post.platform}\n"
            report += f"   📝 {post.content}\n"
            report += f"   🏷️  {' '.join(post.hashtags[:3])}\n"
            report += f"   🎨 Görsel: {post.image_prompt}\n"

        report += f"\n\n{'='*100}\n"
        report += "💡 İÇERİK ÜRETİMİ ÖNERİLERİ:\n"
        report += "   • Görselleri Canva veya Adobe Spark ile oluşturun\n"
        report += "   • Video içerikler için CapCut veya InShot kullanın\n"
        report += "   • Hashtag performansını Analytics ile takip edin\n"
        report += "   • Engagement artırmak için stories kullanın\n"
        report += "   • Her post için CTÇ (Call-to-Action) ekleyin\n"
        report += f"{'='*100}\n"

        report += "\n\n💰 GELİR FIRSATLARI:\n"
        report += "   1. Sponsorlu içerik anlaşmaları (Marka işbirlikleri)\n"
        report += "   2. Affiliate ürün tanıtımları (Komisyon geliri)\n"
        report += "   3. Dijital ürün satışı (E-kitap, kurs, template)\n"
        report += "   4. Danışmanlık hizmetleri (Sosyal medya yönetimi)\n"
        report += "   5. Premium içerik abonelikleri (Patreon, OnlyFans)\n"
        report += f"{'='*100}\n"

        return report

    def export_to_json(self, calendar: List[ContentPost], filename: str = "content_calendar.json"):
        """Takvimi JSON'a aktar"""
        calendar_data = []
        for post in calendar:
            post_dict = asdict(post)
            post_dict['scheduled_time'] = post.scheduled_time.isoformat()
            calendar_data.append(post_dict)

        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(calendar_data, f, ensure_ascii=False, indent=2)

        print(f"✓ İçerik takvimi '{filename}' dosyasına aktarıldı.")


def main():
    """Ana program"""
    automator = SocialMediaContentAutomator()

    print("""
    ╔══════════════════════════════════════════════════════════════════╗
    ║       OTOMATİK İÇERİK ÜRETİCİ VE SOSYAL MEDYA PLANLAVICI       ║
    ║                   Para Kazanma Aracı #3                         ║
    ║                                                                  ║
    ║  • İçerik takvimi oluşturur                                    ║
    ║  • En iyi paylaşım saatlerini belirler                        ║
    ║  • Trending hashtag'ler önerir                                ║
    ║  • Görsel promptları oluşturur                                ║
    ╚══════════════════════════════════════════════════════════════════╝
    """)

    # Kullanıcı seçenekleri
    print("\n📱 PLATFORM SEÇENEKLERİ:")
    platforms = ['Instagram', 'Twitter', 'LinkedIn', 'Facebook', 'TikTok']
    for i, platform in enumerate(platforms, 1):
        print(f"   {i}. {platform}")

    print("\n📋 KATEGORİ SEÇENEKLERİ:")
    categories = list(automator.content_templates.keys())
    for i, category in enumerate(categories, 1):
        print(f"   {i}. {category.capitalize()}")

    # İçerik takvimi oluştur
    print("\n" + "="*70)
    print("📅 İçerik takvimi oluşturuluyor...\n")

    # 30 günlük içerik planı
    calendar = automator.create_content_calendar(
        days=30,
        posts_per_day=3,
        platforms=['Instagram', 'Twitter', 'LinkedIn']
    )

    # Postları kaydet
    for post in calendar:
        automator.save_post(post)

    print(f"✓ {len(calendar)} adet post oluşturuldu ve veritabanına kaydedildi.\n")

    # Rapor oluştur
    report = automator.generate_report(calendar)
    print(report)

    # Raporu kaydet
    report_file = f"social_media_calendar_{datetime.now().strftime('%Y%m%d')}.txt"
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(report)
    print(f"\n✓ Rapor '{report_file}' dosyasına kaydedildi.")

    # JSON'a aktar
    automator.export_to_json(calendar)

    # İçerik fikirleri oluştur
    print("\n\n💡 İÇERİK FİKİRLERİ (Para Kazanma Nişleri):\n")
    niches = ['ecommerce', 'crypto', 'affiliate', 'freelance']

    for niche in niches:
        ideas = automator.generate_content_ideas(niche, 3)
        print(f"\n🎯 {niche.upper()}:")
        for i, idea in enumerate(ideas, 1):
            print(f"   {i}. {idea['idea']}")
            print(f"      Potansiyel Skor: {idea['potential_score']:.1f}/10")

    print("\n\n" + "="*70)
    print("✅ İçerik otomasyonu tamamlandı!")
    print("="*70 + "\n")


if __name__ == "__main__":
    main()
