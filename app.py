import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import matplotlib.pyplot as plt
import seaborn as sns
from welding_physics import WeldingSimulator
from visualization import WeldingVisualizer
from material_properties import MaterialProperties

# Configure page
st.set_page_config(
    page_title="Welding Simulation Analysis",
    page_icon="🔥",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("🔥 Scientific Welding Simulation Application")
st.markdown("**Analyze weld pool characteristics and parameter effects**")

# Initialize session state
if 'simulator' not in st.session_state:
    st.session_state.simulator = WeldingSimulator()
if 'visualizer' not in st.session_state:
    st.session_state.visualizer = WeldingVisualizer()

# Sidebar for parameter controls
st.sidebar.header("Welding Parameters")

# Welding process parameters
st.sidebar.subheader("Arc Parameters")
welding_current = st.sidebar.slider(
    "Welding Current (A)", 
    min_value=50, max_value=400, value=200, step=10,
    help="Current density affects heat input and penetration"
)

welding_voltage = st.sidebar.slider(
    "Welding Voltage (V)", 
    min_value=10, max_value=40, value=25, step=1,
    help="Voltage affects arc length and heat distribution"
)

travel_speed = st.sidebar.slider(
    "Travel Speed (mm/s)", 
    min_value=1.0, max_value=20.0, value=5.0, step=0.5,
    help="Travel speed affects heat input per unit length"
)

# Arc efficiency parameters
st.sidebar.subheader("Arc Efficiency")
arc_efficiency_gtaw = st.sidebar.slider(
    "GTAW Arc Efficiency", 
    min_value=0.5, max_value=0.9, value=0.7, step=0.05
)

arc_efficiency_gmaw = st.sidebar.slider(
    "GMAW Arc Efficiency", 
    min_value=0.4, max_value=0.8, value=0.56, step=0.05
)

# Geometry parameters
st.sidebar.subheader("Joint Geometry")
plate_thickness = st.sidebar.slider(
    "Plate Thickness (mm)", 
    min_value=3.0, max_value=25.0, value=10.0, step=1.0
)

joint_type = st.sidebar.selectbox(
    "Joint Type",
    ["Butt Joint", "Fillet Joint", "Lap Joint", "T-Joint"]
)

# Material selection
st.sidebar.subheader("Material Properties")
material_type = st.sidebar.selectbox(
    "Material Type",
    ["Steel", "Aluminum", "Stainless Steel", "Titanium"]
)

# Get material properties
material_props = MaterialProperties.get_properties(material_type)

# Main content area
col1, col2 = st.columns([2, 1])

with col1:
    # Tab structure for different analyses
    tab1, tab2, tab3, tab4 = st.tabs([
        "Weld Pool Analysis", 
        "Temperature Distribution", 
        "Parameter Effects", 
        "Sensitivity Analysis"
    ])
    
    with tab1:
        st.subheader("Weld Pool Shape and Size")
        
        # Calculate weld pool characteristics
        heat_input = st.session_state.simulator.calculate_heat_input(
            welding_current, welding_voltage, travel_speed, arc_efficiency_gtaw
        )
        
        weld_pool_data = st.session_state.simulator.calculate_weld_pool_geometry(
            heat_input, material_props, plate_thickness
        )
        
        # Display weld pool metrics
        metrics_col1, metrics_col2, metrics_col3 = st.columns(3)
        with metrics_col1:
            st.metric("Heat Input", f"{heat_input:.1f} J/mm", 
                     help="Total heat energy per unit length")
        with metrics_col2:
            st.metric("Pool Width", f"{weld_pool_data['width']:.2f} mm")
        with metrics_col3:
            st.metric("Penetration", f"{weld_pool_data['penetration']:.2f} mm")
        
        # Weld pool cross-section visualization
        fig_pool = st.session_state.visualizer.plot_weld_pool_cross_section(weld_pool_data)
        st.plotly_chart(fig_pool, use_container_width=True)
        
        # 3D weld pool visualization
        fig_3d = st.session_state.visualizer.plot_3d_weld_pool(weld_pool_data)
        st.plotly_chart(fig_3d, use_container_width=True)
    
    with tab2:
        st.subheader("Temperature Distribution Analysis")
        
        # Calculate temperature field
        temp_field = st.session_state.simulator.calculate_temperature_distribution(
            heat_input, material_props, travel_speed
        )
        
        # Temperature statistics
        max_temp = np.max(temp_field['temperature'])
        avg_temp = np.mean(temp_field['temperature'])
        
        temp_col1, temp_col2, temp_col3 = st.columns(3)
        with temp_col1:
            st.metric("Max Temperature", f"{max_temp:.0f} K")
        with temp_col2:
            st.metric("Average Temperature", f"{avg_temp:.0f} K")
        with temp_col3:
            st.metric("Solidus Temperature", f"{material_props['solidus_temp']:.0f} K")
        
        # Temperature contour plot
        fig_temp = st.session_state.visualizer.plot_temperature_distribution(temp_field)
        st.plotly_chart(fig_temp, use_container_width=True)
        
        # Temperature profile along centerline
        fig_profile = st.session_state.visualizer.plot_temperature_profile(temp_field)
        st.plotly_chart(fig_profile, use_container_width=True)
    
    with tab3:
        st.subheader("Welding Parameter Effects")
        
        # Parameter sweep analysis
        st.write("**Current Variation Analysis**")
        current_range = np.arange(100, 350, 25)
        current_effects = []
        
        for current in current_range:
            heat_input_var = st.session_state.simulator.calculate_heat_input(
                current, welding_voltage, travel_speed, arc_efficiency_gtaw
            )
            pool_data_var = st.session_state.simulator.calculate_weld_pool_geometry(
                heat_input_var, material_props, plate_thickness
            )
            current_effects.append({
                'current': current,
                'heat_input': heat_input_var,
                'width': pool_data_var['width'],
                'penetration': pool_data_var['penetration']
            })
        
        effects_df = pd.DataFrame(current_effects)
        
        # Plot parameter effects
        fig_effects = st.session_state.visualizer.plot_parameter_effects(effects_df, 'current')
        st.plotly_chart(fig_effects, use_container_width=True)
        
        # Voltage effects
        st.write("**Voltage Variation Analysis**")
        voltage_range = np.arange(15, 35, 2)
        voltage_effects = []
        
        for voltage in voltage_range:
            heat_input_var = st.session_state.simulator.calculate_heat_input(
                welding_current, voltage, travel_speed, arc_efficiency_gtaw
            )
            pool_data_var = st.session_state.simulator.calculate_weld_pool_geometry(
                heat_input_var, material_props, plate_thickness
            )
            voltage_effects.append({
                'voltage': voltage,
                'heat_input': heat_input_var,
                'width': pool_data_var['width'],
                'penetration': pool_data_var['penetration']
            })
        
        voltage_df = pd.DataFrame(voltage_effects)
        fig_voltage = st.session_state.visualizer.plot_parameter_effects(voltage_df, 'voltage')
        st.plotly_chart(fig_voltage, use_container_width=True)
    
    with tab4:
        st.subheader("Parameter Sensitivity Analysis")
        
        # Sensitivity analysis
        sensitivity_data = st.session_state.simulator.sensitivity_analysis(
            welding_current, welding_voltage, travel_speed, 
            arc_efficiency_gtaw, material_props, plate_thickness
        )
        
        # Display sensitivity results
        sensitivity_df = pd.DataFrame(sensitivity_data)
        
        # Sensitivity heatmap
        fig_sensitivity = st.session_state.visualizer.plot_sensitivity_heatmap(sensitivity_data)
        st.plotly_chart(fig_sensitivity, use_container_width=True)
        
        # Tornado diagram
        fig_tornado = st.session_state.visualizer.plot_tornado_diagram(sensitivity_data)
        st.plotly_chart(fig_tornado, use_container_width=True)

with col2:
    st.subheader("Material Properties")
    
    # Display current material properties
    prop_data = {
        "Property": [
            "Thermal Conductivity",
            "Density",
            "Specific Heat (Solid)",
            "Specific Heat (Liquid)",
            "Solidus Temperature",
            "Liquidus Temperature",
            "Latent Heat of Fusion"
        ],
        "Value": [
            f"{material_props['thermal_conductivity']:.1f} W/m·K",
            f"{material_props['density']:.1f} kg/m³",
            f"{material_props['specific_heat_solid']:.0f} J/kg·K",
            f"{material_props['specific_heat_liquid']:.0f} J/kg·K",
            f"{material_props['solidus_temp']:.0f} K",
            f"{material_props['liquidus_temp']:.0f} K",
            f"{material_props['latent_heat']:.0e} J/kg"
        ]
    }
    
    prop_df = pd.DataFrame(prop_data)
    st.dataframe(prop_df, use_container_width=True, hide_index=True)
    
    st.subheader("Current Analysis Results")
    
    # Current simulation summary
    current_heat_input = st.session_state.simulator.calculate_heat_input(
        welding_current, welding_voltage, travel_speed, arc_efficiency_gtaw
    )
    current_pool = st.session_state.simulator.calculate_weld_pool_geometry(
        current_heat_input, material_props, plate_thickness
    )
    
    summary_data = {
        "Parameter": [
            "Heat Input",
            "Pool Width",
            "Pool Length", 
            "Penetration Depth",
            "Aspect Ratio",
            "Dilution Ratio"
        ],
        "Value": [
            f"{current_heat_input:.1f} J/mm",
            f"{current_pool['width']:.2f} mm",
            f"{current_pool['length']:.2f} mm",
            f"{current_pool['penetration']:.2f} mm",
            f"{current_pool['aspect_ratio']:.2f}",
            f"{current_pool['dilution_ratio']:.2f}"
        ]
    }
    
    summary_df = pd.DataFrame(summary_data)
    st.dataframe(summary_df, use_container_width=True, hide_index=True)
    
    # Export data button
    st.subheader("Data Export")
    
    if st.button("Export Analysis Results", type="primary"):
        # Prepare export data
        export_data = {
            'parameters': {
                'current': welding_current,
                'voltage': welding_voltage,
                'travel_speed': travel_speed,
                'material': material_type,
                'thickness': plate_thickness
            },
            'results': current_pool,
            'material_properties': material_props
        }
        
        # Convert to JSON for download
        import json
        json_data = json.dumps(export_data, indent=2)
        
        st.download_button(
            label="Download JSON",
            data=json_data,
            file_name=f"welding_analysis_{material_type.lower()}.json",
            mime="application/json"
        )

# Footer
st.markdown("---")
st.markdown(
    "**Scientific Welding Simulation** - Advanced analysis of weld pool characteristics and parameter effects"
)
