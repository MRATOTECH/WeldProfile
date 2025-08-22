"""
Material properties database for welding simulation.
Based on the properties table from the uploaded image and standard material databases.
"""

class MaterialProperties:
    """
    Material properties database for different materials used in welding.
    """
    
    @staticmethod
    def get_properties(material_type):
        """
        Get material properties for the specified material type.
        
        Parameters:
        - material_type: String identifying the material
        
        Returns:
        - Dictionary containing material properties
        """
        
        properties_db = {
            "Steel": {
                'thermal_conductivity': 50.0,  # W/m·K (k)
                'density': 7800.0,  # kg/m³ (ρ)
                'specific_heat_solid': 726000.0,  # J/kg·K (Cs) - 7.26×10⁵ erg/g·K converted
                'specific_heat_liquid': 732000.0,  # J/kg·K (Cl) - 7.32×10⁵ erg/g·K converted
                'solidus_temp': 1768.0,  # K (Ts)
                'liquidus_temp': 1798.0,  # K (Tl)
                'latent_heat': 2.77e5,  # J/kg (hsl) - 2.77×10⁹ erg/g converted
                'permeability': 1.26e-6,  # H/m (μm) - 1.26×10⁻⁶ H/m
                'surface_tension': 1.8,  # N/m (typical value for steel)
                'arc_efficiency_gtaw': 0.7,  # ηArc_GTAW
                'arc_efficiency_gmaw': 0.56,  # ηArc_GMAW
                'droplet_efficiency_gmaw': 0.24  # ηd
            },
            
            "Aluminum": {
                'thermal_conductivity': 237.0,  # W/m·K
                'density': 2700.0,  # kg/m³
                'specific_heat_solid': 903000.0,  # J/kg·K
                'specific_heat_liquid': 1080000.0,  # J/kg·K
                'solidus_temp': 933.0,  # K (660°C)
                'liquidus_temp': 943.0,  # K (670°C)
                'latent_heat': 3.97e5,  # J/kg
                'permeability': 1.26e-6,  # H/m (non-magnetic)
                'surface_tension': 0.9,  # N/m
                'arc_efficiency_gtaw': 0.65,
                'arc_efficiency_gmaw': 0.50,
                'droplet_efficiency_gmaw': 0.20
            },
            
            "Stainless Steel": {
                'thermal_conductivity': 16.0,  # W/m·K (lower than carbon steel)
                'density': 8000.0,  # kg/m³
                'specific_heat_solid': 500000.0,  # J/kg·K
                'specific_heat_liquid': 520000.0,  # J/kg·K
                'solidus_temp': 1673.0,  # K (1400°C)
                'liquidus_temp': 1723.0,  # K (1450°C)
                'latent_heat': 2.60e5,  # J/kg
                'permeability': 1.26e-6,  # H/m (austenitic - non-magnetic)
                'surface_tension': 1.6,  # N/m
                'arc_efficiency_gtaw': 0.68,
                'arc_efficiency_gmaw': 0.54,
                'droplet_efficiency_gmaw': 0.22
            },
            
            "Titanium": {
                'thermal_conductivity': 22.0,  # W/m·K
                'density': 4500.0,  # kg/m³
                'specific_heat_solid': 520000.0,  # J/kg·K
                'specific_heat_liquid': 610000.0,  # J/kg·K
                'solidus_temp': 1933.0,  # K (1660°C)
                'liquidus_temp': 1943.0,  # K (1670°C)
                'latent_heat': 4.20e5,  # J/kg
                'permeability': 1.26e-6,  # H/m (non-magnetic)
                'surface_tension': 1.5,  # N/m
                'arc_efficiency_gtaw': 0.72,
                'arc_efficiency_gmaw': 0.58,
                'droplet_efficiency_gmaw': 0.26
            }
        }
        
        if material_type not in properties_db:
            # Default to Steel if material not found
            material_type = "Steel"
        
        return properties_db[material_type]
    
    @staticmethod
    def get_available_materials():
        """
        Get list of available materials in the database.
        
        Returns:
        - List of material names
        """
        return ["Steel", "Aluminum", "Stainless Steel", "Titanium"]
    
    @staticmethod
    def get_thermal_diffusivity(material_type):
        """
        Calculate thermal diffusivity for the given material.
        
        Parameters:
        - material_type: String identifying the material
        
        Returns:
        - Thermal diffusivity (m²/s)
        """
        props = MaterialProperties.get_properties(material_type)
        
        # α = k / (ρ * cp)
        alpha = props['thermal_conductivity'] / (
            props['density'] * props['specific_heat_solid']
        )
        
        return alpha
    
    @staticmethod
    def get_thermal_conductivity_temperature_dependent(material_type, temperature):
        """
        Get temperature-dependent thermal conductivity.
        Simplified linear approximation.
        
        Parameters:
        - material_type: String identifying the material
        - temperature: Temperature in K
        
        Returns:
        - Temperature-dependent thermal conductivity (W/m·K)
        """
        props = MaterialProperties.get_properties(material_type)
        k_room = props['thermal_conductivity']
        
        # Simple linear approximation for temperature dependence
        # Most metals see decreased thermal conductivity with temperature
        if material_type in ["Steel", "Stainless Steel"]:
            # Decrease by ~30% at melting point
            k_factor = 1.0 - 0.3 * (temperature - 298) / (props['liquidus_temp'] - 298)
        elif material_type == "Aluminum":
            # Aluminum conductivity decreases less dramatically
            k_factor = 1.0 - 0.2 * (temperature - 298) / (props['liquidus_temp'] - 298)
        else:  # Titanium
            # Titanium has more stable thermal conductivity
            k_factor = 1.0 - 0.15 * (temperature - 298) / (props['liquidus_temp'] - 298)
        
        # Ensure positive value and reasonable bounds
        k_factor = max(0.3, min(1.0, k_factor))
        
        return k_room * k_factor
    
    @staticmethod
    def get_material_comparison_table():
        """
        Get a comparison table of key properties for all materials.
        
        Returns:
        - Pandas DataFrame with material properties comparison
        """
        import pandas as pd
        
        materials = MaterialProperties.get_available_materials()
        comparison_data = []
        
        for material in materials:
            props = MaterialProperties.get_properties(material)
            alpha = MaterialProperties.get_thermal_diffusivity(material)
            
            comparison_data.append({
                'Material': material,
                'Thermal Conductivity (W/m·K)': props['thermal_conductivity'],
                'Density (kg/m³)': props['density'],
                'Melting Point (°C)': props['liquidus_temp'] - 273.15,
                'Thermal Diffusivity (mm²/s)': alpha * 1e6,  # Convert to mm²/s
                'GTAW Efficiency': props['arc_efficiency_gtaw'],
                'GMAW Efficiency': props['arc_efficiency_gmaw']
            })
        
        return pd.DataFrame(comparison_data)
