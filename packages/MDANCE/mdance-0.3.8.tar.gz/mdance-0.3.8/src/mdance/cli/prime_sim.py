import argparse
import json
import os
import time

from mdance.prime.sim_calc import FrameSimilarity


def main():
    """Main function to run the command line interface for calculating
    frame similarities.
    
    Returns
    -------
    txt file with dictionary of similarities.

    References
    ----------
    Chen, L., Mondal, A., Perez, A. & Miranda-Quintana, R.A. `"Protein Retrieval 
    via Integrative Molecular Ensembles (PRIME) through Extended Similarity Indices."`_.
    *Journal of Chemical Theory and Computation* **2024** 20 (14), 6303-6315

    Examples
    --------
    $ prime_sim -m union -n 6 -i SM -t 0.1  -d normed_clusters -s ../nani/outputs/summary_6.csv

    .. _"Protein Retrieval via Integrative Molecular Ensembles (PRIME) through Extended Similarity Indices.": 
        https://pubs.acs.org/doi/abs/10.1021/acs.jctc.4c00362
    """
    # Parse command-line arguments
    parser = argparse.ArgumentParser()
    parser_dict = {
        'method': {'flags': ['-m', '--method'], 
                   'kwargs': {'help': 'Method to use for similarity calculation. (pairwise, union, medoid, outlier)', 
                              'required': True}},
        'n_clusters': {'flags': ['-n', '--n_clusters'], 
                       'kwargs': {'type': int, 'help': 'Number of clusters for analysis', 
                                  'required': True}},
        'index': {'flags': ['-i', '--index'], 
                  'kwargs': {'help': 'Similarity Index to use (e.g. RR or SM)', 
                             'required': True}},
        'trim_frac': {'flags': ['-t', '--trim_frac'], 
                      'kwargs': {'type': float, 'help': 'Fraction of outliers to trim. (e.g. 0.1, default: None)', 
                                 'default': None}},
        'weighted_by_frames': {'flags': ['-w', '--weighted_by_frames'], 
                               'kwargs': {'help': 'Weighing clusters by frames it contains. (default: True)', 
                                          'default': True}},
        'cluster_folder': {'flags': ['-d', '--cluster_folder'], 
                           'kwargs': {'help': 'Location of the cluster files directory', 
                                      'default': "new_clusters/"}},
        'summary_file': {'flags': ['-s', '--summary_file'], 
                         'kwargs': {'help': 'Location of CPPTRAJ cluster summary file', 
                                    'default': "summary"}}
    }
    for key, value in parser_dict.items():
        parser.add_argument(*value['flags'], **value['kwargs'])
    args = parser.parse_args()

    # Calculate similarities
    start = time.perf_counter()
    lib = FrameSimilarity(cluster_folder=args.cluster_folder, summary_file=args.summary_file, 
                                n_clusters=args.n_clusters, trim_frac=args.trim_frac, 
                                n_ary=args.index, weighted_by_frames=args.weighted_by_frames)
    method_func = getattr(lib, f'calculate_{args.method}')
    new_sims = method_func()

    if args.weighted_by_frames:
        w = "w"
    else:
        w = "nw"

    dir_name = 'outputs'
    if not os.path.exists(dir_name):
        os.makedirs(dir_name)

    if args.trim_frac:
        with open(f'{dir_name}/{w}_{args.method}_{args.index}_t{int(float(args.trim_frac) * 100)}.txt', 
                'w') as file:
            file.write(json.dumps(new_sims, indent=4))
        end = time.perf_counter()
        print(f"{w}_{args.method}_{args.index}_t{int(float(args.trim_frac) * 100)}: \
            Finished in {round(end-start,2)} second")
    else:
        with open(f'{dir_name}/{w}_{args.method}_{args.index}.txt', 'w') as file:
            file.write(json.dumps(new_sims, indent=4))
        end = time.perf_counter()
        print(f"{w}_{args.method}_{args.index}: Finished in {round(end-start,2)} second")


if __name__ == '__main__':
    main()