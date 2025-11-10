"""
Batch Update Script: Add average_score_no_sentiment Column

This script adds a new metric column to all existing comparison CSVs:
- average_score_no_sentiment = (TF-IDF + Embeddings_BERT + content_overlap_ratio) / 3

This excludes sentiment from the scoring, focusing only on text similarity metrics.

Author: AI Assistant
Date: November 7, 2025
"""

import os
import pandas as pd
from pathlib import Path

# Paths
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(SCRIPT_DIR, '..', 'data')

def add_no_sentiment_score_to_csv(csv_path):
    """
    Add average_score_no_sentiment column to a single CSV file.
    
    Args:
        csv_path: Path to the CSV file
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Load CSV
        df = pd.read_csv(csv_path)
        
        # Check if column already exists
        if 'average_score_no_sentiment' in df.columns:
            print(f"  [SKIP] Column already exists: {os.path.basename(csv_path)}")
            return True
        
        # Calculate new metric
        df['average_score_no_sentiment'] = (
            df['TF-IDF'] + 
            df['Embeddings_BERT'] + 
            df['content_overlap_ratio']
        ) / 3
        
        # Reorder columns to place new metric after average_score
        cols = df.columns.tolist()
        
        # Find the position of average_score
        avg_score_idx = cols.index('average_score')
        
        # Remove the new column from its current position
        cols.remove('average_score_no_sentiment')
        
        # Insert it right after average_score
        cols.insert(avg_score_idx + 1, 'average_score_no_sentiment')
        
        # Reorder dataframe
        df = df[cols]
        
        # Save back to CSV
        df.to_csv(csv_path, index=False)
        
        print(f"  [OK] Updated: {os.path.basename(csv_path)}")
        return True
        
    except Exception as e:
        print(f"  [ERROR] Failed to update {os.path.basename(csv_path)}: {str(e)}")
        return False


def main():
    """Main function to update all comparison CSVs."""
    
    print("\n" + "="*80)
    print("BATCH UPDATE: Adding average_score_no_sentiment Column")
    print("="*80 + "\n")
    
    # Find all comparison CSV files
    csv_files = list(Path(DATA_DIR).glob('match_*_enhanced_comparison.csv'))
    
    if len(csv_files) == 0:
        print("[ERROR] No comparison CSV files found!")
        return
    
    print(f"Found {len(csv_files)} CSV files to update\n")
    
    # Update each file
    success_count = 0
    skip_count = 0
    fail_count = 0
    
    for csv_file in sorted(csv_files):
        result = add_no_sentiment_score_to_csv(str(csv_file))
        
        if result:
            # Check if it was skipped (column already exists)
            df = pd.read_csv(str(csv_file))
            if 'average_score_no_sentiment' in df.columns:
                success_count += 1
        else:
            fail_count += 1
    
    # Summary
    print("\n" + "="*80)
    print("BATCH UPDATE COMPLETE")
    print("="*80)
    print(f"\nTotal files processed: {len(csv_files)}")
    print(f"  Successfully updated: {success_count}")
    print(f"  Failed: {fail_count}")
    print(f"\nNew column: average_score_no_sentiment")
    print(f"Formula: (TF-IDF + Embeddings_BERT + content_overlap_ratio) / 3")
    print("="*80 + "\n")


if __name__ == "__main__":
    main()

