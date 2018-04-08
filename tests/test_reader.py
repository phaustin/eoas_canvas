"""
test_reader.py
make a new column in a gradebook

cd /Users/phil/Nextcloud/e340_coursework/e340_2018_spring/Exams/2018_Spring_Midterm_2_grades/raw_grades

python $ec/test_reader.py file_names.json day22_quiz_results.csv -c q 22

the result is a file called "q_22_upload.csv" which replaces the day quiz results
"""
import context
import os
import argparse
import pandas as pd
import json
import pdb
import re
from e340py.utils import make_tuple

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


def stringify_column(df,id_col=None):
    """
    turn a column of floating point numbers into characters

    Parameters
    ----------

    df: dataframe
        input dataframe from quiz or gradebook
    id_col: str
        name of student id column to turn into strings 
        either 'SIS User ID' or 'ID' for gradebook or
        'sis_id' or 'id' for quiz results

    Returns
    -------

    modified dataframe with ids turned from floats into strings
    """
    the_ids = df[id_col].values.astype(np.int)
    index_vals = [f'{item:d}' for item in the_ids]
    df[id_col]=index_vals
    return pd.DataFrame(df)

def clean_id(df,id_col=None):
    """
    give student numbers as floating point, turn
    into 8 character strings, droipping duplicate rows
    in the case of multiple attempts

    Parameters
    ----------

    df: dataframe
        input dataframe from quiz or gradebook
    id_col: str
        name of student id column to turn into strings 
        either 'SIS User ID' for gradebook or
        'sis_id'  quiz results
    
    Returns
    -------

    modified dataframe with duplicates removed and index set to 8 character
    student number
    """
    stringify_column(df,id_col)
    df=df.set_index(id_col,drop=False)
    df.drop_duplicates(id_col,keep='first',inplace=True)
    return pd.DataFrame(df)


def boost_grade(row,quiztype='q'):
    """
     give a row of a dataframe pull the comment and the hours worked and
     calculate additiona points

    Parameters
    ----------

    row: Pandas series
        row of dataframe passed by pandas.apply

    quiztype: str
        either 'q' for quiz or 'a' for assignment
        quiz gets a boost for both comments and hours worked
        assignment only for hours worked
    """
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
    #-----------------
    # merge the modified quiz result with the gradebook and add the boost
    #----------------
    df_small_frame['boost']=df_small_frame.apply(boost_grade,axis=1,quiztype='q')
    df_small_frame=pd.DataFrame(df_small_frame[['boost']])
    score_column = grade_col_dict[(quiztype,quiznum)]
    mergebook=pd.merge(df_gradebook,df_small_frame,how='left',left_index=True,right_index=True,sort=False)
    new_score = mergebook[score_column].values + mergebook['boost'].values
    #---------------------
    #now make a new gradebook to upload the new_score column
    #---------------------
    df_upload= pd.DataFrame(df_gradebook.iloc[:,:4])
    df_upload[score_column] = new_score
    df_upload.to_csv(f'{quiztype}_{quiznum}_upload.csv',index=False)

