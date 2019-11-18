##   样本质控：
    
关于对panel测序数据对质控非常重要，其中一些关键指标可以参考在线文档：

http://netdocs.roche.com/DDM/Effective/07187009001_RNG_SeqCap-EZ_TchNote_Eval-data_v2.1.pdf

此外FOLD_80_BASE_PENALTY这个指标是评价panel性能又一关键指标，对于外显子测序该指标为2-4之间对该指标对解释说明可以参见：

https://twistbioscience.com/sites/default/files/resources/2018-10/Twist_NGS_WhitePaper_UniformityonTarget_18Sep18.pdf

sample_qc.py

This script will given a metrix of bam file stat.

    Usage:python3 sample_qc.py target_bed probe_bed bamfile outdir prefix
    
    target_bed and probe_be maybe a same file
    
    the bamfile must remove or mark PCR duplicates
    
    Email:fanyucai1@126.com

The result output as follows::

        Counts-On-Target_Reads	2051625
        MEDIAN_INSERT_SIZE	200
        mean_depth	967.210889
        median_depth	1157
        FOLD_80_BASE_PENALTY	3.202685
        %_bases_above_1X	97.9
        %_bases_above_10X	95.9
        %_bases_above_20X	94.7
        %_bases_above_50X	91.4
        %_bases_above_100X	87.9
        %_bases_above_200X	84.5
        %_bases_above_250X	83.1
        %_bases_above_500	78.2

fastq_qc.py

This script will filter fastq files and stat raw data.


        usage: QC using fastp. [-h] -p1 PE1 -p2 PE2 [-o OUTDIR] [-p PREFIX] [-l MINLEN]
        optional arguments:
          -h, --help            show this help message and exit
          -p1 PE1, --pe1 PE1    5 reads
          -p2 PE2, --pe2 PE2    3 reads
          -o OUTDIR, --outdir OUTDIR
                                output directory
          -p PREFIX, --prefix PREFIX
                                prefix of output
          -l MINLEN, --minlen MINLEN
                                min length output default is 75
So A P, Vilborg A, Bouhlal Y, et al. A robust targeted sequencing approach for low input and variable quality DNA from clinical samples[J]. NPJ genomic medicine, 2018, 3(1): 2. 

Pindel.py

    Run Pindel for Long Indels & MNPS (32bp-350bp)    
