#!/usr/bin/perl -w

use strict;
use CGI;
use warnings;
use CGI::Carp qw(fatalsToBrowser);    # Remove for production use
use Config::IniFiles;
use DBI;
use JSON;

## create our CGI and TMPL objects
my $cgi  = new CGI;

my $cfg = Config::IniFiles->new(-file => "configfile.ini");
my $userid = $cfg->val("user", "name");
my $userpwd = $cfg->val("user", "passwd");
my $host = $cfg->val("connect", "host");
my $dsn = "DBI:mysql:database=rsem_db; host=$host";
#my $dsn = "DBI:mysql:database=schang72; host=$host";
my $opts = {RaiseError=>1, PrintError=>1};
#my $dbh = DBI->connect($dsn, '$userid', '$userpwd', $opts);
my $dbh = DBI->connect($dsn, 'root', 'mysql@pwd', $opts);

my $json = JSON->new->utf8->allow_nonref;

my $term = "comp106761_c0";
#my $term;
my $maxRows;
#$term = $cgi->param('search_gene_id');

if(defined($term)){
	#do nothing
}
else{
	#Get maxRows and reset term
	$maxRows = $cgi->param('maxRows');
	$term = $cgi->param('transcript_id');
}

## initialize an empty arrayref to store the search matches
my $matches = [];

my $qry = qq{
    SELECT g.GeneID, i.TranscriptID, i.IsoPct, g.Gene_TPM, i.Trans_TPM, g.Gene_FPKM, i.Trans_FPKM
    FROM isoforms i
    JOIN link l on l.TranscriptID=i.TranscriptID
    JOIN genes g on g.GeneID=l.GeneID
    WHERE g.GeneID LIKE ?
    OR i.TranscriptID LIKE ?
};

my $dsh = $dbh->prepare($qry);

$dsh->execute("\%$term\%", "\%$term\%");

if(defined($maxRows)){
	#Limit the rows returned if maxRows is defined.
	for(my $i = 0; $i < $maxRows && defined(my $row = $dsh->fetchrow_hashref); $i++) {
		## push the row to the match array
		push @$matches, $row;
	}
}
else{
	#Submit full query
	while (my $row = $dsh->fetchrow_hashref) {
		## push the row to the match array
		push @$matches, $row;
	}
}

$dsh->finish;
$dbh->disconnect;

## print the header and JSON data
print $cgi->header('application/json');
print $json->encode(
	{ match_count => scalar( @$matches ), matches => $matches }
);