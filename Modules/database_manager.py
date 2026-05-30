import sqlite3
import pandas as pd

DB_FILE = "master_components.db"

def init_db():
    """Creates the database file and table if it doesn't exist."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS components (
            component_value TEXT PRIMARY KEY,
            component_type TEXT,
            feeder TEXT,
            placement_time REAL,
            part_number TEXT
        )
    ''')
    conn.commit()
    conn.close()

def save_component(component_value, comp_type, feeder, placement_time, part_number=""):
    """Saves or updates a component in the database using Value as key."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT OR REPLACE INTO components (component_value, component_type, feeder, placement_time, part_number)
        VALUES (?, ?, ?, ?, ?)
    ''', (str(component_value), str(comp_type), str(feeder), float(placement_time), str(part_number)))
    conn.commit()
    conn.close()

def load_database():
    """Loads the entire database as a pandas DataFrame for viewing."""
    conn = sqlite3.connect(DB_FILE)
    df = pd.read_sql_query("SELECT * FROM components", conn)
    conn.close()
    return df

def delete_component(component_value):
    """Deletes a specific component from the database by Value."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM components WHERE component_value=?", (str(component_value),))
    conn.commit()
    conn.close()

def lookup_component(component_value):
    """Looks up a component by its Value (e.g., '100K', '10K')."""
    if not component_value or component_value == "N/A":
        return None
        
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("SELECT component_type, feeder, placement_time FROM components WHERE component_value=?", (str(component_value),))
        result = cursor.fetchone()
        conn.close()
        return result
    except:
        return None