# 🏭 Factory-Quant: Automated SMT Resource & Cost Planner

![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-Framework-FF4B4B)
![Pandas](https://img.shields.io/badge/Pandas-Data_Processing-150458)
![SQLite](https://img.shields.io/badge/SQLite-Database-003B57)

Factory-Quant is a data-driven manufacturing tool designed to eliminate manual guesswork in Surface Mount Technology (SMT) quoting. It ingests messy, non-standard Bill of Materials (BOM) files from various CAD environments, normalizes the data, intelligently classifies components, and calculates precise physical and financial constraints for the factory floor.

## 🚀 The Problem
Small and Medium Enterprises (MSMEs) in electronics manufacturing often struggle with:
1. **Chaotic Data:** Every CAD software (Altium, KiCad, Eagle) exports different column headers.
2. **Manual Quoting:** Engineers waste hours manually counting components to estimate labor time.
3. **Machine Constraints:** Finding out a board requires more feeder slots than the Pick & Place machine has *after* accepting the job.

## 💡 The Solution
Factory-Quant provides a linear, three-step workflow to turn raw BOMs into profitable, highly accurate manufacturing quotes in seconds.

### Key Features
* **Multi-CAD Parser:** Automatically maps disparate column headers (e.g., "RefDes" vs "Designator") to a strict internal standard using `pandas`.
* **Smart Component Classifier:** Utilizes `RapidFuzz` (fuzzy logic) to dynamically categorize unstructured component descriptions (e.g., distinguishing a standard 0603 resistor from a complex 256-pin BGA).
* **Machine Resource Optimizer:** Groups unique part numbers to map required 8mm, 12mm, 24mm, and Tray feeders, instantly warning operators if machine capacity is exceeded.
* **Dynamic Cost Engine:** Calculates highly accurate batch costs and unit economics by factoring in placement times, labor rates, fixed overheads, and real-world line efficiency.
* **Master Component Library:** A persistent SQLite database with full CRUD capabilities, allowing the software to "learn" and remember custom parts over time.
* **Automated PDF Invoicing:** Generates a professional, color-coded manufacturing report using `fpdf`.

## 🛠️ Software Architecture

| Feature | Tech Stack | Output |
| :--- | :--- | :--- |
| **BOM Importer** | `pandas`, `openpyxl` | Normalized Part List |
| **Component Brain** | `rapidfuzz`, `sqlite3` | Classification & Placement Time |
| **Feeder Optimizer** | Python Custom Logic | Required Feeder List & Widths |
| **Cost Calculator** | Python Math Engine | Final Quote / Cost per Board |
| **Report Generator**| `fpdf` | PDF Manufacturing Summary |
| **User Interface** | `Streamlit` | Single Dashboard Application |

## 📂 Project Structure
```text
FactoryQuant/
│
├── app.py                      # Main Streamlit dashboard and UI routing
├── requirements.txt            # Python dependencies
├── START_FACTORY_QUANT.bat     # Windows batch executable for floor operators
├── master_components.db        # Persistent SQLite database (auto-generated)
│
└── modules/                    # Core backend logic
    ├── parser.py               # CAD alias mapping engine
    ├── classifier.py           # RapidFuzz text classification
    ├── feeder_optimizer.py     # Machine capacity and time math
    ├── cost_calculator.py      # Financial translation engine
    ├── database_manager.py     # SQLite CRUD operations
    └── report_generator.py     # PDF drawing and formatting
