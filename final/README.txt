* ABOUT *

Front-end web utility for processing RNA-Seq transcript assembly files. 
This utility allows for searching and filtering of specified genes/transcripts from RSEM
assembly outputs.

Source code and demo can be found at:
http://bfx.eng.jhu.edu/schang72/final_project/final.tar.gz

* BACKGROUND *

RSEM is a software package used for estimating gene and isoform expression levels from 
RNA-Seq data. The main outputs of the tool are two files: genes.results and isoforms.results. 
These transcript assembly files contain abundance levels and other properties pertaining to
the reads. 

More information can be found in:
http://deweylab.biostat.wisc.edu/rsem/

An example of RSEM outputs can be found here:
http://trinityrnaseq.sourceforge.net/analysis/abundance_estimation.html

This front-end web utility combines the two files for an initial evaluation of the outputs
before proceeding to further analysis of the assemblies. 

Main functionalities include:
	* User uploads the two RSEM output files.
	* Search for a specified gene/transcript by gene ID.
	* Filter genes by specific TPM or FPKM threshold.
	* Send filtered results to user's email.

The end result shows a final table with both genes and isoforms properties.

* PREREQUISITES *
	* Perl v5.10 or later
	* MySQL v5.1.73 or later
	* Linux 2.6.32 or Darwin Kernel version 13.3.0 or later

Storage is minimal. Data transfer should be at least 2 Mb for reasonable
processing times.

Recommended memory/cpu is 2.0 GB.

* USAGE *

1. Go to the Main.html page. Upload two files: the isoforms.results and genes.results files. 
Ensure that both names the "isoforms" or "genes" words in them.

2. The web utility will upload the files and process them into a MySQL database. Processing 
time varies depending on the file size. 

3. Once finished, you will be redirected to a new page allowing you to query your results 
based on a specific gene ID. An autocomplete functionality is implemented if you start typing
the first three letters of your gene.

5. You can also query your results by filtering the data based on a specified cutoff value.

4. When using the filter function, only the top 500 hits will be displayed. 
Consider entering your email address to see the full results. A compressed .csv file is sent.

5. The displayed results will contain your geneID, transcriptID (isoforms) and each of their
respective TPMs and FPKMs, as well as the isoforms percent abundances.


* DEMO DATA *

Truncated RSEM outputs and sample database (.sql) can be found in:

http://bfx.eng.jhu.edu/schang72/final_project/final.tar.gz

