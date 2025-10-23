import mysql.connector
from mysql.connector import Error
from config import DB_CONFIG
import logging

# Logging ayarları
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DatabaseManager:
    def __init__(self):
        self.connection = None
        self.cursor = None
    
    def connect(self):
        """Veritabanına bağlan"""
        try:
            self.connection = mysql.connector.connect(**DB_CONFIG)
            self.cursor = self.connection.cursor()
            logger.info("Veritabanına başarıyla bağlanıldı")
            return True
        except Error as e:
            logger.error(f"Veritabanı bağlantı hatası: {e}")
            return False
    
    def disconnect(self):
        """Veritabanı bağlantısını kapat"""
        if self.cursor:
            self.cursor.close()
        if self.connection and self.connection.is_connected():
            self.connection.close()
            logger.info("Veritabanı bağlantısı kapatıldı")
    
    def create_tables(self):
        """Gerekli tabloları oluştur"""
        try:
            # Kategoriler tablosu
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS kategoriler (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    ad VARCHAR(100) NOT NULL,
                    aciklama TEXT,
                    aktif BOOLEAN DEFAULT TRUE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Ürünler tablosu
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS urunler (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    ad VARCHAR(100) NOT NULL,
                    kategori_id INT,
                    fiyat DECIMAL(10,2) NOT NULL,
                    aciklama TEXT,
                    aktif BOOLEAN DEFAULT TRUE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (kategori_id) REFERENCES kategoriler(id)
                )
            """)
            
            # Masalar tablosu
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS masalar (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    masa_no INT UNIQUE NOT NULL,
                    durum ENUM('bos', 'dolu', 'rezerve') DEFAULT 'bos',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Siparişler tablosu
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS siparisler (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    masa_id INT,
                    toplam_tutar DECIMAL(10,2) DEFAULT 0,
                    durum ENUM('aktif', 'kapatildi', 'iptal') DEFAULT 'aktif',
                    odeme_durumu ENUM('beklemede', 'odendi') DEFAULT 'beklemede',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    FOREIGN KEY (masa_id) REFERENCES masalar(id)
                )
            """)
            
            # Sipariş detayları tablosu
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS siparis_detaylari (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    siparis_id INT,
                    urun_id INT,
                    adet INT NOT NULL DEFAULT 1,
                    birim_fiyat DECIMAL(10,2) NOT NULL,
                    toplam_fiyat DECIMAL(10,2) NOT NULL,
                    notlar TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (siparis_id) REFERENCES siparisler(id),
                    FOREIGN KEY (urun_id) REFERENCES urunler(id)
                )
            """)
            
            # Ödemeler tablosu
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS odemeler (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    siparis_id INT,
                    odeme_tipi ENUM('nakit', 'kredi_karti', 'banka_karti') NOT NULL,
                    tutar DECIMAL(10,2) NOT NULL,
                    tarih TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (siparis_id) REFERENCES siparisler(id)
                )
            """)
            
            self.connection.commit()
            logger.info("Tüm tablolar başarıyla oluşturuldu")
            
            # Varsayılan verileri ekle
            self.insert_default_data()
            
        except Error as e:
            logger.error(f"Tablo oluşturma hatası: {e}")
            return False
        return True
    
    def insert_default_data(self):
        """Varsayılan verileri ekle"""
        try:
            # Varsayılan kategoriler
            kategoriler = [
                ('İçecekler', 'Soğuk ve sıcak içecekler'),
                ('Yemekler', 'Ana yemekler ve atıştırmalıklar'),
                ('Tatlılar', 'Tatlı çeşitleri'),
                ('Kahvaltı', 'Kahvaltı menüsü')
            ]
            
            for kategori in kategoriler:
                self.cursor.execute("""
                    INSERT IGNORE INTO kategoriler (ad, aciklama) 
                    VALUES (%s, %s)
                """, kategori)
            
            # Varsayılan masalar (1-20 arası)
            for masa_no in range(1, 21):
                self.cursor.execute("""
                    INSERT IGNORE INTO masalar (masa_no) 
                    VALUES (%s)
                """, (masa_no,))
            
            # Varsayılan ürünler
            urunler = [
                ('Çay', 1, 5.00, 'Sıcak çay'),
                ('Kahve', 1, 8.00, 'Türk kahvesi'),
                ('Kola', 1, 6.00, 'Soğuk içecek'),
                ('Su', 1, 2.00, 'Şişe su'),
                ('Döner', 2, 25.00, 'Tavuk döner'),
                ('Lahmacun', 2, 15.00, 'İnce hamur lahmacun'),
                ('Pizza', 2, 35.00, 'Margherita pizza'),
                ('Baklava', 3, 20.00, 'Antep fıstıklı baklava'),
                ('Sütlaç', 3, 12.00, 'Ev yapımı sütlaç'),
                ('Menemen', 4, 18.00, 'Domatesli menemen')
            ]
            
            for urun in urunler:
                self.cursor.execute("""
                    INSERT IGNORE INTO urunler (ad, kategori_id, fiyat, aciklama) 
                    VALUES (%s, %s, %s, %s)
                """, urun)
            
            self.connection.commit()
            logger.info("Varsayılan veriler başarıyla eklendi")
            
        except Error as e:
            logger.error(f"Varsayılan veri ekleme hatası: {e}")
    
    def execute_query(self, query, params=None):
        """SQL sorgusu çalıştır"""
        try:
            if params:
                self.cursor.execute(query, params)
            else:
                self.cursor.execute(query)
            
            if query.strip().upper().startswith('SELECT'):
                return self.cursor.fetchall()
            else:
                self.connection.commit()
                return True
        except Error as e:
            logger.error(f"Sorgu hatası: {e}")
            return None
    
    def get_products(self):
        """Tüm ürünleri getir"""
        query = """
            SELECT u.id, u.ad, k.ad as kategori, u.fiyat, u.aciklama 
            FROM urunler u 
            JOIN kategoriler k ON u.kategori_id = k.id 
            WHERE u.aktif = TRUE
            ORDER BY k.ad, u.ad
        """
        return self.execute_query(query)
    
    def get_categories(self):
        """Tüm kategorileri getir"""
        query = "SELECT id, ad FROM kategoriler WHERE aktif = TRUE ORDER BY ad"
        return self.execute_query(query)
    
    def get_tables(self):
        """Tüm masaları getir"""
        query = "SELECT id, masa_no, durum FROM masalar ORDER BY masa_no"
        return self.execute_query(query)
    
    def create_order(self, masa_id):
        """Yeni sipariş oluştur"""
        query = "INSERT INTO siparisler (masa_id) VALUES (%s)"
        result = self.execute_query(query, (masa_id,))
        if result:
            return self.cursor.lastrowid
        return None
    
    def add_order_item(self, siparis_id, urun_id, adet, notlar=None):
        """Siparişe ürün ekle"""
        # Ürün fiyatını al
        price_query = "SELECT fiyat FROM urunler WHERE id = %s"
        price_result = self.execute_query(price_query, (urun_id,))
        
        if not price_result:
            return False
        
        birim_fiyat = price_result[0][0]
        toplam_fiyat = birim_fiyat * adet
        
        query = """
            INSERT INTO siparis_detaylari 
            (siparis_id, urun_id, adet, birim_fiyat, toplam_fiyat, notlar) 
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        return self.execute_query(query, (siparis_id, urun_id, adet, birim_fiyat, toplam_fiyat, notlar))
    
    def get_order_details(self, siparis_id):
        """Sipariş detaylarını getir"""
        query = """
            SELECT sd.id, u.ad, sd.adet, sd.birim_fiyat, sd.toplam_fiyat, sd.notlar
            FROM siparis_detaylari sd
            JOIN urunler u ON sd.urun_id = u.id
            WHERE sd.siparis_id = %s
        """
        return self.execute_query(query, (siparis_id,))
    
    def update_order_total(self, siparis_id):
        """Sipariş toplamını güncelle"""
        query = """
            UPDATE siparisler 
            SET toplam_tutar = (
                SELECT COALESCE(SUM(toplam_fiyat), 0) 
                FROM siparis_detaylari 
                WHERE siparis_id = %s
            )
            WHERE id = %s
        """
        return self.execute_query(query, (siparis_id, siparis_id))
    
    def remove_order_item(self, order_item_id):
        """Sipariş detayını sil"""
        query = "DELETE FROM siparis_detaylari WHERE id = %s"
        return self.execute_query(query, (order_item_id,))
    
    def get_order_summary(self, order_id):
        """Sipariş özetini getir"""
        query = """
            SELECT s.id, s.toplam_tutar, s.created_at, m.masa_no, s.durum
            FROM siparisler s
            JOIN masalar m ON s.masa_id = m.id
            WHERE s.id = %s
        """
        result = self.execute_query(query, (order_id,))
        return result[0] if result else None
