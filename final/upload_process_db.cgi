#!/usr/bin/perl -w
# Author: Silvia Chang
# Upload user provided files into the server's directory
# Process the files (parse) and enter them into 
# MySQL database
# At the end, this will redirect to the search/filter webpage

use warnings;
use strict;
use CGI;
use CGI::Carp qw(fatalsToBrowser);
use Data::Dumper;
use Config::IniFiles;
use DBI;

my $form = new CGI;
my @uploaded_files=();
my $untainted_filename;
my ($bytesread, $buffer);
my $num_bytes = 1024;
my $totalbytes;

# Verify that two files are entered
my @getfiles = $form->param("filename");
foreach my $get (@getfiles) {
	if (!$get) {
        print $form->header("text/html");
        die "You must enter a file before you can upload";
	}
}

### Start uploading files
my @filehandle = $form->upload("filename");
foreach my $filename (@filehandle){
	# Untaint $filename
	if ($filename =~ /^([-\@:\/\\\w.]+)$/) {
		$untainted_filename = $1;
	} else {
		die "Unsupported characters in the filename '$filename'.\nYour filename may only contain alphabetic characters and numbers, and the characters '_', '-', '\@', '/', '\\' and '.'";
	}
	
	if ($untainted_filename =~ m/\.\./) {
		die "Your upload filename may not contain the sequence '..'\nRename your file so that it does not include the sequence '..', and try again.";
	}
	my $dir ="/tmp/schang72";	
	my $file = "$dir/$untainted_filename";
	push @uploaded_files, $file;
	
	# If running this on a non-Unix/non-Linux/non-MacOS platform, be sure to 
	# set binmode on the OUTFILE filehandle, refer to perldoc -f open 
	# and perldoc -f binmode
	
	# Save uploaded file into same directory
	open (OUTFILE, ">$file") or die "Couldn't open $file for writing: $!";
	while ($bytesread = read($filename, $buffer, $num_bytes)) {
		$totalbytes += $bytesread;
	    print OUTFILE $buffer;
	    }
    close OUTFILE or die "Couldn't close $file: $!";
}


### Start processing the uploaded file
# Parsing the RSEM output files
my ($isoform_res, $gene_res) = ("","");

#$isoform_res="/tmp/schang72/test.isoforms.results";
#$gene_res="/tmp/schang72/test.genes.results";

if($uploaded_files[0] =~ m/isoforms/i) {
	$isoform_res = $uploaded_files[0];
	$gene_res = $uploaded_files[1];
} elsif ( $uploaded_files[1] =~ m/isoforms/i){
	$isoform_res = $uploaded_files[1];
	$gene_res = $uploaded_files[0];
} else {
	die  "ERROR: Could not get files or files extensions do not match.";
}

open(ISO, "<$isoform_res") || die "ERROR: Cannot open the isoforms.results file.";
open(GENE, "<$gene_res") || die "ERROR: Cannot open the genes.results file";

# Connect to database 
my $cfg = Config::IniFiles->new(-file => "configfile.ini");
my $userid = $cfg->val("user", "name");
my $userpwd = $cfg->val("user", "passwd");
my $host = $cfg->val("connect", "host");
#my $dsn = "DBI:mysql:database=schang72_rsem; host=$host";
my $dsn = "DBI:mysql::$host";
my $opts = {RaiseError=>1, PrintError=>1};

my $dbh = DBI->connect($dsn, $userid, $userpwd, $opts);

# Create database and tables 
#$dbh->do("CREATE DATABASE IF NOT EXISTS rsem_db"); # no rights to create databases
#$dbh->do("USE rsem_db");
$dbh->do("USE schang72"); # use existing database

# Create new tables if they don't exist
my @mysql_tables = ( 
			# Create main table
			"CREATE TABLE IF NOT EXISTS link (
				TranscriptID varchar(100) NOT NULL PRIMARY KEY,
				GeneID varchar(100) NOT NULL);",
			# Create gene table
			"CREATE TABLE IF NOT EXISTS genes (
				GeneID varchar(100) NOT NULL PRIMARY KEY,
				Gene_length int NOT NULL,
				Gene_effective_length decimal(10,2) NOT NULL,
				Gene_expcount decimal(10,2) NOT NULL,
				Gene_TPM decimal(10,2) NOT NULL, 
				Gene_FPKM decimal(10,2) NOT NULL);",
			# Create isoform table
			"CREATE TABLE IF NOT EXISTS isoforms (
				TranscriptID varchar(100) NOT NULL PRIMARY KEY,
				Trans_length int NOT NULL,
				Trans_effective_length decimal(10,2) NOT NULL,
				Trans_expcount decimal(10,2) NOT NULL,
				Trans_TPM decimal(10,2) NOT NULL,
				Trans_FPKM decimal(10,2) NOT NULL,
				IsoPct decimal(10,2) NOT NULL);"
				);
# Execute all create table statements
for my $statement (@mysql_tables){
	$dbh->do($statement);
}

# Clear all previous data from tables and recreate them as empty tables
my @clear = (
		# Clear link table
		"DELETE FROM link;",
		"DELETE FROM genes;",
		"DELETE FROM isoforms;"
		);
for my $delete (@clear){
	$dbh->do($delete);
}


# Insert statements into the link and isoforms tables
my @link_columns = ();
my $insert_link = qq{ INSERT INTO link (TranscriptID, GeneID) 
						VALUES (?, ?)};
my $insert_iso = qq{ INSERT INTO isoforms (TranscriptID, Trans_length, Trans_effective_length, Trans_expcount, Trans_TPM, Trans_FPKM, IsoPct)
					VALUES (?, ? ,?, ?, ?, ?, ?)};

my $dsh=$dbh->prepare($insert_link);
					
# Insert isoforms values into link and isoform tables from isoforms.results file
foreach my $line (<ISO>) {
	chomp($line);
	next if($line =~ /^transcript_id/);
	@link_columns = split("\t", $line);
	$dsh = $dbh->prepare($insert_link);
	$dsh->execute($link_columns[0], $link_columns[1]);
	$dsh = $dbh->prepare($insert_iso);
	$dsh->execute($link_columns[0], $link_columns[2], $link_columns[3], $link_columns[4], $link_columns[5], $link_columns[6], $link_columns[7]);
}
close ISO;

my @gene_cols = ();
my $insert_gene = qq{INSERT INTO genes (GeneID, Gene_length, Gene_effective_length, Gene_expcount, Gene_TPM, Gene_FPKM)
					VALUES (?, ?, ?, ?, ?, ?)};

# Insert genes values into genes table from genes.results file
foreach my $line2 (<GENE>) {
	chomp($line2);
	next if ($line2 =~ /^gene_id/);
	@gene_cols = split("\t", $line2);
	$dsh = $dbh->prepare($insert_gene);
	$dsh->execute($gene_cols[0], $gene_cols[2], $gene_cols[3], $gene_cols[4], $gene_cols[5], $gene_cols[6]);
}
close GENE;

$dsh->finish();
$dbh->disconnect();

# Redirect to the search page after finishing uploading and processing into MySQL
print $form->redirect("http://bfx.eng.jhu.edu/schang72/final_project/search_filter_page.html");
