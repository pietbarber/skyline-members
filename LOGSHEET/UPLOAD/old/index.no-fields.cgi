#!/usr/bin/perl 
	# A simple program to upload logsheets
	#  .... turns into not so simple a program to verify all the gunk
	#  before comitting it to the database. 

use strict;
	# We gonna use the DB
use DBI;
	# We gonna use CGI
use CGI qw/:standard/; 
	# These are our variables that are global. 
	# $root is for CGI, %logsheet is to store logsheet stuff
	# $dbh is our database handle, so we don keep opening new
	# instances of the database. 
	# @flight_sql is the SQL we are going to use when we go into
	# the database, @contacts_sql is the list of contacts that 
	# came up in the submitted template, and towplots_sql is same,
	# but for towpilots. 
my ($root, %logsheet, $dbh, @flight_sql, @contacts_sql, @towpilots_sql, %tow_count);

#############################
#   Debugging!   
#############################

#my ($DEBUG) = 1; # I need more output 
my ($DEBUG) = 0; # Shut yer mouth, i don't want you yappin about everything. 
	# Comment out whichever above is less appropriate. 


	# header() is a subroutine that makes sure that we are printing
	# the html and content type stuff that is necessary for 
	# a working CGI page. 
print header();
	# and this is where we print the header of the HTML with a title.
start_html( 'Logsheet Upload');

	# If we had a logsheet uploaded here, then do this stuff. 
if (param('logsheet_upload') ne /\w/) {
	# On the off chance that this was an upload with the 
	# upload field, convert it into the logsheet_contents variable. 
  my ($filename) = param('logsheet_upload');
  my ($contents); 
  while (my $line=<$filename>) {
    $contents .= $line; 
    } 
  param('logsheet_contents', $contents);
  }

	# If the logsheet contents contains   stuff
	# Then process it. 
if (param('logsheet_contents') ne /\w/) {
  print include('left-menu.scrap');
  print 	"Received Logsheet.  Processing.... <br>\n";
  print 	qq(<table border = "1" bgcolor = "#F8F8F8">\n);
  print 	qq(<tr><td>Checking for general non-corruptedness...</td>\n);
  check_one(); 
  print 	qq(<tr><td>Converting into XML</td>\n);
  check_two(); # Convert into XML
  print 	qq(<tr><td>Checking for stuff within the submitted data. </td>\n);
  check_three($root); 	# Check contents of submitted data
  print 	qq(<tr><td>Checking for previous submissions for this date...</td>\n);
  if (param('date_override') eq 'duplicate') {
	destroy_old_info();
	}
  else {
	check_for_previous($logsheet{'operations_date'});
	}
  print 	qq(<tr><td>Staff Members for this date: </td>\n);
  #print_out_staff($root->{'LogSheet'}->{'LogSheet_staff'}->{'StaffInfo'});
  print_out_staff($root->{'LogSheet'}->{'LogSheet_staff'}->{'StaffData'}); # New revision
  print 	qq(<tr><td>New Contacts</td>\n); 
  new_contacts($root->{'LogSheet'}->{'LogSheet_new-contacts'}->{'ContactList'});   # Should be OK
  print		qq(<tr><td>Writing about new members, if applicable.</td></tr>\n);
  write_new_members($root->{'LogSheet'}->{'LogSheet_new-contacts'}->{'ContactList'}); # Should be OK
  print 	qq(<tr><td>Flight Information</td>\n);
  #flight_information($root->{'LogSheet'}->{'LogSheet_flights'}->{'FlightList'}->{'FlightInfo'});  # Totally wrong
  flight_information($root->{'LogSheet'}->{'LogSheet_glider-flights'}->{'GliderFlightList'}->{'GliderFlight'});  # New and hopefully OK
  print 	qq(<tr><td>Towplane Information</td>\n); 
  towplane_information($root->{'LogSheet'}->{'LogSheet_towplane-data'}->{'TowPlaneDataList'}); 
  print 	qq(<tr><td>Dropping template into the logsheet vault (database) ... </td>\n); 
  write_to_logsheet_verbose(param('logsheet_contents')); 
  print 	qq(<tr><td colspan="2" align="center">Checks look ok!</td></tr></table>\n);
  print 	qq(<p>Attempting to throw into the database now...\n<table border="1">\n); 
  print 	qq(<tr><td>Writing General Information...</td></tr>\n);
  write_meta_info();
  print		qq(<tr><td>Writing about flights...</td></tr>\n);
  write_flight_info();
  print 	qq(<tr><td>Writing about Towplane...</td></tr>\n);
  write_towplane_info($root->{'LogSheet'}->{'LogSheet_towplane-data'}->{'TowPlaneDataList'}->{'TowPlaneData'}); 
  print		qq(<tr><td>Emailing to the treasurer...</td></td>\n);
  send_via_email();
  if (param('date_override') ne 'duplicate') {
	# Execute the cute little program that mails the 
	# new pending reports list to the instructors. 
	# Only do this on the initial logsheet submission. 
    system ( '/home/httpd/bin/pending_emailer.pl', $logsheet{'operations_date'} ); 
    }

  print qq(<a href="?">Insert another logsheet</a>);
  }

	# This looks like the first run, so we will prompt you 
	# to upload or paste in your logsheet. 

else {
  print include('left-menu.scrap');
  print h2(qq(Upload Your Logsheet:));
  upload_block();
  print h2(qq(Alternatively...));
  print p(qq(You can cut and paste the contents of the template into this text-block:));
  insertion_form();
  print include('footer.scrap');
  }


