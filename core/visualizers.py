# core/visualizers.py
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qtagg import NavigationToolbar2QT as NavigationToolbar
from mpl_toolkits.mplot3d import Axes3D
from typing import Dict, Any, List, Tuple, Optional

class MplCanvas(FigureCanvas):
    """2D visualization canvas"""
    def __init__(self, parent=None, width=12, height=9, dpi=100):
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = self.fig.add_subplot(111)
        self.fig.subplots_adjust(left=0.09, right=0.98, top=0.97, bottom=0.09)
        super().__init__(self.fig)
        self.setMinimumSize(800, 600)

class MplCanvas3D(FigureCanvas):
    """3D visualization canvas"""
    def __init__(self, parent=None, width=12, height=9, dpi=100):
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = self.fig.add_subplot(111, projection='3d')
        self.fig.subplots_adjust(left=0.09, right=0.98, top=0.97, bottom=0.09)
        super().__init__(self.fig)
        self.setMinimumSize(800, 600)

class TMDVisualizer:
    """Enhanced TMD visualization class"""
    
    def __init__(self):
        """Initialize the visualizer"""
        # Color palette for consistent colors across plots
        self.colors = plt.cm.tab10.colors
        self.colormap = 'viridis'
    
    def plot_frequency_ratio(self, canvas: MplCanvas, analysis_results: Dict[str, Any]) -> None:
        """
        Plot frequency ratio analysis with enhanced visualization
        
        Args:
            canvas: Canvas to draw on
            analysis_results: Analysis results dictionary
        """
        canvas.axes.clear()
        
        r_values = analysis_results['r_values']
        beta_values = analysis_results['beta_values']
        results = analysis_results['results']
        mu = analysis_results['mu']
        optimal_beta = analysis_results['optimal_beta']
        optimal_ksi = analysis_results['optimal_ksi']
        
        # Find the index of the optimal beta value
        optimal_idx = -1
        for j, beta in enumerate(beta_values):
            if abs(beta - optimal_beta) < 1e-2:
                optimal_idx = j
                break
        
        # Plot lines with different colors and styles
        for j, beta in enumerate(beta_values):
            if j == optimal_idx:
                # Highlight optimal curve
                canvas.axes.plot(r_values, results[:, j], label=f'{beta:.3f} (optimal)', 
                              linewidth=3, color='red', linestyle='-')
            else:
                canvas.axes.plot(r_values, results[:, j], label=f'{beta:.3f}', 
                              linewidth=2, color=self.colors[j % len(self.colors)])
        
        # Enhance plot appearance
        canvas.axes.set_ylabel('Absolute Transmissibility |X/F|', fontsize=12, fontweight='bold')
        canvas.axes.set_xlabel('Frequency Ratio (r)', fontsize=12, fontweight='bold')
        canvas.axes.set_xlim([0, max(r_values)])
        canvas.axes.set_ylim([0, min(8, np.max(results) * 1.1)])
        
        # Add legend with custom title
        legend = canvas.axes.legend(title='Frequency Ratio (β)', fontsize=10, title_fontsize=11, 
                                 loc='upper right', framealpha=0.9, fancybox=True, shadow=True)
        
        # Set title with more information
        title = f'Frequency Ratio Analysis for TMD (μ={mu:.2f})'
        canvas.axes.set_title(title, fontsize=14, fontweight='bold')
        
        # Add grid for better readability
        canvas.axes.grid(True, linestyle='--', alpha=0.7)
        
        # Add horizontal and vertical lines for reference
        canvas.axes.axvline(x=1.0, color='k', linestyle=':', alpha=0.5)  # Resonance line
        
        # Add detailed information text box
        info_text = f"Mass Ratio (μ) = {mu:.4f}\n"
        info_text += f"Optimal Frequency Ratio (β) = {optimal_beta:.4f}\n"
        info_text += f"Optimal Damping Ratio (ξ) = {optimal_ksi:.4f}"
        
        canvas.axes.text(0.02, 0.02, info_text, transform=canvas.axes.transAxes,
                      fontsize=10, verticalalignment='bottom', horizontalalignment='left',
                      bbox=dict(boxstyle='round,pad=0.5', facecolor='white', alpha=0.8))
        
        canvas.draw()
    
    def plot_damping_ratio(self, canvas: MplCanvas, canvas3d: MplCanvas3D, analysis_results: Dict[str, Any]) -> None:
        """
        Plot damping ratio analysis with enhanced 2D and 3D visualizations
        
        Args:
            canvas: 2D canvas to draw on
            canvas3d: 3D canvas to draw on
            analysis_results: Analysis results dictionary
        """
        canvas.axes.clear()
        canvas3d.axes.clear()
        
        r_values = analysis_results['r_values']
        damping_values = analysis_results['damping_values']
        results = analysis_results['results']
        mu = analysis_results['mu']
        beta = analysis_results['beta']
        optimal_ksi = analysis_results['optimal_ksi']
        
        # Find the index of the optimal damping value
        optimal_idx = -1
        for j, damp in enumerate(damping_values):
            if abs(damp - optimal_ksi) < 1e-2:
                optimal_idx = j
                break
        
        # 2D Plot
        for j, damp in enumerate(damping_values):
            if j == optimal_idx:
                # Highlight optimal curve
                canvas.axes.plot(r_values, results[:, j], label=f'{damp:.4f} (optimal)', 
                              linewidth=3, color='red', linestyle='-')
            else:
                canvas.axes.plot(r_values, results[:, j], label=f'{damp:.4f}', 
                              linewidth=2, color=self.colors[j % len(self.colors)])
        
        # Enhance 2D plot appearance
        canvas.axes.set_ylabel('Absolute Transmissibility |X/F|', fontsize=12, fontweight='bold')
        canvas.axes.set_xlabel('Frequency Ratio (r)', fontsize=12, fontweight='bold')
        canvas.axes.set_xlim([0, max(r_values)])
        canvas.axes.set_ylim([0, min(6, np.max(results) * 1.1)])
        
        # Add legend with custom title
        legend = canvas.axes.legend(title='Damping Ratio (ξ)', fontsize=10, title_fontsize=11, 
                                 loc='upper right', framealpha=0.9, fancybox=True, shadow=True)
        
        # Set title with more information
        title = f'Damping Ratio Analysis for TMD (μ={mu:.2f}, β={beta:.4f})'
        canvas.axes.set_title(title, fontsize=14, fontweight='bold')
        
        # Add grid for better readability
        canvas.axes.grid(True, linestyle='--', alpha=0.7)
        
        # Add reference lines
        canvas.axes.axvline(x=1.0, color='k', linestyle=':', alpha=0.5)  # Resonance line
        
        # Add information text box
        info_text = f"Mass Ratio (μ) = {mu:.4f}\n"
        info_text += f"Frequency Ratio (β) = {beta:.4f}\n"
        info_text += f"Optimal Damping Ratio (ξ) = {optimal_ksi:.4f}"
        
        canvas.axes.text(0.02, 0.02, info_text, transform=canvas.axes.transAxes,
                      fontsize=10, verticalalignment='bottom', horizontalalignment='left',
                      bbox=dict(boxstyle='round,pad=0.5', facecolor='white', alpha=0.8))
        
        canvas.draw()
        
        # 3D Plot
        X, Y = np.meshgrid(damping_values, r_values)
        Z = results
        
        # Create the 3D surface plot with improved appearance
        surf = canvas3d.axes.plot_surface(X, Y, Z, cmap=self.colormap, alpha=0.9, 
                                       edgecolor='k', linewidth=0.1, antialiased=True)
        
        # Enhance 3D plot appearance
        canvas3d.axes.set_xlabel('Damping Ratio (ξ)', fontsize=12, fontweight='bold')
        canvas3d.axes.set_ylabel('Frequency Ratio (r)', fontsize=12, fontweight='bold')
        canvas3d.axes.set_zlabel('Transmissibility |X/F|', fontsize=12, fontweight='bold')
        
        # Set title
        canvas3d.axes.set_title('Transmissibility vs Damping and Frequency', fontsize=14, fontweight='bold')
        
        # Add color bar
        cbar = canvas3d.fig.colorbar(surf, ax=canvas3d.axes, shrink=0.7, aspect=10)
        cbar.set_label('Transmissibility', fontsize=10, fontweight='bold')
        
        # Mark optimal damping value
        if optimal_idx >= 0:
            x_opt = damping_values[optimal_idx]
            canvas3d.axes.plot([x_opt, x_opt], [0, 2], [0, 0], 'r-', linewidth=2)
            
            # Add annotation
            canvas3d.axes.text(x_opt, 1.0, 0, f"Optimal ξ={optimal_ksi:.4f}", 
                           color='black', fontweight='bold', fontsize=10,
                           bbox=dict(boxstyle='round,pad=0.3', facecolor='yellow', alpha=0.8))
        
        canvas3d.draw()
    
    def plot_mass_ratio(self, canvas: MplCanvas, canvas3d: MplCanvas3D, analysis_results: Dict[str, Any]) -> None:
        """
        Plot mass ratio analysis with enhanced 2D and 3D visualizations
        
        Args:
            canvas: 2D canvas to draw on
            canvas3d: 3D canvas to draw on
            analysis_results: Analysis results dictionary
        """
        canvas.axes.clear()
        canvas3d.axes.clear()
        
        r_values = analysis_results['r_values']
        mass_values = analysis_results['mass_values']
        results = analysis_results['results']
        current_mu = analysis_results['current_mu']
        optimal_beta = analysis_results['optimal_beta']
        optimal_ksi = analysis_results['optimal_ksi']
        
        # Find the index closest to current mass ratio
        current_idx = np.argmin(np.abs(np.array(mass_values) - current_mu))
        
        # 2D Plot
        for j, mu in enumerate(mass_values):
            if j == current_idx:
                # Highlight current system
                canvas.axes.plot(r_values, results[:, j], label=f'{mu:.2f} (current)', 
                              linewidth=3, color='red', linestyle='-')
            else:
                canvas.axes.plot(r_values, results[:, j], label=f'{mu:.2f}', 
                              linewidth=2, color=self.colors[j % len(self.colors)])
        
        # Enhance 2D plot appearance
        canvas.axes.set_ylabel('Absolute Transmissibility |X/F|', fontsize=12, fontweight='bold')
        canvas.axes.set_xlabel('Frequency Ratio (r)', fontsize=12, fontweight='bold')
        canvas.axes.set_xlim([0, max(r_values)])
        canvas.axes.set_ylim([0, min(6, np.max(results) * 1.1)])
        
        # Add legend with custom title
        legend = canvas.axes.legend(title='Mass Ratio (μ)', fontsize=10, title_fontsize=11, 
                                 loc='upper right', framealpha=0.9, fancybox=True, shadow=True)
        
        # Set title
        title = 'Mass Ratio Analysis for TMD'
        canvas.axes.set_title(title, fontsize=14, fontweight='bold')
        
        # Add grid
        canvas.axes.grid(True, linestyle='--', alpha=0.7)
        
        # Add reference lines
        canvas.axes.axvline(x=1.0, color='k', linestyle=':', alpha=0.5)  # Resonance line
        
        # Add information text box
        info_text = f"Current Mass Ratio (μ) = {current_mu:.4f}\n"
        info_text += f"Optimal Frequency Ratio (β) = {optimal_beta:.4f}\n"
        info_text += f"Optimal Damping Ratio (ξ) = {optimal_ksi:.4f}"
        
        canvas.axes.text(0.02, 0.02, info_text, transform=canvas.axes.transAxes,
                      fontsize=10, verticalalignment='bottom', horizontalalignment='left',
                      bbox=dict(boxstyle='round,pad=0.5', facecolor='white', alpha=0.8))
        
        canvas.draw()
        
        # 3D Plot
        X, Y = np.meshgrid(mass_values, r_values)
        Z = results
        
        # Create the 3D surface plot
        surf = canvas3d.axes.plot_surface(X, Y, Z, cmap=self.colormap, alpha=0.9, 
                                       edgecolor='k', linewidth=0.1, antialiased=True)
        
        # Enhance 3D plot appearance
        canvas3d.axes.set_xlabel('Mass Ratio (μ)', fontsize=12, fontweight='bold')
        canvas3d.axes.set_ylabel('Frequency Ratio (r)', fontsize=12, fontweight='bold')
        canvas3d.axes.set_zlabel('Transmissibility |X/F|', fontsize=12, fontweight='bold')
        
        # Set title
        canvas3d.axes.set_title('Transmissibility vs Mass Ratio and Frequency', fontsize=14, fontweight='bold')
        
        # Add color bar
        cbar = canvas3d.fig.colorbar(surf, ax=canvas3d.axes, shrink=0.7, aspect=10)
        cbar.set_label('Transmissibility', fontsize=10, fontweight='bold')
        
        # Mark current mass ratio
        if current_idx < len(mass_values):
            x_current = mass_values[current_idx]
            canvas3d.axes.plot([x_current, x_current], [0, 2], [0, 0], 'r-', linewidth=2)
            
            # Add annotation
            canvas3d.axes.text(x_current, 1.0, 0, f"Current μ={current_mu:.4f}", 
                           color='black', fontweight='bold', fontsize=10,
                           bbox=dict(boxstyle='round,pad=0.3', facecolor='yellow', alpha=0.8))
        
        canvas3d.draw()
    
    def plot_with_without_tmd(self, canvas: MplCanvas, comparison_results: Dict[str, Any]) -> None:
        """
        Plot comparison of system with and without TMD
        
        Args:
            canvas: Canvas to draw on
            comparison_results: Comparison results dictionary
        """
        canvas.axes.clear()
        
        r_values = comparison_results['r_values']
        with_tmd = comparison_results['with_tmd']
        without_tmd = comparison_results['without_tmd']
        mu = comparison_results['mu']
        beta = comparison_results['beta']
        ksi = comparison_results['ksi']
        nub = comparison_results['nub']
        
        # Clip infinite values for plotting
        without_tmd_clipped = np.clip(without_tmd, 0, 20)
        
        # Plot the curves
        canvas.axes.plot(r_values, without_tmd_clipped, label='Without TMD', 
                      linewidth=3, color='blue', linestyle='-')
        canvas.axes.plot(r_values, with_tmd, label='With TMD', 
                      linewidth=3, color='red', linestyle='-')
        
        # Enhance plot appearance
        canvas.axes.set_ylabel('Absolute Transmissibility |X/F|', fontsize=12, fontweight='bold')
        canvas.axes.set_xlabel('Frequency Ratio (r)', fontsize=12, fontweight='bold')
        canvas.axes.set_xlim([0, max(r_values)])
        
        # Set a reasonable y-limit
        max_y = min(10, np.max(with_tmd) * 1.5)
        canvas.axes.set_ylim([0, max_y])
        
        # Add legend
        legend = canvas.axes.legend(fontsize=10, loc='upper right', 
                                 framealpha=0.9, fancybox=True, shadow=True)
        
        # Set title
        title = f'Comparison With and Without TMD (μ={mu:.2f})'
        canvas.axes.set_title(title, fontsize=14, fontweight='bold')
        
        # Add grid
        canvas.axes.grid(True, linestyle='--', alpha=0.7)
        
        # Add reference lines
        canvas.axes.axvline(x=1.0, color='k', linestyle=':', alpha=0.5)  # Resonance line
        
        # Calculate reduction percentage at resonance
        resonance_idx = np.argmin(np.abs(r_values - 1.0))
        reduction_pct = 0
        
        if without_tmd[resonance_idx] > 0 and not np.isinf(without_tmd[resonance_idx]):
            reduction_pct = ((without_tmd[resonance_idx] - with_tmd[resonance_idx]) / 
                           without_tmd[resonance_idx]) * 100
        
        # Add information text box
        info_text = f"Mass Ratio (μ) = {mu:.4f}\n"
        info_text += f"Frequency Ratio (β) = {beta:.4f}\n"
        info_text += f"TMD Damping Ratio (ξ) = {ksi:.4f}\n"
        info_text += f"Main System Damping Ratio = {nub:.4f}\n"
        info_text += f"Reduction at Resonance ≈ {reduction_pct:.1f}%"
        
        canvas.axes.text(0.02, 0.02, info_text, transform=canvas.axes.transAxes,
                      fontsize=10, verticalalignment='bottom', horizontalalignment='left',
                      bbox=dict(boxstyle='round,pad=0.5', facecolor='white', alpha=0.8))
        
        # Add regions where TMD improves performance
        for i in range(1, len(r_values)):
            if with_tmd[i] < without_tmd_clipped[i]:
                canvas.axes.axvspan(r_values[i-1], r_values[i], alpha=0.1, color='green')
        
        canvas.draw()
    
    def plot_tmd_effectiveness(self, canvas: MplCanvas, effectiveness_results: Dict[str, Any]) -> None:
        """
        Plot TMD effectiveness analysis
        
        Args:
            canvas: Canvas to draw on
            effectiveness_results: Effectiveness analysis results
        """
        canvas.axes.clear()
        
        mu_values = effectiveness_results['mu_values']
        max_transmissibility = effectiveness_results['max_transmissibility']
        effectiveness = effectiveness_results['effectiveness']
        
        # Create twin axis
        ax1 = canvas.axes
        ax2 = ax1.twinx()
        
        # Plot the curves
        line1 = ax1.plot(mu_values, max_transmissibility, 'b-', linewidth=2, 
                       label='Max Transmissibility')
        line2 = ax2.plot(mu_values, effectiveness * 100, 'r-', linewidth=2, 
                       label='Effectiveness (%)')
        
        # Set labels
        ax1.set_xlabel('Mass Ratio (μ)', fontsize=12, fontweight='bold')
        ax1.set_ylabel('Maximum Transmissibility', fontsize=12, fontweight='bold', color='blue')
        ax2.set_ylabel('Effectiveness (%)', fontsize=12, fontweight='bold', color='red')
        
        # Set title
        title = 'TMD Effectiveness vs Mass Ratio'
        ax1.set_title(title, fontsize=14, fontweight='bold')
        
        # Set reasonable limits
        ax1.set_xlim([min(mu_values), max(mu_values)])
        ax1.set_ylim([0, np.max(max_transmissibility) * 1.1])
        ax2.set_ylim([0, 100])
        
        # Add grid
        ax1.grid(True, linestyle='--', alpha=0.7)
        
        # Add combined legend
        lines = line1 + line2
        labels = [l.get_label() for l in lines]
        ax1.legend(lines, labels, loc='upper right', framealpha=0.9, fancybox=True, shadow=True)
        
        # Add reference guidelines for practical design
        optimal_mu_idx = np.argmax(effectiveness)
        optimal_mu = mu_values[optimal_mu_idx]
        
        ax1.axvline(x=optimal_mu, color='g', linestyle='--', alpha=0.7)
        ax1.text(optimal_mu, 0.5 * np.max(max_transmissibility), 
              f'Optimal μ ≈ {optimal_mu:.3f}',
              rotation=90, verticalalignment='center', 
              bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.8))
        
        # Add practical design regions
        ax1.axvspan(0.01, 0.05, alpha=0.1, color='red', label='Too Small')
        ax1.axvspan(0.05, 0.2, alpha=0.1, color='green', label='Practical Range')
        ax1.axvspan(0.2, 0.5, alpha=0.1, color='yellow', label='Large')
        
        canvas.draw()
    
    def plot_optimization_progress(self, canvas: MplCanvas, optimization_stats: Dict[str, Any]) -> None:
        """
        Plot optimization algorithm progress
        
        Args:
            canvas: Canvas to draw on
            optimization_stats: Optimization statistics dictionary
        """
        canvas.axes.clear()
        
        best_fitness_history = optimization_stats['best_fitness_history']
        mean_fitness_history = optimization_stats['mean_fitness_history']
        
        iterations = np.arange(len(best_fitness_history))
        
        # Plot the curves
        canvas.axes.plot(iterations, best_fitness_history, 'r-', linewidth=2, 
                      label='Best Fitness')
        canvas.axes.plot(iterations, mean_fitness_history, 'b-', linewidth=2, 
                      label='Mean Fitness')
        
        # Set labels
        canvas.axes.set_xlabel('Iteration', fontsize=12, fontweight='bold')
        canvas.axes.set_ylabel('Fitness Value (Lower is Better)', fontsize=12, fontweight='bold')
        
        # Set title
        title = 'Optimization Progress'
        canvas.axes.set_title(title, fontsize=14, fontweight='bold')
        
        # Set reasonable limits
        canvas.axes.set_xlim([0, len(iterations) - 1])
        
        # Add grid
        canvas.axes.grid(True, linestyle='--', alpha=0.7)
        
        # Add legend
        canvas.axes.legend(loc='upper right', framealpha=0.9, fancybox=True, shadow=True)
        
        # Add information about convergence
        improvement = (best_fitness_history[0] - best_fitness_history[-1]) / best_fitness_history[0] * 100
        
        info_text = f"Initial Best Fitness: {best_fitness_history[0]:.4f}\n"
        info_text += f"Final Best Fitness: {best_fitness_history[-1]:.4f}\n"
        info_text += f"Improvement: {improvement:.2f}%"
        
        canvas.axes.text(0.02, 0.98, info_text, transform=canvas.axes.transAxes,
                      fontsize=10, verticalalignment='top', horizontalalignment='left',
                      bbox=dict(boxstyle='round,pad=0.5', facecolor='white', alpha=0.8))
        
        canvas.draw()
    
    def plot_cutting_tool_modes(self, canvas: MplCanvas, tool_model) -> None:
        """
        Plot cutting tool vibration modes
        
        Args:
            canvas: Canvas to draw on
            tool_model: Cutting tool model object
        """
        canvas.axes.clear()
        
        # Calculate natural frequencies for 5 modes
        frequencies = tool_model.calculate_natural_frequencies(modes=5)
        modes = np.arange(1, len(frequencies) + 1)
        
        # Plot the frequencies
        canvas.axes.bar(modes, frequencies, width=0.6, color=self.colors[:len(modes)])
        
        # Set labels
        canvas.axes.set_xlabel('Mode Number', fontsize=12, fontweight='bold')
        canvas.axes.set_ylabel('Natural Frequency (Hz)', fontsize=12, fontweight='bold')
        
        # Set title
        title = f'Natural Frequencies of Cutting Tool ({tool_model.material})'
        canvas.axes.set_title(title, fontsize=14, fontweight='bold')
        
        # Set x-ticks to be integer mode numbers
        canvas.axes.set_xticks(modes)
        
        # Add grid
        canvas.axes.grid(True, linestyle='--', alpha=0.7, axis='y')
        
        # Add value labels on top of bars
        for i, freq in enumerate(frequencies):
            canvas.axes.text(modes[i], freq + (np.max(frequencies) * 0.02), 
                          f'{freq:.1f} Hz', 
                          horizontalalignment='center',
                          fontweight='bold')
        
        # Add tool information
        info_text = f"Length: {tool_model.length*1000:.0f} mm\n"
        info_text += f"Diameter: {tool_model.diameter*1000:.1f} mm\n"
        info_text += f"Mass: {tool_model.mass:.2f} kg"
        
        canvas.axes.text(0.02, 0.98, info_text, transform=canvas.axes.transAxes,
                      fontsize=10, verticalalignment='top', horizontalalignment='left',
                      bbox=dict(boxstyle='round,pad=0.5', facecolor='white', alpha=0.8))
        
        canvas.draw()
    
    def plot_classical_vs_optimized(self, canvas: MplCanvas, comparison_results: Dict[str, Any]) -> None:
        """
        Plot comparison between classical and optimized TMD solutions
        
        Args:
            canvas: Canvas to draw on
            comparison_results: Comparison results dictionary
        """
        canvas.axes.clear()
        
        r_values = comparison_results['r_values']
        classical_trans = comparison_results['classical_trans']
        optimized_trans = comparison_results['optimized_trans']
        
        # Plot the curves
        canvas.axes.plot(r_values, classical_trans, 'b-', linewidth=2, 
                      label='Classical (Den Hartog)')
        canvas.axes.plot(r_values, optimized_trans, 'r-', linewidth=2, 
                      label='Optimized (Bees Algorithm)')
        
        # Set labels
        canvas.axes.set_xlabel('Frequency Ratio (r)', fontsize=12, fontweight='bold')
        canvas.axes.set_ylabel('Transmissibility |X/F|', fontsize=12, fontweight='bold')
        
        # Set title
        improvement = comparison_results['improvement_percentage']
        title = f'Classical vs Optimized TMD (Improvement: {improvement:.1f}%)'
        canvas.axes.set_title(title, fontsize=14, fontweight='bold')
        
        # Set reasonable limits
        canvas.axes.set_xlim([min(r_values), max(r_values)])
        max_y = max(np.max(classical_trans), np.max(optimized_trans)) * 1.1
        canvas.axes.set_ylim([0, min(max_y, 10)])
        
        # Add grid
        canvas.axes.grid(True, linestyle='--', alpha=0.7)
        
        # Add legend
        canvas.axes.legend(loc='upper right', framealpha=0.9, fancybox=True, shadow=True)
        
        # Add parameter comparison
        classical = comparison_results['classical_params']
        optimized = comparison_results['optimized_params']
        
        info_text = "Classical Parameters:\n"
        info_text += f"β = {classical['beta']:.4f}, ξ = {classical['ksi_2_opt']:.4f}\n\n"
        info_text += "Optimized Parameters:\n"
        info_text += f"β = {optimized['beta']:.4f}, ξ = {optimized['ksi_2_opt']:.4f}"
        
        canvas.axes.text(0.02, 0.98, info_text, transform=canvas.axes.transAxes,
                      fontsize=10, verticalalignment='top', horizontalalignment='left',
                      bbox=dict(boxstyle='round,pad=0.5', facecolor='white', alpha=0.8))
        
        canvas.draw()