"""
read titles from day_titles.json and dates from date_dict.json
and write module_titles.json sith titles formatted like:

Day 16 Milankovitch: Tue, Mar 06
"""
import json
import datetime
import dateutil

with open('date_dict.json','r') as f:
    date_dict=json.load(f)

with open('day_titles.json','r') as f:
    day_titles=json.load(f)

def dosort(item):
    return int(item)

module_list=[]
for day in days:
    if int(day) > 25:
        continue
    title=day_titles[day]
    the_date=dateutil.parser.parse(date_dict[day])
    strdate=the_date.strftime('%a, %b %d')
    mod_title=f'{title}: {strdate}'
    module_list.append(mod_title)

with open('module_titles.json','w') as f:
    json.dump(module_list,f,indent=4)
    
