import sys
import os
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QGridLayout, QPushButton, QLabel, 
                             QTableWidget, QTableWidgetItem, QComboBox, 
                             QSpinBox, QTextEdit, QMessageBox, QDialog,
                             QTabWidget, QGroupBox, QLineEdit, QDateEdit,
                             QHeaderView, QSplitter, QFrame)
from PyQt5.QtCore import Qt, QTimer, QDate
from PyQt5.QtGui import QFont, QIcon, QPixmap
from database import DatabaseManager
from config import APP_CONFIG
from product_management import ProductManagementDialog, CategoryManagementDialog
from payment_dialog import PaymentDialog, BillPrintDialog
from reports_dialog import ReportsDialog
import logging

# Logging ayarları
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.db = DatabaseManager()
        self.current_order_id = None
        self.current_table_id = None
        self.init_ui()
        self.connect_database()
        
    def init_ui(self):
        """Ana arayüzü oluştur"""
        self.setWindowTitle(APP_CONFIG['title'])
        self.setGeometry(100, 100, *APP_CONFIG['window_size'])
        
        # Modern stil uygula
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f5f5f5;
            }
            QWidget {
                font-family: 'Segoe UI', Arial, sans-serif;
            }
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 6px;
                font-weight: bold;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:pressed {
                background-color: #3d8b40;
            }
            QPushButton:disabled {
                background-color: #cccccc;
                color: #666666;
            }
            QGroupBox {
                font-weight: bold;
                border: 2px solid #cccccc;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
                background-color: white;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
                color: #333333;
            }
            QTableWidget {
                background-color: white;
                border: 1px solid #ddd;
                border-radius: 6px;
                gridline-color: #e0e0e0;
                selection-background-color: #e3f2fd;
            }
            QTableWidget::item {
                padding: 8px;
                border-bottom: 1px solid #f0f0f0;
            }
            QTableWidget::item:selected {
                background-color: #e3f2fd;
                color: #1976d2;
            }
            QComboBox {
                border: 2px solid #ddd;
                border-radius: 6px;
                padding: 5px;
                background-color: white;
            }
            QComboBox:focus {
                border-color: #4CAF50;
            }
            QSpinBox, QDoubleSpinBox {
                border: 2px solid #ddd;
                border-radius: 6px;
                padding: 5px;
                background-color: white;
            }
            QTextEdit {
                border: 2px solid #ddd;
                border-radius: 6px;
                background-color: white;
            }
            QLabel {
                color: #333333;
            }
        """)
        
        # Ana widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Ana layout
        main_layout = QHBoxLayout(central_widget)
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(10, 10, 10, 10)
        
        # Sol panel - Masa seçimi
        left_panel = self.create_table_panel()
        
        # Sağ panel - Sipariş yönetimi
        right_panel = self.create_order_panel()
        
        # Splitter ile panelleri ayır
        splitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(left_panel)
        splitter.addWidget(right_panel)
        splitter.setSizes([350, 850])
        splitter.setStyleSheet("""
            QSplitter::handle {
                background-color: #ddd;
                width: 3px;
            }
            QSplitter::handle:hover {
                background-color: #4CAF50;
            }
        """)
        
        main_layout.addWidget(splitter)
        
        # Menü çubuğu
        self.create_menu_bar()
        
        # Status bar
        self.statusBar().showMessage("Sistem hazır - Masa seçin")
        self.statusBar().setStyleSheet("""
            QStatusBar {
                background-color: #f0f0f0;
                border-top: 1px solid #ddd;
                color: #333;
            }
        """)
        
    def create_menu_bar(self):
        """Menü çubuğu oluştur"""
        menubar = self.menuBar()
        
        # Dosya menüsü
        file_menu = menubar.addMenu('Dosya')
        
        # Ürün yönetimi
        product_action = file_menu.addAction('Ürün Yönetimi')
        product_action.triggered.connect(self.open_product_management)
        
        # Kategori yönetimi
        category_action = file_menu.addAction('Kategori Yönetimi')
        category_action.triggered.connect(self.open_category_management)
        
        # Raporlar
        report_action = file_menu.addAction('Raporlar')
        report_action.triggered.connect(self.open_reports)
        
        file_menu.addSeparator()
        
        # Çıkış
        exit_action = file_menu.addAction('Çıkış')
        exit_action.triggered.connect(self.close)
        
        # Yardım menüsü
        help_menu = menubar.addMenu('Yardım')
        about_action = help_menu.addAction('Hakkında')
        about_action.triggered.connect(self.show_about)
    
    def create_table_panel(self):
        """Masa seçim paneli oluştur"""
        panel = QGroupBox("🍽️ Masa Seçimi")
        panel.setStyleSheet("""
            QGroupBox {
                font-size: 14px;
                font-weight: bold;
                color: #2c3e50;
                border: 2px solid #3498db;
                border-radius: 10px;
                margin-top: 10px;
                padding-top: 15px;
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                    stop:0 #ecf0f1, stop:1 #bdc3c7);
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 15px;
                padding: 0 8px 0 8px;
                color: #2c3e50;
                font-size: 16px;
            }
        """)
        layout = QVBoxLayout(panel)
        layout.setSpacing(15)
        layout.setContentsMargins(15, 20, 15, 15)
        
        # Masa butonları
        self.table_buttons = {}
        table_layout = QGridLayout()
        table_layout.setSpacing(8)
        
        # 20 masa için butonlar oluştur
        for i in range(1, 21):
            btn = QPushButton(f"🍽️\nMasa {i}")
            btn.setMinimumSize(90, 70)
            btn.setMaximumSize(90, 70)
            btn.setStyleSheet("""
                QPushButton {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                        stop:0 #3498db, stop:1 #2980b9);
                    color: white;
                    border: 2px solid #2980b9;
                    border-radius: 8px;
                    font-weight: bold;
                    font-size: 11px;
                }
                QPushButton:hover {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                        stop:0 #5dade2, stop:1 #3498db);
                    border-color: #5dade2;
                }
                QPushButton:pressed {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                        stop:0 #2980b9, stop:1 #1f618d);
                }
                QPushButton:disabled {
                    background: #bdc3c7;
                    border-color: #95a5a6;
                    color: #7f8c8d;
                }
            """)
            btn.clicked.connect(lambda checked, table_no=i: self.select_table(table_no))
            self.table_buttons[i] = btn
            
            row = (i - 1) // 4
            col = (i - 1) % 4
            table_layout.addWidget(btn, row, col)
        
        layout.addLayout(table_layout)
        
        # Masa durumu
        self.table_status_label = QLabel("🔍 Masa seçin")
        self.table_status_label.setAlignment(Qt.AlignCenter)
        self.table_status_label.setStyleSheet("""
            color: #e74c3c; 
            font-weight: bold; 
            font-size: 13px;
            padding: 8px;
            background-color: #fadbd8;
            border: 1px solid #f1948a;
            border-radius: 6px;
        """)
        layout.addWidget(self.table_status_label)
        
        # Yeni sipariş butonu
        self.new_order_btn = QPushButton("➕ Yeni Sipariş")
        self.new_order_btn.setEnabled(False)
        self.new_order_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                    stop:0 #27ae60, stop:1 #229954);
                color: white;
                border: 2px solid #229954;
                border-radius: 8px;
                font-weight: bold;
                font-size: 13px;
                padding: 10px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                    stop:0 #2ecc71, stop:1 #27ae60);
                border-color: #2ecc71;
            }
            QPushButton:disabled {
                background: #bdc3c7;
                border-color: #95a5a6;
                color: #7f8c8d;
            }
        """)
        self.new_order_btn.clicked.connect(self.create_new_order)
        layout.addWidget(self.new_order_btn)
        
        return panel
    
    def create_order_panel(self):
        """Sipariş yönetim paneli oluştur"""
        panel = QGroupBox("📋 Sipariş Yönetimi")
        panel.setStyleSheet("""
            QGroupBox {
                font-size: 14px;
                font-weight: bold;
                color: #2c3e50;
                border: 2px solid #e74c3c;
                border-radius: 10px;
                margin-top: 10px;
                padding-top: 15px;
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                    stop:0 #fdf2f2, stop:1 #fce4ec);
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 15px;
                padding: 0 8px 0 8px;
                color: #2c3e50;
                font-size: 16px;
            }
        """)
        layout = QVBoxLayout(panel)
        layout.setSpacing(15)
        layout.setContentsMargins(15, 20, 15, 15)
        
        # Sipariş bilgileri
        order_info_frame = QFrame()
        order_info_frame.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                    stop:0 #fff, stop:1 #f8f9fa);
                border: 2px solid #dee2e6;
                border-radius: 8px;
                padding: 10px;
            }
        """)
        order_info_layout = QHBoxLayout(order_info_frame)
        
        self.order_id_label = QLabel("📄 Sipariş: Yok")
        self.order_id_label.setStyleSheet("""
            color: #6c757d;
            font-weight: bold;
            font-size: 13px;
        """)
        
        self.order_total_label = QLabel("💰 Toplam: 0.00 TL")
        self.order_total_label.setStyleSheet("""
            color: #28a745;
            font-weight: bold;
            font-size: 14px;
        """)
        
        order_info_layout.addWidget(self.order_id_label)
        order_info_layout.addStretch()
        order_info_layout.addWidget(self.order_total_label)
        
        layout.addWidget(order_info_frame)
        
        # Tab widget
        tab_widget = QTabWidget()
        tab_widget.setStyleSheet("""
            QTabWidget::pane {
                border: 2px solid #dee2e6;
                border-radius: 8px;
                background-color: white;
            }
            QTabBar::tab {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                    stop:0 #f8f9fa, stop:1 #e9ecef);
                border: 1px solid #dee2e6;
                padding: 8px 16px;
                margin-right: 2px;
                border-top-left-radius: 6px;
                border-top-right-radius: 6px;
            }
            QTabBar::tab:selected {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                    stop:0 #007bff, stop:1 #0056b3);
                color: white;
                border-color: #007bff;
            }
            QTabBar::tab:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                    stop:0 #e9ecef, stop:1 #dee2e6);
            }
        """)
        
        # Sipariş ekleme sekmesi
        order_tab = self.create_order_tab()
        tab_widget.addTab(order_tab, "➕ Sipariş Ekle")
        
        # Sipariş listesi sekmesi
        order_list_tab = self.create_order_list_tab()
        tab_widget.addTab(order_list_tab, "📋 Sipariş Listesi")
        
        layout.addWidget(tab_widget)
        
        # Alt butonlar
        button_frame = QFrame()
        button_frame.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                    stop:0 #f8f9fa, stop:1 #e9ecef);
                border: 2px solid #dee2e6;
                border-radius: 8px;
                padding: 10px;
            }
        """)
        button_layout = QHBoxLayout(button_frame)
        button_layout.setSpacing(10)
        
        self.payment_btn = QPushButton("💳 Ödeme Al")
        self.payment_btn.setEnabled(False)
        self.payment_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                    stop:0 #28a745, stop:1 #1e7e34);
                color: white;
                border: 2px solid #1e7e34;
                border-radius: 8px;
                font-weight: bold;
                font-size: 13px;
                padding: 10px 20px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                    stop:0 #34ce57, stop:1 #28a745);
                border-color: #34ce57;
            }
            QPushButton:disabled {
                background: #bdc3c7;
                border-color: #95a5a6;
                color: #7f8c8d;
            }
        """)
        self.payment_btn.clicked.connect(self.process_payment)
        
        self.print_bill_btn = QPushButton("🖨️ Adisyon Yazdır")
        self.print_bill_btn.setEnabled(False)
        self.print_bill_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                    stop:0 #17a2b8, stop:1 #138496);
                color: white;
                border: 2px solid #138496;
                border-radius: 8px;
                font-weight: bold;
                font-size: 13px;
                padding: 10px 20px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                    stop:0 #20c997, stop:1 #17a2b8);
                border-color: #20c997;
            }
            QPushButton:disabled {
                background: #bdc3c7;
                border-color: #95a5a6;
                color: #7f8c8d;
            }
        """)
        self.print_bill_btn.clicked.connect(self.print_bill)
        
        button_layout.addWidget(self.payment_btn)
        button_layout.addWidget(self.print_bill_btn)
        
        layout.addWidget(button_frame)
        
        return panel
    
    def create_order_tab(self):
        """Sipariş ekleme sekmesi oluştur"""
        widget = QWidget()
        widget.setStyleSheet("""
            QWidget {
                background-color: white;
                border-radius: 8px;
            }
        """)
        layout = QVBoxLayout(widget)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Kategori seçimi
        category_group = QGroupBox("🏷️ Kategori Seçimi")
        category_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                color: #495057;
                border: 2px solid #e9ecef;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 15px;
                background-color: #f8f9fa;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 8px 0 8px;
                color: #495057;
                font-size: 14px;
            }
        """)
        category_layout = QHBoxLayout(category_group)
        category_layout.addWidget(QLabel("📂 Kategori:"))
        
        self.category_combo = QComboBox()
        self.category_combo.setStyleSheet("""
            QComboBox {
                border: 2px solid #ced4da;
                border-radius: 6px;
                padding: 8px;
                background-color: white;
                font-size: 13px;
            }
            QComboBox:focus {
                border-color: #007bff;
            }
            QComboBox::drop-down {
                border: none;
                width: 20px;
            }
            QComboBox::down-arrow {
                image: none;
                border: none;
            }
        """)
        self.category_combo.currentTextChanged.connect(self.load_products)
        category_layout.addWidget(self.category_combo)
        
        layout.addWidget(category_group)
        
        # Ürün seçimi
        product_group = QGroupBox("🍽️ Ürün Seçimi")
        product_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                color: #495057;
                border: 2px solid #e9ecef;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 15px;
                background-color: #f8f9fa;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 8px 0 8px;
                color: #495057;
                font-size: 14px;
            }
        """)
        product_layout = QHBoxLayout(product_group)
        product_layout.addWidget(QLabel("🍕 Ürün:"))
        
        self.product_combo = QComboBox()
        self.product_combo.setStyleSheet("""
            QComboBox {
                border: 2px solid #ced4da;
                border-radius: 6px;
                padding: 8px;
                background-color: white;
                font-size: 13px;
            }
            QComboBox:focus {
                border-color: #007bff;
            }
        """)
        product_layout.addWidget(self.product_combo)
        
        layout.addWidget(product_group)
        
        # Adet ve fiyat
        quantity_group = QGroupBox("🔢 Miktar ve Fiyat")
        quantity_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                color: #495057;
                border: 2px solid #e9ecef;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 15px;
                background-color: #f8f9fa;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 8px 0 8px;
                color: #495057;
                font-size: 14px;
            }
        """)
        quantity_layout = QHBoxLayout(quantity_group)
        
        quantity_layout.addWidget(QLabel("🔢 Adet:"))
        
        self.quantity_spin = QSpinBox()
        self.quantity_spin.setMinimum(1)
        self.quantity_spin.setMaximum(99)
        self.quantity_spin.setValue(1)
        self.quantity_spin.setStyleSheet("""
            QSpinBox {
                border: 2px solid #ced4da;
                border-radius: 6px;
                padding: 8px;
                background-color: white;
                font-size: 13px;
                font-weight: bold;
            }
            QSpinBox:focus {
                border-color: #007bff;
            }
        """)
        self.quantity_spin.valueChanged.connect(self.update_price_display)
        quantity_layout.addWidget(self.quantity_spin)
        
        quantity_layout.addStretch()
        
        quantity_layout.addWidget(QLabel("💰 Fiyat:"))
        self.price_label = QLabel("0.00 TL")
        self.price_label.setStyleSheet("""
            font-weight: bold; 
            color: #28a745;
            font-size: 16px;
            padding: 8px 12px;
            background-color: #d4edda;
            border: 1px solid #c3e6cb;
            border-radius: 6px;
        """)
        quantity_layout.addWidget(self.price_label)
        
        layout.addWidget(quantity_group)
        
        # Notlar
        notes_group = QGroupBox("📝 Notlar")
        notes_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                color: #495057;
                border: 2px solid #e9ecef;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 15px;
                background-color: #f8f9fa;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 8px 0 8px;
                color: #495057;
                font-size: 14px;
            }
        """)
        notes_layout = QVBoxLayout(notes_group)
        
        self.notes_text = QTextEdit()
        self.notes_text.setMaximumHeight(80)
        self.notes_text.setStyleSheet("""
            QTextEdit {
                border: 2px solid #ced4da;
                border-radius: 6px;
                background-color: white;
                font-size: 13px;
                padding: 8px;
            }
            QTextEdit:focus {
                border-color: #007bff;
            }
        """)
        self.notes_text.setPlaceholderText("Ürün için özel notlarınızı buraya yazabilirsiniz...")
        notes_layout.addWidget(self.notes_text)
        
        layout.addWidget(notes_group)
        
        # Ürün ekle butonu
        self.add_product_btn = QPushButton("➕ Siparişe Ekle")
        self.add_product_btn.setEnabled(False)
        self.add_product_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                    stop:0 #007bff, stop:1 #0056b3);
                color: white;
                border: 2px solid #0056b3;
                border-radius: 8px;
                font-weight: bold;
                font-size: 14px;
                padding: 12px 20px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                    stop:0 #0056b3, stop:1 #004085);
                border-color: #004085;
            }
            QPushButton:disabled {
                background: #bdc3c7;
                border-color: #95a5a6;
                color: #7f8c8d;
            }
        """)
        self.add_product_btn.clicked.connect(self.add_product_to_order)
        layout.addWidget(self.add_product_btn)
        
        return widget
    
    def create_order_list_tab(self):
        """Sipariş listesi sekmesi oluştur"""
        widget = QWidget()
        widget.setStyleSheet("""
            QWidget {
                background-color: white;
                border-radius: 8px;
            }
        """)
        layout = QVBoxLayout(widget)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Sipariş tablosu
        table_group = QGroupBox("📋 Sipariş Listesi")
        table_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                color: #495057;
                border: 2px solid #e9ecef;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 15px;
                background-color: #f8f9fa;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 8px 0 8px;
                color: #495057;
                font-size: 14px;
            }
        """)
        table_layout = QVBoxLayout(table_group)
        
        self.order_table = QTableWidget()
        self.order_table.setColumnCount(5)
        self.order_table.setHorizontalHeaderLabels(["🍽️ Ürün", "🔢 Adet", "💰 Birim Fiyat", "💵 Toplam", "📝 Notlar"])
        
        # Tablo ayarları
        self.order_table.setStyleSheet("""
            QTableWidget {
                background-color: white;
                border: 2px solid #dee2e6;
                border-radius: 8px;
                gridline-color: #e9ecef;
                selection-background-color: #e3f2fd;
                font-size: 13px;
            }
            QTableWidget::item {
                padding: 10px;
                border-bottom: 1px solid #f8f9fa;
            }
            QTableWidget::item:selected {
                background-color: #e3f2fd;
                color: #1976d2;
            }
            QHeaderView::section {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                    stop:0 #f8f9fa, stop:1 #e9ecef);
                color: #495057;
                border: 1px solid #dee2e6;
                padding: 10px;
                font-weight: bold;
                font-size: 13px;
            }
        """)
        
        header = self.order_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)
        header.setStretchLastSection(True)
        
        table_layout.addWidget(self.order_table)
        layout.addWidget(table_group)
        
        # Sipariş işlem butonları
        button_group = QGroupBox("🔧 Sipariş İşlemleri")
        button_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                color: #495057;
                border: 2px solid #e9ecef;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 15px;
                background-color: #f8f9fa;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 8px 0 8px;
                color: #495057;
                font-size: 14px;
            }
        """)
        button_layout = QHBoxLayout(button_group)
        button_layout.setSpacing(10)
        
        self.remove_item_btn = QPushButton("🗑️ Seçili Ürünü Çıkar")
        self.remove_item_btn.setEnabled(False)
        self.remove_item_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                    stop:0 #dc3545, stop:1 #c82333);
                color: white;
                border: 2px solid #c82333;
                border-radius: 8px;
                font-weight: bold;
                font-size: 13px;
                padding: 10px 16px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                    stop:0 #e74c3c, stop:1 #dc3545);
                border-color: #e74c3c;
            }
            QPushButton:disabled {
                background: #bdc3c7;
                border-color: #95a5a6;
                color: #7f8c8d;
            }
        """)
        self.remove_item_btn.clicked.connect(self.remove_order_item)
        
        self.clear_order_btn = QPushButton("🧹 Siparişi Temizle")
        self.clear_order_btn.setEnabled(False)
        self.clear_order_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                    stop:0 #ffc107, stop:1 #e0a800);
                color: #212529;
                border: 2px solid #e0a800;
                border-radius: 8px;
                font-weight: bold;
                font-size: 13px;
                padding: 10px 16px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                    stop:0 #ffca2c, stop:1 #ffc107);
                border-color: #ffca2c;
            }
            QPushButton:disabled {
                background: #bdc3c7;
                border-color: #95a5a6;
                color: #7f8c8d;
            }
        """)
        self.clear_order_btn.clicked.connect(self.clear_order)
        
        button_layout.addWidget(self.remove_item_btn)
        button_layout.addWidget(self.clear_order_btn)
        
        layout.addWidget(button_group)
        
        return widget
    
    def connect_database(self):
        """Veritabanına bağlan"""
        if self.db.connect():
            self.db.create_tables()
            self.load_categories()
            self.statusBar().showMessage("Veritabanına bağlandı")
        else:
            QMessageBox.critical(self, "Hata", "Veritabanına bağlanılamadı!")
    
    def load_categories(self):
        """Kategorileri yükle"""
        categories = self.db.get_categories()
        if categories:
            self.category_combo.clear()
            self.category_combo.addItem("Tüm Kategoriler", 0)
            for cat_id, cat_name in categories:
                self.category_combo.addItem(cat_name, cat_id)
    
    def load_products(self):
        """Ürünleri yükle"""
        category_id = self.category_combo.currentData()
        
        if category_id == 0:  # Tüm kategoriler
            products = self.db.get_products()
        else:
            query = """
                SELECT u.id, u.ad, k.ad as kategori, u.fiyat, u.aciklama 
                FROM urunler u 
                JOIN kategoriler k ON u.kategori_id = k.id 
                WHERE u.aktif = TRUE AND u.kategori_id = %s
                ORDER BY u.ad
            """
            products = self.db.execute_query(query, (category_id,))
        
        self.product_combo.clear()
        if products:
            for product in products:
                product_id, name, category, price, description = product
                self.product_combo.addItem(f"{name} - {price:.2f} TL", (product_id, price))
        
        # Ürün seçildiğinde fiyatı güncelle
        self.product_combo.currentTextChanged.connect(self.update_price_display)
    
    def update_price_display(self):
        """Ürün seçildiğinde fiyatı güncelle"""
        product_data = self.product_combo.currentData()
        if product_data:
            product_id, price = product_data
            quantity = self.quantity_spin.value()
            total_price = price * quantity
            self.price_label.setText(f"{total_price:.2f} TL")
        else:
            self.price_label.setText("0.00 TL")
    
    def select_table(self, table_no):
        """Masa seç"""
        self.current_table_id = table_no
        
        # Masa durumunu güncelle
        tables = self.db.get_tables()
        for table in tables:
            if table[1] == table_no:  # masa_no
                table_id, _, status = table
                self.current_table_id = table_id
                break
        
        # Buton renklerini güncelle
        for btn_no, btn in self.table_buttons.items():
            if btn_no == table_no:
                btn.setStyleSheet("""
                    QPushButton {
                        background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                            stop:0 #e74c3c, stop:1 #c0392b);
                        color: white;
                        border: 2px solid #c0392b;
                        border-radius: 8px;
                        font-weight: bold;
                        font-size: 11px;
                    }
                """)
            else:
                btn.setStyleSheet("""
                    QPushButton {
                        background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                            stop:0 #3498db, stop:1 #2980b9);
                        color: white;
                        border: 2px solid #2980b9;
                        border-radius: 8px;
                        font-weight: bold;
                        font-size: 11px;
                    }
                    QPushButton:hover {
                        background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                            stop:0 #5dade2, stop:1 #3498db);
                        border-color: #5dade2;
                    }
                """)
        
        self.table_status_label.setText(f"✅ Masa {table_no} seçildi")
        self.table_status_label.setStyleSheet("""
            color: #27ae60; 
            font-weight: bold; 
            font-size: 13px;
            padding: 8px;
            background-color: #d5f4e6;
            border: 1px solid #a9dfbf;
            border-radius: 6px;
        """)
        self.new_order_btn.setEnabled(True)
        
        # Mevcut siparişi kontrol et
        self.check_existing_order()
    
    def check_existing_order(self):
        """Mevcut siparişi kontrol et"""
        if not self.current_table_id:
            return
        
        query = """
            SELECT id, toplam_tutar, durum 
            FROM siparisler 
            WHERE masa_id = %s AND durum = 'aktif'
        """
        result = self.db.execute_query(query, (self.current_table_id,))
        
        if result:
            order_id, total, status = result[0]
            self.current_order_id = order_id
            self.order_id_label.setText(f"Sipariş: #{order_id}")
            self.order_total_label.setText(f"Toplam: {total:.2f} TL")
            self.load_order_items()
            self.payment_btn.setEnabled(True)
            self.print_bill_btn.setEnabled(True)
        else:
            self.current_order_id = None
            self.order_id_label.setText("Sipariş: Yok")
            self.order_total_label.setText("Toplam: 0.00 TL")
            self.order_table.setRowCount(0)
            self.payment_btn.setEnabled(False)
            self.print_bill_btn.setEnabled(False)
    
    def create_new_order(self):
        """Yeni sipariş oluştur"""
        if not self.current_table_id:
            QMessageBox.warning(self, "Uyarı", "Lütfen önce bir masa seçin!")
            return
        
        order_id = self.db.create_order(self.current_table_id)
        if order_id:
            self.current_order_id = order_id
            self.order_id_label.setText(f"Sipariş: #{order_id}")
            self.order_total_label.setText("Toplam: 0.00 TL")
            self.order_table.setRowCount(0)
            self.payment_btn.setEnabled(True)
            self.print_bill_btn.setEnabled(True)
            self.add_product_btn.setEnabled(True)
            self.clear_order_btn.setEnabled(True)
            self.statusBar().showMessage(f"Yeni sipariş oluşturuldu: #{order_id}")
        else:
            QMessageBox.critical(self, "Hata", "Sipariş oluşturulamadı!")
    
    def add_product_to_order(self):
        """Siparişe ürün ekle"""
        if not self.current_order_id:
            QMessageBox.warning(self, "Uyarı", "Önce bir sipariş oluşturun!")
            return
        
        product_data = self.product_combo.currentData()
        if not product_data:
            QMessageBox.warning(self, "Uyarı", "Lütfen bir ürün seçin!")
            return
        
        product_id, price = product_data
        quantity = self.quantity_spin.value()
        notes = self.notes_text.toPlainText().strip()
        
        if self.db.add_order_item(self.current_order_id, product_id, quantity, notes):
            self.db.update_order_total(self.current_order_id)
            self.load_order_items()
            self.update_order_total()
            self.notes_text.clear()
            self.quantity_spin.setValue(1)
            self.statusBar().showMessage("Ürün siparişe eklendi")
        else:
            QMessageBox.critical(self, "Hata", "Ürün eklenemedi!")
    
    def load_order_items(self):
        """Sipariş ürünlerini yükle"""
        if not self.current_order_id:
            return
        
        items = self.db.get_order_details(self.current_order_id)
        self.order_table.setRowCount(len(items))
        
        for row, item in enumerate(items):
            item_id, product_name, quantity, unit_price, total_price, notes = item
            
            self.order_table.setItem(row, 0, QTableWidgetItem(product_name))
            self.order_table.setItem(row, 1, QTableWidgetItem(str(quantity)))
            self.order_table.setItem(row, 2, QTableWidgetItem(f"{unit_price:.2f}"))
            self.order_table.setItem(row, 3, QTableWidgetItem(f"{total_price:.2f}"))
            self.order_table.setItem(row, 4, QTableWidgetItem(notes or ""))
    
    def update_order_total(self):
        """Sipariş toplamını güncelle"""
        if not self.current_order_id:
            return
        
        query = "SELECT toplam_tutar FROM siparisler WHERE id = %s"
        result = self.db.execute_query(query, (self.current_order_id,))
        
        if result:
            total = result[0][0]
            self.order_total_label.setText(f"Toplam: {total:.2f} TL")
    
    def remove_order_item(self):
        """Seçili ürünü siparişten çıkar"""
        current_row = self.order_table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "Uyarı", "Lütfen çıkarılacak ürünü seçin!")
            return
        
        if not self.current_order_id:
            QMessageBox.warning(self, "Uyarı", "Aktif sipariş bulunamadı!")
            return
        
        # Sipariş detay ID'sini al
        query = """
            SELECT sd.id 
            FROM siparis_detaylari sd
            WHERE sd.siparis_id = %s
            ORDER BY sd.created_at
            LIMIT 1 OFFSET %s
        """
        result = self.db.execute_query(query, (self.current_order_id, current_row))
        
        if not result:
            QMessageBox.warning(self, "Uyarı", "Sipariş detayı bulunamadı!")
            return
        
        item_id = result[0][0]
        
        # Onay al
        reply = QMessageBox.question(self, "Onay", 
                                   "Bu ürünü siparişten çıkarmak istediğinizden emin misiniz?",
                                   QMessageBox.Yes | QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            # Sipariş detayını sil
            if self.db.remove_order_item(item_id):
                # Toplamı güncelle
                self.db.update_order_total(self.current_order_id)
                self.load_order_items()
                self.update_order_total()
                self.statusBar().showMessage("Ürün siparişten çıkarıldı")
            else:
                QMessageBox.critical(self, "Hata", "Ürün çıkarılamadı!")
    
    def clear_order(self):
        """Siparişi temizle"""
        if not self.current_order_id:
            return
        
        reply = QMessageBox.question(self, "Onay", "Siparişi temizlemek istediğinizden emin misiniz?",
                                   QMessageBox.Yes | QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            # Sipariş detaylarını sil
            query = "DELETE FROM siparis_detaylari WHERE siparis_id = %s"
            self.db.execute_query(query, (self.current_order_id,))
            
            # Toplamı güncelle
            self.db.update_order_total(self.current_order_id)
            
            self.load_order_items()
            self.update_order_total()
            self.statusBar().showMessage("Sipariş temizlendi")
    
    def process_payment(self):
        """Ödeme işlemi"""
        if not self.current_order_id:
            QMessageBox.warning(self, "Uyarı", "Önce bir sipariş oluşturun!")
            return
        
        # Sipariş toplamını al
        query = "SELECT toplam_tutar FROM siparisler WHERE id = %s"
        result = self.db.execute_query(query, (self.current_order_id,))
        
        if not result:
            QMessageBox.critical(self, "Hata", "Sipariş bilgileri alınamadı!")
            return
        
        order_total = result[0][0]
        
        if order_total <= 0:
            QMessageBox.warning(self, "Uyarı", "Sipariş toplamı 0 TL!")
            return
        
        # Ödeme penceresini aç
        dialog = PaymentDialog(self.current_order_id, order_total, self)
        dialog.payment_completed.connect(self.on_payment_completed)
        dialog.exec_()
    
    def print_bill(self):
        """Adisyon yazdır"""
        if not self.current_order_id:
            QMessageBox.warning(self, "Uyarı", "Önce bir sipariş oluşturun!")
            return
        
        # Adisyon yazdırma penceresini aç
        dialog = BillPrintDialog(self.current_order_id, self)
        dialog.exec_()
    
    def on_payment_completed(self, order_id):
        """Ödeme tamamlandığında"""
        self.current_order_id = None
        self.current_table_id = None
        
        # Arayüzü sıfırla
        self.order_id_label.setText("Sipariş: Yok")
        self.order_total_label.setText("Toplam: 0.00 TL")
        self.order_table.setRowCount(0)
        self.payment_btn.setEnabled(False)
        self.print_bill_btn.setEnabled(False)
        self.add_product_btn.setEnabled(False)
        self.clear_order_btn.setEnabled(False)
        
        # Masa butonlarını sıfırla
        for btn in self.table_buttons.values():
            btn.setStyleSheet("""
                QPushButton {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                        stop:0 #3498db, stop:1 #2980b9);
                    color: white;
                    border: 2px solid #2980b9;
                    border-radius: 8px;
                    font-weight: bold;
                    font-size: 11px;
                }
                QPushButton:hover {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                        stop:0 #5dade2, stop:1 #3498db);
                    border-color: #5dade2;
                }
            """)
        
        self.table_status_label.setText("🔍 Masa seçin")
        self.table_status_label.setStyleSheet("""
            color: #e74c3c; 
            font-weight: bold; 
            font-size: 13px;
            padding: 8px;
            background-color: #fadbd8;
            border: 1px solid #f1948a;
            border-radius: 6px;
        """)
        self.new_order_btn.setEnabled(False)
        
        self.statusBar().showMessage("Ödeme tamamlandı, masa boşaltıldı")
    
    def open_product_management(self):
        """Ürün yönetimi penceresini aç"""
        dialog = ProductManagementDialog(self)
        dialog.product_updated.connect(self.load_categories)
        dialog.product_updated.connect(self.load_products)
        dialog.exec_()
    
    def open_category_management(self):
        """Kategori yönetimi penceresini aç"""
        dialog = CategoryManagementDialog(self)
        dialog.category_updated.connect(self.load_categories)
        dialog.exec_()
    
    def open_reports(self):
        """Raporlar penceresini aç"""
        dialog = ReportsDialog(self)
        dialog.exec_()
    
    def show_about(self):
        """Hakkında penceresi"""
        QMessageBox.about(self, "Hakkında", 
                         f"{APP_CONFIG['title']} v{APP_CONFIG['version']}\n\n"
                         "PyQt5 ve MySQL ile geliştirilmiş masaüstü adisyon sistemi")
    
    def closeEvent(self, event):
        """Uygulama kapatılırken"""
        self.db.disconnect()
        event.accept()

def main():
    app = QApplication(sys.argv)
    
    # Uygulama stilini ayarla
    app.setStyle('Fusion')
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
