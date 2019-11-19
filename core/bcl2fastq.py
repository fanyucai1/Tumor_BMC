import os
import subprocess
import argparse
import time
import configparser

class Myconf(configparser.ConfigParser):
    def __init__(self, defaults=None):
        configparser.ConfigParser.__init__(self, defaults=defaults)

    def optionxform(self, optionstr):
        return optionstr

def run(bcldir,outdir,SampleSheet,configfile):
    config = Myconf()
    config.read(configfile)
    bcl2fastq=config.get('software','bcl2fastq')
    start=time.time()
    cmd="%s --runfolder-dir %s -o %s -r 8 -p 20 -w 8 --barcode-mismatches 0 " \
        "--ignore-missing-bcls --ignore-missing-filter --ignore-missing-positions " \
        "--ignore-missing-controls --no-lane-splitting --find-adapters-with-sliding-window " \
        "--minimum-trimmed-read-length 35 --adapter-stringency 0.9 --sample-sheet %s"%(bcl2fastq,bcldir,outdir,SampleSheet)
    subprocess.check_call(cmd,shell=True)
    end=time.time()
    print("bcl2fastq has done,elapse time is %g seconds" % (end - start))
    return cmd

if __name__=="__main__":
    parser=argparse.ArgumentParser("Run bcl2fastq pipeline.\n")
    parser.add_argument("--SampleSheet",help="SampleSheet csv file",required=True)
    parser.add_argument("--outdir",help="output directory",required=True)
    parser.add_argument("--bcldir",help="Raw bcl directory",required=True)
