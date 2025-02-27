# core/tmd_calculator.py
import numpy as np

class TMDCalculator:
    """TMD hesaplamalarını gerçekleştiren sınıf"""
    
    def __init__(self, m1=1.0, m2=0.2, w1=707, c1=0):
        """
        TMD hesaplama sınıfını oluşturur
        
        Args:
            m1 (float): Ana sistem kütlesi (kg)
            m2 (float): TMD kütlesi (kg)
            w1 (float): Ana sistem doğal frekansı (rad/s)
            c1 (float): Ana sistemin sönümü
        """
        self.m1 = m1
        self.m2 = m2
        self.w1 = w1
        self.c1 = c1
        
        # Hesaplanmış değerler için boş değişkenler
        self.mu = None
        self.k1 = None
        self.w2_opt = None
        self.k2_opt = None
        self.ksi_2_opt = None
        self.c2_opt = None
        
    def calculate_parameters(self):
        """
        TMD optimal parametrelerini hesaplar
        
        Returns:
            dict: Hesaplanan parametreleri içeren sözlük
        """
        # Kütle Oranı
        self.mu = self.m2 / self.m1
        
        # Baranın Rijitliği
        self.k1 = (self.w1**2) * self.m1
        
        # Optimum TMD Doğal Frekansı
        self.w2_opt = self.w1 / (1 + self.mu)
        
        # TMD Optimum Rijitliği
        self.k2_opt = (self.w2_opt ** 2) * self.m2
        
        # TMD Optimum Sönüm Oranı
        self.ksi_2_opt = np.sqrt((3 * self.mu) / (8 * (1 + self.mu)))
        
        # Optimum TMD Sönüm Katsayısı (Viskoz Yağ)
        self.c2_opt = self.ksi_2_opt * 2 * self.m2 * self.w2_opt
        
        return {
            'mu': self.mu,
            'k1': self.k1,
            'w2_opt': self.w2_opt,
            'k2_opt': self.k2_opt,
            'ksi_2_opt': self.ksi_2_opt,
            'c2_opt': self.c2_opt
        }