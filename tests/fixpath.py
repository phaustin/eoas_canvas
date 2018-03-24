"""
import this in your main function to add the parent 
to the folder holding the script to the front of sys.path
"""
from pathlib import Path
import sys, os
import site
the_path=Path(sys.argv[0]).resolve()
print(f'fixpath: inserting package directory in path: {the_path}')
the_path=the_path.parents[1]
sys.path.insert(0, str(the_path))
site.removeduppaths()
