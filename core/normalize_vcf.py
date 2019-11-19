import os
import sys
import argparse
import configparser
import subprocess
import re
class Myconf(configparser.ConfigParser):
    def __init__(self, defaults=None):
        configparser.ConfigParser.__init__(self, defaults=defaults)

    def optionxform(self, optionstr):
        return optionstr

def GATK(vcf,outdir,prefix,configfile):
    config = Myconf()
    config.read(configfile)
    java = config.get('software', 'java')
    gatk4 = config.get('software', 'gatk4.1.3')
    hg19_ref = config.get('database', 'hg19_ref')
    cmd="%s -jar %s LeftAlignAndTrimVariants -R %s -V %s -O %s/%s.tmp.vcf --split-multi-allelics"\
        %(java,gatk4,hg19_ref,vcf,outdir,prefix)
    subprocess.check_call(cmd,shell=True)
    infile=open("%s/%s.tmp.vcf"%(outdir,prefix),"r")
    outfile = open("%s/%s.normalize.vcf" % (outdir, prefix), "w")
    outfile.write("#CHROM\tPOS\tID\tREF\tALT\tQUAL\tFILTER\tINFO\n")
    for line in infile:
        line=line.strip()
        if not line.startswith("#"):
            array=line.split("\t")
            tmp = array[0] + "\t" + array[1] + "\t" + array[2] + "\t" + array[3] + "\t" + array[4] + "\t" + array[5] + "\t" + array[6]
            GT = array[-1].split(":")[0]
            Ref_Reads = array[-1].split(":")[1].split(",")[0]
            Alt_Reads = array[-1].split(":")[1].split(",")[1]
            if re.search('multiallelic',line):
                GT_AF=array[-1].split(":")[0].split("/")
                num=0
                for i in range(len(GT_AF)):
                    if GT_AF[i]=="1":
                        num=i-1
                AF=array[-1].split(":")[2].split(",")[num]
                tmp+="\tGT=%s;Ref_Reads=%s;Alt_Reads=%s;Var=%s\n"%(GT,Ref_Reads,Alt_Reads,AF)
                outfile.write(tmp)
            else:
                AF=array[-1].split(":")[2]
                tmp += "\tGT=%s;Ref_Reads=%s;Alt_Reads=%s;Var=%s\n" % (GT, Ref_Reads, Alt_Reads, AF)
                outfile.write(tmp)
    outfile.close()
    subprocess.check_call("rm %s/%s.tmp.vcf"%(outdir,prefix),shell=True)



if __name__=="__main__":
    parser=argparse.ArgumentParser("Normalize the VCf.")
    parser.add_argument("-v","--vcf",help="vcf file",required=True)
    parser.add_argument("-o","--outdir",help="output directory",required=True)
    parser.add_argument("-p","--prefix",help="prefix of output",required=True)
    parser.add_argument("-c","--config",help="config file",required=True)
    parser.add_argument("-t","--type",help="gatk or vardict",choices=["gatk","vardict"],required=True)
    args=parser.parse_args()
    if type=="gatk":
        GATK(args.vcf,args.outdir,args.prefix,args.config)
"""
####Decompose multiallelic variants in a VCF file.
bcftools norm -f human_g1k_v37.fasta -o ex1.step2.vcf ex1.step1.vcf
vt decompose gatk.vcf -o gatk.decomposed.vcf
LeftAlignAndTrimVariants(GATK)
#http://annovar.openbioinformatics.org/en/latest/articles/VCF/
"""