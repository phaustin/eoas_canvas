"""
dump grades for an id

python $ec/print_scores.py file_names.json -n 18761149

# bounds={'a+':90,'a':85,'a-':80,'b+':76,'b':72,'b-':68,'c+':64,'c':60,'c-':55,'d':50}
# marks=list(bounds.values())
# marks.sort()
# marks.extend([99.5,100.5])
# marks.insert(0,0)
# marks=np.array(marks)

"""
import context
import sys
import subprocess
import shutil
import os
import argparse
import pandas as pd
import json
import pdb
import csv
import re
from e340py.utils import (make_tuple, clean_id,
                          day_re, assign_re, mid_re)
import numpy as np
from collections import defaultdict
from dateutil.parser import parse
from pathlib import Path
import re

re_final = re.compile('.*Final\s-\s(?P<type>.*)\s.*')

def make_parser():
    linebreaks = argparse.RawTextHelpFormatter
    descrip = __doc__.lstrip()
    parser = argparse.ArgumentParser(formatter_class=linebreaks,
                                     description=descrip)
    parser.add_argument('json_file',type=str,help='input json file with filenames')
    parser.add_argument('-n','--numbers',nargs='+',help='one or more student ids',
                        required=True)

    return parser    

def mark_course(row):
    scores=['quiz_score', 'assign_score',
            'clicker_score', 'final_score', 'midterm_1', 'midterm_2']
    row_scores=row[scores]
    s=make_tuple(row_scores)
    final_weight=0.4
    clicker_weight = 0.05
    mid1_weight=0.15
    mid2_weight=0.15
    quiz_weight=0.10
    assign_weight=0.15
    if s.midterm_1 == 0.0:
        print('missed midterm 1',row)
        final_weight = final_weight + 0.15
        mid1_weight=0.
    if s.midterm_2 == 0.0:
        print('missed midterm 2',row)
        final_weight = final_weight + 0.15
        mid2_weight=0.
    if s.clicker_score < s.final_score:
        clicker_weight=0.
        final_weight=final_weight + 0.05
    weights = mid1_weight + mid2_weight + clicker_weight + quiz_weight + assign_weight + final_weight
    if weights != 1:
        raise ValueError(f'{row}')
    grade = s.midterm_1*mid1_weight + s.midterm_2*mid2_weight + s.final_score*final_weight +\
            s.assign_score*assign_weight + s.quiz_score*quiz_weight + s.clicker_score*clicker_weight + 1
    return grade

def print_num(row):
    row_dict=row.to_dict()
    template = \
        """
        {Student}
        Assign: {assign_score}
        Clicker: {clicker_score}
        Bonus: {bonus}
        Mid1: {Midterm 1}
        Mid2: {Midterm 2}
        Final Ind: {Individual}
        Final Group: {Group}
        Final Combined {Combined}
        Posted: {posted}
        Correct: {course_corrected}
        """
    out=template.format_map(row_dict)
    return out

def get_exams(pathtup):
    n=pathtup
    home_dir= Path(os.environ['HOME'])
    grade_book = home_dir / Path('course_total') / Path(n.grade_book)
    with open(grade_book,'r',encoding='utf-8-sig') as f:
        #
        # skip row 1 (muted/not muted)
        #
        df_gradebook = pd.read_csv(f,sep=',',index_col=False,skiprows=[1])
        points_possible = df_gradebook.iloc[0,:]
        df_workbook=pd.DataFrame(df_gradebook)
        final_col_dict={}
        mid_col_list=[]
        assign_col_list=[]
        quiz_col_list=[]
        posted_dict = {}
        for col in df_workbook.columns:
            the_match=re_final.match(col)
            if the_match:
                the_type=the_match.group('type')
                print(f"{'*'*20}\n{the_type}")
                final_col_dict[col]=the_type
            if mid_re.match(col):
                print('!!: ',col)
                mid_col_list.append(col)
                continue
            elif assign_re.match(col):
                print('!!: ',col)
                assign_col_list.append(col)
                continue
            elif day_re.match(col):
                print('!!: ',col)
                quiz_col_list.append(col)
                continue
            elif col.find('course_corrected') > -1:
                posted_dict[col]='course_corrected'
            elif col.find('posted (') > -1:
                print(f'found posted: {col}')
                posted_dict[col]='posted'
            else:
                continue
    col_vals = ['Student','SIS User ID','Individual','Group','Combined','Midterm 1','Midterm 2','posted','course_corrected']
    new_name_dict={mid_col_list[0]:mid_col_list[0][:9],mid_col_list[1]:mid_col_list[1][:9]}
    new_name_dict.update(final_col_dict)
    new_name_dict.update(posted_dict)
    df_gradebook.rename(columns=new_name_dict,inplace=True)
    df_exams = pd.DataFrame(df_gradebook[col_vals])
    df_exams = clean_id(df_exams,id_col='SIS User ID')
    df_exams.fillna(0.,inplace=True)
    return df_exams


def main(the_args=None):
    parser=make_parser()
    args=parser.parse_args(the_args)
    print(args.numbers)
    with open(args.json_file,'r') as f:
        name_dict=json.load(f)
    n=make_tuple(name_dict)
    df_exams=get_exams(n)
    home_dir= Path(os.environ['HOME'])
    all_points = home_dir / Path(n.data_dir)/ Path(n.all_points)
    with open(all_points,'r',encoding='utf-8-sig') as f:
        #
        # skip row 1 (muted/not muted)
        #
        df_all_points = pd.read_csv(f,sep=',',index_col=False)
        df_all_points = clean_id(df_all_points,id_col='SIS User ID')
        df_all_points.fillna(0.,inplace=True)
        df_all_points=pd.DataFrame(df_all_points[['assign_score','clicker_score','bonus']])

    df_all_points = pd.merge(df_all_points,df_exams,
                          how='left',left_index=True,right_index=True,sort=False)
        
    for item in args.numbers:
        row=df_all_points.loc[item]
        print(print_num(row))
        fsc_list = home_dir / Path(n.data_dir)/ Path(n.fsc_list)
        
    with open(fsc_list,'rb') as f:
        df_fsc=pd.read_excel(f,index_col=False)
        df_fsc.fillna(0.,inplace=True)
        df_fsc = clean_id(df_fsc, id_col = 'Student Number')
    df_fsc=pd.DataFrame(df_fsc[['Surname','Given Name','Student Number']])
    df_fsc  = pd.merge(df_fsc,df_all_points[['posted','course_corrected']],
                          how='left',left_index=True,right_index=True,sort=False)
    hit = df_fsc['posted'].values < df_fsc['course_corrected'].values
    df_fsc = pd.DataFrame(df_fsc.loc[hit])
    df_fsc['posted'] = np.round(df_fsc['posted'].values).astype(np.int)
    df_fsc['course_corrected'] = np.round(df_fsc['course_corrected'].values).astype(np.int)
    with open('posted_revised.csv','w',encoding='utf-8-sig') as f:
         df_fsc.to_csv(f,index=False,sep=',')
    pdb.set_trace()
    return None

if __name__ == "__main__":
    df_fsc=main()
