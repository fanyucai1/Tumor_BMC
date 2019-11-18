import os
import sys
sub=os.path.abspath(__file__)
dir_name=os.path.dirname(sub)
sys.path.append(dir_name)
import core
import argparse
import re
from multiprocessing import Process
import time
project=time.strftime("%Y%m%d_%H:%M:%S", time.localtime())
def run(outdir,SampleSheet,rundir):
    #######################################
    out=outdir+"/"+project
    if not os.path.exists(out):
        os.mkdir(out)
    if not os.path.exists("%s/shell"%(out)):
        os.mkdir("%s/shell"%(out))
    if not os.path.exists("%s/validate_fastq" % (out)):
        os.mkdir("%s/validate_fastq" % (out))
    if not os.path.exists("%s/SNV_indel" % (out)):
        os.mkdir("%s/SNV_indel" % (out))
    if not os.path.exists("%s/anno" % (out)):
        os.mkdir("%s/anno" % (out))
    if not os.path.exists("%s/QC" % (out)):
        os.mkdir("%s/QC" % (out))
    if not os.path.exists("%s/fusion" % (out)):
        os.mkdir("%s/fusion" % (out))
    #######################################bcl2fastq









if __name__=="__main__":
    parser=argparse.ArgumentParser("Run tumor only analysis\n")
    parser.add_argument('--rundir',help="bcl directory",required=True)
    parser.add_argument('--outdir',help="output directory",required=True,default="/data/fyc_panel27")
    parser.add_argument("--SampleSheet", help="SampleSheet csv file", required=True)
    args=parser.parse_args()

