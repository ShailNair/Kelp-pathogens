import argparse
import os

def combine_cazy_bins(input_dir, output_file):
    combined_data = {}

    # Traverse through each bin directory
    for bin_folder in os.listdir(input_dir):
        bin_path = os.path.join(input_dir, bin_folder)
        overview_path = os.path.join(bin_path, "overview.txt")

        # Read overview.txt file
        with open(overview_path, 'r') as overview_file:
            for line in overview_file:
                if not line.startswith("Gene ID"):
                    gene_id, _, hmmer, ecamie, diamond, num_tools = line.strip().split('\t')

                    # Keep only annotations predicted by at least two tools
                    if int(num_tools) >= 2:
                        combined_data[gene_id] = (hmmer, ecamie, diamond, num_tools)

    # Write combined data to the output file
    with open(output_file, 'w') as output:
        output.write("Gene ID\tHMMER\teCAMI\tDIAMOND\t#ofTools\n")
        for gene_id, annotations in combined_data.items():
            output.write(f"{gene_id}\t{annotations[0]}\t{annotations[1]}\t{annotations[2]}\t{annotations[3]}\n")

    print("Combining complete.")

if __name__ == "__main__":
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Combine CAZy bin files")
    parser.add_argument("-i", "--input", type=str, help="Path to input directory containing bin directories")
    parser.add_argument("-o", "--output", type=str, help="Path to output file")
    args = parser.parse_args()

    # Combine CAZy bin files
    combine_cazy_bins(args.input, args.output)
