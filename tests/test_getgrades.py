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
                                         make_fsc_df,make_canvas_df,sanity_check)
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
    df_fsc=make_fsc_df(fsc_path)
    print(f'\nfsc list: {df_fsc.tail()}\n')
    group_grades= base_dir / Path(n.group_file)
    df_group = make_group_df(group_grades)
    print(f'\ngroup grades: {df_group.tail()}\n')
    ind_grades = base_dir / Path(n.ind_file)
    df_ind = make_indiv_df(ind_grades)
    print(f'\nind grades: {df_ind.tail()}\n')
    canvas_path = base_dir / Path(n.grade_book)
    df_canvas = make_canvas_df(canvas_path)
    canvas_small = df_canvas.iloc[:,:3]
    canvas_small['id'] = df_canvas.index.values
    canvas_small=canvas_small.set_index('id',drop=False)
    print(f'\ncanvas grades: {canvas_small.tail()}\n')

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
    df_scores['posted'] = df_scores.apply(calc_grades,axis=1)
    print(df_scores.tail())
    canvas_grades = pd.merge(canvas_small,df_scores,how='left',left_on='id',right_on='id',sort=False)
    canvas_grades.to_csv('midterm2_upload.csv')
    
    
    
    

    




      