#########################################
#     Subroutines!
#########################################

sub send_via_email {
  warn "Attempting to send via email\n" if $DEBUG;
  my ($random);
  for (1..24) {
    my ($new_digit)=int(rand(10));
    $random .= $new_digit; 
    }
  my ($date) = $logsheet{'operations_date'};
  my ($filename) = "$date.txt";
  my ($logsheet_contents) = param('logsheet_contents');
  $logsheet_contents =~ s/\r//g;
  my ($update, $update2);
  if (param('date_override') eq 'duplicate') {
    $update = ' ** This is an update to a previous logsheet! ** ';
    $update2 = "UPDATED Logsheet"; 
    }
  else {
    $update2 = "Original Logsheet";
    }

  open (SENDMAIL, "|-") 
	|| exec ("/usr/sbin/sendmail", "-t", "-oi"); 
  print SENDMAIL qq(From: "Skyline Webmaster" <webmaster\@skylinesoaring.org>
To: "Skyline Treasurer" <treasurer\@skylinesoaring.org>
Cc: "Logsheets" <archive-logsheet-skyline\@skylinesoaring.org>
Cc: "Piet Barber" <pbarber\@skylinesoaring.org>
Content-type: multipart/mixed; boundary=------------$random
User-Agent: Logsheet Submission Program version 1.0
Subject: $update2 for $date

This is a multi-part message in MIME format.

--------------$random
Content-Type: text/plain; charset=ISO-8859-1; format=flowed
Content-Transfer-Encoding: 7bit


$update
A logsheet for the operations on $date has just been uploaded by $ENV{'REMOTE_USER'}. 
A summary of the operations can be viewed at this URL: 
https://members.skylinesoaring.org/STATS/?date=$date
You will find the logsheet is attached to this message. 

--------------$random
Content-Type: text/plain;
 name="$filename"
Content-Transfer-Encoding: 7bit
Content-Disposition: inline;
 filename="$filename"

$logsheet_contents

--------------$random--


);
  close (SENDMAIL);
  warn "I think it was sent via email\n" if $DEBUG ; 
  }

sub destroy_old_info {
  	# Destroy the obsolete information -- we have multiple insertions on one day 
	# You told me to override.  Overriding means all that old stuff with the same
	# operations date needs to go away. 
	# so multiple delete commands, don't really care if they worked or not. 
	# We'll kep the logsheet_verbose stuff around in case there is an 'oops' 
  my ($input) = shift; 
  if (!$dbh) {
    db_connectify();
    }
  my ($sth);
  $sth=$dbh->do(qq(delete from logsheet_info where logsheet_date=?), undef, $logsheet{'operations_date'});
  $sth=$dbh->do(qq(delete from towplane_data where flight_date=?), undef, $logsheet{'operations_date'});
  $sth=$dbh->do(qq(delete from flight_info where flight_date=?), undef, $logsheet{'operations_date'});
  $sth=$dbh->do(qq(delete from ops_days where flight_date=?), undef, $logsheet{'operations_date'});
  }

sub write_meta_info {
  insertify(qq(insert into ops_days (
	flight_date, 
	dutyofficer, 
	instructor, 
	towpilot, 
	assistant) 
	values (?, ?, ?, ?, ?)), 
	$logsheet{'operations_date'},	
	$logsheet{'dutyofficer'},
	$logsheet{'instructor'},
	$logsheet{'towpilot'},
	$logsheet{'assistant'}
	);
  }

sub write_new_members {
	# We should see this input: 
	# $root->{'LogSheet'}->{'LogSheet_new-contacts'}->{'ContactList'}
  my ($input) = shift;
  if (ref($input->{'ContactInfo'}) eq "ARRAY") {
	# Multiple members here. 
	for my $value (@{$input->{'ContactInfo'}}) {
	  insert_member($value);
	  }
	}
  if (ref($input->{'ContactInfo'}) eq "HASH") { # Used to be SCALAR; hope this works.  pb 2008-05-23
	# Single new member here. 
        insert_member($input->{'ContactInfo'});
	}
  }

