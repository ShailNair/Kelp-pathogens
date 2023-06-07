import sys
import pandas as pd
import os

# Check that the number of arguments passed to the script is at least four
if len(sys.argv) < 4:
    print("Error: not enough arguments passed to the script.")
    print("Usage: python merge_datasets.py input_file1 input_file2 output_dir output_file")
    exit()

# Read the input file paths from the command line
input_file1 = sys.argv[1]
input_file2 = sys.argv[2]

# Read the output directory and file name from the command line
output_dir = sys.argv[3]
output_file = sys.argv[4]

# Construct the full file paths for the input files
input_file1_path = os.path.join(input_file1)
input_file2_path = os.path.join(input_file2)

# Convert the output directory path to an absolute path
output_dir_path = os.path.expanduser(output_dir)

# Read the two datasets into Pandas DataFrames
df1 = pd.read_csv(input_file1_path)
df2 = pd.read_csv(input_file2_path)

# Merge the two datasets based on the values in the first column
merged_df = pd.merge(df1, df2, on=df1.columns[0])

# Save the resulting DataFrame to a CSV file in the output directory
merged_df.to_csv(os.path.join(output_dir_path, output_file))
