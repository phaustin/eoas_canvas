"""
http://docs.python-guide.org/en/latest/writing/structure
"""
import os
import sys
import site
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
sep='*'*30
print(f'{sep}\ncontext imported. Front of path:\n{sys.path[0]}\n{sys.path[1]}\n{sep}\n')
site.removeduppaths()

