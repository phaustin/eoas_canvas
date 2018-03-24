"""
functions to turn the group and individual remark excel
files into dataframes indexed by student number
"""

from .utils.excel_utils import make_simple
import glob
import pandas as pd
import numpy as np
from matplotlib import pyplot as plt
import copy
from collections import OrderedDict
import textwrap
from pathlib import Path
import os
import pdb


def make_group_df(group_grades):
    """
    Parameters
    ----------
    group_grades: str or Path
       path to remark group xlsx file

    Returns
    -------

    df_group: DataFrame
       dataframe with index set to integer student id
    """
    df_groupraw=make_simple(group_grades)
    ids=['STUDENT ID #1','STUDENT ID #2','STUDENT ID #3','STUDENT ID #4']
    id_list=[]
    total_list=[]
    percent_list=[]
    for index,the_row in df_groupraw.iterrows():
        for a_id in ids:
            try:
                the_id='{:d}'.format(int(the_row[a_id]))
                id_list.append(the_id)
            except (TypeError,ValueError):
                break
            total_list.append(the_row['Total Score'])
            percent_list.append(the_row['Percent Score'])

    out=[{'id':int(item)} for count,item in enumerate(id_list)]
    df_group=pd.DataFrame.from_records(out)
    df_group['group_total_score']=total_list
    df_group['group_percent_score']=percent_list
    df_group=df_group.set_index('id',drop=False)
    return df_group

def make_indiv_df(ind_grades):
    """
    Parameters
    ----------
    ind_grades: str or Path
       path to remark individual xlsx file

    Returns
    -------

    df_ind: DataFrame
       DataFrame with index set to integer student numbers
    """
    df_ind = make_simple(ind_grades)
    df_ind = pd.DataFrame(df_ind[['STUDENT ID','Total Score','Percent Score']])
    df_ind.rename(columns = {'STUDENT ID':'id','Total Score':'ind_total_score',
                             'Percent Score':'ind_percent_score'}, inplace = True)
    df_ind['id']=df_ind['id'].values.astype(int)
    df_ind = df_ind.set_index('id',drop=False)
    return df_ind

def make_fsc_df(fsc_grades):
    """
    Parameters
    ----------
    fsc_grades: str or Path
       path to xlsx classlist from fsc

    Returns
    -------
    df_fsc: DataFrame
       DataFrame with index set to integer student numbers
    """
    df_fsc = make_simple(fsc_grades)
    df_fsc = pd.DataFrame(df_fsc[['Student Number','Surname','Given Name']])
    df_fsc.rename(columns = {'Student Number':'id','Surname':'last',
                             'Given Name':'first'}, inplace = True)
    idvals=df_fsc['id'].values.astype(int)
    df_fsc['id']=idvals
    df_fsc = df_fsc.set_index('id',drop=False)
    return df_fsc
                          
def sanity_check(df_ind,df_group,df_fsc):
    fsc_ids = list(df_fsc.index.values)
    ind_ids = list(df_ind.index.values)
    sep= '_'*20
    print(f'\{sep} individual ids in gradebook? {sep}\n')
    for ind_id in ind_ids:
        if not ind_id in fsc_ids:
            print(f'individual {ind_id} missing in fsc idlist')
    print(f'\n{sep} group ids in individual list? {sep}\n')
    group_ids = df_group.index.values
    for group_id in group_ids:
        if not group_id in ind_ids:
            print(f'group id {group_id} missing in individual idlist')
            
    
