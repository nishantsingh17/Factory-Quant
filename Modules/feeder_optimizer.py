import pandas as pd

def map_package_to_feeder(package):
    """
    Map package size to feeder width.
    Handles common SMT package sizes and converts package codes to feeder widths.
    """
    package_str = str(package).upper().strip()
    
    # Extract numeric size from package (e.g., "0402", "0603", "0805", "1206")
    import re
    size_match = re.search(r'(\d{4})', package_str)
    
    if size_match:
        size = size_match.group(1)
        if size in ['0402', '0201', '402']:
            return "8mm"
        elif size in ['0603', '0605', '603']:
            return "8mm"
        elif size in ['0805', '0806', '805']:
            return "8mm"
        elif size in ['1206', '1210']:
            return "8mm"
        elif size in ['1812', '1825']:
            return "12mm"
        elif size in ['2010', '2220']:
            return "12mm"
        elif size in ['2512', '2828']:
            return "16mm"
    
    # Component type based mapping
    if 'SOT' in package_str or 'SOD' in package_str:
        return "8mm"
    elif 'SOIC' in package_str or 'TSSOP' in package_str or 'SSOP' in package_str:
        return "12mm"
    elif 'QFN' in package_str or 'QFP' in package_str or 'LQFP' in package_str:
        return "16mm"
    elif 'BGA' in package_str or 'LGA' in package_str:
        return "Tray"
    elif 'CONN' in package_str or 'HEADER' in package_str or 'USB' in package_str:
        return "Manual/Odd"
    elif 'LED' in package_str:
        return "8mm"
    elif 'DIODE' in package_str:
        return "8mm"
    
    # Default to 8mm for small passives
    return "8mm"


def estimate_placement_time(component_type, package, description):
    """
    Estimate placement time based on component type and package.
    """
    desc_upper = str(description).upper()
    pkg_upper = str(package).upper()
    
    # ICs and complex components
    if 'QFN' in pkg_upper or 'QFP' in pkg_upper or 'LQFP' in pkg_upper:
        return 0.80
    elif 'BGA' in pkg_upper or 'LGA' in pkg_upper:
        return 2.50
    elif 'SOIC' in pkg_upper or 'TSSOP' in pkg_upper or 'SSOP' in pkg_upper:
        return 0.60
    elif 'SOT' in pkg_upper or 'SOD' in pkg_upper:
        return 0.15
    
    # Connectors
    if 'CONN' in desc_upper or 'HEADER' in desc_upper or 'USB' in desc_upper:
        return 1.50
    
    # LEDs and Diodes
    if 'LED' in desc_upper:
        return 0.12
    if 'DIODE' in desc_upper:
        return 0.15
    
    # Passives (resistors, capacitors)
    if 'RES' in desc_upper or 'CAP' in desc_upper:
        # Check package size for finer granularity
        if '0402' in pkg_upper or '402' in pkg_upper:
            return 0.08
        elif '0603' in pkg_upper or '603' in pkg_upper:
            return 0.10
        elif '0805' in pkg_upper or '805' in pkg_upper:
            return 0.12
        elif '1206' in pkg_upper:
            return 0.15
        return 0.10
    
    # Default
    return 0.50


