# main.py
import sys
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QIcon
from ui.main_window import TMDAnalyzer

def main():
    app = QApplication(sys.argv)
    
    # Başlat menüsü için program bilgilerini ayarla
    app.setApplicationName("TMD Analiz Programı")
    app.setApplicationDisplayName("TMD Analiz Programı")
    app.setWindowIcon(QIcon("assets/logo.png"))  # Başlat menüsü için logo
    
    ex = TMDAnalyzer()
    ex.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()