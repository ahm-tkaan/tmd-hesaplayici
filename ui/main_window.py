# ui/main_window.py
import sys
import os
from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QSplitter)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon

from ui.parameter_panel import ParameterPanel
from ui.graph_panel import GraphPanel

class TMDAnalyzer(QMainWindow):
    """TMD Analiz Programı ana pencere sınıfı"""
    
    def __init__(self):
        super().__init__()
        
        self.initUI()
        
    def initUI(self):
        """Kullanıcı arayüzünü oluşturur"""
        self.setWindowTitle('TMD Analiz Programı')
        self.setGeometry(100, 100, 1200, 800)
        
        # Favicon ayarla
        try:
            icon = QIcon("assets/favicon.png")
            self.setWindowIcon(icon)
        except:
            pass  # Favicon yüklenemezse devam et
        
        # Ana widget
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        
        # Ana layout
        main_layout = QVBoxLayout(main_widget)
        
        # Parametre girişi ve grafik bölgesi için splitter
        splitter = QSplitter(Qt.Orientation.Horizontal)
        main_layout.addWidget(splitter)
        
        # Sol panel - Parametreler
        self.parameter_panel = ParameterPanel()
        
        # Sağ panel - Grafik gösterimi
        self.graph_panel = GraphPanel()
        
        # Parametre hesaplandığında grafik paneline bildir
        self.parameter_panel.parameters_calculated.connect(self.graph_panel.update_parameters)
        
        # Splitter'a panelleri ekleme
        splitter.addWidget(self.parameter_panel)
        splitter.addWidget(self.graph_panel)
        splitter.setSizes([200, 1000])  # Grafik kısmına çok daha fazla alan ayır