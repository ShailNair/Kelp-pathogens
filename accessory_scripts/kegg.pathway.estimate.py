import argparse
import os
import pandas as pd


def main():
    # Parse command-line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input', required=True, help='Path to input directory containing KO annotation files')
    parser.add_argument('-o', '--output', required=True, help='Path to output directory')
    parser.add_argument('-d', '--pathways', required=True, help='Path to CSV file containing pathway information')
    args = parser.parse_args()

    # Create output directory if it doesn't exist
    if not os.path.exists(args.output):
        os.makedirs(args.output)

    # Read in pathway information
    pathways_df = pd.read_csv(args.pathways)

    # Group pathways by ID and name
    pathways_grouped = pathways_df.groupby(['pathway_id', 'pathway_name'])

    # Loop over KO annotation files
    for filename in os.listdir(args.input):
        if filename.endswith('.txt'):
            input_file = os.path.join(args.input, filename)
            output_file = os.path.join(args.output, os.path.splitext(filename)[0] + '_pathwaycompletion.csv')

            with open(input_file, 'r') as f:
                input_kos = set(line.strip() for line in f)

            results = []

            # Iterate over pathway groups
            for group_key, group_df in pathways_grouped:
                required_kos = set(group_df['ko'].str.split(';').explode())
                present_kos = required_kos & input_kos
                absent_kos = required_kos - input_kos

                if len(required_kos) > 0:
                    completion_pct = len(present_kos) / len(required_kos) * 100
                else:
                    completion_pct = 0

                results.append({
                    'pathway_id': group_key[0],
                    'pathway_name': group_key[1],
                    'completion%': completion_pct,
                    'present': '-'.join(sorted(present_kos)),
                    'absent': '-'.join(sorted(absent_kos))
                })

            results_df = pd.DataFrame(results)
            results_df.to_csv(output_file, index=False)


if __name__ == '__main__':
    main()
