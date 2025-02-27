# core/optimizers.py
import numpy as np
import random
from typing import Callable, List, Tuple, Dict, Any

class BeesAlgorithm:
    """
    Bees Algorithm implementation for TMD parameter optimization
    Based on the paper by Pham et al. (2006) and as used in the cutting tool holder study
    """
    
    def __init__(self, n: int = 20, m: int = 10, e: int = 5, nep: int = 10, 
                 nsp: int = 7, ngh: float = 0.01, max_iterations: int = 100):
        """
        Initialize the Bees Algorithm
        
        Args:
            n (int): Number of scout bees
            m (int): Number of selected sites
            e (int): Number of elite sites
            nep (int): Number of bees recruited for elite sites
            nsp (int): Number of bees recruited for other selected sites
            ngh (float): Initial patch size
            max_iterations (int): Maximum number of iterations
        """
        self.n = n                      # Number of scout bees
        self.m = m                      # Number of selected sites
        self.e = e                      # Number of elite sites
        self.nep = nep                  # Number of bees recruited for elite sites
        self.nsp = nsp                  # Number of bees recruited for other selected sites
        self.ngh = ngh                  # Initial patch size
        self.max_iterations = max_iterations
        
    def optimize(self, objective_function: Callable, bounds: List[Tuple[float, float]], 
                 maximize: bool = False, verbose: bool = False) -> Tuple[List[float], float, Dict]:
        """
        Optimize parameters for the given objective function
        
        Args:
            objective_function: Function to minimize/maximize
            bounds: List of (min, max) tuples for each parameter
            maximize: If True, maximize the objective function; otherwise minimize
            verbose: If True, print progress information
            
        Returns:
            Tuple containing:
            - Best parameters found
            - Best objective value
            - Dictionary with optimization statistics
        """
        sign = 1 if maximize else -1
        dimensions = len(bounds)
        
        # Initialize the scout bees randomly
        scouts = []
        for _ in range(self.n):
            solution = [random.uniform(bounds[j][0], bounds[j][1]) for j in range(dimensions)]
            fitness = sign * objective_function(solution)
            scouts.append({"params": solution, "fitness": fitness})
        
        # Sort scouts by fitness
        scouts.sort(key=lambda x: x["fitness"], reverse=True)
        
        best_solution = scouts[0]["params"].copy()
        best_fitness = scouts[0]["fitness"]
        
        # Statistics dictionary
        stats = {
            "best_fitness_history": [best_fitness/sign],
            "mean_fitness_history": [sum(s["fitness"]/sign for s in scouts) / len(scouts)],
            "best_solutions_history": [best_solution.copy()]
        }
        
        # Main optimization loop
        for iteration in range(self.max_iterations):
            if verbose and iteration % 10 == 0:
                print(f"Iteration {iteration}/{self.max_iterations}, Best fitness: {best_fitness/sign}")
            
            # Shrink patch size over time (optional)
            current_patch_size = self.ngh * (1 - 0.8 * iteration / self.max_iterations)
            
            # Select sites for neighborhood search
            selected_sites = scouts[:self.m]
            elite_sites = selected_sites[:self.e]
            other_sites = selected_sites[self.e:self.m]
            
            # Perform neighborhood search for elite sites
            for i, site in enumerate(elite_sites):
                neighborhood_bees = []
                neighborhood_bees.append(site.copy())  # Keep the original site
                
                # Recruit bees around the elite site
                for _ in range(self.nep - 1):  # -1 because we already added the original site
                    new_params = []
                    for j in range(dimensions):
                        # Create a neighbor within the patch size
                        delta = random.uniform(-current_patch_size, current_patch_size) * (bounds[j][1] - bounds[j][0])
                        new_param = site["params"][j] + delta
                        new_param = max(bounds[j][0], min(bounds[j][1], new_param))  # Ensure within bounds
                        new_params.append(new_param)
                    
                    new_fitness = sign * objective_function(new_params)
                    neighborhood_bees.append({"params": new_params, "fitness": new_fitness})
                
                # Find the best bee in this neighborhood
                neighborhood_bees.sort(key=lambda x: x["fitness"], reverse=True)
                elite_sites[i] = neighborhood_bees[0].copy()
            
            # Perform neighborhood search for other selected sites
            for i, site in enumerate(other_sites):
                neighborhood_bees = []
                neighborhood_bees.append(site.copy())  # Keep the original site
                
                # Recruit bees around the other selected site
                for _ in range(self.nsp - 1):  # -1 because we already added the original site
                    new_params = []
                    for j in range(dimensions):
                        # Create a neighbor within the patch size
                        delta = random.uniform(-current_patch_size, current_patch_size) * (bounds[j][1] - bounds[j][0])
                        new_param = site["params"][j] + delta
                        new_param = max(bounds[j][0], min(bounds[j][1], new_param))  # Ensure within bounds
                        new_params.append(new_param)
                    
                    new_fitness = sign * objective_function(new_params)
                    neighborhood_bees.append({"params": new_params, "fitness": new_fitness})
                
                # Find the best bee in this neighborhood
                neighborhood_bees.sort(key=lambda x: x["fitness"], reverse=True)
                other_sites[i] = neighborhood_bees[0].copy()
            
            # Random search for the remaining scout bees
            remaining_scouts = []
            for _ in range(self.n - self.m):
                solution = [random.uniform(bounds[j][0], bounds[j][1]) for j in range(dimensions)]
                fitness = sign * objective_function(solution)
                remaining_scouts.append({"params": solution, "fitness": fitness})
            
            # Combine all bees for the next iteration
            scouts = elite_sites + other_sites + remaining_scouts
            scouts.sort(key=lambda x: x["fitness"], reverse=True)
            
            # Update best solution if necessary
            if scouts[0]["fitness"] > best_fitness:
                best_solution = scouts[0]["params"].copy()
                best_fitness = scouts[0]["fitness"]
            
            # Update statistics
            stats["best_fitness_history"].append(best_fitness/sign)
            stats["mean_fitness_history"].append(sum(s["fitness"]/sign for s in scouts) / len(scouts))
            stats["best_solutions_history"].append(best_solution.copy())
        
        return best_solution, best_fitness/sign, stats


