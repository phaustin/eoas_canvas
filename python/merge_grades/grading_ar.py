#!/usr/bin/env python
"""
this script parses a csv gradebook from canvas and extracts and formats the cells in the column
that contains the word "articulate"  (i.e. we ask students to articulate a question)
example usage:
python grading_ar.py "/Day 02_ Pre-Class Quiz Quiz Student Analysis Report.csv" >
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
    df1=pd.read_csv(args.csv_file)
    #pdb.set_trace()
    grades=[]
    posvec=[]
    dashes='-'*20
    #
    # find the column number that contains "Articulate"
    #
    for item in df1.columns:
        lowercase=item.lower()
        posvec.append(lowercase.find('articulate')>-1)
    colnum=np.arange(len(df1.columns))[posvec][0]
    #
    # grab all rows for that column and print to stdout
    #
    responses=df1.iloc[:,colnum]
    for item in responses:
        #
        # skip empty cells with nan entries
        # add  point to grades for each student
        #'0' if 'articulate' is empty and '1' if 'articulate' is not empty
        if isinstance(item,numbers.Real):
            grades.append('0')
            continue
        grades.append('1')
        print(item)
     # new dataframe containing names, ids, and 'articulate'
    df2 = df1.iloc[:,np.r_[0,1,colnum]]
    # add a new column named grades to df2
    df2['grades'] = grades
    # remove duplicate row (when students take the quiz more than one time)
    # keeps only the last tentative for grading
    df2 = df2.drop_duplicates(subset=['id'], keep='first')
    
    df2.rename(columns={'id':'ID'}, inplace=True)

    #s ave dataframe2 as execl file or as csv file
    # one problem with saving to csv is that empty row are generated
    # it seems to be a bug with Pandas
    df2.to_csv('out.csv', index=False)
    #df2.to_excel("out.xlsx", index=False)
        
    
if __name__=="__main__":
    main()