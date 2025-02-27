# core/tmd_calculator.py
import numpy as np
from typing import Dict, Any, Optional, Union, List
from core.cutting_tool import CuttingToolModel
from core.optimizers import TMDOptimizer
from core.analyzers import TMDAnalyzer

class TMDCalculator:
    """Advanced TMD calculation and design class"""
    
    def __init__(self, 
                m1: float = 1.0, 
                m2: Optional[float] = None, 
                w1: float = 707, 
                c1: float = 0,
                tool_model: Optional[CuttingToolModel] = None):
        """
        Initialize the TMD calculator
        
        Args:
            m1 (float): Main system mass (kg)
            m2 (float, optional): TMD mass (kg). If None, will be calculated based on mass ratio
            w1 (float): Main system natural frequency (rad/s)
            c1 (float): Main system damping coefficient
            tool_model (CuttingToolModel, optional): Cutting tool model, takes precedence over m1, w1 if provided
        """
        self.analyzer = TMDAnalyzer()
        
        if tool_model is not None:
            # Use tool model parameters
            sdof_model = tool_model.to_single_dof_model()
            self.m1 = sdof_model['m1']
            self.w1 = sdof_model['w1']
            self.c1 = sdof_model['c1']
            self.k1 = sdof_model['k1']
            self.tool_model = tool_model
        else:
            # Use provided parameters
            self.m1 = m1
            self.m2 = m2
            self.w1 = w1
            self.c1 = c1
            self.k1 = w1**2 * m1
            self.tool_model = None
        
        # Mass ratio, to be determined
        self.mu = None if m2 is None else m2 / m1
        
        # Calculated parameters, will be filled after optimization
        self.optimal_params = None
    
    def calculate_parameters(self, mass_ratio: Optional[float] = None) -> Dict[str, float]:
        """
        Calculate TMD parameters using classical Den Hartog formulas
        
        Args:
            mass_ratio (float, optional): Mass ratio (m2/m1). If None and m2 is not set, uses 0.2
            
        Returns:
            dict: Calculated parameters
        """
        if mass_ratio is not None:
            self.mu = mass_ratio
        elif self.mu is None:  # If neither m2 nor mass_ratio provided
            self.mu = 0.2  # Default mass ratio
        
        # Calculate m2 if not provided
        if self.m2 is None:
            self.m2 = self.mu * self.m1
        
        # Calculate optimal parameters using Den Hartog formulas
        opt_params = self.analyzer.calculate_optimal_parameters(self.mu)
        beta_opt = opt_params['beta_opt']
        ksi_opt = opt_params['ksi_opt']
        
        # Calculate TMD parameters
        w2_opt = beta_opt * self.w1
        k2_opt = w2_opt**2 * self.m2
        c2_opt = 2 * ksi_opt * self.m2 * w2_opt
        
        # Store calculated parameters
        self.optimal_params = {
            'mu': self.mu,
            'k1': self.k1,
            'w2_opt': w2_opt,
            'k2_opt': k2_opt,
            'ksi_2_opt': ksi_opt,
            'c2_opt': c2_opt,
            'beta': beta_opt
        }
        
        return self.optimal_params
    
    def optimize_parameters(self, 
                          optimizer_type: str = "bees", 
                          mass_ratio_bounds: tuple = (0.05, 0.5), 
                          **optimizer_params) -> Dict[str, Any]:
        """
        Optimize TMD parameters using specified optimization algorithm
        
        Args:
            optimizer_type (str): Optimization algorithm to use ('bees', 'genetic', etc.)
            mass_ratio_bounds (tuple): Mass ratio bounds (min, max)
            **optimizer_params: Additional parameters for the optimizer
            
        Returns:
            dict: Optimized parameters
        """
        # Create TMD optimizer
        tmd_optimizer = TMDOptimizer(self.analyzer)
        
        # Run optimization
        optimal_params = tmd_optimizer.optimize_tmd_parameters(
            main_mass=self.m1,
            main_frequency=self.w1,
            mass_ratio_bounds=mass_ratio_bounds,
            algorithm=optimizer_type,
            **optimizer_params
        )
        
        # Update parameters
        self.mu = optimal_params['mu']
        self.m2 = optimal_params['m2']
        self.optimal_params = optimal_params
        
        return optimal_params
    
    def calculate_multiple_solutions(self, mass_ratios: List[float]) -> List[Dict[str, float]]:
        """
        Calculate TMD parameters for multiple mass ratios
        
        Args:
            mass_ratios (list): List of mass ratios to calculate parameters for
            
        Returns:
            list: List of dictionaries with parameters for each mass ratio
        """
        solutions = []
        
        for mu in mass_ratios:
            # Save current mu
            current_mu = self.mu
            
            # Calculate for new mu
            params = self.calculate_parameters(mass_ratio=mu)
            
            # Add to solutions
            solutions.append(params.copy())
            
            # Restore original mu
            self.mu = current_mu
        
        return solutions
    
    def compare_classical_vs_optimized(self) -> Dict[str, Any]:
        """
        Compare classical Den Hartog solution with optimized solution
        
        Returns:
            dict: Comparison results
        """
        # Ensure we have an optimized solution
        if self.optimal_params is None or 'optimization_stats' not in self.optimal_params:
            raise ValueError("Optimized parameters not available. Run optimize_parameters() first.")
        
        # Calculate classical solution
        classical_params = self.calculate_parameters(mass_ratio=self.mu)
        
        # Get optimized solution
        optimized_params = self.optimal_params
        
        # Define frequency range for comparison
        r_values = np.linspace(0.5, 1.5, 100)
        
        # Calculate transmissibility for both solutions
        classical_trans = np.zeros(len(r_values))
        optimized_trans = np.zeros(len(r_values))
        
        nub = self.c1 / (2 * self.m1 * self.w1) if self.w1 > 0 else 0
        
        for i, r in enumerate(r_values):
            classical_trans[i] = self.analyzer.calculate_transmissibility(
                r, classical_params['beta'], self.mu, classical_params['ksi_2_opt'], nub
            )
            
            optimized_trans[i] = self.analyzer.calculate_transmissibility(
                r, optimized_params['beta'], self.mu, optimized_params['ksi_2_opt'], nub
            )
        
        # Find maximum transmissibility for each
        max_classical = np.max(classical_trans)
        max_optimized = np.max(optimized_trans)
        
        return {
            'r_values': r_values,
            'classical_trans': classical_trans,
            'optimized_trans': optimized_trans,
            'max_classical': max_classical,
            'max_optimized': max_optimized,
            'improvement_percentage': ((max_classical - max_optimized) / max_classical) * 100,
            'classical_params': classical_params,
            'optimized_params': optimized_params
        }
    
    def get_design_recommendations(self) -> Dict[str, Any]:
        """
        Get practical design recommendations for TMD
        
        Returns:
            dict: Design recommendations
        """
        if self.optimal_params is None:
            raise ValueError("Parameters not calculated. Run calculate_parameters() or optimize_parameters() first.")
        
        # Get optimal parameters
        k2_opt = self.optimal_params['k2_opt']
        c2_opt = self.optimal_params['c2_opt']
        
        # Spring design recommendations
        spring_wire_diameter_mm = 10.0  # Example, would need actual calculation
        spring_coil_diameter_mm = 50.0  # Example
        spring_free_length_mm = 100.0   # Example
        
        # Damper design recommendations
        damper_type = "Viscous"  # Example
        damper_fluid_viscosity = "Medium"  # Example
        
        return {
            'recommended_spring': {
                'type': 'Helical Compression Spring',
                'wire_diameter_mm': spring_wire_diameter_mm,
                'coil_diameter_mm': spring_coil_diameter_mm,
                'free_length_mm': spring_free_length_mm,
                'stiffness_N_m': k2_opt,
                'material': 'Spring Steel'
            },
            'recommended_damper': {
                'type': damper_type,
                'damping_coefficient_Ns_m': c2_opt,
                'fluid_viscosity': damper_fluid_viscosity
            },
            'installation_notes': [
                "Mount TMD at position of maximum vibration amplitude (typically at the tool tip)",
                f"Ensure mass is secured and weighs exactly {self.m2:.3f} kg",
                "Verify spring stiffness experimentally before final installation",
                "Consider multiple smaller TMDs if space is constrained"
            ],
            'optimal_params': self.optimal_params
        }