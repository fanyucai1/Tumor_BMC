import os
import sys
sub=os.path.abspath(__file__)
dir_name=os.path.dirname(sub)
sys.path.append(dir_name)
import core
import argparse
import re
import time
import configparser
import subprocess
class Myconf(configparser.ConfigParser):
    def __init__(self, defaults=None):
        configparser.ConfigParser.__init__(self, defaults=defaults)

    def optionxform(self, optionstr):
        return optionstr

def run(outdir,SampleSheet,rundir,configfile,target,probe,name,method,vaf,pon,cnvkit):
    start=time.strftime("%Y%m%d_%H:%M:%S", time.localtime())
    print("##################Project %s start time:%s###############################"%(name,start))
    config = Myconf()
    config.read(configfile)
    project =name
    python3 = config.get('software', 'python3.7')
    #######################################get sampleID
    sampleID=core.parse_samplesheet.run(SampleSheet)
    #######################################
    if not os.path.exists(outdir):
        os.makedirs(outdir)
    out=outdir+"/"+project
    if not os.path.exists(out):
        os.makedirs(out)
    if not os.path.exists("%s/shell"%(out)):
        os.mkdir("%s/shell"%(out))
    #######################################bcl2fastq
    if not os.path.exists("%s/validate_fastq" % (out)):
        os.mkdir("%s/validate_fastq" % (out))
    out_shell = open("%s/shell/bcl2fastq.1.sh" % (out), "w")
    out_shell.write("%s %s/core/bcl2fastq.py --SampleSheet %s --outdir %s/validate_fastq --bcldir %s --config %s"
                    %(python3,dir_name,SampleSheet,out,rundir,configfile))
    out_shell.close()
    if not os.path.exists("%s/shell/bcl2fastq.log"%(out)):
        subprocess.check_call('sh %s/shell/bcl2fastq.1.sh'%(out),shell=True)
        subprocess.check_call('echo bcl2fastq done >%s/shell/bcl2fastq.log'%(out),shell=True)
    #######################################run fastq quality control
    if not os.path.exists("%s/fastq_qc/"%(out)):
        os.makedirs("%s/fastq_qc/"%(out))
    if not os.path.exists("%s/mapping/"%(out)):
        os.makedirs("%s/mapping/"%(out))
    if not os.path.exists("%s/SNV_indel/"%(out)):
        os.makedirs("%s/SNV_indel/"%(out))
    if not os.path.exists("%s/fusion/"%(out)):
        os.makedirs("%s/fusion/"%(out))
    out_shell=open("%s/shell/pre.2.sh"%(out),"w")
    for (root,dirs,files) in os.walk("%s/validate_fastq" % (out)):
        for file in files:
            tmp=os.path.join(root,file)
            if tmp.endswith("_R1_001.fastq.gz"):
                for prefix in sampleID:
                    if re.search('%s_'%(prefix),tmp):
                        R1=tmp
                        R2=tmp.replace("_R1_","_R2_")
                        out_shell.write("%s %s/core/fastq_qc.py -p1 %s -p2 %s -o %s/fastq_qc/%s -p %s -l %s -c %s && "
                                        %(python3,dir_name,R1,R2,out,prefix,prefix,75,configfile))
                        out_shell.write(
                            "%s %s/core/bwa_picard.py -p1 %s/fastq_qc/%s/%s_R1_001.fastq.gz -p2 %s/fastq_qc/%s/%s_R2_001.fastq.gz -o %s/mapping/%s -p %s -c %s && "
                            % (python3, dir_name, out, prefix, prefix, out, prefix, prefix, out, prefix, prefix,
                               configfile))
                        out_shell.write(
                            "%s %s/core/BQSR.py -b %s/mapping/%s/%s.dup.bam -l %s -o %s/mapping/%s/ -p %s -c %s && "
                            % (python3, dir_name, out, prefix, prefix, target, out, prefix, prefix, configfile))
                        out_shell.write(
                            "%s %s/core/bam_qc.py -t %s -r %s -c %s -o %s/mapping/%s -p %s -b %s/mapping/%s/%s.recal.bam && "
                            % (python3, dir_name, target, probe, configfile, out, prefix, prefix, out, prefix, prefix))
                        out_shell.write(
                            "%s %s/core/fusion.py -p1 %s/fastq_qc/%s/%s_R1_001.fastq.gz -p2 %s/fastq_qc/%s/%s_R2_001.fastq.gz -o %s/fusion/%s -p %s -c %s && "
                            % (python3, dir_name, out, prefix, prefix, out, prefix, prefix, out, prefix, prefix,configfile))
                        if method=="GATK":
                            out_shell.write("%s %s/core/Mutect.py --tbam %s/mapping/%s/%s.recal.bam --tname %s --bed %s --config %s --outdir %s/SNV_indel/%s --pon %s\n"%(python3,dir_name,out,prefix,prefix,prefix,target,configfile,out,prefix,pon))
                        elif method == "vardict":
                            out_shell.write("%s %s/core/vardict.py --vaf %s --bam %s/mapping/%s/%s.recal.bam --bed %s --config %s --outdir %s/SNV_indel/%s --prefix %s\n"%(python3,dir_name,vaf,out,prefix,prefix,target,configfile,out,prefix,prefix))
                        else:
                            out_shell.write(
                                "%s %s/core/Mutect.py --tbam %s/mapping/%s/%s.recal.bam --tname %s --bed %s --config %s --outdir %s/SNV_indel/%s --pon %s && " % (
                                python3, dir_name, out, prefix, prefix, prefix, target, configfile, out, prefix, pon))
                            out_shell.write(
                                "%s %s/core/vardict.py --vaf %s --bam %s/mapping/%s/%s.recal.bam --bed %s --config %s --outdir %s/SNV_indel/%s --prefix %s\n" % (
                                python3, dir_name, vaf, out, prefix, prefix, target, configfile, out, prefix, prefix))
    out_shell.close()
    if not os.path.exists("%s/shell/pre.log"%(out)):
        core.set_use_parallel.run("%s/shell/pre.2.sh" % (out), 'Call snv and indel',8)
        subprocess.check_call('echo done >%s/shell/pre.log'%(out),shell=True)
    #######################################metrix
    out_shell = open("%s/shell/metrix.3.sh" % (out), "w")
    if not os.path.exists("%s/QC/"%(out)):
        os.mkdir("%s/QC/"%(out))
    out_shell.write("%s %s/core/metrix.py %s/fastq_qc/ %s/mapping/ %s/QC/"%(python3,dir_name,out,out,out))
    out_shell.close()
    if not os.path.exists("%s/shell/metrix.log"%(out)):
        core.set_use_parallel.run("%s/shell/metrix.3.sh" % (out), "metrix",1)
        subprocess.check_call('echo done >%s/shell/metrix.log'%(out),shell=True)
    #########################################anno vcf
    out_shell = open("%s/shell/anno.4.sh" % (out), "w")
    if not os.path.exists("%s/anno/"%(out)):
        os.mkdir("%s/anno/"%(out))
    for prefix in sampleID:
        ###################format vcf
        if method=="GATK" or method=='all':
            if not os.path.exists("%s/anno/GATK"%(out)):
                os.mkdir("%s/anno/GATK"%(out))
            out_shell.write("%s %s/core/normalize_vcf.py -v %s/SNV_indel/%s/%s.filtered.pass.vcf -o %s/anno/GATK/%s -p %s -c %s -t GATK && "
                            %(python3,dir_name,out,prefix,prefix,out,prefix,prefix,configfile))
            ###################anno
            out_shell.write("%s %s/core/anno_vcf.py -v %s/anno/GATK/%s/%s.normalize.vcf -o %s/anno/GATK/%s -p %s -c %s && "
                            % (python3, dir_name, out, prefix, prefix, out, prefix, prefix, configfile))
            ###################filter anno
            out_shell.write("%s %s/core/filter_annovar.py -a %s/anno/GATK/%s/%s.annovar.tsv -o %s/anno/GATK/%s -p %s -c %s\n"
                            % (python3, dir_name, out, prefix, prefix, out, prefix, prefix, configfile))
        if method == "vardict" or method == 'all':
            if not os.path.exists("%s/anno/vardict" % (out)):
                os.mkdir("%s/anno/vardict" % (out))
            out_shell.write(
                "%s %s/core/normalize_vcf.py -v %s/SNV_indel/%s/%s.vardict.vcf -o %s/anno/vardict/%s -p %s -c %s -t vardict && "
                % (python3, dir_name, out, prefix,prefix, out, prefix, prefix, configfile))
        ###################anno
        out_shell.write("%s %s/core/anno_vcf.py -v %s/anno/vardict/%s/%s.normalize.vcf -o %s/anno/vardict/%s -p %s -c %s && "
                        %(python3,dir_name,out,prefix,prefix,out,prefix,prefix,configfile))
        ###################filter anno
        out_shell.write("%s %s/core/filter_annovar.py -a %s/anno/vardict/%s/%s.annovar.tsv -o %s/anno/vardict/%s -p %s -c %s\n"
                        %(python3,dir_name,out,prefix,prefix,out,prefix,prefix,configfile))
    out_shell.close()
    if not os.path.exists("%s/shell/anno.log"%(out)):
        core.set_use_parallel.run("%s/shell/anno.4.sh" % (out),"anno vcf",20)
        subprocess.check_call("echo done >%s/shell/anno.log" % (out), shell=True)
    #########################################
    if cnvkit!="0":
        if not os.path.exists("%s/cnv"%(out)):
            os.mkdir("%s/cnv"%(out))
        out_shell = open("%s/shell/cnv.5.sh" % (out), "w")
        for prefix in sampleID:
            out_shell.write("%s %s/core/cnvkit.py --bam %s/mapping/%s/%s.recal.bam --control %s --bed %s --outdir %s/cnv --config %s"
                            %(python3,dir_name,out,prefix,prefix,cnvkit,target,out,configfile))
        out_shell.close()
        if not os.path.exists("%s/shell/cnv.log" % (out)):
            core.set_use_parallel.run("%s/shell/cnv.5.sh" % (out),"cnvkit",10)
            subprocess.check_call("echo done >%s/shell/cnv.log"%(out),shell=True)
    #########################################
    end=time.strftime("%Y%m%d_%H:%M:%S", time.localtime())
    print("##################Project %s finished time: %s###############################" % (name, end))


if __name__=="__main__":
    parser=argparse.ArgumentParser("Run tumor only analysis\n")
    parser.add_argument("-r",'--rundir',help="bcl directory",required=True)
    parser.add_argument("-o",'--outdir',help="output directory",required=True,default="/data/fyc_panel27")
    parser.add_argument("-s","--SampleSheet", help="SampleSheet csv file", required=True)
    parser.add_argument("-t","--target",help="target bed file",required=True)
    parser.add_argument("-p","--probe",help="probe bed",default="0")
    parser.add_argument("-c","--config",help="config file",required=True)
    parser.add_argument("-a","--name",help="project name",required=True)
    parser.add_argument("-m",'--method',help="GATK,vardict or all",choices=["GATK","vardict","all"],required=True)
    parser.add_argument("-v","--vaf",help="variant allele frequency,default:0.02",default=0.02,required=True)
    parser.add_argument("-n","--pon",help="panel of normals vcf",default="0")
    parser.add_argument("-k","--cnvkit",help="control directory contains normal bams",default="0")
    args=parser.parse_args()
    run(args.outdir,args.SampleSheet,args.rundir,args.config,args.target,args.probe,args.name,args.method,args.vaf,args.pon,args.cnvkit)