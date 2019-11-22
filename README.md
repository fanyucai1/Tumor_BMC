1.  Bcl2fastq

2.  Raw data(QC)
        ------sub/fastq_qc.py

3.  Map to Reference and Mark Duplicates
        ------sub/bwa_picard.py

4.  Realign Indels and Base (Quality Score) Recalibration
        ------sub/BRSR.py

5.  Call SNP and Indel
        ------
            planeA:sub/Mutect.py
            planeB:sub/vardict.py

6.  Call CNV
        ------sub/cnvkit.py(attetion:control directory contains normal bam )

7.  annotation(annovar)

8.  fusion(genefuse)
     