#Email:fanyucai1@126.com
#2019.7.8

import os
import argparse
import subprocess
import json
import configparser

class Myconf(configparser.ConfigParser):
    def __init__(self, defaults=None):
        configparser.ConfigParser.__init__(self, defaults=defaults)

    def optionxform(self, optionstr):
        return optionstr


def run(pe1,pe2,minlen,prefix,outdir,configfile):
    config = Myconf()
    config.read(configfile)
    fastp=config.get('software','fastp0.20.0')
    if not os.path.exists(outdir):
        os.mkdir(outdir)
    outdir=os.path.abspath(outdir)
    out=outdir+"/"+prefix
    pe1=os.path.abspath(pe1)
    pe2=os.path.abspath(pe2)
    os.chdir(outdir)
    par=" --detect_adapter_for_pe -W 4 -M 20 -l %s -w 8 -j %s.json -h %s.html " %(minlen,prefix,prefix)
    cmd="%s -i %s -I %s -o %s_R1_001.fastq.gz -O %s_R2_001.fastq.gz %s " %(fastp,pe1,pe2,prefix,prefix,par)
    subprocess.check_call(cmd, shell=True)
    json_file= os.path.abspath("%s/%s.json"%(outdir,prefix))
    outfile = open("%s/%s_raw_data_stat.tsv" % (outdir, prefix), "w")
    outfile.write("SampleID\tRaw_reads\tQ30_R1\tQ30_R2\tClean_reads\n")
    with open("%s" % (json_file), "r") as load_f:
        load_dict = json.load(load_f)
        raw1 = load_dict['summary']['before_filtering']["total_reads"]
        raw2= float(int(load_dict['read1_before_filtering']['q30_bases'])/int(load_dict['read1_before_filtering']['total_bases']))
        raw3 =float(int(load_dict['read2_before_filtering']['q30_bases'])/int(load_dict['read2_before_filtering']['total_bases']))
        clean1 = load_dict['summary']['after_filtering']["total_reads"]
    outfile.write("%s\t%s\t%s\t%s\t%s\n" % (prefix, raw1, raw2, raw3,clean1))
    outfile.close()
    subprocess.check_call("rm %s.json %s.html"%(out,out),shell=True)
    return cmd

if __name__=="__main__":
    parser = argparse.ArgumentParser("QC using fastp.")
    parser.add_argument("-p1", "--pe1", help="5 reads", required=True)
    parser.add_argument("-p2", "--pe2", help="3 reads", required=True)
    parser.add_argument("-o", "--outdir", help="output directory", default=os.getcwd())
    parser.add_argument("-p", "--prefix", help="prefix of output", default="out.clean")
    parser.add_argument("-l","--minlen",help="min length output default is 75",default=75)
    parser.add_argument("-c", "--config", help="config file", required=True)
    args = parser.parse_args()
    run(args.pe1,args.pe2,args.minlen,args.prefix,args.outdir,args.config)
