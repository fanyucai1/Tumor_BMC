import subprocess
import sys
import argparse
import configparser
class Myconf(configparser.ConfigParser):
    def __init__(self, defaults=None):
        configparser.ConfigParser.__init__(self, defaults=defaults)

    def optionxform(self, optionstr):
        return optionstr

def run(vaf,bamfile,bedfile,prefix,outdir,configfile):
    config = Myconf()
    config.read(configfile)
    ref = config.get('database', 'hg19_ref')
    vardict=config.get('software','/software/vardict/VarDict-1.6.0/bin')
    cmd="export PATH=%s:$PATH && VarDict -U -th 10 -q 20 -Q 20 -G %s -f %s -N %s -b %s -z -c 1 -S 2 -E 3 -g 4 %s | teststrandbias.R | var2vcf_valid.pl -d 50 -m 4.25 -N %s -E -f %s >%s/%s.vardict.vcf" \
        %(vardict,ref,vaf,prefix,bamfile,bedfile,prefix,vaf,outdir,prefix)
    subprocess.check_call(cmd,shell=True)
if __name__=="__main__":
    parser=argparse.ArgumentParser("")
    parser.add_argument("--vaf",help="variant allele frequency,default:0.001",default=0.001,required=True)
    parser.add_argument("--bam",help="bam file",required=True)
    parser.add_argument("--bed",help="bed file",required=True)
    parser.add_argument("--outdir",help="output directory",required=True)
    parser.add_argument("--prefix",help="prefix of output",required=True)
    parser.add_argument("--config",help="config file",required=True)
    args=parser.parse_args()
    run(args.vaf, args.bam, args.bed, args.prefix, args.outdir, args.config)