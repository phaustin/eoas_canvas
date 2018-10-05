#!/usr/bin/env python
"""
example usage:

    dump_comments day9.csv

produces text file day9.txt

    dump_comments -o day9_comments.txt day9.csv

produces day9_comments.txt

"""
import sys
import numbers
import numpy as np
import pandas as pd
import argparse
import pdb
import textwrap
import os
from pathlib import Path


def make_parser():
    linebreaks = argparse.RawTextHelpFormatter
    descrip = textwrap.dedent(globals()['__doc__'])
    parser = argparse.ArgumentParser(formatter_class=linebreaks,
                                     description=descrip)
    parser.add_argument('csv_file', type=str, help='path to csv file')
    parser.add_argument('--outfile','-o',type=str,help='optional name for output file, defaults to txt suffix')
    return parser

def main(args=None):
    """
    args: optional -- if missing then args will be taken from command line
    """
    nl=os.linesep
    parser = make_parser()
    args = parser.parse_args(args)
    infile=Path(args.csv_file)
    df_quiz=pd.read_csv(infile,encoding="utf-8")
    work_dir=infile.parent
    if args.outfile:
        outfile_name=Path(args.outfile)
    else:
        in_file=Path(args.csv_file).resolve()
        outfile_name=infile.with_suffix('.txt')
    print(f'writing to: {outfile_name}')
    #pdb.set_trace()
    posvec=[]
    dashes='-'*20
    #
    # find the column number that contains "Articulate"
    #
    for item in df_quiz.columns:
        lowercase=item.lower()
        posvec.append(lowercase.find('articulate')>-1)
    colnum=np.arange(len(df_quiz.columns))[posvec][0]
    #
    # grab all rows for that column and print to stdout
    #
    responses=df_quiz.iloc[:,colnum]
    with open(outfile_name,'w',encoding='utf-8') as f:
        for item in responses:
            #
            # skip empty cells with nan entrines
            #
            if isinstance(item,numbers.Real):
                continue
            f.write(f"\n{dashes}\n{item}\n{dashes}\n")
    
if __name__=="__main__":
    main()
    