class TMDOptimizer:
    """TMD parameter optimizer using various optimization algorithms"""
    
    def __init__(self, tmd_analyzer):
        """
        Initialize the TMD optimizer
        
        Args:
            tmd_analyzer: An instance of TMDAnalyzer to evaluate the TMD performance
        """
        self.analyzer = tmd_analyzer
        
    def objective_function_transmissibility(self, params):
        """
        Objective function for TMD optimization to minimize maximum transmissibility
        
        Args:
            params: List of [mass_ratio, damping_ratio, frequency_ratio]
            
        Returns:
            Maximum transmissibility value (lower is better)
        """
        mu, ksi_a, beta = params
        nub = 0.05  # Main system damping ratio (can be parameterized)
        
        # Generate frequency range
        r_values = np.linspace(0.5, 1.5, 100)  # Focus on resonance region
        
        max_transmissibility = 0
        for r in r_values:
            transmissibility = self.analyzer.calculate_transmissibility(r, beta, mu, ksi_a, nub)
            if transmissibility > max_transmissibility:
                max_transmissibility = transmissibility
        
        return max_transmissibility
    
    def optimize_tmd_parameters(self, main_mass, main_frequency, 
                                mass_ratio_bounds=(0.05, 0.5),
                                damping_ratio_bounds=(0.01, 0.5),
                                frequency_ratio_bounds=(0.5, 1.0),
                                algorithm="bees",
                                **algorithm_params):
        """
        Optimize TMD parameters for minimal transmissibility
        
        Args:
            main_mass: Mass of the main system (kg)
            main_frequency: Natural frequency of the main system (rad/s)
            mass_ratio_bounds: (min, max) bounds for mass ratio
            damping_ratio_bounds: (min, max) bounds for damping ratio
            frequency_ratio_bounds: (min, max) bounds for frequency ratio
            algorithm: Optimization algorithm to use ("bees", "genetic", etc.)
            **algorithm_params: Additional parameters for the optimization algorithm
            
        Returns:
            Dictionary containing optimized parameters
        """
        bounds = [
            mass_ratio_bounds,
            damping_ratio_bounds, 
            frequency_ratio_bounds
        ]
        
        if algorithm == "bees":
            # Extract Bees Algorithm parameters or use defaults
            n = algorithm_params.get("n", 20)
            m = algorithm_params.get("m", 10)
            e = algorithm_params.get("e", 5) 
            nep = algorithm_params.get("nep", 10)
            nsp = algorithm_params.get("nsp", 7)
            ngh = algorithm_params.get("ngh", 0.05)
            max_iterations = algorithm_params.get("max_iterations", 100)
            
            optimizer = BeesAlgorithm(n, m, e, nep, nsp, ngh, max_iterations)
            
        elif algorithm == "genetic":
            # Future implementation for genetic algorithm
            raise NotImplementedError("Genetic algorithm not implemented yet")
        else:
            raise ValueError(f"Unknown optimization algorithm: {algorithm}")
        
        # Run optimization
        best_params, best_value, stats = optimizer.optimize(
            self.objective_function_transmissibility, 
            bounds,
            maximize=False,
            verbose=algorithm_params.get("verbose", False)
        )
        
        # Extract optimized parameters
        mu_opt, ksi_opt, beta_opt = best_params
        
        # Calculate actual TMD parameters
        m2_opt = mu_opt * main_mass
        w2_opt = beta_opt * main_frequency
        k2_opt = w2_opt**2 * m2_opt
        c2_opt = 2 * ksi_opt * m2_opt * w2_opt
        
        return {
            "mu": mu_opt,
            "ksi_2_opt": ksi_opt,
            "beta": beta_opt,
            "m2": m2_opt,
            "w2_opt": w2_opt,
            "k2_opt": k2_opt,
            "c2_opt": c2_opt,
            "max_transmissibility": best_value,
            "optimization_stats": stats
        }