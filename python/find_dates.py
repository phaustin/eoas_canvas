"""
find all Tuesday Thursday classes for term 2, spring 2018
"""
import datetime
import numpy as np
first_day=datetime.datetime(2018, 1, 3)
family_day=datetime.datetime(2018, 2, 12)
good_friday=datetime.datetime(2018, 3, 30)
easter_monday=datetime.datetime(2018,4,2)
holidays=[family_day,good_friday,easter_monday]
last_day=datetime.datetime(2018,4,6)
break_start=datetime.datetime(2018, 2, 18)
break_end=datetime.datetime(2018, 2, 23)
days=['M','T','W','Th','F','Sa','Su']
days=dict(zip(np.arange(0,7),days))
break_days=[]
for item in range(7):
    time_delta=datetime.timedelta(days=item)
    holidays.append(break_start + time_delta)

class_days=0
class_dict={}
for daynum in range(100):
    time_delta=datetime.timedelta(days=daynum)
    the_day=first_day + time_delta
    if the_day > last_day or the_day in holidays:
        continue
    weekday=days[the_day.weekday()]
    day_string=f'{class_days+1:02d}'
    if weekday == 'T' or weekday=='Th':
        class_days+=1
        class_dict[day_string]=the_day.isoformat()
        
with open('date_dict.json','w',encoding='utf8') as f:
    json.dump(class_dict,f,indent=4,ensure_ascii=False)
                 
