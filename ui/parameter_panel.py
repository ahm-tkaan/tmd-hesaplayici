# ui/parameter_panel.py
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QGridLayout, QLabel, QLineEdit, 
                            QGroupBox, QPushButton, QMessageBox)
from PyQt6.QtCore import pyqtSignal, Qt
from PyQt6.QtGui import QFont, QIcon, QPixmap
from core.tmd_calculator import TMDCalculator

class ParameterPanel(QWidget):
    """TMD parametre paneli sınıfı"""
    
    # Parametre hesaplandığında sinyal gönder
    parameters_calculated = pyqtSignal(dict)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Varsayılan değerler
        self.m1 = 1.0       # (kg) Ana sistem kütlesi
        self.m2 = 0.2       # (kg) TMD kütlesi
        self.w1 = 707       # (rad/s) Ana sistem doğal frekansı
        self.c1 = 0         # Ana sistemin sönümü
        
        # TMD hesaplayıcı oluştur
        self.calculator = TMDCalculator(self.m1, self.m2, self.w1, self.c1)
        
        self.initUI()
    
    def initUI(self):
        """Kullanıcı arayüzünü oluşturur"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Parametre girişi grubu
        param_group = QGroupBox("Sistem Parametreleri")
        param_layout = QGridLayout()
        
        # Logo ekle
        try:
            logo_label = QLabel()
            logo_pixmap = QIcon("assets/logo.png").pixmap(QSize(150, 150))
            logo_label.setPixmap(logo_pixmap)
            logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            param_layout.addWidget(logo_label, 0, 0, 1, 2)
        except:
            # Logo yoksa geçici bir başlık koy
            header_label = QLabel("TMD Analiz Programı")
            header_label.setFont(QFont("Arial", 14, QFont.Weight.Bold))
            header_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            param_layout.addWidget(header_label, 0, 0, 1, 2)
        
        # Ana sistem parametreler
        param_layout.addWidget(QLabel("Ana Sistem (Bara):"), 1, 0)
        param_layout.addWidget(QLabel("m₁ (kg):"), 2, 0)
        self.m1_input = QLineEdit(str(self.m1))
        param_layout.addWidget(self.m1_input, 2, 1)
        
        param_layout.addWidget(QLabel("w₁ (rad/s):"), 3, 0)
        self.w1_input = QLineEdit(str(self.w1))
        param_layout.addWidget(self.w1_input, 3, 1)
        
        param_layout.addWidget(QLabel("c₁:"), 4, 0)
        self.c1_input = QLineEdit(str(self.c1))
        param_layout.addWidget(self.c1_input, 4, 1)
        
        # TMD parametreler
        param_layout.addWidget(QLabel("TMD Sistemi:"), 5, 0)
        param_layout.addWidget(QLabel("m₂ (kg):"), 6, 0)
        self.m2_input = QLineEdit(str(self.m2))
        param_layout.addWidget(self.m2_input, 6, 1)
        
        # Hesaplama butonu
        calc_button = QPushButton("Parametreleri Hesapla")
        calc_button.clicked.connect(self.calculate_parameters)
        param_layout.addWidget(calc_button, 7, 0, 1, 2)
        
        param_group.setLayout(param_layout)
        
        # Hesaplanan parametreler
        self.result_group = QGroupBox("Hesaplanan Parametreler")
        result_layout = QGridLayout()
        
        result_layout.addWidget(QLabel("μ (Kütle Oranı):"), 0, 0)
        self.mu_result = QLabel("--")
        result_layout.addWidget(self.mu_result, 0, 1)
        
        result_layout.addWidget(QLabel("k₁ (N/m):"), 1, 0)
        self.k1_result = QLabel("--")
        result_layout.addWidget(self.k1_result, 1, 1)
        
        result_layout.addWidget(QLabel("w₂ₒₚₜ (rad/s):"), 2, 0)
        self.w2_opt_result = QLabel("--")
        result_layout.addWidget(self.w2_opt_result, 2, 1)
        
        result_layout.addWidget(QLabel("k₂ₒₚₜ (N/m):"), 3, 0)
        self.k2_opt_result = QLabel("--")
        result_layout.addWidget(self.k2_opt_result, 3, 1)
        
        result_layout.addWidget(QLabel("ξ₂ₒₚₜ:"), 4, 0)
        self.ksi_2_opt_result = QLabel("--")
        result_layout.addWidget(self.ksi_2_opt_result, 4, 1)
        
        result_layout.addWidget(QLabel("c₂ₒₚₜ (N·s/m):"), 5, 0)
        self.c2_opt_result = QLabel("--")
        result_layout.addWidget(self.c2_opt_result, 5, 1)
        
        self.result_group.setLayout(result_layout)
        
        # Paneli düzene ekle
        layout.addWidget(param_group)
        layout.addWidget(self.result_group)
        layout.addStretch(1)
        
        # Başlangıçta parametreleri hesapla
        self.calculate_parameters()
    
    def calculate_parameters(self):
        """Girilen parametreleri kullanarak TMD hesaplamalarını yapar"""
        try:
            # Parametreleri al
            self.m1 = float(self.m1_input.text())
            self.m2 = float(self.m2_input.text())
            self.w1 = float(self.w1_input.text())
            self.c1 = float(self.c1_input.text())
            
            # Calculator'ı güncelle
            self.calculator = TMDCalculator(self.m1, self.m2, self.w1, self.c1)
            
            # Parametreleri hesapla
            results = self.calculator.calculate_parameters()
            
            # Sonuçları göster
            self.mu_result.setText(f"{results['mu']:.4f}")
            self.k1_result.setText(f"{results['k1']:.2f}")
            self.w2_opt_result.setText(f"{results['w2_opt']:.2f}")
            self.k2_opt_result.setText(f"{results['k2_opt']:.2f}")
            self.ksi_2_opt_result.setText(f"{results['ksi_2_opt']:.4f}")
            self.c2_opt_result.setText(f"{results['c2_opt']:.4f}")
            
            # Sinyal gönder
            self.parameters_calculated.emit(results)
            
            return True
            
        except ValueError as e:
            QMessageBox.warning(self, "Hata", "Lütfen tüm değerleri sayısal olarak giriniz.")
            return False