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
# not used here, useful for debugging
#
def list_folder(dbx, folder, subfolder):
    """List a folder.

    Return a dict mapping unicode filenames to
    FileMetadata|FolderMetadata entries.
    """
    path = '/%s/%s' % (folder, subfolder.replace(os.path.sep, '/'))
    while '//' in path:
        path = path.replace('//', '/')
    path = path.rstrip('/')
    try:
        with stopwatch('list_folder'):
            res = dbx.files_list_folder(path)
    except dropbox.exceptions.ApiError as err:
        print('Folder listing failed for', path, '-- assumed empty:', err)
        print('Folder listing failed for', path, '-- assumed empty:', err)
        return {}
    else:
        rv = {}
        for entry in res.entries:
            rv[entry.name] = entry
            print('here is entry: ',entry.path_display)
            url=dbx.sharing_create_shared_link(entry.path_display)
            print(url)
        return rv

@contextlib.contextmanager
def stopwatch(message):
    """Context manager to print how long a block of code took."""
    t0 = time.time()
    try:
        yield
    finally:
        t1 = time.time()
        print('Total elapsed time for %s: %.3f' % (message, t1 - t0))
    

#
# put your dropbox token in a json file that looks like
# {
#     "app_key": "token goes here"
# }
#
homedir=os.environ.get('HOME')
with open(f'{homedir}/.ssh/dropbox.json','r',encoding='utf8') as f:
    secret_dict=json.loads(f.read())
dbx=dropbox.Dropbox(secret_dict['app_key'])
folder='e340 FILES FOR CONNECT'
the_dir=f'{homedir}/Dropbox/{folder}'
dropbox_dir=Path(f'{homedir}/Dropbox')
#
# get every file
#
p = Path(the_dir).glob('**/*')
files = [x for x in p if x.is_file()]
files = [x.relative_to(dropbox_dir) for x in files]
#
# make list of tuples (filename, url)
#
file_list=[]
for the_file in files:
    if the_file.suffix == '.pdf':
        strfile=f'/{str(the_file)}'
        if strfile.find('conflicted') > -1:
            continue
        print(strfile)
        url=dbx.sharing_create_shared_link(strfile)
        file_list.append((strfile,url.url))

with open('url_list.json','w',encoding='utf8') as f:
    json.dump(file_list,f,indent=4,ensure_ascii=False))
