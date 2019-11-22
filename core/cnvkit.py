import subprocess
import argparse
import sys
import glob
import configparser
class Myconf(configparser.ConfigParser):
    def __init__(self, defaults=None):
        configparser.ConfigParser.__init__(self, defaults=defaults)

    def optionxform(self, optionstr):
        return optionstr

def run(tumor, normal, bed, outdir,configfile):
    config = Myconf()
    config.read(configfile)
    python3=config.get('software','python3.7')
    anno=config.get('database','refFlat')
    cnvkit=config.get('software','cnvkit')
    ref=config.get('database','hg19_ref')
    access=config.get('database','cnkit_access')
    cmd="%s %s batch %s --normal %s/*.bam --targets %s --fasta %s --output-reference my_reference.cnn --output-dir %s --annotate %s --access %s" \
        %(python3,cnvkit,tumor,normal,bed,ref,outdir,anno,access)
    print(cmd)
    subprocess.check_call(cmd,shell=True)
    cns=glob.glob("%s/*.cns"%(outdir))
    infile=open(cns[0],"r")
    outfile=open("%s/cnv.final.tsv"%(outdir),"w")
    outfile.write("#Chr\tStart\tend\tgene\tlog2\ttype\tCopy\n")
    for line in infile:
        if not line.startswith("chromosome"):
            line=line.strip()
            array=line.split("\t")
            copy = 2 ** float(array[4]) * 2
            if float(array[4])>=0.585:#https://cnvkit.readthedocs.io/en/stable/calling.html
                type="gain"
                tmp = array[0] + "\t" + array[1] + "\t" + array[2] + "\t" + array[3] + "\t" + array[4] + "\t" + type + "\t" + str(copy)
                outfile.write("%s\n" % (tmp))
            if float(array[4]) <=-1:
                type="loss"
                tmp=array[0]+"\t"+array[1]+"\t"+array[2]+"\t"+array[3]+"\t"+array[4]+"\t"+type+"\t"+str(copy)
                outfile.write("%s\n"%(tmp))
    outfile.close()

if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--bam",help="bam file",required=True)
    parser.add_argument("--control",help="control directory contains bam file",required=True)
    parser.add_argument("--bed",help="bed file",required=True)
    parser.add_argument("--outdir",help="output directory",required=True)
    parser.add_argument("--config", help="config file", required=True)
    args=parser.parse_args()
    run(args.bam,args.control,args.bed,args.outdir,args.config)