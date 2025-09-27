#!/usr/bin/env python3
"""
Generate sample XLSX file for testing import functionality.

Generuje przykładowy plik XLSX dla testów funkcjonalności importu.
"""

import pandas as pd
import numpy as np
from pathlib import Path

def create_sample_regenerator_data():
    """Create sample regenerator data for testing."""

    # Sample data for Checker Pattern Configuration (Template v1)
    n_checkers = 20
    materials = ['Silica Brick', 'Magnesia Brick', 'Alumina Brick']

    checker_data = {
        'Checker_ID': [f'CHK_{i:03d}' for i in range(1, n_checkers + 1)],
        'Material_Type': [materials[i % len(materials)] for i in range(n_checkers)],
        'Length_mm': np.random.uniform(200, 500, n_checkers),
        'Width_mm': np.random.uniform(100, 300, n_checkers),
        'Height_mm': np.random.uniform(50, 150, n_checkers),
        'Thermal_Conductivity_W_mK': np.random.uniform(1.0, 5.0, n_checkers),
        'Specific_Heat_kJ_kgK': np.random.uniform(0.8, 1.2, n_checkers),
        'Density_kg_m3': np.random.uniform(1800, 2500, n_checkers),
        'Porosity_percent': np.random.uniform(10, 30, n_checkers),
        'Surface_Area_m2_m3': np.random.uniform(100, 500, n_checkers),
        'Operating_Temp_C': np.random.uniform(800, 1600, n_checkers),
        'Design_Pressure_Pa': np.random.uniform(1000, 5000, n_checkers),
    }

    # Wall Configuration data (Template v2)
    n_walls = 10
    wall_types = ['HOT', 'COLD', 'FLUE']
    wall_materials = ['Refractory Brick', 'Insulation Brick', 'Steel Lining']

    wall_data = {
        'Wall_ID': [f'WALL_{i:02d}' for i in range(1, n_walls + 1)],
        'Wall_Type': [wall_types[i % len(wall_types)] for i in range(n_walls)],
        'Material_Name': [wall_materials[i % len(wall_materials)] for i in range(n_walls)],
        'Thickness_mm': np.random.uniform(100, 500, n_walls),
        'Area_m2': np.random.uniform(10, 100, n_walls),
        'U_Value_W_m2K': np.random.uniform(0.5, 3.0, n_walls),
        'Heat_Loss_W': np.random.uniform(1000, 50000, n_walls),
        'Inner_Temp_C': np.random.uniform(800, 1500, n_walls),
        'Outer_Temp_C': np.random.uniform(50, 200, n_walls),
    }

    # Operating Conditions data (Template v3)
    operating_data = {
        'Parameter': [
            'Air_Flow_Rate_m3_h', 'Gas_Flow_Rate_m3_h', 'Air_Inlet_Temp_C',
            'Gas_Inlet_Temp_C', 'Air_Outlet_Temp_C', 'Gas_Outlet_Temp_C',
            'Pressure_Drop_Pa', 'Heat_Recovery_Efficiency_percent',
            'Fuel_Consumption_m3_h', 'CO2_Emissions_kg_h'
        ],
        'Value': [
            25000, 30000, 200, 1450, 800, 350,
            2500, 85.5, 1200, 2800
        ],
        'Unit': [
            'm³/h', 'm³/h', '°C', '°C', '°C', '°C',
            'Pa', '%', 'm³/h', 'kg/h'
        ],
        'Min_Value': [
            20000, 25000, 150, 1200, 600, 250,
            1000, 75.0, 800, 2000
        ],
        'Max_Value': [
            35000, 40000, 300, 1600, 1000, 500,
            5000, 95.0, 2000, 4000
        ]
    }

    return checker_data, wall_data, operating_data

def save_sample_files():
    """Save sample XLSX files for testing."""

    # Create test_data directory
    test_dir = Path('F:/Projekty_ClaudeCode/RegeneratorCalc_v2/test_data')
    test_dir.mkdir(exist_ok=True)

    checker_data, wall_data, operating_data = create_sample_regenerator_data()

    # Create Template v1 - Checker Pattern Configuration
    checker_df = pd.DataFrame(checker_data)
    checker_file = test_dir / 'template_v1_checker_pattern.xlsx'
    checker_df.to_excel(checker_file, index=False, sheet_name='Checker_Configuration')
    print(f"Created: {checker_file}")

    # Create Template v2 - Wall Configuration
    wall_df = pd.DataFrame(wall_data)
    wall_file = test_dir / 'template_v2_wall_config.xlsx'
    wall_df.to_excel(wall_file, index=False, sheet_name='Wall_Configuration')
    print(f"Created: {wall_file}")

    # Create Template v3 - Operating Conditions
    operating_df = pd.DataFrame(operating_data)
    operating_file = test_dir / 'template_v3_operating_conditions.xlsx'
    operating_df.to_excel(operating_file, index=False, sheet_name='Operating_Conditions')
    print(f"Created: {operating_file}")

    # Create multi-sheet comprehensive file
    comprehensive_file = test_dir / 'comprehensive_regenerator_data.xlsx'
    with pd.ExcelWriter(comprehensive_file, engine='openpyxl') as writer:
        checker_df.to_excel(writer, sheet_name='Checker_Pattern', index=False)
        wall_df.to_excel(writer, sheet_name='Wall_Config', index=False)
        operating_df.to_excel(writer, sheet_name='Operating_Conditions', index=False)
    print(f"Created comprehensive file: {comprehensive_file}")

if __name__ == '__main__':
    save_sample_files()
    print("Sample XLSX files created successfully!")