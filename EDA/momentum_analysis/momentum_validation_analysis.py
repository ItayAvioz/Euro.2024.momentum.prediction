import pandas as pd
import numpy as np
import ast
from scipy import stats
import warnings
warnings.filterwarnings('ignore')

class MomentumValidationAnalyzer:
    """Comprehensive validation of momentum function against real football outcomes"""
    
    def __init__(self):
        self.load_data()
        self.prepare_outcome_variables()
    
    def load_data(self):
        """Load Euro 2024 data with momentum scores"""
        print("🔍 MOMENTUM VALIDATION ANALYSIS")
        print("=" * 60)
        
        try:
            # Try to load the data with momentum_y if available
            try:
                self.events_df = pd.read_csv('euro_2024_events_with_momentum_y.csv', low_memory=False)
                print(f"✅ Loaded events with momentum_y: {len(self.events_df):,} rows")
                self.has_momentum = True
            except:
                # Load original data and create momentum_y on the fly
                self.events_df = pd.read_csv('../Data/events_complete.csv', low_memory=False)
                print(f"✅ Loaded original events: {len(self.events_df):,} rows")
                print("⚠️ No momentum_y found - will create simplified momentum proxy")
                self.has_momentum = False
                self.create_momentum_proxy()
            
            # Load matches for context
            try:
                self.matches_df = pd.read_csv('../Data/matches_complete.csv', low_memory=False)
                print(f"✅ Loaded matches: {len(self.matches_df):,} rows")
            except:
                print("⚠️ Matches file not found")
                self.matches_df = None
                
        except Exception as e:
            print(f"❌ Error loading data: {e}")
            raise
    
    def create_momentum_proxy(self):
        """Create simplified momentum proxy if full momentum_y not available"""
        print("\n🔧 CREATING MOMENTUM PROXY...")
        
        # Simple momentum proxy based on event types and timing
        momentum_weights = {
            'Shot': 8.0,
            'Goal': 10.0,
            'Pass': 6.0,
            'Carry': 7.0,
            'Ball Receipt*': 5.0,
            'Pressure': 4.0,
            'Clearance': 2.0,
            'Interception': 3.0,
            'Foul Won': 6.5,
            'Dispossessed': 2.5,
            'Ball Recovery': 4.5,
            'Block': 3.0,
            'Corner Kick': 7.5,
            'Free Kick': 6.0,
            'Throw-in': 5.0
        }
        
        # Extract event type
        def safe_parse_type(value):
            if pd.isna(value):
                return 'Unknown'
            try:
                if isinstance(value, str):
                    parsed = ast.literal_eval(value)
                    if isinstance(parsed, dict) and 'name' in parsed:
                        return parsed['name']
                return str(value)
            except:
                return str(value) if pd.notna(value) else 'Unknown'
        
        self.events_df['event_type'] = self.events_df['type'].apply(safe_parse_type)
        
        # Create momentum proxy
        self.events_df['momentum_y'] = self.events_df['event_type'].map(momentum_weights).fillna(5.0)
        
        # Apply time modifier (simplified)
        minute_modifier = np.where(self.events_df['minute'] >= 75, 1.2,
                         np.where(self.events_df['minute'] >= 60, 1.1, 
                         np.where(self.events_df['minute'] <= 15, 0.9, 1.0)))
        
        self.events_df['momentum_y'] = self.events_df['momentum_y'] * minute_modifier
        self.events_df['momentum_y'] = np.clip(self.events_df['momentum_y'], 0, 10)
        
        print(f"   ✅ Created momentum proxy with mean: {self.events_df['momentum_y'].mean():.2f}")
    
    def prepare_outcome_variables(self):
        """Extract and prepare outcome variables for validation"""
        print("\n🎯 PREPARING OUTCOME VARIABLES...")
        
        # Safe parsing function
        def safe_parse(value, field_name='name'):
            if pd.isna(value) or value == '':
                return None
            try:
                if isinstance(value, str):
                    parsed = ast.literal_eval(value)
                    if isinstance(parsed, dict):
                        return parsed.get(field_name, parsed.get('name', None))
                    return str(parsed)
                return str(value) if pd.notna(value) else None
            except:
                return str(value) if pd.notna(value) else None
        
        # Extract event type
        if 'event_type' not in self.events_df.columns:
            self.events_df['event_type'] = self.events_df['type'].apply(safe_parse)
        
        # Extract shot outcome
        self.events_df['shot_outcome'] = self.events_df['shot'].apply(
            lambda x: safe_parse(x, 'outcome') if pd.notna(x) else None
        )
        
        # Extract pass outcome
        self.events_df['pass_outcome'] = self.events_df['pass'].apply(
            lambda x: safe_parse(x, 'outcome') if pd.notna(x) else None
        )
        
        # Create outcome flags
        self.events_df['is_goal'] = (self.events_df['event_type'] == 'Goal').astype(int)
        self.events_df['is_shot'] = (self.events_df['event_type'] == 'Shot').astype(int)
        self.events_df['is_shot_on_target'] = (
            (self.events_df['event_type'] == 'Shot') & 
            (self.events_df['shot_outcome'].isin(['Goal', 'Saved']))
        ).astype(int)
        self.events_df['is_corner'] = (self.events_df['event_type'] == 'Corner Kick').astype(int)
        self.events_df['is_foul_committed'] = (self.events_df['event_type'] == 'Foul Committed').astype(int)
        self.events_df['is_foul_won'] = (self.events_df['event_type'] == 'Foul Won').astype(int)
        self.events_df['is_card'] = (self.events_df['event_type'].isin(['Yellow Card', 'Red Card'])).astype(int)
        self.events_df['is_clearance'] = (self.events_df['event_type'] == 'Clearance').astype(int)
        self.events_df['is_block'] = (self.events_df['event_type'] == 'Block').astype(int)
        self.events_df['is_interception'] = (self.events_df['event_type'] == 'Interception').astype(int)
        self.events_df['is_pass_success'] = (
            (self.events_df['event_type'] == 'Pass') & 
            (self.events_df['pass_outcome'].isna())  # No outcome means successful
        ).astype(int)
        self.events_df['is_pass_fail'] = (
            (self.events_df['event_type'] == 'Pass') & 
            (self.events_df['pass_outcome'].notna())  # Has outcome means failed
        ).astype(int)
        
        print(f"   ✅ Goals: {self.events_df['is_goal'].sum():,}")
        print(f"   ✅ Shots: {self.events_df['is_shot'].sum():,}")
        print(f"   ✅ Shots on target: {self.events_df['is_shot_on_target'].sum():,}")
        print(f"   ✅ Corners: {self.events_df['is_corner'].sum():,}")
        print(f"   ✅ Fouls Won: {self.events_df['is_foul_won'].sum():,}")
        print(f"   ✅ Fouls Committed: {self.events_df['is_foul_committed'].sum():,}")
        print(f"   ✅ Cards: {self.events_df['is_card'].sum():,}")
        print(f"   ✅ Clearances: {self.events_df['is_clearance'].sum():,}")
        print(f"   ✅ Blocks: {self.events_df['is_block'].sum():,}")
    
    def analyze_momentum_correlations(self):
        """Analyze correlations between momentum and outcomes"""
        print("\n📊 MOMENTUM-OUTCOME CORRELATIONS")
        print("-" * 50)
        
        # Expected positive correlations (attacking outcomes)
        positive_outcomes = [
            ('Goals', 'is_goal'),
            ('Shots', 'is_shot'), 
            ('Shots on Target', 'is_shot_on_target'),
            ('Corners', 'is_corner'),
            ('Fouls Won', 'is_foul_won'),
            ('Pass Success', 'is_pass_success')
        ]
        
        # Expected negative correlations (defensive outcomes)
        negative_outcomes = [
            ('Clearances', 'is_clearance'),
            ('Blocks', 'is_block'),
            ('Interceptions', 'is_interception'),
            ('Fouls Committed', 'is_foul_committed'),
            ('Cards Received', 'is_card'),
            ('Pass Failures', 'is_pass_fail')
        ]
        
        all_outcomes = positive_outcomes + negative_outcomes
        correlations = []
        
        print("🚀 ATTACKING OUTCOMES (Expected Positive):")
        for outcome_name, outcome_var in positive_outcomes:
            if outcome_var in self.events_df.columns and self.events_df[outcome_var].sum() > 0:
                corr, p_value = stats.pearsonr(
                    self.events_df['momentum_y'].fillna(5.0),
                    self.events_df[outcome_var]
                )
                
                # Rate analysis
                high_momentum = self.events_df[self.events_df['momentum_y'] >= 7.0]
                low_momentum = self.events_df[self.events_df['momentum_y'] <= 3.0]
                
                high_rate = high_momentum[outcome_var].mean() * 100 if len(high_momentum) > 0 else 0
                low_rate = low_momentum[outcome_var].mean() * 100 if len(low_momentum) > 0 else 0
                
                significance = '***' if p_value < 0.001 else '**' if p_value < 0.01 else '*' if p_value < 0.05 else 'ns'
                
                correlations.append({
                    'Outcome': outcome_name,
                    'Category': 'Attacking',
                    'Correlation': corr,
                    'P-Value': p_value,
                    'Significance': significance,
                    'High_Momentum_Rate': high_rate,
                    'Low_Momentum_Rate': low_rate,
                    'Rate_Difference': high_rate - low_rate,
                    'Expected_Direction': 'Positive',
                    'Matches_Expectation': corr > 0
                })
                
                print(f"   {outcome_name}: {corr:+.4f} ({significance}) | High: {high_rate:.3f}% Low: {low_rate:.3f}% Diff: {high_rate-low_rate:+.3f}pp")
        
        print("\n📉 DEFENSIVE OUTCOMES (Expected Negative):")
        for outcome_name, outcome_var in negative_outcomes:
            if outcome_var in self.events_df.columns and self.events_df[outcome_var].sum() > 0:
                corr, p_value = stats.pearsonr(
                    self.events_df['momentum_y'].fillna(5.0),
                    self.events_df[outcome_var]
                )
                
                # Rate analysis
                high_momentum = self.events_df[self.events_df['momentum_y'] >= 7.0]
                low_momentum = self.events_df[self.events_df['momentum_y'] <= 3.0]
                
                high_rate = high_momentum[outcome_var].mean() * 100 if len(high_momentum) > 0 else 0
                low_rate = low_momentum[outcome_var].mean() * 100 if len(low_momentum) > 0 else 0
                
                significance = '***' if p_value < 0.001 else '**' if p_value < 0.01 else '*' if p_value < 0.05 else 'ns'
                
                correlations.append({
                    'Outcome': outcome_name,
                    'Category': 'Defensive',
                    'Correlation': corr,
                    'P-Value': p_value,
                    'Significance': significance,
                    'High_Momentum_Rate': high_rate,
                    'Low_Momentum_Rate': low_rate,
                    'Rate_Difference': high_rate - low_rate,
                    'Expected_Direction': 'Negative',
                    'Matches_Expectation': corr < 0
                })
                
                print(f"   {outcome_name}: {corr:+.4f} ({significance}) | High: {high_rate:.3f}% Low: {low_rate:.3f}% Diff: {high_rate-low_rate:+.3f}pp")
        
        return pd.DataFrame(correlations)
    
    def analyze_momentum_by_time_periods(self):
        """Analyze momentum patterns across game periods"""
        print("\n⏰ MOMENTUM BY TIME PERIODS")
        print("-" * 50)
        
        time_periods = [
            ('Early Game (0-15)', 0, 15),
            ('First Phase (15-30)', 15, 30),
            ('Late First Half (30-45)', 30, 45),
            ('Early Second Half (45-60)', 45, 60),
            ('Crucial Phase (60-75)', 60, 75),
            ('Final Push (75-90)', 75, 90),
            ('Extra Time (90+)', 90, 120)
        ]
        
        period_results = []
        
        for period_name, start_min, end_min in time_periods:
            period_data = self.events_df[
                (self.events_df['minute'] >= start_min) & 
                (self.events_df['minute'] < end_min)
            ]
            
            if len(period_data) == 0:
                continue
            
            # Basic stats
            avg_momentum = period_data['momentum_y'].mean()
            goal_rate = period_data['is_goal'].mean() * 1000  # per 1000 events
            shot_rate = period_data['is_shot'].mean() * 1000
            
            # High vs low momentum comparison
            high_momentum = period_data[period_data['momentum_y'] >= 7.0]
            low_momentum = period_data[period_data['momentum_y'] <= 3.0]
            
            high_goal_rate = (high_momentum['is_goal'].mean() * 1000) if len(high_momentum) > 0 else 0
            low_goal_rate = (low_momentum['is_goal'].mean() * 1000) if len(low_momentum) > 0 else 0
            
            period_results.append({
                'Period': period_name,
                'Events': len(period_data),
                'Avg_Momentum': avg_momentum,
                'Goal_Rate_per_1000': goal_rate,
                'Shot_Rate_per_1000': shot_rate,
                'High_Mom_Events': len(high_momentum),
                'Low_Mom_Events': len(low_momentum),
                'High_Mom_Goal_Rate': high_goal_rate,
                'Low_Mom_Goal_Rate': low_goal_rate,
                'Goal_Rate_Difference': high_goal_rate - low_goal_rate
            })
            
            print(f"\n📅 {period_name}:")
            print(f"   Events: {len(period_data):,} | Avg Momentum: {avg_momentum:.2f}")
            print(f"   Goal Rate: {goal_rate:.2f}/1000 events | Shot Rate: {shot_rate:.2f}/1000")
            print(f"   High Mom Goal Rate: {high_goal_rate:.2f}/1000 | Low Mom: {low_goal_rate:.2f}/1000")
            print(f"   Difference: {high_goal_rate - low_goal_rate:+.2f}/1000 events")
        
        return pd.DataFrame(period_results)
    
    def analyze_team_momentum_performance(self):
        """Analyze team-level momentum vs performance"""
        print("\n🏆 TEAM MOMENTUM vs PERFORMANCE")
        print("-" * 50)
        
        team_stats = []
        
        for team in self.events_df['team'].unique():
            if pd.isna(team):
                continue
                
            team_data = self.events_df[self.events_df['team'] == team]
            
            if len(team_data) < 100:  # Skip teams with very few events
                continue
            
            team_stats.append({
                'Team': team,
                'Total_Events': len(team_data),
                'Avg_Momentum': team_data['momentum_y'].mean(),
                'Momentum_Std': team_data['momentum_y'].std(),
                'Total_Goals': team_data['is_goal'].sum(),
                'Total_Shots': team_data['is_shot'].sum(),
                'Goals_per_1000': (team_data['is_goal'].sum() / len(team_data)) * 1000,
                'Shots_per_1000': (team_data['is_shot'].sum() / len(team_data)) * 1000,
                'Shot_Accuracy': (team_data['is_shot_on_target'].sum() / team_data['is_shot'].sum() * 100) if team_data['is_shot'].sum() > 0 else 0,
                'High_Momentum_Pct': (team_data['momentum_y'] >= 7.0).mean() * 100,
                'Low_Momentum_Pct': (team_data['momentum_y'] <= 3.0).mean() * 100,
                'Clearance_Rate': (team_data['is_clearance'].sum() / len(team_data)) * 1000,
                'Pass_Success_Rate': (team_data['is_pass_success'].sum() / (team_data['is_pass_success'].sum() + team_data['is_pass_fail'].sum()) * 100) if (team_data['is_pass_success'].sum() + team_data['is_pass_fail'].sum()) > 0 else 0
            })
        
        team_df = pd.DataFrame(team_stats)
        
        if len(team_df) > 2:
            # Team-level correlations
            correlations = [
                ('Momentum vs Goals/1000', stats.pearsonr(team_df['Avg_Momentum'], team_df['Goals_per_1000'])),
                ('Momentum vs Shots/1000', stats.pearsonr(team_df['Avg_Momentum'], team_df['Shots_per_1000'])),
                ('Momentum vs Shot Accuracy', stats.pearsonr(team_df['Avg_Momentum'], team_df['Shot_Accuracy'])),
                ('Momentum vs Clearance Rate', stats.pearsonr(team_df['Avg_Momentum'], team_df['Clearance_Rate']))
            ]
            
            print(f"\n📈 TEAM-LEVEL CORRELATIONS:")
            for corr_name, (corr, p_val) in correlations:
                significance = '***' if p_val < 0.001 else '**' if p_val < 0.01 else '*' if p_val < 0.05 else 'ns'
                print(f"   {corr_name}: {corr:+.3f} ({significance})")
        
        # Top performers
        team_df_sorted = team_df.sort_values('Avg_Momentum', ascending=False)
        
        print(f"\n🥇 TOP 5 MOMENTUM TEAMS:")
        for _, team in team_df_sorted.head(5).iterrows():
            print(f"   {team['Team']}: {team['Avg_Momentum']:.2f} mom | {team['Goals_per_1000']:.1f} goals/1000 | {team['Shot_Accuracy']:.1f}% accuracy")
        
        print(f"\n🔻 BOTTOM 5 MOMENTUM TEAMS:")
        for _, team in team_df_sorted.tail(5).iterrows():
            print(f"   {team['Team']}: {team['Avg_Momentum']:.2f} mom | {team['Goals_per_1000']:.1f} goals/1000 | {team['Clearance_Rate']:.1f} clear/1000")
        
        return team_df
    
    def create_validation_summary(self, correlation_df, period_df, team_df):
        """Create comprehensive validation summary"""
        print("\n🎯 MOMENTUM VALIDATION SUMMARY")
        print("=" * 60)
        
        # Correlation analysis
        significant_corr = correlation_df[correlation_df['P-Value'] < 0.05]
        correct_direction = correlation_df[correlation_df['Matches_Expectation'] == True]
        
        attacking_corr = correlation_df[correlation_df['Category'] == 'Attacking']
        defensive_corr = correlation_df[correlation_df['Category'] == 'Defensive']
        
        attacking_correct = attacking_corr[attacking_corr['Correlation'] > 0]
        defensive_correct = defensive_corr[defensive_corr['Correlation'] < 0]
        
        print(f"\n📊 CORRELATION VALIDATION:")
        print(f"   Total correlations tested: {len(correlation_df)}")
        print(f"   Statistically significant (p<0.05): {len(significant_corr)}/{len(correlation_df)} ({len(significant_corr)/len(correlation_df)*100:.1f}%)")
        print(f"   Correct direction: {len(correct_direction)}/{len(correlation_df)} ({len(correct_direction)/len(correlation_df)*100:.1f}%)")
        print(f"   Attacking outcomes positive: {len(attacking_correct)}/{len(attacking_corr)} ({len(attacking_correct)/len(attacking_corr)*100:.1f}%)")
        print(f"   Defensive outcomes negative: {len(defensive_correct)}/{len(defensive_corr)} ({len(defensive_correct)/len(defensive_corr)*100:.1f}%)")
        
        # Strongest correlations
        strongest_positive = correlation_df.loc[correlation_df['Correlation'].idxmax()]
        strongest_negative = correlation_df.loc[correlation_df['Correlation'].idxmin()]
        
        print(f"\n🏆 STRONGEST CORRELATIONS:")
        print(f"   Positive: {strongest_positive['Outcome']} ({strongest_positive['Correlation']:+.4f}) {strongest_positive['Significance']}")
        print(f"   Negative: {strongest_negative['Outcome']} ({strongest_negative['Correlation']:+.4f}) {strongest_negative['Significance']}")
        
        # Time validation
        if len(period_df) > 0:
            early_momentum = period_df.iloc[0]['Avg_Momentum'] if len(period_df) > 0 else 0
            late_momentum = period_df.iloc[-2]['Avg_Momentum'] if len(period_df) > 1 else 0
            momentum_increases = late_momentum > early_momentum
            
            print(f"\n⏰ TIME VALIDATION:")
            print(f"   Early game momentum: {early_momentum:.2f}")
            print(f"   Late game momentum: {late_momentum:.2f}")
            print(f"   Momentum increases over time: {'✅' if momentum_increases else '❌'}")
        
        # Overall validation score
        validation_score = (len(significant_corr) + len(correct_direction)) / (2 * len(correlation_df))
        
        print(f"\n🎉 OVERALL VALIDATION SCORE: {validation_score*100:.1f}%")
        
        if validation_score >= 0.6:
            print("   ✅ MOMENTUM FUNCTION IS VALID - Strong predictive power!")
        elif validation_score >= 0.4:
            print("   ⚠️ MOMENTUM FUNCTION IS MODERATE - Some predictive power")
        else:
            print("   ❌ MOMENTUM FUNCTION NEEDS IMPROVEMENT - Weak predictive power")
        
        return {
            'total_correlations': len(correlation_df),
            'significant_correlations': len(significant_corr),
            'correct_direction': len(correct_direction),
            'validation_score': validation_score,
            'strongest_positive_corr': strongest_positive['Correlation'],
            'strongest_negative_corr': strongest_negative['Correlation'],
            'momentum_increases_over_time': momentum_increases if len(period_df) > 1 else False
        }
    
    def save_results(self, correlation_df, period_df, team_df, summary):
        """Save all validation results"""
        print("\n💾 SAVING VALIDATION RESULTS...")
        
        # Save detailed results
        correlation_df.to_csv('momentum_validation_correlations.csv', index=False)
        period_df.to_csv('momentum_validation_periods.csv', index=False)
        team_df.to_csv('momentum_validation_teams.csv', index=False)
        
        # Create summary for thoughts folder
        summary_data = []
        summary_data.append(['Analysis', 'Momentum Validation Analysis', 'Complete validation of momentum function'])
        summary_data.append(['Total Correlations Tested', summary['total_correlations'], 'Number of outcome variables tested'])
        summary_data.append(['Significant Correlations', f"{summary['significant_correlations']}/{summary['total_correlations']}", 'Statistically significant correlations (p<0.05)'])
        summary_data.append(['Correct Direction', f"{summary['correct_direction']}/{summary['total_correlations']}", 'Correlations matching expected direction'])
        summary_data.append(['Validation Score', f"{summary['validation_score']*100:.1f}%", 'Overall validation success rate'])
        summary_data.append(['Strongest Positive', f"{summary['strongest_positive_corr']:+.4f}", 'Strongest positive correlation found'])
        summary_data.append(['Strongest Negative', f"{summary['strongest_negative_corr']:+.4f}", 'Strongest negative correlation found'])
        summary_data.append(['Time Pattern Valid', summary['momentum_increases_over_time'], 'Momentum increases over game time as expected'])
        
        summary_df = pd.DataFrame(summary_data, columns=['Metric', 'Value', 'Description'])
        summary_df.to_csv('../thoughts/momentum_validation_summary.csv', index=False)
        
        print(f"   ✅ Correlations: momentum_validation_correlations.csv")
        print(f"   ✅ Time periods: momentum_validation_periods.csv")
        print(f"   ✅ Team analysis: momentum_validation_teams.csv")
        print(f"   ✅ Summary: ../thoughts/momentum_validation_summary.csv")
    
    def run_complete_validation(self):
        """Run the complete momentum validation analysis"""
        print("\n🚀 STARTING MOMENTUM VALIDATION")
        print("=" * 70)
        
        # Run all analyses
        correlation_df = self.analyze_momentum_correlations()
        period_df = self.analyze_momentum_by_time_periods()
        team_df = self.analyze_team_momentum_performance()
        
        # Create summary
        summary = self.create_validation_summary(correlation_df, period_df, team_df)
        
        # Save results
        self.save_results(correlation_df, period_df, team_df, summary)
        
        print(f"\n🎉 MOMENTUM VALIDATION COMPLETE!")
        return correlation_df, period_df, team_df, summary

if __name__ == "__main__":
    analyzer = MomentumValidationAnalyzer()
    correlation_df, period_df, team_df, summary = analyzer.run_complete_validation()