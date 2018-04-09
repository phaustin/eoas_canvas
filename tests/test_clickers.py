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
from e340py.utils import make_tuple, read_csv
import numpy as np
from collections import defaultdict
from dateutil.parser import parse
print(parse.__doc__)

#Session 1 Performance 1/18/18
perf_re = re.compile('.*Session\s(\d+)\sPerformance\s(\d+/\d+/\d+).*')
#Session 1 Participation 1/18/18
part_re = re.compile('.*Session\s(\d+)\sParticipation\s(\d+/\d+/\d+).*')


def read_clickers(filename,delim=','):
    #
    # canvas uses a BOM
    # https://stackoverflow.com/questions/179o12307/u-ufeff-in-python-string
    #
    print(f'in read_csv: reading {filename}')
    keep_rows=[]
    with open(filename,'r',encoding='utf-8-sig') as f:
        out=csv.reader(f,delimiter=delim)
        colnames=next(out)
        colnames=[item.strip() for item in colnames]
        possible=next(out)
        theDict=csv.DictReader(f,fieldnames=colnames,delimiter=delim)
        for item in theDict:
            keep_rows.append(item)
    the_frame=pd.DataFrame(keep_rows)
    return the_frame, possible

def make_parser():
    linebreaks = argparse.RawTextHelpFormatter
    descrip = __doc__.lstrip()
    parser = argparse.ArgumentParser(formatter_class=linebreaks,
                                     description=descrip)
    parser.add_argument('json_file',type=str,help='input json file with filenames')
    return parser    


if __name__ == "__main__":

    parser=make_parser()
    args=parser.parse_args()

    with open(args.json_file,'r') as f:
        name_dict=json.load(f)
    n=make_tuple(name_dict)

    df_clickers, possible = read_clickers(n.pha_clickers)
    df_gradebook = read_csv(n.grade_book)
    id_dict={}
    for sis_id,item in df_gradebook.iterrows():
        id_dict[item['ID']] = sis_id
    sis_col=[]
    fake_id_counter = 97  #this is 'a'
    for clicker_id in df_clickers['ID']:
        try:
            sis_col.append(id_dict[clicker_id])
        except KeyError:   #student not in gradebook
            sis_id = chr(fake_id_counter)*8
            sis_col.append(sis_id)
            fake_id_counter += 1

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
                
    with open(n.grade_book,'r',encoding='utf-8-sig') as f:
        out=pd.read_csv(f)
    with open(n.pha_clickers,'r',encoding='utf-8-sig') as f:
        out2=pd.read_csv(f)

    pdb.set_trace()