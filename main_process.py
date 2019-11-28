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
    out=outdir+"/"+project
    if not os.path.exists(out):
        os.mkdir(out)
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
        core.set_use_parallel.run("%s/shell/bcl2fastq.1.sh"%(out),"bcl2fastq",1)
        subprocess.check_call('echo bcl2fastq done >%s/shell/bcl2fastq.log'%(out),shell=True)
    #######################################run fastq quality control
    out_shell=open("%s/shell/fastq_qc.2.sh"%(out),"w")
    if not os.path.exists("%s/fastq_qc/"%(out)):
        os.mkdir("%s/fastq_qc/"%(out))
    for (root,dirs,files) in os.walk("%s/validate_fastq" % (out)):
        for file in files:
            tmp=os.path.join(root,file)
            if tmp.endswith("_R1_001.fastq.gz"):
                for prefix in sampleID:
                    if re.search('%s_'%(prefix),tmp):
                        R1=tmp
                        R2=tmp.replace("_R1_","_R2_")
                        out_shell.write("%s %s/core/fastq_qc.py -p1 %s -p2 %s -o %s/fastq_qc/%s -p %s -l %s -c %s\n"
                                        %(python3,dir_name,R1,R2,out,prefix,prefix,75,configfile))
    out_shell.close()
    if not os.path.exists("%s/shell/fastq_qc.log"%(out)):
        core.set_use_parallel.run("%s/shell/fastq_qc.2.sh" % (out), "fastq_qc",10)
        subprocess.check_call('echo fastq_qc done >%s/shell/fastq_qc.log' % (out), shell=True)
    #######################################bwa_picard
    out_shell = open("%s/shell/mapping.3.sh" % (out), "w")
    if not os.path.exists("%s/mapping/"%(out)):
        os.mkdir("%s/mapping/"%(out))
    for prefix in sampleID:
        out_shell.write("%s %s/core/bwa_picard.py -p1 %s/fastq_qc/%s/%s_R1_001.fastq.gz -p2 %s/fastq_qc/%s/%s_R2_001.fastq.gz -o %s/mapping/%s -p %s -c %s\n"
                        %(python3,dir_name,out,prefix,prefix,out,prefix,prefix,out,prefix,prefix,configfile))
    out_shell.close()
    if not os.path.exists("%s/shell/mapping.log"%(out)):
        core.set_use_parallel.run("%s/shell/mapping.3.sh" % (out), "mapping",5)
        subprocess.check_call('echo mapping done >%s/shell/mapping.log'%(out),shell=True)
    #######################################BQSR
    out_shell = open("%s/shell/BQSR.4.sh" % (out), "w")
    for prefix in sampleID:
        out_shell.write("%s %s/core/BQSR.py -b %s/mapping/%s/%s.dup.bam -l %s -o %s/mapping/%s/ -p %s -c %s\n"
                        %(python3,dir_name,out,prefix,prefix,target,out,prefix,prefix,configfile))
    out_shell.close()
    if not os.path.exists("%s/shell/BQSR.log" % (out)):
        core.set_use_parallel.run("%s/shell/BQSR.4.sh" % (out), "BQSR",5)
        subprocess.check_call('echo BQSR done >%s/shell/BQSR.log' % (out), shell=True)
    #######################################bam stat
    out_shell = open("%s/shell/bam.qc.5.sh" % (out), "w")
    if probe=="0":
        probe=target
    for prefix in sampleID:
        out_shell.write("%s %s/core/bam_qc.py -t %s -r %s -c %s -o %s/mapping/%s -p %s -b %s/mapping/%s/%s.recal.bam\n"
                        %(python3,dir_name,target,probe,configfile,out,prefix,prefix,out,prefix,prefix))
    out_shell.close()
    if not os.path.exists("%s/shell/bam.qc.log"%(out)):
        core.set_use_parallel.run("%s/shell/bam.qc.5.sh" % (out), "bam stat",5)
        subprocess.check_call('echo bam stat done >%s/shell/bam.qc.log' % (out), shell=True)
    #######################################call SNV and Indel
    out_shell = open("%s/shell/SNV_indel.6.sh" % (out), "w")
    if not os.path.exists("%s/SNV_indel/"%(out)):
        os.mkdir("%s/SNV_indel/"%(out))
    for prefix in sampleID:
        if method=="GATK" or method=="all":
            out_shell.write("%s %s/core/Mutect.py --tbam %s/mapping/%s/%s.recal.bam --tname %s --bed %s --config %s --outdir %s/SNV_indel/%s --pon %s\n"%(python3,dir_name,out,prefix,prefix,prefix,target,configfile,out,prefix,pon))
        if method == "vardict" or method == "all":
            out_shell.write("%s %s/core/vardict.py --vaf %s --bam %s/mapping/%s/%s.recal.bam --bed %s --config %s --outdir %s/SNV_indel/%s --prefix %s\n"
                            %(python3,dir_name,vaf,out,prefix,prefix,target,configfile,out,prefix,prefix))
    out_shell.close()
    if not os.path.exists("%s/shell/SNV_indel.log"%(out)):
        core.set_use_parallel.run("%s/shell/SNV_indel.6.sh" % (out), 'Call snv and indel',5)
        subprocess.check_call('echo done >%s/shell/SNV_indel.log'%(out),shell=True)
    #######################################metrix
    out_shell = open("%s/shell/metrix.7.sh" % (out), "w")
    if not os.path.exists("%s/QC/"%(out)):
        os.mkdir("%s/QC/"%(out))
    out_shell.write("%s %s/core/metrix.py %s/fastq_qc/ %s/mapping/ %s/QC/"%(python3,dir_name,out,out,out))
    out_shell.close()
    if not os.path.exists("%s/shell/metrix.log"%(out)):
        core.set_use_parallel.run("%s/shell/metrix.7.sh" % (out), "metrix",1)
        subprocess.check_call('echo done >%s/shell/metrix.log'%(out),shell=True)
    #######################################fusion
    out_shell = open("%s/shell/fusion.8.sh" % (out), "w")
    if not os.path.exists("%s/fusion/"%(out)):
        os.mkdir("%s/fusion/"%(out))
    for prefix in sampleID:
        out_shell.write("%s %s/core/fusion.py -p1 %s/fastq_qc/%s/%s_R1_001.fastq.gz -p2 %s/fastq_qc/%s/%s_R2_001.fastq.gz -o %s/fusion/%s -p %s -c %s\n"
                        %(python3,dir_name,out,prefix,prefix,out,prefix,prefix,out,prefix,prefix,configfile))
    out_shell.close()
    if not os.path.exists("%s/shell/fusion.log"%(out)):
        core.set_use_parallel.run("%s/shell/fusion.8.sh" % (out), "Gene fusion",10)
        subprocess.check_call("echo done >%s/shell/fusion.log"%(out),shell=True)
    #########################################anno vcf
    out_shell = open("%s/shell/anno.9.sh" % (out), "w")
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
        core.set_use_parallel.run("%s/shell/anno.9.sh" % (out),"anno vcf",20)
        subprocess.check_call("echo done >%s/shell/anno.log" % (out), shell=True)
    #########################################
    if cnvkit!="0":
        if not os.path.exists("%s/cnv"%(out)):
            os.mkdir("%s/cnv"%(out))
        out_shell = open("%s/shell/cnv.10.sh" % (out), "w")
        for prefix in sampleID:
            out_shell.write("%s %s/core/cnvkit.py --bam %s/mapping/%s/%s.recal.bam --control %s --bed %s --outdir %s/cnv --config %s"
                            %(python3,dir_name,out,prefix,prefix,cnvkit,target,out,configfile))
        out_shell.close()
        if not os.path.exists("%s/shell/cnv.log" % (out)):
            core.set_use_parallel.run("%s/shell/cnv.10.sh" % (out),"cnvkit",5)
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