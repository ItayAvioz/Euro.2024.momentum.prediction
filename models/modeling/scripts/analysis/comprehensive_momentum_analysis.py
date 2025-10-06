#!/usr/bin/env python3
"""
Comprehensive Momentum Analysis - Differential Sign + Directional Accuracy
Combines differential sign analysis with directional accuracy for ARIMAX momentum→change model

Author: AI Assistant
Date: August 2024
"""

import pandas as pd
import numpy as np
import warnings
warnings.filterwarnings('ignore')

class ComprehensiveMomentumAnalyzer:
    """
    Comprehensive analysis combining:
    1. Differential Sign Analysis (Team X vs Team Y comparison)
    2. Directional Accuracy (Individual momentum change trends)
    3. Contextual Interpretation (Sign + Direction meaning)
    """
    
    def __init__(self):
        self.load_data()
        self.differential_results = []
        self.directional_results = []
        
    def load_data(self):
        """Load ARIMAX momentum→change predictions only"""
        print("🎯 COMPREHENSIVE MOMENTUM ANALYSIS")
        print("=" * 70)
        
        # Load all ARIMAX predictions
        self.df = pd.read_csv('../outputs/predictions/arimax_predictions.csv')
        
        # Filter for momentum_to_change_arimax model only
        self.arimax_data = self.df[self.df['model_type'] == 'momentum_to_change_arimax'].copy()
        
        print(f"✅ Loaded ARIMAX momentum→change predictions: {len(self.arimax_data):,} records")
        print(f"📊 Games covered: {self.arimax_data['game_id'].nunique()}")
        print(f"👥 Teams analyzed: {self.arimax_data['team'].nunique()}")
        
    def analyze_differential_signs(self):
        """
        Analyze differential signs using the 6-case framework:
        1. Positive - Positive > 0: Team X more positive
        2. Positive - Positive < 0: Team Y more positive  
        3. Positive - Negative > 0: Team X positive vs Team Y negative (always X wins)
        4. Negative - Positive < 0: Team Y positive vs Team X negative (always Y wins)
        5. Negative - Negative > 0: Team X less negative
        6. Negative - Negative < 0: Team Y less negative
        """
        print(f"\n🔍 DIFFERENTIAL SIGN ANALYSIS")
        print("=" * 50)
        
        # Group by game_id and minutes_prediction to get team pairs
        grouped = self.arimax_data.groupby(['game_id', 'minutes_prediction'])
        
        for (game_id, minute_window), window_data in grouped:
            if len(window_data) != 2:
                continue  # Skip windows without exactly 2 teams
                
            # Sort teams alphabetically for consistent ordering
            window_data = window_data.sort_values('team').reset_index(drop=True)
            
            team_x = window_data['team'].iloc[0]
            team_y = window_data['team'].iloc[1]
            
            # Actual and predicted momentum changes
            team_x_actual = window_data['actual_value'].iloc[0]
            team_y_actual = window_data['actual_value'].iloc[1]
            team_x_pred = window_data['prediction_value'].iloc[0]
            team_y_pred = window_data['prediction_value'].iloc[1]
            
            # Calculate differentials: Team X - Team Y
            actual_diff = team_x_actual - team_y_actual
            pred_diff = team_x_pred - team_y_pred
            
            # Determine case types based on momentum change signs
            actual_case = self.classify_differential_case(team_x_actual, team_y_actual)
            pred_case = self.classify_differential_case(team_x_pred, team_y_pred)
            
            # Calculate signs
            actual_sign = np.sign(actual_diff)
            pred_sign = np.sign(pred_diff)
            
            # Check if signs match
            signs_match = actual_sign == pred_sign
            
            # Football interpretation
            actual_interpretation = self.interpret_differential(team_x_actual, team_y_actual, actual_diff)
            pred_interpretation = self.interpret_differential(team_x_pred, team_y_pred, pred_diff)
            
            self.differential_results.append({
                'game_id': game_id,
                'window': minute_window,
                'minute_start': window_data['minute_start'].iloc[0],
                'team_x': team_x,
                'team_y': team_y,
                'team_x_actual': team_x_actual,
                'team_y_actual': team_y_actual,
                'team_x_pred': team_x_pred,
                'team_y_pred': team_y_pred,
                'actual_diff': actual_diff,
                'pred_diff': pred_diff,
                'actual_sign': actual_sign,
                'pred_sign': pred_sign,
                'signs_match': signs_match,
                'actual_case': actual_case,
                'pred_case': pred_case,
                'actual_interpretation': actual_interpretation,
                'pred_interpretation': pred_interpretation,
                'interpretation_match': actual_interpretation == pred_interpretation
            })
    
    def classify_differential_case(self, team_x_change, team_y_change):
        """
        Classify the differential case based on momentum change signs
        Returns: pos_pos, pos_neg, neg_pos, neg_neg
        """
        if team_x_change >= 0 and team_y_change >= 0:
            return "pos_pos"
        elif team_x_change >= 0 and team_y_change < 0:
            return "pos_neg"
        elif team_x_change < 0 and team_y_change >= 0:
            return "neg_pos"
        else:  # both negative
            return "neg_neg"
    
    def interpret_differential(self, team_x_change, team_y_change, differential):
        """
        Interpret the differential result in football context
        """
        if differential > 0:
            if team_x_change >= 0 and team_y_change >= 0:
                return "team_x_more_positive"
            elif team_x_change >= 0 and team_y_change < 0:
                return "team_x_positive_vs_team_y_negative"
            else:  # both negative
                return "team_x_less_negative"
        elif differential < 0:
            if team_x_change >= 0 and team_y_change >= 0:
                return "team_y_more_positive"
            elif team_x_change < 0 and team_y_change >= 0:
                return "team_y_positive_vs_team_x_negative"
            else:  # both negative
                return "team_y_less_negative"
        else:
            return "teams_equal"
    
    def analyze_directional_accuracy(self):
        """
        Analyze directional accuracy for individual teams with momentum context
        """
        print(f"\n📈 DIRECTIONAL ACCURACY ANALYSIS")
        print("=" * 50)
        
        # Group by game_id and team for time series analysis
        team_groups = self.arimax_data.groupby(['game_id', 'team'])
        
        for (game_id, team), team_data in team_groups:
            if len(team_data) < 2:
                continue  # Need at least 2 points for direction analysis
                
            # Sort by minute_start to ensure chronological order
            team_data = team_data.sort_values('minute_start').reset_index(drop=True)
            
            actual_values = team_data['actual_value'].values
            pred_values = team_data['prediction_value'].values
            
            # Calculate trends (differences between consecutive points)
            actual_trends = np.diff(actual_values)
            pred_trends = np.diff(pred_values)
            
            # Calculate directional accuracy
            actual_directions = actual_trends > 0  # True = increasing, False = decreasing
            pred_directions = pred_trends > 0
            
            direction_matches = actual_directions == pred_directions
            directional_accuracy = np.mean(direction_matches)
            
            # Analyze each trend with momentum context
            for i in range(len(actual_trends)):
                minute_start = team_data['minute_start'].iloc[i]
                
                # Actual momentum change values (before and after)
                momentum_change_before = actual_values[i]  # Actual momentum change at time t
                momentum_change_after = actual_values[i + 1]  # Actual momentum change at time t+1
                
                # Predicted momentum change values (before and after)  
                pred_momentum_change_before = pred_values[i]  # Predicted momentum change at time t
                pred_momentum_change_after = pred_values[i + 1]  # Predicted momentum change at time t+1
                
                # Trends (change in momentum change)
                actual_change = actual_trends[i]  # Change in momentum change (actual)
                pred_change = pred_trends[i]  # Change in momentum change (predicted)
                
                # Context classification based on actual momentum change level
                momentum_context = self.classify_momentum_context(momentum_change_before, momentum_change_after)
                
                # Directional interpretation
                actual_dir_interpretation = self.interpret_direction(momentum_change_before, actual_change)
                pred_dir_interpretation = self.interpret_direction(pred_momentum_change_before, pred_change)
                
                self.directional_results.append({
                    'game_id': game_id,
                    'team': team,
                    'window_start': minute_start,
                    'momentum_change_before_actual': momentum_change_before,
                    'momentum_change_after_actual': momentum_change_after, 
                    'momentum_change_before_pred': pred_momentum_change_before,
                    'momentum_change_after_pred': pred_momentum_change_after,
                    'actual_change_in_change': actual_change,
                    'pred_change_in_change': pred_change,
                    'actual_direction': actual_directions[i],
                    'pred_direction': pred_directions[i],
                    'direction_match': direction_matches[i],
                    'momentum_context': momentum_context,
                    'actual_interpretation': actual_dir_interpretation,
                    'pred_interpretation': pred_dir_interpretation,
                    'interpretation_match': actual_dir_interpretation == pred_dir_interpretation
                })
    
    def classify_momentum_context(self, momentum_before, momentum_after):
        """Classify the momentum context for better interpretation"""
        if momentum_before > 0.5:
            return "high_positive"
        elif momentum_before > 0:
            return "building"
        elif momentum_before > -0.5:
            return "declining"
        else:
            return "crisis"
    
    def interpret_direction(self, momentum_before, change):
        """
        Interpret direction change in football context based on momentum level
        """
        if change > 0:  # Increasing trend
            if momentum_before >= 0:
                return "accelerating_gains"
            else:
                return "recovery"
        elif change < 0:  # Decreasing trend
            if momentum_before >= 0:
                return "slowing_gains"
            else:
                return "accelerating_decline"
        else:
            return "stable"
    
    def calculate_accuracy_metrics(self):
        """Calculate comprehensive accuracy metrics"""
        print(f"\n📊 ACCURACY RESULTS")
        print("=" * 50)
        
        # Convert to DataFrames
        diff_df = pd.DataFrame(self.differential_results)
        dir_df = pd.DataFrame(self.directional_results)
        
        results = {}
        
        # Overall Differential Sign Accuracy
        if len(diff_df) > 0:
            results['total_game_windows'] = len(diff_df)
            results['differential_sign_accuracy'] = diff_df['signs_match'].mean()
            results['differential_interpretation_accuracy'] = diff_df['interpretation_match'].mean()
            
            # Accuracy by case type
            case_accuracy = diff_df.groupby('actual_case')['signs_match'].agg(['count', 'mean']).round(4)
            results['accuracy_by_case'] = case_accuracy.to_dict()
            
            # Interpretation accuracy by case
            interp_accuracy = diff_df.groupby('actual_case')['interpretation_match'].agg(['count', 'mean']).round(4)
            results['interpretation_accuracy_by_case'] = interp_accuracy.to_dict()
        
        # Overall Directional Accuracy
        if len(dir_df) > 0:
            results['total_directional_predictions'] = len(dir_df)
            results['directional_accuracy'] = dir_df['direction_match'].mean()
            results['directional_interpretation_accuracy'] = dir_df['interpretation_match'].mean()
            
            # Accuracy by momentum context
            context_accuracy = dir_df.groupby('momentum_context')['direction_match'].agg(['count', 'mean']).round(4)
            results['accuracy_by_context'] = context_accuracy.to_dict()
            
            # Interpretation accuracy by context
            context_interp = dir_df.groupby('momentum_context')['interpretation_match'].agg(['count', 'mean']).round(4)
            results['interpretation_accuracy_by_context'] = context_interp.to_dict()
        
        return results, diff_df, dir_df
    
    def print_results(self, results):
        """Print comprehensive results"""
        print(f"\n🎯 COMPREHENSIVE RESULTS SUMMARY")
        print("=" * 70)
        
        # Differential Sign Results
        if 'differential_sign_accuracy' in results:
            print(f"\n📊 DIFFERENTIAL SIGN ANALYSIS:")
            print(f"   Game Windows Analyzed: {results['total_game_windows']:,}")
            print(f"   Sign Accuracy: {results['differential_sign_accuracy']:.4f} ({results['differential_sign_accuracy']*100:.2f}%)")
            print(f"   Interpretation Accuracy: {results['differential_interpretation_accuracy']:.4f} ({results['differential_interpretation_accuracy']*100:.2f}%)")
            
            print(f"\n   📈 Accuracy by Case Type:")
            for case_type, metrics in results['accuracy_by_case']['mean'].items():
                count = results['accuracy_by_case']['count'][case_type]
                print(f"      {case_type}: {metrics:.4f} ({metrics*100:.2f}%) - {count} windows")
        
        # Directional Accuracy Results
        if 'directional_accuracy' in results:
            print(f"\n📈 DIRECTIONAL ACCURACY ANALYSIS:")
            print(f"   Predictions Analyzed: {results['total_directional_predictions']:,}")
            print(f"   Direction Accuracy: {results['directional_accuracy']:.4f} ({results['directional_accuracy']*100:.2f}%)")
            print(f"   Interpretation Accuracy: {results['directional_interpretation_accuracy']:.4f} ({results['directional_interpretation_accuracy']*100:.2f}%)")
            
            print(f"\n   🎯 Accuracy by Momentum Context:")
            for context, metrics in results['accuracy_by_context']['mean'].items():
                count = results['accuracy_by_context']['count'][context]
                print(f"      {context}: {metrics:.4f} ({metrics*100:.2f}%) - {count} predictions")
    
    def save_results(self, diff_df, dir_df):
        """Save detailed results to CSV files"""
        print(f"\n💾 SAVING RESULTS")
        print("=" * 30)
        
        # Save differential analysis
        diff_output_path = '../outputs/comprehensive_differential_analysis.csv'
        diff_df.to_csv(diff_output_path, index=False)
        print(f"✅ Differential analysis saved: {diff_output_path}")
        
        # Save directional analysis  
        dir_output_path = '../outputs/comprehensive_directional_analysis.csv'
        dir_df.to_csv(dir_output_path, index=False)
        print(f"✅ Directional analysis saved: {dir_output_path}")
        
        return diff_output_path, dir_output_path
    
    def run_comprehensive_analysis(self):
        """Run complete analysis pipeline"""
        # Run analyses
        self.analyze_differential_signs()
        self.analyze_directional_accuracy()
        
        # Calculate metrics
        results, diff_df, dir_df = self.calculate_accuracy_metrics()
        
        # Print results
        self.print_results(results)
        
        # Save results
        diff_path, dir_path = self.save_results(diff_df, dir_df)
        
        print(f"\n✅ COMPREHENSIVE ANALYSIS COMPLETED!")
        print(f"   📊 Differential results: {diff_path}")
        print(f"   📈 Directional results: {dir_path}")
        
        return results, diff_df, dir_df

def main():
    """Main execution function"""
    analyzer = ComprehensiveMomentumAnalyzer()
    results, diff_df, dir_df = analyzer.run_comprehensive_analysis()
    
    print(f"\n🎯 KEY INSIGHTS:")
    print(f"   • Differential Sign Accuracy measures team-vs-team momentum advantage prediction")
    print(f"   • Directional Accuracy measures individual team momentum trend prediction") 
    print(f"   • Interpretation Accuracy shows football context understanding")
    print(f"   • Context-aware analysis reveals where model performs best/worst")

if __name__ == "__main__":
    main()
