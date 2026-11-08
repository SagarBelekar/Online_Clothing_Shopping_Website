import os
import django
import urllib.request
import ssl

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()

from django.conf import settings
from django.core.files.base import ContentFile
from csw_app.models import Category, Product, ProductVariant

# Static & Media directories setup
static_cat_dir = os.path.join(settings.BASE_DIR, 'static', 'images', 'categories')
static_prod_dir = os.path.join(settings.BASE_DIR, 'static', 'images', 'products')
media_cat_dir = os.path.join(settings.MEDIA_ROOT, 'categories')
media_prod_dir = os.path.join(settings.MEDIA_ROOT, 'products')

for path in [static_cat_dir, static_prod_dir, media_cat_dir, media_prod_dir]:
    os.makedirs(path, exist_ok=True)

# SSL Certificate verification bypass for seamless downloading
ssl_context = ssl._create_unverified_context()

def download_image(url):
    req = urllib.request.Request(
        url, 
        headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'}
    )
    try:
        with urllib.request.urlopen(req, context=ssl_context, timeout=20) as res:
            return res.read()
    except Exception as e:
        print(f"Error fetching image from {url}: {e}")
        return None

# High-resolution category images
category_photos = {
    "Men": "https://images.unsplash.com/photo-1490578474895-699cd4e2cf59?w=600&auto=format&fit=crop&q=80",
    "Women": "https://images.unsplash.com/photo-1483985988355-763728e1935b?w=600&auto=format&fit=crop&q=80",
    "Kids": "https://images.unsplash.com/photo-1514090458221-65bb69cf63e6?w=600&auto=format&fit=crop&q=80",
    "Winter Wear": "https://images.unsplash.com/photo-1548883354-7622d03aca27?w=600&auto=format&fit=crop&q=80",
    "Ethnic & Traditional": "https://images.unsplash.com/photo-1610030469983-98e550d6193c?w=600&auto=format&fit=crop&q=80",
    "Activewear": "https://images.unsplash.com/photo-1518611012118-696072aa579a?w=600&auto=format&fit=crop&q=80",
    "Casual T-Shirts": "https://images.unsplash.com/photo-1521572267360-ee0c2909d518?w=600&auto=format&fit=crop&q=80",
    "Formal Wear": "https://images.unsplash.com/photo-1507679799987-c73779587ccf?w=600&auto=format&fit=crop&q=80"
}

# Real studio/flatlay apparel photos mapped accurately
product_photos = {
    # Exclusive Men Clothes
    "Men Casual Cuban Linen Shirt": "https://images.unsplash.com/photo-1596755094514-f87e34085b2c?w=600&auto=format&fit=crop&q=80",
    "Men Textured Knit Polo Shirt": "https://images.unsplash.com/photo-1625910513413-5bc2174fcad3?w=600&auto=format&fit=crop&q=80",
    "Men Slim Fit Stretch Chinos": "https://images.unsplash.com/photo-1624378439575-d8705ad7ae80?w=600&auto=format&fit=crop&q=80",
    "Men Biker Faux Leather Jacket": "https://images.unsplash.com/photo-1520975954732-35dd22299614?w=600&auto=format&fit=crop&q=80",
    "Men Vintage Wash Denim Jacket": "https://images.unsplash.com/photo-1576995853123-5a10305d93c0?w=600&auto=format&fit=crop&q=80",
    "Men Cable Knit Wool Sweater": "https://images.unsplash.com/photo-1434389677669-e08b4cac3105?w=600&auto=format&fit=crop&q=80",
    "Men Heavyweight Streetwear Hoodie": "https://images.unsplash.com/photo-1556905055-8f358a7a47b2?w=600&auto=format&fit=crop&q=80",
    "Men Tailored Formal Wool Blazer": "https://images.unsplash.com/photo-1507679799987-c73779587ccf?w=600&auto=format&fit=crop&q=80",
    "Slim Fit Oxford Formal Shirt": "https://images.unsplash.com/photo-1602810318383-e386cc2a3ccf?w=600&auto=format&fit=crop&q=80",
    "Vintage Straight Fit Denim Jeans": "https://images.unsplash.com/photo-1541099649105-f69ad21f3246?w=600&auto=format&fit=crop&q=80",
    # Other Main Collections
    "Classic Oversized Cotton T-Shirt": "https://images.unsplash.com/photo-1583743814966-8936f5b7be1a?w=600&auto=format&fit=crop&q=80",
    "Floral Print Tiered Maxi Dress": "https://images.unsplash.com/photo-1572804013309-59a88b7e92f1?w=600&auto=format&fit=crop&q=80",
    "Designer Anarkali Kurta Set": "https://images.unsplash.com/photo-1617627143750-d86bc21e42bb?w=600&auto=format&fit=crop&q=80",
    "Heavyweight Fleece Pullover Hoodie": "https://images.unsplash.com/photo-1556905055-8f358a7a47b2?w=600&auto=format&fit=crop&q=80",
    "Quick-Dry Stretch Gym Trackpants": "https://images.unsplash.com/photo-1506629082955-511b1aa562c8?w=600&auto=format&fit=crop&q=80",
    "Boys 2-Piece Cotton Dungaree Set": "https://images.unsplash.com/photo-1519457431-44ccd64a579b?w=600&auto=format&fit=crop&q=80"
}

