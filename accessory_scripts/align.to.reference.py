#!/usr/bin/env python3

import argparse
import os
import subprocess
import sys
import tempfile

# Define command-line arguments
parser = argparse.ArgumentParser(description='Map paired-end reads to a reference genome using bowtie2 and samtools.')
parser.add_argument('--reference', type=str, required=True, help='Path to reference genome.')
parser.add_argument('--R1', type=str, required=True, nargs='+', help='Path to R1 reads.')
parser.add_argument('--R2', type=str, required=True, nargs='+', help='Path to R2 reads.')
parser.add_argument('--output', type=str, required=True, help='Path to output directory.')
parser.add_argument('--threads', type=int, default=1, help='Number of threads to use.')
parser.add_argument('--verbose', action='store_true', help='Print verbose output.')
parser.add_argument('--keep_tmp', action='store_true', help='Keep the temporary directory')
args = parser.parse_args()

# Create temporary directory for intermediate files
tmp_dir = os.path.join(args.output, 'tmp')
os.makedirs(tmp_dir, exist_ok=True)
if args.verbose:
    print(f'Created temporary directory: {tmp_dir}')

# Build index
index_prefix = os.path.join(tmp_dir, 'ref')
cmd = f'bowtie2-build {args.reference} {index_prefix} --threads {args.threads}'
if args.verbose:
    print(f'Running command: {cmd}')
try:
    subprocess.run(cmd, shell=True, check=True)
except subprocess.CalledProcessError as e:
    print(f'Error building index: {e.stderr}', file=sys.stderr)
    sys.exit(1)

# Map reads
for i in range(len(args.R1)):
    r1 = args.R1[i]
    r2 = args.R2[i]
    basename = os.path.splitext(os.path.basename(r1))[0]
    sam_file = os.path.join(tmp_dir, f'{basename}.sam')
    bam_file = os.path.join(tmp_dir, f'{basename}.bam')
    sorted_bam_file = os.path.join(tmp_dir, f'{basename}sort.bam')
    r1_out = os.path.join(args.output, f'{basename}.R1.fq.gz')
    r2_out = os.path.join(args.output, f'{basename}.R2.fq.gz')

    cmd = f'bowtie2 --threads {args.threads} -x {index_prefix} -1 {r1} -2 {r2} -S {sam_file}'
    if args.verbose:
        print(f'Running command: {cmd}')
    try:
        subprocess.run(cmd, shell=True, check=True)
    except subprocess.CalledProcessError as e:
        print(f'Error mapping reads: {e.stderr}', file=sys.stderr)
        sys.exit(1)

    cmd = f'samtools view -F 4 -bS {sam_file} > {bam_file} -@ {args.threads}'
    if args.verbose:
        print(f'Running command: {cmd}')
    try:
        subprocess.run(cmd, shell=True, check=True)
    except subprocess.CalledProcessError as e:
        print(f'Error converting to BAM: {e.stderr}', file=sys.stderr)
        sys.exit(1)

    cmd = f'samtools sort -@ {args.threads} -o {sorted_bam_file} {bam_file}'
    if args.verbose:
        print(f'Running command: {cmd}')
    try:
        subprocess.run(cmd, shell=True, check=True)
    except subprocess.CalledProcessError as e:
        print(f'Error sorting BAM: {e.stderr}', file=sys.stderr)
    cmd = f'samtools index {sorted_bam_file} -@ {args.threads}'
    if args.verbose:
        print(f'Running command: {cmd}')
    try:
        subprocess.run(cmd, shell=True, check=True)
    except subprocess.CalledProcessError as e:
        print(f'Error indexing BAM: {e.stderr}', file=sys.stderr)
        sys.exit(1)
    
    cmd = f'samtools fastq -1 {r1_out} -2 {r2_out} {sorted_bam_file} -@ {args.threads}'
    if args.verbose:
        print(f'Running command: {cmd}')
    try:
        subprocess.run(cmd, shell=True, check=True)
    except subprocess.CalledProcessError as e:
        print(f'Error generating fastq files: {e.stderr}', file=sys.stderr)
        sys.exit(1)

# Remove temporary directory
if not args.keep_tmp:
    cmd = f'rm -rf {tmp_dir}'
    if args.verbose:
        print(f'Running command: {cmd}')
    try:
        subprocess.run(cmd, shell=True, check=True)
    except subprocess.CalledProcessError as e:
        print(f'Error removing temporary directory: {e.stderr}', file=sys.stderr)
        sys.exit(1)
else:
    print(f'Keeping temporary directory: {tmp_dir}')
    
print('Finished mapping reads.')