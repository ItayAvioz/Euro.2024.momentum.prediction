import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, r2_score
import warnings
warnings.filterwarnings("ignore")

print("🧪 TESTING MOMENTUM PREDICTION & COMMENTARY GENERATION MODELS")
print("=" * 80)

# Load data
try:
    events_df = pd.read_csv("euro_2024_sample_100_rows.csv")
    print(f"📊 Loaded {len(events_df)} events for testing")
    print(f"📅 Match: {events_df[\"home_team\"].iloc[0]} vs {events_df[\"away_team\"].iloc[0]}")
    print(f"🏟️ Teams: {events_df[\"team_name\"].dropna().unique()}")
except Exception as e:
    print(f"❌ Error loading data: {e}")
    exit()

# Simple Momentum Predictor Class
class MomentumPredictor:
    def __init__(self):
        self.model = RandomForestRegressor(n_estimators=30, random_state=42)
        self.is_trained = False
    
    def extract_features(self, events_df, current_time, team_name):
        start_time = max(0, current_time - 180)
        recent = events_df[
            (events_df["timestamp"] >= start_time) & 
            (events_df["timestamp"] <= current_time)
        ]
        team_events = recent[recent["team_name"] == team_name]
        
        return {
            "total_events": len(team_events),
            "pass_count": len(team_events[team_events["event_type"] == "Pass"]),
            "shot_count": len(team_events[team_events["event_type"] == "Shot"]),
            "carry_count": len(team_events[team_events["event_type"] == "Carry"]),
            "possession_pct": len(team_events) / len(recent) * 100 if len(recent) > 0 else 50,
            "attacking_actions": len(team_events[team_events["event_type"].isin(["Shot", "Dribble", "Carry"])])
        }
    
    def train(self, events_df):
        print("🚀 Training momentum model...")
        events_df["timestamp"] = events_df["minute"] * 60 + events_df["second"]
        
        training_data = []
        teams = events_df["team_name"].dropna().unique()
        
        for time_point in range(180, int(events_df["timestamp"].max()), 60):
            for team in teams:
                features = self.extract_features(events_df, time_point, team)
                momentum = min(10, max(0, 
                    features["attacking_actions"] * 1.5 +
                    features["possession_pct"] * 0.05 +
                    features["shot_count"] * 2.0
                ))
                features["momentum"] = momentum
                training_data.append(features)
        
        df = pd.DataFrame(training_data)
        if len(df) == 0:
            print("❌ No training data")
            return None
        
        self.feature_names = [c for c in df.columns if c != "momentum"]
        X = df[self.feature_names]
        y = df["momentum"]
        
        self.model.fit(X, y)
        self.is_trained = True
        
        y_pred = self.model.predict(X)
        mse = mean_squared_error(y, y_pred)
        r2 = r2_score(y, y_pred)
        
        print(f"✅ Trained! MSE: {mse:.3f}, R²: {r2:.3f}")
        print(f"📊 Features: {len(self.feature_names)}, Samples: {len(df)}")
        return df
    
    def predict(self, events_df, time_point, team):
        if not self.is_trained:
            return 5.0
        features = self.extract_features(events_df, time_point, team)
        X = [features.get(f, 0) for f in self.feature_names]
        return max(0, min(10, self.model.predict([X])[0]))

# Simple Commentary Generator Class
class CommentaryGenerator:
    def __init__(self):
        self.templates = {
            "Pass": {
                "low": ["{player} plays a simple pass", "{player} keeps possession"],
                "high": ["{player} with a brilliant pass!", "Superb ball from {player}!"]
            },
            "Shot": {
                "low": ["{player} shoots from distance", "Effort from {player}"],
                "high": ["{player} SHOOTS! What a strike!", "GOAL ATTEMPT by {player}!"]
            },
            "Carry": {
                "low": ["{player} advances with the ball"],
                "high": ["{player} breaks clear with pace!"]
            }
        }
    
    def generate(self, event, momentum=5):
        event_type = event["event_type"]
        player = event.get("player_name", "Player")
        minute = event.get("minute", 0)
        
        if pd.isna(player):
            player = "the player"
        
        excitement = "high" if (momentum > 6 or minute > 80 or event_type == "Shot") else "low"
        
        if event_type in self.templates:
            templates = self.templates[event_type].get(excitement, 
                       self.templates[event_type].get("low", [f"{player} with a {event_type.lower()}"]))
            commentary = np.random.choice(templates).format(player=player)
        else:
            commentary = f"{player} with a {event_type.lower()}"
        
        return {
            "commentary": commentary,
            "excitement": excitement,
            "momentum": momentum
        }

