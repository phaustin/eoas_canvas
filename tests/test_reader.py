"""
make a new column in a gradebook
"""
import subprocess
import shutil
import os
import argparse
import pandas as pd
import json
import pdb

def make_parser():
    linebreaks = argparse.RawTextHelpFormatter
    descrip = __doc__.lstrip()
    parser = argparse.ArgumentParser(formatter_class=linebreaks,
                                     description=descrip)
    parser.add_argument('csv_in',type=str,help='input csv file')
    parser.add_argument('csv_out',type=str,help='output csv file')
    return parser    


if __name__ == "__main__":
    import fixpath
    import csv
    parser=make_parser()
    args=parser.parse_args()
    keep_rows=[]
    with open(args.csv_in,'r') as f:
        out=csv.reader(f,delimiter=',')
        colnames=next(out)
        colnames=[item.strip() for item in colnames]
        theDict=csv.DictReader(f,fieldnames=colnames,delimiter=',')
        for item in theDict:
            keep_rows.append(item)

    with open(args.csv_out, 'w', newline='') as csvfile:
        fieldnames = list(keep_rows[0].keys())
        fieldnames.append('new test')
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for item in keep_rows:
            item['new test'] = 1
            writer.writerow(item)
