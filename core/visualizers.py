# core/visualizers.py
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qtagg import NavigationToolbar2QT as NavigationToolbar
from mpl_toolkits.mplot3d import Axes3D

class MplCanvas(FigureCanvas):
    """2D grafik canvas sınıfı"""
    def __init__(self, parent=None, width=12, height=9, dpi=100):
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = self.fig.add_subplot(111)
        self.fig.subplots_adjust(left=0.09, right=0.98, top=0.97, bottom=0.09)
        super().__init__(self.fig)
        self.setMinimumSize(800, 600)

class MplCanvas3D(FigureCanvas):
    """3D grafik canvas sınıfı"""
    def __init__(self, parent=None, width=12, height=9, dpi=100):
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = self.fig.add_subplot(111, projection='3d')
        self.fig.subplots_adjust(left=0.09, right=0.98, top=0.97, bottom=0.09)
        super().__init__(self.fig)
        self.setMinimumSize(800, 600)

class TMDVisualizer:
    """TMD analiz sonuçlarını görselleştiren sınıf"""
    
    def __init__(self):
        """Görselleştirme sınıfını oluşturur"""
        pass
    
    def plot_frequency_ratio(self, canvas, analysis_results):
        """
        Frekans oranı analiz sonuçlarını 2D grafikte görselleştirir
        
        Args:
            canvas (MplCanvas): Çizim yapılacak canvas
            analysis_results (dict): Analiz sonuçlarını içeren sözlük
        """
        canvas.axes.clear()
        
        r_values = analysis_results['r_values']
        beta_values = analysis_results['beta_values']
        results = analysis_results['results']
        mu = analysis_results['mu']
        optimal_beta = analysis_results['optimal_beta']
        optimal_ksi = analysis_results['optimal_ksi']
        
        for j, beta in enumerate(beta_values):
            canvas.axes.plot(r_values, results[:, j], label=f'{beta:.3f}', linewidth=2)
        
        # Eksen etiketleri ve stil ayarları
        canvas.axes.set_ylabel('Absolute transmissibility of the main system, |Xk/F|', fontsize=12, fontweight='bold')
        canvas.axes.set_xlabel('Frequency ratio, r', fontsize=12, fontweight='bold')
        canvas.axes.set_xlim([0, max(r_values)])
        canvas.axes.set_ylim([0, 8])
        canvas.axes.legend(title='Frequency ratio', fontsize=10, title_fontsize=11)
        canvas.axes.set_title(f'Frequency ratio analysis (μ={mu:.2f})', fontsize=14, fontweight='bold')
        canvas.axes.tick_params(axis='both', which='major', labelsize=10)
        canvas.axes.grid(True, linestyle='--', alpha=0.7)
        
        # Koordinat paneli ekle
        coord_text = f"μ={mu:.4f}, β-opt={optimal_beta:.4f}, ξ-opt={optimal_ksi:.4f}"
        canvas.axes.text(0.5, 0.02, coord_text, transform=canvas.axes.transAxes,
                      fontsize=11, fontweight='bold', ha='center', va='bottom',
                      bbox=dict(boxstyle='round,pad=0.5', facecolor='lightyellow', alpha=0.9, edgecolor='orange'))
        
        canvas.draw()
    
    def plot_damping_ratio(self, canvas, canvas3d, analysis_results):
        """
        Sönüm oranı analiz sonuçlarını 2D ve 3D grafiklerde görselleştirir
        
        Args:
            canvas (MplCanvas): 2D çizim için canvas
            canvas3d (MplCanvas3D): 3D çizim için canvas
            analysis_results (dict): Analiz sonuçlarını içeren sözlük
        """
        canvas.axes.clear()
        canvas3d.axes.clear()
        
        r_values = analysis_results['r_values']
        damping_values = analysis_results['damping_values']
        results = analysis_results['results']
        mu = analysis_results['mu']
        beta = analysis_results['beta']
        optimal_ksi = analysis_results['optimal_ksi']
        
        # 2D grafik
        for j, damp in enumerate(damping_values):
            canvas.axes.plot(r_values, results[:, j], label=f'{damp:.4f}', linewidth=2)
        
        # Eksen etiketleri ve stil ayarları
        canvas.axes.set_ylabel('Absolute transmissibility of the main system, |Xk/F|', fontsize=12, fontweight='bold')
        canvas.axes.set_xlabel('Frequency ratio, r', fontsize=12, fontweight='bold')
        canvas.axes.set_xlim([0, max(r_values)])
        canvas.axes.set_ylim([0, 6])
        canvas.axes.legend(title='Damping ratio', fontsize=10, title_fontsize=11)
        canvas.axes.set_title(f'Damping ratio analysis (μ={mu:.2f}, β={beta:.4f})', fontsize=14, fontweight='bold')
        canvas.axes.tick_params(axis='both', which='major', labelsize=10)
        canvas.axes.grid(True, linestyle='--', alpha=0.7)
        
        # Koordinat paneli ekle
        optimal_text = f"μ={mu:.4f}, β-opt={beta:.4f}, ξ-opt={optimal_ksi:.4f}"
        canvas.axes.text(0.5, 0.02, optimal_text, transform=canvas.axes.transAxes,
                      fontsize=11, fontweight='bold', ha='center', va='bottom',
                      bbox=dict(boxstyle='round,pad=0.5', facecolor='lightyellow', alpha=0.9, edgecolor='orange'))
        
        canvas.draw()
        
        # 3D grafik
        X, Y = np.meshgrid(damping_values, r_values)
        Z = results
        surf = canvas3d.axes.plot_surface(X, Y, Z, cmap='rainbow', alpha=0.9)
        
        # 3D eksen etiketleri ve stil ayarları
        canvas3d.axes.set_xlabel('Damping ratio', fontsize=12, fontweight='bold')
        canvas3d.axes.set_ylabel('Frequency ratio, r', fontsize=12, fontweight='bold')
        canvas3d.axes.set_zlabel('Absolute transmissibility, |Xk/F|', fontsize=12, fontweight='bold')
        canvas3d.axes.set_title('Transmissibility vs Damping and Frequency', fontsize=14, fontweight='bold')
        canvas3d.axes.tick_params(axis='both', which='major', labelsize=10)
        
        # Renk çubuğu ekle
        cbar = canvas3d.fig.colorbar(surf, ax=canvas3d.axes, shrink=0.7, aspect=10)
        cbar.set_label('Transmissibility', fontsize=10, fontweight='bold')
        
        # Optimum değeri işaretle
        opt_idx = np.argmin(np.abs(np.array(damping_values) - optimal_ksi))
        canvas3d.axes.text(damping_values[opt_idx], 1.0, 0, f"Optimal ξ={optimal_ksi:.4f}", 
                         color='black', fontweight='bold', fontsize=10,
                         bbox=dict(boxstyle='round,pad=0.3', facecolor='yellow', alpha=0.8))
        
        canvas3d.draw()
    
    def plot_mass_ratio(self, canvas, canvas3d, analysis_results):
        """
        Kütle oranı analiz sonuçlarını 2D ve 3D grafiklerde görselleştirir
        
        Args:
            canvas (MplCanvas): 2D çizim için canvas
            canvas3d (MplCanvas3D): 3D çizim için canvas
            analysis_results (dict): Analiz sonuçlarını içeren sözlük
        """
        canvas.axes.clear()
        canvas3d.axes.clear()
        
        r_values = analysis_results['r_values']
        mass_values = analysis_results['mass_values']
        results = analysis_results['results']
        current_mu = analysis_results['current_mu']
        optimal_beta = analysis_results['optimal_beta']
        optimal_ksi = analysis_results['optimal_ksi']
        
        # 2D grafik
        for j, mu in enumerate(mass_values):
            canvas.axes.plot(r_values, results[:, j], label=f'{mu:.2f}', linewidth=2)
        
        # Eksen etiketleri ve stil ayarları
        canvas.axes.set_ylabel('Absolute transmissibility of the main system, |Xk/F|', fontsize=12, fontweight='bold')
        canvas.axes.set_xlabel('Frequency ratio, r', fontsize=12, fontweight='bold')
        canvas.axes.set_xlim([0, max(r_values)])
        canvas.axes.set_ylim([0, 6])
        canvas.axes.legend(title='Mass ratio', fontsize=10, title_fontsize=11)
        canvas.axes.set_title('Mass ratio analysis', fontsize=14, fontweight='bold')
        canvas.axes.tick_params(axis='both', which='major', labelsize=10)
        canvas.axes.grid(True, linestyle='--', alpha=0.7)
        
        # Koordinat paneli ekle
        current_mu_text = f"Current system: μ={current_mu:.4f}, β-opt={optimal_beta:.4f}, ξ-opt={optimal_ksi:.4f}"
        
        canvas.axes.text(0.5, 0.02, current_mu_text, transform=canvas.axes.transAxes,
                      fontsize=11, fontweight='bold', ha='center', va='bottom',
                      bbox=dict(boxstyle='round,pad=0.5', facecolor='lightyellow', alpha=0.9, edgecolor='orange'))
        
        canvas.draw()
        
        # 3D grafik
        X, Y = np.meshgrid(mass_values, r_values)
        Z = results
        surf = canvas3d.axes.plot_surface(X, Y, Z, cmap='rainbow', alpha=0.9)
        
        # 3D eksen etiketleri ve stil ayarları
        canvas3d.axes.set_xlabel('Mass ratio', fontsize=12, fontweight='bold')
        canvas3d.axes.set_ylabel('Frequency ratio, r', fontsize=12, fontweight='bold')
        canvas3d.axes.set_zlabel('Absolute transmissibility, |Xk/F|', fontsize=12, fontweight='bold')
        canvas3d.axes.set_title('Transmissibility vs Mass and Frequency', fontsize=14, fontweight='bold')
        canvas3d.axes.tick_params(axis='both', which='major', labelsize=10)
        
        # Renk çubuğu ekle
        cbar = canvas3d.fig.colorbar(surf, ax=canvas3d.axes, shrink=0.7, aspect=10)
        cbar.set_label('Transmissibility', fontsize=10, fontweight='bold')
        
        # Mevcut kütle değerini işaretle
        current_idx = np.argmin(np.abs(mass_values - current_mu))
        if current_idx < len(mass_values):
            canvas3d.axes.text(mass_values[current_idx], 1.0, 0, f"Current μ={current_mu:.4f}", 
                             color='black', fontweight='bold', fontsize=10,
                             bbox=dict(boxstyle='round,pad=0.3', facecolor='yellow', alpha=0.8))
        
        canvas3d.draw()