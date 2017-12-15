"""
walk the dropbox folder tree and find the dropbox url for all pdf files
write out a file 'save.json' with the (filename,url) tuples as a list
"""
import dropbox
from pathlib import Path
import re,os
import contextlib, time
import json
#
homedir=os.environ.get('HOME')
with open(f'{homedir}/.ssh/dropbox.json','r',encoding='utf8') as f:
    secret_dict=json.loads(f.read())
dbx=dropbox.Dropbox(secret_dict['app_key'])
folder='e340_coursework/e340_2017_fall/Classes'
the_dir=f'{homedir}/Dropbox/{folder}'
dropbox_dir=Path(f'{homedir}/Dropbox/e340_coursework/e340_2017_fall/Classes')
#
# get every file
#
p = Path(the_dir).glob('**/*')
files = [x for x in p if x.is_dir()]
files = [x.relative_to(dropbox_dir) for x in files if (str(x).find('Slides') > -1)]
files =[item.parts[0] for item in files]
files=[item.replace('_',' ') for item in files]
unique=list(set(files))
the_dict={}
for item in unique:
    key=item.split()[1]
    the_dict[key]=item

with open('day_titles.json','w') as f:
    json.dump(the_dict,f,indent=4)
    
# #
# # make list of tuples (filename, url)
# #
# file_list=[]
# for the_file in files:
#     if the_file.suffix == '.pdf':
#         strfile=f'/{str(the_file)}'
#         if strfile.find('conflicted') > -1:
#             continue
#         print(strfile)
#         url=dbx.sharing_create_shared_link(strfile)
#         file_list.append((strfile,url.url))

# with open('url_list.json','w',encoding='utf8') as f:
#     json.dump(file_list,f,indent=4,ensure_ascii=False))
