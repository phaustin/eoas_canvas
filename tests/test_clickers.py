"""
test_clickers.py
make a new column in a gradebook

cd /Users/phil/Nextcloud/e340_coursework/e340_2018_spring/Exams/2018_Spring_Midterm_2_grades/raw_grades

python $ec/test_reader.py file_names.json day22_quiz_results.csv -c q 22

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

#Session 1 Total 1/18/18
re_total = re.compile('.*Session\s(\d+)\sTotal\s(\d+/\d+/\d+).*')
re_final = re.compile('.*Final\s-\s(?P<type>.*)\s.*')

def make_parser():
    linebreaks = argparse.RawTextHelpFormatter
    descrip = __doc__.lstrip()
    parser = argparse.ArgumentParser(formatter_class=linebreaks,
                                     description=descrip)
    parser.add_argument('json_file',type=str,help='input json file with filenames')
    return parser    

def clean_clickers(clicker_file):
    with open(clicker_file,'r',encoding='utf-8-sig') as f:
        df_clickers=pd.read_csv(f,sep=',',index_col=False)
        df_clickers=df_clickers.reset_index()
        points_possible=df_clickers.iloc[0,:]
        #
        # drops points possible
        #
        df_clickers.drop(0,inplace=True)
        df_clickers.fillna(0.,inplace=True)
        df_clickers = clean_id(df_clickers, id_col = 'ID')
    return df_clickers

def mark_final(row):
    group = row['group_score']
    if group < row['ind_score']:
        group = row['ind_score']
    mark = 0.85*row['ind_score'] + 0.15*group
    return mark

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

def mark_clickers(row):
    out=np.sort(row)
    good=out[4:]
    score = np.sum(good > 0.)/len(good)*100.
    return score


def mark_quizzes(row,quiz_col_list,points_possible):
    throttled=[]
    check_points=zip(row[quiz_col_list].values,
                     points_possible[quiz_col_list].values)
    for score,maxpoints in check_points:
        if score > maxpoints:
            score=maxpoints
        throttled.append(score/maxpoints*100.)
    throttled=np.array(throttled)
    out=np.sort(throttled)
    good=out[4:]
    score=np.sum(good)/len(good)
    return score

def mark_assigns(row,assign_col_list,points_possible):
    check_points=zip(row[assign_col_list].values,points_possible[assign_col_list].values)
    throttled=[]
    for score,maxpoints in check_points:
        if score > maxpoints:
            score=maxpoints
        throttled.append(score/maxpoints*100.)
    throttled=np.array(throttled)
    score=np.sum(throttled)/len(throttled)
    return score
    
def convert_ids(float_id,bad_id=97):
    id_list=[]
    for item in float_id:
        if np.isnan(item):
            the_id=chr(bad_id)
            id_list.append(the_id)
            bad_id+=1
        else:
            the_id=f'{int(item):d}'
            id_list.append(the_id)
    if len(float_id) != len(id_list):
        msg=f'given {len(float_id)} returned {len(the_id)}'
        raise ValueError(msg)
    return id_list, bad_id
    
def read_finals(file_tuple):
    n=file_tuple
    root_dir = Path(os.environ['HOME']) / Path(n.final_dir)
    group_file = root_dir / Path(n.group_final)
    with open(group_file,'rb') as f:
        group_grades=pd.read_excel(f,sheet=None,index_col=False)
    columns=group_grades.columns
    group_scores=[]
    #
    # the group excel file has 4 columns for student ids
    #
    bad_id=97  #ascii a
    for col in columns[:4]:
        the_ids,bad_id=convert_ids(group_grades[col],bad_id)
        the_scores = group_grades['Percent Score'].values
        if len(the_ids) != len(the_scores):
            print(f'trouble: {the_ids} \n {the_scores}')
        for the_id,the_score in zip(the_ids,the_scores):
            group_scores.append({'id':the_id,'group_score':the_score})
    df_group=pd.DataFrame.from_records(group_scores)
    df_group=df_group.set_index('id',drop=False)
    #
    # get the individual final
    #
    root_dir = Path(os.environ['HOME']) / Path(n.final_dir)
    ind_file = root_dir / Path(n.ind_final)
    with open(ind_file,'rb') as f:
        ind_grades=pd.read_excel(f,sheet=None,index_col=False)
    df_ind = clean_id(ind_grades, id_col = 'STUDENT NUMBER')
    df_ind = df_ind[['Percent Score']]
    df_final = pd.merge(df_ind,df_group,
                        how='left',left_index=True,right_index=True,sort=False)
    df_final.fillna(0.,inplace=True)
    df_final.rename(columns={'Percent Score': 'ind_score'},inplace=True)
    print(f'number of ind exams: {len(df_ind)}')
    print(f'number of group exams: {len(df_group)}')
    return df_final
    
    
def main(the_args=None):
    
    parser=make_parser()
    args=parser.parse_args(the_args)
    
    with open(args.json_file,'r') as f:
        name_dict=json.load(f)
    n=make_tuple(name_dict)
    home_dir= Path(os.environ['HOME'])
    #
    #  read in all the clickers
    #
    clickers_mac = home_dir / Path(n.data_dir)/ Path(n.clickers_mac)
    df_clickers_mac = clean_clickers(clickers_mac)
    clickers_win = home_dir / Path(n.data_dir)/ Path(n.clickers_win)
    df_clickers_win = clean_clickers(clickers_win)
    clickers_cj = home_dir / Path(n.clickers_cj)
    df_clickers_cj = clean_clickers(clickers_cj)

    df_clickers = pd.merge(df_clickers_win,df_clickers_mac,how='left',left_index=True,right_index=True,sort=False)
    df_clickers = pd.merge(df_clickers,df_clickers_cj,how='left',left_index=True,right_index=True,sort=False)

    fsc_list = home_dir / Path(n.data_dir)/ Path(n.fsc_list)
    with open(fsc_list,'rb') as f:
        df_fsc=pd.read_excel(f,index_col=False)
        df_fsc.fillna(0.,inplace=True)
        df_fsc = clean_id(df_fsc, id_col = 'Student Number')

    fsc_list = home_dir / Path(n.data_dir)/ Path(n.posted)
    with open(fsc_list,'rb') as f:
        df_posted_fsc=pd.read_excel(f,index_col=False)
        df_posted_fsc.fillna(0.,inplace=True)
        df_posted_fsc = clean_id(df_fsc, id_col = 'Student Number')
        
    grade_book = home_dir / Path('course_total') / Path(n.grade_book)
    with open(grade_book,'r',encoding='utf-8-sig') as f:
        #
        # skip row 1 (muted/not muted)
        #
        df_gradebook = pd.read_csv(f,sep=',',index_col=False,skiprows=[1])
        points_possible = df_gradebook.iloc[0,:]
        df_workbook=pd.DataFrame(df_gradebook)
        final_col_dict={}
        for col in df_workbook.columns:
            the_match=re_final.match(col)
            if the_match:
                the_type=the_match.group('type')
                print(f"{'*'*20}\n{the_type}")
                final_col_dict[the_type]=col
        #
        # now drop points_possible
        #
        df_workbook = clean_id(df_workbook,id_col='SIS User ID')
        df_workbook.fillna(0.,inplace=True)

    grade_cols=df_workbook.columns
    mid_col_list=[]
    assign_col_list=[]
    quiz_col_list=[]
    for col in df_workbook.columns:
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
        else:
            continue
    #-------
    # make a dictinoary with dict[clicker_id]=sis_id
    #-------
    id_dict={}
    for sis_id,item in df_workbook.iterrows():
        key = f"{int(item['ID']):d}"
        id_dict[key] = sis_id
        
    sis_col=[]
    fake_id_counter = 97  #this is 'a'
    for clicker_id in df_clickers.index:
        try:
            sis_col.append(id_dict[clicker_id])
        except KeyError:   #student not in gradebook
            sis_id = chr(fake_id_counter)*8
            sis_col.append(sis_id)
            fake_id_counter += 1
    df_clickers['SIS User ID'] = sis_col
    df_clickers = df_clickers.set_index('SIS User ID',drop=False)
    #
    # get only the clicker scores columns that match re_total
    # 
    #
    quiz_column_list=[]
    for col in df_clickers.columns:
        the_match=re_total.match(col)
        if the_match:
            the_sess, the_date = the_match.groups()
            print(f'quiz match: {col}, {the_sess}, {the_date}')
            quiz_column_list.append(col)
    df_scores = pd.DataFrame(df_clickers[quiz_column_list])
    out=df_scores.apply(mark_clickers,axis=1)
    df_clickers['clicker_score']=out
    df_workbook=pd.merge(df_workbook,df_clickers[['clicker_score']],
                           how='left',left_index=True,right_index=True,sort=False)
    assign_marks=df_workbook.apply(mark_assigns,args=(assign_col_list,
                                              points_possible),
                           axis=1)
    df_workbook['assign_score'] = assign_marks
    quiz_marks=df_workbook.apply(mark_quizzes,args=(quiz_col_list,
                                              points_possible),
                           axis=1)
    df_workbook['quiz_score'] = quiz_marks
    df_final=read_finals(n)
    final_scores = df_final.apply(mark_final,axis=1)
    df_final['final_score'] = final_scores
    df_workbook=pd.merge(df_workbook,df_final[['final_score','ind_score','group_score']],
                           how='left',left_index=True,right_index=True,sort=False)
    cols=['Student','quiz_score','assign_score','clicker_score','final_score','ind_score','group_score']
    cols.extend(mid_col_list)
    df_course=pd.DataFrame(df_workbook[cols])
    df_course.to_csv('gradebook.csv')
    new_name_dict={mid_col_list[0]:'midterm_1',mid_col_list[1]:'midterm_2'}
    df_course.rename(columns=new_name_dict,inplace=True)
    df_fsc_out = pd.DataFrame(df_fsc[['Surname','Given Name']])
    pdb.set_trace()
    df_fsc_out = pd.merge(df_fsc_out,df_course,
                          how='left',left_index=True,right_index=True,sort=False)
    course_grade=df_fsc_out.apply(mark_course,axis=1)
    course_grade[np.isnan(course_grade)] = 0.
    df_fsc_out['course_corrected'] = np.round(course_grade).astype(np.int)
    df_fsc_out['posted'] = df_posted_fsc['Percent Grade']
    df_course=pd.merge(df_course,df_fsc_out[['posted','course_corrected']],
                           how='left',left_index=True,right_index=True,sort=False)
    del df_course['Student']
    pdb.set_trace()
    #
    # work with the real gradebook which has points possible
    #
    df_upload=pd.DataFrame(df_workbook.iloc[:,:5])
    df_upload=pd.merge(df_upload,df_course,
                           how='left',left_index=True,right_index=True,sort=False)
    columns = list(df_workbook.columns[:5])
    pdb.set_trace()
    columns.extend(['quiz_score','assign_score','clicker_score','bonus','posted','course_corrected'])
    df_upload['bonus'] = 1.
    df_upload=pd.DataFrame(df_upload[columns])
    total_score=points_possible.values
    total_score[5:8]=100.
    total_score[8] = 1.
    total_score[9] = 100.
    total_score[10] = 100.
    upload_possible=pd.Series(total_score[:11],index=df_upload.columns)
    for item in [1,2,3,4]:
        upload_possible[item] = ' '
    df_upload=df_upload[columns]
    df_upload.iloc[0,:] = upload_possible
    with open('upload_revised.csv','w',encoding='utf-8-sig') as f:
         df_upload.to_csv(f,index=False,sep=',')
    # df_upload=pd.DataFrame(df_workbook)
    # score_column = final_col_dict['Individual']
    # df_upload[score_column]=df_upload['ind_score']
    # mandatory_columns = list(df_upload.columns[:5])
    # mandatory_columns = mandatory_columns + [score_column]
    # df_upload= pd.DataFrame(df_upload[mandatory_columns])
    # points_upload=pd.Series(points_possible)
    # for item in [1,2,3,4]:
    #     points_upload[item] = ' '
    # df_upload.iloc[0,:] = points_upload[mandatory_columns]
    # with open('ind_final.csv','w',encoding='utf-8-sig') as f:
    #     df_upload.to_csv(f,index=False,sep=',')

    # df_upload=pd.DataFrame(df_workbook)
    # score_column = final_col_dict['Group']
    # df_upload[score_column]=df_upload['group_score']
    # mandatory_columns = list(df_upload.columns[:5])
    # mandatory_columns = mandatory_columns + [score_column]
    # df_upload= pd.DataFrame(df_upload[mandatory_columns])
    # df_upload.iloc[0,:] = points_upload[mandatory_columns]
    # with open('group_final.csv','w',encoding='utf-8-sig') as f:
    #     df_upload.to_csv(f,index=False,sep=',')
        
    # df_upload=pd.DataFrame(df_workbook)
    # score_column = final_col_dict['Combined']
    # df_upload[score_column]=df_upload['final_score']
    # mandatory_columns = list(df_upload.columns[:5])
    # mandatory_columns = mandatory_columns + [score_column]
    # df_upload= pd.DataFrame(df_upload[mandatory_columns])
    # df_upload.iloc[0,:] = points_upload[mandatory_columns]
    # with open('combined_final.csv','w',encoding='utf-8-sig') as f:
    #     df_upload.to_csv(f,index=False,sep=',')
    # full_grade = df_fsc_out['course'].values
    # full_grade[np.isnan(full_grade)]=0.
    # df_fsc['Percent Grade'] = np.round(full_grade).astype(np.int)
    # pdb.set_trace()
    # fsc_list = home_dir / Path(n.data_dir)/ Path('total_upload.xls')
    # with open(fsc_list,'wb') as f:
    #     df_fsc.to_excel(f)
        
    return df_fsc_out

if __name__ == "__main__":
    df_fsc=main()
