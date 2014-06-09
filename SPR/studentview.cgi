#!/usr/bin/perl

	# Studentview
	# This is mostly the same program as the instructor 
	# program, but has view only and no 
	# ability to see anybody else's stuff
	# and no ability to insert. 
	# hopefully. 


use CGI qw(:standard);  # Talk to the CGI stream
use DBI;                # Allows access to DB functions
use strict;             # Create extra hoops to jump through

			# Comment out the less appropriate of these two: 
my ($DEBUG)=0; 		# Shut yer mouth with yer whinin' 
my ($DEBUG)=1; 		# Be verbose with your whining. 
my ($the_student)=$ENV{'REMOTE_USER'}; 	# So we can override occasionally
#my ($the_student)='zbendorf'; 		# Override Here!
my ($dbh);              # Handle for DB connections
my (%syllabus);		# Contains the syllabus
my (%progress);		# Contains progress for somebody in particular
connectify();           # Connect to DB
my %handle_labels = fetch_members(); # allows me to convert handles to names
my %handle_to_name = fetch_straight_members(); # allows me to convert handles to fname,lname format names
my %flight_colspan; 	# For when we have more than one flight per lesson session. 

	# So now we go through the main list portion of the program

  if (!param) {
	# If the page is loaded with no parameters, 
    start_page(sprintf('Training Record for %s', $handle_to_name{$the_student}) );
	# Then print out all existing members; 
	# active students
    print mini_javascript();
    show_notes_page($the_student); 
    end_page();
    }
	# If the 'student' field has a value, 
	# and it matches up to a student in our database...
	# Then we need to show the student's record
	# and make the page editable by the instructor
	# If the submit button has been hit
	# then it's time to insert the data into the database. 

  elsif ($handle_to_name{param('student')}) {
    if (param('notes') eq 'on') {
      start_page("Instruction Record for " . $handle_to_name{$the_student});
      print mini_javascript();
      show_notes_page($the_student); 
      } 
    else {
      start_page($handle_to_name{$the_student});
      show_current_syllabus($the_student); 
      } 
    end_page();
    }

exit;


sub include {
	# Pull file from the INCLUDES directory
	# output of subroutine is that file.
  my $file = shift;
  my $title = shift;
  my $answer;
  open (INCLUDE, "/var/www/members/html/INCLUDES/$file") || print "Can't open that file $!";
  while (my $line = <INCLUDE>) {
    $answer .= $line;
    }
  close (INCLUDE);
  $answer;
  }

sub connectify {
	# Just connect to the database. 
  my $driver = "DBI::Pg";
  my $database = 'skyline';
  $dbh = DBI->connect("DBI:Pg:dbname=skyline")
        || die ("Can't connect to database $!\n");
  }

