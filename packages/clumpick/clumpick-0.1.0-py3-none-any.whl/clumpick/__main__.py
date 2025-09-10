import argparse
from .funcs import load_files
from .html import generate_html_content

def main(args):
    print(args.membership_folder)
    print(args.alignment_file)
    data_json, alignment_json = load_files(args.membership_folder, args.alignment_file)
    html_content = generate_html_content(data_json, alignment_json)
    




def parse_args():
    parser = argparse.ArgumentParser(description="Clumpick: A tool for clustering and mapping genomic data.")
    parser.add_argument('--membership_folder', type=str, required=True, help='Input folder containing the clustering result files.')
    parser.add_argument('--alignment_file', type=str, required=True, help='Input file containing the cluster alignment.')
    #parser.add_argument('--output', type=str, required=True, help='Output file to save results.')
    #parser.add_argument('--method', type=str, choices=['kmeans', 'hierarchical'], default='kmeans', help='Clustering method to use.')
    return parser.parse_args()


# Now i want to generate html content

if __name__ =="__main__":
    args = parse_args()
    main(args)