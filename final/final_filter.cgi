#!/usr/bin/perl -w
=begin
Author: Silvia Chang
This script will execute a filtered search based on
user's selected value. A threshold is entered as well.
Default values are assigned when nothing is provided.
When the email is provided, the script will also send the 
MySQL queried results to the user's email.
=cut

use strict;
use CGI;
use warnings;
use CGI::Carp qw(fatalsToBrowser);    # Remove for production use
use Config::IniFiles;
use DBI;
use JSON;
use Data::Dumper;
use MIME::Lite;
use Archive::Tar;

## create our CGI and TMPL objects
my $cgi  = new CGI;

my $cfg = Config::IniFiles->new(-file => "configfile.ini");
my $userid = $cfg->val("user", "name");
my $userpwd = $cfg->val("user", "passwd");
my $host = $cfg->val("connect", "host");
#my $dsn = "DBI:mysql:database=rsem_db; host=$host";
my $dsn = "DBI:mysql:database=schang72; host=$host";
my $opts = {RaiseError=>1, PrintError=>1};
my $dbh = DBI->connect($dsn, $userid, $userpwd, $opts);

my $json = JSON->new->utf8->allow_nonref;

my $email;
$email = $cgi->param('email');

my $cutoff;
$cutoff = $cgi->param("cutoff");
#$cutoff = "1500";

my $type = $cgi->param("reads");

#my $type = "tpm";
if(defined($cutoff)){
	$cutoff = $cutoff*1;
}
else{

	$cutoff = 1000;
}

## initialize an empty arrayref to store the search matches
my $matches = [];

my $qry;

if ($type eq "fpkm") {
	$qry = qq{
    SELECT g.GeneID, i.TranscriptID, i.IsoPct, g.Gene_TPM, i.Trans_TPM, g.Gene_FPKM, i.Trans_FPKM
    FROM genes g
    JOIN link l on l.GeneID=g.GeneID
    JOIN isoforms i on i.TranscriptID=l.TranscriptID
    WHERE g.Gene_FPKM >= ?
	};
} else  {
	$qry = qq{
    SELECT g.GeneID, i.TranscriptID, i.IsoPct, g.Gene_TPM, i.Trans_TPM, g.Gene_FPKM, i.Trans_FPKM
    FROM genes g
    JOIN link l on l.GeneID=g.GeneID
    JOIN isoforms i on i.TranscriptID=l.TranscriptID
    WHERE g.Gene_TPM >= ?
	};
}
my $dsh = $dbh->prepare($qry);
$dsh->execute($cutoff);


#Submit full query
while (my $row = $dsh->fetchrow_hashref) {
	## push the row to the match array
	push @$matches, $row;
}

# Send results to email if email provided
if ($email eq "") {
	#do nothing 
} else{
	$dsh = $dbh->prepare($qry);
	$dsh->execute($cutoff);
	my $temp= "";
	my @rows=();
	while( @rows = $dsh-> fetchrow){
		foreach my $val (@rows) {
			$temp .= $val;
			$temp .=",";
		}
		$temp .= "\n";
	}
	my $dir ="/tmp/schang72";
	my $result_file = "$dir/results.csv";
	open (OUTFILE, ">$result_file") || die "Error: Cannot open file!";
	print OUTFILE $temp;
	close OUTFILE;
	send_email($email, $result_file);
}

$dsh->finish;
$dbh->disconnect;

## print the header and JSON data
print $cgi->header('application/json');
print $json->encode(
	{ match_count => scalar( @$matches ), matches => $matches }
);

##### Subroutines ####
# function to send results to an email

sub send_email {
	my($email, $file) = @_;

# Options to tar files if needed
#	my $tar = Archive::Tar ->new;
#	$tar->add_files($file);
#	$tar->write("output.tar");

	my $cc = "";
	my $from = 'schang72@jhu.edu';
	my $subject = 'Filtered Results';
	my $message = 'This contains the output results';

	my $msg = MIME::Lite->new(
                 From 	  => $from,
                 To       => $email,
                 Cc       => $cc,
                 Subject  => $subject,
                 Type     => 'multipart/mixed'
                 );
                 
	# Add your text message.
	$msg->attach(Type        => 'text',
             	Data         => $message
            );
            
	# Specify your file as attachement.
	$msg->attach(Type    => "AUTO",
             Path        => $file,
             Filename    => $file,
             Disposition => 'attachment'
            );       
	$msg->send;
}