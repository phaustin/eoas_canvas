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
           'e340':'EOSC 340 101 Global Climate Change',
           'box':'Philip_Sandbox'}

#
# get the courses and make a dictionary of coursename,id values
#
canvas = Canvas(API_URL, API_KEY)
courses=list(canvas.get_courses())
keep=dict()
for item in courses:
    for shortname,longname in nicknames.items():
        if item.name.find(longname) > -1:
            keep[shortname]=item.id

#
# find all modules in e340
#
course='box'
e340=canvas.get_course(keep[course])
modules=e340.get_modules()
modules=list(modules)
#
# now grab rthe one with Assignments in its name
#
module_name='day 1 test module'
module_dict=dict()
for item in modules:
    module_dict[item.name]=item
    if item.name.find(module_name) > -1:
        assign_module=item

print(f'found module: {assign_module}')


# secret_dict=dict(token=token)
# with open('.canvas.json','w') as f:
#     json.dump(secret_dict,f)
        
# json_out={'courses':keep,'modules':list(module_dict.keys())}
# with open('savecourse.json','w') as out:
#     json.dump(json_out,out,indent=4)

#pdb.set_trace()
#out=assign_module.edit(module={'name':'assignpha'})  #
out=assign_module.set_attributes({'name':'assignpha'})  #
print(assign_module)
assign_module.edit()
pdb.set_trace()









