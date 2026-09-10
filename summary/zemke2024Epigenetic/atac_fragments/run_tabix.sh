#!/bin/bash
#SBATCH --job-name tabix
#SBATCH --time=03:00:00
#SBATCH --cpus-per-task=1
#SBATCH --mem=2G

DIR=$(sed -n "${SLURM_ARRAY_TASK_ID}p" dirs.txt)

echo "Processing $DIR"
cd "$DIR"
tabix -s 1 -b 2 -e 3 -c "#" *.tsv.gz
