# ui/tool_panel.py
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, QLineEdit, 
                            QGroupBox, QPushButton, QMessageBox, QComboBox, QSpinBox, QDoubleSpinBox,
                            QTabWidget, QSplitter, QFormLayout)
from PyQt6.QtCore import pyqtSignal, Qt
from PyQt6.QtGui import QFont, QIcon, QPixmap

from core.visualizers import MplCanvas, NavigationToolbar, TMDVisualizer
from core.cutting_tool import CuttingToolModel
import numpy as np

class CuttingToolPanel(QWidget):
    """Panel for cutting tool analysis and TMD design"""
    
    # Signal emitted when a tool model is created
    tool_model_created = pyqtSignal(object)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Initialize visualizer
        self.visualizer = TMDVisualizer()
        
        # Initialize default tool parameters
        self.length = 808.0  # mm (from paper)
        self.diameter = 20.0  # mm
        self.material = 'steel'
        self.mass = 3.94  # kg (from paper)
        
        # Tool model
        self.tool_model = None
        
        self.initUI()
    
    def initUI(self):
        """Initialize the user interface"""
        main_layout = QVBoxLayout(self)
        
        # Create splitter for parameters and visualization
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Left panel - parameters
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        
        # Tool geometry
        geometry_group = QGroupBox("Tool Geometry")
        geometry_form = QFormLayout()
        
        self.length_input = QDoubleSpinBox()
        self.length_input.setRange(100.0, 2000.0)
        self.length_input.setValue(self.length)
        self.length_input.setSingleStep(10.0)
        self.length_input.setSuffix(" mm")
        geometry_form.addRow("Length:", self.length_input)
        
        self.diameter_input = QDoubleSpinBox()
        self.diameter_input.setRange(5.0, 100.0)
        self.diameter_input.setValue(self.diameter)
        self.diameter_input.setSingleStep(1.0)
        self.diameter_input.setSuffix(" mm")
        geometry_form.addRow("Diameter:", self.diameter_input)
        
        self.material_combo = QComboBox()
        self.material_combo.addItems(['steel', 'aluminum', 'carbide'])
        geometry_form.addRow("Material:", self.material_combo)
        
        self.mass_input = QDoubleSpinBox()
        self.mass_input.setRange(0.1, 50.0)
        self.mass_input.setValue(self.mass)
        self.mass_input.setSingleStep(0.1)
        self.mass_input.setSuffix(" kg")
        geometry_form.addRow("Mass (optional):", self.mass_input)
        
        self.calculate_button = QPushButton("Calculate Tool Properties")
        self.calculate_button.clicked.connect(self.calculate_tool_properties)
        geometry_form.addRow(self.calculate_button)
        
        geometry_group.setLayout(geometry_form)
        left_layout.addWidget(geometry_group)
        
        # Tool properties (calculated)
        properties_group = QGroupBox("Calculated Properties")
        properties_form = QFormLayout()
        
        self.natural_freq_label = QLabel("--")
        properties_form.addRow("Natural Frequency (1st mode):", self.natural_freq_label)
        
        self.stiffness_label = QLabel("--")
        properties_form.addRow("Stiffness:", self.stiffness_label)
        
        self.moment_inertia_label = QLabel("--")
        properties_form.addRow("Moment of Inertia:", self.moment_inertia_label)
        
        properties_group.setLayout(properties_form)
        left_layout.addWidget(properties_group)
        
        # TMD design
        tmd_group = QGroupBox("TMD Design")
        tmd_form = QFormLayout()
        
        self.mass_ratio_input = QDoubleSpinBox()
        self.mass_ratio_input.setRange(0.05, 0.5)
        self.mass_ratio_input.setValue(0.3)
        self.mass_ratio_input.setSingleStep(0.05)
        self.mass_ratio_input.setDecimals(2)
        tmd_form.addRow("Mass Ratio (μ):", self.mass_ratio_input)
        
        self.design_button = QPushButton("Design TMD")
        self.design_button.clicked.connect(self.design_tmd)
        self.design_button.setEnabled(False)  # Enable after calculating properties
        tmd_form.addRow(self.design_button)
        
        self.tmd_mass_label = QLabel("--")
        tmd_form.addRow("TMD Mass:", self.tmd_mass_label)
        
        self.tmd_stiffness_label = QLabel("--")
        tmd_form.addRow("TMD Stiffness:", self.tmd_stiffness_label)
        
        self.tmd_damping_label = QLabel("--")
        tmd_form.addRow("TMD Damping:", self.tmd_damping_label)
        
        tmd_group.setLayout(tmd_form)
        left_layout.addWidget(tmd_group)
        
        # Analysis options
        analysis_group = QGroupBox("Analysis Options")
        analysis_layout = QVBoxLayout()
        
        self.analysis_combo = QComboBox()
        self.analysis_combo.addItems([
            "Natural Frequencies", 
            "With vs. Without TMD", 
            "TMD Effectiveness"
        ])
        analysis_layout.addWidget(self.analysis_combo)
        
        self.analyze_button = QPushButton("Analyze")
        self.analyze_button.clicked.connect(self.run_analysis)
        self.analyze_button.setEnabled(False)  # Enable after calculating properties
        analysis_layout.addWidget(self.analyze_button)
        
        analysis_group.setLayout(analysis_layout)
        left_layout.addWidget(analysis_group)
        
        # Right panel - visualization
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        
        # Visualization canvas
        self.canvas = MplCanvas(self, width=5, height=4, dpi=100)
        
        # Toolbar
        toolbar_container = QWidget()
        toolbar_layout = QVBoxLayout(toolbar_container)
        toolbar_layout.setContentsMargins(0, 0, 0, 0)
        
        self.toolbar = NavigationToolbar(self.canvas, toolbar_container)
        toolbar_layout.addWidget(self.toolbar)
        
        right_layout.addWidget(toolbar_container)
        right_layout.addWidget(self.canvas)
        
        # Add panels to splitter
        splitter.addWidget(left_panel)
        splitter.addWidget(right_panel)
        splitter.setSizes([300, 700])  # Allocate more space to visualization
        
        # Add splitter to main layout
        main_layout.addWidget(splitter)
    
    def calculate_tool_properties(self):
        """Calculate cutting tool properties"""
        try:
            # Get parameters
            length = self.length_input.value()
            diameter = self.diameter_input.value()
            material = self.material_combo.currentText()
            mass = self.mass_input.value()
            
            # Create tool model
            self.tool_model = CuttingToolModel(
                length=length,
                diameter=diameter,
                material=material,
                mass=mass
            )
            
            # Calculate properties
            natural_frequencies = self.tool_model.calculate_natural_frequencies(modes=5)
            stiffness = self.tool_model.calculate_stiffness()
            moment_of_inertia = self.tool_model.moment_of_inertia
            
            # Update labels
            self.natural_freq_label.setText(f"{natural_frequencies[0]:.2f} Hz")
            self.stiffness_label.setText(f"{stiffness:.2e} N/m")
            self.moment_inertia_label.setText(f"{moment_of_inertia:.2e} m⁴")
            
            # Enable buttons
            self.design_button.setEnabled(True)
            self.analyze_button.setEnabled(True)
            
            # Visualize natural frequencies
            self.visualizer.plot_cutting_tool_modes(self.canvas, self.tool_model)
            
            # Emit signal with tool model
            self.tool_model_created.emit(self.tool_model)
            
            # Show success message
            QMessageBox.information(self, "Success", "Tool properties calculated successfully!")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to calculate tool properties: {str(e)}")
    
    def design_tmd(self):
        """Design TMD for the cutting tool"""
        if not self.tool_model:
            QMessageBox.warning(self, "Warning", "Calculate tool properties first")
            return
        
        try:
            # Get mass ratio
            mass_ratio = self.mass_ratio_input.value()
            
            # Get SDOF model
            sdof_model = self.tool_model.to_single_dof_model()
            
            # Calculate TMD parameters
            m1 = sdof_model['m1']
            w1 = sdof_model['w1']
            
            # Calculate TMD mass
            m2 = mass_ratio * m1
            
            # Calculate frequency ratio using Den Hartog formula
            beta = 1 / (1 + mass_ratio)
            
            # Calculate TMD natural frequency
            w2 = beta * w1
            
            # Calculate optimal damping ratio
            ksi_opt = np.sqrt((3 * mass_ratio) / (8 * (1 + mass_ratio)))
            
            # Calculate TMD parameters
            k2 = w2**2 * m2
            c2 = 2 * ksi_opt * m2 * w2
            
            # Update labels
            self.tmd_mass_label.setText(f"{m2:.3f} kg")
            self.tmd_stiffness_label.setText(f"{k2:.2f} N/m")
            self.tmd_damping_label.setText(f"{c2:.2f} N·s/m")
            
            # Plot with vs without TMD
            comparison_results = {
                'r_values': np.linspace(0.1, 2.0, 400),
                'with_tmd': np.zeros(400),
                'without_tmd': np.zeros(400),
                'mu': mass_ratio,
                'beta': beta,
                'ksi': ksi_opt,
                'nub': 0.05  # Default damping ratio
            }
            
            # Calculate transmissibility
            for i, r in enumerate(comparison_results['r_values']):
                # For without TMD: |X/F| = 1/sqrt((1-r^2)^2 + (2*zeta*r)^2)
                denominator = (1 - r**2)**2 + (2 * 0.05 * r)**2
                comparison_results['without_tmd'][i] = 1 / np.sqrt(denominator) if denominator > 0 else float('inf')
                
                # For with TMD:
                comparison_results['with_tmd'][i] = self.calculate_transmissibility(
                    r, beta, mass_ratio, ksi_opt, 0.05)
            
            # Plot comparison
            self.visualizer.plot_with_without_tmd(self.canvas, comparison_results)
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to design TMD: {str(e)}")
    
    def calculate_transmissibility(self, r, beta, mu, nua, nub):
        """Calculate transmissibility"""
        numerator = (beta**2 - r**2)**2 + 4 * (r**2) * (nua**2)
        
        denominator1 = ((1 - (r**2)) * ((beta**2) - (r**2)) - (mu * (beta**2) * (r**2)) - (4 * nua * nub * (r**2)))**2
        denominator2 = (nua * (1 - (r**2) - mu * (r**2)) + (nub * ((beta**2) - (r**2))))**2
        denominator3 = denominator2 * 4 * (r**2)
        denominator = denominator1 + denominator3
        
        return np.sqrt(numerator / denominator)
    
    def run_analysis(self):
        """Run selected analysis"""
        if not self.tool_model:
            QMessageBox.warning(self, "Warning", "Calculate tool properties first")
            return
        
        analysis_type = self.analysis_combo.currentIndex()
        
        try:
            if analysis_type == 0:  # Natural Frequencies
                self.visualizer.plot_cutting_tool_modes(self.canvas, self.tool_model)
                
            elif analysis_type == 1:  # With vs. Without TMD
                # Get mass ratio
                mass_ratio = self.mass_ratio_input.value()
                
                # Get SDOF model
                sdof_model = self.tool_model.to_single_dof_model()
                
                # Calculate TMD parameters
                m1 = sdof_model['m1']
                w1 = sdof_model['w1']
                
                # Calculate frequency ratio using Den Hartog formula
                beta = 1 / (1 + mass_ratio)
                
                # Calculate optimal damping ratio
                ksi_opt = np.sqrt((3 * mass_ratio) / (8 * (1 + mass_ratio)))
                
                # Create comparison results
                comparison_results = {
                    'r_values': np.linspace(0.1, 2.0, 400),
                    'with_tmd': np.zeros(400),
                    'without_tmd': np.zeros(400),
                    'mu': mass_ratio,
                    'beta': beta,
                    'ksi': ksi_opt,
                    'nub': 0.05  # Default damping ratio
                }
                
                # Calculate transmissibility
                for i, r in enumerate(comparison_results['r_values']):
                    # For without TMD
                    denominator = (1 - r**2)**2 + (2 * 0.05 * r)**2
                    comparison_results['without_tmd'][i] = 1 / np.sqrt(denominator) if denominator > 0 else float('inf')
                    
                    # For with TMD
                    comparison_results['with_tmd'][i] = self.calculate_transmissibility(
                        r, beta, mass_ratio, ksi_opt, 0.05)
                
                # Plot comparison
                self.visualizer.plot_with_without_tmd(self.canvas, comparison_results)
                
            elif analysis_type == 2:  # TMD Effectiveness
                # Create effectiveness results
                mu_values = np.linspace(0.01, 0.5, 100)
                max_transmissibility = np.zeros(len(mu_values))
                
                for i, mu_val in enumerate(mu_values):
                    # Calculate optimal parameters
                    beta_opt = 1 / (1 + mu_val)
                    ksi_opt = np.sqrt((3 * mu_val) / (8 * (1 + mu_val)))
                    
                    # Calculate transmissibility around resonance
                    r_values = np.linspace(0.7, 1.3, 50)
                    transmissibility = np.zeros(len(r_values))
                    
                    for j, r in enumerate(r_values):
                        transmissibility[j] = self.calculate_transmissibility(
                            r, beta_opt, mu_val, ksi_opt, 0.05)
                    
                    # Get maximum transmissibility
                    max_transmissibility[i] = np.max(transmissibility)
                
                # Calculate without TMD (single peak)
                without_tmd = 1 / (2 * 0.05)  # At resonance for damping 0.05
                
                # Calculate effectiveness
                effectiveness = 1 - (max_transmissibility / without_tmd)
                
                # Create results dictionary
                effectiveness_results = {
                    'mu_values': mu_values,
                    'max_transmissibility': max_transmissibility,
                    'without_tmd': without_tmd,
                    'effectiveness': effectiveness
                }
                
                # Plot effectiveness
                self.visualizer.plot_tmd_effectiveness(self.canvas, effectiveness_results)
        
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Analysis failed: {str(e)}")
    
    def save_current_plot(self, filename):
        """Save current plot to file"""
        self.canvas.fig.savefig(filename, dpi=300, bbox_inches='tight')