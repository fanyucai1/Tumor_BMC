import os
import sys
import re

def run(fastq_dir,bam_stat_dir,outdir):
    if not os.path.exists(outdir):
        os.mkdir(outdir)
    ####################################
    SampleID,Raw_reads,Q30_R1,Q30_R2,Clean_reads=[],{},{},{},{}
    for(root,dirs,files) in os.walk(fastq_dir):
        for file in files:
            tmp=os.path.join(root,file)
            if tmp.endswith("csv"):
                infile=open(tmp,"r")
                num=0
                for line in infile:
                    num+=1
                    line=line.strip()
                    array=re.split(r'[\t,]',line)
                    Raw_reads[tmp.split("/")[-2]]=array[1]
                    Q30_R1[tmp.split("/")[-2]]=array[2]
                    Q30_R2[tmp.split("/")[-2]] =array[3]
                    Clean_reads[tmp.split("/")[-2]]=array[4]
                SampleID.append(tmp.split("/")[-2])
                infile.close()
    ####################################
    Target_Reads, insert_size, mean_depth, median_depth = {}, {}, {}, {}
    base1, base20, base50, base100, base200, base250, base500 = {}, {}, {}, {}, {}, {}, {}
    FOLD_80_BASE_PENALTY,dup,align = {},{},{}
    for (root, dirs, files) in os.walk(bam_stat_dir):
        for file in files:
            tmp = os.path.join(root, file)
            if tmp.endswith("bam.stat.tsv"):
                infile = open(tmp, "r")
                num = 0
                for line in infile:
                    num += 1
                    line = line.strip()
                    array=re.split(r'[\t,]',line)
                    if num==1:
                        Target_Reads[tmp.split("/")[-2]]=array[1]
                    if num==2:
                        insert_size[tmp.split("/")[-2]]=array[1]
                    if num == 3:
                        mean_depth[tmp.split("/")[-2]]=array[1]
                    if num == 4:
                        median_depth[tmp.split("/")[-2]]=array[1]
                    if num == 5:
                        FOLD_80_BASE_PENALTY[tmp.split("/")[-2]]=array[1]
                    if num == 6:
                        base1[tmp.split("/")[-2]]=array[1]
                    if num == 7:
                        base20[tmp.split("/")[-2]] = array[1]
                    if num == 8:
                        base50[tmp.split("/")[-2]] = array[1]
                    if num == 9:
                        base100[tmp.split("/")[-2]] = array[1]
                    if num == 10:
                        base200[tmp.split("/")[-2]] = array[1]
                    if num == 11:
                        base250[tmp.split("/")[-2]] = array[1]
                    if num == 12:
                        base500[tmp.split("/")[-2]] = array[1]
                    if num==13:
                        align[tmp.split("/")[-2]] = array[1]
                infile.close()
            if tmp.endswith("marked_dup_metrics.txt"):
                infile=open(tmp,"r")
                num,counts=0,0
                for line in infile:
                    num+=1
                    line=line.strip()
                    array=line.split("\t")
                    if re.search(r'PERCENT_DUPLICATION',line):
                        counts=num
                    if counts!=0 and num==counts+1:
                        dup[tmp.split("/")[-2]]=array[-2]
                infile.close()
    ####################################
    outfile=open("%s/MetricsReport.tsv"%(outdir),"w")
    outfile.write("[Run Metrics]\n")
    outfile.write("Metric(UOM)\tLSL Guideline\tUSL Guideline")
    for i in range(len(SampleID)):
        outfile.write("\t%s"%(SampleID[i]))
    outfile.write("\nPCT_Q30_R1(%)\t80.0\tNA")
    for i in range(len(SampleID)):
        outfile.write("\t%.2f" % (float(Q30_R1[SampleID[i]])*100))
    outfile.write("\nPCT_Q30_R2(%)\t80.0\tNA")
    for i in range(len(SampleID)):
        outfile.write("\t%.2f" % (float(Q30_R2[SampleID[i]])*100))
    outfile.write("\n\n")
    ###########################
    outfile.write("[DNA Library QC Metrics for Small Variant Calling]\n")
    outfile.write("Metric(UOM)\tLSL Guideline\tUSL Guideline")
    for i in range(len(SampleID)):
        outfile.write("\t%s"%(SampleID[i]))
    outfile.write("\nMEDIAN_INSERT_SIZE(bp)\t70\tNA")
    for i in range(len(SampleID)):
        outfile.write("\t%s"%(insert_size[SampleID[i]]))
    outfile.write("\nMEDIAN_COVERAGE(Count)\t150\tNA")
    for i in range(len(SampleID)):
        outfile.write("\t%s"%(median_depth[SampleID[i]]))
    outfile.write("\nPCT_50X(%)\t90.0\t100.0")
    for i in range(len(SampleID)):
        outfile.write("\t%s"%(base50[SampleID[i]]))
    ############################
    outfile.write("\n\n[DNA Expanded Metrics]\n")
    outfile.write("Metric(UOM)\tLSL Guideline\tUSL Guideline")
    for i in range(len(SampleID)):
        outfile.write("\t%s"%(SampleID[i]))
    outfile.write("Raw_read(Counts)\tNA\tNA")
    for i in range(len(SampleID)):
        outfile.write("\t%s"%(Raw_reads[SampleID[i]]))
    outfile.write("\nTarget_read(Counts)\tNA\tNA")
    for i in range(len(SampleID)):
        outfile.write("\t%s"%(Target_Reads[SampleID[i]]))
    outfile.write("\nMEAN_TARGET_COVERAGE(Counts)\tNA\tNA")
    for i in range(len(SampleID)):
        outfile.write("\t%s"%(mean_depth[SampleID[i]]))
    outfile.write("\nPCT_TARGET_100X(%)\tNA\tNA")
    for i in range(len(SampleID)):
        outfile.write("\t%s"%(base100[SampleID[i]]))
    outfile.write("\nPCT_TARGET_250X(%)\tNA\tNA")
    for i in range(len(SampleID)):
        outfile.write("\t%s" % (base250[SampleID[i]]))
    outfile.write("\nDuplication(%)\tNA\tNA")
    for i in range(len(SampleID)):
        outfile.write("\t%.2f" % (float(dup[SampleID[i]])*100))
    outfile.write("\nPCT_ALIGNED_READS(%)\tNA\tNA")
    for i in range(len(SampleID)):
        outfile.write("\t%s" % (align[SampleID[i]]))
    outfile.write("\n")
    outfile.close()

if __name__=="__main__":
    if len(sys.argv)!=4:
        print("usage:python3 %s fastq_dir bam_stat_dir output_dir\n"%(sys.argv[0]))
        print("Email:fanyucai1@126.com")
    else:
        fastq_dir, bam_stat_dir, outdir=sys.argv[1],sys.argv[2],sys.argv[3]
        run(fastq_dir, bam_stat_dir, outdir)
