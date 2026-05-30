import sqlite3
from rapidfuzz import fuzz

# Fuzzy Logic Rules for Component Classification
RULES = [
    {"keywords": ["RESISTOR", "RES", "0402", "0603", "0805", "1206", "K", "OHM", "R", "RC"], "type": "Passive", "feeder": "8mm", "time": 0.10},
    {"keywords": ["CAPACITOR", "CAP", "CERAMIC", "UF", "NF", "PF", "F", "CC"], "type": "Passive", "feeder": "8mm", "time": 0.10},
    {"keywords": ["DIODE", "ZENER", "SCHOTTKY", "SOD", "LED"], "type": "Discrete", "feeder": "8mm", "time": 0.15},
    {"keywords": ["QFN", "SOIC", "TSSOP", "MCU", "IC", "CHIP", "STM", "MICRO"], "type": "Standard IC", "feeder": "12mm", "time": 0.80},
    {"keywords": ["BGA", "FPGA", "256-PIN", "LGA", "LQFP", "QFP"], "type": "Advanced IC", "feeder": "Tray", "time": 2.50},
    {"keywords": ["HEADER", "CONN", "USB", "RECEPTACLE", "JACK", "CONNECTOR"], "type": "Connector", "feeder": "Manual/Odd", "time": 1.50}
]

def check_database(component_value):
    """Checks the Master Component Database using Value (e.g., '100K', '10K')."""
    if not component_value or component_value == "N/A" or component_value == "UNKNOWN":
        return None
        
    try:
        conn = sqlite3.connect("master_components.db")
        cursor = conn.cursor()
        cursor.execute("SELECT component_type, feeder, placement_time FROM components WHERE component_value=?", (str(component_value),))
        result = cursor.fetchone()
        conn.close()
        return result
    except:
        return None

def classify_component(row):
    """
    Analyzes the BOM row and outputs standardized manufacturing constraints.
    Uses the 'Value' column (which becomes Part Number after normalization) for lookup.
    """
    part_num = str(row.get("Part Number", ""))
    desc = str(row.get("Description", "")).upper()
    package = str(row.get("Package", "")).upper()
    
    # The Value from BOM (e.g., "100K", "10K") is stored in Part Number after normalization
    component_value = part_num
    
    # Combine Description, Part Number, and Package for a stronger text-analysis string
    analysis_text = f"{desc} {part_num} {package}"
    
    # 1. Database Memory Override - Look up by Value
    db_result = check_database(component_value)
    if db_result:
        return {
            "Component_Type": db_result[0],
            "Feeder": db_result[1],
            "Placement_Time": db_result[2]
        }
    
    # 2. Try to classify by package size first
    if "0402" in package or "402" in package:
        return {"Component_Type": "Passive", "Feeder": "8mm", "Placement_Time": 0.08}
    elif "0603" in package or "603" in package:
        return {"Component_Type": "Passive", "Feeder": "8mm", "Placement_Time": 0.10}
    elif "0805" in package or "805" in package:
        return {"Component_Type": "Passive", "Feeder": "8mm", "Placement_Time": 0.12}
    elif "1206" in package:
        return {"Component_Type": "Passive", "Feeder": "8mm", "Placement_Time": 0.15}
    elif "SOT" in package:
        return {"Component_Type": "Discrete", "Feeder": "8mm", "Placement_Time": 0.15}
    elif "SOIC" in package or "TSSOP" in package:
        return {"Component_Type": "Standard IC", "Feeder": "12mm", "Placement_Time": 0.60}
    elif "QFN" in package:
        return {"Component_Type": "Standard IC", "Feeder": "16mm", "Placement_Time": 0.80}
    elif "BGA" in package:
        return {"Component_Type": "Advanced IC", "Feeder": "Tray", "Placement_Time": 2.50}
    
    # 3. NLP / Fuzzy Logic Engine
    best_score = 0
    best_match = None
    
    for rule in RULES:
        for keyword in rule["keywords"]:
            score = fuzz.partial_ratio(keyword, analysis_text)
            if score > best_score:
                best_score = score
                best_match = rule
                
    # If confidence is > 70%, assign the matched parameters
    if best_score >= 70 and best_match:
        return {
            "Component_Type": best_match["type"],
            "Feeder": best_match["feeder"],
            "Placement_Time": best_match["time"]
        }
        
    # 4. Failsafe for Unrecognized Components
    return {
        "Component_Type": "Unknown",
        "Feeder": "8mm",
        "Placement_Time": 0.50
    }