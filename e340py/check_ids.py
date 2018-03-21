"""
 python check_ids.py /Users/phil/ownCloud/e340_mid1_2017wT2 Grades_Group.xlsx \
               Grades_Individual.xlsx fsc_classlist.xlsx
"""

import pyutils
import os
import numpy as np
from pathlib import Path
import argparse
from pyutils.excel_utils import make_simple
import textwrap
from fuzzywuzzy import fuzz

def convert_ids(float_id):
    the_id = [f'{int(item):d}' for item in float_id if not np.isnan(item)]
    return the_id

def make_parser():
    linebreaks = argparse.RawTextHelpFormatter
    descrip = textwrap.dedent(__doc__)
    parser = argparse.ArgumentParser(formatter_class=linebreaks,
                                     description=descrip)
    parser.add_argument('the_dir',type=str,help='path to directory containing gradebooks')
    parser.add_argument('group',type=str,help='name of group exam gradebook')
    parser.add_argument('individ',type=str,help='name of individual exam gradebook')
    parser.add_argument('canvas',type=str,help='name of canvas gradebook')
    return parser    

def main(the_args=None):
    parser = make_parser()
    args = parser.parse_args(the_args)


    base_dir=Path(args.the_dir)
    classlist = base_dir / Path(args.canvas)
    official_list = make_simple(classlist)
    print(official_list.head())
    group_grades= base_dir / Path(args.group)
    group_grades = make_simple(group_grades)
    columns=group_grades.columns

    group_ids=[]
    for col in columns[:4]:
        the_ids=convert_ids(group_grades[col])
        group_ids.extend(the_ids)

        
    ind_grades = base_dir / Path(args.individ)
    ind_grades = make_simple(ind_grades)
    ind_ids = ind_grades['STUDENT ID']
    ind_ids=convert_ids(ind_ids)
    official_ids=official_list['Student Number'].tolist()
    print(f'number of ind exams: {len(ind_ids)}')
    missing = set(official_ids) - set(ind_ids)
    print('missed exam individual')
    for number in missing:
        print(official_list[official_list['Student Number']==number])

    print('missed group exam')    
    missed_group = set(official_ids) - set(group_ids)
    for number in missed_group:
        print(official_list[official_list['Student Number']==number])



    def find_closest(the_id,good_ids):
        score_list=[]
        for choice in good_ids:
            score_list.append(fuzz.ratio(the_id,choice))
        score_array=np.array(score_list)
        max_index=np.argmax(score_array)
        good_choice=good_ids[max_index]
        return good_choice


    for item in ind_ids:
        if item not in official_ids:
            print(f'individ. miss on {item}')
            nearest=find_closest(item,official_ids)
            print(f'possible value is {nearest}')

    print('now group')

    for item in group_ids:
        if item not in official_ids:
            print(f'group miss on {item}')
            nearest=find_closest(item,official_ids)
            print(f'possible value is {nearest}')

if __name__ == "__main__":
    main()

# ind_file='/Users/phil/ownCloud/EOSC340 Midterm 1/M1_Indiv_Grades.xlsx'b
# group_file='/Users/phil/ownCloud/EOSC340 Midterm 1/M1_Group_Grades.xlsx'
# df_ind = make_simple(ind_file)
# print(df_ind.columns)
# df_groupraw = make_simple(group_file)
# print(df_groupraw.columns)
