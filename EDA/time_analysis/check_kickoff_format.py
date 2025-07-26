import pandas as pd

# Load the data
matches = pd.read_csv('../Data/matches_complete.csv')

print("Kickoff samples:")
print(matches['kick_off'].head(10))

print("\nUnique kickoff values:")
print(matches['kick_off'].unique()[:10])

print("\nData types:")
print(matches['kick_off'].dtype)

print("\nColumn names:")
print(matches.columns.tolist()) 