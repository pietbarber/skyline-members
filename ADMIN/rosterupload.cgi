#!/usr/bin/perl 

	# Use CGI
	# use database
	# use ugly ass old school Berkeley DB
	# take input in the form of an uploaded file
	# that uploaded file has to have the right kind of 
	# format, too, and just jam that shit into the current running
	# Berkely db for the current roster stuff. 
	# hope this shit works. 

	# Piet Barber 2010-06-05

use strict; 
use CGI qw(:standard); 
use DBI;
print header();
my ($DEBUG)		= 1; 
my ($dbh)		= DBI->connect("dbi:Pg:dbname=skyline");
my (%towpilots)		= fetch_db ('towpilot');
my (%towpilots1)	= fetch_db ('towpilot');
my (%towpilots2)	= fetch_db ('towpilot');
my (%instructors)	= fetch_db ('instructor');
my (%duty)		= fetch_db ('dutyofficer');
my (%ados)		= fetch_db ('ado');
my (%ROSTER); 
dbmopen (%ROSTER, "/home/httpd/db/roster", 0666);
my (%roster) = %ROSTER;
dbmclose (%ROSTER);
my (%newroster); 

open (INPUT, "/home/httpd/db/roster-info.database");
my ($q);
while (!eof(INPUT)) {
  $q=new CGI(INPUT); 
  }
close (INPUT); 


for my $key ($q->param) {
  printf "%s => %s<br>", $key, $q->param($key); 
  }



if (!param()) { 
  print header(); 
  print "Please to uploading your text file now.  Be careful! It overwrite everything!\n";   
  print start_multipart_form();
  print filefield (
	-name => 'upload',
	-default => 'filename.txt',
	-size => 20
	); 
  print submit (
	-value => 'Submit for uploading',
	);
  endform(); 
  }

elsif (param('upload')) {
  print header(); 
  my ($filename) = param ('upload'); 
  my ($contents); 
  print param('upload'); 
  while (my $line =<$filename>) {
    $contents .= $line; 
     
    }
  print pre($contents); 
  
  check_input_pls();
  }

sub check_input_pls {
  }

sub fetch_db {
	# Please to be talking to Psql database
	# and fetching the type of member based on
	# $type 
  my (%answer);
  my ($type)  = shift;
  my ($sql) = qq(select rostername, lastname from members
        where $type = true
        and memberstatus != 'I'
        and memberstatus != 'N'
        );
  #warn "SQL: $sql";
  my ($get_info) = $dbh->prepare($sql);
  $get_info -> execute();
  while (my $ans = $get_info->fetchrow_hashref()) {
    if ($ans->{'rostername'}) {
      $answer{$ans->{'rostername'}} = 1;
      }
    elsif ($ans->{'lastname'}) {
      $answer{$ans->{'lastname'}} = 1;
      }
    }

  if ($type eq 'ado') {
        # If this is an ADO, we can put the DOs in there too.
    for (keys (%duty))  {
      $answer{'* ' . $_} = 1;
      }
    }
  %answer;
  }



sub find_name {
        # Since we get input with names that could be
        # Bob Meister
        # Robert Meister
        # Rob Mister
        # Robert C Mister
        # all meaning the same person, it seems silly for us to put these
        # directly into the database as-is.  I came up with a new table called "aliases"
        # which has a many to one relationship for all the different sorts of ways a name
        # could be misspelled; and we'll give them a handle as output.
        # select handle from aliases where name "George Hazelrigg";
        # will return you "ghazelrigg"
        # if you set name to "George Hazelrigg, Jr" you would get same result.
        # That's the best I could come up with, honestly.
        # So this subroutines takes a name as input,
        # hits the DB up for a handle
        # and returns a handle if it's available,
        # or returns the original input if it's not in the aliases table.
        # We also check the members table just in case the dude doesn't have an entry in the
        # aliases table for whatever reason.
        # Only do that if there is no entry in the aliases table.
  my ($input) = shift;
  return "" if $input eq '';
  my ($answer);
  my ($lname, $fname) = $2, $1
        if ($input =~ /^\s*(\w+)\s+(\w+)\s*$/);
  if (!$dbh) {
    db_connectify();
    }
  my($get_info) = $dbh->prepare("select distinct handle from aliases where name ='$input'");
  $get_info->execute();
  while (my $ans = $get_info->fetchrow_hashref()) {
    $answer = $ans->{'handle'};
    warn "Answer is '$answer', input was '$input'\n" if $DEBUG;
    }
  if ($answer eq '') {
    $dbh->prepare("select distinct handle from members where lastname='$lname' and firstname='$fname' and memberstatus != 'N' and memberstatus != 'I'");
    $get_info->execute();
    while (my $ans = $get_info->fetchrow_hashref()) {
      $answer = $ans->{'handle'};
      }
    }

  if ($answer eq '') {
    warn "No handle found for user '$input'. \n";
    $answer=$input;
    }
  $answer;
  }



