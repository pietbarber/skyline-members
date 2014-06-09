#!/usr/bin/perl 

		# Where I left off: 
		# The upload section, I was about to write
		# The part where we allow the user to type
		# in information about what the page is about. 

use CGI;		# Allows cool CGI type stuff
use strict;		# Bleck
my $q = new CGI;	# Associate $q with CGI module
			# Temporary directory for where files get temporarily placed
my $tempdir = '/var/www/members/html/ADMIN/tempdir';
			# Directory where document lives
my $memroot = "/var/www/members/html";
my $docroot = "/var/www/skyline/html";
			# These are the months of the year
my @months = qw(
	January February March April
	May June July August September
	October November December
	);
my %months = qw(
	January 	1 
	February	2
	March 		3
	April 		4
	May		5
	June		6
	July		7
	August		8
	September	9
	October		10
	November	11
	December	12
	);
			# These are the years we will accept uploads for.

			# These are the years we will accept uploads for.

			# Find out what the month and year are 
			# for default values. 
my @date = localtime(time);
my $this_month = $months[$date[4]];
my $this_year = $date[5]+1900;
my @years = ( 1995 .. ($this_year+1) );
my %years; 
for (@years) {
  $years{$_}++;
  }

			# Print out starter for html headers. 
print_html_head();

	# If we run this program with 'Upload' as the value for 'mode' variable...
if ($q->param('mode') eq 'Upload') {
	# that means that we are uploading something.  So process uploads
  upload_section();
  ending();
  exit;
  }
else {
	# Otherwise, just take input to allow uploads for 
	# a certain month and year. 
  print_upload_dialog();
  ending();
  exit;
  }

sub print_upload_dialog {
	# Print out some HTML for the dialog box. 
  printf (qq(
%s
<h1>Upload Newsletter</h1>
<table border =1 bgcolor="#E8E8E8">
<tr><td>Month:</td><td>%s</td></tr>
<tr><td>Year:</td><td>%s</td></tr>
  ), 
	$q->start_multipart_form(),
	$q->popup_menu(
		-name => "month", 
		-values => [@months],
		-default => $this_month
	),
	$q->popup_menu(
		-name => "year", 
		-values => [@years],
		-default => $this_year
	)
    );
    printf "<tr><td>Select File:</td><td>%s</td></tr>\n",
	$q->filefield(
		-name => 'uploaded_file',
		-default => 'starting value', 
		);


  printf "<tr><td colspan=\"2\" align=\"center\">%s</td></tr></table>", 
	$q->submit(
		-name => "mode",
		-value => "Upload"
	)
  }

sub print_html_head {
	# Print out HTML headers. 
  print $q->header;
  print qq~<!DOCTYPE HTML PUBLIC "-//W4C//DTD HTML 4.01 Transitional//EN">
<html>
<head>
  <meta http-equiv="Content-Type" content="text/html; charset=utf-8">
  <link rel="SHORTCUT ICON" href="/favicon.ico">
  <title>Document Upload</title>
~;
  include_file ("$memroot/INCLUDES/left-menu.scrap");
  }

sub include_file {
	# Include a file; the name given as the argument
  my $filename = shift;
  open (INCLUDE, "$filename") || die ("I can't find that file $!\n");
  while (<INCLUDE>) {
    print;
    }
  close (INCLUDE);
  }

