import context
import setuptools_scm
from pathlib import Path
import e340py

with open(e340py.version_file,'w') as f:
    the_version = setuptools_scm.get_version()
    f.write(f'{the_version}\n')
    
print(f'wrote {the_version}')