sub insert_member {
	# We should see this input: 
	# $root->{'LogSheet'}->{'LogSheet_new-contacts'}->{'ContactList'}->{'ContactInfo'} 
  my ($input) = shift; 
    warn ("input is $input")  if $DEBUG; 
    warn ( "Person name is ". $input->{'ContactInfo_name'}->{'PersonName'}->{'value'} . "\n" )  if $DEBUG; 
    warn ("Membership type is ". $input->{'ContactInfo_type'}->{'MemberType'}->{'value'}->{'value'} . "\n") if $DEBUG ; 
	# If we go to the find_name subroutine, and get the exact same answer that we got when we asked it 
	# Then that means we need to s
  if (find_name($input->{'ContactInfo_name'}->{'PersonName'}->{'value'}) eq $input->{'ContactInfo_name'}->{'PersonName'}->{'value'}) {
	warn ( "find_name(" . $input->{'ContactInfo_name'}->{'PersonName'}->{'value'}  . ") eq (" . $input->{'ContactInfo_name'}->{'PersonName'}->{'value'}  .  ") ? ") if $DEBUG; 
	# We don't put people into our membership database if they are special members. 
    if ($input->{'ContactInfo_type'}->{'MemberType'}->{'value'}->{'value'}  =~ /special/ ) {
      warn ("Special class membership doesn't get put into the database. \n") if $DEBUG; 
      return; 
      } 
    my ($handle); 
    my ($firstname, $lastname); 

    if ($input->{'ContactInfo_name'}->{'PersonName'}->{'value'}  =~ /^\s*(\S+)\s+(\S+)\s*$/) {
      $firstname = $1; 
      $lastname = $2; 
     }
    
    if ($input->{'ContactInfo_name'}->{'PersonName'}->{'value'}  =~ /^\s*(\S+)\s+(\S+)\s+(\S+)\s*$/) {
      $firstname = sprintf "%s %s", $1, $2; 
      $lastname = $3; 
     }

    if ($input->{'ContactInfo_name'}->{'PersonName'}->{'value'} =~/^\s*(\S).+\s+(\S+)\s*$/) {
      $handle = sprintf ("%s%s", $1,  $2); 
      } 
    $handle =~ tr/[A-Z]/[a-z]/; 
    $handle =~ s/[^a-z0-9]//; 	# Strip out annoying non-a-z0-9 chars for handles.
    my ($offset_number)=1; 
    if (handle_search($handle)) { 
      while (handle_search($handle . $offset_number) == 0) {
        $offset_number++; 
        }
      }


    if (!$handle) { 
	return; 
	}

#     Column     |          Type          |                             Modifiers                              
#----------------+------------------------+--------------------------------------------------------------------
# handle         | character varying(20)  | not null
# ssa_id         | integer                | 
# firstname      | character varying(30)  | not null
# lastname       | character varying(30)  | not null
# middleinitial  | character(2)           | default ''::bpchar
# namesuffix     | character varying(4)   | default ''::character varying
# official_title | character varying(70)  | 
# rostername     | character varying(20)  | 
# address1       | character varying(60)  | 
# address2       | character varying(60)  | 
# city           | character varying(30)  | 
# state          | character varying(8)   | 
# zip            | character varying(20)  | 
# country        | character(2)           | 
# email          | character varying(128) | 
# phone1         | character varying(16)  | 
# phone2         | character varying(16)  | 
# director       | boolean                | default false
# treasurer      | boolean                | default false
# secretary      | boolean                | default false
# webmaster      | boolean                | default false
# instructor     | boolean                | default false
# towpilot       | boolean                | default false
# dutyofficer    | boolean                | default false
# ado            | boolean                | default false
# otherduties    | boolean                | default false
# memberstatus   | character(1)           | default 'P'::bpchar
# rating         | character varying(4)   | default 'S'::character varying
# glider_owned   | character varying(30)  | 
# glider_owned2  | character varying(30)  | 
# joindate       | character varying(20)  | 
# lastupdated    | integer                | not null
# md5_password   | character varying(50)  | default '$apr1$rewi29wr$UGF1TTu.07Iae4edMlaQs/'::character varying
# newsletter     | boolean                | default true
# mailinglist    | boolean                | default true
# misc_list      | boolean                | default true
# weekday_list   | boolean                | default false
# bio_online     | boolean                | default false 
# mugshot        | boolean                | 
# public_notes   | text                   | 
# private_notes  | text                   | 
# cell_phone     | character varying(16)  | 


    my (@dude) = (	
	$handle,	# handle
	'0', 		# ssa_id
	$firstname, 
	$lastname, 
	'', 		# Middle Initial
	'', 		# name suffix
	'', 		# Official Title
	'', 		# rostername
	$input->{'ContactInfo_address'}->{'value'},
	'', 		# address 2 
	$input->{'ContactInfo_city'}->{'value'},
	$input->{'ContactInfo_state'}->{'value'},
	$input->{'ContactInfo_zip-code'}->{'value'},
	'', 		# country
	$input->{'ContactInfo_e-mail'}->{'value'},
	$input->{'ContactInfo_home-phone'}->{'value'}, # Phone 1
	$input->{'ContactInfo_work-phone'}->{'value'}, # phone 2 
        'false', 'false', 'false', 'false', 'false', 'false', 'false', 'false', 'false', 	# Director through otherduties
	'E', 		# Temporary Member (Introductory Member)
	'S', 		# rating
	'', 		# glider #1
	'', 		# glider #2
	$logsheet{'operations_date'},	 # Join Date
	time, 		# last updated
	'$apr1$rewi29wr$UGF1TTu.07Iae4edMlaQs/', 	# md5_password (default)
	'false', 		# newsletter
	'false', 		# mailing list (obsolete)
	'false', 		# misc list (obsolete) 
	'false', 		# weekday list (obsolete) 
	'false', 		# BIO_ONLINE
	'false', 		# mugshot online
	'', 			# public notes
	'', 			# private notes
	$input->{'ContactInfo_cell-phone'}->{'value'}	# Cell Phone
	);
	
    insertify (qq(
	insert into members (
handle, ssa_id, firstname, lastname, middleinitial, namesuffix,  official_title, rostername, 
address1, address2, city, state, zip, country, email, phone1, phone2, director, treasurer, secretary, 
webmaster, instructor, towpilot, dutyofficer, ado, otherduties, memberstatus, rating, glider_owned, 
glider_owned2, joindate, lastupdated, md5_password, newsletter, mailinglist, misc_list, 
weekday_list, bio_online, mugshot, public_notes, private_notes, cell_phone) 
		values (?, ?, ?, ?, ?, ?, ?, ?, 
			?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 
			?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 
			?, ?, ?, ?, ?, ?, ?, ?,  
			?, ?, ? )), @dude); 
    insertify (qq(insert into new_contacts (handle, join_date) values (?, ?)), $handle, $logsheet{'operations_date'});
    insertify (qq(insert into aliases (handle, name) values (?, ?)), $handle, $input->{'ContactInfo_name'}->{'PersonName'}->{'value'});
	
    open (SENDMAIL, "|-") 
	|| exec ("/usr/sbin/sendmail", "-toi"); 
    print SENDMAIL qq(From: "Skyline Webmaster" <webmaster\@skylinesoaring.org>
To: "Steve Rockwood" <srockwood\@skylinesoaring.org>
CC: "Piet Barber" <pbarber\@skylinesoaring.org>
Subject: New Member uploaded

Hello, this is the web program that is used to upload logsheets. 
According to this logsheet uploaded by $ENV{'REMOTE_USER'}, there is 
a new member who was a part of the data for this logsheet.  The person's
information is as follows: 

Name:             $dude[2] $dude[3]
Address:          $dude[8] 
                  $dude[9]
City, State, Zip: $dude[10], $dude[11] $dude[12]
Email Address:    $dude[14]
Phone1:           $dude[15]
Phone2:           $dude[16]

He is inserted as an introductory member, which may or may not be accurate. 
You will need to log in and correct any extra information about this 
member, and reset his password. . 

);
    close (SENDMAIL);
    }
 	# Any place where this user is referenced should have his handle
	# now instead of his name.  So we're going to run find member on this dude. 
  find_name($input); 
  }


