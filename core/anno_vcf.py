#Email:fanyucai1@126.com
#2019.7.5

import os
import subprocess
import re
import configparser
import argparse
class Myconf(configparser.ConfigParser):
    def __init__(self, defaults=None):
        configparser.ConfigParser.__init__(self, defaults=defaults)
    def optionxform(self, optionstr):
        return optionstr

out_name=['Chr','Start','End','Ref','Alt','Func.refGene','Gene.refGene','GeneDetail.refGene',
          'ExonicFunc.refGene',	'AAChange.refGene',	'cytoBand',	'1000g2015aug_all',	'avsnp150',	'snp138',
          'CLNALLELEID','CLNDN','CLNDISDB',	'CLNREVSTAT','CLNSIG','cosmic88_coding','SIFT_score','SIFT_pred',
          'Polyphen2_HDIV_score','Polyphen2_HDIV_pred','esp6500siv2_all','ExAC_ALL','ExAC_EAS','1000g2015aug_eas',
          '1000g2015aug_sas','1000g2015aug_afr','1000g2015aug_amr','1000g2015aug_eur','InterVar_automated','GT','AAChange.1',
          'Ref_Reads',	'Alt_Reads','Var']
def run_hgvs(var_site):
    p1=re.search(r'[A-Z]fs\*\d+$',var_site)###匹配移码突变
    p2=re.search(r'del([ACGT]+)ins',var_site)###匹配del和ins
    if p1:
        new=re.sub(r'[A-Z]fs\*\d+$',"",var_site)
        new=new+"fs"
    else:
        new=var_site
    if var_site.endswith("X"):####终止密码子X替换*
        new1= re.sub(r'X$', "*", new)
    else:
        new1=new
    if p2:
        new2=re.sub(p2.group(1),"",new1,count=1)
    else:
        new2 = new1
    return new2

def sub_transcript(genename,configfile):
    config = Myconf()
    config.read(configfile)
    clinvar = config.get('database', 'Canonical_transcript_file')
    MSK=config.get('database','msk_transcript')
    genelist={}
    infile=open(MSK,"r")
    for line in infile:
        line=line.strip()
        array = re.split("\s", line)
        genelist[array[0]]=array[1]
    infile.close()
    infile=open(clinvar,"r")
    for line in infile:
        line=line.strip()
        array = line.split("\t")
        if not array[0] in genelist:
            genelist[array[0]]=array[1].split(".")[0]
    infile.close()
    if genename in genelist:
        return genelist[genename]
    else:
        return "no"
#######################################################################################
def run(vcf,outdir,prefix,configfile):
    config = Myconf()
    config.read(configfile)
    annovar=config.get('software','annovar')
    if not os.path.exists(outdir):
        os.mkdir(outdir)
    out=outdir+"/"+prefix
    ##########################run annovar
    par = " -protocol refGene,cytoBand,snp138,avsnp150,exac03,esp6500siv2_all,1000g2015aug_all,1000g2015aug_eas,gnomad211_exome,gnomad211_genome,cosmic88_coding,clinvar_20190305,ljb26_all,intervar_20180118"
    par += ",1000g2015aug_sas,1000g2015aug_afr,1000g2015aug_amr,1000g2015aug_eur "
    par += " -operation g,r,f,f,f,f,f,f,f,f,f,f,f,f,f,f,f,f "
    par += " -nastring . -polish "
    subprocess.check_call("perl %s/table_annovar.pl %s %s/humandb -buildver hg19 -out %s -remove %s -vcfinput " % (annovar, vcf, annovar, out, par), shell=True)
    subprocess.check_call("rm -rf %s.hg19_multianno.vcf %s.avinput" % (out, out), shell=True)
    infile = open("%s.hg19_multianno.txt" % (out), "r")
    outfile = open("%s.annovar.tsv" % (out), "w")
    for i in range(len(out_name)):
        if i == 0:
            outfile.write("%s" % (out_name[i]))
        else:
            outfile.write("\t%s" % (out_name[i]))
    outfile.write("\n")
    dict = {}
    for line in infile:
        line = line.strip()
        array = line.split("\t")
        name = []
        if line.startswith("Chr"):
            for i in range(len(array)):
                name.append(array[i])
                dict[array[i]] = i
        else:
            GT = array[-1].split(";")[0].split("=")[1]
            Ref_Reads = array[-1].split(";")[1].split("=")[1]
            Alt_Reads = array[-1].split(";")[2].split("=")[1]
            Var = array[-1].split(";")[3].split("=")[1]
            ##########################format output knownCanonical transcript
            tmp = array[dict['AAChange.refGene']].split(",")
            final_nm =sub_transcript(array[6],configfile)
            if array[dict['AAChange.refGene']]==".":
                final_nm ="."
            elif final_nm=="no":
                final_nm=tmp[0]
            else:
                for key in tmp:
                    if re.search("%s"%(final_nm),key):
                        final_nm=key
            ##########################
            for l in range(len(out_name)):
                if l == 0:
                    outfile.write("%s" % (array[dict[out_name[l]]]))
                elif out_name[l] == "Var":
                    tmp_num = float(Var) * 100
                    outfile.write("\t%.2f" % (tmp_num) + "%")
                elif out_name[l] == "Alt_Reads":
                    outfile.write("\t%s" % (Alt_Reads))
                elif out_name[l] == "Ref_Reads":
                    outfile.write("\t%s" % (Ref_Reads))
                elif out_name[l] == "AAChange.1":
                    outfile.write("\t%s" % (run_hgvs(final_nm)))
                elif out_name[l] == "GT":
                    outfile.write("\t%s" % (GT))
                else:
                    outfile.write("\t%s" % (array[dict[out_name[l]]]))
            outfile.write("\n")
    infile.close()
    outfile.close()
    if os.path.exists("%s.hg19_multianno.txt" % (out)):
        subprocess.check_call("rm -rf %s.hg19_multianno.txt" % (out), shell=True)

if __name__=="__main__":
    parser=argparse.ArgumentParser("Run annovar")
    parser.add_argument("-v","--vcf",help="vcf file",required=True)
    parser.add_argument("-o","--outdir",help="output directory",required=True)
    parser.add_argument("-p","--prefix",help="prefix of output",required=True)
    parser.add_argument("-c", "--config", help="config file", required=True)
    args=parser.parse_args()
    run(args.vcf,args.outdir,args.prefix,args.config)