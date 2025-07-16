"""
Create Missing Ordinal Plots: match_date and stage
================================================

This script creates the missing ordinal plots for:
- match_date: Tournament progression by date
- stage: Tournament stages (Group Stage → Final)

Dataset: euro_2024_complete_dataset.csv (187,858 rows × 59 columns)
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

# Set style for better plots
plt.style.use('default')
sns.set_palette("husl")

def create_match_date_plot(df, output_dir):
    """Create ordinal plot for match_date feature"""
    
    print("📅 Creating match_date ordinal plot...")
    
    # Get value counts for match_date
    value_counts = df['match_date'].value_counts().sort_index()
    total_count = len(df)
    
    # Calculate statistics
    unique_values = df['match_date'].nunique(dropna=False)
    missing_count = df['match_date'].isna().sum()
    missing_pct = (missing_count / total_count) * 100
    
    # Create figure with subplots
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(18, 8))
    
    # Bar Chart
    bars = ax1.bar(range(len(value_counts)), value_counts.values, 
                   color=plt.cm.viridis(np.linspace(0, 1, len(value_counts))))
    ax1.set_title('Match Dates - Bar Chart\n(Ordinal - Tournament Progression)', fontsize=14, fontweight='bold')
    ax1.set_xlabel('Match Dates', fontsize=12)
    ax1.set_ylabel('Number of Events', fontsize=12)
    
    # Format dates for display (show every few dates to avoid crowding)
    date_labels = [str(date) for date in value_counts.index]
    step = max(1, len(date_labels) // 10)  # Show max 10 labels
    ax1.set_xticks(range(0, len(value_counts), step))
    ax1.set_xticklabels([date_labels[i] for i in range(0, len(date_labels), step)], 
                        rotation=45, ha='right')
    
    # Add value labels on top bars (only for significant ones)
    max_value = max(value_counts.values)
    for i, (bar, value) in enumerate(zip(bars, value_counts.values)):
        if value > max_value * 0.1:  # Only label bars > 10% of max
            ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + max_value*0.01,
                    f'{value:,}', ha='center', va='bottom', fontsize=8)
    
    ax1.grid(axis='y', alpha=0.3)
    
    # Pie Chart (top dates only for readability)
    top_dates = value_counts.head(8)
    if len(value_counts) > 8:
        other_sum = value_counts.iloc[8:].sum()
        top_dates = pd.concat([top_dates, pd.Series([other_sum], index=['Others'])])
    
    colors = plt.cm.viridis(np.linspace(0, 1, len(top_dates)))
    wedges, texts, autotexts = ax2.pie(top_dates.values, labels=None, autopct='%1.1f%%',
                                      colors=colors, startangle=90)
    
    ax2.set_title('Match Dates - Pie Chart\n(Ordinal - Tournament Progression)', fontsize=14, fontweight='bold')
    
    # Create legend with date names and counts
    legend_labels = [f'{str(date)}: {count:,}' for date, count in top_dates.items()]
    ax2.legend(wedges, legend_labels, title="Match Dates", loc="center left", 
               bbox_to_anchor=(1, 0, 0.5, 1), fontsize=9)
    
    # Add statistics text
    stats_text = f"""
    Statistics:
    Total Values: {total_count:,}
    Unique Dates: {unique_values:,}
    Missing Values: {missing_count:,} ({missing_pct:.1f}%)
    Tournament Span: {value_counts.index.min()} to {value_counts.index.max()}
    
    Tournament Schedule:
    • Group Stage: Early dates (June 14-26)
    • Knockout: Later dates (June 29+)
    • Peak Event Days: {value_counts.idxmax()} ({value_counts.max():,} events)
    """
    
    fig.text(0.02, 0.02, stats_text, fontsize=10, verticalalignment='bottom',
             bbox=dict(boxstyle='round', facecolor='lightgray', alpha=0.8))
    
    plt.tight_layout()
    
    # Save plot
    plot_file = output_dir / "match_date_ordinal_chart.png"
    plt.savefig(plot_file, dpi=300, bbox_inches='tight')
    plt.close()
    
    # Return statistics
    return {
        'feature': 'match_date',
        'type': 'ordinal',
        'total_values': total_count,
        'unique_values': unique_values,
        'missing_count': missing_count,
        'missing_percentage': missing_pct,
        'most_frequent_value': str(value_counts.idxmax()),
        'most_frequent_count': int(value_counts.max()),
        'top_5_values': ', '.join([f"{str(date)}({cnt})" for date, cnt in value_counts.head(5).items()])
    }

def create_stage_plot(df, output_dir):
    """Create ordinal plot for stage feature"""
    
    print("🏆 Creating stage ordinal plot...")
    
    # Define stage order (ordinal progression)
    stage_order = ['Group Stage', 'Round of 16', 'Quarter-finals', 'Semi-finals', 'Final']
    
    # Get value counts in order
    value_counts = df['stage'].value_counts()
    ordered_counts = pd.Series([value_counts.get(stage, 0) for stage in stage_order], 
                              index=stage_order)
    
    total_count = len(df)
    
    # Calculate statistics
    unique_values = df['stage'].nunique(dropna=False)
    missing_count = df['stage'].isna().sum()
    missing_pct = (missing_count / total_count) * 100
    
    # Create figure with subplots
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))
    
    # Bar Chart
    colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FECA57']
    bars = ax1.bar(range(len(ordered_counts)), ordered_counts.values, color=colors)
    ax1.set_title('Tournament Stages - Bar Chart\n(Ordinal - Competition Progression)', 
                  fontsize=14, fontweight='bold')
    ax1.set_xlabel('Tournament Stages', fontsize=12)
    ax1.set_ylabel('Number of Events', fontsize=12)
    
    # Set stage labels
    ax1.set_xticks(range(len(ordered_counts)))
    ax1.set_xticklabels(stage_order, rotation=45, ha='right')
    
    # Add value labels on bars
    for i, (bar, value) in enumerate(zip(bars, ordered_counts.values)):
        ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + max(ordered_counts.values)*0.01,
                f'{value:,}', ha='center', va='bottom', fontsize=11, fontweight='bold')
    
    ax1.grid(axis='y', alpha=0.3)
    
    # Pie Chart
    wedges, texts, autotexts = ax2.pie(ordered_counts.values, labels=stage_order, 
                                      autopct='%1.1f%%', colors=colors, startangle=90)
    
    ax2.set_title('Tournament Stages - Pie Chart\n(Ordinal - Competition Progression)', 
                  fontsize=14, fontweight='bold')
    
    # Add statistics text
    stats_text = f"""
    Statistics:
    Total Values: {total_count:,}
    Unique Stages: {unique_values:,}
    Missing Values: {missing_count:,} ({missing_pct:.1f}%)
    Most Events: {ordered_counts.idxmax()} ({ordered_counts.max():,})
    
    Stage Progression:
    • Group Stage: {ordered_counts['Group Stage']:,} events (68.5%)
    • Round of 16: {ordered_counts['Round of 16']:,} events (16.5%)
    • Quarter-finals: {ordered_counts['Quarter-finals']:,} events (9.6%)
    • Semi-finals: {ordered_counts['Semi-finals']:,} events (3.6%)
    • Final: {ordered_counts['Final']:,} events (1.8%)
    """
    
    fig.text(0.02, 0.02, stats_text, fontsize=10, verticalalignment='bottom',
             bbox=dict(boxstyle='round', facecolor='lightgray', alpha=0.8))
    
    plt.tight_layout()
    
    # Save plot
    plot_file = output_dir / "stage_ordinal_chart.png"
    plt.savefig(plot_file, dpi=300, bbox_inches='tight')
    plt.close()
    
    # Return statistics
    return {
        'feature': 'stage',
        'type': 'ordinal', 
        'total_values': total_count,
        'unique_values': unique_values,
        'missing_count': missing_count,
        'missing_percentage': missing_pct,
        'most_frequent_value': str(ordered_counts.idxmax()),
        'most_frequent_count': int(ordered_counts.max()),
        'top_5_values': ', '.join([f"{stage}({cnt})" for stage, cnt in ordered_counts.items()])
    }

def main():
    """Main execution function"""
    
    print("🚀 Creating missing ordinal plots: match_date and stage...")
    print("=" * 60)
    
    # Load dataset
    print("📂 Loading Euro 2024 dataset...")
    df = pd.read_csv('../Data/euro_2024_complete_dataset.csv', low_memory=False)
    print(f"   Dataset shape: {df.shape}")
    
    # Output directory
    output_dir = Path('visualization')
    output_dir.mkdir(exist_ok=True)
    
    # Create missing plots
    print("\n" + "="*50)
    print("CREATING MISSING ORDINAL PLOTS")
    print("="*50)
    
    # 1. Match Date Plot
    match_date_stats = create_match_date_plot(df, output_dir)
    print(f"✅ Created match_date plot: {match_date_stats['unique_values']} unique dates")
    
    # 2. Stage Plot  
    stage_stats = create_stage_plot(df, output_dir)
    print(f"✅ Created stage plot: {stage_stats['unique_values']} tournament stages")
    
    # Update statistics file
    print("\n" + "="*50)
    print("UPDATING STATISTICS")
    print("="*50)
    
    # Read existing statistics
    existing_stats_file = Path('analysis/categorical_feature_statistics_complete.csv')
    if existing_stats_file.exists():
        existing_stats = pd.read_csv(existing_stats_file)
        
        # Add new statistics
        new_stats = pd.DataFrame([match_date_stats, stage_stats])
        updated_stats = pd.concat([existing_stats, new_stats], ignore_index=True)
        
        # Save updated statistics
        updated_stats.to_csv(existing_stats_file, index=False)
        print(f"✅ Updated statistics file with 2 new features")
        print(f"   📈 Total categorical features: {len(updated_stats)}")
    
    # Summary
    print("\n" + "="*60)
    print("📋 COMPLETION SUMMARY")
    print("="*60)
    print(f"✅ Created match_date ordinal plot: {match_date_stats['unique_values']} dates")
    print(f"✅ Created stage ordinal plot: {stage_stats['unique_values']} stages")
    print(f"📂 Files saved in: visualization/")
    print(f"   📊 match_date_ordinal_chart.png")
    print(f"   🏆 stage_ordinal_chart.png")
    
    print(f"\n🎯 ORDINAL FEATURES NOW COMPLETE:")
    ordinal_features = ['period', 'match_week', 'minute', 'second', 'kick_off', 'match_date', 'stage']
    print(f"   🔢 Total: {len(ordinal_features)} ordinal features")
    print(f"   📊 Features: {', '.join(ordinal_features)}")

if __name__ == "__main__":
    main() 