def feeder_summary(df):
    """
    Calculates physical machine resource requirements and 
    total placement time based on the classified BOM.
    Also provides feeder placement optimization recommendations.
    """
    
    # Safety step: Ensure quantities and times are treated as numbers, not text
    df['Quantity'] = pd.to_numeric(df['Quantity'], errors='coerce').fillna(0)
    
    # Create Component Type if not exists
    if 'Component_Type' not in df.columns:
        df['Component_Type'] = df['Description'].apply(
            lambda x: 'Passive' if any(k in str(x).upper() for k in ['RES', 'CAP', 'RESISTOR', 'CAPACITOR']) 
            else ('Standard IC' if any(k in str(x).upper() for k in ['IC', 'MCU', 'STM', 'MICRO', 'QFN', 'SOIC']) 
            else ('Connector' if any(k in str(x).upper() for k in ['CONN', 'HEADER', 'USB']) 
            else 'Unknown'))
        )
    
    # Create Feeder column if not exists
    if 'Feeder' not in df.columns:
        df['Feeder'] = df['Package'].apply(map_package_to_feeder)
    
    # Create Placement Time if not exists
    if 'Placement_Time' not in df.columns:
        df['Placement_Time'] = df.apply(
            lambda row: estimate_placement_time(
                row.get('Component_Type', 'Unknown'), 
                row.get('Package', ''), 
                row.get('Description', '')
            ), axis=1
        )
    
    # 1. Feeder Count Algorithm
    # We group by the 'Feeder' width, and count the UNIQUE 'Part Numbers'.
    feeder_counts = df.groupby('Feeder')['Part Number'].nunique().to_dict()
    
    # Calculate the total physical slots required on the machine
    total_slots_used = sum(feeder_counts.values())
    
    # 2. Time & Component Calculations
    df['Total_Time'] = df['Quantity'] * df['Placement_Time']
    total_placement_time = df['Total_Time'].sum()
    total_components = int(df['Quantity'].sum())
    
    # 3. Component Type Counts
    component_counts = df['Component_Type'].value_counts().to_dict()
    
    # 4. Feeder Optimization Analysis (Pareto Principle)
    part_quantity = df.groupby('Part Number').agg({
        'Quantity': 'sum',
        'Feeder': 'first',
        'Component_Type': 'first',
        'Placement_Time': 'first',
        'Description': 'first',
        'Package': 'first'
    }).reset_index()
    
    part_quantity = part_quantity.sort_values('Quantity', ascending=False)
    total_quantity = part_quantity['Quantity'].sum()
    
    if total_quantity > 0:
        cumulative = 0
        high_volume_parts = []
        medium_volume_parts = []
        low_volume_parts = []
        
        for _, row in part_quantity.iterrows():
            cumulative += row['Quantity']
            cumulative_percentage = (cumulative / total_quantity) * 100
            
            if cumulative_percentage <= 80:
                high_volume_parts.append(row)
            elif cumulative_percentage <= 95:
                medium_volume_parts.append(row)
            else:
                low_volume_parts.append(row)
        
        # Generate feeder placement recommendations
        feeder_recommendations = {
            "center_feeder_positions": [],
            "edge_feeder_positions": [],
            "optimization_summary": {}
        }
        
        # High volume components -> CENTER
        for part in high_volume_parts:
            feeder_recommendations["center_feeder_positions"].append({
                "part_number": str(part['Part Number']),
                "quantity": int(part['Quantity']),
                "quantity_percentage": round((part['Quantity'] / total_quantity) * 100, 1),
                "feeder_width": part['Feeder'],
                "component_type": part.get('Component_Type', 'Unknown'),
                "placement_time": part['Placement_Time'],
                "description": str(part.get('Description', 'N/A'))[:50],
                "package": str(part.get('Package', 'N/A')),
                "recommended_position": "CENTER (High Speed Zone)",
                "reason": f"High volume - {int(part['Quantity'])} pcs ({round((part['Quantity'] / total_quantity) * 100, 1)}% of total)"
            })
        
        # Medium volume -> MIDDLE ZONE
        for part in medium_volume_parts:
            feeder_recommendations["edge_feeder_positions"].append({
                "part_number": str(part['Part Number']),
                "quantity": int(part['Quantity']),
                "quantity_percentage": round((part['Quantity'] / total_quantity) * 100, 1),
                "feeder_width": part['Feeder'],
                "component_type": part.get('Component_Type', 'Unknown'),
                "placement_time": part['Placement_Time'],
                "description": str(part.get('Description', 'N/A'))[:50],
                "package": str(part.get('Package', 'N/A')),
                "recommended_position": "MIDDLE ZONE",
                "reason": f"Medium volume - {int(part['Quantity'])} pcs ({round((part['Quantity'] / total_quantity) * 100, 1)}% of total)"
            })
        
        # Low volume components -> EDGE
        for part in low_volume_parts:
            feeder_recommendations["edge_feeder_positions"].append({
                "part_number": str(part['Part Number']),
                "quantity": int(part['Quantity']),
                "quantity_percentage": round((part['Quantity'] / total_quantity) * 100, 1),
                "feeder_width": part['Feeder'],
                "component_type": part.get('Component_Type', 'Unknown'),
                "placement_time": part['Placement_Time'],
                "description": str(part.get('Description', 'N/A'))[:50],
                "package": str(part.get('Package', 'N/A')),
                "recommended_position": "EDGE (Low Speed Zone)",
                "reason": f"Low volume - {int(part['Quantity'])} pcs ({round((part['Quantity'] / total_quantity) * 100, 1)}% of total)"
            })
        
        # Calculate estimated time savings (15% reduction for high-volume parts)
        total_high_volume_time = sum([p['Placement_Time'] * p['Quantity'] for p in high_volume_parts])
        estimated_time_savings = total_high_volume_time * 0.15
        
        feeder_recommendations["optimization_summary"] = {
            "total_unique_parts": len(part_quantity),
            "high_volume_parts_count": len(high_volume_parts),
            "medium_volume_parts_count": len(medium_volume_parts),
            "low_volume_parts_count": len(low_volume_parts),
            "high_volume_percentage": round((sum([p['Quantity'] for p in high_volume_parts]) / total_quantity) * 100, 1),
            "estimated_time_savings_seconds": round(estimated_time_savings, 2),
            "optimization_message": f"Place {len(high_volume_parts)} high-volume components in CENTER feeders for optimal speed",
            "pareto_principle": f"{len(high_volume_parts)} parts = {round((sum([p['Quantity'] for p in high_volume_parts]) / total_quantity) * 100, 1)}% of volume"
        }
    else:
        feeder_recommendations = {
            "center_feeder_positions": [],
            "edge_feeder_positions": [],
            "optimization_summary": {
                "total_unique_parts": 0,
                "high_volume_parts_count": 0,
                "medium_volume_parts_count": 0,
                "low_volume_parts_count": 0,
                "high_volume_percentage": 0,
                "estimated_time_savings_seconds": 0,
                "optimization_message": "No components to optimize",
                "pareto_principle": "No data available"
            }
        }

    return {
        "feeder_counts": feeder_counts,
        "total_slots_used": total_slots_used,
        "total_placement_time": total_placement_time,
        "total_components": total_components,
        "component_counts": component_counts,
        "feeder_recommendations": feeder_recommendations,
        "part_quantity_analysis": part_quantity.to_dict('records') if total_quantity > 0 else []
    }