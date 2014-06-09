#!/usr/bin/perl 
	# A simple program to upload logsheets
	#  .... turns into not so simple a program to verify all the gunk
	#  before comitting it to the database. 

use strict;
use DBI;
use CGI qw/:standard/; 
my ($root, %logsheet, $dbh, @flight_sql, @contacts_sql, @towpilots_sql);

print header();
start_html( 'Logsheet Upload');

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
  print_out_staff($root->{'LogSheet'}->{'LogSheet_staff'}->{'StaffInfo'});
  print 	qq(<tr><td>New Contacts</td>\n); 
  new_contacts($root->{'LogSheet'}->{'LogSheet_new-contacts'}->{'ContactList'});  
  print 	qq(<tr><td>Flight Information</td>\n);
  flight_information($root->{'LogSheet'}->{'LogSheet_flights'}->{'FlightList'}->{'FlightInfo'}); 
  print 	qq(<tr><td>Towplane Information</td>\n); 
  towplane_information($root->{'LogSheet'}->{'LogSheet_towplane-data'}->{'TowPlaneList'}); 
  print 	qq(<tr><td>Dropping template into the logsheet vault (database) ... </td>\n); 
  write_to_logsheet_verbose(param('logsheet_contents')); 
  print 	qq(<tr><td colspan="2" align="center">Checks look ok!</td></tr></table>\n);
  print 	qq(<p>Attempting to throw into the database now...\n<table border="1">\n);
  print 	qq(<tr><td>Writing General Information...</td></tr>\n);
  write_meta_info();
  print		qq(<tr><td>Writing about new members, if applicable.</td></tr>\n);
  write_new_members($root->{'LogSheet'}->{'LogSheet_new-contacts'}->{'ContactList'});
  print		qq(<tr><td>Writing about flights...</td></tr>\n);
  write_flight_info();
  print 	qq(<tr><td>Writing about Towplane...</td></tr>\n);
  write_towplane_info($root->{'LogSheet'}->{'LogSheet_towplane-data'}->{'TowPlaneList'}->{'TowPlaneData'}); 
  print		qq(<tr><td>Emailing to the treasurer...</td></td>\n);
  send_via_email();
  print qq(<a href="?">Insert another logsheet</a>);
  }

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
  warn "Attempting to send via email\n"; 
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
  warn "I think it was sent via email\n"; 
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
  my ($input) = shift;
  if (ref($input) eq "ARRAY") {
	# Multiple members here. 
	for my $value (@{$input}) {
	  insert_member($value);
	  }
	}
  if (ref($input) eq "HASH") { # Used to be SCALAR; hope this works.  pb 2008-05-23
	# Single new member here. 
        insert_member($input);
	}
  }

sub insert_member {
  my ($input) = shift; 
  if (find_name($input->{'ContactInfo_name'}->{'PersonName'}) ne $input->{'ContactInfo_name'}->{'PersonName'}) {
    my ($firstname, $lastname) = ($1, $2) if ($input =~ /^(\w+)\s+(\w+)$/);
    my ($handle_stub) = ($1, $2) if ($input=~/^(\w)\s+\s+(\w+)$/); 
    my ($handle_count);
    while (! handle_search($handle_stub)) {
      $handle_stub .= $handle_count++; 
      }
    my (@dude) = (	$handle_stub,
	$firstname, 
	$lastname, 
	$input->{'ContactInfo_address'},
	$input->{'ContactInfo_city'},
	$input->{'ContactInfo_state'},
	$input->{'ContactInfo_zip-code'},
	$input->{'ContactInfo_home-phone'},
	$input->{'ContactInfo_work-phone'},
	$input->{'ContactInfo_cell-phone'},
	$input->{'ContactInfo_e-mail'},
	$logsheet{'operations_date'},
	'T');
	
    insertify (qq(insert into members (handle, firstname, lastname, address1, address2, city, state, zip, phone1, phone2, cell_phone, email, join_date, memberstatus ) values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)), @dude); 
    insertify (qq(insert into new_contacts (handle, join_date) values (?, ?)), $handle_stub, $logsheet{'operations_date'});
    insertify (qq(insert into aliases (handle, name) values (?, ?)), $handle_stub, $input->{'ContactInfo_name'}->{'PersonName'});
	
    open (SENDMAIL, "|-") 
	|| exec ("/usr/sbin/sendmail", "-toi"); 
    print SENDMAIL qq(From: "Skyline Webmaster" <webmaster\@skylinesoaring.org>
To: "Membership Meister" <pbarber\@skylinesoaring.org>
Subject: New Member uploaded

Hello, this is the web program that is used to upload logsheets. 
According to this logsheet uploaded by $ENV{'REMOTE_USER'}, there is 
a new member who was a part of the data for this logsheet.  The person's
information is as follows: 

Name:             $dude[1] $dude[2]
Address:          $dude[3]
City, State, Zip: $dude[4], $dude[5], $dude[6]
Phone1:           $dude[7]
Phone2:           $dude[8]
Cell Phone:       $dude[9]
Email Address:    $dude[10]

);
    close (SENDMAIL);
    }
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
  insertify(qq(insert into towplane_data 
    (flight_date, towplane, start_tach, stop_tach, tach_time, gas_added,
    towpilot_comments, tows) values (?, ?, ?, ?, ?, ?, ?, ?)),
    $logsheet{'operations_date'},
    $root->{'Logsheet'}->{'LogSheet_towplane'}->{'TowPlaneName'},
    $input->{'TowPlaneData_start-tach'}->{'value'},
    $input->{'TowPlaneData_end-tach'}->{'value'},
    $input->{'TowPlaneData_tach-time'}->{'value'},
    $input->{'TowPlaneData_gas-added'}->{'value'},
    ($input->{'TowPlaneData_comment'}->{'value'} || "No Comment"),
    scalar(@flight_sql));
  }

