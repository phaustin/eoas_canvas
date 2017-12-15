"""
read url_list.json written by get_url.py and write json dict
with files keyed by day number
"""
import re,json
from pathlib import Path

get_day=re.compile('.*Day(\d\d).*$')

with open('url_list.json','r') as f:
    url_list=json.load(f)

the_dict={}
for day in range(27):
    day_plus_one=day+1
    key=f'{day_plus_one:02d}'
    the_dict[key]=[]
for name,url in url_list:
    if name.find('Dummy') > -1:
        continue
    match=get_day.match(name)
    if match:
        the_day=match.group(1)
        if int(the_day) > 26:
            print(f'trouble with {name}')
            continue
        the_dict[the_day].append((name,url))

with open('day_dict.json','w',encoding='utf8') as f:
    f.write(json.dumps(the_dict,indent=4,ensure_ascii=False))
        
        
    
    
    
