import os
import sys
sub=os.path.abspath(__file__)
dir_name=os.path.dirname(sub)
sys.path.append(dir_name)
import sub
import argparse
import re










if __name__=="__main__":
    parser=argparse.ArgumentParser("Run tumor_normal or tumor only analysis\n")
    parser.add_argument("--tp1",help="5 read from tumor",required=True)
    parser.add_argument("--tp2",help="3 read from tumor",required=True)
    parser.add_argument("--tumor",help="tumor name",required=True)
    parser.add_argument("--np1",help="5 read from normal",default="0")
    parser.add_argument("--np2",help="3 read from normal",default="0")
    parser.add_argument("--normal", help="normal name", required=True)
    parser.add_argument("--od",help="output directory",required=True)
    args=parser.parse_args()


