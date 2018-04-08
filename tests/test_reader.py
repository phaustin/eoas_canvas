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
from e340py.utils import make_tuple

import numpy as np
from collections import defaultdict


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


def stringify_column(df,id_col=None):
    """
    turn a column of floating point numbers into characters
     """
    the_ids = df[id_col].values
    the_ids = the_ids.astype(np.int)
    index_vals = [f'{item:d}' for item in the_ids]
    df[id_col]=index_vals
    return pd.DataFrame(df)

def clean_id(df,id_col=None):
    """
    give student numbers as floating point, turn
    into 8 character strings, droipping duplicate rows
    in the case of multiple atemps
    """
    stringify_column(df,id_col)
    df=df.set_index(id_col,drop=False)
    df.drop_duplicates(id_col,keep='first',inplace=True)
    return pd.DataFrame(df)


def boost_grade(row,quiztype='q'):
    comment_points=0
    hours_points=0
    if quiztype =='q':
        try:
            len_comments=len(row.comments)
        except TypeError:  #nan
            len_comments=0
        if len_comments > 0 and \
           row.comments != 'none':
           comment_points=1.
        else:
            comment_points=0.
    if row.hours > 0 and row.hours < 50:
        hours_points=0.5
    out=comment_points + hours_points
    #print(f'boost: {out} {comment_points} {hours_points}')
    if np.isnan(out):
        out=0.
    return out

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
    with open(n.grade_book,'r',encoding='utf-8-sig') as f:
        df_gradebook=pd.read_csv(f)
    df_gradebook=df_gradebook.fillna(0)
    points_possible = df_gradebook.iloc[1,:]
    df_gradebook=df_gradebook.drop([0,1])
    df_gradebook=clean_id(df_gradebook, id_col = 'SIS User ID')
    df_gradebook=stringify_column(df_gradebook, id_col = 'ID')
    grade_cols = list(df_gradebook.columns.values)
    dumplist=[]
    #
    # get all assignment and quiz columns from gradebook
    #
    for item in grade_cols:
        day_out=day_re.match(item)
        assign_out = assign_re.match(item)
        if day_out:
            daynum=('q',day_out.groups(1)[0])
            dumplist.append((daynum,item))
        elif assign_out:
            assignnum=('a',assign_out.groups(1)[0])
            dumplist.append((assignnum,item))
        else:
            continue
        
    grade_col_dict=dict(dumplist)
    #-----------------------------
    # read in the quiz/assignment results
    #-----------------------------
    with open(args.quiz_file,'r',encoding='utf-8-sig') as f:
        df_quiz_result=pd.read_csv(f)
    df_quiz_result=stringify_column(df_quiz_result,'id')
    df_quiz_result.fillna(0.,inplace=True)
    df_quiz_result=clean_id(df_quiz_result, id_col = 'sis_id')
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
    df_small_frame=pd.DataFrame(df_small_frame[['boost']])
    old_score = df_gradebook[grade_col_dict[(quiztype,quiznum)]].values
    clean_score = []
    for item in old_score:
        try:
            out=float(item)
        except ValueError:
            out=0
        clean_score.append(out)
    df_gradebook['clean_old']=clean_score
    name_dict=dict()
    for item in df_gradebook.index.values:
        if item in name_dict:
            raise ValueError('found duplicate id')
        name_dict[item] = df_gradebook.loc[item,'Student']

    mergebook=pd.merge(df_gradebook,df_small_frame,how='left',left_index=True,right_index=True,sort=False)
    checkdict=defaultdict(list)
    for item in mergebook.index.values:
        checkdict[item].append(name_dict[item])
    for key,value in checkdict.items():
        if len(value) > 1:
            print(key,value)
    mergebook.fillna(0.,inplace=True)
    new_score = mergebook['clean_old'].values + mergebook['boost'].values
    df_upload= pd.DataFrame(df_gradebook.iloc[:,:4])
    quiz_col=grade_col_dict[(quiztype,quiznum)]
    df_upload[quiz_col] = new_score
    df_upload.to_csv('test_upload.csv',index=False)
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
