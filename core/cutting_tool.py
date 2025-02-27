# core/cutting_tool.py
import numpy as np

class CuttingToolModel:
    """
    Model for a cutting tool holder as described in the paper:
    "OPTIMIZATION OF THE TUNED MASS DAMPER FOR VIBRATION SUPPRESSION OF A CUTTING TOOL HOLDER USING THE BEES ALGORITHM"
    """
    
    def __init__(self, length=808, diameter=20, material='steel', mass=3.94):
        """
        Initialize the cutting tool model
        
        Args:
            length (float): Tool length in mm
            diameter (float): Tool diameter in mm
            material (str): Tool material ('steel', 'aluminum', 'carbide', etc.)
            mass (float): Tool mass in kg (if provided, overrides calculated mass)
        """
        self.length = length / 1000  # Convert to meters
        self.diameter = diameter / 1000  # Convert to meters
        self.material = material
        self.custom_mass = mass
        
        # Material properties dictionary
        self.materials = {
            'steel': {
                'density': 7850,  # kg/m^3
                'youngs_modulus': 210e9,  # Pa
                'poissons_ratio': 0.3
            },
            'aluminum': {
                'density': 2700,  # kg/m^3
                'youngs_modulus': 69e9,  # Pa
                'poissons_ratio': 0.33
            },
            'carbide': {
                'density': 15000,  # kg/m^3
                'youngs_modulus': 550e9,  # Pa
                'poissons_ratio': 0.24
            }
        }
        
        if material not in self.materials:
            raise ValueError(f"Material '{material}' not recognized. Available materials: {list(self.materials.keys())}")
        
        # Calculate properties
        self._calculate_properties()
    
    def _calculate_properties(self):
        """Calculate the physical properties of the cutting tool holder"""
        self.material_props = self.materials[self.material]
        
        # Cross-sectional area
        self.area = np.pi * (self.diameter/2)**2  # m^2
        
        # Second moment of area (for circular cross-section)
        self.moment_of_inertia = np.pi * (self.diameter/2)**4 / 4  # m^4
        
        # If custom mass is provided, use it, otherwise calculate from density
        if self.custom_mass is not None:
            self.mass = self.custom_mass
        else:
            self.mass = self.material_props['density'] * self.area * self.length  # kg
        
        # Distributed mass per unit length
        self.mass_per_length = self.mass / self.length  # kg/m
    
    def calculate_natural_frequencies(self, modes=5):
        """
        Calculate the natural frequencies of the cutting tool holder modeled as a cantilever beam
        
        Args:
            modes (int): Number of modes to calculate
            
        Returns:
            list: Natural frequencies in Hz for each mode
        """
        # Constants for the first five modes from the paper
        k_values = [3.52, 22.0, 61.7, 121, 200]
        
        # Calculate natural frequencies using the formula from the paper
        frequencies = []
        for i in range(min(modes, len(k_values))):
            # Formula: fn = (Kn/2π)·√(EIg/wL^4)
            # where:
            # Kn is the constant for mode n
            # E is Young's modulus
            # I is the second moment of area
            # g is acceleration due to gravity (9.81 m/s^2)
            # w is weight per unit length
            # L is the length of the beam
            
            E = self.material_props['youngs_modulus']
            I = self.moment_of_inertia
            g = 9.81  # m/s^2
            w = self.mass_per_length
            L = self.length
            
            fn = (k_values[i] / (2 * np.pi)) * np.sqrt((E * I * g) / (w * L**4))
            frequencies.append(fn)
        
        return frequencies
    
    def calculate_stiffness(self):
        """
        Calculate the equivalent stiffness of the cutting tool holder
        
        Returns:
            float: Equivalent stiffness in N/m
        """
        # For a cantilever beam, the stiffness at the free end is:
        # k = 3EI/L^3
        E = self.material_props['youngs_modulus']
        I = self.moment_of_inertia
        L = self.length
        
        stiffness = 3 * E * I / (L**3)
        return stiffness
    
    def calculate_damping_coefficient(self, damping_ratio=0.05):
        """
        Calculate the damping coefficient based on a given damping ratio
        
        Args:
            damping_ratio (float): Damping ratio (typically 0.01-0.1 for metal structures)
            
        Returns:
            float: Damping coefficient in N·s/m
        """
        # First calculate the natural frequency of the first mode
        natural_frequencies = self.calculate_natural_frequencies(modes=1)
        omega_n = 2 * np.pi * natural_frequencies[0]  # rad/s
        
        # Calculate critical damping coefficient
        critical_damping = 2 * self.mass * omega_n
        
        # Calculate actual damping coefficient
        damping_coefficient = damping_ratio * critical_damping
        
        return damping_coefficient
    
    def to_single_dof_model(self, damping_ratio=0.05):
        """
        Convert the cutting tool holder to a single degree of freedom model
        
        Args:
            damping_ratio (float): Damping ratio for the main system
            
        Returns:
            dict: Dictionary with parameters for a single DOF model
        """
        natural_frequencies = self.calculate_natural_frequencies(modes=1)
        omega_n = 2 * np.pi * natural_frequencies[0]  # rad/s
        
        stiffness = self.calculate_stiffness()
        damping = self.calculate_damping_coefficient(damping_ratio)
        
        return {
            'm1': self.mass,
            'k1': stiffness,
            'c1': damping,
            'w1': omega_n
        }