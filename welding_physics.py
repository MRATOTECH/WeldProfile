import numpy as np
import scipy.special as special
from scipy.optimize import fsolve
import math

class WeldingSimulator:
    """
    Physics-based welding simulation class for calculating weld pool characteristics
    and temperature distributions based on heat transfer equations.
    """
    
    def __init__(self):
        self.pi = np.pi
        self.stefan_boltzmann = 5.67e-8  # Stefan-Boltzmann constant
        
    def calculate_heat_input(self, current, voltage, travel_speed, arc_efficiency):
        """
        Calculate heat input to the workpiece.
        
        Parameters:
        - current: Welding current (A)
        - voltage: Arc voltage (V)
        - travel_speed: Travel speed (mm/s)
        - arc_efficiency: Arc efficiency (dimensionless)
        
        Returns:
        - heat_input: Heat input (J/mm)
        """
        # Convert travel speed from mm/s to mm/min for standard units
        travel_speed_mm_min = travel_speed * 60
        
        # Calculate net heat input
        heat_input = (arc_efficiency * voltage * current * 60) / travel_speed_mm_min
        
        return heat_input
    
    def calculate_weld_pool_geometry(self, heat_input, material_props, plate_thickness):
        """
        Calculate weld pool dimensions using Rosenthal's equations and empirical correlations.
        
        Parameters:
        - heat_input: Heat input (J/mm)
        - material_props: Dictionary of material properties
        - plate_thickness: Plate thickness (mm)
        
        Returns:
        - Dictionary containing weld pool dimensions
        """
        # Material properties
        k = material_props['thermal_conductivity']  # W/m·K
        rho = material_props['density']  # kg/m³
        cp = material_props['specific_heat_solid']  # J/kg·K
        T_m = material_props['liquidus_temp']  # K
        T_0 = 298  # Room temperature (K)
        
        # Thermal diffusivity
        alpha = k / (rho * cp)  # m²/s
        
        # Convert heat input to SI units (W·m)
        q = heat_input * 1000  # J/mm to J/m
        
        # Characteristic thermal length
        delta_T = T_m - T_0
        l_c = q / (2 * self.pi * k * delta_T)  # Characteristic length (m)
        
        # Weld pool width (empirical correlation)
        # Based on the assumption that pool width scales with thermal diffusion
        width = 2.5 * l_c * 1000  # Convert to mm
        
        # Weld pool length (typically 2-4 times the width for moving heat sources)
        length = 3.2 * width
        
        # Penetration depth calculation using modified Rosenthal equation
        # For thick plate (3D heat conduction)
        if plate_thickness > 3 * width:
            penetration = 0.8 * l_c * 1000  # Convert to mm
        else:
            # For thin plate (2D heat conduction)
            penetration = min(0.6 * l_c * 1000, plate_thickness * 0.9)
        
        # Ensure physical constraints
        penetration = min(penetration, plate_thickness)
        width = min(width, plate_thickness * 2)
        
        # Calculate additional parameters
        aspect_ratio = length / width
        dilution_ratio = penetration / (penetration + 3.0)  # Assuming 3mm cap height
        
        # Pool volume (approximating as ellipsoid)
        volume = (self.pi / 6) * width * length * penetration
        
        return {
            'width': width,
            'length': length,
            'penetration': penetration,
            'aspect_ratio': aspect_ratio,
            'dilution_ratio': dilution_ratio,
            'volume': volume,
            'heat_input': heat_input,
            'characteristic_length': l_c * 1000
        }
    
    def calculate_temperature_distribution(self, heat_input, material_props, travel_speed):
        """
        Calculate temperature distribution using moving heat source theory.
        
        Parameters:
        - heat_input: Heat input (J/mm)
        - material_props: Dictionary of material properties
        - travel_speed: Travel speed (mm/s)
        
        Returns:
        - Dictionary containing temperature field data
        """
        # Material properties
        k = material_props['thermal_conductivity']  # W/m·K
        rho = material_props['density']  # kg/m³
        cp = material_props['specific_heat_solid']  # J/kg·K
        T_0 = 298  # Room temperature (K)
        
        # Thermal diffusivity
        alpha = k / (rho * cp)  # m²/s
        
        # Convert parameters to SI units
        q = heat_input * 1000  # J/mm to J/m
        v = travel_speed / 1000  # mm/s to m/s
        
        # Create coordinate grid (in mm, then convert to m for calculations)
        x_mm = np.linspace(-20, 40, 61)  # -20mm to +40mm
        y_mm = np.linspace(-15, 15, 31)  # -15mm to +15mm
        X_mm, Y_mm = np.meshgrid(x_mm, y_mm)
        
        # Convert to meters for calculation
        X = X_mm / 1000
        Y = Y_mm / 1000
        
        # Calculate temperature field using Rosenthal's moving point source solution
        # For 3D case (thick plate)
        T = np.zeros_like(X)
        
        for i in range(X.shape[0]):
            for j in range(X.shape[1]):
                x, y = X[i, j], Y[i, j]
                r = np.sqrt(x**2 + y**2)
                
                if r > 0:
                    # Moving point source solution
                    R = np.sqrt(x**2 + y**2)
                    exponential_term = np.exp(-v * (R - x) / (2 * alpha))
                    T[i, j] = T_0 + (q / (2 * self.pi * k * R)) * exponential_term
                else:
                    # At the source point, use a high temperature
                    T[i, j] = T_0 + q / (4 * self.pi * k * 0.001)  # 1mm effective radius
        
        # Limit maximum temperature to avoid unrealistic values
        T = np.minimum(T, 3500)  # Maximum ~3500K
        
        return {
            'x': x_mm,
            'y': y_mm,
            'X': X_mm,
            'Y': Y_mm,
            'temperature': T,
            'max_temp': np.max(T),
            'min_temp': np.min(T)
        }
    
    def sensitivity_analysis(self, base_current, base_voltage, base_speed, 
                           arc_efficiency, material_props, plate_thickness):
        """
        Perform sensitivity analysis for key parameters.
        
        Returns:
        - Dictionary containing sensitivity coefficients
        """
        # Base case calculation
        base_heat_input = self.calculate_heat_input(
            base_current, base_voltage, base_speed, arc_efficiency
        )
        base_pool = self.calculate_weld_pool_geometry(
            base_heat_input, material_props, plate_thickness
        )
        
        # Parameter variations (±10%)
        variation = 0.1
        sensitivity_results = []
        
        parameters = [
            ('current', base_current),
            ('voltage', base_voltage),
            ('travel_speed', base_speed),
            ('arc_efficiency', arc_efficiency)
        ]
        
        for param_name, base_value in parameters:
            # Calculate with increased parameter
            if param_name == 'current':
                heat_input_high = self.calculate_heat_input(
                    base_value * (1 + variation), base_voltage, base_speed, arc_efficiency
                )
                heat_input_low = self.calculate_heat_input(
                    base_value * (1 - variation), base_voltage, base_speed, arc_efficiency
                )
            elif param_name == 'voltage':
                heat_input_high = self.calculate_heat_input(
                    base_current, base_value * (1 + variation), base_speed, arc_efficiency
                )
                heat_input_low = self.calculate_heat_input(
                    base_current, base_value * (1 - variation), base_speed, arc_efficiency
                )
            elif param_name == 'travel_speed':
                heat_input_high = self.calculate_heat_input(
                    base_current, base_voltage, base_value * (1 + variation), arc_efficiency
                )
                heat_input_low = self.calculate_heat_input(
                    base_current, base_voltage, base_value * (1 - variation), arc_efficiency
                )
            else:  # arc_efficiency
                heat_input_high = self.calculate_heat_input(
                    base_current, base_voltage, base_speed, base_value * (1 + variation)
                )
                heat_input_low = self.calculate_heat_input(
                    base_current, base_voltage, base_speed, base_value * (1 - variation)
                )
            
            # Calculate pool geometries
            pool_high = self.calculate_weld_pool_geometry(
                heat_input_high, material_props, plate_thickness
            )
            pool_low = self.calculate_weld_pool_geometry(
                heat_input_low, material_props, plate_thickness
            )
            
            # Calculate sensitivities for width and penetration
            width_sensitivity = (
                (pool_high['width'] - pool_low['width']) / 
                (2 * variation * base_value)
            ) * (base_value / base_pool['width'])
            
            penetration_sensitivity = (
                (pool_high['penetration'] - pool_low['penetration']) / 
                (2 * variation * base_value)
            ) * (base_value / base_pool['penetration'])
            
            sensitivity_results.append({
                'parameter': param_name,
                'width_sensitivity': width_sensitivity,
                'penetration_sensitivity': penetration_sensitivity,
                'base_value': base_value
            })
        
        return sensitivity_results
