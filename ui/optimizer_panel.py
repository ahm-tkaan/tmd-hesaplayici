# ui/optimizer_panel.py
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, QLineEdit, 
                            QGroupBox, QPushButton, QMessageBox, QComboBox, QSpinBox, QDoubleSpinBox,
                            QTabWidget, QProgressBar, QFormLayout, QCheckBox, QTextEdit, QSplitter)
from PyQt6.QtCore import pyqtSignal, Qt, QTimer
from PyQt6.QtGui import QFont, QIcon, QPixmap

from core.visualizers import MplCanvas, MplCanvas3D, NavigationToolbar, TMDVisualizer
from core.optimizers import TMDOptimizer
from core.analyzers import TMDAnalyzer
from core.tmd_calculator import TMDCalculator
from core.cutting_tool import CuttingToolModel

class OptimizerPanel(QWidget):
    """
    Panel for TMD optimization using the Bees Algorithm
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Initialize analyzer and visualizer
        self.analyzer = TMDAnalyzer()
        self.visualizer = TMDVisualizer()
        
        # Default system parameters
        self.m1 = 3.94       # (kg) Main system mass (default from paper)
        self.w1 = 125.54 * 2 * 3.14159  # (rad/s) Main system natural frequency (default from paper)
        self.c1 = 0.05       # Main system damping ratio
        
        # Create calculator
        self.calculator = TMDCalculator(self.m1, None, self.w1, self.c1)
        
        # Tool model (optional)
        self.tool_model = None
        
        # Optimization results
        self.optimization_results = None
        
        self.initUI()
    
    def initUI(self):
        """Initialize the user interface"""
        main_layout = QVBoxLayout(self)
        
        # Splitter to divide parameters and results
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Left panel - Parameters
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        
        # System parameters
        system_group = QGroupBox("System Parameters")
        system_form = QFormLayout()
        
        self.m1_input = QDoubleSpinBox()
        self.m1_input.setRange(0.1, 100.0)
        self.m1_input.setValue(self.m1)
        self.m1_input.setSingleStep(0.1)
        self.m1_input.setDecimals(3)
        system_form.addRow("Main Mass (kg):", self.m1_input)
        
        self.w1_input = QDoubleSpinBox()
        self.w1_input.setRange(1.0, 10000.0)
        self.w1_input.setValue(self.w1)
        self.w1_input.setSingleStep(10.0)
        self.w1_input.setDecimals(2)
        system_form.addRow("Natural Frequency (rad/s):", self.w1_input)
        
        self.c1_input = QDoubleSpinBox()
        self.c1_input.setRange(0.0, 1.0)
        self.c1_input.setValue(self.c1)
        self.c1_input.setSingleStep(0.01)
        self.c1_input.setDecimals(3)
        system_form.addRow("Main Damping Ratio:", self.c1_input)
        
        self.frequency_hz_label = QLabel(f"{self.w1/(2*3.14159):.2f} Hz")
        system_form.addRow("Frequency in Hz:", self.frequency_hz_label)
        
        # Connect signals to update Hz label
        self.w1_input.valueChanged.connect(self.update_frequency_hz)
        
        system_group.setLayout(system_form)
        left_layout.addWidget(system_group)
        
        # Optimization parameters
        opt_group = QGroupBox("Bees Algorithm Parameters")
        opt_form = QFormLayout()
        
        self.n_input = QSpinBox()
        self.n_input.setRange(10, 100)
        self.n_input.setValue(20)
        opt_form.addRow("Scout Bees (n):", self.n_input)
        
        self.m_input = QSpinBox()
        self.m_input.setRange(5, 50)
        self.m_input.setValue(10)
        opt_form.addRow("Selected Sites (m):", self.m_input)
        
        self.e_input = QSpinBox()
        self.e_input.setRange(1, 20)
        self.e_input.setValue(5)
        opt_form.addRow("Elite Sites (e):", self.e_input)
        
        self.nep_input = QSpinBox()
        self.nep_input.setRange(5, 50)
        self.nep_input.setValue(10)
        opt_form.addRow("Bees for Elite Sites (nep):", self.nep_input)
        
        self.nsp_input = QSpinBox()
        self.nsp_input.setRange(2, 30)
        self.nsp_input.setValue(7)
        opt_form.addRow("Bees for Other Sites (nsp):", self.nsp_input)
        
        self.ngh_input = QDoubleSpinBox()
        self.ngh_input.setRange(0.001, 0.5)
        self.ngh_input.setValue(0.05)
        self.ngh_input.setSingleStep(0.01)
        self.ngh_input.setDecimals(3)
        opt_form.addRow("Initial Patch Size (ngh):", self.ngh_input)
        
        self.iterations_input = QSpinBox()
        self.iterations_input.setRange(10, 500)
        self.iterations_input.setValue(100)
        opt_form.addRow("Max Iterations:", self.iterations_input)
        
        opt_group.setLayout(opt_form)
        left_layout.addWidget(opt_group)
        
        # Search bounds
        bounds_group = QGroupBox("Search Bounds")
        bounds_form = QFormLayout()
        
        # Mass ratio bounds
        bounds_form.addRow(QLabel("Mass Ratio (μ):"))
        
        bounds_layout = QHBoxLayout()
        self.mu_min_input = QDoubleSpinBox()
        self.mu_min_input.setRange(0.01, 0.5)
        self.mu_min_input.setValue(0.05)
        self.mu_min_input.setSingleStep(0.01)
        self.mu_min_input.setDecimals(2)
        
        self.mu_max_input = QDoubleSpinBox()
        self.mu_max_input.setRange(0.01, 0.5)
        self.mu_max_input.setValue(0.5)
        self.mu_max_input.setSingleStep(0.01)
        self.mu_max_input.setDecimals(2)
        
        bounds_layout.addWidget(QLabel("Min:"))
        bounds_layout.addWidget(self.mu_min_input)
        bounds_layout.addWidget(QLabel("Max:"))
        bounds_layout.addWidget(self.mu_max_input)
        bounds_form.addRow(bounds_layout)
        
        # Damping ratio bounds
        bounds_form.addRow(QLabel("Damping Ratio (ξ):"))
        
        damping_layout = QHBoxLayout()
        self.ksi_min_input = QDoubleSpinBox()
        self.ksi_min_input.setRange(0.01, 0.5)
        self.ksi_min_input.setValue(0.01)
        self.ksi_min_input.setSingleStep(0.01)
        self.ksi_min_input.setDecimals(2)
        
        self.ksi_max_input = QDoubleSpinBox()
        self.ksi_max_input.setRange(0.01, 0.9)
        self.ksi_max_input.setValue(0.5)
        self.ksi_max_input.setSingleStep(0.01)
        self.ksi_max_input.setDecimals(2)
        
        damping_layout.addWidget(QLabel("Min:"))
        damping_layout.addWidget(self.ksi_min_input)
        damping_layout.addWidget(QLabel("Max:"))
        damping_layout.addWidget(self.ksi_max_input)
        bounds_form.addRow(damping_layout)
        
        # Frequency ratio bounds
        bounds_form.addRow(QLabel("Frequency Ratio (β):"))
        
        freq_layout = QHBoxLayout()
        self.beta_min_input = QDoubleSpinBox()
        self.beta_min_input.setRange(0.5, 1.0)
        self.beta_min_input.setValue(0.5)
        self.beta_min_input.setSingleStep(0.01)
        self.beta_min_input.setDecimals(2)
        
        self.beta_max_input = QDoubleSpinBox()
        self.beta_max_input.setRange(0.5, 1.0)
        self.beta_max_input.setValue(1.0)
        self.beta_max_input.setSingleStep(0.01)
        self.beta_max_input.setDecimals(2)
        
        freq_layout.addWidget(QLabel("Min:"))
        freq_layout.addWidget(self.beta_min_input)
        freq_layout.addWidget(QLabel("Max:"))
        freq_layout.addWidget(self.beta_max_input)
        bounds_form.addRow(freq_layout)
        
        bounds_group.setLayout(bounds_form)
        left_layout.addWidget(bounds_group)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.optimize_button = QPushButton("Run Optimization")
        self.optimize_button.clicked.connect(self.run_optimization)
        
        self.compare_button = QPushButton("Compare with Classical")
        self.compare_button.clicked.connect(self.compare_with_classical)
        self.compare_button.setEnabled(False)  # Disable until optimization is run
        
        button_layout.addWidget(self.optimize_button)
        button_layout.addWidget(self.compare_button)
        
        left_layout.addLayout(button_layout)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        left_layout.addWidget(self.progress_bar)
        
        # Status text
        self.status_text = QTextEdit()
        self.status_text.setReadOnly(True)
        self.status_text.setMaximumHeight(100)
        left_layout.addWidget(self.status_text)
        
        # Right panel - Results visualization
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        
        # Create tab widget for different visualizations
        visualization_tabs = QTabWidget()
        
        # 2D Graph tab
        self.canvas = MplCanvas(self, width=5, height=4, dpi=100)
        plot_widget = QWidget()
        plot_layout = QVBoxLayout(plot_widget)
        
        toolbar_container = QWidget()
        toolbar_layout = QVBoxLayout(toolbar_container)
        toolbar_layout.setContentsMargins(0, 0, 0, 0)
        
        self.toolbar = NavigationToolbar(self.canvas, toolbar_container)
        toolbar_layout.addWidget(self.toolbar)
        
        plot_layout.addWidget(toolbar_container)
        plot_layout.addWidget(self.canvas)
        
        # 3D Graph tab
        self.canvas3d = MplCanvas3D(self, width=5, height=4, dpi=100)
        plot3d_widget = QWidget()
        plot3d_layout = QVBoxLayout(plot3d_widget)
        
        toolbar3d_container = QWidget()
        toolbar3d_layout = QVBoxLayout(toolbar3d_container)
        toolbar3d_layout.setContentsMargins(0, 0, 0, 0)
        
        self.toolbar3d = NavigationToolbar(self.canvas3d, toolbar3d_container)
        toolbar3d_layout.addWidget(self.toolbar3d)
        
        plot3d_layout.addWidget(toolbar3d_container)
        plot3d_layout.addWidget(self.canvas3d)
        
        # Add tabs
        visualization_tabs.addTab(plot_widget, "2D Graph")
        visualization_tabs.addTab(plot3d_widget, "3D Graph")
        
        # Results group
        results_group = QGroupBox("Optimization Results")
        results_layout = QVBoxLayout()
        
        self.results_form = QFormLayout()
        
        # Add result labels for optimal parameters
        self.mu_result = QLabel("--")
        self.results_form.addRow("Mass Ratio (μ):", self.mu_result)
        
        self.beta_result = QLabel("--")
        self.results_form.addRow("Frequency Ratio (β):", self.beta_result)
        
        self.ksi_result = QLabel("--")
        self.results_form.addRow("Damping Ratio (ξ):", self.ksi_result)
        
        self.m2_result = QLabel("--")
        self.results_form.addRow("TMD Mass (kg):", self.m2_result)
        
        self.k2_result = QLabel("--")
        self.results_form.addRow("TMD Stiffness (N/m):", self.k2_result)
        
        self.c2_result = QLabel("--")
        self.results_form.addRow("TMD Damping (N·s/m):", self.c2_result)
        
        self.trans_result = QLabel("--")
        self.results_form.addRow("Max Transmissibility:", self.trans_result)
        
        results_layout.addLayout(self.results_form)
        
        # Add visualization selector
        vis_layout = QHBoxLayout()
        vis_layout.addWidget(QLabel("Visualization:"))
        
        self.vis_combo = QComboBox()
        self.vis_combo.addItems([
            "Optimization Progress",
            "Transmissibility Curve",
            "With vs Without TMD",
            "TMD Effectiveness"
        ])
        self.vis_combo.currentIndexChanged.connect(self.update_visualization)
        
        vis_layout.addWidget(self.vis_combo)
        results_layout.addLayout(vis_layout)
        
        results_group.setLayout(results_layout)
        
        # Add to right panel
        right_layout.addWidget(results_group)
        right_layout.addWidget(visualization_tabs)
        
        # Add panels to splitter
        splitter.addWidget(left_panel)
        splitter.addWidget(right_panel)
        splitter.setSizes([300, 900])  # Allocate more space to visualization
        
        # Add splitter to main layout
        main_layout.addWidget(splitter)
    
    def update_frequency_hz(self):
        """Update the frequency in Hz label based on rad/s input"""
        rad_per_s = self.w1_input.value()
        hz = rad_per_s / (2 * 3.14159)
        self.frequency_hz_label.setText(f"{hz:.2f} Hz")
    
    def set_tool_model(self, tool_model):
        """
        Set cutting tool model from tool panel
        
        Args:
            tool_model: CuttingToolModel instance
        """
        self.tool_model = tool_model
        
        # Update system parameters based on tool model
        sdof_model = tool_model.to_single_dof_model()
        
        self.m1_input.setValue(sdof_model['m1'])
        self.w1_input.setValue(sdof_model['w1'])
        self.c1_input.setValue(sdof_model['c1'] / (2 * sdof_model['m1'] * sdof_model['w1']))
        
        self.add_status_message(f"Loaded cutting tool model: {tool_model.length*1000:.0f}mm {tool_model.material}")
    
    def run_optimization(self):
        """Run TMD optimization using the Bees Algorithm"""
        try:
            # Get parameters
            self.m1 = self.m1_input.value()
            self.w1 = self.w1_input.value()
            self.c1 = self.c1_input.value()
            
            # Get Bees Algorithm parameters
            n = self.n_input.value()
            m = self.m_input.value()
            e = self.e_input.value()
            nep = self.nep_input.value()
            nsp = self.nsp_input.value()
            ngh = self.ngh_input.value()
            max_iterations = self.iterations_input.value()
            
            # Get search bounds
            mass_ratio_bounds = (self.mu_min_input.value(), self.mu_max_input.value())
            damping_ratio_bounds = (self.ksi_min_input.value(), self.ksi_max_input.value())
            frequency_ratio_bounds = (self.beta_min_input.value(), self.beta_max_input.value())
            
            # Update status
            self.add_status_message("Starting optimization...")
            self.progress_bar.setValue(0)
            
            # Recreate calculator with current parameters
            if self.tool_model:
                self.calculator = TMDCalculator(tool_model=self.tool_model)
                self.add_status_message("Using cutting tool model for optimization")
            else:
                self.calculator = TMDCalculator(self.m1, None, self.w1, self.c1)
            
            # Create optimizer
            tmd_optimizer = TMDOptimizer(self.analyzer)
            
            # Run optimization
            self.optimization_results = self.calculator.optimize_parameters(
                optimizer_type="bees",
                mass_ratio_bounds=mass_ratio_bounds,
                damping_ratio_bounds=damping_ratio_bounds,
                frequency_ratio_bounds=frequency_ratio_bounds,
                n=n, m=m, e=e, nep=nep, nsp=nsp, ngh=ngh, 
                max_iterations=max_iterations,
                verbose=True
            )
            
            # Update results display
            self.mu_result.setText(f"{self.optimization_results['mu']:.4f}")
            self.beta_result.setText(f"{self.optimization_results['beta']:.4f}")
            self.ksi_result.setText(f"{self.optimization_results['ksi_2_opt']:.4f}")
            self.m2_result.setText(f"{self.optimization_results['m2']:.4f}")
            self.k2_result.setText(f"{self.optimization_results['k2_opt']:.1f}")
            self.c2_result.setText(f"{self.optimization_results['c2_opt']:.4f}")
            self.trans_result.setText(f"{self.optimization_results['max_transmissibility']:.4f}")
            
            # Enable compare button
            self.compare_button.setEnabled(True)
            
            # Update visualization
            self.update_visualization()
            
            # Update status
            self.add_status_message("Optimization completed successfully!")
            self.progress_bar.setValue(100)
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Optimization failed: {str(e)}")
            self.add_status_message(f"Error: {str(e)}")
    
    def compare_with_classical(self):
        """Compare optimization results with classical Den Hartog solution"""
        if not self.optimization_results:
            QMessageBox.warning(self, "Warning", "Run optimization first")
            return
        
        try:
            # Run comparison
            comparison_results = self.calculator.compare_classical_vs_optimized()
            
            # Plot comparison
            self.visualizer.plot_classical_vs_optimized(self.canvas, comparison_results)
            
            # Update status
            improvement = comparison_results['improvement_percentage']
            self.add_status_message(f"Comparison complete. Improvement: {improvement:.1f}%")
            
            # Set visualization combo to show comparison
            self.vis_combo.setCurrentIndex(1)  # Transmissibility Curve
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Comparison failed: {str(e)}")
            self.add_status_message(f"Error: {str(e)}")
    
    def update_visualization(self):
        """Update visualization based on selected visualization type"""
        if not self.optimization_results:
            return
        
        vis_type = self.vis_combo.currentIndex()
        
        try:
            if vis_type == 0:  # Optimization Progress
                self.visualizer.plot_optimization_progress(
                    self.canvas, self.optimization_results['optimization_stats'])
                
            elif vis_type == 1:  # Transmissibility Curve
                # Create data for transmissibility curve
                mu = self.optimization_results['mu']
                beta = self.optimization_results['beta']
                ksi = self.optimization_results['ksi_2_opt']
                
                # Get main system damping ratio
                nub = self.c1
                
                # Generate frequency range
                r_values = np.linspace(0.1, 2.0, 400)
                
                # Calculate transmissibility
                transmissibility = np.zeros(len(r_values))
                for i, r in enumerate(r_values):
                    transmissibility[i] = self.analyzer.calculate_transmissibility(
                        r, beta, mu, ksi, nub)
                
                # Plot
                self.canvas.axes.clear()
                self.canvas.axes.plot(r_values, transmissibility, 'r-', linewidth=2)
                self.canvas.axes.set_xlabel('Frequency Ratio (r)', fontsize=12, fontweight='bold')
                self.canvas.axes.set_ylabel('Transmissibility |X/F|', fontsize=12, fontweight='bold')
                self.canvas.axes.set_title('Optimized TMD Transmissibility', fontsize=14, fontweight='bold')
                self.canvas.axes.grid(True, linestyle='--', alpha=0.7)
                self.canvas.draw()
                
            elif vis_type == 2:  # With vs Without TMD
                # Compare with and without TMD
                comparison_results = self.analyzer.compare_with_without_tmd(
                    self.optimization_results['mu'], 
                    self.c1)
                
                self.visualizer.plot_with_without_tmd(self.canvas, comparison_results)
                
            elif vis_type == 3:  # TMD Effectiveness
                # Show effectiveness vs mass ratio
                effectiveness_results = self.analyzer.calculate_tmd_effectiveness(
                    self.optimization_results['mu'],
                    self.c1)
                
                self.visualizer.plot_tmd_effectiveness(self.canvas, effectiveness_results)
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Visualization failed: {str(e)}")
            self.add_status_message(f"Error: {str(e)}")
    
    def add_status_message(self, message):
        """Add message to status text box"""
        self.status_text.append(message)
        # Scroll to bottom
        self.status_text.verticalScrollBar().setValue(
            self.status_text.verticalScrollBar().maximum())
    
    def save_current_plot(self, filename):
        """Save current plot to file"""
        self.canvas.fig.savefig(filename, dpi=300, bbox_inches='tight')