sub write_flight_info {
	# Write out all the flights you collected earlier. 
  for my $flight (@flight_sql) {

    insertify (qq(insert into flight_info 
		(flight_date, pilot, passenger, glider, instructor,
		 towpilot, flight_type, takeoff_time, landing_time, 
		 flight_time, release_altitude, flight_cost, tow_cost,
		 total_cost) values (?,?,?,?,?,?,?,?,?,?,?,?,?,?)),
	@{$flight}
	);
    }
  }

sub write_towplane_info {
	# Write out all the flights you collected earlier. 
	# This program is not yet capable of handling multiple 
	# tow planes in one day.  When that day comes, bad things are going 
	# to happen to this subroutine. 
  my ($input) = shift;
	# Input is normally: 
	# $root->{'LogSheet'}->{'LogSheet_towplane-data'}->{'TowPlaneList'}->{'TowPlaneData'}); 
  warn "Doing Towplane Insertions here\n" if $DEBUG; 
  if (ref($input) eq "ARRAY") {
    for my $towplane_link (@{$input}) { 
	warn "New variable towplane link is: ". $towplane_link . "\n" if $DEBUG;  
        warn "I think the towplane's name is: " . $towplane_link->{'towplane'}->{'value'} . "\n" if $DEBUG; 
      insertify(qq(insert into towplane_data 
        (flight_date, towplane, start_tach, stop_tach, tach_time, gas_added,
        towpilot_comments, tows) values (?, ?, ?, ?, ?, ?, ?, ?)),
        $logsheet{'operations_date'},
        $towplane_link->{'TowPlaneData_towplane'}->{'TowPlaneName'}->{'value'},
        $towplane_link->{'TowPlaneData_start-tach'}->{'value'},
        $towplane_link->{'TowPlaneData_end-tach'}->{'value'},
        $towplane_link->{'TowPlaneData_tach-time'}->{'value'},
        $towplane_link->{'TowPlaneData_gas-added'}->{'value'},
        ($towplane_link->{'TowPlaneData_comment'}->{'value'} || "No Comment"),
        $tow_count{$towplane_link->{'TowPlaneData_towplane'}->{'TowPlaneName'}->{'value'}})
      }
    }

  #elsif (ref($input) eq 'SCALAR') {
  else {
    warn "OK so we have us a single towplane here. and we should insert as appropriate. \n" if $DEBUG; 
    insertify(qq(insert into towplane_data 
      (flight_date, towplane, start_tach, stop_tach, tach_time, gas_added,
      towpilot_comments, tows) values (?, ?, ?, ?, ?, ?, ?, ?)),
      $logsheet{'operations_date'},
      #$root->{'Logsheet'}->{'LogSheet_towplane'}->{'TowPlaneName'}->{'value'},
      $input->{'TowPlaneData_towplane'}->{'TowPlaneName'}->{'value'},
      $input->{'TowPlaneData_start-tach'}->{'value'},
      $input->{'TowPlaneData_end-tach'}->{'value'},
      $input->{'TowPlaneData_tach-time'}->{'value'},
      $input->{'TowPlaneData_gas-added'}->{'value'},
      ($input->{'TowPlaneData_comment'}->{'value'} || "No Comment"),
      scalar(@flight_sql));
    }
  warn "Done doing Towplane Insertions here\n" if $DEBUG; 
  }

sub handle_search {
  	# do a select for this handle, 
	# return 1 if it exists, 
	# return 0 if it doesn't. 
  my ($input) = shift;
  my ($answer);
  warn("Doing this here SQL: select handle for members where handle ='$input'");
  my($get_info) = $dbh->prepare("select handle for members where handle ='$input'");
  $get_info->execute();
  while (my $ans = $get_info->fetchrow_hashref()) {
    $answer = $ans->{'handle'};
    }
  if ($answer > 0) {
    return 1;
    }
  else {
    return 0;
    }
  0;
  }

