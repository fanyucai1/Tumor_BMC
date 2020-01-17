#Email:fanyucai1@126.com

import subprocess
import os
import re
import argparse
import configparser
class Myconf(configparser.ConfigParser):
    def __init__(self, defaults=None):
        configparser.ConfigParser.__init__(self, defaults=defaults)

    def optionxform(self, optionstr):
        return optionstr

def run(pe1,pe2,prefix,outdir,configfile):
    config = Myconf()
    config.read(configfile)
    genefuse=config.get('software','genefuse')
    list=config.get('database','genefuse_cancer')
    ref=config.get('database','hg19_ref')
    if not os.path.exists(outdir):
        os.mkdir(outdir)
    out=outdir+"/"+prefix
    cmd="%s -t 8 -u 5 -r %s -f %s -1 %s -2 %s -h %s.html -j %s.json > %s.result" \
        %(genefuse,ref,list,pe1,pe2,out,out,out)
    subprocess.check_call(cmd,shell=True)
    infile = open("%s.result"%(out), "r")
    outfile = open("%s.tsv" % (out), "w")
    outfile.write(
        "Chr_Left\tPos_Left\tGene_Left\tChr_Right\tPos_Right\tGene_right\tUnique_Read_Depth\tInfo_left\tInfo_right\n")
    p1 = re.compile(r'(chr[\dXY]+)')
    p2 = re.compile(r'unique:(\d+)')
    num = 0
    for line in infile:
        line = line.strip()
        if line.startswith("#Fusion:"):
            num += 1
            array = line.split("___")
            array1 = array[0].split(":")
            Gene_Left = array1[1].split("_")[0]
            Pos_Left = array1[-1]

            array2 = array[1].split(":")
            Pos_Right = array2[3].split(" ")[0]
            Gene_Right = array2[0].split("_")[0]
            Unique_Read_Depth = p2.findall(line)[0]
            chr = p1.findall(line)
            outfile.write("%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n" % (chr[0], Pos_Left, Gene_Left, chr[1], Pos_Right, Gene_Right, Unique_Read_Depth, array[0], array[1]))
    outfile.close()
    if num == 0:
        subprocess.check_call("rm -rf %s.tsv" % (out), shell=True)
        print("Sample %s not find fuse." % (prefix))

if __name__=="__main__":
    parser=argparse.ArgumentParser("genefuse find fusion")
    parser.add_argument("-p1","--pe1",help="5 read",required=True)
    parser.add_argument("-p2", "--pe2", help="5 read", required=True)
    parser.add_argument("-o", "--outdir", help="output directory", required=True)
    parser.add_argument("-p", "--prefix", help="prefix of output", required=True)
    parser.add_argument("-c", "--config", help="config file", required=True)
    args=parser.parse_args()
    run(args.pe1, args.pe2, args.prefix,args.outdir, args.config)