sub abort {
	# Kind of like an error handling page. 
	# The equivalent of die(), but outputs appropriate
	# HTML headers and stuff. 
  start_page(@_);
  print h1(@_);
  end_page(@_);
  exit;
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

sub mini_javascript {
	# If you need the cool javascript, 
	# but don' t need all the extra stuff for editing the textblock
	# use mini_javascript
  my $answer =<<EOM;
<!--ToolTip headers-->
<script language="JavaScript" type="text/javascript" src="/INCLUDES/wz_tooltip.js"></script>
<!--Spr specific headers-->
<script language="JavaScript" type="text/javascript" src="/INCLUDES/spr_header.js"></script>
EOM
  $answer;
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
  $answer=sprintf(qq(<table cellspacing="0" border="0"><tr><td width="%d" bgcolor="#44FF44"></td>
	<td width="%d" bgcolor="#888888"></td><td>&nbsp;%d%%</table>),
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
  my $sql = qq( select number, mode from student_syllabus3 where handle='$handle' and mode = 4 and signoff_date <= '$date_of');
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

sub fetch_count_list {
	# Given a column name, gimme the number of hits
	# for this $handle in this column. 
  my $handle = shift;
  my $mode = shift;
  my $get_info = $dbh->prepare(qq#
	select count(*) from student_syllabus3 where handle = '$handle' and mode = '$mode' #);
  $get_info->execute();
  $get_info->fetchrow();
  }

sub fetch_flight_info {
	# Subroutine for fetching in the flights for a particular
	# pilot. 
  my $handle = shift;
  my $limit = shift; 
  my @answer; 
  $limit ||= 200; 
  my ($count)=0;
  my ($sql)=qq#
	select flight_tracking_id, ((CURRENT_DATE at TIME ZONE 'EST')::date-flight_date::date) as days_ago, glider, flight_date, instructor, round(release_altitude/100,1)::real as release_altitude, instructor from flight_info where pilot='$handle' and instructor != '' and instructor !='$handle' order by flight_date desc limit $limit #;
  my $get_info = $dbh->prepare($sql);
  $get_info->execute();
  while (my $ans = $get_info->fetchrow_hashref) {
    my %answer;
    for my $field (qw(flight_date flight_tracking_id instructor release_altitude days_ago glider)) {
      $answer{$field}=$ans->{$field};
      }
    $answer[$count++] = \%answer; 
    }
  reverse(@answer);
  }


sub show_notes_page {
 	# For a given student, go through all the flight groupings, instruction reports, 
	# ground instruction reports, and show all of this in a big logbook format. 
  my ($student) = shift; 
  	# Here we need to go thru the database and find all dates of
	# flight_groups, instructor reports, ground_instruction reports (pending)
	# then send each one of those off 
  my (%answer); 
  my ($flight_sessions);
	# make up for my dumbness with more perl, and less SQL, I will just break
	# it out into two separate SQL hits, and join the two with an associative array. 
  my ($sql)=qq#
	select distinct signoff_date from student_syllabus3 where handle='$student' #;
  my $get_info = $dbh->prepare($sql);
  $get_info->execute();
  while (my $ans = $get_info->fetchrow_hashref) {
    $answer{$ans->{'signoff_date'}}++; 
    }

  my ($sql)=qq#
	select distinct report_date from instructor_reports2 where handle='$student'#;
  my $get_info = $dbh->prepare($sql);
  $get_info->execute();
  while (my $ans = $get_info->fetchrow_hashref()) {
    $answer{$ans->{'report_date'}}++; 
    }

  my ($sql)=qq#
	select distinct flight_date from flight_info where pilot='$student' and instructor != ''#;
  my $get_info = $dbh->prepare($sql);
  $get_info->execute();
  while (my $ans = $get_info->fetchrow_hashref()) {
    $answer{$ans->{'flight_date'}}++; 
    $flight_sessions++; 
    }
  if (! has_a_rating($student)) { 
    print qq(<ul><table border="0" bgcolor="#F8F8FF"><tr><td>\n); 
    print qq(According to our records, you do not have a glider rating. If this is incorrect, please notify the Member Meister and the Chief Flight Instructor of any necessary corrections by sending an email to <a href="mailto:membermeister\@skylinesoaring.org">membermeister\@skylinesoaring.org</a> . Flights and instruction not done at Skyline Soaring Club will not be included in this Training Report.<br>
<b>Note:</b> Flight totals and some counts are not included before 1 January 2005.<br>
<b>Note:</b> Flight Instruction done before 1 June 2009 could not be scored at level <img src="/icons/blobs/blob4.png" align="absmiddle">  ) ; 
    print h2("Current Status in the Training Program:"); 
    print qq(<a href="/STATS/?pilot=$student" target="_logbook">Show Flight Log</a> / \n); 
    print qq(<a href="?student=$student">Show Instruction Grid</a>\n); 
    print qq(<table border="1">\n); 
    print qq(<tr align="center" bgcolor="#E0E0E0"><td>Flights (ASK)</td><td>Flights (Grob)</td><td>Flights (Sprite)</td><td>Flights (Total)<td>Total Flight Time</td><td>Sessions</td><td>Most Recent Flight</td><td>Instructors</td></tr>\n); 

    my (%flights, @instructors, $total_flight_time, $max_date); 

    my ($sql)=qq#select glider, count(*) as count from flight_info where pilot='$student' group by glider#;
    my $get_info = $dbh->prepare($sql);
    $get_info->execute();
    while (my $ans = $get_info->fetchrow_hashref()) {
      $flights{$ans->{'glider'}}=$ans->{'count'}; 
      }

    my ($sql)=qq#select distinct instructor from flight_info where pilot='$student' and instructor != ''#;
    my $get_info = $dbh->prepare($sql);
    $get_info->execute();
    while (my $ans = $get_info->fetchrow_hashref()) {
      push (@instructors, $handle_to_name{$ans->{'instructor'}}); 
      }

    my ($total_flights); 
    my ($sql)=qq#select count(*) from flight_info where pilot='$student'#;
    my $get_info = $dbh->prepare($sql);
    $get_info->execute();
    while (my $ans = $get_info->fetchrow_hashref()) {
      $total_flights=$ans->{'count'}; 
      }

    my ($sql)=qq#select max(flight_date) as max_date, sum(flight_time) as totals from flight_info where pilot='$student'#;
    my $get_info = $dbh->prepare($sql);
    $get_info->execute();
    while (my $ans = $get_info->fetchrow_hashref()) {
      $max_date=$ans->{'max_date'}; 
      $total_flight_time=$ans->{'totals'}; 
      }

    printf (qq(<tr align="center"><td>%s</td><td>%s</td><td>%s</td><td>%s<td>%s</td><td>%s</td><td>%s</td><td align="left">%s</td></tr>\n),
	($flights{'ASK-21'}+0), 
	($flights{'GROB 103'}+0), 
	($flights{'Sprite'}+0), 
	($total_flights+0), 
	$total_flight_time, 
	$flight_sessions, 
	$max_date, 
	join (", ", @instructors), 
	
	); 

    print qq(</table><br>\n); 
    print qq(<table border="1">\n); 
    print dude_still_needs($student, today());
    print "</table></td></tr></table></ul>\n"; 
    }
  else {
    print qq(<a href="/STATS/?pilot=$student" target="_logbook">Show Flight Log</a> / \n); 
    print qq(<a href="?student=$student">Show Instruction Grid</a>\n); 
    }

  for my $date (reverse sort keys (%answer)) {
    print h3("Flights / Instruction on $date"); 
    print "<ul>\n"; 
    print show_verbose_report($date, $student); 
    print "</ul>\n"; 
    }
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
        $answer .= sprintf(qq(<tr><td><img src="/icons/blobs/blob%d.png" align="absmiddle"> %s</td><td>%s</td></tr>\n), 
	   $label, 
	   $outcome_labels[$label], 
           lesson_labels(sort(@{$lesson_outcome{$label}})) 
	   );
        }
      else { 
        $answer .= sprintf(qq(<tr><td><img src="/icons/blobs/blob%d.png" align="absmiddle"> %s</td><td><i>None</i></td></tr>\n), 
	   $label,
	   $outcome_labels[$label], 
	   );
        }
      }
    $answer .= "</table>\n"; 
    }

  $outcome_count=0; 
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
<tr bgcolor= "#E0E0E0"><td><u>%s</u> wrote on %s<br></td></tr>
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
 	# Given a list of lesson numbers ( 1a, 1b, 1c, etc) 
	# output a list of hyperlinks to the lesson plans, 
	# joined with spaces. 
	# Also, do whatever types of shenanigans you need to to make 
	# that cool javascript tip thing work. 
  my (@input) = @_; 
  my ($answer); 
  my (%field_names) = lesson_fields(); 
  for my $lesson_number (0..$#input) { 
    $answer .= sprintf ( qq(<a href="http://skylinesoaring.org/TRAINING/Syllabus/%s.shtml" 
	target="_lesson"
	onMouseover="Tip('%s');" onMouseout="UnTip('');">%s</a> \n),
	$input[$lesson_number], 
	$field_names{$input[$lesson_number]},
	$input[$lesson_number]
	); 
    }
  $answer; 
  } 
 
sub show_current_syllabus {
	# Just like the subroutine says; show the current syllabus for $user
	# Seems simle enough, eh? 
	# Need to get all of the flights out of the flight_info database. 
  my ($user) = $the_student;
  my (%flight_cols);			# All the information about a flight per lesson number
  my (@flights);			# All the stuff about the flights for this guy.
  my (%syllabus) = gimme_syllabus();	# All the info about the syllabus in general
  print mini_javascript();		# Just enough javascript to get the blobs to work
  my ($sql) = gimme_sql($user);		# Give me the SQL for given user
  my $get_info = $dbh->prepare($sql);	# Fetch database for that SQL
  print start_form(-id=>'myform');	# The form is named 'myform' do HTML headers for form
  print hidden('handle', $user);	# we have to secretly include the handle
  #print h2("$handle_to_name{$user}");	# print out the title at the top of the page with dude's name
  print <<EOM;
<table border="0">  
<tr align="center"><td bgcolor="#888888" colspan="5"><font color="#FFFFFF">Key:</font></td></tr>
<td><img src="/icons/blobs/blob0.png"></td><td>Not Covered</td><td>&nbsp;</td>
<td><img src="/icons/blobs/blob1.png"></td><td>Demonstrated</td></tr>
<td><img src="/icons/blobs/blob2.png"></td><td>Performed</td><td >&nbsp;</td>
<td><img src="/icons/blobs/blob3.png"></td><td>Solo Proficient</td></tr>
<td><img src="/icons/blobs/blob4.png"></td><td>Rating Proficient</td><td >&nbsp;</td>
<td><img src="/icons/blobs/blob5.png"></td><td>Critical Issue</td></tr>

<td align="center" colspan=5 bgcolor="#888888"><font color="#FFFFFF">Backgrounds</font></td></tr>
<td bgcolor="#AAAADD"></td><td>Max score > 20 flights prior</td><td >&nbsp;</td>
<td bgcolor="#AADDAA"></td><td>Maximum Attained</td></tr>
EOM


    if (! param('limit')) {
      printf qq(<tr align="left"><td><td colspan="3" align="left"><a href="?student=%s&limit=1000">Show all flights</a> (if appropriate)</td>),
	$user;
      }
    else {
      printf qq(<tr align="left"><td><td colspan="3" align="left"><a href="?student=%s">Show 20 most recent flights</a></td>),
	$user;
      }
    printf (qq(<td><a href="/STATS/?pilot=$user">Show Flight Log</a><br><a href="?student=$user&notes=on">Show Instruction Record</a> </td> </tr>)); 



  print "</table><br>\n";

  print '<table border = "1" bgcolor = "#FFFFFF">' . "\n";
  my ($limit)=param('limit');
  $limit ||= 20; 
  @flights=fetch_flight_info($user,$limit); 
  if ($#flights == 19) {
    unshift (@flights, 
	{ 'flight_date' => $flights[0]->{'flight_date'},
	  'flight_tracking_id' => '-1',
	  'instructor' => '-',
	  'release_altitude' => '-',
	  'days_ago' => '<i>Prev</i>',
	  'glider' => '-' }
	);
    }
 
  push (@flights, 
	{ 'flight_date' => '-',
	  'flight_tracking_id' => '-2',
	  'instructor' => '-',
	  'release_altitude' => '-',
	  'days_ago' => '<i>Max</i>',
	  'glider' => '-' }
	);
  for my $flight_number (0 .. $#flights) {
    #next if $flight_colspan{$flight_number};
    my($id)=$flights[$flight_number]->{'flight_tracking_id'}; 

    $flight_cols{$id}=column_for_this_flight(
		$user,
		$flights[$flight_number]->{'instructor'},
		$flights[$flight_number]->{'flight_date'},
		#$flights[$flight_number]->{'flight_tracking_id'},
		$flights[$flight_number]->{'days_ago'}
		);
    }
 
  print "</tr>\n"; 
  print_header_bar('Days Ago', 'days_ago', @flights);
  print_header_bar('Glider', 'glider', @flights);
  print_header_bar('Tow Release (x100)', 'release_altitude', @flights);
  print_header_bar('Instructor', 'instructor', @flights);

  print '<tr bgcolor="#444444">' . "\n";
  for my $lesson ('Lesson','Phase&nbsp;&nbsp;') {
    printf ('<td align="right"><font color ="#FFFFFF" size="+1">%s</font></td>', $lesson);
    }
  printf qq(<td colspan="%d"></td></tr>), ($#flights+1);
  print "</tr>\n";

  
  for my $lesson_number (sort keys(%syllabus)) {
	# Start going through all of our keys in the syllabus and call each key
	# $lesson_number.  Some example lesson numbers might be 1a, 1b, 1c, etc. 
    my(%flight_count);
    if ($lesson_number =~ /^\d[a-z]/) {
	# If we have a lesson number that is just a digit, like '3', we are not interested. 
	# So in this section, we need a lesson number like 1a, and not '1'

	# First, print the name of the lesson, and when you mouseover this name, 
	# you get the full name.  The default is to print the abbreviation. 
      printf (qq(<tr><td>%s</td><td align="right">%s</td>),
	$lesson_number,
	href_tipify(
		"http://skylinesoaring.org/TRAINING/Syllabus/$lesson_number.shtml",
		$syllabus{$lesson_number}->{'title'},
		$syllabus{$lesson_number}->{'description'},
		)
	); 
	
      for my $flight_number (0..$#flights) {
		# We pulled in the information for the flights earlier, and stuck them into the 
		# %flights assoc.array.  It is packed with information, and now we are going 
		# to start printing out all that information for each of the flights for this
		# student and his flights, and particulars for each flight. 

		# This silly line is to group up the flights with the instructor, student, and date groupings
        next if $flight_count{$flights[$flight_number]->{'flight_date'}}{$flights[$flight_number]->{'instructor'}};
		# Keep track of the instructors with this student on this date with this counter that we 
		# will start incrementing now.  If this number is a non-zero, we will skip it 
		# on the next loop through.  
        $flight_count{$flights[$flight_number]->{'flight_date'}}{$flights[$flight_number]->{'instructor'}}++;
        my ($id) = $flights[$flight_number]->{'flight_tracking_id'};
        my ($bgcolor)="#FFFFFF";
        my $lesson_ball=lesson_ball($flight_cols{$id}->{$lesson_number},$lesson_number,$flight_number);
        if ($flight_number == $#flights) {
          $bgcolor="#AADDAA";
          }
        if ($flight_number == 0 && $#flights == 21) {
          $bgcolor="#AAAADD";
          }

       printf (qq(<td colspan="%s" bgcolor="%s" align="center">%s</td>\n),
	# wonky 
	  $flight_colspan{$flights[$flight_number]->{'flight_date'}}{$flights[$flight_number]->{'instructor'}},
	  $bgcolor,
	  $lesson_ball
	  );
        }
      }
    else {
      printf (qq(<tr bgcolor="#888888"><td><font color="#FFFFFF">%s</font></td>\n) .
		qq(<td align="right"><font color="#FFFFFF">%s</font></td>), 
		$lesson_number,
		$syllabus{$lesson_number}->{'title'}
		);
      printf qq(<td colspan="%d"></td></tr>), ($#flights+1);
      }
    print "</tr>\n"; 
    }
  print '</table>' . "\n";
  print end_form;
  }

sub print_header_bar {
	# This was kind of repetitive, so I made it so that 
	# the top grey bar used when printing out the syllabus
	# is just a subroutine.
	# title is the name of the header bar.
	# input is the name of flights information we want. 
	# output is printed straight away and not shoved into some $answer;
  my $title=shift;
  my $input=shift;
  my @flights = @_;
  print qq(<tr bgcolor="#DDDDDD" align="right"><td colspan="2">$title</td>\n);
  for my $flight_number (0..$#flights) {
    my $output_line = $flights[$flight_number]->{$input};
    if ($input eq 'days_ago') {
      $output_line = tipify( 
	$flights[$flight_number]->{'flight_date'}, 
	$flights[$flight_number]->{'days_ago'}
	);
      }
    elsif ($input eq 'instructor') {
      $output_line = instructor_initials($flights[$flight_number]->{$input}); 
      }
    elsif ($input eq 'glider') {
      $output_line = glider_abbreviation($flights[$flight_number]->{$input});
      }

    printf (qq(<td><font size="-1">%s</font></td>\n),
	$output_line);
    }
  print "</tr>\n";
  }



sub lesson_ball {
	# Just a shortcut to draw all the HTML needed to make the progresws ball 
	# Input is the number 0 through 5 
	# second input is the number of the lesson plan
	# third number is the number of the flight
	# output is HTML to draw the ball of progress 
  my ($input)=shift; 
  my ($lesson_number) = shift;
  my ($flightno) = shift; 
  my ($blobno) = $input+0; 
  my ($answer);
  my ($js_id) = sprintf ("s-%s-%s", $lesson_number, $flightno);
  $answer = sprintf (qq(<img border="0" 
	src="/icons/blobs/blob%s.png", 
	id="%s"
	onmouseover="Tip(levels_description[%s])"
	onmouseout="UnTip('')">),
	$blobno,
	$js_id,
	$blobno,
	);
  $answer;
  }

sub instructor_initials {
	# Take a handle of an instructor
	# Return the intials of him
	# with javascript that makes his name expanded
  my $input=shift;
  return '-' if $input eq '-'; 
  my ($initials) = $1 if ($input =~ /^(..)/);
  $initials =~ tr/a-z/A-Z/;
  my ($answer)=tipify($handle_to_name{$input}, $initials);
  $answer;
  }

sub href_tipify {
 	# Take two inputs
	# first input is what you show
	# second input is what you hint
	# This will be a non-hyperlinked tip. 
  my $url=shift;
  my $what_you_tip=shift;
  my $what_you_show=shift;
  $what_you_show ||= $what_you_tip;
  sprintf (qq(<a href="%s" onmouseover="Tip('%s')" onmouseout="UnTip('')">%s</a>),
	$url,
	$what_you_tip,
	$what_you_show
	);
  }

sub tipify {
 	# Take two inputs
	# first input is what you show
	# second input is what you hint
	# This will be a non-hyperlinked tip. 
  my $what_you_tip=shift;
  my $what_you_show=shift;
  sprintf (qq(<a name="#" onmouseover="Tip('%s')" onmouseout="UnTip('')">%s</a>),
	$what_you_tip,
	$what_you_show
	);
  }

sub glider_abbreviation {
	# Take a glider name 
	# Return "G", "K", or "O"
	# For the Grob, the K or other
  my $input=shift;
  my %answers=('GROB 103' => 'G', 'CAPSTAN' => 'C', 'ASK-21' => 'K', '-' => '-', '' => '-' ); 
  $answers{$input} || "O";
  }


sub user_has_rating {
	# This is a quick check to the db to see if the user 
	# in question has a rating or not. 
  my ($user) = shift;
  my ($answer) = 1;
  my ($ans);
  my ($sql) = sprintf <<EOM, $user;
select rating from members where handle='%s';
EOM
  my ($ans);
  my $get_info = $dbh->prepare($sql);
  $get_info->execute();

  while ($ans = $get_info->fetchrow_hashref) {
    if ($ans->{'rating'} eq 'S' || $ans->{'rating'} eq 'N/A') {
      $answer = 0;  
      }
    }
  $answer;
  }

sub gimme_sql {
  my ($user) = shift;
  my ($sql) = sprintf <<EOM, $user;
select * from student_syllabus3 where handle = '%s' order by number; 
EOM
  $sql;
  }


sub column_for_this_flight {
  	# For a given user and flight (use the tracking id if possible)
	# output all of the syllabus markups for that flight 
	# If no tracking_id is present in the DB, then match on the 
	# flight_date and the instructor, and assume that 
	# any progress for the student on that day copies over to all 
	# flights. 
  my ($handle) = shift; 
  my ($instructor) = shift; 
  my ($flight_date) = shift; 
  #my ($flight_tracking_id) = shift; 
  my ($days_ago) = shift; 
  my (%answer); 
  my ($sql);
  $flight_colspan{$flight_date}{$instructor}++; 
  if ($days_ago eq '<i>Max</i>') {
    $sql = sprintf <<EOM;
select number, max(mode) as mode from student_syllabus3 where ( handle='$handle' and mode != 5 )
	group by number;
EOM
    }
  elsif ($days_ago eq '<i>Prev</i>') {
    $sql = sprintf <<EOM;
select number, max(mode) as mode from student_syllabus3 where ( handle='$handle' and signoff_date < '$flight_date' and mode != 5) group by number;
EOM
    }
  else {
    $sql = sprintf <<EOM; 
select number, mode from student_syllabus3 where handle='$handle' and (instructor='$instructor' and signoff_date='$flight_date');
EOM
    }
  my ($ans);
  #open OUTFILE, ">>/tmp/outfile.txt";
  #print OUTFILE "$sql \n\n";
  #close OUTFILE;
  my $get_info = $dbh->prepare($sql);
  $get_info->execute();

	# wonky
  while ($ans = $get_info->fetchrow_hashref) {
    $answer{$ans->{'number'}}=$ans->{'mode'};
    $answer{'marked'}++;
    }

  \%answer;
  }


sub gimme_syllabus {
	# Fetches the syllabus contents from the databse. 
  my (%answer);
  my ($sql) = sprintf <<EOM;
select * from syllabus_contents order by number; 
EOM
  my ($ans);
  my $get_info = $dbh->prepare($sql);
  $get_info->execute();

  while ($ans = $get_info->fetchrow_hashref) {
    for my $key ('number', 'title', 'description', 'far_requirement', 'pts_aoa' ) {
      $answer{$ans->{'number'}}{$key}=$ans->{$key};
      }
    }
  %answer;
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
  print h1($title);
  }

sub end_page {
  print include('footer.scrap');
  exit;
  }

sub by_lastname {
        # Sort the list by the person's last name
  $handle_labels{$a} cmp $handle_labels{$b};
  }


sub enter_data_table {
	# The table that you enter your report in. 
	# the elm1 is the super cool javascript that makes all the syntax highlighting, etc. 

  my ($input)=shift; 
  print "<br><b>Enter Additional Comments (Optional)</b> <br>\n";
  print textarea(
	-name => "$input",
	-rows => "15",
	-cols => "80",
	-id => 'elm1'
	);
  }

sub mail_instructor_report {
	# I don't think this actually sends anything useful for now
	# I also don't know if it's being called yet. 
	# I should really look into this
	# FIXME
  open (SENDMAIL, "|-")
        || exec ('/usr/sbin/sendmail', '-t', '-oi');
  my ($random_num);
  my (@allow_chars) = (0..9);
  for (1..24) {
    $random_num .= $allow_chars[int(rand($#allow_chars))];
    }
  use HTML::Strip; 
  my $hs = HTML::Strip->new();

  my (@text_report) = (
	($handle_labels{param('handle')} || sprintf ("%s, %s", param('lastname'), param('firstname'))),
	$handle_labels{param('instructor')},
	param('report_date'),
	$hs->parse(param('text'))
	);
  
  printf SENDMAIL "From: \"%s\" <%s\@skylinesoaring.org>\n", 
	$handle_labels{param('instructor')}, 
	param('instructor');
  printf SENDMAIL "MIME-Version: 1.0\n";
  printf SENDMAIL "X-Accept-Language: en-us, en\n";
  #print SENDMAIL "To: \"Skyline Instructors\" <instructors\@skylinesoaring.org>\n";
  print SENDMAIL "To: \"Piet Barber\" <pbarber\@skylinesoaring.org>\n";
  #printf SENDMAIL "Subject: Instruction Report for %s\n", param('report_date');
  printf SENDMAIL "Subject: IR for %s\n", $text_report[0];

printf SENDMAIL <<EOM, @text_report, show_content(), end_html();
Content-Type: multipart/alternative;
 boundary="------------$random_num"
This is a multi-part message in MIME format.
--------------$random_num
Content-Type: text/plain; charset=ISO-8859-1; format=flowed
Content-Transfer-Encoding: 7bit

    Instruction Report on file for %s

         Instructor: %s
Date of Instruction: %s

%s

Enter Instruction reports by going to: 
http://members.skylinesoaring.org/INSTRUCTORS/Instructor%20Reports/
------------------------------------------------------------------------

--------------$random_num
Content-Type: text/html; charset=ISO-8859-1
Content-Transfer-Encoding: 7bit

<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN">
<html>
<head>
  <meta content="text/html;charset=ISO-8859-1" http-equiv="Content-Type">
  <title>Instruction Report</title>
</head>
<body bgcolor="#ffffff" text="#000000">
%s

Enter Instruction reports by going to: <br>
<a href = "http://members.skylinesoaring.org/INSTRUCTORS/Instructor%20Reports/">http://members.skylinesoaring.org/INSTRUCTORS/Instructor%20Reports/</a>
%s
--------------$random_num--


EOM

  close (SENDMAIL);
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

sub print_hidden_fields {
	# In case of debug, please to printing out all hiddenfields. 
  for my $field (param) {
    print hidden($field);
    print "\n";
    }
  }


sub leet {
  # ($ENV{'REMOTE_USER'} eq 'pbarber' || $ENV{'REMOTE_USER'} eq 'jkellett');
  0;
  }

__END__
