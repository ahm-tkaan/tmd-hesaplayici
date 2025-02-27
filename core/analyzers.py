# core/analyzers.py
import numpy as np
from functools import lru_cache
from typing import Dict, List, Tuple, Optional

class TMDAnalyzer:
    """Analyzes TMD systems with various parameters"""
    
    def __init__(self):
        """Initialize the analyzer"""
        pass
    
    @lru_cache(maxsize=1024)
    def calculate_transmissibility(self, r: float, beta: float, mu: float, nua: float, nub: float) -> float:
        """
        Calculate transmissibility for given parameters
        
        Args:
            r (float): Frequency ratio
            beta (float): TMD frequency ratio
            mu (float): Mass ratio
            nua (float): TMD damping ratio
            nub (float): Main system damping ratio
            
        Returns:
            float: Calculated transmissibility value
        """
        numerator = (beta**2 - r**2)**2 + 4 * (r**2) * (nua**2)
        
        denominator1 = ((1 - (r**2)) * ((beta**2) - (r**2)) - (mu * (beta**2) * (r**2)) - (4 * nua * nub * (r**2)))**2
        denominator2 = (nua * (1 - (r**2) - mu * (r**2)) + (nub * ((beta**2) - (r**2))))**2
        denominator3 = denominator2 * 4 * (r**2)
        denominator = denominator1 + denominator3
        
        return np.sqrt(numerator / denominator)
    
    def calculate_optimal_parameters(self, mu: float) -> Dict[str, float]:
        """
        Calculate optimal TMD parameters based on Den Hartog's classical formulas
        
        Args:
            mu (float): Mass ratio
            
        Returns:
            dict: Dictionary with optimal parameters
        """
        # Optimal frequency ratio
        beta_opt = 1 / (1 + mu)
        
        # Optimal damping ratio
        ksi_opt = np.sqrt((3 * mu) / (8 * (1 + mu)))
        
        return {
            'beta_opt': beta_opt,
            'ksi_opt': ksi_opt
        }
    
    def frequency_ratio_analysis(self, mu: float, nub: float = 0.01, num_points: int = 400, 
                                 r_range: Tuple[float, float] = (0.1, 2.0),
                                 beta_values: Optional[List[float]] = None) -> Dict:
        """
        Perform frequency ratio analysis
        
        Args:
            mu (float): Mass ratio
            nub (float): Main system damping ratio
            num_points (int): Number of points for frequency range
            r_range (tuple): Range of frequency ratio values (min, max)
            beta_values (list, optional): List of frequency ratios to analyze, defaults to range 0.5-1.0
            
        Returns:
            dict: Analysis results
        """
        if beta_values is None:
            beta_values = np.arange(0.5, 1.05, 0.1)
            
        r_values = np.linspace(r_range[0], r_range[1], num_points)
        results = np.zeros((len(r_values), len(beta_values)))
        
        # Calculate optimal parameters for reference
        opt_params = self.calculate_optimal_parameters(mu)
        
        # Perform transmissibility calculations
        for j, beta in enumerate(beta_values):
            # Calculate optimal damping
            if np.isclose(beta, opt_params['beta_opt'], atol=0.01):
                nua = opt_params['ksi_opt']
            else:
                nua = np.sqrt((3 * mu) / (8 * (1 + mu)))  # Use formula as approximation
            
            for i, r in enumerate(r_values):
                results[i, j] = self.calculate_transmissibility(r, beta, mu, nua, nub)
        
        return {
            'r_values': r_values,
            'beta_values': beta_values,
            'results': results,
            'mu': mu,
            'optimal_beta': opt_params['beta_opt'],
            'optimal_ksi': opt_params['ksi_opt']
        }
    
    def damping_ratio_analysis(self, mu: float, nub: float = 0.01, num_points: int = 400,
                              r_range: Tuple[float, float] = (0.1, 2.0),
                              damping_values: Optional[List[float]] = None) -> Dict:
        """
        Perform damping ratio analysis
        
        Args:
            mu (float): Mass ratio
            nub (float): Main system damping ratio
            num_points (int): Number of points for frequency range
            r_range (tuple): Range of frequency ratio values (min, max)
            damping_values (list, optional): List of damping values to analyze
            
        Returns:
            dict: Analysis results
        """
        # Calculate optimal parameters
        opt_params = self.calculate_optimal_parameters(mu)
        beta = opt_params['beta_opt']  # Use optimal frequency ratio
        
        if damping_values is None:
            # Include optimal damping in the list
            optimal_ksi = opt_params['ksi_opt']
            damping_values = [0.0, 0.1, optimal_ksi, 0.3, 0.6, 0.99]
            # Sort damping values
            damping_values = sorted(damping_values)
        
        r_values = np.linspace(r_range[0], r_range[1], num_points)
        results = np.zeros((len(r_values), len(damping_values)))
        
        # Perform transmissibility calculations
        for j, nua in enumerate(damping_values):
            for i, r in enumerate(r_values):
                results[i, j] = self.calculate_transmissibility(r, beta, mu, nua, nub)
        
        return {
            'r_values': r_values,
            'damping_values': damping_values,
            'results': results,
            'mu': mu,
            'beta': beta,
            'optimal_ksi': opt_params['ksi_opt']
        }
    
    def mass_ratio_analysis(self, current_mu: float, nub: float = 0.01, num_points: int = 400,
                           r_range: Tuple[float, float] = (0.1, 2.0),
                           mass_values: Optional[List[float]] = None) -> Dict:
        """
        Perform mass ratio analysis
        
        Args:
            current_mu (float): Current mass ratio
            nub (float): Main system damping ratio
            num_points (int): Number of points for frequency range
            r_range (tuple): Range of frequency ratio values (min, max)
            mass_values (list, optional): List of mass ratios to analyze
            
        Returns:
            dict: Analysis results
        """
        if mass_values is None:
            # Generate mass ratio values
            mass_values = np.linspace(0.05, 0.5, 10)
        
        r_values = np.linspace(r_range[0], r_range[1], num_points)
        results = np.zeros((len(r_values), len(mass_values)))
        
        # Current system optimal parameters
        current_opt_params = self.calculate_optimal_parameters(current_mu)
        
        # Perform transmissibility calculations
        for j, mu in enumerate(mass_values):
            # Calculate optimal parameters for this mass ratio
            opt_params = self.calculate_optimal_parameters(mu)
            beta = opt_params['beta_opt']
            nua = opt_params['ksi_opt']
            
            for i, r in enumerate(r_values):
                results[i, j] = self.calculate_transmissibility(r, beta, mu, nua, nub)
        
        return {
            'r_values': r_values,
            'mass_values': mass_values,
            'results': results,
            'current_mu': current_mu,
            'optimal_beta': current_opt_params['beta_opt'],
            'optimal_ksi': current_opt_params['ksi_opt']
        }
    
    def compare_with_without_tmd(self, mu: float, nub: float = 0.01, num_points: int = 400,
                               r_range: Tuple[float, float] = (0.1, 2.0)) -> Dict:
        """
        Compare system response with and without TMD
        
        Args:
            mu (float): Mass ratio
            nub (float): Main system damping ratio
            num_points (int): Number of points for frequency range
            r_range (tuple): Range of frequency ratio values (min, max)
            
        Returns:
            dict: Comparison results
        """
        r_values = np.linspace(r_range[0], r_range[1], num_points)
        
        # Calculate optimal parameters
        opt_params = self.calculate_optimal_parameters(mu)
        beta = opt_params['beta_opt']
        nua = opt_params['ksi_opt']
        
        # With TMD (optimal parameters)
        with_tmd = np.zeros(len(r_values))
        for i, r in enumerate(r_values):
            with_tmd[i] = self.calculate_transmissibility(r, beta, mu, nua, nub)
        
        # Without TMD (mu = 0, equivalent to no TMD)
        without_tmd = np.zeros(len(r_values))
        for i, r in enumerate(r_values):
            if np.isclose(r, 1.0, atol=0.01) and nub == 0:
                # At resonance with no damping, transmissibility is theoretically infinite
                without_tmd[i] = float('inf')
            else:
                # For a single DOF system: T = 1/sqrt((1-r^2)^2 + (2*zeta*r)^2)
                denominator = (1 - r**2)**2 + (2 * nub * r)**2
                without_tmd[i] = 1 / np.sqrt(denominator) if denominator > 0 else float('inf')
        
        return {
            'r_values': r_values,
            'with_tmd': with_tmd,
            'without_tmd': without_tmd,
            'mu': mu,
            'beta': beta,
            'ksi': nua,
            'nub': nub
        }
    
    def calculate_tmd_effectiveness(self, mu: float, nub: float = 0.01, num_points: int = 400) -> Dict:
        """
        Calculate effectiveness metrics for TMD
        
        Args:
            mu (float): Mass ratio
            nub (float): Main system damping ratio
            num_points (int): Number of points for effectiveness curve
            
        Returns:
            dict: Effectiveness metrics
        """
        # Generate mass ratio range
        mu_values = np.linspace(0.01, 0.5, num_points)
        
        # Calculate maximum transmissibility for each mass ratio
        max_transmissibility = np.zeros(len(mu_values))
        optimal_beta = np.zeros(len(mu_values))
        optimal_ksi = np.zeros(len(mu_values))
        
        for i, mu_val in enumerate(mu_values):
            opt_params = self.calculate_optimal_parameters(mu_val)
            optimal_beta[i] = opt_params['beta_opt']
            optimal_ksi[i] = opt_params['ksi_opt']
            
            # Calculate transmissibility around resonance to find maximum
            r_values = np.linspace(0.7, 1.3, 100)
            transmissibility = np.zeros(len(r_values))
            
            for j, r in enumerate(r_values):
                transmissibility[j] = self.calculate_transmissibility(
                    r, optimal_beta[i], mu_val, optimal_ksi[i], nub)
            
            # Get maximum transmissibility
            max_transmissibility[i] = np.max(transmissibility)
        
        # Calculate without TMD (single peak)
        without_tmd = float('inf') if nub == 0 else 1 / (2 * nub)
        
        # Calculate effectiveness (reduction in max transmissibility)
        effectiveness = 1 - (max_transmissibility / without_tmd)
        
        return {
            'mu_values': mu_values,
            'max_transmissibility': max_transmissibility,
            'optimal_beta': optimal_beta,
            'optimal_ksi': optimal_ksi,
            'without_tmd': without_tmd,
            'effectiveness': effectiveness
        }