"""
test_reader.py
make a new column in a gradebook

cd /Users/phil/Nextcloud/e340_coursework/e340_2018_spring/Exams/2018_Spring_Midterm_2_grades/raw_grades

python $ec/test_reader.py file_names.json day22_quiz_results.csv -c q 22
"""
import context
import subprocess
import shutil
import os
import argparse
import pandas as pd
import json
import pdb
import csv
import re
from e340py.utils.make_tuple import make_tuple
import numpy as np

def make_parser():
    linebreaks = argparse.RawTextHelpFormatter
    descrip = __doc__.lstrip()
    parser = argparse.ArgumentParser(formatter_class=linebreaks,
                                     description=descrip)
    parser.add_argument('json_file',type=str,help='input json file with filenames')
    parser.add_argument('-c','--column',nargs='+',help='quiz/assignment column')
    parser.add_argument('quiz_file',type=str,help='quiz file for the day')
    return parser    

day_re = re.compile('.*Day\s(\d+).*')
assign_re = re.compile('.*Assign.*\s(\d+).*')
hours_re = re.compile('.*How much time did you spend.*')
ques_re = re.compile('.*something you found confusing or unclear.*')

def read_csv(filename,delim=',',the_id='SIS User ID'):
    #
    # canvas uses a BOM
    # https://stackoverflow.com/questions/17912307/u-ufeff-in-python-string
    #
    with open(filename,'r',encoding='utf-8-sig') as f:
        out=csv.reader(f,delimiter=delim)
        colnames=next(out)
        colnames=[item.strip() for item in colnames]
        theDict=csv.DictReader(f,fieldnames=colnames,delimiter=delim)
        keep_rows=[]
        for item in theDict:
            print(len(keep_rows))
            #print(item.keys())
            try:
                if len(item[the_id]) != 8:
                    continue
            except KeyError:
                print(f'threw KeyError --{the_id}--{item.keys()}')
                continue
            #print('csv reader: ',item)
            keep_rows.append(item)
    print(f'in reader,rowcount = {len(keep_rows)}')
    the_frame=pd.DataFrame(keep_rows)
    the_frame=the_frame.set_index(the_id,drop=False)
    return the_frame

def boost_grade(row,quiztype='q'):
    comment_points=0
    hours_points=0
    if quiztype =='q':
        if len(row.comments) > 0 and \
           row.comments != 'none':
           comment_points=1.
    if row.hours > 0 and row.hours < 50:
        hours_points=0.5
    return comment_points + hours_points

if __name__ == "__main__":
    parser=make_parser()
    args=parser.parse_args()
    quiztype,quiznum = list(args.column)
    keep_rows=[]
    with open(args.json_file,'r') as f:
        name_dict=json.load(f)
    n=make_tuple(name_dict)
    #
    # read in the gradebook
    #
    df_gradebook=read_csv(n.grade_book,the_id='SIS User ID')
    grade_cols = list(df_gradebook.columns.values)
    dumplist=[]
    #
    # get all assignment and quiz columns from gradebook
    #
    for item in grade_cols:
        day_out=day_re.match(item)
        assign_out = assign_re.match(item)
        if day_out:
            daynum=('q',int(day_out.groups(1)[0]))
            dumplist.append((daynum,item))
        elif assign_out:
            assignnum=('a',int(assign_out.groups(1)[0]))
            dumplist.append((assignnum,item))
        else:
            continue
        
    grade_col_dict=dict(dumplist)
    #
    # read in the quiz/assignment results
    #
    df_quiz_result=read_csv(args.quiz_file,delim=',',the_id='sis_id')
    quiz_cols = list(df_quiz_result.columns.values)
    #
    # find the hours column
    #
    for col in quiz_cols:
        hours_string=None
        match = hours_re.match(col)
        if match:
            hours_string=col
            break
    #
    # add the hours column to a minimal gradebook revision
    #
    comment_string=None
    df_small_frame = pd.DataFrame(df_quiz_result.iloc[:,:4])
    ques_hours = df_quiz_result[hours_string]
    hours_list=[]
    for item in ques_hours:
        try:
            out=float(item)
        except ValueError:
            out=0
        hours_list.append(out)
    df_small_frame['hours']=hours_list
    #
    # if it's a quiz instead of an assignment, add the comments
    #
    if quiztype == 'q':
        for col in quiz_cols:
            match = ques_re.match(col)
            if match:
                comment_string=col
                break
        ques_scores = df_quiz_result[comment_string]
        df_small_frame['comments']=ques_scores
    
    df_small_frame['boost']=df_small_frame.apply(boost_grade,axis=1,quiztype='q')
    pdb.set_trace()
    # df_small_frame['int_id'] = convert_ids(df_small_frame['sis_id'].values)
    # df_small_frame = df_small_frame.set_index('int_id',drop=False)
    # print(df_small_frame.head())
        
# print(df_quiz_result.head())
# pdb.set_trace()        
# print(comment_string)
# print(hours_string)
# df_gradebook[grade_col_dict[('q',22)]]
# pdb.set_trace()

#def bump_grade(df_gradebook, df_quiz, quiz_col, extra_points):
    

    # with open(args.csv_out, 'w', newline='') as csvfile:
    #     fieldnames = list(keep_rows[0].keys())
    #     fieldnames.append('new test')
    #     writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    #     writer.writeheader()
    #     for item in keep_rows:
    #         item['new test'] = 1
    #         writer.writerow(item)
