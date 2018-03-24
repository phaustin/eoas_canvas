"""
doc
"""
import subprocess
import shutil
import os
import argparse
import pandas as pd
import json
import pdb

def make_parser():
    linebreaks = argparse.RawTextHelpFormatter
    descrip = __doc__.lstrip()
    parser = argparse.ArgumentParser(formatter_class=linebreaks,
                                     description=descrip)
    parser.add_argument('file_list',type=str,help='json file with file locations')
    return parser    


if __name__ == "__main__":
    import fixpath
    from pathlib import Path
    import sys
    from e340py.get_grade_frames import (make_indiv_df, make_group_df,
                                     make_fsc_df, sanity_check)
    from e340py.utils.make_tuple import make_tuple
    from e340py.utils.excel_utils import make_simple
    import e340py.utils.excel_utils
    parser = make_parser()
    args = parser.parse_args()
    with open(args.file_list,'r') as f:
        name_dict=json.load(f)
    n=make_tuple(name_dict)    
    base_dir=Path(n.data_dir)
    fsc_path = base_dir / Path(n.fsc_list)
    official_list = make_simple(fsc_path)
    print(f'fsc columns: \n{official_list.head()}')
    group_grades= base_dir / Path(n.group_file)
    df_group = make_group_df(group_grades)
    print(f'group grades: {df_group.tail()}')
    ind_grades = base_dir / Path(n.ind_file)
    df_ind = make_indiv_df(ind_grades)
    print(f'ind grades: {df_ind.tail()}')
    fsc_path = base_dir / Path(n.fsc_list)
    df_fsc=make_fsc_df(fsc_path)
    sanity_check(df_ind,df_group,df_fsc)

    df_scores = pd.merge(df_ind,df_group,how='left',left_on='id',right_on='id',sort=True)

    def calc_grades(row):
        ind=float(row['ind_percent_score'])
        try:
            group=float(row['group_percent_score'])
        except ValueError:
            group=0.
        if ind > group:
            final = ind
        else:
            final=0.85*ind + 0.15*group
        return final
    
    print(df_scores.tail())
    df_scores['posted'] = df_scores.apply(calc_grades,axis=1)
    
    

    




      

