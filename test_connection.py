#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Veritabanı bağlantı testi
"""

from database import DatabaseManager
import sys

def test_connection():
    """Veritabanı bağlantısını test et"""
    print("Veritabanı bağlantısı test ediliyor...")
    
    db = DatabaseManager()
    
    # Bağlantıyı test et
    if db.connect():
        print("SUCCESS: Veritabani baglantisi basarili!")
        
        # Tabloları oluştur
        print("Tablolar olusturuluyor...")
        if db.create_tables():
            print("SUCCESS: Tablolar basariyla olusturuldu!")
        else:
            print("ERROR: Tablo olusturma hatasi!")
        
        db.disconnect()
        return True
    else:
        print("ERROR: Veritabani baglantisi basarisiz!")
        print("\nLutfen asagidakileri kontrol edin:")
        print("1. MySQL servisinin calistigindan emin olun")
        print("2. Veritabani bilgilerini config.py'de kontrol edin")
        print("3. MySQL kullanici yetkilerini kontrol edin")
        print("4. MySQL root sifresini config.py'de guncelleyin")
        return False

if __name__ == "__main__":
    if test_connection():
        print("\nSUCCESS: Sistem kullanima hazir!")
        print("Uygulamayi baslatmak icin: python main.py")
    else:
        print("\nWARNING: Lutfen veritabani ayarlarini kontrol edin")
        sys.exit(1)
