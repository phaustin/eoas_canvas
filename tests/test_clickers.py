"""
test_clickers.py
make a new column in a gradebook

cd /Users/phil/Nextcloud/e340_coursework/e340_2018_spring/Exams/2018_Spring_Midterm_2_grades/raw_grades

python $ec/test_reader.py file_names.json day22_quiz_results.csv -c q 22
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
from e340py.utils import make_tuple
import numpy as np
from collections import defaultdict
from dateutil.parser import parse
from e340py.utils import clean_id, stringify_column
from pathlib import Path
import re

#Session 1 Performance 1/18/18
perf_re = re.compile('.*Session\s(\d+)\sPerformance\s(\d+/\d+/\d+).*')
#Session 1 Participation 1/18/18
part_re = re.compile('.*Session\s(\d+)\sParticipation\s(\d+/\d+/\d+).*')


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
        df_clickers.drop(0,inplace=True)
        df_clickers.fillna(0.,inplace=True)
        df_clickers = clean_id(df_clickers, id_col = 'ID')
    return df_clickers


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

    df_clickers_tot = mergebook=pd.merge(df_clickers_win,df_clickers_mac,how='left',left_index=True,right_index=True,sort=False)
    df_clickers_tot = mergebook=pd.merge(df_clickers_tot,df_clickers_cj,how='left',left_index=True,right_index=True,sort=False)
    pdb.set_trace()

    fsc_list = home_dir / Path(n.data_dir)/ Path(n.fsc_list)
    with open(fsc_list,'rb') as f:
        df_fsc=pd.read_excel(f)
        df_fsc.fillna(0.,inplace=True)
        #pdb.set_trace()
        df_fsc = clean_id(df_fsc, id_col = 'Student Number')
        
    grade_book = home_dir / Path(n.data_dir)/ Path(n.grade_book)
    with open(grade_book,'r',encoding='utf-8-sig') as f:
        df_gradebook = pd.read_csv(f,sep=',')
        df_gradebook = clean_id(df_gradebook,id_col='SIS User ID')
        df_gradebook.fillna(0.,inplace=True)

    #-------
    # make a dictinoary with dict[clicker_id]=sis_id
    #-------
    id_dict={}
    for sis_id,item in df_gradebook.iterrows():
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
    col_dict={}
    regexs=[part_re, perf_re]
    names = ['part','perf']
    for col in df_clickers.columns:
        for the_name, re_exp in zip(names,regexs):
            the_match=re_exp.match(col)
            if the_match:
                the_sess, the_date = the_match.groups()
                print(f'match: {col}, {the_sess}, {the_date}')
                date=parse(the_date,dayfirst=False)
                vals=df_clickers[col].values
                num_vals=[]
                for item in vals:
                    try:
                        num_vals.append(float(item))
                    except:
                        num_vals.append(0)
                col_dict[(the_name,the_sess)]=dict(col=col,date=the_date,vals=num_vals)
    scores = df_clickers.iloc[:,5:-2].values
    cumscore=np.sum(scores,axis=1)
    df_clickers['clicker_score']=cumscore
    only_scores=df_clickers[['clicker_score']]
    mergebook=pd.merge(df_gradebook,only_scores,how='left',left_index=True,right_index=True,sort=False)
    return mergebook,df_fsc


if __name__ == "__main__":
    mergebook, df_fsc=main()
    mid_re = re.compile('.*Midterm\s(\d)\s-\sIndividual')
    mid_dict={}
    for item in mergebook.columns:
        mid_match = mid_re.match(item)
        if mid_match:
            mid_num=mid_match.group(1)
            key=f'mid_{mid_num}'
            mid_dict[key]=item
    avg_mid = (mergebook[mid_dict['mid_1']] + mergebook[mid_dict['mid_2']])/2.
    mergebook['avg_mid'] = avg_mid
    cols = ['Student',mid_dict['mid_1'],mid_dict['mid_2'],'avg_mid','clicker_score']
    df_results=pd.DataFrame(mergebook[cols])
    hit = df_results['clicker_score'] == 0.
    df_missing = pd.DataFrame(df_results.loc[hit,:])
    df_missing.sort_values(mid_dict['mid_2'],axis=0,inplace=True)
    df_names = df_fsc[['Surname','Given Name']]
    df_missing=pd.merge(df_missing,df_names,how='left',left_index=True,right_index=True,sort=False)
    df_missing.sort_values('Surname',inplace=True)
    pdb.set_trace()
    
    
    
    

        

