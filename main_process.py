import os
import sys
sub=os.path.abspath(__file__)
dir_name=os.path.dirname(sub)
sys.path.append(dir_name)
import core
import argparse
import re
import time
import subprocess
import configparser
class Myconf(configparser.ConfigParser):
    def __init__(self, defaults=None):
        configparser.ConfigParser.__init__(self, defaults=defaults)

    def optionxform(self, optionstr):
        return optionstr
######################################
project=time.strftime("%Y%m%d_%H:%M:%S", time.localtime())
######################################

def run(outdir,SampleSheet,rundir,configfile,target,probe):
    config = Myconf()
    config.read(configfile)
    python3 = config.get('software', 'python3.7')
    #######################################get sampleID
    sampleID=core.parse_samplesheet.run(SampleSheet)
    #######################################
    out=outdir+"/"+project
    if not os.path.exists(out):
        os.mkdir(out)
    if not os.path.exists("%s/shell"%(out)):
        os.mkdir("%s/shell"%(out))
    #######################################bcl2fastq
    if not os.path.exists("%s/validate_fastq" % (out)):
        os.mkdir("%s/validate_fastq" % (out))
    out_shell = open("%s/shell/bcl2fastq.1.sh" % (out), "w")
    out_shell.write("%s %s/core/bcl2fastq.py --SampleSheet %s --outdir %s/validate_fastq --bcldir %s"
                    %(python3,dir_name,SampleSheet,out,rundir))
    out_shell.close()
    #######################################run fastq quality control
    out_shell=open("%s/shell/fastq_qc.2.sh"%(out),"w")
    if not os.path.exists("%s/fastq_qc/"%(out)):
        os.mkdir("%s/fastq_qc/"%(out))
    for (root,dirs,files) in os.walk("%s/validate_fastq" % (out)):
        for file in files:
            tmp=os.path.join(root,file)
            if tmp.endswith("_R1_001.fastq.gz"):
                for prefix in sampleID:
                    if re.search('%s'%(prefix),tmp):
                        R1=tmp
                        R2=tmp.replace("_R1_","_R2_")
                        out_shell.write("%s %s/core/fastq_qc.py -p1 %s -p2 %s -o %s/fastq_qc/%s -p %s -l %s -c %s\n"
                                        %(python3,dir_name,R1,R2,out,prefix,prefix,75,configfile))
    out_shell.close()
    #######################################bwa_picard
    out_shell = open("%s/shell/mapping.3.sh" % (out), "w")
    if not os.path.exists("%s/mapping/"%(out)):
        os.mkdir("%s/mapping/"%(out))
    for prefix in sampleID:
        out_shell.write("%s %s/core/bwa_picard.py -p1 %s/fastq_qc/%s/%s_R1_001.fastq.gz -p2 %s/fastq_qc/%s/%s_R2_001.fastq.gz -o %s/mapping/%s -p %s -c %s\n"
                        %(python3,dir_name,out,prefix,prefix,out,prefix,prefix,out,prefix,prefix,configfile))
    out_shell.close()
    #######################################BQSR
    out_shell = open("%s/shell/BQSR.4.sh" % (out), "w")
    for prefix in sampleID:
        out_shell.write("%s %s/core/BQSR.py -b %s/mapping/%s/%s.dup.bam -l %s -o %s/mapping/%s/ -p %s -c %s\n"
                        %(python3,dir_name,out,prefix,prefix,target,out,prefix,prefix,configfile))
    out_shell.close()
    #######################################bam stat
    out_shell = open("%s/shell/bam.qc.5.sh" % (out), "w")
    if probe=="0":
        probe=target
    for prefix in sampleID:
        out_shell.write("%s %s/core/bam_qc.py -t %s -r %s -c %s -o %s/mapping/%s -p %s -b %s/mapping/%s/%s.recal.bam\n"
                        %(python3,dir_name,target,probe,configfile,out,prefix,prefix,out,prefix,prefix))
    out_shell.close()
    #######################################call SNV and Indel
    out_shell = open("%s/shell/SNV_indel.6.sh" % (out), "w")
    if not os.path.exists("%s/SNV_indel/"%(out)):
        os.mkdir("%s/SNV_indel/"%(out))
    for prefix in sampleID:
        out_shell.write("%s %s/core/Mutect.py --tbam %s/mapping/%s/%s.recal.bam --tname %s --bed %s --config %s --outdir %s/SNV_indel/%s\n"
                        %(python3,dir_name,out,prefix,prefix,prefix,target,configfile,out,prefix))
    out_shell.close()
    #######################################metrix
    out_shell = open("%s/shell/metrix.7.sh" % (out), "w")
    if not os.path.exists("%s/QC/"%(out)):
        os.mkdir("%s/QC/"%(out))
        out_shell.write("%s %s/core/metrix.py %s/fastq_qc/ %s/mapping/ %s/QC/"
                        %(python3,dir_name,out,out,out))
    out_shell.close()
    #######################################
    core.set_use_parallel.run("%s/shell/bcl2fastq.1.sh"%(out),"bcl2fastq")
    core.set_use_parallel.run("%s/shell/fastq_qc.2.sh" % (out),"fastq_qc")
    core.set_use_parallel.run("%s/shell/mapping.3.sh" % (out),"mapping")
    core.set_use_parallel.run("%s/shell/BQSR.4.sh" % (out),"BQSR")
    core.set_use_parallel.run("%s/shell/bam.qc.5.sh" % (out),"bam stat")
    core.set_use_parallel.run("%s/shell/SNV_indel.6.sh" % (out),'Call snv and indel')
    core.set_use_parallel.run("%s/shell/metrix.7.s" % (out),"metrix")
    #########################################
if __name__=="__main__":
    parser=argparse.ArgumentParser("Run tumor only analysis\n")
    parser.add_argument('--rundir',help="bcl directory",required=True)
    parser.add_argument('--outdir',help="output directory",required=True,default="/data/fyc_panel27")
    parser.add_argument("--SampleSheet", help="SampleSheet csv file", required=True)
    parser.add_argument("--target",help="target bed file",required=True)
    parser.add_argument("--probe",help="probe bed",default="0")
    parser.add_argument("--config",help="config file",required=True)
    args=parser.parse_args()
    run(args.outdir,args.SampleSheet,args.rundir,args.config,args.target,args.probe)