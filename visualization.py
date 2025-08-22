import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import numpy as np
import pandas as pd

class WeldingVisualizer:
    """
    Visualization class for welding simulation results.
    """
    
    def __init__(self):
        self.color_scales = {
            'temperature': 'plasma',
            'pool': 'viridis',
            'sensitivity': 'RdBu'
        }
    
    def plot_weld_pool_cross_section(self, weld_pool_data):
        """
        Create a cross-sectional view of the weld pool.
        """
        width = weld_pool_data['width']
        penetration = weld_pool_data['penetration']
        
        # Create weld pool profile (assuming parabolic shape)
        y = np.linspace(-width/2, width/2, 100)
        
        # Parabolic profile for the weld pool
        x_top = np.zeros_like(y)  # Surface level
        x_bottom = -penetration * (1 - (2*y/width)**2)
        
        # Create the plot
        fig = go.Figure()
        
        # Add weld pool boundary
        fig.add_trace(go.Scatter(
            x=np.concatenate([x_top, x_bottom[::-1]]),
            y=np.concatenate([y, y[::-1]]),
            fill='toself',
            fillcolor='rgba(255, 165, 0, 0.6)',
            line=dict(color='red', width=2),
            name='Weld Pool',
            hovertemplate='Width: %{y:.2f} mm<br>Depth: %{x:.2f} mm<extra></extra>'
        ))
        
        # Add base metal
        base_y = np.linspace(-width*1.5, width*1.5, 50)
        base_x_top = np.zeros_like(base_y)
        base_x_bottom = np.full_like(base_y, -penetration*2)
        
        fig.add_trace(go.Scatter(
            x=np.concatenate([base_x_top, base_x_bottom[::-1]]),
            y=np.concatenate([base_y, base_y[::-1]]),
            fill='toself',
            fillcolor='rgba(128, 128, 128, 0.3)',
            line=dict(color='gray', width=1),
            name='Base Metal',
            showlegend=False
        ))
        
        # Add annotations
        fig.add_annotation(
            x=0, y=width/4,
            text=f"Width: {width:.2f} mm",
            showarrow=True,
            arrowhead=2,
            arrowcolor="blue",
            arrowsize=1,
            arrowwidth=2
        )
        
        fig.add_annotation(
            x=-penetration/2, y=0,
            text=f"Penetration: {penetration:.2f} mm",
            showarrow=True,
            arrowhead=2,
            arrowcolor="green",
            arrowsize=1,
            arrowwidth=2
        )
        
        fig.update_layout(
            title="Weld Pool Cross-Section",
            xaxis_title="Depth (mm)",
            yaxis_title="Width (mm)",
            xaxis=dict(range=[-penetration*1.2, penetration*0.2]),
            yaxis=dict(range=[-width*0.8, width*0.8]),
            showlegend=True,
            height=400
        )
        
        return fig
    
    def plot_3d_weld_pool(self, weld_pool_data):
        """
        Create a 3D visualization of the weld pool.
        """
        width = weld_pool_data['width']
        length = weld_pool_data['length']
        penetration = weld_pool_data['penetration']
        
        # Create 3D mesh for weld pool
        theta = np.linspace(0, 2*np.pi, 50)
        z = np.linspace(0, -penetration, 20)
        
        # Create cylindrical-like coordinates
        r_max = width / 2
        x_mesh = []
        y_mesh = []
        z_mesh = []
        
        for i, z_val in enumerate(z):
            # Radius decreases with depth (tapered pool)
            r_current = r_max * (1 - abs(z_val)/penetration)**0.5
            
            # Elliptical cross-section (longer in travel direction)
            x_circle = r_current * np.cos(theta) * (length/width)
            y_circle = r_current * np.sin(theta)
            z_circle = np.full_like(theta, z_val)
            
            x_mesh.append(x_circle)
            y_mesh.append(y_circle)
            z_mesh.append(z_circle)
        
        x_mesh = np.array(x_mesh)
        y_mesh = np.array(y_mesh)
        z_mesh = np.array(z_mesh)
        
        # Create the 3D surface
        fig = go.Figure()
        
        fig.add_trace(go.Surface(
            x=x_mesh,
            y=y_mesh,
            z=z_mesh,
            colorscale='Hot',
            opacity=0.8,
            name="Weld Pool",
            colorbar=dict(title="Depth (mm)")
        ))
        
        fig.update_layout(
            title="3D Weld Pool Visualization",
            scene=dict(
                xaxis_title="Length Direction (mm)",
                yaxis_title="Width Direction (mm)",
                zaxis_title="Depth (mm)",
                camera=dict(
                    eye=dict(x=1.5, y=1.5, z=1.5)
                )
            ),
            height=500
        )
        
        return fig
    
    def plot_temperature_distribution(self, temp_field):
        """
        Create a temperature contour plot.
        """
        fig = go.Figure()
        
        fig.add_trace(go.Contour(
            x=temp_field['x'],
            y=temp_field['y'],
            z=temp_field['temperature'],
            colorscale='plasma',
            contours=dict(
                start=300,
                end=np.max(temp_field['temperature']),
                size=200
            ),
            colorbar=dict(title="Temperature (K)"),
            hovertemplate='X: %{x:.1f} mm<br>Y: %{y:.1f} mm<br>Temperature: %{z:.0f} K<extra></extra>'
        ))
        
        # Add isotherms for important temperatures
        fig.add_contour(
            x=temp_field['x'],
            y=temp_field['y'],
            z=temp_field['temperature'],
            contours=dict(
                start=1768,  # Solidus temperature
                end=1768,
                size=1,
                coloring='lines'
            ),
            line=dict(color='red', width=3),
            showscale=False,
            name='Solidus Line'
        )
        
        fig.add_contour(
            x=temp_field['x'],
            y=temp_field['y'],
            z=temp_field['temperature'],
            contours=dict(
                start=1798,  # Liquidus temperature
                end=1798,
                size=1,
                coloring='lines'
            ),
            line=dict(color='blue', width=3),
            showscale=False,
            name='Liquidus Line'
        )
        
        fig.update_layout(
            title="Temperature Distribution",
            xaxis_title="Distance along travel direction (mm)",
            yaxis_title="Distance perpendicular to travel (mm)",
            height=400
        )
        
        return fig
    
    def plot_temperature_profile(self, temp_field):
        """
        Plot temperature profile along the centerline.
        """
        # Extract centerline temperature (y=0)
        center_idx = len(temp_field['y']) // 2
        centerline_temp = temp_field['temperature'][center_idx, :]
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=temp_field['x'],
            y=centerline_temp,
            mode='lines',
            line=dict(color='red', width=3),
            name='Centerline Temperature',
            hovertemplate='Distance: %{x:.1f} mm<br>Temperature: %{y:.0f} K<extra></extra>'
        ))
        
        # Add reference temperatures
        fig.add_hline(
            y=1768, line_dash="dash", line_color="blue",
            annotation_text="Solidus Temperature"
        )
        fig.add_hline(
            y=1798, line_dash="dash", line_color="green",
            annotation_text="Liquidus Temperature"
        )
        fig.add_hline(
            y=298, line_dash="dot", line_color="gray",
            annotation_text="Room Temperature"
        )
        
        fig.update_layout(
            title="Temperature Profile Along Weld Centerline",
            xaxis_title="Distance along travel direction (mm)",
            yaxis_title="Temperature (K)",
            height=400
        )
        
        return fig
    
    def plot_parameter_effects(self, effects_df, parameter_name):
        """
        Plot the effects of parameter variation on weld pool characteristics.
        """
        fig = make_subplots(
            rows=1, cols=2,
            subplot_titles=('Pool Width vs Parameter', 'Penetration vs Parameter'),
            x_title=f"{parameter_name.title()}"
        )
        
        # Pool width
        fig.add_trace(
            go.Scatter(
                x=effects_df[parameter_name],
                y=effects_df['width'],
                mode='lines+markers',
                name='Pool Width',
                line=dict(color='blue', width=3),
                marker=dict(size=8)
            ),
            row=1, col=1
        )
        
        # Penetration
        fig.add_trace(
            go.Scatter(
                x=effects_df[parameter_name],
                y=effects_df['penetration'],
                mode='lines+markers',
                name='Penetration',
                line=dict(color='red', width=3),
                marker=dict(size=8)
            ),
            row=1, col=2
        )
        
        fig.update_yaxes(title_text="Width (mm)", row=1, col=1)
        fig.update_yaxes(title_text="Penetration (mm)", row=1, col=2)
        
        fig.update_layout(
            title=f"Effect of {parameter_name.title()} on Weld Pool Geometry",
            height=400,
            showlegend=False
        )
        
        return fig
    
    def plot_sensitivity_heatmap(self, sensitivity_df):
        """
        Create a sensitivity analysis heatmap.
        """
        # Prepare data for heatmap
        parameters = [s['parameter'] for s in sensitivity_df]
        width_sens = [s['width_sensitivity'] for s in sensitivity_df]
        penetration_sens = [s['penetration_sensitivity'] for s in sensitivity_df]
        
        # Create heatmap data
        heatmap_data = np.array([width_sens, penetration_sens])
        
        fig = go.Figure(data=go.Heatmap(
            z=heatmap_data,
            x=parameters,
            y=['Pool Width', 'Penetration'],
            colorscale='RdBu',
            zmid=0,
            colorbar=dict(title="Sensitivity Coefficient"),
            hovertemplate='Parameter: %{x}<br>Output: %{y}<br>Sensitivity: %{z:.3f}<extra></extra>'
        ))
        
        fig.update_layout(
            title="Parameter Sensitivity Analysis",
            xaxis_title="Input Parameters",
            yaxis_title="Output Characteristics",
            height=300
        )
        
        return fig
    
    def plot_tornado_diagram(self, sensitivity_df):
        """
        Create a tornado diagram for sensitivity analysis.
        """
        parameters = [s['parameter'] for s in sensitivity_df]
        width_sens = [abs(s['width_sensitivity']) for s in sensitivity_df]
        penetration_sens = [abs(s['penetration_sensitivity']) for s in sensitivity_df]
        
        fig = go.Figure()
        
        # Width sensitivity bars
        fig.add_trace(go.Bar(
            y=parameters,
            x=width_sens,
            name='Pool Width',
            orientation='h',
            marker_color='lightblue'
        ))
        
        # Penetration sensitivity bars
        fig.add_trace(go.Bar(
            y=parameters,
            x=penetration_sens,
            name='Penetration',
            orientation='h',
            marker_color='lightcoral'
        ))
        
        fig.update_layout(
            title="Tornado Diagram - Parameter Sensitivity",
            xaxis_title="Absolute Sensitivity Coefficient",
            yaxis_title="Parameters",
            barmode='group',
            height=400
        )
        
        return fig
