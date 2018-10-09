"""

add_points -- modify a gradebook column to account for comments and hours worked

to run:

cd /Users/phil/Nextcloud/e340_2018_spring/Exams/2018_Spring_Midterm_2_grades/raw_grades

quiz 22 example:

add_points file_names.json day22_quiz_results.csv -c q 22

the result is a file called "q_22_upload.csv" which replaces the day quiz results

assignment 1 example:

add_points file_names.json assignment_1_results.csv -c a 1

"""
import context
import os
import argparse
import pandas as pd
import json
import pdb
import re
from pathlib import Path
import os
from e340py.utils import make_tuple, stringify_column, clean_id

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

#-------------
# use these regular expressions to identify quizzes and assignments and to find
# the hours and comments questions in an individual quiz/assignment
#-------------

mid_re = re.compile('.*Midterm\s(\d)\s-\sIndividual')
day_re = re.compile('.*Day\s(\d+).*')
assign_re = re.compile('.*Assign.*\s(\d+).*')
hours_re = re.compile('.*How much time did you spend.*')
ques_re = re.compile('.*something you found confusing or unclear.*')


def find_dups(row,attempts):
    print(row.to_frame().columns[0])
    out=list(row.to_dict().keys())
    attempts[0]+=1
    print(out)

def check_score(df_quiz,df_gradebook,quiz_col):
    the_ids=df_quiz.index.values
    print(len(the_ids),len(set(the_ids)))
    quiz_only=df_quiz[['name','score']]
    gradebook_only = df_gradebook[[quiz_col]]
    mergequiz=pd.merge(quiz_only,gradebook_only,how='left',left_index=True,right_index=True,sort=False)
    hit = mergequiz['score'].values != mergequiz[quiz_col].values
    return mergequiz.loc[hit]
    

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
    if row.hours > 0. and row.hours < 50:
        hours_points=0.5
    out=comment_points + hours_points
    #print(f'boost: {out} {comment_points} {hours_points}')
    if np.isnan(out):
        out=0.
    return out

def main(the_args=None):
    #
    # make_parser uses sys.args by default,
    # the_args can be set during code testing
    #
    parser=make_parser()
    args=parser.parse_args()
    quiztype,quiznum = list(args.column)
    quiznum = f'{int(quiznum):02d}'
    keep_rows=[]
    with open(args.json_file,'r') as f:
        name_dict=json.load(f)
    n=make_tuple(name_dict)
    #----------------------
    # read in the gradebook
    #----------------------
    root_dir = Path(os.environ['HOME']) / Path(n.data_dir)
    quiz_dir = Path(os.environ['HOME']) / Path(n.data_dir)
    grade_book =  root_dir / Path(n.grade_book)
    #pdb.set_trace()
    #
    # skip mute/readonly line after headers
    #
    with open(grade_book,'r',encoding='utf-8-sig') as f:
        df_gradebook=pd.read_csv(f,index_col=False,skiprows=[1])
        points_possible = pd.Series(df_gradebook.iloc[0,:])
    df_gradebook=df_gradebook.fillna(0)
    #-----------------
    # drop the mute/not mute row
    # and save points possbile for final write
    #-----------------
    df_gradebook=clean_id(df_gradebook, id_col = 'SIS User ID')
    df_gradebook=stringify_column(df_gradebook, id_col = 'ID')
    df_gradebook.iloc[0,:] = points_possible
    grade_cols = list(df_gradebook.columns.values)
    dumplist=[]
    #--------------------
    # get all assignment and quiz column headers from gradebook
    # and save in grade_col_dict
    #---------------------
    for item in grade_cols:
        day_out = day_re.match(item)
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
    score_column = grade_col_dict[(quiztype,quiznum)]
    pdb.set_trace()
    new_score=pd.Series(df_gradebook[score_column])
    old_score = pd.Series(new_score)
    # boost everyone's score to 11.5 for quiz 24
    #----------------
    hit = new_score > 0.
    new_score[hit] = 11.5
    mergebook = pd.DataFrame(df_gradebook)
    df_check=pd.DataFrame(mergebook[['Student',score_column]])
    df_check['new_score'] = new_score
    new_name = f'{quiztype}_{quiznum}_check.csv'
    new_name = root_dir / Path(new_name)
    with open(new_name,'w',encoding='utf-8-sig') as f:
        df_check.to_csv(f,index=False,sep=',')
    #---------------------
    # now make a new gradebook to upload the new_score column
    # this gradebook has the quiz score header so canvas will overwrite
    #---------------------
    mandatory_columns = list(mergebook.columns[:5])
    mandatory_columns = mandatory_columns + [score_column] 
    df_upload= pd.DataFrame(mergebook[mandatory_columns])
    for item in [1,2,3,4]:
        points_possible[item] = ' '
    df_upload.iloc[0,:] = points_possible[mandatory_columns]
    total_points = points_possible[score_column]
    hit = df_upload[score_column] > total_points
    df_upload.loc[hit,score_column] = total_points
    new_name = f'{quiztype}_{quiznum}_upload.csv'
    new_name = root_dir / Path(new_name)
    with open(new_name,'w',encoding='utf-8-sig') as f:
        df_upload.to_csv(f,index=False,sep=',')
    print(f'created: {str(new_name)}')
    return None

if __name__ == "__main__":
    main()
