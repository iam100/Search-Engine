#!/bin/bash
#SBATCH -A research
#SBATCH --qos=medium
#SBATCH -n 20
#SBATCH --mem-per-cpu=2048
#SBATCH --time=1-00:00:00
#SBATCH --mail-type=END

source ~/.bashrc

cd /scratch
mkdir anush_maha
cd anush_maha

scp -r anush_maha@ada:/share1/anush_maha/data/IRE ./
cp -r ~/IRE/20171020/*.py ./
mkdir inverted_index

python3 indexer2.py

scp -r inverted_index anush_maha@ada:/share1/anush_maha