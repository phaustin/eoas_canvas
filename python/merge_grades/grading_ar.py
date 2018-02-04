#!/usr/bin/env python
"""
this script parses a csv gradebook from canvas and extracts and formats the cells in the column
that contains the word "articulate"  (i.e. we ask students to articulate a question)

example usage:

python grading_ar.py 4

where 4 is the daynumber in the file "Day 04_ Pre-Class Quiz Quiz Student Analysis Report.csv"

On completion this would produce two new files:

  day_04_comment_score.csv
  day_04_comment_text.txt
"""
import sys
import numbers
import numpy as np
import pandas as pd
import argparse
import pdb
import textwrap
from pathlib import Path
import re
import copy

def make_parser():
    linebreaks = argparse.RawTextHelpFormatter
    descrip = textwrap.dedent(__doc__)
    parser = argparse.ArgumentParser(formatter_class=linebreaks,
                                     description=descrip)
    parser.add_argument('daynum', type=int, help='1 or 2 digit day number for quiz')
    parser.add_argument("--path","-p",default=".",
                        help="absolute or relative path to csv file -- defaults to '.'")
    helpstring = ("absolute or relative path to csv output file\n"
                  "-- defaults to 'day_xx_comment_score.csv'\n"
                  "where xx is the day number of the quiz")
    parser.add_argument("--outcsv","-o",type=str,
                        help=helpstring)
    helpstring = ("absolute or relative path to comment text file\n"
                  "-- defaults to 'day_xx_comment_text.txt'\n"
                  "where xx is the day number of the quiz")
    parser.add_argument("--outtext","-t",type=str,
                        help=helpstring)
    return parser

def find_file(day_num,the_path='.'):
    """
       given a 1 or two digit day number, return the full path to the csv file
    """
    
    root_path=Path(the_path).resolve()
    csv_files=root_path.glob("*.csv")
    re_string=r".*Day\s{day_num:02d}.*Student\sAnalysis\sReport.csv".format_map(locals())
    test=re.compile(re_string)
    file_list=[]
    for the_file in csv_files:
        the_match=test.match(str(the_file))
        if the_match is not None:
            file_list.append(str(the_file))
    if len(file_list) != 1:
        error_mesg=f'found {len(file_list)} files: list is {file_list}'
        raise ValueError(err_mesg)
    return file_list[0]

def main(args=None):
    """
    args: optional -- if missing then args will be taken from command line
    """
    parser = make_parser()
    args = parser.parse_args(args)
    filename=find_file(args.daynum)
    if args.outcsv is None:
        args.outcsv = f"day_{args.daynum:02d}_comment_score.csv"
    if args.outtext is None:
        args.outtext = f"day_{args.daynum:02d}_comment_text.txt"
    df1=pd.read_csv(filename)
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
    with open(args.outtext,'w') as out:
        for item in responses:
            #
            # skip empty cells with nan entries
            # add  point to grades for each student
            #'0' if 'articulate' is empty and '1' if 'articulate' is not empty
            if isinstance(item,numbers.Real):
                grades.append('0')
                continue
            grades.append('1')
            out.write(f'{dashes}\n{item}\n{dashes}')
    # new dataframe containing names, ids, and 'articulate'
    df2 = copy.deepcopy(df1.iloc[:,np.r_[0,1,colnum]])
    # add a new column named grades to df2
    df2['grades'] = grades
    # remove duplicate row (when students take the quiz more than one time)
    # keeps only the last tentative for grading
    df2 = df2.drop_duplicates(subset=['id'], keep='first')
    
    df2.rename(columns={'id':'ID'}, inplace=True)

    #s ave dataframe2 as execl file or as csv file
    # one problem with saving to csv is that empty row are generated
    # it seems to be a bug with Pandas
    df2.to_csv(args.outcsv, index=False)
    print(f"created {args.outcsv} and {args.outtext}")
    #df2.to_excel("out.xlsx", index=False)
        
    
if __name__=="__main__":
    main()
