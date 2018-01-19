#!/usr/bin/env python
"""
this script parses a csv gradebook from canvas and extracts and formats the cells in the column
that contains the word "articulate"  (i.e. we ask students to articulate a question)

example usage:

./dump_comments.py "/Users/phil/Downloads/Day 02_ Pre-Class Quiz Quiz Student Analysis Report.csv" > out.txt
"""
import sys
import numbers
import numpy as np
import pandas as pd
import argparse
import pdb
import textwrap

def make_parser():
    linebreaks = argparse.RawTextHelpFormatter
    descrip = textwrap.dedent(__doc__)
    parser = argparse.ArgumentParser(formatter_class=linebreaks,
                                     description=descrip)
    parser.add_argument('csv_file', type=str, help='full path to csv file')
    return parser

def main(args=None):
    """
    args: optional -- if missing then args will be taken from command line
    """
    parser = make_parser()
    args = parser.parse_args(args)
    df_quiz=pd.read_csv(args.csv_file)
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
    for item in responses:
        #
        # skip empty cells with nan entries
        #
        if isinstance(item,numbers.Real):
            continue
        print(f'\n{dashes}\n{item}\n{dashes}\n')
        
    
if __name__=="__main__":
    main()
    
