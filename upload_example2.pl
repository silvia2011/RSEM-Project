#!/usr/bin/perl -w
# A sample file upload script
# www.perlmeme.org

use strict;
use warnings;
use CGI;
use CGI::Carp qw(fatalsToBrowser);    # Remove for production use
use HTML::Template;

# $CGI::POST_MAX = 1024 * 100;  # maximum upload filesize is 100K

sub save_file($);

my $q = new CGI;
my $tmpl = HTML::Template->new(filename => 'tmpl/final_project.tmpl');
print $q->header('text/html');

#$tmpl-> param(PAGE_TITLE => "RSEM Project");
#$tmpl-> param(PAGE_HEADER => "SChang Final Project");
#
#print $tmpl->output;

# Upload the file
if ($q->param()) {
	save_file($q);
}

#-------------------------------------------------------------

sub save_file($) {
	my ($q) = @_;
    my ($bytesread, $buffer);
    my $num_bytes = 1024;
    my $totalbytes;
    my $filename = $q->upload('filename');
    my $untainted_filename;

    if (!$filename) {
    	print $q->p('You must enter a filename before you can upload it');
    	return;
    }

    # Untaint $filename

    if ($filename =~ /^([-\@:\/\\\w.]+)$/) {
        $untainted_filename = $1;
    } else {
        die "Unsupported characters in the filename '$filename'.\nYour filename may only contain alphabetic characters and numbers, and the characters '_', '-', '\@', '/', '\\' and '.'";
    }

    if ($untainted_filename =~ m/\.\./) {
    	die "Your upload filename may not contain the sequence '..'\nRename your file so that it does not include the sequence '..', and try again.";
    }

    my $file = "/tmp/schang72/$untainted_filename";
    print "Uploading $filename<BR>";

    # If running this on a non-Unix/non-Linux/non-MacOS platform, be sure to 
    # set binmode on the OUTFILE filehandle, refer to 
    #    perldoc -f open 
    # and
    #    perldoc -f binmode

    open (OUTFILE, ">", "$file") or die "Couldn't open $file for writing: $!";
    while ($bytesread = read($filename, $buffer, $num_bytes)) {
	    $totalbytes += $bytesread;
        print OUTFILE $buffer;
    }
    die "Read failure" unless defined($bytesread);
    unless (defined($totalbytes)) {
    	print "<p>Error: Could not read file ${untainted_filename}, ";
        print "or the file was zero length.";
    } else {
        print "<p>Done. File $filename uploaded ($totalbytes bytes)";
    }
    close OUTFILE or die "Couldn't close $file: $!";

    }
#-------------------------------------------------------------