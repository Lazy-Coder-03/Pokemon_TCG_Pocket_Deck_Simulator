import os
import glob
import pandas as pd

data_folder = r'data'
output_file = 'ALL_SETS.csv'

# Get all CSV files in the folder, sorted alphabetically
csv_files = sorted(glob.glob(os.path.join(data_folder, '*.csv')))

# Read and concatenate all CSVs
dfs = [pd.read_csv(f) for f in csv_files]
combined_df = pd.concat(dfs, ignore_index=True)

# Write to output file
combined_df.to_csv(output_file, index=False)
print(f'Combined {len(csv_files)} files into {output_file}')