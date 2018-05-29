"""
 python check_ids.py  file_list.json
"""

import pyutils
import os
import numpy as np
from pathlib import Path
import argparse
from fuzzywuzzy import fuzz
import pdb
import json
from .utils import make_tuple, stringify_column, clean_id
import pandas as pd


def convert_ids(float_id):
    the_id = [f'{int(item):d}' for item in float_id if not np.isnan(item)]
    if len(float_id) != len(the_id):
        print(f'given {len(float_id)} returned {len(the_id)}')
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
    #
    # get the final individual
    #
    #
    # get the class list
    #
    root_dir = Path(os.environ['HOME']) / Path(n.data_dir)
    official_list = root_dir / Path(n.fsc_list)
    with open(official_list,'rb') as f:
        df_fsc=pd.read_excel(f,sheet=None)
    #
    # get the group final
    #
    root_dir = Path(os.environ['HOME']) / Path(n.final_dir)
    group_file = root_dir / Path(n.group_final)
    with open(group_file,'rb') as f:
        group_grades=pd.read_excel(f,sheet=None)
    columns=group_grades.columns

    group_ids=[]
    #
    # the group excel file has 4 columns for student ids
    #
    for col in columns[:4]:
        the_ids=convert_ids(group_grades[col])
        group_ids.extend(the_ids)
    #
    # get the individual final
    #
    root_dir = Path(os.environ['HOME']) / Path(n.final_dir)
    ind_file = root_dir / Path(n.ind_final)
    with open(ind_file,'rb') as f:
        ind_grades=pd.read_excel(f,sheet=None)
    ind_ids = clean_id(ind_grades, id_col = 'STUDENT NUMBER')
    official_ids= clean_id(df_fsc,id_col='Student Number')
    print(f'number of ind exams: {len(ind_ids)}')
    print(f'number of group exams: {len(group_ids)}')
    #
    # find official ideas that appear
    #
    missing = set(official_ids.index.values) - set(ind_ids.index.values)
    print('\nmissed exam individual\n')
    for number in missing:
        hit = official_ids.index.values==number
        info = official_ids[hit][['Surname','Student Number']].values[0]
        print(*info)

    print('\nmissed group exam\n')    
    missed_group = set(official_ids.index.values) - set(group_ids)
    for number in missed_group:
        hit = official_ids.index.values==number
        info = official_ids[hit][['Surname','Student Number']].values[0]
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

    for item in ind_ids.index:
        if item not in official_ids.index.values:
            if item == '47582151':  #isaac clark
                continue
            print(f'individ. miss on {item}')
            nearest=find_closest(item,official_ids.index.values)
            print(f'possible value is {nearest}')

    if len(group_ids) > 0:
        print('\nnow group: suggest close ids\n')

    for item in group_ids:
        if item not in official_ids.index.values:
            if item == '47582151':  #isaac clark
                continue
            print(f'group miss on {item}')
            nearest=find_closest(item,official_ids.index.values)
            print(f'possible value is {nearest}')

    print('\ndone\n')
            
if __name__ == "__main__":
    main()

