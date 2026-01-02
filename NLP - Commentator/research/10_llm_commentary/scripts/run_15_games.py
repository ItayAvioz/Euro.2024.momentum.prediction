"""Run 15 games: 10 main + 5 random."""
import subprocess
import sys
import os

# Change to scripts directory
os.chdir(os.path.dirname(os.path.abspath(__file__)))

# 10 main games we've been testing
main_games = [
    ("Germany", "Scotland"),
    ("Netherlands", "Turkey"),
    ("England", "Switzerland"),
    ("Spain", "England"),
    ("Portugal", "France"),
    ("Germany", "Denmark"),
    ("France", "Belgium"),
    ("Spain", "Germany"),
    ("Austria", "Turkey"),
    ("Romania", "Netherlands"),
]

# 5 random additional games
random_games = [
    ("Italy", "Albania"),
    ("Slovenia", "Serbia"),
    ("England", "Serbia"),
    ("Croatia", "Albania"),
    ("Switzerland", "Germany"),
]

all_games = main_games + random_games

print("=" * 70)
print(f"RUNNING {len(all_games)} GAMES")
print("=" * 70)

for i, (home, away) in enumerate(all_games, 1):
    print(f"\n[{i}/{len(all_games)}] {home} vs {away}")
    print("-" * 50)
    
    result = subprocess.run(
        [sys.executable, "batch_generate_v6.py", "--home", home, "--away", away],
        capture_output=False
    )
    
    if result.returncode != 0:
        print(f"[WARN] {home} vs {away} may have had issues")

print("\n" + "=" * 70)
print("ALL GAMES COMPLETE!")
print("=" * 70)

