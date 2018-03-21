import pyutils
import os
import numpy as np
from pathlib import Path
print(pyutils.__file__)
from pyutils.excel_utils import make_simple
base_dir=os.environ['HOME']
base_dir = Path(base_dir) / Path('ownCloud/e340_mid1_2017wT2/')
classlist = base_dir / Path('fsc_classlist.xlsx')
official_list = make_simple(classlist)
print(official_list.head())
group_grades= base_dir / Path('group_grades_clean.xlsx')
group_grades = make_simple(group_grades)
columns=group_grades.columns

def convert_ids(float_id):
    the_id = [f'{int(item):d}' for item in float_id if not np.isnan(item)]
    return the_id

group_ids=[]
for col in columns[:4]:
    the_ids=convert_ids(group_grades[col])
    group_ids.extend(the_ids)

    
#ind_grades = base_dir / Path('individual_grades_clean.xlsx')
ind_grades = base_dir / Path('individual_grades_clean.xlsx')
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


from fuzzywuzzy import fuzz
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


# ind_file='/Users/phil/ownCloud/EOSC340 Midterm 1/M1_Indiv_Grades.xlsx'b
# group_file='/Users/phil/ownCloud/EOSC340 Midterm 1/M1_Group_Grades.xlsx'
# df_ind = make_simple(ind_file)
# print(df_ind.columns)
# df_groupraw = make_simple(group_file)
# print(df_groupraw.columns)
