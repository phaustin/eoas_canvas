"""
python make_tickets.py  json_file
"""
import argparse
import json
import sys
import pdb
import numpy as np
import copy
import textwrap
from pathlib import Path
from .utils import make_tuple
from .get_grade_frames import make_fsc_df

def display_marks(row,df_key,df_names):
    """
    Parameters
    ----------

    Returns
    -------
    """
    out_dict={}
    the_id=int(row['STUDENT ID'])
    txt_id=f'{the_id}'
    row['STUDENT ID']=txt_id
    row['LAST NAME']=df_names.loc[the_id]['Surname']
    row['FIRST NAME']=df_names.loc[the_id]['Preferred Name']
    for item in ['LAST NAME', 'FIRST NAME', 'STUDENT ID','Number Incorrect','TEST FORM']:
        out_dict[item]=row[item]
    out_dict['Total Score'] = 20 - out_dict['Number Incorrect']
    columns=['Q-1', 'Q-2','Q-3', 'Q-4', 'Q-5', 'Q-6', 'Q-7', 'Q-8', 'Q-9',
                'Q-10','Q-11', 'Q-12', 'Q-13', 'Q-14', 'Q-15', 'Q-16', 'Q-17',
                'Q-18','Q-19','Q-20']

    response=list(row[columns])
    for index,item in enumerate(response):
        if item not in ['A','B','C','D','E']:
            response[index] = 'F'
    if row['TEST FORM'] == 'B':
        key_answers=list(df_key['A Answer'])
    else:
        key_answers=list(df_key['A Answer'])

    xlist=[]
    grade=0
    for index,student_correct in enumerate(zip(response,key_answers)):
        student_answer,correct_answer=student_correct
        hit = correct_answer == student_answer
        if hit:
            xlist.append(' ')
            grade+=1
        else:
            xlist.append('X')
    out_dict['questions']='  '.join(response)
    out_dict['answers'] = '  '.join(key_answers)
    out_dict['xlist']='  '.join(xlist)
    numbers=np.arange(1,21)
    numbers = ['{:>2d}'.format(item) for item in numbers]
    out_dict['numbers']=' '.join(numbers)
    out_dict['possible'] = 20
    out_dict['grade'] = row['Percent Score']
    return out_dict

def grade_ids(df_ques,df_key):
    """
       grade assuming C=A version of key
    """
    numbers=np.arange(1,21)
    a_q=['Q-{}'.format(item) for item in numbers]
    a_answer_dict=dict(zip(a_q,df_key['A Answer'].values))
    score=[]
    for index,row in df_ques.iterrows():
        print(f'{row["LAST NAME"]}')
        if row['TEST FORM'] == 'B':
            answer_dict = a_answer_dict
        else:
            answer_dict = a_answer_dict
        the_marks=[]
        for qnum,key_answer in enumerate(answer_dict.items()):
            key,answer=key_answer
            the_marks.append(row[key]==answer)
        score.append(np.sum(np.array(the_marks)))
    print(f'scored {len(score)} exames in grade_ids')
    return np.array(score)

def make_parser():
    linebreaks = argparse.RawTextHelpFormatter
    descrip = __doc__.lstrip()
    parser = argparse.ArgumentParser(formatter_class=linebreaks,
                                     description=descrip)
    parser.add_argument('file_list',type=str,help='json file with file locations')
    return parser    

if __name__ == "__main__":
    parser = make_parser()
    args = parser.parse_args()
    with open(args.file_list,'r') as f:
        name_dict=json.load(f)
    n=make_tuple(name_dict)    
    base_dir=Path(n.data_dir)
    ind_grades = base_dir / Path(n.ind_file)
    df_ind = pd.read_csv(ind_grades)
    fsc_path = base_dir / Path(n.fsc_list)
    df_fsc=pd.read_cwv(fsc_path)
    key_path = base_dir / Path(n.key_file)
    df_key = pd.read_csv(key_path)
    score=grade_ids(df_ind,df_key)
    df_ind['check_score'] =copy.deepcopy(score)
    # #group_ques=grade_ques(df_groupraw,df_key)
    # #ind_ques=grade_ques(df_ind,df_key)
    df_names=df_fsc[['Student Number','Surname','Preferred Name']]
    df_names=df_names.set_index('Student Number',drop=False)
    out=list(df_ind.apply(display_marks,axis=1,args=(df_key,df_names,)))
    print(f'ready to print {len(out)} exams')
    def sortit(the_dict):
        return (the_dict['LAST NAME'],the_dict['FIRST NAME'],the_dict['STUDENT ID'])

    out.sort(key=sortit)

    text = """
    ::

         {LAST NAME:s} {FIRST NAME:s}:   EOSC340 Term 1, 2018 MT2         , SCORE=  {grade:<d}%
                       |SN:{STUDENT ID:s}   Score=({Total Score:d}/{possible:d})  Test Form {TEST FORM:s}

                   Qnum|{numbers:<s}
                   Ans | {questions:<s}
                   key | {answers:<s}
                       | {xlist:<s}
    """
    text = textwrap.dedent(text)

    with open('out.rst','w') as f:

        for count,item in enumerate(out):
            if count%6 == 0:
                f.write('.. raw:: pdf\n')
                f.write('\n    PageBreak\n\n')
            f.write(text.format_map(item))
