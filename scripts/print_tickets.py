"""
get rst file for tickets
"""
from e340py.make_tickets import display_marks, grade_ids
import argparse
import json
from e340py.utils import make_tuple
from pathlib import Path
import pdb
import os
import pandas as pd
import copy
import textwrap


def make_parser():
    linebreaks = argparse.RawTextHelpFormatter
    descrip = __doc__.lstrip()
    parser = argparse.ArgumentParser(formatter_class=linebreaks,
                                     description=descrip)
    parser.add_argument('file_list',type=str,help='json file with file locatoins')
    return parser

def main(the_args=None):
    parser = make_parser()
    args = parser.parse_args(the_args)
    with open(args.file_list,'r') as f:
        name_dict=json.load(f)
    n=make_tuple(name_dict)
    base_dir= Path(os.environ['HOME']) / Path(n.data_dir)
    ind_grades = base_dir / Path(n.ind_file)
    print(f"reading {ind_grades}")
    df_ind = pd.read_excel(ind_grades)
    df_ind.set_index('STUDENT ID',inplace=True,drop=False)
    fsc_path = base_dir / Path(n.fsc_list)
    df_fsc= pd.read_excel(fsc_path)
    pdb.set_trace()
    df_fsc.set_index('Student Number',inplace=True,drop=False)
    key_path = base_dir / Path(n.key_file)
    df_key = pd.read_csv(str(key_path))
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

         {LAST NAME:s} {FIRST NAME:s}:   EOSC340 Term 2, 2017 MT2         , SCORE=  {grade:<d}%
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


if __name__ == "__main__":
    main()
