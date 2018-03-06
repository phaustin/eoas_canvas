#!/usr/bin/env python
"""
docstring
"""
import argparse


def make_parser():
    """
    set up the command line arguments needed to call the program
    """
    linebreaks = argparse.RawTextHelpFormatter
    parser = argparse.ArgumentParser(
        formatter_class=linebreaks, description=__doc__.lstrip())
    parser.add_argument('infile', type=str, help='input filename')
    return parser

def main(args=None):
    parser = make_parser()
    args=parser.parse_args(args)
    filename=args.infile
    with open(filename,'rb') as fp:
        the_bytes=fp.read()
        the_string=the_bytes.decode("utf-8-sig")
    with open(filename,'w') as fp:
        fp.write(the_string)
        
    with open(filename,'r',encoding='utf8') as f:
        for the_line in f:
            try:
                the_line.encode('ascii',"ignore")
                print(the_line,end="")
            except UnicodeEncodeError:
                print('error: ',the_line)

if __name__=="__main__":
    main()
