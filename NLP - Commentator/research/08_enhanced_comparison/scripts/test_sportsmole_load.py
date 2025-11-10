"""Test loading SportsMole CSVs with different parameters"""
import pandas as pd
import sys

files = [
    "sports_mole_spain_germany_commentary.csv",
    "sports_mole_portugal_france_commentary.csv", 
    "sports_mole_france_belgium_commentary.csv"
]

data_dir = r"C:\Users\yonatanam\Desktop\Euro 2024 - momentum - DS-AI project\NLP - Commentator\research\05_real_commentary_comparison\data"

for file in files:
    filepath = f"{data_dir}\\{file}"
    print(f"\n{'='*60}")
    print(f"Testing: {file}")
    print(f"{'='*60}")
    
    try:
        # Try with default settings
        df = pd.read_csv(filepath)
        print(f"[SUCCESS] Default: {len(df)} rows loaded")
    except Exception as e:
        print(f"[FAILED] Default: {str(e)[:100]}")
        
    try:
        # Try with error_bad_lines=False (deprecated but might work)
        df = pd.read_csv(filepath, on_bad_lines='skip')
        print(f"[SUCCESS] on_bad_lines='skip': {len(df)} rows loaded")
    except Exception as e:
        print(f"[FAILED] on_bad_lines='skip': {str(e)[:100]}")
        
    try:
        # Try with quoting
        df = pd.read_csv(filepath, quoting=1)  # QUOTE_ALL
        print(f"[SUCCESS] quoting=1: {len(df)} rows loaded")
    except Exception as e:
        print(f"[FAILED] quoting=1: {str(e)[:100]}")

