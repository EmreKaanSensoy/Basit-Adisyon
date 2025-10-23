import os
from dotenv import load_dotenv

load_dotenv()

# MySQL Veritabanı Ayarları
# Eğer .env dosyası yoksa, buradaki değerleri kullanın
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'user': os.getenv('DB_USER', 'root'),
    'password': os.getenv('DB_PASSWORD', 'heves.55'),  # MySQL root şifrenizi buraya yazın
    'database': os.getenv('DB_NAME', 'adisyon_sistemi'),
    'port': int(os.getenv('DB_PORT', 3306))
}

# Uygulama Ayarları
APP_CONFIG = {
    'title': 'Adisyon Sistemi',
    'version': '1.0.0',
    'window_size': (1200, 800)
}