sub handle_search {
  	# do a select for this handle, 
	# return 1 if it exists, 
	# return 0 if it doesn't. 
  my ($input) = shift;
  my ($answer);
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
  #warn "Attempting to write this SQL: \n$sql_markup \n"; 
  #warn "Attempting to use these values: " . join (":", @inserted_data) . "\n"; 
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
	warn "Found multiple flights\n"; 
	printf (qq(Number of flights extracted: %d<br>\n),
		scalar(@{$input}));
	for my $flight (@{$input}) {
	  push (@flight_sql, process_flight($flight));
	  }
	}

  elsif (ref($input) eq "SCALAR") {
	warn "Found one flight\n"; 
	print (qq(Number of flights extracted: One measley flight, eh?<br>\n));
	push (@flight_sql, (process_flight($input)));
	}
	
  elsif (ref($input) eq "HASH") {
	warn "Found one flight\n"; 
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

	# This is ultra-annoying. 
	# sometims the logsheet program inputs a '-1' in the field to show
	# that it is undefined. 
	# instead of inserting monies that end up looking like 
	# $-1.-01, I have to catch these manually 
	# and replace them with "0"
	# Unfortunately, I have to do this for all of the three cost types. 
  my $flight_dollars=$input->{'FlightInfo_flight-cost'}->{'DollarAmount'}->{'DollarAmount_dollars'}->{'value'};
  my $flight_cents=$input->{'FlightInfo_flight-cost'}->{'DollarAmount'}->{'DollarAmount_cents'}->{'value'};
    if ($flight_dollars == -1 || $flight_cents == -1) {
      $flight_dollars=0;
      $flight_cents=0;
      }
  my $tow_dollars=$input->{'FlightInfo_tow-cost'}->{'DollarAmount'}->{'DollarAmount_dollars'}->{'value'};
  my $tow_cents=$input->{'FlightInfo_tow-cost'}->{'DollarAmount'}->{'DollarAmount_cents'}->{'value'};
    if ($tow_dollars == -1 || $tow_cents == -1) {
      $tow_dollars=0;
      $tow_cents=0;
      }
  my $total_dollars=$input->{'FlightInfo_total-cost'}->{'DollarAmount'}->{'DollarAmount_dollars'}->{'value'};
  my $total_cents=$input->{'FlightInfo_total-cost'}->{'DollarAmount'}->{'DollarAmount_cents'}->{'value'};
    if ($total_dollars == -1 || $total_cents == -1) {
      $total_dollars=0;
      $total_cents=0;
      }
	
  my $tow_height =$input->{'FlightInfo_release-altitude'}->{'TowHeight'}->{'value'};
  if ($tow_height == -1) {
    $tow_height = "3000";
    }
	# One big long answer:
  my (@answer) = ( 
	$logsheet{'operations_date'},	#1
	find_name($input->{'FlightInfo_name'}->{'PersonName'}->{'value'}), #2
	find_name($input->{'FlightInfo_passenger'}->{'PersonName'}->{'value'}), #3
        $input->{'FlightInfo_glider'}->{'GliderName'}->{'value'}, #4
	find_name($input->{'FlightInfo_instructor'}->{'PersonName'}->{'value'}), #5
	find_name($input->{'FlightInfo_towpilot'}->{'PersonName'}->{'value'}), #6
	$input->{'FlightInfo_category'}->{'value'}->{'value'}, #7
	sprintf("%2.2d:%2.2d", #8
        	$input->{'FlightInfo_takeoff'}->{'ClockTime'}->{'ClockTime_hour'}->{'value'},
        	$input->{'FlightInfo_takeoff'}->{'ClockTime'}->{'ClockTime_minute'}->{'value'},
        	),
	sprintf("%2.2d:%2.2d", #9
        	$input->{'FlightInfo_landing'}->{'ClockTime'}->{'ClockTime_hour'}->{'value'},
        	$input->{'FlightInfo_landing'}->{'ClockTime'}->{'ClockTime_minute'}->{'value'},
        	),
	sprintf("%2.2d:%2.2d", #10
       		$input->{'FlightInfo_flight-time'}->{'FlightTime'}->{'FlightTime_hours'}->{'value'},
        	$input->{'FlightInfo_flight-time'}->{'FlightTime'}->{'FlightTime_minutes'}->{'value'},
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
This should have worked.  Tell your webmaster right away, 
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
  $logsheet{'dutyofficer'} =	find_name($input->{StaffInfo_dutyofficer}->{PersonName}->{value});
  $logsheet{'assistant'}   =	find_name($input->{StaffInfo_assistant}->{PersonName}->{value});
  $logsheet{'instructor'}  =	find_name($input->{StaffInfo_instructor}->{PersonName}->{value});
  $logsheet{'towpilot'}    =	find_name($input->{StaffInfo_towpilot}->{PersonName}->{value});
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
  #warn ("The pwd is $fulldir\n");
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
	if ($input =~ /^(\w+)\s+(\w+)$/);
  if (!$dbh) {
    db_connectify();
    }
  my($get_info) = $dbh->prepare("select distinct handle from aliases where name ='$input'");
  $get_info->execute();
  while (my $ans = $get_info->fetchrow_hashref()) {
    $answer = $ans->{'handle'};
    #warn "Answer is '$answer', input was '$input'\n";
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



