
import argparse
import csv
import json
import os
import webbrowser
import re
import time
import datetime
import logging   



def load_files(data_folder, alignment_across_K):
    # Placeholder function to load files
        

    # Pattern: e.g., capeverde_K4M2.csv
    file_pattern = re.compile(r'.*?_K(\d+)M(\d+).*\.csv')

    # Storage for parsed CSV files
    csv_files = {}



    # Scan the directory and categorize
    for filename in os.listdir(data_folder):
        match = file_pattern.match(filename)
        if match:
            k = f"K{match.group(1)}"
            m = f"M{match.group(2)}"
            filepath = os.path.join(data_folder, filename) #use os instead of manual concatenation is cleaner
            csv_files.setdefault(k, {})[m] = filepath #making nested dictionary

    # Load and process all CSVs, convert to floats
    all_data = {}

    for k, modes in csv_files.items():
        all_data[k] = {} #start new dictionary
        for m, filepath in modes.items():
            data = []
            with open(filepath, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    for col in row:
                        if col.startswith('Cluster'):
                            try: # Learned try may be more suitable for file conversions
                                row[col] = float(row[col])
                            except ValueError:
                                pass  # Skip if not float
                    data.append(row)
            all_data[k][m] = data # Should be sorted into Cluster number --> Mode number --> (Individual, ClusterX1 float, ClusterX2 float... )


    # Convert all datasets to a JSON object
    data_json = json.dumps(all_data)

    # Alignment for Across-K data 

    alignment_data = {}

    with open(alignment_across_K, newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            key = row["Mode1-Mode2"]
            alignment_data[key] = {
                "cost": float(row["Cost"]),
            
            }

    # Then dump to JSON
    alignment_json = json.dumps(alignment_data)

    return data_json, alignment_json