# Test Model 1: Momentum Prediction
print("\n" + "="*60)
print("🔮 MOMENTUM PREDICTION MODEL")
print("="*60)

momentum_model = MomentumPredictor()
training_data = momentum_model.train(events_df)

if training_data is not None:
    print(f"\n📊 FEATURE IMPORTANCE:")
    importance = dict(zip(momentum_model.feature_names, momentum_model.model.feature_importances_))
    for i, (feature, imp) in enumerate(sorted(importance.items(), key=lambda x: x[1], reverse=True), 1):
        print(f"   {i}. {feature}: {imp:.3f}")
    
    print("\n🎯 MOMENTUM PREDICTIONS:")
    teams = events_df["team_name"].dropna().unique()
    for test_time in [300, 1200, 2700]:
        print(f"\n   At {test_time//60}:{test_time%60:02d}:")
        for team in teams:
            momentum = momentum_model.predict(events_df, test_time, team)
            interpretation = ("🔥 High" if momentum > 7 else "📈 Medium" if momentum > 4 else "📉 Low")
            print(f"      {team}: {momentum:.1f}/10 - {interpretation}")

# Test Model 2: Commentary Generation
print("\n" + "="*60)
print("🎙️ COMMENTARY GENERATION MODEL")
print("="*60)

commentary_model = CommentaryGenerator()

sample_events = []
for event_type in ["Pass", "Shot", "Carry"]:
    matching = events_df[events_df["event_type"] == event_type]
    if not matching.empty:
        sample_events.append(matching.iloc[0])

print("📝 COMMENTARY EXAMPLES:")
for i, event in enumerate(sample_events, 1):
    event_time = event["minute"] * 60 + event["second"]
    momentum = momentum_model.predict(events_df, event_time, event["team_name"]) if momentum_model.is_trained else 5
    
    commentary = commentary_model.generate(event, momentum)
    
    print(f"\n   {i}. {event[\"event_type\"]} EVENT:")
    print(f"      Time: {event[\"minute\"]:02d}:{event[\"second\"]:02d}")
    print(f"      Player: {event[\"player_name\"]}")
    print(f"      Momentum: {momentum:.1f}/10")
    print(f"      Commentary: \"{commentary[\"commentary\"]}\"")
    print(f"      Excitement: {commentary[\"excitement\"].title()}")

print("\n" + "="*80)
print("📊 MODEL PERFORMANCE ANALYSIS")
print("="*80)

print("🔮 MOMENTUM MODEL:")
print("   Algorithm: Random Forest Regressor")
print("   Features: Event counts, possession %, attacking actions")
print("   Window: 3-minute sliding window")
print("   Output: 0-10 momentum score")

print("\n🎙️ COMMENTARY MODEL:")
print("   Algorithm: Template-based with context classification")
print("   Templates: Event-specific with excitement levels")
print("   Context: Momentum-aware excitement calculation")
print("   Output: Natural language commentary")

template_count = sum(len(templates[level]) for templates in commentary_model.templates.values() for level in templates)
print(f"   Total templates: {template_count}")

print("\n🔬 TECHNIQUES USED:")
print("   Momentum: Sliding window, feature engineering, ensemble ML")
print("   Commentary: Template matching, context classification")
print("   Integration: Real-time momentum feeds into commentary excitement")

print("\n✅ MODEL TESTING COMPLETE!")
print("🎯 Successfully demonstrated both models with Euro 2024 data")