sub insertify {
	# Expect two inputs: 
	# First is the general SQL 
	# second is the array of the junk you want inserted. 
  my ($sql_markup) = shift; 
  my (@inserted_data) = @_;
  my ($sth);
  $sth=$dbh->prepare($sql_markup);
  warn "Attempting to write this SQL: \n$sql_markup \n" if $DEBUG; 
  warn "Attempting to use these values: " . join (":", @inserted_data) . "\n" if $DEBUG; 
  $sth->execute(@inserted_data); 
  }

sub write_to_logsheet_verbose {
	# This is like an audit trail. 
	# that way, if somebody submits a logsheet, we always will ahve a copy of the submitted item. 
	# hope we got enough disk space... 
  my ($input) = shift; 
  my ($sth);
  $sth=$dbh->prepare(qq(insert into logsheet_verbose (handle, submit_time, logsheet_date, logsheet_contents) values (?, ?, ?, ?)));
  $sth->execute($ENV{'REMOTE_USER'}, scalar(localtime(time)), $logsheet{'operations_date'}, param('logsheet_contents'));
  print qq(<td bgcolor="#88FF88">OK</td></tr>\n);
  }

sub check_for_previous {
  	# Just snoop around the database, 
	# check to see if there are any older submissions on this date
	# if, so, override page is presented. 
  my ($input) = shift;
  return if $input eq '';
  my ($answer);
  if (!$dbh) {
    db_connectify();
    }
  my($get_info) = $dbh->prepare("select count(*) as quantity from flight_info where flight_date ='$input'");
  $get_info->execute();
  while (my $ans = $get_info->fetchrow_hashref()) {
    $answer += $ans->{'quantity'};
    }
  my($get_info) = $dbh->prepare("select count(*) as quantity from ops_days where flight_date ='$input'");
  $get_info->execute();
  while (my $ans = $get_info->fetchrow_hashref()) {
    $answer += $ans->{'quantity'};
    }
  my($get_info) = $dbh->prepare("select count(*) as quantity from towplane_data where flight_date ='$input'");
  $get_info->execute();
  while (my $ans = $get_info->fetchrow_hashref()) {
    $answer += $ans->{'quantity'};
    }
  undef($get_info);
  if ($answer > 0) {
    param('date_override', 'duplicate');
    warn_out(qq(Looks like a logsheet for $logsheet{'operations_date'} is already submitted. Overwrite?<br>\n));
    }
  else {
    print qq(<td bgcolor="#88FF88">OK</td></tr>\n);
    }
  }

sub upload_block {
	# The cool upload block that lets somebody upload the logsheet. 
  print start_multipart_form();
  my ($default_filename) = `date +%m%d%y`; 
  chomp $default_filename;
  $default_filename .= ".txt"; 
  printf (qq(
<table border="1" bgcolor="#F8F8F*">
<tr><td>Choose File to Upload:</td><td>%s</td>
</tr><td colspan="2" align="center">%s</td></tr></table>
	),
	filefield (
		-name => 'logsheet_upload',
		-default => $default_filename,
		-size => 20,
		),
	submit (
		-value => "Submit for processing"
		)
	);
  print end_form();
  }

sub insertion_form {
	# this is the big text area. 
  print start_form();
  printf (qq(
<table border="1" bgcolor="#F8F8F8">
<tr><td>Paste Logsheet Here: </td><td>%s</td>
<tr><td colspan="2">%s</td></tr></table>
	),
	textarea (
		-name => 'logsheet_contents',
		-cols => 100,
		-rows => 35
		),
	submit (
		-value => "Submit for processing"
		)
 	); 
  print end_form();
  }

sub resubmit_gunk {
	# Give dude the opportunity to try again. 
	# Throws all the stuff into hidden variables. 
	# Shows the first ten lines of the logsheet before proceding
	# Includes the secret override key
  print start_form();
  my ($first_ten, $count);
  for my $line (split /\n/, param('logsheet_contents')) {
    last if $count++ > 10;
    $first_ten .= $line
    }
  printf (qq(
<table border="1" bgcolor="#F8F8F8">
<tr><td colspan="2"><pre>%s\n...</pre>\n%s\n%s\n%s\n%s</td></tr>
<tr><td colspan="2">%s</td></tr>
	),
	$first_ten,
	hidden('override'),
	hidden('override_do'),
	hidden('date_override'),
	hidden('override_towplane'),
	hidden('logsheet_contents'),
	submit (
		-value => "Override Warning"
		)
 	); 
  print end_form();
  }

sub write_to_logsheet_verbose {
  my ($input) = shift; 
  my ($sth);
  $sth=$dbh->prepare(qq(insert into logsheet_verbose (handle, submit_time, logsheet_date, logsheet_contents) values (?, ?, ?, ?)));
  $sth->execute($ENV{'REMOTE_USER'}, scalar(localtime(time)), $logsheet{'operations_date'}, param('logsheet_contents'));
  print qq(<td bgcolor="#88FF88">OK</td></tr>\n);
  }


sub new_contacts {
  my ($input) = shift;
  if (ref($input) eq "ARRAY") {
	printf (qq(Multiple of new contacts extracted: %d<br>\n),
		scalar(@{$input}));
	}
  if (ref($input) eq "HASH") { # Used to be SCALAR; hope this works pb 2008-05-23
	print (qq(One new contact extracted<br>\n)),
	}
  
  print qq(<td bgcolor="#88FF88">OK</td></tr>\n);
  }

