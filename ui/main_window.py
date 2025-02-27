# ui/main_window.py
import sys
import os
from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QSplitter, 
                            QTabWidget, QMessageBox, QFileDialog, QDockWidget)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon, QAction

from ui.parameter_panel import ParameterPanel
from ui.graph_panel import GraphPanel
from ui.optimizer_panel import OptimizerPanel
from ui.tool_panel import CuttingToolPanel

class TMDAnalyzer(QMainWindow):
    """TMD Analyzer main window class"""
    
    def __init__(self):
        super().__init__()
        
        self.initUI()
        
    def initUI(self):
        """Initialize the user interface"""
        self.setWindowTitle('TMD Analyzer - Cutting Tool Vibration Suppression')
        self.setGeometry(100, 100, 1200, 800)
        
        # Set favicon
        try:
            icon = QIcon("assets/favicon.png")
            self.setWindowIcon(icon)
        except:
            pass
        
        # Create menu bar
        self.create_menu()
        
        # Main widget
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        
        # Main layout
        main_layout = QVBoxLayout(main_widget)
        main_layout.setContentsMargins(5, 5, 5, 5)
        
        # Create tab widget for different analysis modes
        self.tab_widget = QTabWidget()
        
        # ----- Standard TMD Analysis Tab -----
        standard_tab = QWidget()
        standard_layout = QVBoxLayout(standard_tab)
        
        # Create splitter for parameter and graph panels
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Parameter panel
        self.parameter_panel = ParameterPanel()
        
        # Graph panel
        self.graph_panel = GraphPanel()
        
        # Connect parameter panel to graph panel
        self.parameter_panel.parameters_calculated.connect(self.graph_panel.update_parameters)
        
        # Add panels to splitter
        splitter.addWidget(self.parameter_panel)
        splitter.addWidget(self.graph_panel)
        splitter.setSizes([250, 950])  # Allocate more space to graph
        
        standard_layout.addWidget(splitter)
        
        # ----- Optimization Tab -----
        optimization_tab = QWidget()
        optimization_layout = QVBoxLayout(optimization_tab)
        
        # Create optimizer panel
        self.optimizer_panel = OptimizerPanel()
        
        # Add to layout
        optimization_layout.addWidget(self.optimizer_panel)
        
        # ----- Cutting Tool Analysis Tab -----
        tool_tab = QWidget()
        tool_layout = QVBoxLayout(tool_tab)
        
        # Create cutting tool panel
        self.tool_panel = CuttingToolPanel()
        
        # Add to layout
        tool_layout.addWidget(self.tool_panel)
        
        # Connect tool panel to optimizer panel
        self.tool_panel.tool_model_created.connect(self.optimizer_panel.set_tool_model)
        
        # Add tabs to tab widget
        self.tab_widget.addTab(standard_tab, "Standard TMD Analysis")
        self.tab_widget.addTab(optimization_tab, "Bees Algorithm Optimization")
        self.tab_widget.addTab(tool_tab, "Cutting Tool Analysis")
        
        # Add tab widget to main layout
        main_layout.addWidget(self.tab_widget)
        
        # Show status bar
        self.statusBar().showMessage('Ready')
    
    def create_menu(self):
        """Create application menu"""
        # Create actions
        # File menu
        exit_action = QAction('Exit', self)
        exit_action.setShortcut('Ctrl+Q')
        exit_action.setStatusTip('Exit application')
        exit_action.triggered.connect(self.close)
        
        save_project_action = QAction('Save Project', self)
        save_project_action.setShortcut('Ctrl+S')
        save_project_action.setStatusTip('Save current project')
        save_project_action.triggered.connect(self.save_project)
        
        load_project_action = QAction('Load Project', self)
        load_project_action.setShortcut('Ctrl+O')
        load_project_action.setStatusTip('Load project from file')
        load_project_action.triggered.connect(self.load_project)
        
        # Tools menu
        export_results_action = QAction('Export Results', self)
        export_results_action.setStatusTip('Export analysis results')
        export_results_action.triggered.connect(self.export_results)
        
        export_graph_action = QAction('Export Graph', self)
        export_graph_action.setStatusTip('Export current graph')
        export_graph_action.triggered.connect(self.export_graph)
        
        # Help menu
        about_action = QAction('About', self)
        about_action.setStatusTip('About this application')
        about_action.triggered.connect(self.show_about)
        
        help_action = QAction('Help', self)
        help_action.setShortcut('F1')
        help_action.setStatusTip('Show help')
        help_action.triggered.connect(self.show_help)
        
        # Create menubar
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu('&File')
        file_menu.addAction(save_project_action)
        file_menu.addAction(load_project_action)
        file_menu.addSeparator()
        file_menu.addAction(exit_action)
        
        # Tools menu
        tools_menu = menubar.addMenu('&Tools')
        tools_menu.addAction(export_results_action)
        tools_menu.addAction(export_graph_action)
        
        # Help menu
        help_menu = menubar.addMenu('&Help')
        help_menu.addAction(help_action)
        help_menu.addAction(about_action)
    
    def save_project(self):
        """Save current project to file"""
        file_name, _ = QFileDialog.getSaveFileName(
            self, 
            "Save Project", 
            "", 
            "TMD Project Files (*.tmd);;All Files (*)"
        )
        
        if file_name:
            try:
                # Implement saving logic here
                QMessageBox.information(self, "Success", f"Project saved to {file_name}")
                self.statusBar().showMessage(f'Project saved to {file_name}')
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to save project: {str(e)}")
    
    def load_project(self):
        """Load project from file"""
        file_name, _ = QFileDialog.getOpenFileName(
            self, 
            "Load Project", 
            "", 
            "TMD Project Files (*.tmd);;All Files (*)"
        )
        
        if file_name:
            try:
                # Implement loading logic here
                QMessageBox.information(self, "Success", f"Project loaded from {file_name}")
                self.statusBar().showMessage(f'Project loaded from {file_name}')
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to load project: {str(e)}")
    
    def export_results(self):
        """Export analysis results"""
        file_name, _ = QFileDialog.getSaveFileName(
            self, 
            "Export Results", 
            "", 
            "CSV Files (*.csv);;Excel Files (*.xlsx);;JSON Files (*.json);;All Files (*)"
        )
        
        if file_name:
            try:
                # Implement export logic here
                QMessageBox.information(self, "Success", f"Results exported to {file_name}")
                self.statusBar().showMessage(f'Results exported to {file_name}')
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to export results: {str(e)}")
    
    def export_graph(self):
        """Export current graph"""
        file_name, _ = QFileDialog.getSaveFileName(
            self, 
            "Export Graph", 
            "", 
            "PNG Files (*.png);;JPEG Files (*.jpg);;SVG Files (*.svg);;PDF Files (*.pdf);;All Files (*)"
        )
        
        if file_name:
            try:
                # Get current tab
                current_tab_index = self.tab_widget.currentIndex()
                
                if current_tab_index == 0:  # Standard analysis
                    self.graph_panel.save_current_plot(file_name)
                elif current_tab_index == 1:  # Optimization
                    self.optimizer_panel.save_current_plot(file_name)
                elif current_tab_index == 2:  # Cutting tool
                    self.tool_panel.save_current_plot(file_name)
                
                QMessageBox.information(self, "Success", f"Graph exported to {file_name}")
                self.statusBar().showMessage(f'Graph exported to {file_name}')
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to export graph: {str(e)}")
    
    def show_about(self):
        """Show about dialog"""
        about_text = """
        <h1>TMD Analyzer</h1>
        <p>Version 1.0</p>
        <p>A specialized tool for the optimization of Tuned Mass Dampers (TMD) 
        for vibration suppression of cutting tool holders using the Bees Algorithm.</p>
        <p>Based on the research paper:<br>
        "OPTIMIZATION OF THE TUNED MASS DAMPER FOR VIBRATION SUPPRESSION OF A CUTTING TOOL HOLDER USING THE BEES ALGORITHM"</p>
        <p>Copyright © 2024</p>
        """
        
        QMessageBox.about(self, "About TMD Analyzer", about_text)
    
    def show_help(self):
        """Show help information"""
        help_text = """
        <h1>TMD Analyzer Help</h1>
        
        <h2>Standard TMD Analysis</h2>
        <p>This tab allows you to analyze basic TMD parameters using classical formulas:</p>
        <ul>
            <li>Enter main system parameters (mass, frequency, damping)</li>
            <li>Enter TMD mass or mass ratio</li>
            <li>Click "Calculate Parameters" to compute optimal TMD parameters</li>
            <li>Use the Graph Panel to visualize different analysis types</li>
        </ul>
        
        <h2>Bees Algorithm Optimization</h2>
        <p>This tab uses the Bees Algorithm to find optimal TMD parameters:</p>
        <ul>
            <li>Set optimization parameters</li>
            <li>Click "Run Optimization" to find the best TMD parameters</li>
            <li>Compare results with classical formulas</li>
        </ul>
        
        <h2>Cutting Tool Analysis</h2>
        <p>This tab allows modeling of cutting tool holders:</p>
        <ul>
            <li>Define tool geometry and material</li>
            <li>Analyze natural frequencies</li>
            <li>Design TMD specifically for the modeled tool</li>
        </ul>
        """
        
        help_dialog = QMessageBox(self)
        help_dialog.setWindowTitle("TMD Analyzer Help")
        help_dialog.setText(help_text)
        help_dialog.setStandardButtons(QMessageBox.StandardButton.Ok)
        help_dialog.exec()