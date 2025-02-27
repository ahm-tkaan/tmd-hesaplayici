# core/analyzers.py
import numpy as np

class TMDAnalyzer:
    """TMD sistemlerinin farklı analizlerini gerçekleştiren sınıf"""
    
    def __init__(self):
        """Analiz sınıfını oluşturur"""
        pass
    
    def calculate_transmissibility(self, r, beta, mu, nua, nub):
        """
        Belirli parametreler için geçirgenlik hesaplar
        
        Args:
            r (float): Frekans oranı
            beta (float): TMD frekans oranı
            mu (float): Kütle oranı
            nua (float): TMD sönüm oranı
            nub (float): Ana sistem sönüm oranı
            
        Returns:
            float: Hesaplanan geçirgenlik değeri
        """
        pay = (beta**2 - r**2)**2 + 4 * (r**2) * (nua**2)
        
        payda1 = ((1 - (r**2)) * ((beta**2) - (r**2)) - (mu * (beta**2) * (r**2)) - (4 * nua * nub * (r**2)))**2
        payda2 = (nua * (1 - (r**2) - mu * (r**2)) + (nub * ((beta**2) - (r**2))))**2
        payda3 = payda2 * 4 * (r**2)
        payda = payda1 + payda3
        
        return np.sqrt(pay / payda)

    def frequency_ratio_analysis(self, mu, nub):
        """
        Frekans oranı değişimi analizi
        
        Args:
            mu (float): Kütle oranı
            nub (float): Ana sistem sönümü
            
        Returns:
            dict: Analiz sonuçlarını içeren sözlük
        """
        beta_values = np.arange(0.5, 1.1, 0.1)
        r_values = np.arange(0.1, 2.005, 0.005)
        results = np.zeros((len(r_values), len(beta_values)))
        
        for j, beta in enumerate(beta_values):
            if (beta > 0.79) and (beta < 0.89):
                beta = 0.87  # frekans oranı doğrudan girilebilir AMA OPTİMUM OLMAZ
            
            sigma2_optimum = np.sqrt((3 * mu) / (8 * (1 + mu)))  # OPTIMAL sönüm oranı
            nua = 0.058  # Absorber damping
            
            for i, r in enumerate(r_values):
                results[i, j] = self.calculate_transmissibility(r, beta, mu, nua, nub)
        
        return {
            'r_values': r_values,
            'beta_values': beta_values,
            'results': results,
            'mu': mu,
            'optimal_beta': 1/(1+mu),
            'optimal_ksi': np.sqrt((3*mu)/(8*(1+mu)))
        }
    
    def damping_ratio_analysis(self, mu, nub):
        """
        Sönüm oranı değişimi analizi
        
        Args:
            mu (float): Kütle oranı
            nub (float): Ana sistem sönümü
            
        Returns:
            dict: Analiz sonuçlarını içeren sözlük
        """
        beta = 1 / (1 + mu)  # OPTIMAL frekans oranı
        sigma2_optimum = np.sqrt((3 * mu) / (8 * (1 + mu)))  # OPTIMAL sönüm oranı
        
        sonumler = [0.1, sigma2_optimum, 0.3, 0.6, 0.99]  # FARKLI Absorber damping
        r_values = np.arange(0.1, 2.005, 0.005)
        results = np.zeros((len(r_values), len(sonumler)))
        
        for j, nua in enumerate(sonumler):
            for i, r in enumerate(r_values):
                results[i, j] = self.calculate_transmissibility(r, beta, mu, nua, nub)
        
        return {
            'r_values': r_values,
            'damping_values': sonumler,
            'results': results,
            'mu': mu,
            'beta': beta,
            'optimal_ksi': sigma2_optimum
        }
    
    def mass_ratio_analysis(self, current_mu, nub):
        """
        Kütle oranı değişimi analizi
        
        Args:
            current_mu (float): Mevcut kütle oranı
            nub (float): Ana sistem sönümü
            
        Returns:
            dict: Analiz sonuçlarını içeren sözlük
        """
        zz_values = np.arange(0.05, 0.6, 0.05)  # Kütle oranları
        r_values = np.arange(0.1, 2.005, 0.005)
        results = np.zeros((len(r_values), len(zz_values)))
        
        for j, mu in enumerate(zz_values):
            beta = 1 / (1 + mu)  # OPTIMAL frekans oranı
            sigma2_optimum = np.sqrt((3 * mu) / (8 * (1 + mu)))  # OPTIMAL sönüm oranı
            nua = sigma2_optimum  # Absorber damping
            
            for i, r in enumerate(r_values):
                results[i, j] = self.calculate_transmissibility(r, beta, mu, nua, nub)
        
        return {
            'r_values': r_values,
            'mass_values': zz_values,
            'results': results,
            'current_mu': current_mu,
            'optimal_beta': 1/(1+current_mu),
            'optimal_ksi': np.sqrt((3*current_mu)/(8*(1+current_mu)))
        }