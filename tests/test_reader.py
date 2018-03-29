"""
make a new column in a gradebook

cd /Users/phil/Nextcloud/e340_coursework/e340_2018_spring/Exams/2018_Spring_Midterm_2_grades/raw_grades
python $ec/test_reader.py file_names.json
"""
import context
import subprocess
import shutil
import os
import argparse
import pandas as pd
import json
import pdb
import csv
from e340py.utils.make_tuple import make_tuple

def make_parser():
    linebreaks = argparse.RawTextHelpFormatter
    descrip = __doc__.lstrip()
    parser = argparse.ArgumentParser(formatter_class=linebreaks,
                                     description=descrip)
    parser.add_argument('json_file',type=str,help='input json file with filenames')
    parser.add_argument('quiz_file',type=str,help='quiz file for the day')
    return parser    


if __name__ == "__main__":
    parser=make_parser()
    args=parser.parse_args()
    keep_rows=[]

    with open(args.json_file,'r') as f:
        name_dict=json.load(f)
    n=make_tuple(name_dict)    

    with open(n.grade_book,'r') as f:
        out=csv.reader(f,delimiter=',')
        colnames=next(out)
        colnames=[item.strip() for item in colnames]
        theDict=csv.DictReader(f,fieldnames=colnames,delimiter=',')
        for item in theDict:
            keep_rows.append(item)
    pdb.set_trace()

o    # with open(args.csv_out, 'w', newline='') as csvfile:
    #     fieldnames = list(keep_rows[0].keys())
    #     fieldnames.append('new test')
    #     writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    #     writer.writeheader()
    #     for item in keep_rows:
    #         item['new test'] = 1
    #         writer.writerow(item)
