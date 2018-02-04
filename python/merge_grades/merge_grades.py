#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Feb  3 16:07:24 2018

this script parses a csv named 'out.csv' and merge it with a gradebook csv file.
Two columns are added toghether to compute a final grade.  A csv file named 'gradebook' created.

example usage:

python merge_grades.py 4 2018-02-04T0852_Grades-EOSC340.csv
"""


import pandas as pd
import numpy as np
import argparse
import textwrap
from pathlib import Path
import pdb
import re

def make_parser():
    linebreaks = argparse.RawTextHelpFormatter
    descrip = textwrap.dedent(__doc__)
    parser = argparse.ArgumentParser(formatter_class=linebreaks,
                                     description=descrip)
    helpstring = ("1 or 2 digit day number\n"
                  "assumes that a file with the name\n"
                  "day_xx_comment_score.csv has been created by grading_ar.py")
    parser.add_argument('daynum', type=int, help=helpstring)
    parser.add_argument('gradebook', type=str, help="path to canvas gradebook csv file")
    helpstring = ("absolute or relative path to new csv file\n"
                  "with modified quiz score\n"
                  "-- defaults to 'day_xx_upload.csv'\n"
                  "where xx is the day number of the quiz")
    parser.add_argument("--newgrades","-n",type=str,
                        help=helpstring)
    return parser

def find_file(day_num,the_path='.'):
    """
       given a 1 or two digit day number, return the full path to the csv file
    """
    root_path=Path(the_path).resolve()
    csv_files=root_path.glob("*.csv")
    re_string=r".*day_{day_num:02d}_comment_score.csv".format_map(locals())
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
    if args.newgrades is None:
        args.newgrades = f"day_{args.daynum:02d}_upload.csv"

    comment_score_file=find_file(args.daynum)
    df2=pd.read_csv(args.gradebook)

    posvec=[]

    df1=pd.read_csv(comment_score_file)

    #df2=pd.read_csv('/users/marc.denojeanmairet/28_Jan_21_43_Grades-EOSC340.csv')

    #find column possition for 'day xx' in exported gradebook.csv

    for item in df2.columns:
        lowercase=item.lower()
        posvec.append(lowercase.find(f'day {args.daynum:02d}')>-1)
    colnum=np.arange(len(df2.columns))[posvec][0]
    colname= df2.columns[colnum]
    #pdb.set_trace()

    #create new dataframes with specified columns
    df3 = df2.iloc[:,np.r_[0,1,colnum]]

    df4 = df1.iloc[:,np.r_[0,1,3]]

    #merge the two new dataframes on ID key
    #frames= [df4, df3]
    result = pd.merge(df3, df4, on='ID')

    #rename column
    result.rename(columns={colname:'Quiz_grade'}, inplace=True)

    #add two column in a new column
    result[colname] = result['Quiz_grade'] + result['grades']

    #drop unwanted columns and only keep 'student', 'ID', 'Day 02' columns
    result.drop(['Quiz_grade', 'name', 'grades'], axis = 1, inplace = True)

    #output a new csv file named gradebook
    result.to_csv(args.newgrades, index=False)
    outstring=f'read from {comment_score_file}\nwrote {args.newgrades}'
    print(outstring)

if __name__=="__main__":
    main()