# Default Stock Variants per item type
default_variants = {
    "pant": [("30", "Navy", 18), ("32", "Khaki", 24), ("34", "Black", 20)],
    "jean": [("30", "Dark Blue", 15), ("32", "Mid Blue", 20), ("34", "Black", 16)],
    "blazer": [("38", "Charcoal", 8), ("40", "Navy", 14), ("42", "Black", 10)],
    "jacket": [("M", "Tan Brown", 12), ("L", "Jet Black", 18), ("XL", "Dark Brown", 10)],
    "regular": [("S", "White", 15), ("M", "Navy", 25), ("L", "Black", 20), ("XL", "Olive", 12)]
}

print("--- Step 1: Updating Category Images ---")
for cat in Category.objects.all():
    url = category_photos.get(cat.category_name, "https://images.unsplash.com/photo-1441986300917-64674bd600d8?w=600&auto=format&fit=crop&q=80")
    print(f"Fetching photo for Category: {cat.category_name}...")
    img_data = download_image(url)
    if img_data:
        filename = f"cat_{cat.id}.jpg"
        # Static folder save
        with open(os.path.join(static_cat_dir, filename), 'wb') as f:
            f.write(img_data)
        # Media / DB save
        cat.image.save(filename, ContentFile(img_data), save=True)

print("\n--- Step 2: Updating Product Photos & Variants ---")
for prod in Product.objects.all():
    # Fuzzy matching to locate best URL
    target_url = None
    for name_key, url_val in product_photos.items():
        if name_key.lower() in prod.name.lower() or prod.name.lower() in name_key.lower():
            target_url = url_val
            break

    if not target_url:
        target_url = "https://images.unsplash.com/photo-1523381210434-271e8be1f52b?w=600&auto=format&fit=crop&q=80"

    print(f"Fetching photo for: {prod.name}...")
    img_data = download_image(target_url)
    if img_data:
        filename = f"prod_{prod.id}.jpg"
        # 1. Static folder save
        with open(os.path.join(static_prod_dir, filename), 'wb') as f:
            f.write(img_data)
        # 2. Media / DB save
        prod.image.save(filename, ContentFile(img_data), save=True)

    # Agar product ke variants empty hain toh default variants add karein
    if prod.variants.count() == 0:
        lname = prod.name.lower()
        if "chino" in lname or "trouser" in lname or "pant" in lname:
            selected_v = default_variants["pant"]
        elif "jean" in lname or "denim" in lname:
            selected_v = default_variants["jean"]
        elif "blazer" in lname or "suit" in lname:
            selected_v = default_variants["blazer"]
        elif "jacket" in lname:
            selected_v = default_variants["jacket"]
        else:
            selected_v = default_variants["regular"]

        for size, color, stock in selected_v:
            ProductVariant.objects.create(
                product=prod,
                size=size,
                color=color,
                stock=stock
            )
        print(f"  -> Variants auto-created for {prod.name}")

print("\nSuccess: Sabhi Categories aur Men's Clothes real images aur stock variants ke sath update ho gaye hain!")