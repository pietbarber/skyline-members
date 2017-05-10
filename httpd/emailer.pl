#!/usr/bin/perl

	# This goes through the spr_audit database and finds any reports written within the last $x minutes
	# Collects all of the students, their instructors, the flying date
	# Then generates a page that gets emailed to the student and instructor
	# of his lesson review. 

	#####################################################
	# Immediate todo
	#####################################################

	# Uh.... nothing I think. 

use DBI;                # Allows access to DB functions
use strict;             # Create extra hoops to jump through
			# Comment out the less appropriate of these two: 
my ($DEBUG)=0; 		# Shut yer mouth with yer whinin' 
#my ($DEBUG)=1; 		# Be verbose with your whining. 
						# and pretend we're an instructor for debugging
my ($dbh);              # Handle for DB connections

connectify();           # Connect to DB
my %handle_labels = fetch_members(); # allows me to convert handles to names
my %handle_to_name = fetch_straight_members(); # allows me to convert handles to fname,lname format names
my %instructors = fetch_instructors(); # Gets me a list of the instructors

my (@students); 

find_new_reports(); 
exit;

	######################################################
	# Subroutines! 
	######################################################


sub find_new_reports { 
  my ($sql) = qq(select * from spr_audit where (CURRENT_TIMESTAMP-lastupdated)::interval < '24:00:00'); 
  #my ($sql) = qq(select * from spr_audit where ((CURRENT_DATE at TIME ZONE 'EST')::date-lastupdated::date) < 1;); 
  #my ($sql) = qq(select * from spr_audit where ((CURRENT_DATE at TIME ZONE 'GMT')::date-lastupdated::date) = 3;); 
  my $row;
  my $get_info = $dbh->prepare($sql); 
  $get_info->execute();
  while ( my $row = $get_info->fetchrow_hashref ) {
    #$answer{$row->{'handle'}}{'date'}= $row->{'report_date'};
    #$answer{$row->{'handle'}}{'instructor'}= $row->{'instructor'};
    #$answer{$row->{'handle'}}{'lastupdated'}= $row->{'lastupdated'};
    email_student_update($row->{'handle'}, $row->{'report_date'}, $row->{'instructor'}); 
    email_instructor_update($row->{'handle'}, $row->{'report_date'}, $row->{'instructor'}); 
    }
  }

