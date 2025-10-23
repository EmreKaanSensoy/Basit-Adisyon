from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QGridLayout,
                             QPushButton, QLabel, QLineEdit, QComboBox,
                             QTableWidget, QTableWidgetItem, QMessageBox,
                             QHeaderView, QGroupBox, QCheckBox, QDoubleSpinBox,
                             QTextEdit, QSplitter, QWidget)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont
from database import DatabaseManager
import logging

logger = logging.getLogger(__name__)

class ProductManagementDialog(QDialog):
    product_updated = pyqtSignal()  # Ürün güncellendiğinde ana pencereye sinyal gönder
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.db = DatabaseManager()
        self.db.connect()
        self.init_ui()
        self.load_products()
        self.load_categories()
    
    def init_ui(self):
        """Ürün yönetimi arayüzünü oluştur"""
        self.setWindowTitle("Ürün Yönetimi")
        self.setModal(True)
        self.setMinimumSize(800, 600)
        
        layout = QVBoxLayout(self)
        
        # Başlık
        title = QLabel("Ürün Yönetimi")
        title.setFont(QFont("Arial", 16, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # Ana splitter
        splitter = QSplitter(Qt.Horizontal)
        
        # Sol panel - Ürün listesi
        left_panel = self.create_product_list_panel()
        splitter.addWidget(left_panel)
        
        # Sağ panel - Ürün düzenleme
        right_panel = self.create_product_edit_panel()
        splitter.addWidget(right_panel)
        
        splitter.setSizes([400, 400])
        layout.addWidget(splitter)
        
        # Alt butonlar
        button_widget = QWidget()
        button_layout = QHBoxLayout(button_widget)
        
        self.new_product_btn = QPushButton("Yeni Ürün")
        self.new_product_btn.clicked.connect(self.new_product)
        
        self.save_btn = QPushButton("Kaydet")
        self.save_btn.clicked.connect(self.save_product)
        self.save_btn.setEnabled(False)
        
        self.delete_btn = QPushButton("Sil")
        self.delete_btn.clicked.connect(self.delete_product)
        self.delete_btn.setEnabled(False)
        
        self.close_btn = QPushButton("Kapat")
        self.close_btn.clicked.connect(self.close)
        
        button_layout.addWidget(self.new_product_btn)
        button_layout.addWidget(self.save_btn)
        button_layout.addWidget(self.delete_btn)
        button_layout.addStretch()
        button_layout.addWidget(self.close_btn)
        
        layout.addWidget(button_widget)
    
    def create_product_list_panel(self):
        """Ürün listesi paneli oluştur"""
        panel = QGroupBox("Ürün Listesi")
        layout = QVBoxLayout(panel)
        
        # Arama
        search_layout = QHBoxLayout()
        search_layout.addWidget(QLabel("Ara:"))
        
        self.search_input = QLineEdit()
        self.search_input.textChanged.connect(self.filter_products)
        search_layout.addWidget(self.search_input)
        
        layout.addLayout(search_layout)
        
        # Ürün tablosu
        self.product_table = QTableWidget()
        self.product_table.setColumnCount(6)
        self.product_table.setHorizontalHeaderLabels([
            "ID", "Ürün Adı", "Kategori", "Fiyat", "Açıklama", "Aktif"
        ])
        
        # Tablo ayarları
        header = self.product_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)
        self.product_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.product_table.itemSelectionChanged.connect(self.on_product_selected)
        
        layout.addWidget(self.product_table)
        
        return panel
    
    def create_product_edit_panel(self):
        """Ürün düzenleme paneli oluştur"""
        panel = QGroupBox("Ürün Bilgileri")
        layout = QVBoxLayout(panel)
        
        # Ürün adı
        name_layout = QHBoxLayout()
        name_layout.addWidget(QLabel("Ürün Adı:"))
        self.product_name_input = QLineEdit()
        name_layout.addWidget(self.product_name_input)
        layout.addLayout(name_layout)
        
        # Kategori
        category_layout = QHBoxLayout()
        category_layout.addWidget(QLabel("Kategori:"))
        self.category_combo = QComboBox()
        category_layout.addWidget(self.category_combo)
        layout.addLayout(category_layout)
        
        # Fiyat
        price_layout = QHBoxLayout()
        price_layout.addWidget(QLabel("Fiyat:"))
        self.price_input = QDoubleSpinBox()
        self.price_input.setRange(0, 9999.99)
        self.price_input.setDecimals(2)
        self.price_input.setSuffix(" TL")
        price_layout.addWidget(self.price_input)
        layout.addLayout(price_layout)
        
        # Açıklama
        desc_layout = QHBoxLayout()
        desc_layout.addWidget(QLabel("Açıklama:"))
        layout.addLayout(desc_layout)
        
        self.description_input = QTextEdit()
        self.description_input.setMaximumHeight(80)
        layout.addWidget(self.description_input)
        
        # Aktif durumu
        self.active_checkbox = QCheckBox("Aktif")
        self.active_checkbox.setChecked(True)
        layout.addWidget(self.active_checkbox)
        
        layout.addStretch()
        
        return panel
    
    def load_categories(self):
        """Kategorileri yükle"""
        categories = self.db.get_categories()
        self.category_combo.clear()
        if categories:
            for cat_id, cat_name in categories:
                self.category_combo.addItem(cat_name, cat_id)
    
    def load_products(self):
        """Ürünleri yükle"""
        products = self.db.get_products()
        self.product_table.setRowCount(len(products))
        
        for row, product in enumerate(products):
            product_id, name, category, price, description = product
            
            self.product_table.setItem(row, 0, QTableWidgetItem(str(product_id)))
            self.product_table.setItem(row, 1, QTableWidgetItem(name))
            self.product_table.setItem(row, 2, QTableWidgetItem(category))
            self.product_table.setItem(row, 3, QTableWidgetItem(f"{price:.2f}"))
            self.product_table.setItem(row, 4, QTableWidgetItem(description or ""))
            self.product_table.setItem(row, 5, QTableWidgetItem("Evet"))
    
    def filter_products(self):
        """Ürünleri filtrele"""
        search_text = self.search_input.text().lower()
        
        for row in range(self.product_table.rowCount()):
            should_show = False
            for col in range(self.product_table.columnCount()):
                item = self.product_table.item(row, col)
                if item and search_text in item.text().lower():
                    should_show = True
                    break
            
            self.product_table.setRowHidden(row, not should_show)
    
    def on_product_selected(self):
        """Ürün seçildiğinde"""
        current_row = self.product_table.currentRow()
        if current_row >= 0:
            # Seçili ürünün bilgilerini düzenleme paneline yükle
            product_id = int(self.product_table.item(current_row, 0).text())
            product_name = self.product_table.item(current_row, 1).text()
            category = self.product_table.item(current_row, 2).text()
            price = float(self.product_table.item(current_row, 3).text())
            description = self.product_table.item(current_row, 4).text()
            
            self.product_name_input.setText(product_name)
            self.price_input.setValue(price)
            self.description_input.setPlainText(description)
            
            # Kategori seçimi
            for i in range(self.category_combo.count()):
                if self.category_combo.itemText(i) == category:
                    self.category_combo.setCurrentIndex(i)
                    break
            
            self.save_btn.setEnabled(True)
            self.delete_btn.setEnabled(True)
            self.current_product_id = product_id
        else:
            self.clear_form()
    
    def clear_form(self):
        """Formu temizle"""
        self.product_name_input.clear()
        self.price_input.setValue(0.0)
        self.description_input.clear()
        self.active_checkbox.setChecked(True)
        self.save_btn.setEnabled(False)
        self.delete_btn.setEnabled(False)
        self.current_product_id = None
    
    def new_product(self):
        """Yeni ürün oluştur"""
        self.clear_form()
        self.product_table.clearSelection()
        self.save_btn.setEnabled(True)
        self.current_product_id = None
    
    def save_product(self):
        """Ürünü kaydet"""
        name = self.product_name_input.text().strip()
        if not name:
            QMessageBox.warning(self, "Uyarı", "Ürün adı boş olamaz!")
            return
        
        category_id = self.category_combo.currentData()
        if not category_id:
            QMessageBox.warning(self, "Uyarı", "Lütfen bir kategori seçin!")
            return
        
        price = self.price_input.value()
        description = self.description_input.toPlainText().strip()
        active = self.active_checkbox.isChecked()
        
        if self.current_product_id:
            # Güncelleme
            query = """
                UPDATE urunler 
                SET ad = %s, kategori_id = %s, fiyat = %s, aciklama = %s, aktif = %s
                WHERE id = %s
            """
            params = (name, category_id, price, description, active, self.current_product_id)
        else:
            # Yeni ürün ekleme
            query = """
                INSERT INTO urunler (ad, kategori_id, fiyat, aciklama, aktif)
                VALUES (%s, %s, %s, %s, %s)
            """
            params = (name, category_id, price, description, active)
        
        if self.db.execute_query(query, params):
            self.load_products()
            self.clear_form()
            self.product_updated.emit()  # Ana pencereye sinyal gönder
            QMessageBox.information(self, "Başarılı", "Ürün kaydedildi!")
        else:
            QMessageBox.critical(self, "Hata", "Ürün kaydedilemedi!")
    
    def delete_product(self):
        """Ürünü sil"""
        if not self.current_product_id:
            return
        
        reply = QMessageBox.question(self, "Onay", 
                                   "Bu ürünü silmek istediğinizden emin misiniz?",
                                   QMessageBox.Yes | QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            # Önce ürünü pasif yap (soft delete)
            query = "UPDATE urunler SET aktif = FALSE WHERE id = %s"
            if self.db.execute_query(query, (self.current_product_id,)):
                self.load_products()
                self.clear_form()
                self.product_updated.emit()
                QMessageBox.information(self, "Başarılı", "Ürün silindi!")
            else:
                QMessageBox.critical(self, "Hata", "Ürün silinemedi!")
    
    def closeEvent(self, event):
        """Pencere kapatılırken"""
        self.db.disconnect()
        event.accept()

class CategoryManagementDialog(QDialog):
    category_updated = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.db = DatabaseManager()
        self.db.connect()
        self.init_ui()
        self.load_categories()
    
    def init_ui(self):
        """Kategori yönetimi arayüzünü oluştur"""
        self.setWindowTitle("Kategori Yönetimi")
        self.setModal(True)
        self.setMinimumSize(600, 400)
        
        layout = QVBoxLayout(self)
        
        # Başlık
        title = QLabel("Kategori Yönetimi")
        title.setFont(QFont("Arial", 16, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # Kategori listesi
        self.category_table = QTableWidget()
        self.category_table.setColumnCount(3)
        self.category_table.setHorizontalHeaderLabels(["ID", "Kategori Adı", "Açıklama"])
        
        header = self.category_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)
        self.category_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.category_table.itemSelectionChanged.connect(self.on_category_selected)
        
        layout.addWidget(self.category_table)
        
        # Düzenleme formu
        form_layout = QGridLayout()
        
        form_layout.addWidget(QLabel("Kategori Adı:"), 0, 0)
        self.category_name_input = QLineEdit()
        form_layout.addWidget(self.category_name_input, 0, 1)
        
        form_layout.addWidget(QLabel("Açıklama:"), 1, 0)
        self.category_desc_input = QTextEdit()
        self.category_desc_input.setMaximumHeight(60)
        form_layout.addWidget(self.category_desc_input, 1, 1)
        
        layout.addLayout(form_layout)
        
        # Butonlar
        button_widget = QWidget()
        button_layout = QHBoxLayout(button_widget)
        
        self.new_category_btn = QPushButton("Yeni Kategori")
        self.new_category_btn.clicked.connect(self.new_category)
        
        self.save_category_btn = QPushButton("Kaydet")
        self.save_category_btn.clicked.connect(self.save_category)
        self.save_category_btn.setEnabled(False)
        
        self.delete_category_btn = QPushButton("Sil")
        self.delete_category_btn.clicked.connect(self.delete_category)
        self.delete_category_btn.setEnabled(False)
        
        self.close_btn = QPushButton("Kapat")
        self.close_btn.clicked.connect(self.close)
        
        button_layout.addWidget(self.new_category_btn)
        button_layout.addWidget(self.save_category_btn)
        button_layout.addWidget(self.delete_category_btn)
        button_layout.addStretch()
        button_layout.addWidget(self.close_btn)
        
        layout.addWidget(button_widget)
    
    def load_categories(self):
        """Kategorileri yükle"""
        query = "SELECT id, ad, aciklama FROM kategoriler ORDER BY ad"
        categories = self.db.execute_query(query)
        
        self.category_table.setRowCount(len(categories))
        
        for row, category in enumerate(categories):
            cat_id, name, description = category
            self.category_table.setItem(row, 0, QTableWidgetItem(str(cat_id)))
            self.category_table.setItem(row, 1, QTableWidgetItem(name))
            self.category_table.setItem(row, 2, QTableWidgetItem(description or ""))
    
    def on_category_selected(self):
        """Kategori seçildiğinde"""
        current_row = self.category_table.currentRow()
        if current_row >= 0:
            cat_id = int(self.category_table.item(current_row, 0).text())
            name = self.category_table.item(current_row, 1).text()
            description = self.category_table.item(current_row, 2).text()
            
            self.category_name_input.setText(name)
            self.category_desc_input.setPlainText(description)
            
            self.save_category_btn.setEnabled(True)
            self.delete_category_btn.setEnabled(True)
            self.current_category_id = cat_id
        else:
            self.clear_form()
    
    def clear_form(self):
        """Formu temizle"""
        self.category_name_input.clear()
        self.category_desc_input.clear()
        self.save_category_btn.setEnabled(False)
        self.delete_category_btn.setEnabled(False)
        self.current_category_id = None
    
    def new_category(self):
        """Yeni kategori oluştur"""
        self.clear_form()
        self.category_table.clearSelection()
        self.save_category_btn.setEnabled(True)
        self.current_category_id = None
    
    def save_category(self):
        """Kategoriyi kaydet"""
        name = self.category_name_input.text().strip()
        if not name:
            QMessageBox.warning(self, "Uyarı", "Kategori adı boş olamaz!")
            return
        
        description = self.category_desc_input.toPlainText().strip()
        
        if self.current_category_id:
            # Güncelleme
            query = "UPDATE kategoriler SET ad = %s, aciklama = %s WHERE id = %s"
            params = (name, description, self.current_category_id)
        else:
            # Yeni kategori ekleme
            query = "INSERT INTO kategoriler (ad, aciklama) VALUES (%s, %s)"
            params = (name, description)
        
        if self.db.execute_query(query, params):
            self.load_categories()
            self.clear_form()
            self.category_updated.emit()
            QMessageBox.information(self, "Başarılı", "Kategori kaydedildi!")
        else:
            QMessageBox.critical(self, "Hata", "Kategori kaydedilemedi!")
    
    def delete_category(self):
        """Kategoriyi sil"""
        if not self.current_category_id:
            return
        
        # Önce bu kategoride ürün var mı kontrol et
        query = "SELECT COUNT(*) FROM urunler WHERE kategori_id = %s"
        result = self.db.execute_query(query, (self.current_category_id,))
        
        if result and result[0][0] > 0:
            QMessageBox.warning(self, "Uyarı", 
                               "Bu kategoride ürünler bulunmaktadır. Önce ürünleri silin veya başka kategoriye taşıyın.")
            return
        
        reply = QMessageBox.question(self, "Onay", 
                                   "Bu kategoriyi silmek istediğinizden emin misiniz?",
                                   QMessageBox.Yes | QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            query = "DELETE FROM kategoriler WHERE id = %s"
            if self.db.execute_query(query, (self.current_category_id,)):
                self.load_categories()
                self.clear_form()
                self.category_updated.emit()
                QMessageBox.information(self, "Başarılı", "Kategori silindi!")
            else:
                QMessageBox.critical(self, "Hata", "Kategori silinemedi!")
    
    def closeEvent(self, event):
        """Pencere kapatılırken"""
        self.db.disconnect()
        event.accept()