sub upload_section {
	# Subroutine to process uploaded files. 
	# Go thru a loop of how many files we allow to upload
	# Start another form...
  print $q->start_form();
	# Start a table...
  print qq!<table border = "1" bgcolor="#88FF88">!;
    if ($q->param('uploaded_file') ) {
	# Set filehandle to the contents of this file.
      my $fh=$q->upload('uploaded_file');
	# If errors from the upload... or the filehandle doesn't exist... 
      if (!$fh && $q->cgi_error) {
        print "Error uploading file # $!\n";
        ending();
        exit
        }
	# Otherwise, we should be good to write this to a file... 
      else {  
        my ($bytes) = 0;
        my ($line);
        open (OUTFILE, ">$tempdir/file") || die ("I canna write to that file, in that dir! $! \n");
        while ($line = <$fh>) {
          print OUTFILE $line;
          $bytes += length ($line);
          }
        close (OUTFILE);
        print "<tr><td>File # $_ successfully uploaded.  $bytes bytes written. </td></tr>\n";
	print "<tr><td>Checking to see if this file is a PDF: </td><td>"; 
	my ($filename) = $q->param('uploaded_file');
	my ($type) = $q->uploadInfo($filename)->{'Content-Type'};
	unless ($type eq 'application/pdf') {
		abort ("I need only PDF files to be uploaded, please. ");
		}

	my $upload_month = $q->param('month') if exists $months{$q->param('month')};
	my $upload_year = $q->param('year') if exists $years{$q->param('year')};
	if ( ! $upload_month  || ! $upload_year) {
		abort ("<tr><td>Not a valid month or year.  Catastrophy! Are you trying to hack me? </td></tr>");
		}
	if ( ! -d $docroot . '/NEWSLETTER/' . $upload_year) {
		system ('mkdir', $docroot . '/NEWSLETTER/' . $upload_year);
		}
	if (! -d $docroot . "/NEWSLETTER/$upload_year/$upload_month") {
		system ('mkdir', $docroot . '/NEWSLETTER/' . $upload_year . "/" . $upload_month); 
		}
	if (! -d $docroot . "/NEWSLETTER/$upload_year/$upload_month") {
		abort ("<tr><td>I tried to make the directory for the newsletter, but something happened, and I can't. I tried to create '$docroot/NEWSLETTER/$upload_year/$upload_month' \n</td></tr>");
		}
	else {
		my ($pdf_filename) = sprintf ("%4.4d%2.2dnews.pdf", $upload_year, $months{$upload_month});
		system ('/bin/mv', "$tempdir/file", $docroot . "/NEWSLETTER/$upload_year/$upload_month/$pdf_filename");
		system ('/bin/rm', $docroot . '/NEWSLETTER/previous.pdf');
		system ('/bin/mv', $docroot . '/NEWSLETTER/current.pdf', 'previous.pdf');
		if (-e "$tempdir/file") {
			abort("<tr><td>I couldn't move the file into position, something went wrong. Call Piet$!\n</td></tr>");
			}
		chdir ($docroot . "/NEWSLETTER/");
		system ('/bin/ln', '-s', $docroot . "/NEWSLETTER/$upload_year/$upload_month/$pdf_filename", 'current.pdf');
		chdir ($docroot . "/NEWSLETTER/$upload_year/$upload_month");
		system ('/bin/ln', '-s', $pdf_filename, 'index.pdf');
		print "<br>It looks to me like the newsletter successfully uploaded.  Check out these links to make sure. ";
		print "<br>Current NEWSLETTER full URL:";
	 	print qq~<a href = "http://skylinesoaring.org/NEWSLETTER/$upload_year/$upload_month/">/NEWSLETTER/$upload_year/$upload_month/</a>~;
		print "<br>Current Newsletter link:";
	 	print qq~<a href = "http://skylinesoaring.org/NEWSLETTER/current.pdf">/NEWSLETTER/current.pdf</a>~;
		print "<br>Previous Newsletter link:";
	 	print qq~<a href = "http://skylinesoaring.org/NEWSLETTER/previous.pdf">/NEWSLETTER/previous.pdf</a>~;
		print "<br>If everything looks OK, send an email to: ";
	 	print qq~<a href = "mailto:newsletter-announce\@skylinesoaring.org">newsletter-announce\@skylinesoaring.org</a>~;
		}
      }
    }

  print "</table>\n";
  print $q->end_form;
  }

sub abort {
	print "</table>\n";
	print "</form>\n";
	print join ("\n", @_);
	warn join ("\n", @_) . "\n";
	ending();
	exit;
	}

sub ending {
  print qq~
<!-- End Meat -->
      </td>
    </tr>
  </tbody>
</table>
</body>
</html>~;
  };