sub flight_information {
	# Look through the flight information, could be one or many
	# or could be none.  If none, generate warning condition. 
  my ($input) = shift;
  if (ref($input) eq "ARRAY") {
	warn "Found multiple flights\n" if $DEBUG; 
	printf (qq(Number of flights extracted: %d<br>\n),
		scalar(@{$input}));
	for my $flight (@{$input}) {
	  push (@flight_sql, process_flight($flight));
	  }
	}

  elsif (ref($input) eq "SCALAR") {
	warn "Found one flight\n" if $DEBUG; 
	print (qq(Number of flights extracted: One measley flight, eh?<br>\n));
	push (@flight_sql, (process_flight($input)));
	}
	
  elsif (ref($input) eq "HASH") {
	warn "Found one flight\n" if $DEBUG; 
	print (qq(Number of flights extracted: One measley flight, eh?<br>\n));
	push (@flight_sql, (process_flight($input)));
	}

  if (! $input && param('override') ne 'no_flights') {
        param('override', 'no_flights');
	warn_out(qq(No Flights on this logsheet.  I hope that's OK with you.<br>\n));
	}
  print qq(<td bgcolor="#88FF88">OK</td></tr>\n);
  }

sub process_flight {
  my ($input) = shift;
	# Sometimes some of the fields are ommitted, and I can't think of a situation that this would
	# be considered to be acceptable.   I will do some flight by flight checks 
	# and barf out with an error if these fail.  The DO should ought to correct them 
	# and then upload the new logsheet. No warnings here.  You better fix that sh*t.  

	# You're towing behind a club tow plane, and the tow pilots name is missing? REJECTION! 

  if ($input->{'GliderFlight_towpilot'}->{'PersonName'}->{'value'} eq '' && 
      ( $input->{'GliderFlight_towplane'}->{'TowPlaneName'}->{'value'} eq '' || 
        $input->{'GliderFlight_towplane'}->{'TowPlaneName'}->{'value'} eq 'SSC Pawnee' || 
        $input->{'GliderFlight_towplane'}->{'TowPlaneName'}->{'value'} eq 'SSC Pawnee'
	))    { 
      error_out(qq(One of the flights has no tow pilot listed for ) . 
	$input->{'GliderFlight_name'}->{'PersonName'}->{'value'} . 
	qq('s flight.  There is no way I can process this logsheet.  Please correct it within the logsheet program and upload the revised logsheet. If you need the latest version of the Logsheet program, please fetch it from the link to the left named "LOGSHEETS" )); 
    } 

	# Take off or landing times have -1s in them?  REJECTION! 
  for my $flight_regime ('takeoff', 'landing') { 
    if ($input->{$flight_regime}->{'ClockTime'}->{'ClockTime_hour'}->{'value'} > 23)   { 
      error_out(qq(One of the flights has a truly bogus value [) . 
        $input->{'GliderFlight_' . $flight_regime}->{'ClockTime'}->{'ClockTime_hour'}->{'value'} .  
	qq(] for the hour field of ) . 
	$input->{'GliderFlight_name'}->{'PersonName'}->{'value'} . 
	qq('s flight's <b><i>$flight_regime</i></b>.  There is no way I can process this logsheet.  Please correct it within the logsheet program and upload the revised logsheet. If you need the latest version of the Logsheet program, please fetch it from the link to the left named "LOGSHEETS" )); 
      } 
    for my $h_m ( 'hour', 'minute') { 
      if ($input->{'GliderFlight_' . $flight_regime}->{'ClockTime'}->{'ClockTime_' . $h_m}->{'value'} == -1) { 
        error_out(qq(One of ) .  
 	 	$input->{'GliderFlight_name'}->{'PersonName'}->{'value'} . 
		qq('s flights has an empty $h_m value. Please correct it in the logsheet program, and upload a corrected logsheet. If you don't know the exact time, please enter your best guess.  If you are doing this from home, and you need the latest Logsheet program, please download it in the "LOGSHEETS" link to your left.  )) ; 
        }
      } 
    }
  
	# This is ultra-annoying. 
	# sometimes the logsheet program inputs a '-1' in the field to show
	# that it is undefined. 
	# instead of inserting monies that end up looking like 
	# $-1.-01, I have to catch these manually 
	# and replace them with "0"
	# Unfortunately, I have to do this for all of the three cost types. 
  my $flight_dollars=$input->{'GliderFlight_flight-cost'}->{'DollarAmount'}->{'DollarAmount_dollars'}->{'value'};
  my $flight_cents=$input->{'GliderFlight_flight-cost'}->{'DollarAmount'}->{'DollarAmount_cents'}->{'value'};
    if ($flight_dollars == -1 || $flight_cents == -1) {
      $flight_dollars=0;
      $flight_cents=0;
      }
  my $tow_dollars=$input->{'GliderFlight_tow-cost'}->{'DollarAmount'}->{'DollarAmount_dollars'}->{'value'};
  my $tow_cents=$input->{'GliderFlight_tow-cost'}->{'DollarAmount'}->{'DollarAmount_cents'}->{'value'};
    if ($tow_dollars == -1 || $tow_cents == -1) {
      $tow_dollars=0;
      $tow_cents=0;
      }
  my $total_dollars=$input->{'GliderFlight_total-cost'}->{'DollarAmount'}->{'DollarAmount_dollars'}->{'value'};
  my $total_cents=$input->{'GliderFlight_total-cost'}->{'DollarAmount'}->{'DollarAmount_cents'}->{'value'};
    if ($total_dollars == -1 || $total_cents == -1) {
      $total_dollars=0;
      $total_cents=0;
      }
	
  my $tow_height =$input->{'GliderFlight_release-altitude'}->{'ReleaseHeight'}->{'value'};
  if ($tow_height == -1) {
    $tow_height = "3000";
    }

	# If the takeofftime and landing time are the same 
	# and the flighttime is -1 or 0
	# Then fudge it, 
	# and force the flight to be one minute long. 
	# I'll just get Kans to prevent the logsheet program from doing this
  #if (
	#( $input->{'GliderFlight_takeoff'}->{'ClockTime'}->{'Clocktime_hour'}->{'value'}  . 
	  #$input->{'GliderFlight_takeoff'}->{'ClockTime'}->{'Clocktime_minute'}->{'value'} eq 
	  #$input->{'GliderFlight_landing'}->{'ClockTime'}->{'Clocktime_hour'}->{'value'} 
	  #$input->{'GliderFlight_landing'}->{'ClockTime'}->{'Clocktime_minute'}->{'value'} ) 
	#&& 
       	#$input->{'GliderFlight_flight-time'}->{'FlightTime'}->{'FlightTime_hours'}->{'value'} <= 0
	#&& 
       	#$input->{'GliderFlight_flight-time'}->{'FlightTime'}->{'FlightTime_minutes'}->{'value'} <= 0
	#) {

     #$input->{'GliderFlight_flight-time'}->{'FlightTime'}->{'FlightTime_hours'}->{'value'} = 0;
     #$input->{'GliderFlight_flight-time'}->{'FlightTime'}->{'FlightTime_minutes'}->{'value'} = 1;
     #}
	

	# We should keep count of the flights each towplane does. 
	# 
  my $towplane = $input->{'GliderFlight_towplane'}->{'TowPlaneName'}->{'value'}; 
	# In case that fancy new value for each field doesn't exist 
	# we just plop in the towplane name at the top of the logsheet
	# (for backward compatibility purposes) 
	# Othwerwise, use the new-fangled thing above. 

  $towplane ||= $root->{'Logsheet'}->{'LogSheet_towplane'}->{'TowPlaneName'}->{'value'};

  $tow_count{$towplane}++; 



	# One big long answer:
  my (@answer) = ( 
	$logsheet{'operations_date'},	#1
	find_name($input->{'GliderFlight_name'}->{'PersonName'}->{'value'}), #2
	find_name($input->{'GliderFlight_passenger'}->{'PersonName'}->{'value'}), #3
        $input->{'GliderFlight_glider'}->{'GliderName'}->{'value'}, #4
	find_name($input->{'GliderFlight_instructor'}->{'PersonName'}->{'value'}), #5
	find_name($input->{'GliderFlight_towpilot'}->{'PersonName'}->{'value'}), #6
	$input->{'GliderFlight_category'}->{'value'}->{'value'}, #7
	sprintf("%2.2d:%2.2d", #8
        	$input->{'GliderFlight_takeoff'}->{'ClockTime'}->{'ClockTime_hour'}->{'value'},
        	$input->{'GliderFlight_takeoff'}->{'ClockTime'}->{'ClockTime_minute'}->{'value'},
        	),
	sprintf("%2.2d:%2.2d", #9
        	$input->{'GliderFlight_landing'}->{'ClockTime'}->{'ClockTime_hour'}->{'value'},
        	$input->{'GliderFlight_landing'}->{'ClockTime'}->{'ClockTime_minute'}->{'value'},
        	),
	sprintf("%2.2d:%2.2d", #10
       		$input->{'GliderFlight_flight-time'}->{'FlightTime'}->{'FlightTime_hours'}->{'value'},
        	$input->{'GliderFlight_flight-time'}->{'FlightTime'}->{'FlightTime_minutes'}->{'value'},
        	),
	$tow_height,
	sprintf("\$%d.%2.2d", #12
		$flight_dollars,
		$flight_cents
		),
	sprintf("\$%d.%2.2d", #13
		$tow_dollars,
		$tow_cents
		),
	sprintf("\$%d.%2.2d", #14
		$total_dollars,
		$total_cents
        	)
        );
  \@answer;
  }

sub towplane_information {
	# Check for towplane information for OK-ness. 
  my ($input) = shift; 
  if (! $input && param('override_towplane') ne 'towplane') {
    return soft_warn(qq(The Towplane data is missing!)); 
    #param("override_towplane", "towplane");
    }
  if (ref($input) eq "ARRAY") {
	printf (qq(Multiple Towplanes for Today<br>\n),
		scalar(@{$input}));
	}
  print qq(<td bgcolor="#88FF88">OK</td></tr>\n);
  }

sub error_out {
	# Definitely an error that is not acceptable. 
  my ($input) = shift; 
  printf (qq(<td bgcolor="#FF8888"><b>ERROR</b><br>%s</td></tr></table>), $input);
  print h1("Failure in Submission.  Try again?");
  resubmit_gunk();
  insertion_form();
  print include("footer.scrap"); 
  exit;
  }

sub soft_warn {
  my ($input) = shift;
  sprintf (qq(<td bgcolor="#FFFF88"><b>WARN</b><br>%s</td></tr></table>), $input);
  }

sub warn_out {
	# Not a terrible failure, but something we want confirmation is OK. 
  my ($input) = shift; 
  printf (qq(<td bgcolor="#FFFF88"><b>WARN</b><br>%s</td></tr></table>), $input);
  print h1("Warning in Submission.  Continue?");
  resubmit_gunk();
  print include("footer.scrap"); 
  exit;
  }

sub check_one {
  if (param('logsheet_contents') !~ /^LogSheet ::= {/)  {
    error_out(qq(Missing 'LogSheet ::=' header. This is a fatal error. I really don't like what you sent me. )); 
    }

  print qq(<td bgcolor="#88FF88">OK</td></tr>\n);
  }

sub check_two {
	# Take the logsheet, as submitted, write it to a temp file in a specified directory
	# Take that logsheet, and use Jonathan's program to convert it into XML. 
	# Then look to make sure that that file is in fact, parsable XML. 
  my ($tempdir) = "/home/httpd/logsheets/"; 
  my ($tempfile) = $tempdir . "logsheet-" . time . "-" . $$ . ".txt"; 
  my ($xmlfile) = $tempdir . "logsheet-" . time . "-" . $$ . ".xml"; 
  open (OUTPUT, ">$tempfile") || error_out("Unable to write to my tempfile, <tt>'$tempfile'</tt>.  Tell the webmaster, and try again when he's fixed the problem.  Tell the webmaster that I am  the program 'logsheet_upload.cgi' (he should be able to figure that out)"); 
  print OUTPUT param('logsheet_contents'); 
  close (OUTPUT);
  	# Execute asn2xml program here. 
  my ($asn_convert_program) = '/home/httpd/bin/sscasn2xml'; 
  open (ASN2XML, "-|") || exec ($asn_convert_program, "-i", $tempfile, "-o", $xmlfile); 
  #open (ASN2XML, "-|") || exec ($asn_convert_program, "-r", $tempdir, "-p", $tempdir); 
  my $asn_output=join ("\n", <ASN2XML>); 
  close (ASN2XML); 
  if (! -e $xmlfile) {
    error_out(qq(Your logsheet didn't convert into XML for some reason.  
This should have worked.  If you didn't do something dumb like edit the XML manually
(and made a mistake), tell your webmaster right away, 
and include the logsheet you're trying to upload, so he can debug it.\n)); 
    } 
  use XML::Bare;
  my $xml = new XML::Bare( file => $xmlfile );
  $root = $xml->parse();
  if (ref($root) ne 'HASH') {
    error_out(qq(Your Logsheet didn't parse into XML like I was expecting it to. Please tell the webmasters, 
    and let them figure this mess out.  Tell him I'm running as ) . $ARGV[0] . "\n");
    }
  print qq(<td bgcolor="#88FF88">OK</td></tr>\n);
  }

sub print_out_staff {
  my ($input)=shift;
  $logsheet{'dutyofficer'} =	find_name($input->{StaffData_dutyofficer}->{PersonName}->{value});
  $logsheet{'assistant'}   =	find_name($input->{StaffData_assistant}->{PersonName}->{value});
  $logsheet{'instructor'}  =	find_name($input->{StaffData_instructor}->{PersonName}->{value});
  $logsheet{'towpilot'}    =	find_name($input->{StaffData_towpilot}->{PersonName}->{value});
  if ($logsheet{'dutyofficer'}) {
    print qq(<td bgcolor="#88FF88">OK</td></tr>\n);
    }
  elsif (param("override_do") ne "Duty Officer") {
    param('override_do', "Duty Officer");
    warn_out(qq(Unable to find a Duty Officer listed for today.  Was there one? ));
    }
  }

sub check_three {
	# Check contents for submitted data
  my ($input) = shift; 
  	# Input should be the HASH from $root
  my (%month) = qw(
        january 1
        february 2
        march 3
        april 4
        may 5
        june 6
        july 7
        august 8
        september 9
        october 10
        november 11
        december 12
        );
  $logsheet{'operations_date'} =  sprintf ("%4.4d-%2.2d-%2.2d",
        $input->{LogSheet}->{LogSheet_date}->{CalendarDate}->{CalendarDate_year}->{value},
        $month{$input->{LogSheet}->{LogSheet_date}->{CalendarDate}->{CalendarDate_month}->{value}->{value}},
        $input->{LogSheet}->{LogSheet_date}->{CalendarDate}->{CalendarDate_day}->{value}
	);
  $logsheet{'towplane'} =       $input->{LogSheet}->{LogSheet_towplane}->
                                {TowPlaneName}->{value};

  if ($logsheet{'operations_date'} !~ /\d{4}-\d{2}-\d{2}/) {
    error_out(qq(Your Operations Date couldn't be parsed from the logsheet.  Something terrible has happened.  Did you upload me a corrupted Logsheet?  Did the Logsheet not contain a date?  Could you check into it and resubmit?));
    }

  print qq(<td bgcolor="#88FF88">OK</td></tr>\n);
  }

sub include {
        # Pull file from the INCLUDES directory
        # output of subroutine is that file.
  my $file = shift;
  my $answer;
  my ($dir, $fulldir);
  use Cwd;
  $fulldir=getcwd;
  $dir = 'skyline' if ($fulldir =~ m#/var/www/skyline#);
  warn ("The pwd is $fulldir\n") if $DEBUG;
  $dir ||= 'members';
  open (INCLUDE, "/var/www/$dir/html/INCLUDES/$file") || print "Can't open that file $!";
  while (my $line = <INCLUDE>) {
    $answer .= $line;
    }
  close (INCLUDE);
  $answer;
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



sub db_connectify {
        # Just connect to the database.
  my $driver = "DBI:Pg";
  my $database = 'skyline';
  $dbh = DBI->connect("$driver:dbname=$database")
        || error_out ("Can't connect to $driver database $database $!\n");
  }



