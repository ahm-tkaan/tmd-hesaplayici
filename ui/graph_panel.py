# ui/graph_panel.py
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QComboBox, 
                            QGroupBox, QPushButton, QFileDialog, QMessageBox, QTabWidget)
from PyQt6.QtCore import pyqtSignal, Qt
from core.visualizers import MplCanvas, MplCanvas3D, NavigationToolbar, TMDVisualizer
from core.analyzers import TMDAnalyzer

class GraphPanel(QWidget):
    """TMD grafik görüntüleme ve analiz paneli"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # TMD analiz ve görselleştirme sınıflarını oluştur
        self.analyzer = TMDAnalyzer()
        self.visualizer = TMDVisualizer()
        
        # Parametre değerleri
        self.parameters = None
        
        self.initUI()
    
    def initUI(self):
        """Kullanıcı arayüzünü oluşturur"""
        layout = QVBoxLayout(self)
        
        # Analiz kontrolleri
        control_layout = QHBoxLayout()
        
        # Analiz türü seçimi
        analysis_group = QGroupBox("Analiz Türü")
        analysis_layout = QVBoxLayout()
        
        self.analysis_combo = QComboBox()
        self.analysis_combo.addItems([
            "Frekans Oranı Değişimi Analizi", 
            "Sönüm Oranı Değişimi Analizi", 
            "Kütle Oranı Değişimi Analizi"
        ])
        analysis_layout.addWidget(self.analysis_combo)
        
        # Analiz butonu
        analyze_button = QPushButton("Analiz Et")
        analyze_button.clicked.connect(self.run_analysis)
        analysis_layout.addWidget(analyze_button)
        
        # Grafik kaydetme butonu
        save_button = QPushButton("Grafiği Kaydet")
        save_button.clicked.connect(self.save_plot)
        analysis_layout.addWidget(save_button)
        
        analysis_group.setLayout(analysis_layout)
        control_layout.addWidget(analysis_group)
        
        layout.addLayout(control_layout)
        
        # Sekme widget'ı
        self.tab_widget = QTabWidget()
        
        # 2D grafik sekmesi
        self.canvas = MplCanvas(self, width=5, height=4, dpi=100)
        
        plot_widget = QWidget()
        plot_layout = QVBoxLayout(plot_widget)
        
        # Navigation toolbar için container widget
        toolbar_container = QWidget()
        toolbar_layout = QVBoxLayout(toolbar_container)
        toolbar_layout.setContentsMargins(0, 0, 0, 0)
        
        self.toolbar = NavigationToolbar(self.canvas, toolbar_container)
        toolbar_layout.addWidget(self.toolbar)
        
        plot_layout.addWidget(toolbar_container)
        plot_layout.addWidget(self.canvas)
        
        # 3D grafik sekmesi
        self.canvas3d = MplCanvas3D(self, width=5, height=4, dpi=100)
        
        plot3d_widget = QWidget()
        plot3d_layout = QVBoxLayout(plot3d_widget)
        
        # Navigation toolbar için container widget
        toolbar3d_container = QWidget()
        toolbar3d_layout = QVBoxLayout(toolbar3d_container)
        toolbar3d_layout.setContentsMargins(0, 0, 0, 0)
        
        self.toolbar3d = NavigationToolbar(self.canvas3d, toolbar3d_container)
        toolbar3d_layout.addWidget(self.toolbar3d)
        
        plot3d_layout.addWidget(toolbar3d_container)
        plot3d_layout.addWidget(self.canvas3d)
        
        # Sekmeleri ekleme
        self.tab_widget.addTab(plot_widget, "2D Grafik")
        self.tab_widget.addTab(plot3d_widget, "3D Grafik")
        
        layout.addWidget(self.tab_widget)
    
    def update_parameters(self, parameters):
        """
        TMD parametrelerini günceller
        
        Args:
            parameters (dict): TMD parametrelerini içeren sözlük
        """
        self.parameters = parameters
    
    def run_analysis(self):
        """Seçilen analiz türünü çalıştırır"""
        if not self.parameters:
            QMessageBox.warning(self, "Hata", "Önce parametreleri hesaplamalısınız.")
            return
        
        analysis_type = self.analysis_combo.currentIndex()
        
        if analysis_type == 0:
            self.run_frequency_ratio_analysis()
        elif analysis_type == 1:
            self.run_damping_ratio_analysis()
        elif analysis_type == 2:
            self.run_mass_ratio_analysis()
    
    def run_frequency_ratio_analysis(self):
        """Frekans oranı değişimi analizini çalıştırır"""
        analysis_results = self.analyzer.frequency_ratio_analysis(
            mu=self.parameters['mu'],
            nub=self.parameters.get('c1', 0)
        )
        
        self.visualizer.plot_frequency_ratio(self.canvas, analysis_results)
        self.tab_widget.setCurrentIndex(0)  # 2D grafiğe odaklan
    
    def run_damping_ratio_analysis(self):
        """Sönüm oranı değişimi analizini çalıştırır"""
        analysis_results = self.analyzer.damping_ratio_analysis(
            mu=self.parameters['mu'],
            nub=self.parameters.get('c1', 0)
        )
        
        self.visualizer.plot_damping_ratio(self.canvas, self.canvas3d, analysis_results)
    
    def run_mass_ratio_analysis(self):
        """Kütle oranı değişimi analizini çalıştırır"""
        analysis_results = self.analyzer.mass_ratio_analysis(
            current_mu=self.parameters['mu'],
            nub=self.parameters.get('c1', 0)
        )
        
        self.visualizer.plot_mass_ratio(self.canvas, self.canvas3d, analysis_results)
    
    def save_plot(self):
        """Mevcut aktif grafiği dosyaya kaydeder"""
        file_name, _ = QFileDialog.getSaveFileName(
            self, 
            "Grafiği Kaydet", 
            "", 
            "PNG (*.png);;JPEG (*.jpg *.jpeg);;SVG (*.svg);;PDF (*.pdf)"
        )
        
        if file_name:
            active_tab = self.tab_widget.currentIndex()
            if active_tab == 0:  # 2D grafik
                self.canvas.fig.savefig(file_name, dpi=300, bbox_inches='tight')
            else:  # 3D grafik
                self.canvas3d.fig.savefig(file_name, dpi=300, bbox_inches='tight')
            
            QMessageBox.information(self, "Başarılı", f"Grafik kaydedildi: {file_name}")