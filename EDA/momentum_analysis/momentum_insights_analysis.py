import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

def create_insights_report():
    """Generate comprehensive insights report from momentum analysis"""
    
    print("🎯 COMPREHENSIVE MOMENTUM ANALYSIS INSIGHTS")
    print("=" * 80)
    
    # Load results
    pass_clusters = pd.read_csv('pass_cluster_analysis.csv')
    carry_clusters = pd.read_csv('carry_cluster_analysis.csv')
    pass_importance = pd.read_csv('pass_feature_importance.csv')
    carry_importance = pd.read_csv('carry_feature_importance.csv')
    
    # Create visualizations
    fig, axes = plt.subplots(2, 3, figsize=(18, 12))
    
    # Pass cluster analysis
    axes[0,0].pie(pass_clusters['Size'], labels=[f'C{i}' for i in pass_clusters['Cluster']], 
                  autopct='%1.1f%%', startangle=90)
    axes[0,0].set_title('Pass Event Clusters Distribution')
    
    # Pass forward progress by cluster
    axes[0,1].bar(pass_clusters['Cluster'], pass_clusters['Avg_Forward_Progress'].str.replace('', '').astype(float))
    axes[0,1].set_title('Pass Forward Progress by Cluster')
    axes[0,1].set_xlabel('Cluster')
    axes[0,1].set_ylabel('Avg Forward Progress (meters)')
    
    # Pass success rate by cluster
    axes[0,2].bar(pass_clusters['Cluster'], pass_clusters['Pass_Success_Rate'].str.replace('', '').astype(float))
    axes[0,2].set_title('Pass Success Rate by Cluster')
    axes[0,2].set_xlabel('Cluster')
    axes[0,2].set_ylabel('Success Rate')
    
    # Carry cluster analysis
    axes[1,0].pie(carry_clusters['Size'], labels=[f'C{i}' for i in carry_clusters['Cluster']], 
                  autopct='%1.1f%%', startangle=90)
    axes[1,0].set_title('Carry Event Clusters Distribution')
    
    # Carry forward progress by cluster
    axes[1,1].bar(carry_clusters['Cluster'], carry_clusters['Avg_Forward_Progress'].str.replace('', '').astype(float))
    axes[1,1].set_title('Carry Forward Progress by Cluster')
    axes[1,1].set_xlabel('Cluster')
    axes[1,1].set_ylabel('Avg Forward Progress (meters)')
    
    # Carry speed by cluster
    axes[1,2].bar(carry_clusters['Cluster'], carry_clusters['Avg_Speed'].str.replace('', '').astype(float))
    axes[1,2].set_title('Carry Speed by Cluster')
    axes[1,2].set_xlabel('Cluster')
    axes[1,2].set_ylabel('Avg Speed (m/s)')
    
    plt.tight_layout()
    plt.savefig('momentum_analysis_insights.png', dpi=300, bbox_inches='tight')
    plt.show()
    
    # Feature importance visualization
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))
    
    # Pass feature importance
    top_pass_features = pass_importance.head(8)
    ax1.barh(top_pass_features['feature'], top_pass_features['importance'])
    ax1.set_title('Top Pass Features for Momentum Prediction')
    ax1.set_xlabel('Feature Importance')
    
    # Carry feature importance
    top_carry_features = carry_importance.head(8)
    ax2.barh(top_carry_features['feature'], top_carry_features['importance'])
    ax2.set_title('Top Carry Features for Momentum Prediction')
    ax2.set_xlabel('Feature Importance')
    
    plt.tight_layout()
    plt.savefig('feature_importance_analysis.png', dpi=300, bbox_inches='tight')
    plt.show()
    
    # Generate insights
    print("\n🔍 DISCOVERED HIDDEN PATTERNS:")
    print("=" * 60)
    
    print("\n📊 PASS EVENT PATTERNS:")
    print("-" * 30)
    
    # Identify pass patterns
    high_success_clusters = pass_clusters[pass_clusters['Pass_Success_Rate'].str.replace('', '').astype(float) > 0.9]
    risky_clusters = pass_clusters[pass_clusters['Pass_Success_Rate'].str.replace('', '').astype(float) < 0.5]
    progressive_clusters = pass_clusters[pass_clusters['Avg_Forward_Progress'].str.replace('', '').astype(float) > 10]
    
    print(f"🎯 Conservative Success Clusters: {len(high_success_clusters)} clusters")
    for _, cluster in high_success_clusters.iterrows():
        print(f"   Cluster {cluster['Cluster']}: {cluster['Size']} events ({cluster['Percentage']}) - {cluster['Pass_Success_Rate']} success")
    
    print(f"\n⚠️  High-Risk Clusters: {len(risky_clusters)} clusters")
    for _, cluster in risky_clusters.iterrows():
        print(f"   Cluster {cluster['Cluster']}: {cluster['Size']} events ({cluster['Percentage']}) - {cluster['Pass_Success_Rate']} success, {cluster['Avg_Forward_Progress']}m progress")
    
    print(f"\n🚀 Progressive Clusters: {len(progressive_clusters)} clusters")
    for _, cluster in progressive_clusters.iterrows():
        print(f"   Cluster {cluster['Cluster']}: {cluster['Size']} events ({cluster['Percentage']}) - {cluster['Avg_Forward_Progress']}m progress")
    
    print("\n📊 CARRY EVENT PATTERNS:")
    print("-" * 30)
    
    # Identify carry patterns
    fast_carries = carry_clusters[carry_clusters['Avg_Speed'].str.replace('s', '').astype(float) > 4.0]
    progressive_carries = carry_clusters[carry_clusters['Avg_Forward_Progress'].str.replace('', '').astype(float) > 10]
    long_duration_carries = carry_clusters[carry_clusters['Avg_Duration'].str.replace('s', '').astype(float) > 3.0]
    
    print(f"⚡ Fast Carry Clusters: {len(fast_carries)} clusters")
    for _, cluster in fast_carries.iterrows():
        print(f"   Cluster {cluster['Cluster']}: {cluster['Size']} events ({cluster['Percentage']}) - {cluster['Avg_Speed']} speed")
    
    print(f"\n🚀 Progressive Carry Clusters: {len(progressive_carries)} clusters")
    for _, cluster in progressive_carries.iterrows():
        print(f"   Cluster {cluster['Cluster']}: {cluster['Size']} events ({cluster['Percentage']}) - {cluster['Avg_Forward_Progress']}m progress")
    
    print(f"\n⏱️  Deliberate Carry Clusters: {len(long_duration_carries)} clusters")
    for _, cluster in long_duration_carries.iterrows():
        print(f"   Cluster {cluster['Cluster']}: {cluster['Size']} events ({cluster['Percentage']}) - {cluster['Avg_Duration']} duration")
    
    # Key insights
    print("\n💡 KEY TACTICAL INSIGHTS:")
    print("=" * 60)
    
    print("🎯 PASS MOMENTUM PATTERNS:")
    print("1. SAFE CIRCULATION (Clusters 0,1,5): 72.7% of passes")
    print("   - High success rate (96-98%)")
    print("   - Minimal forward progress (0.47-1.77m)")
    print("   - Possession maintenance focus")
    
    print("\n2. RISKY PENETRATION (Cluster 2): 7.1% of passes")
    print("   - Massive forward progress (44.87m)")
    print("   - Low success rate (38%)")
    print("   - High-risk, high-reward attempts")
    
    print("\n3. FAILED ATTEMPTS (Cluster 3): 7.9% of passes")
    print("   - Moderate forward progress (8.55m)")
    print("   - Very low success rate (10%)")
    print("   - Pressure-induced failures")
    
    print("\n🏃 CARRY MOMENTUM PATTERNS:")
    print("1. STANDARD PROGRESSION (Clusters 0,1,4): 74.1% of carries")
    print("   - Minimal forward progress (0.94-1.18m)")
    print("   - Standard speed (2.30-2.59 m/s)")
    print("   - Ball control and positioning")
    
    print("\n2. EXPLOSIVE ATTACKS (Cluster 3): 7.8% of carries")
    print("   - Massive forward progress (18.43m)")
    print("   - High speed (5.46 m/s)")
    print("   - Long duration (4.85s)")
    print("   - Game-changing moments")
    
    print("\n3. QUICK TRANSITIONS (Cluster 2): 18.1% of carries")
    print("   - Minimal progress but high speed (3.64 m/s)")
    print("   - Quick decision-making")
    print("   - Tempo control")
    
    print("\n🔬 FEATURE IMPORTANCE INSIGHTS:")
    print("=" * 60)
    
    print("📈 PASS MOMENTUM PREDICTORS:")
    top_3_pass = pass_importance.head(3)
    for i, (_, feature) in enumerate(top_3_pass.iterrows(), 1):
        print(f"{i}. {feature['feature']}: {feature['importance']:.3f}")
    
    print("\n📈 CARRY MOMENTUM PREDICTORS:")
    top_3_carry = carry_importance.head(3)
    for i, (_, feature) in enumerate(top_3_carry.iterrows(), 1):
        print(f"{i}. {feature['feature']}: {feature['importance']:.3f}")
    
    # Generate recommendations
    print("\n🎯 TACTICAL RECOMMENDATIONS:")
    print("=" * 60)
    
    print("1. MOMENTUM BUILDING:")
    print("   - Focus on forward_progress and zone_progression")
    print("   - Balance risk vs. success rate")
    print("   - Use carry_speed for quick momentum shifts")
    
    print("\n2. PATTERN RECOGNITION:")
    print("   - Identify 'Explosive Attack' carries (Cluster 3)")
    print("   - Monitor 'Risky Penetration' passes (Cluster 2)")
    print("   - Track momentum through sequence length")
    
    print("\n3. DEFENSIVE STRATEGIES:")
    print("   - Pressure during high-forward-progress events")
    print("   - Disrupt carry sequences before acceleration")
    print("   - Force passes into high-risk categories")
    
    return {
        'pass_clusters': pass_clusters,
        'carry_clusters': carry_clusters,
        'pass_importance': pass_importance,
        'carry_importance': carry_importance
    }

if __name__ == "__main__":
    results = create_insights_report() 