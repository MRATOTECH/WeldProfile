# Overview

This is a scientific welding simulation application built with Streamlit that provides physics-based analysis of welding processes. The application allows users to analyze weld pool characteristics, temperature distributions, and parameter effects using established heat transfer equations and material properties. It features an interactive web interface for adjusting welding parameters and visualizing simulation results through various charts and cross-sectional views.

# User Preferences

Preferred communication style: Simple, everyday language.

# System Architecture

## Frontend Architecture
- **Framework**: Streamlit web application framework for rapid prototyping and scientific applications
- **Layout**: Wide layout with expandable sidebar for parameter controls
- **Visualization**: Plotly for interactive 3D and 2D charts, with matplotlib/seaborn as fallback options
- **User Interface**: Real-time parameter sliders and controls in sidebar, main content area for results display

## Backend Architecture
- **Physics Engine**: Custom `WeldingSimulator` class implementing Rosenthal's heat transfer equations and empirical correlations
- **Material Database**: `MaterialProperties` class containing thermal and physical properties for different materials (Steel, Aluminum, etc.)
- **Visualization Engine**: `WeldingVisualizer` class for generating weld pool cross-sections, temperature distributions, and sensitivity analyses
- **Session Management**: Streamlit session state for maintaining simulator and visualizer instances across user interactions

## Core Simulation Components
- **Heat Input Calculations**: Arc efficiency-based models for GTAW and GMAW processes
- **Weld Pool Geometry**: Physics-based calculations using material thermal properties and heat transfer equations
- **Temperature Distribution**: Rosenthal's moving heat source solutions for 2D and 3D temperature fields
- **Material Properties**: Comprehensive database including thermal conductivity, density, specific heat, melting temperatures, and latent heat values

## Data Flow
- User inputs welding parameters through sidebar controls
- Parameters fed to physics simulator for weld pool calculations
- Results processed by visualization engine for chart generation
- Interactive plots displayed in main application area with real-time updates

# External Dependencies

## Python Libraries
- **streamlit**: Web application framework and UI components
- **numpy**: Numerical computing and array operations
- **pandas**: Data manipulation and analysis
- **plotly**: Interactive visualization and charting (graph_objects, express, subplots)
- **matplotlib**: Static plotting and chart generation
- **seaborn**: Statistical data visualization
- **scipy**: Scientific computing (special functions, optimization)

## Visualization Stack
- **Plotly**: Primary visualization engine for interactive 3D plots, temperature distributions, and weld pool cross-sections
- **Matplotlib/Seaborn**: Secondary plotting options for static charts and statistical visualizations

## Scientific Computing
- **SciPy**: Optimization algorithms for solving heat transfer equations and special mathematical functions
- **NumPy**: Mathematical operations, array handling, and numerical integration for physics calculations