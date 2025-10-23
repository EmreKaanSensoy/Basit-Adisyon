from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QGridLayout,
                             QPushButton, QLabel, QLineEdit, QComboBox,
                             QTableWidget, QTableWidgetItem, QMessageBox,
                             QHeaderView, QGroupBox, QDoubleSpinBox,
                             QTextEdit, QFrame, QWidget)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont
from database import DatabaseManager
import logging

logger = logging.getLogger(__name__)

class PaymentDialog(QDialog):
    payment_completed = pyqtSignal(int)  # Ödeme tamamlandığında sipariş ID'sini gönder
    
    def __init__(self, order_id, order_total, parent=None):
        super().__init__(parent)
        self.order_id = order_id
        self.order_total = order_total
        self.db = DatabaseManager()
        self.db.connect()
        self.init_ui()
        self.load_order_details()
    
    def init_ui(self):
        """Ödeme arayüzünü oluştur"""
        self.setWindowTitle("Ödeme İşlemi")
        self.setModal(True)
        self.setMinimumSize(600, 500)
        
        layout = QVBoxLayout(self)
        
        # Başlık
        title = QLabel("Ödeme İşlemi")
        title.setFont(QFont("Arial", 16, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # Sipariş bilgileri
        order_info_group = QGroupBox("Sipariş Bilgileri")
        order_layout = QVBoxLayout(order_info_group)
        
        self.order_id_label = QLabel(f"Sipariş No: #{self.order_id}")
        self.order_total_label = QLabel(f"Toplam Tutar: {self.order_total:.2f} TL")
        self.order_total_label.setStyleSheet("font-size: 14px; font-weight: bold; color: green;")
        
        order_layout.addWidget(self.order_id_label)
        order_layout.addWidget(self.order_total_label)
        
        layout.addWidget(order_info_group)
        
        # Sipariş detayları
        details_group = QGroupBox("Sipariş Detayları")
        details_layout = QVBoxLayout(details_group)
        
        self.order_table = QTableWidget()
        self.order_table.setColumnCount(4)
        self.order_table.setHorizontalHeaderLabels(["Ürün", "Adet", "Birim Fiyat", "Toplam"])
        
        header = self.order_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)
        self.order_table.setEditTriggers(QTableWidget.NoEditTriggers)
        
        details_layout.addWidget(self.order_table)
        layout.addWidget(details_group)
        
        # Ödeme bilgileri
        payment_group = QGroupBox("Ödeme Bilgileri")
        payment_layout = QGridLayout(payment_group)
        
        # Ödeme tipi
        payment_layout.addWidget(QLabel("Ödeme Tipi:"), 0, 0)
        self.payment_type_combo = QComboBox()
        self.payment_type_combo.addItems(["Nakit", "Kredi Kartı", "Banka Kartı"])
        payment_layout.addWidget(self.payment_type_combo, 0, 1)
        
        # Ödenen tutar
        payment_layout.addWidget(QLabel("Ödenen Tutar:"), 1, 0)
        self.paid_amount_input = QDoubleSpinBox()
        self.paid_amount_input.setRange(0, 9999.99)
        self.paid_amount_input.setDecimals(2)
        self.paid_amount_input.setSuffix(" TL")
        self.paid_amount_input.setValue(self.order_total)
        self.paid_amount_input.valueChanged.connect(self.calculate_change)
        payment_layout.addWidget(self.paid_amount_input, 1, 1)
        
        # Para üstü
        payment_layout.addWidget(QLabel("Para Üstü:"), 2, 0)
        self.change_label = QLabel("0.00 TL")
        self.change_label.setStyleSheet("font-weight: bold; color: blue;")
        payment_layout.addWidget(self.change_label, 2, 1)
        
        # Notlar
        payment_layout.addWidget(QLabel("Notlar:"), 3, 0)
        self.notes_input = QTextEdit()
        self.notes_input.setMaximumHeight(60)
        payment_layout.addWidget(self.notes_input, 3, 1)
        
        layout.addWidget(payment_group)
        
        # Butonlar
        button_widget = QWidget()
        button_layout = QHBoxLayout(button_widget)
        
        self.complete_payment_btn = QPushButton("Ödemeyi Tamamla")
        self.complete_payment_btn.clicked.connect(self.complete_payment)
        
        self.cancel_btn = QPushButton("İptal")
        self.cancel_btn.clicked.connect(self.reject)
        
        button_layout.addWidget(self.complete_payment_btn)
        button_layout.addWidget(self.cancel_btn)
        
        layout.addWidget(button_widget)
        
        # İlk hesaplama
        self.calculate_change()
    
    def load_order_details(self):
        """Sipariş detaylarını yükle"""
        items = self.db.get_order_details(self.order_id)
        self.order_table.setRowCount(len(items))
        
        for row, item in enumerate(items):
            item_id, product_name, quantity, unit_price, total_price, notes = item
            
            self.order_table.setItem(row, 0, QTableWidgetItem(product_name))
            self.order_table.setItem(row, 1, QTableWidgetItem(str(quantity)))
            self.order_table.setItem(row, 2, QTableWidgetItem(f"{unit_price:.2f}"))
            self.order_table.setItem(row, 3, QTableWidgetItem(f"{total_price:.2f}"))
    
    def calculate_change(self):
        """Para üstünü hesapla"""
        paid_amount = self.paid_amount_input.value()
        order_total = float(self.order_total)
        change = paid_amount - order_total
        
        if change >= 0:
            self.change_label.setText(f"{change:.2f} TL")
            self.change_label.setStyleSheet("font-weight: bold; color: green;")
        else:
            self.change_label.setText(f"{change:.2f} TL")
            self.change_label.setStyleSheet("font-weight: bold; color: red;")
    
    def complete_payment(self):
        """Ödemeyi tamamla"""
        paid_amount = self.paid_amount_input.value()
        
        if paid_amount < self.order_total:
            QMessageBox.warning(self, "Uyarı", "Ödenen tutar toplam tutardan az olamaz!")
            return
        
        payment_type = self.payment_type_combo.currentText()
        notes = self.notes_input.toPlainText().strip()
        
        # Ödeme kaydını ekle
        payment_query = """
            INSERT INTO odemeler (siparis_id, odeme_tipi, tutar)
            VALUES (%s, %s, %s)
        """
        
        if self.db.execute_query(payment_query, (self.order_id, payment_type.lower(), paid_amount)):
            # Sipariş durumunu güncelle
            update_query = """
                UPDATE siparisler 
                SET durum = 'kapatildi', odeme_durumu = 'odendi'
                WHERE id = %s
            """
            
            if self.db.execute_query(update_query, (self.order_id,)):
                # Masa durumunu güncelle
                table_query = """
                    UPDATE masalar 
                    SET durum = 'bos' 
                    WHERE id = (SELECT masa_id FROM siparisler WHERE id = %s)
                """
                self.db.execute_query(table_query, (self.order_id,))
                
                self.payment_completed.emit(self.order_id)
                QMessageBox.information(self, "Başarılı", "Ödeme tamamlandı!")
                self.accept()
            else:
                QMessageBox.critical(self, "Hata", "Sipariş durumu güncellenemedi!")
        else:
            QMessageBox.critical(self, "Hata", "Ödeme kaydedilemedi!")
    
    def closeEvent(self, event):
        """Pencere kapatılırken"""
        self.db.disconnect()
        event.accept()

class BillPrintDialog(QDialog):
    def __init__(self, order_id, parent=None):
        super().__init__(parent)
        self.order_id = order_id
        self.db = DatabaseManager()
        self.db.connect()
        self.init_ui()
        self.load_bill_data()
    
    def init_ui(self):
        """Adisyon yazdırma arayüzünü oluştur"""
        self.setWindowTitle("Adisyon Yazdır")
        self.setModal(True)
        self.setMinimumSize(500, 600)
        
        layout = QVBoxLayout(self)
        
        # Başlık
        title = QLabel("Adisyon")
        title.setFont(QFont("Arial", 18, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # Adisyon içeriği
        self.bill_text = QTextEdit()
        self.bill_text.setReadOnly(True)
        self.bill_text.setFont(QFont("Courier", 10))
        layout.addWidget(self.bill_text)
        
        # Butonlar
        button_widget = QWidget()
        button_layout = QHBoxLayout(button_widget)
        
        self.print_btn = QPushButton("Yazdır")
        self.print_btn.clicked.connect(self.print_bill)
        
        self.close_btn = QPushButton("Kapat")
        self.close_btn.clicked.connect(self.close)
        
        button_layout.addWidget(self.print_btn)
        button_layout.addWidget(self.close_btn)
        
        layout.addWidget(button_widget)
    
    def load_bill_data(self):
        """Adisyon verilerini yükle"""
        # Sipariş bilgilerini al
        order_query = """
            SELECT s.id, s.toplam_tutar, s.created_at, m.masa_no
            FROM siparisler s
            JOIN masalar m ON s.masa_id = m.id
            WHERE s.id = %s
        """
        order_result = self.db.execute_query(order_query, (self.order_id,))
        
        if not order_result:
            return
        
        order_id, total, created_at, table_no = order_result[0]
        
        # Sipariş detaylarını al
        items = self.db.get_order_details(self.order_id)
        
        # Adisyon metnini oluştur
        bill_text = f"""
{'='*50}
                ADİSYON
{'='*50}
Sipariş No: #{order_id}
Masa No: {table_no}
Tarih: {created_at.strftime('%d.%m.%Y %H:%M')}
{'='*50}

"""
        
        total_amount = 0
        for item in items:
            item_id, product_name, quantity, unit_price, total_price, notes = item
            bill_text += f"{product_name:<25} {quantity:>3}x {unit_price:>6.2f} = {total_price:>8.2f}\n"
            if notes:
                bill_text += f"    Not: {notes}\n"
            total_amount += total_price
        
        bill_text += f"""
{'='*50}
TOPLAM: {total_amount:>42.2f} TL
{'='*50}

Teşekkür ederiz!
"""
        
        self.bill_text.setPlainText(bill_text)
    
    def print_bill(self):
        """Adisyonu yazdır"""
        try:
            from PyQt5.QtPrintSupport import QPrinter, QPrintDialog
            
            printer = QPrinter()
            print_dialog = QPrintDialog(printer, self)
            
            if print_dialog.exec_() == QPrintDialog.Accepted:
                self.bill_text.print_(printer)
                QMessageBox.information(self, "Başarılı", "Adisyon yazdırıldı!")
        except ImportError:
            QMessageBox.warning(self, "Uyarı", "Yazdırma modülü bulunamadı!")
        except Exception as e:
            QMessageBox.critical(self, "Hata", f"Yazdırma hatası: {str(e)}")
    
    def closeEvent(self, event):
        """Pencere kapatılırken"""
        self.db.disconnect()
        event.accept()
