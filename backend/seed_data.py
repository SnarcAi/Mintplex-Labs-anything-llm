"""
Seed database with initial data (products, demo users).
"""
import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import AsyncSessionLocal
from app.core.security import get_password_hash
from app.models.user import User, GrillLevel
from app.models.product import ShopProduct, ProductCategory


async def seed_products(db: AsyncSession):
    """Seed shop products."""
    products = [
        ShopProduct(
            name="MissYak Pro Grill",
            description="Premium bioethanol grill with stainless steel finish. Perfect for balconies and terraces. No smoke, no ash, just pure grilling pleasure.",
            image_url="https://placehold.co/600x400/1a1a1a/ffffff?text=MissYak+Pro+Grill",
            price=2499.00,
            currency="TRY",
            category=ProductCategory.GRILL,
            external_url="https://missyak.com/products/pro-grill",
            is_active=True,
        ),
        ShopProduct(
            name="MissYak Mini Grill",
            description="Compact bioethanol grill ideal for small spaces. Portable and easy to use. Great for 2-3 people.",
            image_url="https://placehold.co/600x400/2a2a2a/ffffff?text=MissYak+Mini",
            price=1299.00,
            currency="TRY",
            category=ProductCategory.GRILL,
            external_url="https://missyak.com/products/mini-grill",
            is_active=True,
        ),
        ShopProduct(
            name="MissYak Premium Grill XL",
            description="Extra-large bioethanol grill for serious grill masters. Perfect for large gatherings and parties.",
            image_url="https://placehold.co/600x400/3a3a3a/ffffff?text=MissYak+XL",
            price=3999.00,
            currency="TRY",
            category=ProductCategory.GRILL,
            external_url="https://missyak.com/products/xl-grill",
            is_active=True,
        ),
        ShopProduct(
            name="Bioethanol Fuel - 1L",
            description="High-quality bioethanol fuel for clean, odorless grilling. One bottle lasts approximately 3-4 hours.",
            image_url="https://placehold.co/600x400/ff6b35/ffffff?text=Bioethanol+1L",
            price=89.90,
            currency="TRY",
            category=ProductCategory.FUEL,
            external_url="https://missyak.com/products/fuel-1l",
            is_active=True,
        ),
        ShopProduct(
            name="Bioethanol Fuel - 5L Pack",
            description="Economy pack of 5 liters bioethanol fuel. Save 15% compared to buying individual bottles.",
            image_url="https://placehold.co/600x400/ff6b35/ffffff?text=Bioethanol+5L",
            price=379.90,
            currency="TRY",
            category=ProductCategory.FUEL,
            external_url="https://missyak.com/products/fuel-5l",
            is_active=True,
        ),
        ShopProduct(
            name="Premium Grill Tool Set",
            description="Professional 5-piece grilling tool set with wooden handles. Includes spatula, tongs, fork, brush, and knife.",
            image_url="https://placehold.co/600x400/4ecdc4/ffffff?text=Tool+Set",
            price=299.00,
            currency="TRY",
            category=ProductCategory.ACCESSORY,
            external_url="https://missyak.com/products/tool-set",
            is_active=True,
        ),
        ShopProduct(
            name="Grill Cleaning Kit",
            description="Complete cleaning kit with brushes, scrapers, and eco-friendly cleaning solution.",
            image_url="https://placehold.co/600x400/95e1d3/ffffff?text=Cleaning+Kit",
            price=149.00,
            currency="TRY",
            category=ProductCategory.ACCESSORY,
            external_url="https://missyak.com/products/cleaning-kit",
            is_active=True,
        ),
        ShopProduct(
            name="MissYak Starter Bundle",
            description="Everything you need to start grilling! Includes MissYak Pro Grill, 5L fuel pack, and premium tool set. Save 20%!",
            image_url="https://placehold.co/600x400/f38181/ffffff?text=Starter+Bundle",
            price=2899.00,
            currency="TRY",
            category=ProductCategory.BUNDLE,
            external_url="https://missyak.com/products/starter-bundle",
            is_active=True,
        ),
        ShopProduct(
            name="Ultimate Grill Master Bundle",
            description="The complete package for grill masters! MissYak Premium XL, 10L fuel, tool set, cleaning kit, and recipe book.",
            image_url="https://placehold.co/600x400/aa96da/ffffff?text=Master+Bundle",
            price=4799.00,
            currency="TRY",
            category=ProductCategory.BUNDLE,
            external_url="https://missyak.com/products/master-bundle",
            is_active=True,
        ),
    ]

    for product in products:
        db.add(product)

    await db.commit()
    print(f"✅ Seeded {len(products)} products")


async def seed_demo_users(db: AsyncSession):
    """Seed demo users."""
    users = [
        User(
            email="usta@missyak.com",
            password_hash=get_password_hash("password123"),
            display_name="Mangal Ustası Ahmet",
            bio="20 yıllık tecrübeli ızgara ustası. Her Cuma akşamı canlı yayında!",
            grill_level=GrillLevel.USTA,
            avatar_url="https://i.pravatar.cc/150?img=12",
        ),
        User(
            email="ayse@missyak.com",
            password_hash=get_password_hash("password123"),
            display_name="Ayşe'nin Mutfağı",
            bio="Balık ve deniz ürünleri uzmanı. Sağlıklı tarifler paylaşıyorum.",
            grill_level=GrillLevel.AMATOR,
            avatar_url="https://i.pravatar.cc/150?img=45",
        ),
        User(
            email="mehmet@missyak.com",
            password_hash=get_password_hash("password123"),
            display_name="Köfteci Mehmet",
            bio="Köfte sanatının sırlarını öğrenin!",
            grill_level=GrillLevel.USTA,
            avatar_url="https://i.pravatar.cc/150?img=33",
        ),
    ]

    for user in users:
        db.add(user)

    await db.commit()
    print(f"✅ Seeded {len(users)} demo users")


async def main():
    """Main seed function."""
    print("🌱 Seeding database...")

    async with AsyncSessionLocal() as db:
        await seed_products(db)
        await seed_demo_users(db)

    print("✅ Database seeding complete!")


if __name__ == "__main__":
    asyncio.run(main())
