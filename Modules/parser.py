import pandas as pd
import re

def normalize_bom(raw_df):
    """
    Ingests BOM DataFrames and maps varied column headers to an internal standard.
    Handles multiple BOM formats including those without Part Numbers or Package columns.
    This is a ROBUST version that can handle almost any CSV format.
    """
    
    # 1. Edge Case: Drop completely blank rows immediately
    raw_df = raw_df.dropna(how='all')
    
    # 2. Remove completely empty columns (all NaN or empty strings)
    raw_df = raw_df.dropna(axis=1, how='all')
    empty_cols = []
    for col in raw_df.columns:
        if raw_df[col].astype(str).str.strip().eq('').all():
            empty_cols.append(col)
    if empty_cols:
        raw_df = raw_df.drop(columns=empty_cols)
    
    # 3. Make a copy and convert column names to uppercase for case-insensitive matching
    df = raw_df.copy()
    df.columns = [str(col).strip().upper() for col in df.columns]
    
    # 4. Define column mappings (flexible matching)
    column_mapping = {
        "Designator": ["REFDES", "REF", "DESIGNATOR", "ID", "PART REFERENCE", "REFERENCE", "COMPONENT", "NAME", "PART"],
        "Part Number": ["MPN", "PN", "PART NUMBER", "MANUFACTURER PN", "MFG PN", "PART", "COMPONENT", "VALUE", "PARTNO"],
        "Description": ["DESCRIPTION", "DESC", "COMMENT", "NAME", "COMPONENT", "VALUE", "DETAILS", "PART NAME"],
        "Quantity": ["QTY", "QUANTITY", "COUNT", "AMOUNT", "Q"],
        "Package": ["PACKAGE", "FOOTPRINT", "PATTERN", "PCB FOOTPRINT", "CASE", "PKG", "SIZE"]
    }
    
    # 5. Create normalized DataFrame with standard columns
    normalized_df = pd.DataFrame()
    
    # Map each standard column
    for standard_col, aliases in column_mapping.items():
        found = False
        for alias in aliases:
            if alias in df.columns:
                normalized_df[standard_col] = df[alias]
                found = True
                break
        
        if not found:
            # Try partial matching (e.g., "QTY" in "TOTAL QTY")
            for col in df.columns:
                for alias in aliases:
                    if alias in col or col in alias:
                        normalized_df[standard_col] = df[col]
                        found = True
                        break
                if found:
                    break
        
        # If still not found, create default column
        if not found:
            if standard_col == "Designator":
                # Create designator from row index
                normalized_df[standard_col] = [f"Comp_{i+1}" for i in range(len(df))]
            elif standard_col == "Part Number":
                normalized_df[standard_col] = "UNKNOWN"
            elif standard_col == "Description":
                normalized_df[standard_col] = "N/A"
            elif standard_col == "Quantity":
                normalized_df[standard_col] = 1
            elif standard_col == "Package":
                normalized_df[standard_col] = "0603"  # Default package
    
    # 6. Clean and convert data types
    # Convert Quantity to numeric
    normalized_df['Quantity'] = pd.to_numeric(normalized_df['Quantity'], errors='coerce').fillna(1)
    
    # Ensure Quantity is at least 1
    normalized_df['Quantity'] = normalized_df['Quantity'].clip(lower=1)
    
    # Convert all text columns to string
    normalized_df['Part Number'] = normalized_df['Part Number'].astype(str).str.strip()
    normalized_df['Description'] = normalized_df['Description'].astype(str).str.strip()
    normalized_df['Package'] = normalized_df['Package'].astype(str).str.strip()
    normalized_df['Designator'] = normalized_df['Designator'].astype(str).str.strip()
    
    # 7. Handle missing Part Numbers - use Description if available
    missing_part_mask = (normalized_df['Part Number'] == "UNKNOWN") | (normalized_df['Part Number'] == "")
    if missing_part_mask.any():
        normalized_df.loc[missing_part_mask, 'Part Number'] = normalized_df.loc[missing_part_mask, 'Description']
    
    # 8. Extract package size from Description or Part Number if Package is default
    package_default_mask = normalized_df['Package'] == "0603"
    if package_default_mask.any():
        def extract_package(text):
            text = str(text).upper()
            # Look for common package patterns
            patterns = [
                (r'0402', '0402'), (r'0603', '0603'), (r'0805', '0805'), 
                (r'1206', '1206'), (r'1210', '1210'), (r'1812', '1812'),
                (r'2010', '2010'), (r'2512', '2512'),
                (r'SOT-?\d+', 'SOT'), (r'SOIC-?\d+', 'SOIC'), 
                (r'QFN-?\d+', 'QFN'), (r'TSSOP-?\d+', 'TSSOP'),
                (r'BGA-?\d+', 'BGA'), (r'LQFP-?\d+', 'LQFP')
            ]
            for pattern, pkg in patterns:
                if re.search(pattern, text, re.IGNORECASE):
                    return pkg
            return "0603"
        
        normalized_df.loc[package_default_mask, 'Package'] = normalized_df.loc[package_default_mask, 'Description'].apply(extract_package)
        normalized_df.loc[package_default_mask, 'Package'] = normalized_df.loc[package_default_mask, 'Part Number'].apply(extract_package)
    
    # 9. Clean Part Numbers - remove special characters and normalize
    normalized_df['Part Number'] = normalized_df['Part Number'].str.replace(r'[^\w\s-]', '', regex=True)
    
    # 10. Drop rows with zero or invalid quantities
    normalized_df = normalized_df[normalized_df['Quantity'] > 0]
    
    # 11. Reset index
    normalized_df = normalized_df.reset_index(drop=True)
    
    # 12. Select only the columns we need (in correct order)
    final_columns = ["Designator", "Part Number", "Description", "Quantity", "Package"]
    existing_columns = [col for col in final_columns if col in normalized_df.columns]
    normalized_df = normalized_df[existing_columns]
    
    return normalized_df