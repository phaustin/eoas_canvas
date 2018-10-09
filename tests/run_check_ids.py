"""
  run_check_ids.py
"""

import context
import argparse
import pandas as pd
import json
import pdb
import re
from e340py.check_ids import main
from pathlib import Path
import os


if __name__ == "__main__":
    df_gradebook = main()
    