sub email_student_update {
  my ($student) = shift; 
  my ($report_date) = shift; 
  my ($instructor) = shift; 
  my ($student_name)=$handle_to_name{$student};
  my ($instructor_name)=$handle_to_name{$instructor};
  my ($email)=fetch_email_for($student);
  my ($answer); 

  print "Fetching report for $student...\n" if $DEBUG; 
  my ($html_report) = show_verbose_report($report_date, $student);
  use HTML::Strip; 
  my $hs = HTML::Strip->new();
  my ($text_report) = $hs->parse($html_report); 
  $hs->eof;

  open (SENDMAIL, "|-")
        || exec ('/usr/sbin/sendmail', '-t', '-oi');
  my ($random_num);
  my (@allow_chars) = (0..9);
  for (1..24) {
    $random_num .= $allow_chars[int(rand($#allow_chars))];
    }
  print SENDMAIL "From: \"Skyline Instructors\" <instructors\@skylinesoaring.org>\n"; 
  print SENDMAIL "MIME-Version: 1.0\n";
  print SENDMAIL "X-Accept-Language: en-us, en\n";
  print SENDMAIL qq(To: \"$student_name\" <$email>\n) unless $DEBUG;
  print SENDMAIL qq(To: \"Piet Barber\" <piet\@pietbarber.com>\n) if $DEBUG;
  print SENDMAIL qq(CC: \"Piet Barber\" <piet\@pietbarber.com>\n) unless $DEBUG;
  printf SENDMAIL "Subject: Skyline Instruction Record Updated\n";
  printf SENDMAIL qq(Content-Type: multipart/alternative;
 boundary="------------$random_num"
This is a multi-part message in MIME format.
--------------$random_num
Content-Type: text/plain; charset=ISO-8859-1; format=flowed
Content-Transfer-Encoding: 7bit

Dear $student_name,
The Skyline Soaring Club Student Progress Report system has detected
that there are new updates to your training record: 

Flights on $report_date
$text_report

View your complete instruction record by going to:
http://members.skylinesoaring.org/STUDENTS/
------------------------------------------------------------------------

--------------$random_num
Content-Type: text/html; charset=ISO-8859-1
Content-Transfer-Encoding: 7bit

<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN">
<html>
<head>
  <meta content="text/html;charset=ISO-8859-1" http-equiv="Content-Type">
  <title>Instruction Report Has Been Updated</title>
</head>
<body bgcolor="#ffffff" text="#000000">

<p>Dear $student_name,<br> 
<u>The Skyline Soaring Club Student Progress Report</u> system has detected
that there are new updates to your training record: </p>

<h2>Flights on $report_date</h2>
$html_report

<p>View your complete instruction record by going to:
<a href = "http://members.skylinesoaring.org/STUDENTS/">http://members.skylinesoaring.org/STUDENTS/</a></p>
--------------$random_num--

);

  close (SENDMAIL);
  }

sub email_instructor_update {
  my ($student) = shift; 
  my ($report_date) = shift; 
  my ($instructor) = shift; 
  my ($student_name)=$handle_to_name{$student};
  my ($instructor_name)=$handle_to_name{$instructor};
  my ($email)=fetch_email_for($student);
  my ($answer); 

  print "Fetching report for $student...\n" if $DEBUG; 
  my ($html_report) = show_verbose_report($report_date, $student);
  use HTML::Strip; 
  my $hs = HTML::Strip->new();
  my ($text_report) = $hs->parse($html_report); 
  $hs->eof;

  open (SENDMAIL, "|-")
        || exec ('/usr/sbin/sendmail', '-t', '-oi');
  my ($random_num);
  my (@allow_chars) = (0..9);
  for (1..24) {
    $random_num .= $allow_chars[int(rand($#allow_chars))];
    }
  print SENDMAIL "From: \"Skyline Instructors\" <instructors\@skylinesoaring.org>\n"; 
  print SENDMAIL "MIME-Version: 1.0\n";
  print SENDMAIL "X-Accept-Language: en-us, en\n";
  print SENDMAIL "To: \"Skyline Instructors\" <instructors\@skylinesoaring.org>\n" unless $DEBUG; 
  print SENDMAIL qq(To: \"Piet Barber\" <piet\@pietbarber.com>\n) if $DEBUG;
  print SENDMAIL qq(CC: \"Piet Barber\" <piet\@pietbarber.com>\n) unless $DEBUG;
  printf SENDMAIL "Subject: SPR Updated for $student_name\n";
  printf SENDMAIL qq(Content-Type: multipart/alternative;
 boundary="------------$random_num"
This is a multi-part message in MIME format.
--------------$random_num
Content-Type: text/plain; charset=ISO-8859-1; format=flowed
Content-Transfer-Encoding: 7bit

Dear Instructors, 
$instructor_name has updated the training record for $student_name. 

Flights on $report_date
$text_report

View your complete instruction record by going to:
http://members.skylinesoaring.org/STUDENTS/
------------------------------------------------------------------------

--------------$random_num
Content-Type: text/html; charset=ISO-8859-1
Content-Transfer-Encoding: 7bit

<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN">
<html>
<head>
  <meta content="text/html;charset=ISO-8859-1" http-equiv="Content-Type">
  <title>Instruction Report Has Been Updated</title>
</head>
<body bgcolor="#ffffff" text="#000000">

<p>$instructor_name has updated the training record for $student_name.</p>

<h2>Flights on $report_date</h2>
$html_report

<p>View this student's complete instruction record:<br>
<a href = "http://members.skylinesoaring.org/INSTRUCTORS/SPR/?student=$student">Grid</a><br>
<a href = "http://members.skylinesoaring.org/INSTRUCTORS/SPR/?student=$student&notes=on">Instruction Record</a></p>
--------------$random_num--

);

  close (SENDMAIL);
  }





sub connectify {
	# Just connect to the database. 
  my $driver = "DBI::Pg";
  my $database = 'skyline';
  $dbh = DBI->connect("DBI:Pg:dbname=skyline")
        || die ("Can't connect to database $!\n");
  }

sub remove_amp {
  my ($input) = shift;
  $input =~ s/\&/\\\&/g;
  $input;
  }

sub by_lname {
	# Just sorts the dudes by last name. 
  $handle_labels{$a} cmp $handle_labels{$b};
  }

sub lesson_fields {
        # Fetch an assoc.array of the lesson plan names indexed by number.
  my %answer;
  my $row;

  my $get_info = $dbh->prepare(
	qq(select number, title from syllabus_contents));
  $get_info->execute();

  while ( my $row = $get_info->fetchrow_hashref ) {
    $answer{$row->{'number'}}= $row->{'title'};
    }
  %answer;
  }

sub get_flights_from_id {
	# Input is a flight_tracking_id
	# Output is an array (of one, in most cases)
	# of the flight_tracking_ids that share the
	# instructor, pilot, flight_date. 
  my ($input) = shift; 
  my (@these_flights); 
  my (@answer); 
  my ($sql)=qq#
	select flight_tracking_id, flight_date, pilot, instructor from flight_info where flight_tracking_id='$input'#;
  my $get_info = $dbh->prepare($sql);
  $get_info->execute();
  while (my $ans = $get_info->fetchrow_hashref) {
    push (@these_flights, $ans); 
    }
   for my $ans (@these_flights) { 
     my ($sql2)=sprintf (qq#
	select flight_tracking_id from flight_info where flight_date='%s' and pilot='%s' and instructor='%s'#,
	$ans->{'flight_date'}, 
	$ans->{'pilot'}, 
	$ans->{'instructor'}
	); 
    my $get_info = $dbh->prepare($sql2);
    $get_info->execute();
    while (my $ans = $get_info->fetchrow_hashref) {
      push (@answer, $ans->{'flight_tracking_id'}); 
      }
    }
  @answer; 
  }

sub get_flight_info {
	# Given a flight_tracking_id, gimme an array of flights (with flight info imbedded in em
	# that gives me what I need. 
  my $tracking_id = shift;
  my %answer;
  my ($count)=0;
  my ($sql)=qq#
	select * from flight_info where flight_tracking_id='$tracking_id' order by takeoff_time desc#;
  my $get_info = $dbh->prepare($sql);
  $get_info->execute();
  while (my $ans = $get_info->fetchrow_hashref) {
    for my $field (qw(flight_date flight_tracking_id instructor release_altitude days_ago glider pilot flight_time takeoff_time)) {
      $answer{$field}=$ans->{$field};
      }
    }
  \%answer; 
  }

sub percent_complete {
	# This shows a cool little graphic showing his progress 
	# according to how far he needs to go. 
	# The output will be two img tags of different size
	# showing his progress according to "needed_for_rating" 
	# and a percentage number. 
  my ($input) = shift; 
  my ($answer); 
  if (has_a_rating($input)) { 
    return ('<i> Rated Pilot </i>'); 
    }
  my ($still_needed_count); 
  my (%still_needed) = needed_for_solo($input, today()); 
  for (sort keys(%still_needed)) {
    $still_needed_count++;
    }
  my ($total_for_solo) = 1;  
  my $sql = qq(select count(*) as total from syllabus_contents where far_requirement != '');
  my $get_info = $dbh->prepare($sql);
  $get_info->execute();
  while (my $ans = $get_info->fetchrow_hashref()) {
    $total_for_solo=$ans->{'total'};
    }

  my ($done)=sprintf("%d", (1-($still_needed_count/$total_for_solo))*100); 
  my ($yet)=sprintf("%d", ($still_needed_count/$total_for_solo)*100);
  $answer=sprintf(qq(<table cellspacing="0" border="1"><tr><td height="10" width="%d" bgcolor="#44FF44"></td>
	<td width="%d" bgcolor="#888888"></td></tr></table>),
	$done,
	$yet,
	$done
	);

  $answer;
  }

sub needed_for_rating {
	# For a given handle, go through the syllabus.  
	# Find any items that are called out in 
	# the 61.87 and the PTS.   Find any items not listed, return them in an assoc_array. 
	# Don't search any records past $date_of; this allows us to have the retrospective of 
	# allowing older records to be inserted in. 

  my ($handle) = shift; 
  my ($date_of) = shift; 
  my ($done) = shift; 
  my (%already_done); 
  if ($done ne '') { 
    %already_done = %{$done}; 
    }
  my (%required); 
  my (%answer, %last_date);
  $handle =~ s/[^A-Za-z0-9]//g; 
  my $sql = qq(select number from syllabus_contents where far_requirement != '' and pts_aoa != ''); 
  my $get_info = $dbh->prepare($sql);
  $get_info->execute();
  while (my $ans = $get_info->fetchrow_hashref()) {
    $required{$ans->{'number'}}++; 
    }
  my $sql = qq( select distinct (number, mode) from student_syllabus3 where handle='$handle' and mode = 4 and signoff_date <= '$date_of');
  my $get_info = $dbh->prepare($sql);
  $get_info->execute();
  while (my $ans = $get_info->fetchrow_hashref()) {
    if ($ans->{'mode'} == 4) {
      delete($required{$ans->{'number'}}); 
      }
    }
  for my $ans (keys(%already_done)) { 
    
    delete($required{$ans}); 
    }
  %required; 
  }

sub needed_for_solo {
	# For a given handle, go through the syllabus.  i
	# Find any items that are called out in 
	# the 61.87 for solo flight.   Find any items not listed, return them in an assoc_array. 
	# Don't search any records past $date_of; this allows us to have the retrospective of 
	# allowing older records to be inserted in. 

  my ($handle) = shift; 
  my ($date_of) = shift; 
  my ($done) = shift; 
  my (%already_done); 
  if ($done ne '') { 
    %already_done = %{$done}; 
    }
  my (%required); 
  my (%answer, %last_date);
  $handle =~ s/[^A-Za-z0-9]//g; 
  my $sql = qq(select number from syllabus_contents where far_requirement != ''); 
  my $get_info = $dbh->prepare($sql);
  $get_info->execute();
  while (my $ans = $get_info->fetchrow_hashref()) {
    $required{$ans->{'number'}}++; 
    }
  my $sql = qq( select number, mode from student_syllabus3 where handle='$handle' and mode != 5 and mode >= 3 and signoff_date <= '$date_of');
  my $get_info = $dbh->prepare($sql);
  $get_info->execute();
  while (my $ans = $get_info->fetchrow_hashref()) {
    if ($ans->{'mode'} >= 3) {
      delete($required{$ans->{'number'}}); 
      }
    }
  for my $ans (keys(%already_done)) { 
    delete($required{$ans}); 
    }
  %required; 
  }

sub has_a_rating {
	# Does input person have a rating as of this date? (According to members database)
	# Do a quick hit to the DB to find out. 
	# 1: Yes
	# 0: No
	# FIXME date not implemented yet. at least it is currently silently ignored.  

  my $input=shift;
  my $date=shift;
  my $answer=0; 
  $input =~ s/[^A-Za-z0-9]//g; 
  my $sql = qq(select handle from members where handle='$input' and rating != 'S' and rating != 'N/A'); 
  my $get_info = $dbh->prepare($sql);
  $get_info->execute();
  my (%answer, %last_date);
  while (my $ans = $get_info->fetchrow_hashref()) {
    $answer{$ans->{'handle'}}++; 
    }
  $answer = 1 if exists ($answer{$input}); 
  $answer; 
  } 

sub today {
        # What is today?
        # We can probably purge this
  my @today = localtime; 
  sprintf ("%4.4d-%2.2d-%2.2d", $today[5]+1900, $today[4]+1, $today[3]);
  }

sub show_verbose_report {
	# For a given flight date, student, 
	# show me all of the syllabus items checked off, 
	# the progress up to this point 
	# The notes that this instructor has entered for this dude.  
	# Any output here just gets appended to $answer. 
  my ($date) = shift; 
  my ($student) = shift; 
  my ($answer); 
  my (@flights, $flight_count, %report_text);
  my ($sql)=qq#
	select flight_tracking_id from flight_info where pilot='$student' and instructor != '' and flight_date='$date' order by takeoff_time#;
  my $get_info = $dbh->prepare($sql);
  $get_info->execute();
  while (my $ans = $get_info->fetchrow_hashref) {
    push (@flights, $ans->{'flight_tracking_id'}); 
    }
  if (@flights) { 
    $answer .= qq(<table border="1" bgcolor="#FFFFFF"><tr bgcolor="#E0E0E0">
	<td>Glider</td><td>Release</td><td>Flight Time</td><td>Instructor</td></tr>);
    for my $flight_id (@flights) {
      $flight_count++; 
      my (%flight_information)=%{get_flight_info($flight_id)}; 
      $answer .= sprintf (qq(<tr><td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>),
	$flight_information{'glider'}, 
	$flight_information{'release_altitude'}, 
	$flight_information{'flight_time'},
	$handle_to_name{$flight_information{'instructor'}} 
	); 
      }
    $answer .= "</table>\n"; 
    }
 
  my(@outcome_labels) = (
	'Not Covered',
	'Demonstrated', 
	'Performed', 
	'Solo Proficient', 
	'Rating Proficient', 
	'Critical Issue'
	); 

  my (%lesson_outcome, $outcome_count, %lesson_result); 
  my ($sql)=qq#
	select number, mode from student_syllabus3 where handle='$student' and signoff_date='$date'#;
  my $get_info = $dbh->prepare($sql);
  $get_info->execute();
  while (my $ans = $get_info->fetchrow_hashref) {
    push(@{$lesson_outcome{$ans->{'mode'}}}, $ans->{'number'});
    $lesson_result{$ans->{'mode'}}++;
    $outcome_count++; 
    }

  if ($outcome_count) { 
    $answer .= qq(<br><table bgcolor="#FFFFFF" border="1"><tr bgcolor="#E0E0E0"><td>Performance Level</td><td>Results</td></tr>\n);
    for my $label (1..$#outcome_labels) {
      if ($lesson_result{$label}) { 
        $answer .= sprintf(qq(<tr><td><img src="http://skylinesoaring.org/icons/blobs/blob%d.png" align="absmiddle"> %s</td><td>%s</td></tr>\n), 
	   $label, 
	   $outcome_labels[$label], 
           lesson_labels(sort(@{$lesson_outcome{$label}})) 
	   );
        }
      else { 
        $answer .= sprintf(qq(<tr><td><img src="http://skylinesoaring.org/icons/blobs/blob%d.png" align="absmiddle"> %s</td><td><i>None</i></td></tr>\n), 
	   $label,
	   $outcome_labels[$label], 
	   );
        }
      }
    $answer .= "</table>\n"; 
    }

  $outcome_count=0; 

	# Now we start outputting the instructor comments sections, as appropriate

  my ($sql)=qq#
	select * from instructor_reports2 where handle='$student' and report_date='$date' order by lastupdated#;
  my $get_info = $dbh->prepare($sql);
  $get_info->execute();
  while (my $ans = $get_info->fetchrow_hashref) {
    my ($report); 
	# The original instructors reports were all 
	# plain text, and should be presented as pre
	# formatted text.  After this time, anything
	# else should be considered html, and doesn't have 
	# to be preformatted. 
    if ($ans->{'lastupdated'} < 1171287324) { 
      $report = "<pre>". $ans->{'report'} . "</pre>"; 
      }
    else { 
      $report=$ans->{'report'}; 
      } 
    $answer .= sprintf (qq(<br><table border="1" bgcolor="#FFFFFF">
<tr bgcolor= "#E0E0E0"><td><u>%s</u> wrote on %s UTC <br></td></tr>
<tr><td>%s</td></tr>
</table>),
    	$handle_to_name{$ans->{'instructor'}}, 
    	scalar localtime($ans->{'lastupdated'}), 
    	$report,
	); 
    }

  $answer;
  } 

sub dude_still_needs {
 	# If this guy is a non-rated pilot, he probably still has some lesson 
	# entries that are needed to be wiped out before he soloes or gets his 
	# check-off for a rating.  This is the section to show what he still needs 
	# to do. 
	# We input the student, the date of what is still needed (is this necessary?)
	# and go through the db trying to find what he still needs.  
  my ($student)=shift; 
  my ($date)=shift; 
  my ($answer); 
  my (%output_names)=lesson_fields();
  my %still_needs = needed_for_solo($student,  $date);  
  $answer .= sprintf qq(<tr><td bgcolor="#cccccc"><i>Progress Toward Solo:</i></td><td>%s</td></tr>\n), percent_complete($student); 

  $answer .= qq(<tr><td bgcolor="#cccccc"><i>Needs&nbsp;<img src="/icons/blobs/blob3.png" align="absmiddle">&nbsp;or&nbsp;<img src="/icons/blobs/blob4.png" align="absmiddle">&nbsp;for&nbsp;Solo</i></td><td>);
  my ($output_count)=0;
  for my $field (sort keys (%still_needs)) {

    $answer .= sprintf (qq(<a href="/TRAINING/Syllabus/%s.shtml" target="_syllabus" onmouseover="Tip('%s')" onmouseout="UnTip('')">%s</a>, ), 
		$field,
		$output_names{$field},
		$field
		);
    $output_count++;
    }
  if ($output_count == 0) {
    $answer .= qq(<i>None</i>); 
    }
  $answer .= qq(</td></tr>), 
  my %still_needs = needed_for_rating($student, $date);  
  $answer .= qq(<tr><td bgcolor="#cccccc"><i>Needs <img src="/icons/blobs/blob4.png" align="absmiddle">&nbsp;for&nbsp;Rating</i></td><td>);
  my ($output_count)=0;
  for my $field (sort keys (%still_needs)) {
    $answer .= sprintf (qq(<a href="/TRAINING/Syllabus/%s.shtml" target="_syllabus" onmouseover="Tip('%s')" onmouseout="UnTip('')">%s</a>, ), 
		$field,
		$output_names{$field},
		$field
		);
    $output_count++;
    }
  if ($output_count == 0) {
    $answer .= qq(<i>None</i>); 
    }
  $answer .= qq(</td></tr>); 
  $answer
  }

sub lesson_labels { 
 	# Given a list of lesson names, not numbers ( not 1a, 1b, 1c, etc) 
	# output a list of hyperlinks to the lesson plans, 
	# joined with spaces. 
  my (@input) = @_; 
  my ($answer); 
  my (%field_names) = lesson_fields(); 
  for my $lesson_number (0..$#input) { 
    $answer .= sprintf ( qq(<a href="http://skylinesoaring.org/TRAINING/Syllabus/%s.shtml">%s</a> \n),
	$input[$lesson_number], 
	$field_names{$input[$lesson_number]},
	$field_names{$input[$lesson_number]},
	); 
    }
  $answer; 
  } 


sub fetch_email_for {
        # Fetch an assoc.array of members.
  my $input=shift;
  my ($answer); 
  my $get_info = $dbh->prepare(
	qq(select email from members where handle='$input'));
  $get_info->execute();

  while ( my $row = $get_info->fetchrow_hashref ) {
    $answer = $row->{'email'}; 
    }
  $answer;
  }


sub fetch_members {
        # Fetch an assoc.array of members.
  my %answer;
  my $row;

  my $get_info = $dbh->prepare(
	qq(select handle, lastname, firstname, middleinitial, memberstatus, namesuffix from members));
  $get_info->execute();

  while ( my $row = $get_info->fetchrow_hashref ) {
    if ($row->{'namesuffix'} =~ /\w/) {
    $answer{$row->{'handle'}}= sprintf ("%s %s, %s %s",
	$row->{'lastname'},
	$row->{'namesuffix'},
	$row->{'firstname'},
	$row->{'middleinitial'},
	);
      }
    else {
    $answer{$row->{'handle'}}= sprintf ("%s, %s %s",
	$row->{'lastname'},
	$row->{'firstname'},
	$row->{'middleinitial'},
	);
      }
    }
  %answer;
  }

sub fetch_instructors {
        # Fetch an assoc.array of instructors.
  my %answer;
  my $row;

  my $get_info = $dbh->prepare(
	qq(select handle, lastname, firstname, middleinitial, memberstatus from members where instructor='true'));
  $get_info->execute();

  while ( my $row = $get_info->fetchrow_hashref ) {
    $answer{$row->{'handle'}}= sprintf ("%s, %s %s",
	$row->{'lastname'},
	$row->{'firstname'},
	$row->{'middleinitial'},
	);
    }
  %answer;
  }


sub start_page {
	# Prints the starting information for the page
	# Like the HTML headers, the DOCtypes,
	# The left-menu-headers, etc.
	# We basically just include the left-menu.scrap
  my $title = shift;
  my $header = shift;
  $title ||= "Instruction Report";
  print header unless $header eq 'noheader';
print <<EOM;
<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN">
<html>
<head>
  <meta http-equiv="Content-Type" content="text/html; charset=utf-8">
  <link rel="SHORTCUT ICON" href="/favicon.ico">
  <title>$title</title>
EOM
  print include('left-menu.scrap') unless $header eq 'noheader';
  beta_test();
  print h1($title);
  }

sub beta_test {
  print qq(<table border=0 bgcolor="FFE8E8"><tr><td><h2>NOTE WELL</h2>This page is going through beta
testing. Any information you enter here will not be permanently stored.  Please immediately report bugs 
or any feedback you have to Piet Barber (<a href="mailto:pb\@pietbarber.com">pb\@pietbarber.com</a>)</td></tr></table>
	); 
  }

sub end_page {
  print include('footer.scrap');
  exit;
  }

sub by_lastname {
        # Sort the list by the person's last name
  $handle_labels{$a} cmp $handle_labels{$b};
  }


sub escape {
	# This is a really ghetto way of escaping input. 
	# if i was smart i would use a Perl module that escapes properly. 
  my ($input) =shift;
  my ($answer);
  $answer = $input;
  $answer =~ s/'/\\\'/g;
  $answer =~ s/\?/&#077;/g;
  $answer;
  }


sub fetch_straight_members {
        # Fetch an assoc.array of members.
        # make names output like " Piet Barber " and not " Barber, Piet" 
        # the term straight has nothing to do with the sexual preference of the members
  my %answer;
  my $row;

  my $get_info = $dbh->prepare(
        qq(select handle, lastname, firstname, middleinitial, memberstatus, namesuffix from members));
  $get_info->execute();

  while ( my $row = $get_info->fetchrow_hashref ) {
    if ($row->{'namesuffix'} =~ /\w/) {
    $answer{$row->{'handle'}}= sprintf ("%s %s %s, %s",
        $row->{'firstname'},
        $row->{'middleinitial'},
        $row->{'lastname'},
        $row->{'namesuffix'},
        );
      }
    else {
    $answer{$row->{'handle'}}= sprintf ("%s %s %s",
        $row->{'firstname'},
        $row->{'middleinitial'},
        $row->{'lastname'},
        );
      }
    }
  %answer;
  }


__END__
