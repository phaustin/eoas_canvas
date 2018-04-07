"""
 python check_ids.py  file_list.json
"""

import pyutils
import os
import numpy as np
from pathlib import Path
import argparse
from pyutils.excel_utils import make_simple
from fuzzywuzzy import fuzz
import pdb
import json
from .utils.make_tuple import make_tuple


def convert_ids(float_id):
    the_id = [f'{int(item):d}' for item in float_id if not np.isnan(item)]
    if len(float_id) != len(the_id):
        raise ValueError('dropped/missing id values in gradesheet')
    return the_id

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
    base_dir=Path(n.data_dir)
    classlist = base_dir / Path(n.fsc_list)
    official_list = make_simple(classlist)
    print(official_list.head())
    group_grades= base_dir / Path(n.group_file)
    group_grades = make_simple(group_grades)
    columns=group_grades.columns

    group_ids=[]
    #
    # the group excel file has 4 columns for student ids
    #
    for col in columns[:4]:
        the_ids=convert_ids(group_grades[col])
        group_ids.extend(the_ids)

        
    ind_grades = base_dir / Path(n.ind_file)
    ind_grades = make_simple(ind_grades)
    ind_ids = ind_grades['STUDENT ID'].values.astype(int)
    ind_ids=convert_ids(ind_ids)
    official_ids=official_list['Student Number'].values.astype(int)
    official_ids=convert_ids(official_ids)
    print(f'number of ind exams: {len(ind_ids)}')
    print(f'number of group exams: {len(group_ids)}')
    #
    # find official ideas that appear
    #
    missing = set(official_ids) - set(ind_ids)
    print('\nmissed exam individual\n')
    for number in missing:
        hit = np.array(official_ids)==number
        info = official_list[hit][['Surname','Student Number']].values[0]
        print(*info)

    print('\nmissed group exam\n')    
    missed_group = set(official_ids) - set(group_ids)
    for number in missed_group:
        hit = np.array(official_ids)==number
        info = official_list[hit][['Surname','Student Number']].values[0]
        print(*info)


    def find_closest(the_id,good_ids):
        score_list=[]
        for choice in good_ids:
            score_list.append(fuzz.ratio(the_id,choice))
        score_array=np.array(score_list)
        max_index=np.argmax(score_array)
        good_choice=good_ids[max_index]
        return good_choice

    print('\nindividual exam: suggest close ids if typos\n')

    for item in ind_ids:
        if item not in official_ids:
            print(f'individ. miss on {item}')
            nearest=find_closest(item,official_ids)
            print(f'possible value is {nearest}')

    if len(group_ids) > 0:
        print('\nnow group: suggest close ids\n')

    for item in group_ids:
        if item not in official_ids:
            print(f'group miss on {item}')
            nearest=find_closest(item,official_ids)
            print(f'possible value is {nearest}')

    print('\ndone\n')
            
if __name__ == "__main__":
    main()

