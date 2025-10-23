from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QGridLayout,
                             QPushButton, QLabel, QLineEdit, QComboBox,
                             QTableWidget, QTableWidgetItem, QMessageBox,
                             QHeaderView, QGroupBox, QDateEdit, QTabWidget,
                             QTextEdit, QFrame, QCheckBox, QWidget)
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import QFont
from database import DatabaseManager
import logging

logger = logging.getLogger(__name__)

class ReportsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.db = DatabaseManager()
        self.db.connect()
        self.init_ui()
    
    def init_ui(self):
        """Raporlar arayüzünü oluştur"""
        self.setWindowTitle("📊 Satış Raporları")
        self.setModal(True)
        self.setMinimumSize(1000, 700)
        
        # Modern stil uygula
        self.setStyleSheet("""
            QDialog {
                background-color: #f8f9fa;
            }
            QWidget {
                font-family: 'Segoe UI', Arial, sans-serif;
            }
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                    stop:0 #007bff, stop:1 #0056b3);
                color: white;
                border: 2px solid #0056b3;
                border-radius: 8px;
                font-weight: bold;
                font-size: 13px;
                padding: 10px 20px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                    stop:0 #0056b3, stop:1 #004085);
                border-color: #004085;
            }
            QGroupBox {
                font-weight: bold;
                color: #495057;
                border: 2px solid #dee2e6;
                border-radius: 10px;
                margin-top: 10px;
                padding-top: 15px;
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                    stop:0 #fff, stop:1 #f8f9fa);
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 15px;
                padding: 0 8px 0 8px;
                color: #495057;
                font-size: 14px;
            }
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
            QTabWidget::pane {
                border: 2px solid #dee2e6;
                border-radius: 8px;
                background-color: white;
            }
            QTabBar::tab {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                    stop:0 #f8f9fa, stop:1 #e9ecef);
                border: 1px solid #dee2e6;
                padding: 10px 20px;
                margin-right: 2px;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
                font-weight: bold;
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
            QComboBox, QDateEdit, QSpinBox {
                border: 2px solid #ced4da;
                border-radius: 6px;
                padding: 8px;
                background-color: white;
                font-size: 13px;
            }
            QComboBox:focus, QDateEdit:focus, QSpinBox:focus {
                border-color: #007bff;
            }
            QLabel {
                color: #495057;
                font-weight: bold;
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Başlık
        title = QLabel("📊 Satış Raporları")
        title.setFont(QFont("Segoe UI", 18, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("""
            color: #2c3e50;
            padding: 15px;
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                stop:0 #e3f2fd, stop:1 #bbdefb);
            border: 2px solid #2196f3;
            border-radius: 10px;
        """)
        layout.addWidget(title)
        
        # Tab widget
        tab_widget = QTabWidget()
        
        # Günlük rapor sekmesi
        daily_tab = self.create_daily_report_tab()
        tab_widget.addTab(daily_tab, "📅 Günlük Rapor")
        
        # Aylık rapor sekmesi
        monthly_tab = self.create_monthly_report_tab()
        tab_widget.addTab(monthly_tab, "📆 Aylık Rapor")
        
        # Ürün raporu sekmesi
        product_tab = self.create_product_report_tab()
        tab_widget.addTab(product_tab, "🍽️ Ürün Raporu")
        
        # Masa raporu sekmesi
        table_tab = self.create_table_report_tab()
        tab_widget.addTab(table_tab, "🪑 Masa Raporu")
        
        layout.addWidget(tab_widget)
        
        # Alt butonlar
        button_frame = QFrame()
        button_frame.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                    stop:0 #f8f9fa, stop:1 #e9ecef);
                border: 2px solid #dee2e6;
                border-radius: 8px;
                padding: 15px;
            }
        """)
        button_layout = QHBoxLayout(button_frame)
        button_layout.setSpacing(15)
        
        self.export_btn = QPushButton("📊 Excel'e Aktar")
        self.export_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                    stop:0 #28a745, stop:1 #1e7e34);
                color: white;
                border: 2px solid #1e7e34;
                border-radius: 8px;
                font-weight: bold;
                font-size: 13px;
                padding: 12px 20px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                    stop:0 #34ce57, stop:1 #28a745);
                border-color: #34ce57;
            }
        """)
        self.export_btn.clicked.connect(self.export_to_excel)
        
        self.print_btn = QPushButton("🖨️ Yazdır")
        self.print_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                    stop:0 #17a2b8, stop:1 #138496);
                color: white;
                border: 2px solid #138496;
                border-radius: 8px;
                font-weight: bold;
                font-size: 13px;
                padding: 12px 20px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                    stop:0 #20c997, stop:1 #17a2b8);
                border-color: #20c997;
            }
        """)
        self.print_btn.clicked.connect(self.print_report)
        
        self.close_btn = QPushButton("❌ Kapat")
        self.close_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                    stop:0 #6c757d, stop:1 #5a6268);
                color: white;
                border: 2px solid #5a6268;
                border-radius: 8px;
                font-weight: bold;
                font-size: 13px;
                padding: 12px 20px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                    stop:0 #868e96, stop:1 #6c757d);
                border-color: #868e96;
            }
        """)
        self.close_btn.clicked.connect(self.close)
        
        button_layout.addWidget(self.export_btn)
        button_layout.addWidget(self.print_btn)
        button_layout.addStretch()
        button_layout.addWidget(self.close_btn)
        
        layout.addWidget(button_frame)
    
    def create_daily_report_tab(self):
        """Günlük rapor sekmesi oluştur"""
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
        
        # Tarih seçimi
        date_group = QGroupBox("📅 Tarih Seçimi")
        date_group.setStyleSheet("""
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
        date_layout = QHBoxLayout(date_group)
        date_layout.addWidget(QLabel("📅 Tarih:"))
        
        self.daily_date = QDateEdit()
        self.daily_date.setDate(QDate.currentDate())
        self.daily_date.setCalendarPopup(True)
        self.daily_date.setStyleSheet("""
            QDateEdit {
                border: 2px solid #ced4da;
                border-radius: 6px;
                padding: 8px;
                background-color: white;
                font-size: 13px;
            }
            QDateEdit:focus {
                border-color: #007bff;
            }
        """)
        date_layout.addWidget(self.daily_date)
        
        self.generate_daily_btn = QPushButton("📊 Rapor Oluştur")
        self.generate_daily_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                    stop:0 #007bff, stop:1 #0056b3);
                color: white;
                border: 2px solid #0056b3;
                border-radius: 8px;
                font-weight: bold;
                font-size: 13px;
                padding: 10px 20px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                    stop:0 #0056b3, stop:1 #004085);
                border-color: #004085;
            }
        """)
        self.generate_daily_btn.clicked.connect(self.generate_daily_report)
        date_layout.addWidget(self.generate_daily_btn)
        
        layout.addWidget(date_group)
        
        # Rapor tablosu
        table_group = QGroupBox("📋 Günlük Satış Raporu")
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
        
        self.daily_table = QTableWidget()
        self.daily_table.setColumnCount(6)
        self.daily_table.setHorizontalHeaderLabels([
            "📄 Sipariş No", "🪑 Masa", "💰 Toplam", "💳 Ödeme Tipi", "🕐 Saat", "📊 Durum"
        ])
        
        header = self.daily_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)
        
        table_layout.addWidget(self.daily_table)
        layout.addWidget(table_group)
        
        # Özet bilgiler
        summary_group = QGroupBox("📊 Özet Bilgiler")
        summary_group.setStyleSheet("""
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
        summary_layout = QHBoxLayout(summary_group)
        
        self.daily_total_label = QLabel("💰 Toplam Satış: 0.00 TL")
        self.daily_total_label.setStyleSheet("""
            color: #28a745;
            font-weight: bold;
            font-size: 14px;
            padding: 10px;
            background-color: #d4edda;
            border: 1px solid #c3e6cb;
            border-radius: 6px;
        """)
        
        self.daily_count_label = QLabel("📊 Sipariş Sayısı: 0")
        self.daily_count_label.setStyleSheet("""
            color: #007bff;
            font-weight: bold;
            font-size: 14px;
            padding: 10px;
            background-color: #d1ecf1;
            border: 1px solid #bee5eb;
            border-radius: 6px;
        """)
        
        summary_layout.addWidget(self.daily_total_label)
        summary_layout.addWidget(self.daily_count_label)
        
        layout.addWidget(summary_group)
        
        return widget
    
    def create_monthly_report_tab(self):
        """Aylık rapor sekmesi oluştur"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Ay seçimi
        month_widget = QWidget()
        month_layout = QHBoxLayout(month_widget)
        month_layout.addWidget(QLabel("Ay:"))
        
        self.month_combo = QComboBox()
        months = ["Ocak", "Şubat", "Mart", "Nisan", "Mayıs", "Haziran",
                 "Temmuz", "Ağustos", "Eylül", "Ekim", "Kasım", "Aralık"]
        self.month_combo.addItems(months)
        self.month_combo.setCurrentIndex(QDate.currentDate().month() - 1)
        
        month_layout.addWidget(self.month_combo)
        
        self.year_spin = QComboBox()
        current_year = QDate.currentDate().year()
        for year in range(current_year - 5, current_year + 1):
            self.year_spin.addItem(str(year))
        self.year_spin.setCurrentText(str(current_year))
        
        month_layout.addWidget(self.year_spin)
        
        self.generate_monthly_btn = QPushButton("Rapor Oluştur")
        self.generate_monthly_btn.clicked.connect(self.generate_monthly_report)
        month_layout.addWidget(self.generate_monthly_btn)
        
        layout.addWidget(month_widget)
        
        # Rapor tablosu
        self.monthly_table = QTableWidget()
        self.monthly_table.setColumnCount(3)
        self.monthly_table.setHorizontalHeaderLabels(["Gün", "Sipariş Sayısı", "Toplam Satış"])
        
        header = self.monthly_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)
        
        layout.addWidget(self.monthly_table)
        
        # Özet bilgiler
        summary_widget = QWidget()
        summary_layout = QHBoxLayout(summary_widget)
        
        self.monthly_total_label = QLabel("Aylık Toplam: 0.00 TL")
        self.monthly_avg_label = QLabel("Günlük Ortalama: 0.00 TL")
        
        summary_layout.addWidget(self.monthly_total_label)
        summary_layout.addWidget(self.monthly_avg_label)
        
        layout.addWidget(summary_widget)
        
        return widget
    
    def create_product_report_tab(self):
        """Ürün raporu sekmesi oluştur"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Tarih aralığı seçimi
        date_range_widget = QWidget()
        date_range_layout = QHBoxLayout(date_range_widget)
        date_range_layout.addWidget(QLabel("Başlangıç:"))
        
        self.start_date = QDateEdit()
        self.start_date.setDate(QDate.currentDate().addDays(-30))
        self.start_date.setCalendarPopup(True)
        date_range_layout.addWidget(self.start_date)
        
        date_range_layout.addWidget(QLabel("Bitiş:"))
        
        self.end_date = QDateEdit()
        self.end_date.setDate(QDate.currentDate())
        self.end_date.setCalendarPopup(True)
        date_range_layout.addWidget(self.end_date)
        
        self.generate_product_btn = QPushButton("Rapor Oluştur")
        self.generate_product_btn.clicked.connect(self.generate_product_report)
        date_range_layout.addWidget(self.generate_product_btn)
        
        layout.addWidget(date_range_widget)
        
        # Rapor tablosu
        self.product_table = QTableWidget()
        self.product_table.setColumnCount(5)
        self.product_table.setHorizontalHeaderLabels([
            "Ürün", "Kategori", "Satılan Adet", "Toplam Tutar", "Ortalama Fiyat"
        ])
        
        header = self.product_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)
        
        layout.addWidget(self.product_table)
        
        return widget
    
    def create_table_report_tab(self):
        """Masa raporu sekmesi oluştur"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Tarih seçimi
        table_date_widget = QWidget()
        table_date_layout = QHBoxLayout(table_date_widget)
        table_date_layout.addWidget(QLabel("Tarih:"))
        
        self.table_date = QDateEdit()
        self.table_date.setDate(QDate.currentDate())
        self.table_date.setCalendarPopup(True)
        table_date_layout.addWidget(self.table_date)
        
        self.generate_table_btn = QPushButton("Rapor Oluştur")
        self.generate_table_btn.clicked.connect(self.generate_table_report)
        table_date_layout.addWidget(self.generate_table_btn)
        
        layout.addWidget(table_date_widget)
        
        # Rapor tablosu
        self.table_report_table = QTableWidget()
        self.table_report_table.setColumnCount(4)
        self.table_report_table.setHorizontalHeaderLabels([
            "Masa No", "Sipariş Sayısı", "Toplam Satış", "Ortalama Sipariş"
        ])
        
        header = self.table_report_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)
        
        layout.addWidget(self.table_report_table)
        
        return widget
    
    def generate_daily_report(self):
        """Günlük rapor oluştur"""
        selected_date = self.daily_date.date().toString("yyyy-MM-dd")
        
        query = """
            SELECT s.id, m.masa_no, s.toplam_tutar, o.odeme_tipi, s.created_at, s.durum
            FROM siparisler s
            JOIN masalar m ON s.masa_id = m.id
            LEFT JOIN odemeler o ON s.id = o.siparis_id
            WHERE DATE(s.created_at) = %s AND s.durum = 'kapatildi'
            ORDER BY s.created_at
        """
        
        results = self.db.execute_query(query, (selected_date,))
        
        if not results:
            self.daily_table.setRowCount(0)
            self.daily_total_label.setText("Toplam Satış: 0.00 TL")
            self.daily_count_label.setText("Sipariş Sayısı: 0")
            return
        
        self.daily_table.setRowCount(len(results))
        
        total_sales = 0
        for row, result in enumerate(results):
            order_id, table_no, total, payment_type, created_at, status = result
            
            self.daily_table.setItem(row, 0, QTableWidgetItem(f"#{order_id}"))
            self.daily_table.setItem(row, 1, QTableWidgetItem(str(table_no)))
            self.daily_table.setItem(row, 2, QTableWidgetItem(f"{total:.2f} TL"))
            self.daily_table.setItem(row, 3, QTableWidgetItem(payment_type or "Nakit"))
            self.daily_table.setItem(row, 4, QTableWidgetItem(created_at.strftime("%H:%M")))
            self.daily_table.setItem(row, 5, QTableWidgetItem(status))
            
            total_sales += total
        
        self.daily_total_label.setText(f"Toplam Satış: {total_sales:.2f} TL")
        self.daily_count_label.setText(f"Sipariş Sayısı: {len(results)}")
    
    def generate_monthly_report(self):
        """Aylık rapor oluştur"""
        month = self.month_combo.currentIndex() + 1
        year = int(self.year_spin.currentText())
        
        query = """
            SELECT DAY(s.created_at) as gun, COUNT(*) as siparis_sayisi, SUM(s.toplam_tutar) as toplam
            FROM siparisler s
            WHERE MONTH(s.created_at) = %s AND YEAR(s.created_at) = %s AND s.durum = 'kapatildi'
            GROUP BY DAY(s.created_at)
            ORDER BY gun
        """
        
        results = self.db.execute_query(query, (month, year))
        
        if not results:
            self.monthly_table.setRowCount(0)
            self.monthly_total_label.setText("Aylık Toplam: 0.00 TL")
            self.monthly_avg_label.setText("Günlük Ortalama: 0.00 TL")
            return
        
        self.monthly_table.setRowCount(len(results))
        
        total_monthly = 0
        for row, result in enumerate(results):
            day, order_count, daily_total = result
            
            self.monthly_table.setItem(row, 0, QTableWidgetItem(f"{day}. Gün"))
            self.monthly_table.setItem(row, 1, QTableWidgetItem(str(order_count)))
            self.monthly_table.setItem(row, 2, QTableWidgetItem(f"{daily_total:.2f} TL"))
            
            total_monthly += daily_total
        
        avg_daily = total_monthly / len(results) if results else 0
        
        self.monthly_total_label.setText(f"Aylık Toplam: {total_monthly:.2f} TL")
        self.monthly_avg_label.setText(f"Günlük Ortalama: {avg_daily:.2f} TL")
    
    def generate_product_report(self):
        """Ürün raporu oluştur"""
        start_date = self.start_date.date().toString("yyyy-MM-dd")
        end_date = self.end_date.date().toString("yyyy-MM-dd")
        
        query = """
            SELECT u.ad, k.ad as kategori, SUM(sd.adet) as toplam_adet, 
                   SUM(sd.toplam_fiyat) as toplam_tutar, AVG(sd.birim_fiyat) as ortalama_fiyat
            FROM siparis_detaylari sd
            JOIN urunler u ON sd.urun_id = u.id
            JOIN kategoriler k ON u.kategori_id = k.id
            JOIN siparisler s ON sd.siparis_id = s.id
            WHERE DATE(s.created_at) BETWEEN %s AND %s AND s.durum = 'kapatildi'
            GROUP BY u.id, u.ad, k.ad
            ORDER BY toplam_tutar DESC
        """
        
        results = self.db.execute_query(query, (start_date, end_date))
        
        if not results:
            self.product_table.setRowCount(0)
            return
        
        self.product_table.setRowCount(len(results))
        
        for row, result in enumerate(results):
            product_name, category, total_quantity, total_amount, avg_price = result
            
            self.product_table.setItem(row, 0, QTableWidgetItem(product_name))
            self.product_table.setItem(row, 1, QTableWidgetItem(category))
            self.product_table.setItem(row, 2, QTableWidgetItem(str(total_quantity)))
            self.product_table.setItem(row, 3, QTableWidgetItem(f"{total_amount:.2f} TL"))
            self.product_table.setItem(row, 4, QTableWidgetItem(f"{avg_price:.2f} TL"))
    
    def generate_table_report(self):
        """Masa raporu oluştur"""
        selected_date = self.table_date.date().toString("yyyy-MM-dd")
        
        query = """
            SELECT m.masa_no, COUNT(s.id) as siparis_sayisi, 
                   SUM(s.toplam_tutar) as toplam_satis, AVG(s.toplam_tutar) as ortalama_siparis
            FROM masalar m
            LEFT JOIN siparisler s ON m.id = s.masa_id AND DATE(s.created_at) = %s AND s.durum = 'kapatildi'
            GROUP BY m.id, m.masa_no
            ORDER BY m.masa_no
        """
        
        results = self.db.execute_query(query, (selected_date,))
        
        if not results:
            self.table_report_table.setRowCount(0)
            return
        
        self.table_report_table.setRowCount(len(results))
        
        for row, result in enumerate(results):
            table_no, order_count, total_sales, avg_order = result
            
            self.table_report_table.setItem(row, 0, QTableWidgetItem(f"Masa {table_no}"))
            self.table_report_table.setItem(row, 1, QTableWidgetItem(str(order_count or 0)))
            self.table_report_table.setItem(row, 2, QTableWidgetItem(f"{total_sales or 0:.2f} TL"))
            self.table_report_table.setItem(row, 3, QTableWidgetItem(f"{avg_order or 0:.2f} TL"))
    
    def export_to_excel(self):
        """Excel'e aktar"""
        QMessageBox.information(self, "Bilgi", "Excel aktarım özelliği henüz tamamlanmadı")
    
    def print_report(self):
        """Raporu yazdır"""
        QMessageBox.information(self, "Bilgi", "Yazdırma özelliği henüz tamamlanmadı")
    
    def closeEvent(self, event):
        """Pencere kapatılırken"""
        self.db.disconnect()
        event.accept()
