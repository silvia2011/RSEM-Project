#!/usr/bin/perl -w
# Final Project
# RSEM output files processing
# 2nd portion of the final project
# parse the RSEM output files and store into MySQL database

use strict;
use warnings;
use CGI;
use CGI::Carp qw(fatalsToBrowser);    # Remove for production use
use Config::IniFiles;
use DBI;

my @uploaded_files = ("RSEM.genes.results", "RSEM.isoforms.results");

my $cfg = Config::IniFiles->new(-file => "configfile.ini");
my $userid = $cfg->val("user", "name");
my $userpwd = $cfg->val("user", "passwd");
my $host = $cfg->val("connect", "host");
#my $dsn = "DBI:mysql:database=schang72_rsem; host=$host";
my $dsn = "DBI:mysql::$host";
my $opts = {RaiseError=>1, PrintError=>1};
my $dbh = DBI->connect($dsn, 'root', 'mysql@pwd', $opts);
#my $dbh = DBI->connect($dsn, $userid, $userpwd, $opts);

# Create database and tables 
$dbh->do("CREATE DATABASE IF NOT EXISTS rsem_db");
$dbh->do("USE rsem_db");
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

my ($isoform_res, $gene_res) = ("","");
# Parsing the RSEM output files
if($uploaded_files[0] =~ m/\w+\.isoforms\.\w*/i) {
	$isoform_res = $uploaded_files[0];
	$gene_res = $uploaded_files[1];
} elsif ( $uploaded_files[1] =~ m/\w+\.isoforms\.\w*/i){
	$isoform_res = $uploaded_files[1];
	$gene_res = $uploaded_files[0];
} else {
	die  "ERROR: Files extensions do not match.";
}

open(ISO, "<$isoform_res") || die "ERROR: Cannot open the isoforms.results file.";
open(GENE, "<$gene_res") || die "ERROR: Cannot open the genes.results file";

my @link_columns = ();
my $insert_link = qq{ INSERT INTO link (TranscriptID, GeneID) 
						VALUES (?, ?)};
my $insert_iso = qq{ INSERT INTO isoforms (TranscriptID, Trans_length, Trans_effective_length, Trans_expcount, Trans_TPM, Trans_FPKM, IsoPct)
					VALUES (?, ? ,?, ?, ?, ?, ?)};
my $dsh="";					
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