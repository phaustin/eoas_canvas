#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Feb  3 16:07:24 2018

this script parses a csv named 'out.csv' and merge it with a gradebook csv file.
Two columns are added toghether to compute a final grade.  A csv file named 'gradebook' created.
example usage:
python grading_ar.py "/28_Jan_21_43_Grades-EOSC340.csv" >
"""


import pandas as pd
import numpy as np
import argparse
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
    df2=pd.read_csv(args.csv_file)

    posvec=[]

    df1=pd.read_csv('/users/marc.denojeanmairet/out.csv')

    #df2=pd.read_csv('/users/marc.denojeanmairet/28_Jan_21_43_Grades-EOSC340.csv')

    #find column possition for 'day 02' in exported gradebook.csv
    for item in df2.columns:
        lowercase=item.lower()
        posvec.append(lowercase.find('day 02')>-1)
    colnum=np.arange(len(df2.columns))[posvec][0]


    #create new dataframes with specified columns
    df3 = df2.iloc[:,np.r_[0,1,colnum]]

    df4 = df1.iloc[:,np.r_[0,1,3]]

    #merge the two new dataframes on ID key
    #frames= [df4, df3]
    result = pd.merge(df3, df4, on='ID')

    #rename column
    result.rename(columns={'Day 02: Pre-Class Quiz (29195)':'Quiz_grade'}, inplace=True)

    #add two column in a new column
    result['Day 02: Pre-Class Quiz (29195)'] = result['Quiz_grade'] + result['grades']

    #drop unwanted columns and only keep 'student', 'ID', 'Day 02' columns
    result.drop(['Quiz_grade', 'name', 'grades'], axis = 1, inplace = True)

    #output a new csv file named gradebook
    result.to_csv('gradebook.csv', index=False)

if __name__=="__main__":
    main()