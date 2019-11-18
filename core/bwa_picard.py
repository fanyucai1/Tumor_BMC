import os
import argparse
import subprocess
import time
import configparser
import pysam
class Myconf(configparser.ConfigParser):
    def __init__(self, defaults=None):
        configparser.ConfigParser.__init__(self, defaults=defaults)

    def optionxform(self, optionstr):
        return optionstr

def run(pe1,pe2,outdir,prefix,configfile):
    start=time.time()
    config = Myconf()
    config.read(configfile)
    java = config.get('software','java')
    picard = config.get('software','picard2.20.6')
    bwa = config.get('software','bwa0.7.17')
    ref =config.get('database', 'hg19_ref')
    samtools = config.get('software','samtools1.9')
    if not os.path.exists(outdir):
        os.mkdir(outdir)
    os.chdir(outdir)
    out=outdir+"/"+prefix
    cmd = "%s mem -t 10 -R \'@RG\\tID:%s\\tSM:%s\\tLB:lib:\\tPL:Illumina\' %s %s %s |" % (bwa, prefix, prefix, ref, pe1, pe2)
    cmd += "%s view -@ 10 -o %s.bam" % (samtools, out)
    #subprocess.check_call(cmd, shell=True)
    cmd = "%s sort -@ 10 %s.bam -o %s.sort.bam && rm %s.bam && %s index %s.sort.bam" % (samtools, out, out,out,samtools, out)
    #subprocess.check_call(cmd, shell=True)
    cmd = "%s -Xmx100G -jar %s MarkDuplicates I=%s.sort.bam O=%s.dup.bam M=%s.marked_dup_metrics.txt && rm %s.sort.bam %s.sort.bam.bai && %s index %s.dup.bam" % (java, picard, out, out, out,out,out,samtools,out)
    #subprocess.check_call(cmd, shell=True)
    end=time.time()
    print("Elapse time is %g seconds" % (end - start))
    
if __name__=="__main__":
    parser=argparse.ArgumentParser("Map to Reference and Mark Duplicates")
    parser.add_argument("-p1","--pe1",help="5 reads",required=True)
    parser.add_argument("-p2", "--pe2", help="3 reads", required=True)
    parser.add_argument("-o","--outdir",help="output directory",default=os.getcwd())
    parser.add_argument("-p", "--prefix", help="prefix of output", required=True)
    parser.add_argument("-c", "--config", help="config file", required=True)
    args=parser.parse_args()
    run(args.pe1, args.pe2, args.outdir, args.prefix,args.config)