"""
make a new column in a gradebook
"""
"""
python make_tickets.py  json_file
"""
import context
import argparse
import json
import sys
import pdb
import numpy as np
import copy
import textwrap
import pandas as pd
from pathlib import Path
from matplotlib import pyplot as plt
from e340py.utils.make_tuple import make_tuple


def make_parser():
    linebreaks = argparse.RawTextHelpFormatter
    descrip = __doc__.lstrip()
    parser = argparse.ArgumentParser(formatter_class=linebreaks,
                                     description=descrip)
    parser.add_argument('file_list',type=str,help='json file with file locations')
    return parser    

if __name__ == "__main__":
    parser = make_parser()
    args = parser.parse_args()
    with open(args.file_list,'r') as f:
        name_dict=json.load(f)
    n=make_tuple(name_dict)    
    out=pd.read_csv(n.upload_file)
    print(out.columns)
    columns=['ind_percent_score',  'group_percent_score','posted']
    fig, ax = plt.subplots(2,2,figsize=(10,10))
    plots=[ax[0,0],ax[0,1],ax[1,0]]
    for column,plot in zip(columns,plots):
        data = out[column].values
        data  = data[~np.isnan(data)]
        data_median = np.median(data)
        plot.hist(data)
        plot.set_title(f'{column} median= {data_median}')
    bad=ax[1,1]
    fig.delaxes(bad)
    fig.canvas.draw()
    fig.savefig('grades.png')
    #'group_percent_score', 'ind_percent_score', 'posted'
