from canvasapi import Canvas
import pdb
import json
from pathlib import Path
import os

my_home=Path(os.environ['HOME'])
full_path=my_home / Path('.canvas.json')
with open(full_path,'r') as f:
    secret_dict=json.load(f)
token=secret_dict['token']

# Canvas API URL
API_URL = "https://canvas.ubc.ca"
# Canvas API key
API_KEY = token
nicknames={'a301':'ATSC 301 Atmospheric Radiation and Remote Sensing',
           'e340':'EOSC 340 101 Global Climate Change'}

#
# get the courses and make a dictionary of coursename,id values
#
canvas = Canvas(API_URL, API_KEY)
out=list(canvas.get_courses())
keep=dict()
for item in out:
    for shortname,longname in nicknames.items():
        if item.name.find(longname) > -1:
            keep[shortname]=item.id

#
# find all modules in e340
#
e340=canvas.get_course(keep['e340'])
out=e340.get_modules()
modules=list(out)
#
# now grab rthe one with Assignments in its name
#
module_dict=dict()
for item in modules:
    module_dict[item.name]=item
    if item.name.find('Weekly Assignments') > -1:
        assign_module=item

print(f'found module: {assign_module}')

# secret_dict=dict(token=token)
# with open('.canvas.json','w') as f:
#     json.dump(secret_dict,f)
        
# json_out={'courses':keep,'modules':list(module_dict.keys())}
# with open('savecourse.json','w') as out:
#     json.dump(json_out,out,indent=4)

out=assign_module.edit(module={'name':'assignpha'})  # 
print(out)








