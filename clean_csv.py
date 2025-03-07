import pandas as pd
import glob
import os

# Find the most recent CSV file
csv_files = glob.glob('olx_bikes_*.csv')
latest_csv = max(csv_files, key=os.path.getctime)

print(f"Cleaning file: {latest_csv}")

# Read the CSV
df = pd.read_csv(latest_csv)

# Print initial stats
print(f"\nInitial stats:")
print(f"Total rows: {len(df)}")
print(f"Pages covered: {df['page_number'].min()} to {df['page_number'].max()}")

# Keep only rows up to page 49
df_cleaned = df[df['page_number'] < 50].copy()

# Print final stats
print(f"\nAfter cleaning:")
print(f"Total rows: {len(df_cleaned)}")
print(f"Pages covered: {df_cleaned['page_number'].min()} to {df_cleaned['page_number'].max()}")

# Save to new file
output_file = latest_csv.replace('.csv', '_cleaned.csv')
df_cleaned.to_csv(output_file, index=False)
print(f"\nCleaned data saved to: {output_file}") 