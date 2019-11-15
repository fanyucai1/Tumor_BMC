import os
import sys
import subprocess

picard="/software/picard/picard.jar"
ref="/data/Database/hg19/ucsc.hg19.fasta"
gatk3="/software/gatk/3.7/GenomeAnalysisTK.jar"
bedtools="/software/bedtools/bedtools2/bin/bedtools"
def run(target_bed,probe_bed,bam,outdir,prefix):
    if not os.path.exists(outdir):
        os.mkdir(outdir)
    out=outdir+"/"+prefix
    ####BedToIntervalList (Picard)#############
    cmd="java -jar %s BedToIntervalList I=%s O=%s/target.interval_list SD=%s" %(picard,target_bed,outdir,bam)
    subprocess.check_call(cmd,shell=True)
    cmd = "java -jar %s BedToIntervalList I=%s O=%s/probe.interval_list SD=%s" % (picard, probe_bed, outdir, bam)
    subprocess.check_call(cmd, shell=True)
    ####Metrics generated by CollectHsMetrics for the analysis of target-capture sequencing experiments#######
    cmd="java -Xmx40g -jar %s CollectHsMetrics I=%s O=%s.hs_metrics.txt R=%s TARGET_INTERVALS=%s/target.interval_list" \
        " BAIT_INTERVALS=%s/probe.interval_list COVMAX=1000000 "%(picard,bam,out,ref,outdir,outdir)
    subprocess.check_call(cmd,shell=True)
    ################InsertSize####################
    cmd="java -Xmx40g -jar %s CollectInsertSizeMetrics I=%s O=%s.insert_size_metrics.txt H=%s.insert_size_histogram.pdf"%(picard,bam,out,out)
    subprocess.check_call(cmd,shell=True)
    ####Assess sequence coverage by a wide array of metrics, partitioned by sample, read group, or library#############
    cmd = "java -Xmx40g -jar %s -T DepthOfCoverage -allowPotentiallyMisencodedQuals --minBaseQuality 20 --minMappingQuality 20 -R %s -I %s -o %s " \
          " -ct 1 -ct 10 -ct 20 -ct 50 -ct 100 " \
          " -ct 150 -ct 200 -ct 250 -ct 500 -L %s/target.interval_list --omitDepthOutputAtEachBase --omitIntervalStatistics" \
          % (gatk3, ref, bam, out, outdir)
    subprocess.check_call(cmd, shell=True)
    ################Count On-Target Reads##########
    cmd = os.popen("%s intersect -bed -u -abam %s -b %s | wc -l"%(bedtools,bam,target_bed))
    reads = cmd.read()
    reads = reads.strip()
    outfile = open("%s.MetricsReport.tsv" % (out), "w")
    outfile.write("Counts-On-Target_Reads\t%s\n"%(reads))
    ################################################
    infile = open("%s.insert_size_metrics.txt" % (out), "r")
    num, name, counts = 0, [], 0
    for line in infile:
        line = line.strip()
        array = line.split("\t")
        counts += 1
        if line.startswith("MEDIAN_INSERT_SIZE"):
            num = counts
            for i in range(len(array)):
                name.append(array[i])
        if counts == num + 1 and num != 0:
            print(line)
            outfile.write("meadian_insert_size\t%s\n" % (array[0]))
    infile.close()
    ###############################################
    infile=open("%s.hs_metrics.txt"%(out),"r")
    num=0
    name=[]
    for line in infile:
        if not line.startswith("#"):
            array=line.split("\t")
            if array[0]=="BAIT_SET":
                for i in range(len(array)):
                    name.append(array[i])
                num += 1
            else:
                if num==1 and len(array)==len(name):
                    for i in range(len(array)):
                        if name[i] == "FOLD_80_BASE_PENALTY":
                            outfile.write("FOLD_80_BASE_PENALTY\t%s\n"%(array[i]))
                        if name[i] == "MEAN_TARGET_COVERAGE":
                            outfile.write("mean_depth\t%s\n" % (array[i]))
                        if name[i] == "MEDIAN_TARGET_COVERAGE":
                            outfile.write("median_depth\t%s\n" % (array[i]))
    infile.close()
    ###############################################
    infile = open("%s.sample_summary" % (out), "r")
    num, name = 0, []
    for line in infile:
        num += 1
        line = line.strip()
        array = line.split("\t")
        if num == 1:
            for i in range(len(array)):
                name.append(array[i])
        if num == 2:
            for i in range(len(array)):
                if name[i] == "%_bases_above_1":
                    outfile.write("%%_bases_above_1X\t%s\n" % (array[i]))
                if name[i] == "%_bases_above_20":
                    outfile.write("%%_bases_above_20X\t%s\n" % (array[i]))
                if name[i] == "%_bases_above_50":
                    outfile.write("%%_bases_above_50X\t%s\n" % (array[i]))
                if name[i] == "%_bases_above_100":
                    outfile.write("%%_bases_above_100X\t%s\n" % (array[i]))
                if name[i] == "%_bases_above_200":
                    outfile.write("%%_bases_above_200X\t%s\n" % (array[i]))
                if name[i] == "%_bases_above_250":
                    outfile.write("%%_bases_above_250X\t%s\n" % (array[i]))
                if name[i] == "%_bases_above_500":
                    outfile.write("%%_bases_above_500X\t%s\n" % (array[i]))
    infile.close()
    outfile.close()
    outfile.close()
    subprocess.check_call("rm -rf %s.sample*"%(out),shell=True)
if __name__=="__main__":
    if (len(sys.argv)!=6):
        print("\nUsage:python3 %s target_bed probe_bed bamfile outdir prefix"%(sys.argv[0]))
        print("target_bed and probe_be maybe a same file\n")
        print("the bamfile must remove or mark PCR duplicates\n")
        print("\nEmail:fanyucai1@126.com")
    else:
        target_bed=sys.argv[1]
        probe_bed=sys.argv[2]
        bam=sys.argv[3]
        outdir=sys.argv[4]
        prefix=sys.argv[5]
        run(target_bed,probe_bed,bam,outdir,prefix)

