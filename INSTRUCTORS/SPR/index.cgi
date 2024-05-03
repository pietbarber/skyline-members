#!/usr/bin/perl


	#####################################################
	# Immediate todo
	# Get submitted information insertified into the database
	# but first... need to do some sanity checks to ensure 
	# that bad shit isn't being inserted into the db. 
	#####################################################


	# One stop shopping for SPR version 2.0
	# Combine the flights in the flight_info data base with the 
	# Student Progress Reports -- This allows instructors to comment
	# on any or all aspects of all flights with students. 
	# If any further information is necessary for any flight, 
	# it can be added in with what used to be the Instructor Reports 
	# interface.

	# So now we have a combination of Instructors Report and SPR and 
	# the flight statistics program. 

	# Uses the database extensively. 


	# To Do List, which is painfully long: 
	# 13) Make opportunity for return to grid work. 
	# 14) Make a place for AC 61-65E signoffs to get explicitly recorded. 


	# Has been removed from this program for scope issues 
	# 4) Get the ability for the student to check off that he has 
	#    reviewed the page and accepted the output (out of scope)
	# 6) Get the email notification that somebody's syllabus has been updated
	#    to be mailed to members, and also to instructors  (separate program
	#    out of scope. 
	# <s>9) Maybe allow a function to only print flights where there is some sort
	#    of remark from an instructor. </s>

	# To be currently in the processes of doing: 

	# To Do that is Done: 
	# Make the instructor have the ability to mark off quals for the membership
	# (front seat, back seat, solo, etc). 
	# Make the instructor have the ability to add an endorsement for each flying event or 
	# Ground instruction event. 
	# 15) make history of flight records nicer to look at
	# 1) make it so that ground instruction, or mark-offs without
	#    a specific flight involved can be remarked. (like if dude
	#    does the written test on a day when he doesn't fly) 
	# 5) Get the ability for an instructor to log flights that day
	#    instead of having to wait for the flights to be entered into the 
	#    flight_info database. 
	# 7) Actually make insert button insert stuff into the database. 
	# 11) Check for sanity before insertion. (Unlike many girlfriends I had in college)
	#      well.... sorta accomplished. 
	# 2) Make it so that multiple flights within a day get grouped together
	#    (which should be very hard) 
	# 3) Get the first click by default thing to actually work 
	# 8) Allow a limit override to allow more flights than just 20. 
	# 10) Give instructor one more time to review stuff. 
        # 12) Make a page that shows all of the instruction reports built in 
	#    with all of the syllabus tick-off-items. 


use CGI qw(:standard);  # Talk to the CGI stream
use DBI;                # Allows access to DB functions
use strict;             # Create extra hoops to jump through

			# Comment out the less appropriate of these two: 
my ($DEBUG)=0; 		# Shut yer mouth with yer whinin' 
#my ($DEBUG)=1; 		# Be verbose with your whining. 
my ($the_instructor)=$ENV{'REMOTE_USER'}; 	# So we can override occasionally
#my ($the_instructor)='cstover' if $ENV{'REMOTE_USER'} eq 'pbarber'; 	# So we can override occasionally
						# and pretend we're an instructor for debugging
my ($dbh);              # Handle for DB connections
my %user_permissions;   # assoc.array to store permissions
my (%syllabus);		# Contains the syllabus
my (%progress);		# Contains progress for somebody in particular
my ($submission)=0;	# this wouldn't be here if i wasn't so lazy.
my ($max_days_ago)=30;	# Don't let me insert reports older than this number
			# Don't show pending reports older than that number either. 

connectify();           # Connect to DB
my %handle_labels = fetch_members(); # allows me to convert handles to names
my %handle_to_name = fetch_straight_members(); # allows me to convert handles to fname,lname format names
my %instructors = fetch_instructors(); # Gets me a list of the instructors
my %flight_colspan; 	# For when we have more than one flight per lesson session. 

	# So now we go through the main list portion of the program
	
	# If this user didn't need to authenticate to get here, then
	# just show them an empty training syllabus, and no form or means
	# to get them to show a student's information, or enter in new info. 

	# If the user authenticated, and that user is an instructor...
if (is_user_instructor($the_instructor) || $the_instructor eq 'evanweezendonk1') {
	# If there were no arguments passed, then just show a 
	# list of the students. 
  if (!param) {
	# If the page is loaded with no parameters, 
    start_page('Student Progress Reports' );
	# First pring a listing of all the instructor's pending reports
    pending_reports($the_instructor);
    print qq(<a href="?comments=on">Add Comments or Quals to a Student Record</a><br>\n);
    print qq(<a href="?ground=on">Log Ground Instruction</a><br>\n);
    print qq(<a href="?logflight=on">Log Flight Instruction</a> (when the log sheet is not yet uploaded by a DO)<br>\n);
	# Then print out all existing members; 
	# active students
    print qq(<table border = "0"><tr valign="top"><td>);
    print br, hr; 
    print h2("Active Students");
    show_student_list('active student');
 	# Inactive people  (that list is ever growing!) 
    print h2("Recently Inactive Students");
    show_student_list('inactive student');

    print h2("All Resigned or Inactive Members");
    show_student_pulldown('inactive student');
    print qq(</td><td>&nbsp;&nbsp;&nbsp;</td><td valign="top">\n);
    print br, hr; 
	# Active Rated pilots
    print h2("Active Rated Pilots");
    show_student_list('active rated');
    print qq(</td></tr>\n);
    print qq(</table><br>\n); 
    end_page();
    }
	# If the 'student' field has a value, 
	# and it matches up to a student in our database...
	# Then we need to show the student's record
	# and make the page editable by the instructor
	# If the submit button has been hit
	# then it's time to insert the data into the database. 

  elsif ($handle_to_name{param('student')}) {
    if (param('ground_instruction') eq 'on') {
	warn "Insertifiying Ground Instruction now. \n" if $DEBUG; 
      insertify_ground_instruction(); 
      }
    elsif (param('missing_flight_instruction') eq 'on') {
      insertify_flight_instruction(); 
      }

    if (param('adding_comment') eq 'on') {
     start_page("Adding Comments for " . $handle_to_name{param('student')});
      print full_javascript();
      show_expired_status(param('student'));
        # Let's check to see if he has a comment from this instructor,
        # for this day.  If so, we'll just read in that information, and make it
        # easier for the instructor to simply update the record, rather than kablooey'ing
        # all over him for trying to add a comment. 
      check_for_existing_comments(param('student'), param('datefield'));  
      insertify_just_comments();
      }
    elsif (param('notes') eq 'on') {
      start_page("Instruction Record for " . $handle_to_name{param('student')});
      print mini_javascript();
      show_expired_status(param('student'));
      show_notes_page(param('student')); 
      } 
    elsif (param('areas') eq 'on') {
      start_page($handle_to_name{param('student')});
      show_expired_status(param('student'));
      show_sheet(param('student')); 
      }
    else {
      start_page($handle_to_name{param('student')});
      show_expired_status(param('student'));
      show_current_syllabus(param('student')); 
      } 
    end_page();
    }

  elsif (param('logflight') eq 'on') {
    start_page('Log New Flight Instruction');
    print qq(<a href="?">Return to Main</a>\n);
    print start_form();
    flight_instruction_logger();
    end_page();
    }

  elsif (param('comments') eq 'on') {
    start_page('Add Comments to a Student\'s Record');
    print qq(<a href="?">Return to Main</a>\n);
    print start_form();
    comment_logger();
    end_page();
    }

  elsif (param('ground') eq 'on') {
    start_page('Log Ground Instruction');
    print qq(<a href="?">Return to Main</a>\n);
    print start_form();
    instruction_logger();
    end_page();
    }

	# so I see somebody has hit the final_submit button.
	# Here is where we do some checks 
	# and then throw the shit into the db. 
  elsif (param('final_submit') eq 'Submit Report') {
    if (param('comments_added') eq 'on') {
      start_page("Inserting Comments for " . $handle_to_name{param('handle')});
      handjam_comments();
      print hr(); 
      pending_reports($the_instructor);
      print qq(<a href="?">Return to Main</a><br>\n);
      print qq(<a href="?comments=on">Add Qualifications or Endorsements for another member</a>\n);
      end_page();
      }
    else {
      start_page($handle_to_name{param('handle')});
      verbose_output() if $DEBUG;
      submit_final_report();
      print hr(); 
      pending_reports($the_instructor);
      print qq(<a href="?">Return to Main</a>\n);
      end_page();
      }
    }

  elsif (param('submit') eq 'Record This as a Default Demo Flight') {
    my(@flights)=fetch_flight_info(param('handle'),10);
    my ($theflight)=$flights[0]{'flight_tracking_id'}; 
    for my $lesson_number ('1c', '1d', '2d', '2e', '2f', '2h', '2i', '2h', '2i', '2l') {
      param('s-' . $lesson_number . '-' . $theflight, '1'); 
      }
    allow_for_instructor_comments(); 
    end_page(); 
    }
	# So, I see that soembody has hit the submit_information button
	# This means the instructor is expected to review the report
	# and submit comments if they like. 
	# After this submit is submitted, they will go to the 
	# elsif clause just above, ( submit Report) 
  elsif (param('submit') eq 'Proceed') {
    allow_for_instructor_comments();
    end_page();
    }

	# You have craftilly sifted your way through all of my 
	# tests.  This means you get a verbose output
	# and you have no clue how you got here. 
	# I will add some notifications to the webhamster later. 
	# maybe some sort of error saying you did something terrible.  
	# At least the person who got us here had to be an instructor. 
  elsif (param('submit') eq 'Record Ground Instruction') {
    }

  else {
    start_page("How did you get here?");
    print qq(<a href="https://www.youtube.com/watch?v=5IsSpAOD6K8&t=51s">Click Here for Additional Details</a><br>\n);
    verbose_output() if $DEBUG;
    end_page();
    }
  }

	# If we got here, he who views this page isn't
	# an instructor.  Therefore, he should see only his own 
	# record.  And not in edit mode. 
	# But only if this remote user is somebody who is in the database. 

else {
  start_page("unknown Error mode. Doh!");
  end_page();
  }

exit;


sub please_to_fetching_scalar {
        # Take SQL string as input
        # send that sql string to db
        # Get output
        # throw away anything for first thousand answers, 
        # only include last answer. 
  my ($sql) = shift;
  my (@whatchuwant) = @_;
  my ($answer);
    my $get_info = $dbh->prepare($sql);
  $get_info->execute();
  while (my $ans = $get_info->fetchrow_hashref) {
    for my $key (@whatchuwant) {
      $answer = $ans->{$key};
      }
    }
  $answer;
  }


sub show_sheet {
	# Shows the Training Affirmation Sheet for the student. 
	# This is just basically all of the items in the syllabus
	# and for each field, we'll find the latest signoff for 4
	# and write the instructor's name and signoff-date.
  my ($student)=shift; 
  printf (qq(<a href="?">Return to Main</a> ) . 
	qq(/ <a href="?student=$student&notes=on">Show Instruction Record</a>) . 
	qq(/ <a href="/STATS/?pilot=$student">Show Flight Log</a><br>)); 

  print qq(<table border = "1"><tr valign="top">\n);
  print qq(<tr bgcolor="#444444">
<td align="right"><font color ="#FFFFFF" size="+1">Lesson</font></td><td align="right"><font color ="#FFFFFF" size="+1">Phase&nbsp;&nbsp;</font></td><td align="right"><font color ="#FFFFFF" size="+1">PTS Area</font></td><td align="right"><font color ="#FFFFFF" size="+1">Instructor Sign-Off and Date</font></td><tr>\n);

  my (%max_signoff) = please_to_fetching_unordered(
	qq(select number, max(signoff_date) as signoff_date from student_syllabus3 where handle='$student' and mode='4' group by number order by number),
		'number', 'signoff_date');
	# Now we have all of the signoffs and dates from instructors where there is a score of 4, stored in %max_signoff. 
	# We need to go in and populate the instructor handle for each one of those fields. 
	# If I knew SQL better, I could do some sort of fancy schmancy join select inner outer join thing. 
	# But I'm not so smart, and do know how to brute force my way around this problem in perl. 
	#
  for my $number (keys %max_signoff) {
    $max_signoff{$number}{'instructor'} = please_to_fetching_scalar(
	sprintf(qq(select instructor from student_syllabus3 where handle='%s' and number = '%s' and signoff_date = '%s' limit 1),
		$student, 
		$max_signoff{$number}{'number'},
		$max_signoff{$number}{'signoff_date'}
		), 'instructor'
	);
    }
  my (%syllabus) = gimme_syllabus();	# All the info about the syllabus in general
  for my $number (sort keys %syllabus) { 
		# Go through each line of the syllabus, 
		# and fetch from the database the last instructor to sign off this number with a 4. 
    next if ($syllabus{$number}{'pts_aoa'} eq '' && $number !~ /^\d$/);
    if ($number	=~ /^\d$/) {
	printf (qq(<td bgcolor="#888888" align="right"><font size="+1" color="#FFFFFF">%s</font>&nbsp;</td>\n) . 
		qq(<td bgcolor="#888888" align="right"><font size="+1" color="#FFFFFF">%s</font>&nbsp;</td>\n) .
		qq(<td bgcolor="#888888" align="right"><font size="+1" color="#FFFFFF"></font>&nbsp;</td>\n) .
		qq(<td bgcolor="#888888" align="right"><font size="+1" color="#FFFFFF"></font>&nbsp;</td>\n),
		$syllabus{$number}{'number'},
		$syllabus{$number}{'title'},
		);
      }
    else {
      print qq(<tr>\n); 
      print qq(<td bgcolor="#D8D8D8" align="right"><font size="+0" color="#000000">$number</font>&nbsp;</td>\n);
      printf (qq(<td bgcolor="#FFFFFF" align="right"><a href="https://members.skylinesoaring.org/TRAINING/Syllabus/%s.shtml">%s</a>&nbsp;</td>\n),
	$syllabus{$number}{'number'},
	$syllabus{$number}{'title'}
	);
      printf (qq(<td bgcolor="#D8D8D8" align="right"><font size="-1" color="#000000">%s&nbsp;</font></td>\n),
	$syllabus{$number}{'pts_aoa'}
	);
      if ($max_signoff{$number}{'signoff_date'} ne '') {
        printf (qq(<td bgcolor="#FFFFFF" align="right"><font size="-1" color="#000000">%s&nbsp;%s&nbsp;</font></td>\n), 
		$handle_to_name{$max_signoff{$number}{'instructor'}},
		$max_signoff{$number}{'signoff_date'},
		);
        }
      else {
        print qq(<td bgcolor="#E8E800" align="right">&nbsp;</td>\n); 
        }
      }

    print qq(</tr>\n);
    }

  
  print qq(</table><br>\n); 
  end_page();
  } 



sub show_progress_chart {
	# input is the student handle. 
	# Go find his flights, make 0 to 100 the x axis. 
	# Go find his student progress reports, relative to 
	# the required outcome for solo. 
	# Draw a table, columns are green for %age toward solo
	# Each column is a hyperlink to an instruction event. (to the html anchor)
	# Each column has a js tooltip with the basic info about the instruction event
	# Each time student flew with a new instructor, drop in an arrow icon. 
	# When student solos, make the column stand out with blueness
	# If the student has instruction over multiple years, show that.

  my ($student) = shift; 
  my ($director) = shift;
  my (@instruction_dates, %flight_dual, $first_solo, %first_flight_with, @instructors);
  my (%data_structure);	# This is the assoc.array that has all the info
	# 1st, collect all of the unique dates where we have something for this student
	# Anything in the student_syllabus3 table linked to $student.
	# Put that into an array named instruction_dates
  my @instruction_dates = (please_to_fetching_single(
		sprintf (qq(select distinct signoff_date from student_syllabus3 where handle='%s' order by signoff_date),
			$student
			),
		'signoff_date'
		));
	# If $student doesn't have anything, then we really shouldn't continue with this data dive. 
  if (@instruction_dates) {
    }
  else {
    return "No data for student $student";
    }
	# Collect the date that dude did his first solo
  my @first_solo;
  @first_solo = please_to_fetching_single(qq(select min(flight_date) as flight_date from flight_info where pilot='$student' and instructor='' and passenger=''), 'flight_date');
  $first_solo=$first_solo[0];


	# Collect list of all instructors who flew with $student
  @instructors = please_to_fetching_single(
		sprintf (qq(select distinct instructor from student_syllabus3 where handle='%s'),
			$student
			),
		'instructor'
		);
  if (@instructors) {
    }
  else {
    return "No instructors flew with student $student.";
    }

	# Collect an assoc.array of all instructors' first flight with $student. 
  for my $inst (@instructors) {
    $first_flight_with{$inst}=please_to_fetching_single(
		sprintf (qq(select min(flight_date)from flight_info where pilot='%s' and instructor='%s'),
			$student,
			$inst
			),
		'flight_date'
		);
    $data_structure{$first_flight_with{$inst}}{'new_instructor'} = $inst;
    }
	# Collect information from the syllabus.  How many items need '3' to solo? 
  my %ans;

  %ans = please_to_fetching_unordered (qq(select flight_date, count(*) as count from flight_info where pilot='$student' and instructor !='' group by flight_date),
	'flight_date', 'count'
	);

	# OK, based off of all the dates that dude had flight instruction, we're now going 
	# to start filling information into that %data_structure assoc.array, with the 
	# flight date as the key of the assoc.array. 
 
  for my $dates (@instruction_dates) {
	# Places that have scores of 3 or 4 get thrown into the solo_completed field. 
    $data_structure{$dates}{'solo_complete'}=percent_complete_by_date('3', $student, $dates);
	# Scores of 4 per date get thrown into rating_complete. 
    $data_structure{$dates}{'rating_complete'}=percent_complete_by_date('4', $student, $dates);
	# Dude had so many flights on this date
    $data_structure{$dates}{'flights_onday'} = $ans{$dates}{'count'};
	# Sorry i have to throw this into a temporary array, and then extract just the first field, it seems
	# to be an ugly bug in the fetching_single method. Anyway, find out
	# how many flights dude did before and on  this date, throw it into flights_sofar, which we will
	# use later in the popup text. 
    my @ans2 = please_to_fetching_single (qq(select count(*) as count from flight_info where pilot='$student' and instructor !='' and flight_date <= '$dates'),
	'count'
	);
    $data_structure{$dates}{'flights_sofar'} = join ("", @ans2);
    }

	# OK, let's start making a table with all of this data, and see how it looks. 
	# We'll draw two tables, one for solo-complete, and one for rating complete. 
	# They're pretty much the same thing, but with small differences, so we'll just
	# do a for loop of the mode. 
  for my $mode ('solo_complete', 'rating_complete') {
	# The fadecolor is the color of the column, and it fades slightly to give contrast. 
	# Black fade for pre-solo training, green fade for PPL training, blue fade for days 
	# when dude did his first solo. 
    my ($previouscolor); 
    my ($fadecolor);
    if ($mode eq 'solo_complete') {
      $fadecolor='black';
	# If the mode is solo complete, then make the bars black, make the header text 
	# specific to pre-solo work. 
      if ($director) {
        print h2(qq($handle_to_name{$student}));
        flight_summary_box($student);
        print h3(qq(Solo Progress));
        $fadecolor='black';
        }
      }
	# If the mode is rating complete, then make the bars green, and use appropriate
	# header text
    elsif ($mode eq 'rating_complete') {
      $fadecolor='green';
      if ($director) {
        print h3(qq(Rating Progress));
        $fadecolor='green';
        }
      }
    $previouscolor=$fadecolor;
	# Print out an invisible table for this barchart to live in. 
	# I tried it with cell spacing 0 and you can't see the discrete
	# bars very easily, and can't discern how many flights dude is having 
	# per instructional session, so i kept the cellspacing at 1. 
	# It is smoother and prettier with cell spacing 0, but not as useful. 
    print qq(<table border="0" cellpadding="0" cellspacing="1" bgcolor="#FFFFFF">\n);
	# The table will be 200 pixels high. If you want it bigger, punch up the factor
	# to a bigger number. 
    my $factor=199;
	# One flight is 5 pixels wide. Two flights is 10 pixels wide.  X factor
	# is the multiplier for how many pixels each should be represented in the x axis.
    my $x_factor = 5; 
    print qq(<tr valign="top" height="200">);
    my (%year_span); 
	# How many columns have we printed so far? Start counting at -1.
	# We do this so we can make the years underneath the barcharts span the
	# number of flights that dude did in that year. 
    my $colcount=-1; 
    my $lastyear=0; 
	# OK, we populated %data_structure above by doing lots of SQL queries,
	# The key for %data_structure is the instruction date. We'll go thru the sorted
	# dates now, and make a column based on that information stored in that structure. 
	# Starting with the first instruction date, going all the way through till the end
	# for instruction time. 
	# Only flights with instructurs are included here. 
    for my $col (sort keys %data_structure) {
      my $x=sprintf("%d", (0+($x_factor * $data_structure{$col}{'flights_onday'}))); 
      next if $x == 0; 
      $colcount++; 
	# Extract the year from the date.  This way we figure out if the year changed or not
      my $year = $1 if ($col =~ /^(\d{4})-\d{2}-\d{2}$/);
      if ($lastyear == 0) { 
        $lastyear = $year; 
        $year_span{$year} = $colcount;
        }
	# If the year changed, we need to punch in a 2 pixel column that is grey, and 
	# remember how many columns wide this year was, so we can label the years 
	# under this batch of flights at the bottom of the graph. 
      if ($lastyear < $year) {
        $year_span{$lastyear} = $colcount;
        $colcount = 0 ; 
        $lastyear = $year; 
        print qq(<td valign="bottom" height="200"><img src="/icons/blobs/greyfade.png" width="2" height="$factor" valign="bottom"></td>);
        }
	# We made it through this column, so add id to the number of flights in this $year
      $year_span{$year}++;
	# Is the dude's date of his first solo the same as this column's date? 
      if ($first_solo eq $col ) {
	# If so, then remember what color the columns used to be. 
        $previouscolor=$fadecolor;
	# and make this column blue. 
        $fadecolor='blue';
        } 
	# Is the dude's date of his first passenger the same as this column's date? 
      else {
	# Otherwise, stop being blue, and go back to the old color that you used to be. 
        $fadecolor=$previouscolor;
        }
	# OK, now that we've gone through some of the preliminaries, time to actually make 
	# The image for the column.  Figure out how many pixels we need for height of the 
	# empty field. White Y is the height of the white, invisible column above the data. 
      my $white_y = sprintf("%d", (1+($factor - ( $data_structure{$col}{$mode}) * $factor)));  
	# Convert the fraction of percent complete into a number relative to 100%
      my $percent_complete=($data_structure{$col}{$mode} * 100); 
	# Put the number of flights dude has had so far and on this day into temporary variables. 
      my $flights_sofar = $data_structure{$col}{'flights_sofar'}; 
      my $flights_onday = $data_structure{$col}{'flights_onday'};
	# How many pixels high is the data column? Get that number, multiply it by the factor height
	# add zero to make sure that perl interprets it as an integer and not as a string. 
      my $y = sprintf("%d", (0+(( $data_structure{$col}{$mode}) * $factor)));  
	# Print the whitefade image. 
      print qq(<td valign="bottom" height="200"><img src="/icons/blobs/whitefade.png" width="$x" height="$white_y" cellpadding="0" valign="bottom"><br>);
	# print the green or black barchart. 
      print qq(<a href="#$col" border="0" cellpadding="0"><img src="/icons/blobs/${fadecolor}fade.png" width = "$x" height="$y" valign="bottom" cellpadding="0" ); 
	# Include the javascript mouseover event for the text that pops up. You can now 
	# see the details about what this column is about.  How much percentage completion, what date, and how many flights
	# so far. 
      print qq(onMouseover="Tip('$col<br>$percent_complete% complete<br>$flights_sofar flights');" onMouseout="UnTip('');"></a></td>);
      }
	# Close up your table row. 
    print qq(</tr>\n);
	# Start printing the years
    print qq(<tr>);
    for my $year (sort keys (%year_span)) {
      print qq(<td valign="bottom" bgcolor="#cccccc" colspan="$year_span{$year}" align="center" cellpadding="0">$year</td><td  cellpadding="0" valign="top" bgcolor="#888888"></td>);
      }
    print qq(</tr>\n);
    print "</table>\n";
    }
  print "<br>"; 
  }


sub check_for_existing_comments {
	# Do we already have a report from this instructor for this student on thi flight date?
  my($student) = shift;
  my($datefield)= shift;
  my($rightnow) = time;
  my (%comments) =  please_to_fetching_unordered(
    sprintf (qq(select handle, report, report_date, lastupdated from instructor_reports2 where handle='%s' and instructor='%s' and report_date='%s'), 
	$student,
	$the_instructor,
	$datefield
	), 
      'handle', 'report', 'report_date', 'lastupdated'	
    );
  if ($comments{$student}{'report_date'} eq param('datefield')  && $rightnow > ($comments{$student}{'lastupdated'} + (86400 * $max_days_ago))) {
     printf <<EOF, param('datefield'), $comments{$student}{'report_date'};
<table border=1 bgcolor="#F88888">
<tr><td>It appears there is already a record from you for this student on this date. (%s)(%s)<br>
You may not update a record that is older than $max_days_ago days old. 
</td></tr>
</table>
EOF
    end_page();
    }
  elsif ($rightnow < ($comments{$student}{'lastupdated'} + (86400 * $max_days_ago))) {
    my $comment_added = scalar localtime $comments{$student}{'lastupdated'};
    print <<EOF;
<table border=1 bgcolor="#F88888">
<tr><td>It appears there is already a record from you for this student on this date.<br>
You added this comment at $comment_added. <br>
You may update that record by continuing your report here.
This will not update any of the SPR grid items. 
</td></tr>
</table>
EOF
    param('updating_record', 'on');
    param('lastupdated', $comments{$student}{'lastupdated'});
    param('just_comment', $comments{$student}{'report'});
    }
  else {
    # No older report found, so we do nothing...
    }
  }

sub show_expired_status {
	# If dude man is expired, show a pink box at the top 
	# of the report indicating so.  This makes the instructor 
	# viewing the report aware, so he won't go flying with the
	# non dues paying member.  or whatever. 
  my ($person) = shift; 
  my $lastupdated = active_member($person); 
  if ($lastupdated > 0) {
    my $updated_on = scalar gmtime ($lastupdated);
    print qq(<table border="1" bgcolor="#FFE8E8"><tr><td><h2>Please Note</h2>
This person is not currently an active member of the club. <br>This person's record 
was last updated on $updated_on UTC. 
</td></tr></table><br>\n);
    }
  }

sub active_member {
	# Input: user handle
	# answer: 0 for "he's active"
	# lastupdated field in member table for "nope.  Not active. This persons record was last updated on $x"
  my ($input) = shift; 
  my ($answer); 
  my $row;
  my $sql = qq#(memberstatus != 'I' and memberstatus != 'N'#; 
  my $get_info = $dbh->prepare(
	qq(select lastupdated from members where handle = '$input' and (memberstatus = 'I' or memberstatus = 'N')));
  $get_info->execute();
  while ( my $row = $get_info->fetchrow_hashref ) {
    $answer=$row->{'lastupdated'};
    warn "printing $answer\n" if $DEBUG; 
    }
  warn "active member answer for $input is $answer\n" if $DEBUG; 
  $answer; 
  }

sub insertify_flight_instruction {
	# Take no input
	# Expect a few fields to be filled in and passed in. 
	# If they don't exist, return silently. 
	# Take these fields, and then throw them into the 
	# ground instruction table in the database, which looks like this: 

#skyline=> \d flight_info
#                                Table "public.flight_info"
#       Column       |          Type          |                  Modifiers
#--------------------+------------------------+---------------------------------------------
# flight_tracking_id | integer                | default nextval('flight_tracking_id'::text)
# flight_date        | date                   | not null
# pilot              | character varying      |
# passenger          | character varying      |
# glider             | character varying(20)  |
# instructor         | character varying(20)  |
# towpilot           | character varying(20)  | default 'Not Specified'::character varying
# flight_type        | character varying(20)  |
# takeoff_time       | time without time zone |
# landing_time       | time without time zone |
# flight_time        | time without time zone |
# release_altitude   | integer                |
# flight_cost        | money                  |
# tow_cost           | money                  |
# total_cost         | money                  |
#Indexes:
#    "flight_info_idx" btree (flight_date)

	# No output is expected from this sub, just silent insertion. 
  my ($fieldcount); 
  for my $field (qw(student datefield)) {
    (param($field) ne '' )&& $fieldcount++; 
    }
  if ($fieldcount == 2) {
    my ($sql) = sprintf (qq(insert into flight_info values(
			nextval('flight_tracking_id'::text), 
			'%s', -- flight_date
			'%s', -- pilot
			'', -- passenger
			'(pending)', -- glider
			'%s', -- instructor
			'(pending)', -- towpilot
			'(pending)', -- flight_type
			'00:00', -- takeoff_time
			'00:00', -- landing_time
			'00:00', -- flight_time
			'1', -- release_altitude
			'\$0.00', -- flight_cost
			'\$0.00', -- tow_cost
			'\$0.00' -- total_cost
			)),
	param('datefield'),
	param('student'),
	$the_instructor,
	); 
    please_to_inserting($sql);
    }
  else {
    warn "Somehow.... not all four fields are filled in for missing flight instruction" if $DEBUG;
    }
  }


sub insertify_just_comments {
	# Take no input
	# Just go straight to adding comments and qualifications to the student's record. 
  print start_form();
  enter_data_table('just_comment'); 
  add_qualifications(param('datefield'), param('student'));
  print submit (
	-name => 'final_submit',
	-label => 'Submit Report'
	);
  print hidden ('comments_added', 'on');
  print hidden ('updating_record');
  print hidden ('lastupdated');
  print hidden ('handle', param('student'));
  print hidden ('datefield');
  print end_form();
  }


sub insertify_ground_instruction {
	# Take no input
	# Expect a few fields to be filled in and passed in. 
	# If they don't exist, return silently. 
	# Take these fields, and then throw them into the 
	# ground instruction table in the database, which looks like this: 
#skyline=> \d ground_inst 
#                                Table "public.ground_inst"
#       Column       |         Type          |                  Modifiers                  
#--------------------+-----------------------+---------------------------------------------
# ground_tracking_id | integer               | default nextval('ground_tracking_id'::text)
# inst_date          | date                  | not null
# pilot              | character varying     | not null
# instructor         | character varying(20) | not null
# duration           | interval              | 
# location           | character varying     | default 'KFRR'::character varying
#
#skyline=> 
#

	# No output is expected from this sub, just silent insertion. 
  my ($fieldcount); 
  for my $field (qw(student datefield location duration)) {
    (param($field) ne '' )&& $fieldcount++; 
    }
  if ($fieldcount == 4) {
    my ($sql) = sprintf (qq(insert into ground_inst values(
			nextval('ground_tracking_id'::text), 
			'%s', '%s', '%s', '%s', '%s')),
	param('datefield'),
	param('student'),
	$the_instructor,
	param('duration'),
	param('location'),
	); 
    please_to_inserting($sql);
    }
  else {
    warn "Somehow.... not all four fields are filled in for ground instruction" if $DEBUG; 
    }
  }

sub comment_logger {
	# So you just want to add some comments, and maybe some qualifications?
	# OK, we can do it here...
  print p(qq(Use this page for when you just want to add some comments to the student's record,
without adding any completed items in their instruction syllabus tracking sheet. You can also
use this page to just add qualifications (or endorsements), without logging any ground instruction.\n));
  print qq(<table border=0><tr>\n);
  my (%handles)=fetch_members('active');
  my (@members) = sort by_lastname keys(%handles); 
  print popup_menu(
	-name => 'student',
	-values => [@members],
	-labels => \%handles
	);
  print "</td></tr>\n";
  print qq(<tr><td align="right">Enter date (YYYY-MM-DD):</td><td>);
  print textfield (
	-name => 'datefield',
	-default => today(),
	-size => 10
	);
  print "</td></tr>\n";
  print qq(<tr><td align="center" colspan="2">\n);
  print hidden ('adding_comment', 'on');
  print submit (
	-label => 'Proceed'
	);
  print end_form();
  }


sub flight_instruction_logger {
	# One page to print form information -- 
	# this is where the instructor selects the information 
	# necessary to get us to the next page, which allows
	# the instructor to log flight instruction -- instruction 
	# that is not associated with any flight operations. 
	# This happens when the DO is lazy and hasn't yet uploaded the 
	# day's operations yet. 
	# or he's lost the floppy disk, or his usb thumbdrive got eaten
	# by the dog or whatever.... 

  print p(qq(Use this page for when the Duty Officer hasn't yet uploaded the log for this day's 
operations.  Once you enter the information on this page, you will be taken to the grid for 
this student, and you will be able to fill in the scores about the flights and his performance. 
	));
  print qq(<table border =0><tr>); 
  print qq(<td align="right">Select the member</td><td>);
  my (%handles)=fetch_members('active');
  my (@members) = sort by_lastname keys(%handles); 
  print popup_menu(
	-name => 'student',
	-values => [@members],
	-labels => \%handles
	);
  print "</td></tr>\n";
  print qq(<tr><td align="right">Enter date (YYYY-MM-DD):</td><td>);
  print textfield (
	-name => 'datefield',
	-default => today(),
	-size => 10
	);
  print "</td></tr>\n";
  print qq(<tr><td align="center" colspan="2">\n);
  print hidden ('missing_flight_instruction', 'on');
  print submit (
	-label => 'Proceed'
	);
  print end_form();
  }


sub instruction_logger {
	# One page to print form information -- 
	# this is where the instructor selects the information 
	# necessary to get us to the next page, which allows
	# the instructor to log ground instruction -- instruction 
	# that is not associated with any flight operations. 
  print qq(<table border ="1"><tr>); 
  print qq(<td align="right">Select the member</td><td>);
  #my (%handles)=fetch_members();
  my (%handles)=fetch_members('active');
  my (@members) = sort by_lastname keys(%handles); 
  print popup_menu(
	-name => 'student',
	-values => [@members],
	-labels => \%handles
	);
  print "</td></tr>\n";
  print qq(<tr><td align="right">Enter date (YYYY-MM-DD):</td><td>);
  print textfield (
	-name => 'datefield',
	-default => today(),
	-size => 10
	);
  print "</td></tr>\n";
  print qq(<tr><td align="right">Duration: (HH:MM)</td><td>), 
	textfield (
	-name => 'duration',
	-default => '01:00',
	-size => 5,
	);
  print "</td></tr>\n";
  print qq(<tr><td align="right">Location: </td><td>), 
	textfield (
	-name => 'location',
	-default => 'Front Royal, VA',
	-size => 20
	);
  print "</td></tr>\n";
  print qq(<tr><td align="center" colspan="2">\n);
  print hidden ('ground_instruction', 'on');
  print submit (
	-label => 'Proceed'
	);
  print end_form();
  }


sub handjam_comments {
	# So you've decided to go the route of just submitting comments, 
	# instead of writing up an instruction report, or a ground_isntruction report. 
	# This will just take the comments and put them into the student's record. 
	# Also, if any qualifications have been tacked on, they'll be added, too. 
	#
  verbose_output() if $DEBUG; 
  if (param('updating_record') eq 'on' && param('just_comment')) {
  #if (param('updating_record') eq 'on' && param('just_comment') && param('lastupdated') + (86400*$max_days_ago) < 30) {
    warn "Attempting to update, rather than insert..." if $DEBUG;
    my ($sql) = sprintf (qq(update instructor_reports2 set 
		lastupdated='%s',
		report='%s'
		where
		handle='%s' and
		report_date='%s' and
		instructor='%s' and
		lastupdated='%s'),
	time, 
	escape(param('just_comment')), 
	param('handle'),
	param('datefield'),
	$the_instructor,
	param('lastupdated')
	);
    print "Attempting to submit this here sql; ($sql)\n" if $DEBUG; 
    if (please_to_inserting($sql)) { 
      print p("Existing instructor report essay updated with new remarks.\n"); 
      }
    }
  elsif (param('just_comment')) {
    my ($sql) = sprintf (qq(insert into instructor_reports2 values (
		'%s',	-- handle 
		'%s',	-- report_date
		'%s',	-- instructor
		'%s',	-- lastupdated
		'%s'	-- Report text 
		)),
	param('handle'),
	param('datefield'),
	$the_instructor,
	time, 
	escape(param('just_comment')), 
	1
	);
    print "Attempting to submit this here sql; ($sql)\n" if $DEBUG; 
    if (please_to_inserting($sql)) { 
      print p("Instructor report essay updated with remark.\n"); 
      }
    }
  else {
    print "No comments were added.<br>\n";
    }

	# OK, now we're going to look at the qualifactions that may
	# or may not have been checked off on the only-comments page. 
	# If any new qualifications are listed, then we'll insert into 
	# the database any qualifications that got added. 

  my ($qual_notes)='';
  my (%quals) =  please_to_fetching_unordered(
    qq(select name, img_url, description, is_qual from endorsement_roles),
      'name', 'img_url', 'description', 'is_qual'	
    );
 
  for my $qual (param('quals')) {
    print "Adding $qual to Qualifications...<br>\n" if $DEBUG;
    next unless (exists ($quals{$qual})); 	# If somehow somebody tries to insert a qualification
						# that isn't in the endorsement_roles table, then 
						# this endorsement is skipped. 
    print "The qual of $qual appears to be legit...<br>\n" if $DEBUG; 
    my ($sql) = sprintf (qq(insert into quals values (
		'%s', 	-- handle
		'%s',	-- qualification
		TRUE,	-- is_qualified boolean
		FALSE, 	-- expires boolean
		NULL, 	-- Expiration Date
		'%s',	-- instructor handle
		'%s' 	-- Any notes
		)),
	param('handle'),
	$qual, 
	$the_instructor, 
	$qual_notes
	);
    print "Attempting to insert this SQL: <pre>$sql</pre><br>\n" if $DEBUG;
    please_to_inserting($sql); 
    }
  print "Handjam section complete" if $DEBUG;
  }

sub submit_final_report {
	# Go through everything in param
	# pick out the text inserted for each flight_grouping
	# Pick out the lesson numbers for each flight_grouping
	# Group out the flights. 
	# perform inserts into sql with the data. 
	# Check that it has inserted
	# Give the instructor the list of other flights pending his remarks. 
  my(%lesson_outcome, %flight_tracking_id, %lesson_fields, %text_for_lesson, @flights); 

  for my $field (param()) {
    if ($field eq 's-default-0' || param($field) eq '' || param($field) eq '0' ) { 
      # Don't do anything
      }
    elsif ($field =~ /^s-([^-]+)-(\d+)$/) {
      $flight_tracking_id{$2}++;
      $lesson_outcome{$2}{$1}=param($field);
	# OK, now we have all of the insertions in this associated array. 
	# each lesson outcome entry has two keys, the flight tracking ID, 
	# and teh second key is the lesson number.  
	# The right value is the number of the mode (0, not used, 1, demo, 2, performed, etc). 
      push(@{$lesson_fields{param($field)}{$2}}, $1); 
	# That weird duck right above, makes an array, sorted on the outcome. 
	# So we have a list of the lessons that are performed, proficient, etc. 
      }
    elsif ($field =~ /^(\d+)-text$/) {
      $text_for_lesson{$1}=param($field); 
      }
    }

  for my $flight_no (sort keys (%flight_tracking_id)) { 
    my ($count); 
    verbose_output() if $DEBUG; 
    my(%flight_info)=%{get_flight_info($flight_no)};
    if ($flight_info{'flight_date'} !~ /^\d{4}-\d{2}-\d{2}$/) {
		# Your date isn't a date, and that makes me sad. 
		# I bet what happened is that the flight_tracking_id 
		# disappeared from the database in mid-transaction. 
		# We'll just have to go find the new flight_tracking_id ($flight_no)
		# And run it through the database again. 
      my($new_flight_no);
      my $datefield=param('dd-'. $flight_no);	# Thankfully, we jammed the date for that old flight number into this param
      if ($datefield =~ /^\d{4}-\d{2}-\d{2}/) {
		# So long as what we've got in that hand jammed variable above looks like a date...
		# We should be able to query the database for flights with 
		# The student + the instructor + that flying day. 
		# Once we find the new flight_no, we'll assign it to $new_flight_no
		# and then see if that passes the new test. 
 
        my ($ans) =  please_to_fetching_single(
		sprintf (qq(select flight_tracking_id from flight_info where instructor='%s' and flight_date='%s' and pilot='%s' order by takeoff_time desc limit 1),
			$the_instructor,
			$datefield,
			param('handle')
			),
		'flight_tracking_id'
		);
        printf (qq(select flight_tracking_id from flight_info where instructor='%s' and flight_date='%s' and pilot='%s' order by takeoff_time desc limit 1),
                        $the_instructor,
                        $datefield,
                        param('handle')
                        ) if $DEBUG;
	print "I think the new flight number will be ->" . $ans . "<-" if $DEBUG; 
		# Now we'll have to go through all the hidden variables and change the old number to the new number. 
        if ($ans =~ /^\d+$/) {
	  for my $param (param){
            my $new_param=$param;
            if ($new_param =~ s/^s-(.+)-$flight_no$/s-$1-$ans/ || $new_param =~ s/^$flight_no-text/$ans-text|^dd-$flight_no/) {
              print "Changing $param to $new_param<br>\n" if $DEBUG; 
              my ($temp) = param($param); 
              param($new_param, $temp); 
              Delete($param); # Remove the old value, I don't want it mucking up my program. 
              }
            }
          }
		# I suppose You should just resubmit with the new values. 
        $flight_no=$ans;
        print h1("PLEASE TRY AGAIN"); 
        print h2("New Logsheet Uploaded"); 
        print p(qq(The logsheet has NOT been submitted));
	print p(qq(The system detected that somebody uploaded a new log sheet between the time you pulled up 
this instruction report to the time you submitted it. This might have changed some of the information about the 
flight in question.  I've updated the information about the flights you'll be reporting on.  Please review this 
information and continue with your instruction report. You may have to re-enter any qualifications gained during
this instruction session. ));
        Delete('quals');
        allow_for_instructor_comments('quiet');
        end_page();
        } 
      }
    for my $lesson_number (keys %{$lesson_outcome{$flight_no}}) {
      my ($sql)=sprintf (qq(insert into student_syllabus3 values ('%s', '%s', '%s', '%s', '%s')),
        param('handle'), 
	$lesson_number,
	$lesson_outcome{$flight_no}{$lesson_number}, 
	$flight_info{'instructor'}, 
	$flight_info{'flight_date'},
	);
      if (please_to_inserting($sql)) {
        $count++; 
        }
      }
    if ($count > 0) {
      print p(qq(Syllabus grid updated with $count entries));
      }
    my ($qual_notes)='';
    my (%quals) =  please_to_fetching_unordered(
      qq(select name, img_url, description, is_qual from endorsement_roles),
        'name', 'img_url', 'description', 'is_qual'	
      );
    for my $qual (param('quals')) {
      print "Adding $qual to Qualifications...<br>\n" if $DEBUG;
      next unless (exists ($quals{$qual})); 	# If somehow somebody tries to insert a qualification
						# that isn't in the endorsement_roles table, then 
						# this endorsement is skipped. 
      print "The qual of $qual appears to be legit...<br>\n" if $DEBUG; 
      my ($sql) = sprintf (qq(insert into quals values (
		'%s', 	-- handle
		'%s',	-- qualification
		TRUE,	-- is_qualified boolean
		FALSE, 	-- expires boolean
		NULL, 	-- Expiration Date
		'%s',	-- instructor handle
		'%s' 	-- Any notes
		)),
	param('handle'),
	$qual, 
	$the_instructor, 
	$qual_notes
	);
      print "Attempting to insert this SQL: <pre>$sql</pre><br>\n" if $DEBUG;
      please_to_inserting($sql); 
      }

    my ($sql)=sprintf (qq(insert into spr_audit values ('%s', '%s', '%s', '%s')), 
	param('handle'),
	$flight_info{'instructor'}, 
	$flight_info{'flight_date'}, 
	scalar (localtime(time))
	); 
    if (please_to_inserting($sql)) {
      print p(qq(Audit trail records inserted.));
      }
 
    if (param($flight_no . '-text')) {
      my ($sql) = sprintf (qq(insert into instructor_reports2 values (
		'%s',	-- handle 
		'%s',	-- report_date
		'%s',	-- instructor
		'%s',	-- lastupdated
		'%s'	-- Report text 
		)),
	param('handle'),
	$flight_info{'flight_date'},
	$flight_info{'instructor'}, 
	time, 
	escape(param($flight_no . '-text')), 
	1
	);
      if (please_to_inserting($sql)) { 
        print p("Instructor report essay updated with remark.\n"); 
        }
      }
    }
  }

sub please_to_inserting {
	# Please to taking input
	# and throwing into database wholesale. 
	# kthxbai. 
  my ($input) = shift; 
  my $sth = $dbh->prepare($input);
  my ($result) = $sth->execute(); 
  my ($errornum) = $sth->err;
  my ($error) = $sth->errstr;
  if ($result) {
    warn "Line inserted. ($input) Errnum: ($errornum), Error: ($error)\n" if $DEBUG;
    }

  elsif ($errornum == 7) {
    print p(qq(Duplicate: This report was already inserted by this instructor for this student on this date.)); 
    gunk_bomb($input,$errornum,$error);
    print pre($input); 
    } 
 
  else {
    gunk_bomb($input,$errornum,$error);
    }
  $result;
  }

sub gunk_bomb {
    my ($input) = shift; 
    my ($errornum) = shift; 
    my ($error) = shift; 
    open (GUNK, ">> /var/www/members/sql/sql-$$-gunk.sql");
    print GUNK "----------------------------\n";
    print GUNK `date`  . "\n";
    print GUNK "=======================\n";
    print GUNK $input;
    print GUNK "=======================\n";
    close (GUNK);
    open (GUNK2, ">> /var/www/members/sql/sql-$$-gunk2.sql");
    print GUNK2 "---------------------------\n";
    print GUNK2 `date` . "\n";
    print GUNK2 "=====================\n";
    select (GUNK2);
    verbose_output();
    select (STDOUT);
    print GUNK2 "=====================\n";
    close (GUNK2);
    abort(qq(Ka-blooey!
    Your report didn't go through. Error String was [$errornum][$error] Please e-mail the following gunk to Piet Barber:<br>
<pre>$input</pre>)); 
  }


sub verbose_output {
    print "<pre>";
    for my $line (param()) {
      printf ("%s => %s\n",
	 $line,
	 param($line)
	 );
      }
    print "</pre>";
 
  }

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

sub full_javascript {
	# If you are going to use a textarea (and elm1), then you need 
	# the full_javascript, which includes the mini javascript subroutine's output too.

  my $answer = mini_javascript();
  $answer.=<<EOM;
<!-- TinyMCE -->
<script src="/INCLUDES/tinymce/js/tinymce/tinymce.min.js"></script>
<script>
	tinymce.init({
		selector: "textarea",
			plugins: [
				"advlist autolink lists link image charmap print preview anchor",
				"searchreplace visualblocks code fullscreen",
				"insertdatetime media table contextmenu paste"
			],
		toolbar: "insertfile undo redo | styleselect | bold italic underline superscript subscript| alignleft aligncenter alignright alignjustify | bullist numlist outdent indent | link image",
		autosave_ask_before_unload: false,
		relative_urls : false,
        	convert_urls: false,
		});
</script>
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

sub allow_for_instructor_comments {
	# This is where the instructor hit "Submit Information" button
	# from the breakout for syllabus content items versus flights. 
	# and has a bunch of fields to show off.  
	# we will go through all of the submitted fields names
	# find flight tracking IDs associated with them, 
	# then cross check the flight_info database to make sure that 
	# this instructor had a flight with this student with this tracking ID number. 
	# Once all of those hurdles are cleared, 	
	# we will print a small logbook entry for the flights in question, and 
	# give the instructor an opportunity to add information through the 
	# old instructor reports page stapled on. 
	# We will give the instructor an opportunity to write a separate instruction 
	# report for each one of the flight groupings for this student. 

	# Wow, that seems like a tall order, but here we go! 
  my ($quiet) = shift; 
  start_page("Review Flight Results for " . $handle_to_name{param('handle')}, '', 1) unless $quiet;
  my ($handle, %flight_tracking_id, %lesson_outcome, 
	%lesson_fields, %output_names, %completed_for_solo, %completed_for_rating);
  $handle=param('handle'); 
  verbose_output() if $DEBUG;
  %output_names=lesson_fields();
  my ($flights_counts)=0; 

  for my $field (param()) {
    if ($field eq 's-default-0' || param($field) eq '' || param($field) eq '0' ) { 
      # Don't do anything
      }
    elsif ($field =~ /^s-([^-]+)-(\d+)$/) {
      $flight_tracking_id{$2}++;
      $lesson_outcome{$2}{$1}=param($field);
	# OK, now we have all of the insertions in this associated array. 
	# each lesson outcome entry has two keys, the flight tracking ID, 
	# and teh second key is the lesson number.  
	# The right value is the number of the mode (0, not used, 1, demo, 2, performed, etc). 
      push(@{$lesson_fields{param($field)}{$2}}, $1); 
	# That weird duck right above, makes an array, sorted on the outcome. 
	# So we have a list of the lessons that are performed, proficient, etc. 
      $flights_counts++; 
      }
    }
	# By now we should have something in the flight_tracking_id assoc.array. 
	# If not, we need to complain and send dude to the syllabus page again. 

  if ($flights_counts == 0) { 
    print "You need to select something on the syllabus sheet.  At least one meazley thing\n";
    show_current_syllabus($handle);
    end_page();
    }
  my (@outcome_labels); 

  @outcome_labels = (
	'Not Covered',
	'Demonstrated', 
	'Performed', 
	'Solo Proficient', 
	'Rating Proficient', 
	'Critical Issue'
	); 

  print full_javascript();
  print start_form();

	# First we go through a loop of all of the flight_tracking_Ids we found. 
  for my $flight_grouping (sort (keys %flight_tracking_id)) { 
	print "Flight Grouping $flight_grouping<br>\n" if $DEBUG; 
    print "<hr>"; 
    my %flight_information=%{get_flight_info($flight_grouping)}; 

	# So we found a new flight grouping (i.e. same day same instructor, same student)
	# And we group up all of the blobs that were checked for this day's flying
	# with this instructor.   This is called a Flight Evaluation. 
    printf h2("Instruction Evaluation for %s"), $flight_information{'flight_date'}; 
	# Mini logbook entry (needs location for 61.51 completeness)
	# This has the date, glider, release and duration. 
    
	# Ah,so we have flights within a flight grouping... sometimes. 
	# sometimes its only one flight, but sometimes more. 
	# the get_flights_from_id figures that out for you. 
    if ($flight_information{'ground_tracking_id'} > 0) {
      
      print qq(<table border="1">\n); 
      print qq(<tr bgcolor="#E0E088"><td colspan="3">Ground Instruction</td></tr>); 
      print qq(<tr bgcolor="#E0E088"><td>Date</td><td>Location</td><td>Duration</td>\n); 
      print "</tr>\n"; 
      print "<tr>\n"; 
      for my $logbook_line (qw(flight_date location duration)) { 
        printf (qq(<td>%s</td>), $flight_information{$logbook_line}); 
        }
      print "</tr>\n";  
      print qq(</table><br>\n); 
      }
    elsif ($flight_information{'flight_tracking_id'} > 0) { 
      print qq(<table border="1">\n); 
      print qq(<tr bgcolor="#aaaaaa"><td>Date</td><td>Glider</td><td>Release</td><td>Duration</td>\n); 
      print "</tr>\n"; 
      for my $flight (get_flights_from_id($flight_grouping)) { 
        my %flight_information2=%{get_flight_info($flight)}; 
        print "<tr>\n"; 
	  # We print out each of the appropriate fields for the flight(s)
        for my $logbook_line (qw(flight_date glider release_altitude flight_time)) { 
          printf (qq(<td>%s</td>), $flight_information2{$logbook_line}); 
          }
        print "</tr>\n";  
        } 
      print qq(</table><br>\n); 
      }


    print qq(<table border="1">\n); 

	# Keep a count of stuff that was accomplished on solo proficient
	# or rating proficient. For this first one, solo performance 
	# or rating proficient performance count toward solo. 

    for my $outcome (3,4) {
      my ($output_count)=0;
      for my $field (@{$lesson_fields{$outcome}{$flight_grouping}}) {
        $completed_for_solo{$field}++; 
        }
      }

	# To count toward ratings, you need to be a green blob (score=4)
    for my $outcome (4) {
      my ($output_count)=0;
      for my $field (@{$lesson_fields{$outcome}{$flight_grouping}}) {
        $completed_for_rating{$field}++; 
        }
      }
 

	# For all other outcomes, the lesson plans involved get put into their own little array here.  
    for my $outcome (1..5) {
      printf (qq(<tr><td bgcolor="#aaaaaa">%s</td><td>%s), 
	    $outcome_labels[$outcome], 
	    ); 
      my ($output_count)=0;
      my ($output_length) = $#{$lesson_fields{$outcome}{$flight_grouping}} ; 
      for my $field (@{$lesson_fields{$outcome}{$flight_grouping}}) {
        printf (qq(<a href="/TRAINING/Syllabus/%s.shtml" target="_syllabus" onmouseover="Tip('%s')" onmouseout="UnTip('')">%s</a>), 
		$field,
		$output_names{$field},
		$field
		);
	$output_count++;
        if ($output_count <= $output_length) { 
          print ", "; 
          }
        }
      if ($output_count == 0) {
        print qq(<i>None</i>); 
        }
      print qq(</td></tr>), 
      }
    my ($handle)=param('handle'); 

    if (! has_a_rating($handle)) {
      my %still_needs = needed_for_solo($handle,  $flight_information{'flight_date'}, \%completed_for_solo);  

      print qq(<tr><td bgcolor="#cccccc"><i>Needs&nbsp;<img src="/icons/blobs/blob3.png" align="absmiddle">&nbsp;or&nbsp;<img src="/icons/blobs/blob4.png" align="absmiddle">&nbsp;for&nbsp;Solo</i></td><td>);
      my ($output_count)=0;
      for my $field (sort keys (%still_needs)) {

        printf (qq(<a href="/TRAINING/Syllabus/%s.shtml" target="_syllabus" onmouseover="Tip('%s')" onmouseout="UnTip('')">%s</a>, ), 
		$field,
		$output_names{$field},
		$output_names{$field},
		);
	$output_count++;
        }
      if ($output_count == 0) {
        print qq(<i>None</i>); 
        }
      my %still_needs = needed_for_rating($handle,  $flight_information{'flight_date'}, \%completed_for_rating);  
      print qq(<tr><td bgcolor="#cccccc"><i>Needs <img src="/icons/blobs/blob4.png" align="absmiddle">&nbsp;for&nbsp;Rating</i></td><td>);
      my ($output_count)=0;
      for my $field (sort keys (%still_needs)) {
        printf (qq(<a href="/TRAINING/Syllabus/%s.shtml" target="_syllabus" onmouseover="Tip('%s')" onmouseout="UnTip('')">%s</a>, ), 
		$field,
		$output_names{$field},
		$output_names{$field},
		);
	$output_count++;
        }
      if ($output_count == 0) {
        print qq(<i>None</i>); 
        }
      print qq(</td></tr>), 
      }
    print qq(</table><br>\n); 
    #print_hidden_fields();
	# The following is commented out until we can figure out
	# why the whole return to grid concept doesn't work 

    #print hidden('student', (param('student'))); 
    #print submit (
	#-name => 'return_to_grid', 
	#-value => 'Return to Grid for Corrections', 
	#);
    print "<br>\n";
    enter_data_table($flight_grouping . "-text");
    add_qualifications($flight_information{'flight_date'}, param('handle'));
    }
  print_hidden_fields();
  print submit(
	-name=>'final_submit',
	-value=>'Submit Report',
	);
  print end_form();
  print "<br><br><br><br><br><br><br>\n";
  end_page();
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
	# It could also maybe be ground instruction.  If the tracking_id doesn't match the pilot's
	# name, maybe it's ground instruction. We'll do a hit on the DB to make sure 
	# that it's not ground instruction, too. 
  my $tracking_id = shift;
  my %answer;
  my ($success_count)=0;
  my ($it_was_ground);
  my ($sql)=sprintf (qq#
	select * from flight_info 
		where flight_tracking_id='%s' and 
		pilot='%s' 
	order by takeoff_time desc#, 
	$tracking_id,
	param('handle') || param('student')
	);
  print "SQL: $sql<br>\n"  if $DEBUG;
  my $get_info = $dbh->prepare($sql);
  $get_info->execute();
  while (my $ans = $get_info->fetchrow_hashref) {
    $success_count++;
    for my $field (qw(flight_date flight_tracking_id instructor 
	release_altitude days_ago glider pilot flight_time takeoff_time)) {
      $answer{$field}=$ans->{$field};
      }
    }
  if (!$success_count) { 
	# If nothing matched for this guy, so maybe it's ground instruction
    $sql=qq#
	select inst_date as flight_date, ground_tracking_id, location, duration, instructor, pilot 
		from ground_inst 
	where ground_tracking_id='$tracking_id'#;
    print "SQL: $sql<br>\n"  if $DEBUG;
    my $get_info = $dbh->prepare($sql);
    $get_info->execute();
    while (my $ans = $get_info->fetchrow_hashref) {
      $it_was_ground;
      for my $field (qw(flight_date ground_tracking_id instructor pilot location duration )) {
        $answer{$field}=$ans->{$field};
        }
      }
    }
  if ($it_was_ground) {
    $answer{'glider'}='Ground'; 
    $answer{'release_altitude'}='Ground'; 
    $answer{'flight_time'}='-'; 
    }

  \%answer; 
  }

sub pending_reports {
	# This just prints out a list of the flights that we have
	# from the instructor, that don't have associated flight reports. 
	# We only go back $max_days_ago (global) number of days ago. 

  my ($instructor) = shift; 
  my ($pending_count) = 0; 
  my ($sql) = qq(select flight_date, pilot from flight_info where instructor='$instructor' 
	and ((CURRENT_DATE at TIME ZONE 'EST')::date-flight_date::date) < $max_days_ago 
	and pilot not like '% %' and pilot != '$instructor'
	);
  my $get_info = $dbh->prepare($sql);
  $get_info->execute();
  my (%flights);
  while (my $ans = $get_info->fetchrow_hashref()) {
	# Now we have a list of all pilots and all fights that have flown with $instructor.
    $flights{$ans->{'pilot'}}{$ans->{'flight_date'}}++;
    }
  for my $pilot (keys %flights) { 
	# Now we go through our list of pilot/flights with instructor, 
	# and cut out any times where we find a corresponding match in the syllabus3 table. 
	# we will use the delete command to cull it from teh array.
	# I probably could do this with one sql statement, but I don't think I am smart enough.
	# If you see it as obvious, I won't be upset if you rewrite this subroutine. 
    for my $date (keys (%{$flights{$pilot}})) {  
      $get_info = $dbh->prepare (sprintf (qq#
	select distinct signoff_date, handle from student_syllabus3 where handle='%s' and instructor='%s' and signoff_date='%s' #,
	$pilot, 
	$instructor,
	$date, 
	));
      $get_info->execute();
      while (my $ans = $get_info->fetchrow_hashref()) {
	delete($flights{$ans->{'handle'}}{$ans->{'signoff_date'}}); 
        }
      }
    }
  my (%already_done); 
  for my $key (keys (%flights)) { 
    for my $date (keys (%{$flights{$key}})) {
      $pending_count++;
      }
    }
  if ($pending_count) {
    print h2("Welcome, $handle_to_name{$the_instructor}.<br>There are flights pending your remarks"); 
    print h3("(in the last $max_days_ago days)"); 
    print qq(<table border="1"> <tr>
<td bgcolor="#000000" align="center"><font color="#FFFFFF">Pilot</font></td>
<td bgcolor="#000000" align="center" colspan="2"><font color="#FFFFFF">Reports</font></td>\n 
<td bgcolor="#000000" align="center"><font color="#FFFFFF">Progress</font></td>
<td bgcolor="#000000" align="center"><font color="#FFFFFF">Date</font></td>\n
</tr>\n); 
    for my $pilot (sort by_lastname keys (%flights)) {
      for my $date (sort keys (%{$flights{$pilot}})) { 
        my ($user);
        if (is_user_introductory($pilot)) {
          $user = "<u><i>" . $handle_labels{$pilot} .  "</i></u>";
          }
        else {
          $user = $handle_labels{$pilot};
          }
        next if ($already_done{$pilot}); 
        $already_done{$pilot}++; 
        printf (qq(<tr>\n<td align="right">%s</td>
	<td><a href="?student=%s">Grid</a></td>
	<td><a href="?student=%s&notes=on">Record</a></td>
	<td>%s</td>
	<td>%s</td>\n</tr>
	),
		($user || $pilot), 
		$pilot, 
		$pilot,
		percent_complete($pilot),
		$date,
		); 
        } 
      }
    } 
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
  $answer=sprintf(qq(<table cellspacing="0" border="0" cellpadding="0"><tr><td><tt>S</tt></td><td height="10" width="%d" bgcolor="#44FF44" onmouseover="Tip('Solo: %d%% Complete')" onmouseout="UnTip('')" ></td>
	<td width="%d" bgcolor="#888888"></td></tr></table>),
	$done,
	$done,
	$yet
	);

  $answer;
  }


sub rating_percent_complete {
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
  my (%still_needed) = needed_for_rating($input, today()); 
  for (sort keys(%still_needed)) {
    $still_needed_count++;
    }
  my ($total_for_rating) = 1;  
  my $sql = qq(select count(*) as total from syllabus_contents where far_requirement!= '' and pts_aoa != '');
  my $get_info = $dbh->prepare($sql);
  $get_info->execute();
  while (my $ans = $get_info->fetchrow_hashref()) {
    $total_for_rating=$ans->{'total'};
    }

  my ($done)=sprintf("%d", (1-($still_needed_count/$total_for_rating))*100); 
  my ($yet)=sprintf("%d", ($still_needed_count/$total_for_rating)*100);
  $answer=sprintf(qq(<table cellspacing="0" border="0" cellpadding="0">\n<tr><td><tt>R</tt></td></td><td height="10" width="%d" bgcolor="#44FF44" onmouseover="Tip('Rating: %d%% Complete (%d/%d)')" onmouseout="UnTip('')" ></td>
	<td width="%d" bgcolor="#888888"></td></tr></table>),
	$done,
        $done,
	($total_for_rating-$still_needed_count),
	$total_for_rating,
	$yet
	);

  $answer;
  }



sub percent_complete_by_date {
	# Input: '3' or '4', Dude's name, date. 
	# Return: Number of things rating_quality or solo_quality, divided by the total number of things needed for rating or solo, formatted as a percent. 
  my ($level) = shift; 
  my ($student) = shift; 
  my ($date) = shift; 
  my ($answer, $still_needed_count);
  if ($level == 3) {
    my (%still_needed) = needed_for_solo($student, $date); 
    for my $key (sort keys(%still_needed)) {
      $still_needed_count++ if $still_needed{$key} > 0;
      }
    my ($total_for_solo) = please_to_fetching_single (qq(  
    	select count(*) as total from syllabus_contents where far_requirement != ''
	), 'total');
    if ($total_for_solo == 0) { $answer = 0 }
    else {
      $answer = (($total_for_solo - $still_needed_count)/ $total_for_solo);
      }
    }
  if ($level == 4) {
    my (%still_needed) = needed_for_rating($student, $date); 
    for my $key (sort keys(%still_needed)) {
      $still_needed_count++ if $still_needed{$key} > 0;
      }
    my ($total_for_rating) = please_to_fetching_single (qq(  
    	select count(*) as total from syllabus_contents where far_requirement != '' and pts_aoa != ''
	), 'total');
    if ($total_for_rating == 0) { $answer = 0 }
    else {
      $answer = (($total_for_rating - $still_needed_count)/ $total_for_rating);
      }
    }
  sprintf ("%6.4s", $answer);
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
	# Here we build up the %required array with things that need to be accomplished
  while (my $ans = $get_info->fetchrow_hashref()) {
    $required{$ans->{'number'}}++; 
    }
  my $sql = qq( select number, mode from student_syllabus3 where handle='$handle' and mode::integer = 4 and signoff_date <= '$date_of');
  my $get_info = $dbh->prepare($sql);
  $get_info->execute();
	# Now we go through that %required array and delete key-values that are completed at level 4
	# If we have nothing left, then the dude is ready for the practical test
	# If we haven't clobbered any values, then he has a long way to go
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
  my $sql = qq( select number, mode from student_syllabus3 where handle='$handle' and mode::integer != 5 and mode::integer >= 3 and signoff_date <= '$date_of');
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

sub show_student_pulldown {
  my ($input) = shift; 
  my ($status_append) = qq#((memberstatus = 'I' or memberstatus = 'N') and (rating = 'S' or rating = 'N/A');#;
  print start_form ( -method => 'post'); 
  my (%handles)=fetch_members('inactive');
  my (@members) = sort by_lastname keys(%handles); 
  print popup_menu(
	-name => 'student',
	-values => [@members],
	-labels => \%handles
	);
  print submit (
        -label => 'Show Grid'
        );
  print end_form;
  }

sub show_student_list {
	# Depending on the input, we should show active students
	# or Active Rated Pilots. 
  my ($input) = shift;
  my ($status_append);
  print mini_javascript();
  my ($people_count);
  if ($input eq 'active student') {
    $status_append = qq#(memberstatus != 'I' and memberstatus != 'N' and (rating = 'S' or rating = 'N/A'));#;
    }
  elsif ($input eq 'active rated') {
    $status_append = qq#(memberstatus != 'I' and memberstatus != 'N' and rating != 'N/A' and rating != 'S');#;
    }

  elsif ($input eq 'inactive student') {
    my $active_since=(time-(86400*14));
    $status_append = qq#((memberstatus = 'I' or memberstatus = 'N') and (rating = 'S' or rating = 'N/A') and lastupdated > $active_since);#;
    }

  elsif ($input eq 'inactive') {
    $status_append = qq#(memberstatus = 'I' or memberstatus = 'N');#;
    }

  print '<table border = "1" bgcolor = "#FFFFFF">' . "\n";
  my ($progress);
  $progress = qq(Progress) if ($input eq 'active student' || $input eq 'inactive student'); 
  print <<EOM;
<tr>
  <td bgcolor="#000000" align="right"><font color="#FFFFFF">Pilot</font></td>
  <td bgcolor="#000000" colspan="3" align="center"><font color="#FFFFFF">Reports</font></td>
  <td bgcolor="#000000" align="center"><font color="#FFFFFF">$progress</font></td>
  <td bgcolor="#000000"><font color="#FFFFFF">Last Flight</font></td>
</tr>
EOM
  my ($sql) = qq(select handle from members
	where $status_append);
  my $get_info = $dbh->prepare($sql);
  $get_info->execute();
  my (%answer, %last_date);
  while (my $ans = $get_info->fetchrow_hashref()) {
    $answer{$ans->{'handle'}}++; 
    }
  
  $get_info = $dbh->prepare (qq#
	select pilot as handle, max(flight_date) as latest from flight_info where instructor != '' group by pilot#);
  $get_info->execute();
  while (my $ans = $get_info->fetchrow_hashref()) {
    $last_date{$ans->{'handle'}} = $ans->{'latest'};
    }

  for my $key (sort by_lastname keys (%answer)) {
    my ($user); 
    if (is_user_introductory($key)) { 
      $user = "<u><i>" . $handle_labels{$key} .  "</i></u>"; 
      }
    else {
      $user = $handle_labels{$key}; 
      }
    my (@answers) = (
	$last_date{$key}
	);
    printf (qq(
<tr>
  <td align="right">%s</td>
  <td><a href="?student=%s">Grid</td>
  <td><a href="?areas=on\&student=%s">Areas</td>
  <td><a href="?student=%s&notes=on">Record</a></td>
  <td>%s%s</td>
  <td align="center">%s</td>
</tr>),
	$user,
	$key, 
	$key, 
	$key, 
	((($input eq 'active student') || $input eq 'inactive student') && percent_complete($key)),
	((($input eq 'active student') || $input eq 'inactive student') && rating_percent_complete($key)),
	($last_date{$key} || '<i>None</i> ')
	); 
    $people_count++;
    }
  print '</table>' . "\n";
  printf "Total of %s people<br>\n", ($people_count+0);
  }

sub fetch_count_list {
	# Given a column name, gimme the number of hits
	# for this $handle in this column. 
  my $handle = shift;
  my $mode = shift;
  my $get_info = $dbh->prepare(qq#
	select count(*) from student_syllabus3 where handle = '$handle' and mode::integer = '$mode' #);
  $get_info->execute();
  $get_info->fetchrow();
  }

sub fetch_flight_info {
	# Subroutine for fetching in the flights for a particular
	# pilot. 
	# Added changes to allow for ground_instruction reports to be included
	# in this big glob of an answer. 
	# input: handle and an arbitrary limit. 
	# limit is set to 200 if we don't have one on input. 
	# output: array of associated arrays, containing a list of 
	# flights, ordered by date.  entry in the array is a link to an associative
	# array that has information about each flight, suitable for populating the header
	# columns for each flight group.   Wow this is kinda ugly.  Maybe
	# you want to shy away your eyes till the next subroutine. 

	# I had to kludge these two tables together with perl, because i suck at 
	# doing clever union joins or outer selects, or knowing pretty much how
	# to do any of those fancy sql selects. 
	# so i brute forced my way out of this problem with perl, and now you, 
	# as code reader, have eyes that are bleeding. I told you to look away!
  my $handle = shift;
  my $limit = shift; 
  my @answer; 
  $limit ||= 200; 
  my ($count)=0;
	# Here is the code to bring in the ground instruction. 
  my ($sql_ground)=qq#
	select ground_tracking_id, 
		((CURRENT_DATE at TIME ZONE 'EST')::date-inst_date::date) as days_ago, 
		inst_date as flight_date, 
		instructor from ground_inst
	where pilot='$handle' and 
		instructor != '' and 
		instructor !='$handle' 
	order by flight_date desc 
	limit $limit #;
	# and the code to bring in the flight instruction. 
  my ($sql_fly)=qq#
	select flight_tracking_id, 
		((CURRENT_DATE at TIME ZONE 'EST')::date-flight_date::date) as days_ago, 
		glider, 
		flight_date, 
		round(release_altitude/100,1)::real as release_altitude, 
		instructor 
	from flight_info 
	where pilot='$handle' and 
		instructor != '' and 
		instructor !='$handle' 
	order by flight_date desc 
	limit $limit #;

	# Your big answer is going to get stuffed into %biganswer. 
  my %biganswer;
	# First, get the database to tell us about the flying instruction stuff.... 
  my $get_info = $dbh->prepare($sql_fly);
  $get_info->execute();
  while (my $ans = $get_info->fetchrow_hashref) {
    my (%answer); 
    for my $field (qw(flight_date flight_tracking_id ground_tracking_id 
	instructor release_altitude days_ago glider)) {
      $answer{$field}=$ans->{$field};
      }
    $biganswer{sprintf("%s:%9.9d", 
	$ans->{'flight_date'},
	$ans->{'flight_tracking_id'},
	)} = \%answer; 
    }
	# Next, get the ground instruction stuff, and continue to stuff it into %biganswer
	# Note that %biganswer's key is basically something like this:
	# flight_date:(flight_tracking_id|"g" + ground_tracking_id)
	# and will look like this: 
	#   2010-11-12:g00000009   <- Ground Instruction
	# or
	#   2010-11-12:000003151   <- Flight Instruction
	# Hopefully, that will sort nicely. 
	# the only time we will use this is in this subroutine, so this handy
	# sorting method won't survive outside of this subroutine. 
  my $get_info2 = $dbh->prepare($sql_ground);
  $get_info2->execute();
  while (my $ans = $get_info2->fetchrow_hashref) {
    my (%answer); 
    for my $field (qw(flight_date flight_tracking_id ground_tracking_id 
	instructor days_ago glider)) {
      $answer{$field}=$ans->{$field};
      }
    $answer{'release_altitude'}='-'; 
    $answer{'glider'}='-'; 
    $biganswer{sprintf("%s:%9.9d", 
	$ans->{'flight_date'},
	$ans->{'ground_tracking_id'}
	)} = \%answer; 
    }
  
  for my $key (sort keys (%biganswer)) { 
    push(@answer, \%{$biganswer{$key}}); 
    }
  @answer;
  }


sub is_user_introductory {
	# Is the user an introductory user? Boolean response in $answer; 
  my ($input) = shift; 
  my ($answer)=0; 
  my ($sql)=qq#
	select handle from members where memberstatus='E' and handle='$input'#;
  my $get_info = $dbh->prepare($sql);
  $get_info->execute();
  while (my $ans = $get_info->fetchrow_hashref) {
    $answer++; 
    }
  $answer; 
  } 

sub show_endorsements {
	# Show the current endorsements, then show the expired endorsements. 
	# The endorsements mean "something that would be in the logbook that 
	# the FAA might care about"  This differs from quals, which are 
	# club endorsements. 
  }

sub show_quals {
	# Show qualifications.  These might be qualificaitons that members
	# have earned through their tenure.  This is also the way that we are
	# going to check the status of this member attending the spring safety meeting. 
	
  my ($handle) = shift; 
  my (%quals) =  please_to_fetching_unordered(
    qq(select name, img_url, description, is_qual from endorsement_roles),
      'name', 'img_url', 'description', 'is_qual'	
    );
  my (%dude_qual) = please_to_fetching_unordered(
    sprintf (qq(select role_name, is_qualified, expires, expiration_date, instructor, notes from quals where handle='%s' and is_qualified=TRUE), $handle), 
	'role_name', 'is_qualified', 'expires', 'expiration_date', 'instructor', 'notes'
	);

  for my $is_qualified (sort %dude_qual) {
    next if user_has_rating($handle) && $quals{$is_qualified}{'description'} =~ /Student/i;
    next if $quals{$is_qualified}{'img_url'} eq '';
    printf (qq(<img src="/INCLUDES/Qual-Icons/%s" alt="%s" width="50" height="50" onmouseover="Tip('%s')" onmouseout="UnTip('')">\n),
	$quals{$is_qualified}{'img_url'},
	$quals{$is_qualified}{'description'},
	$quals{$is_qualified}{'description'},
	);
      }
  }

sub show_badges_earned {
  my ($handle) = shift;
  my ($badge_count);
  my (%badges) = (
        'A' => '/images/A-Badge.png',
        'B' => '/images/B-Badge.png',
        'C' => '/images/C-Badge.png',
        'Bronze Badge' => '/images/Bronze%20Badge.png',
        'Silver Badge' => '/images/Silver%20Badge.png',
        'Gold Badge' => '/images/Gold%20Badge.png',
        'Diamond Badge' => '/images/Diamond%20Badge.png',
        );
  my (@badge_order) = (
        'A',
        'B',
        'C',
        'Bronze Badge',
        'Silver Badge',
        'Silver Distance',
        'Silver Duration',
        'Gold Altitude',
        'Gold Badge',
        'Silver Altitude',
        'Diamond Altitude',
        'Diamond Badge',
        'Diamond Distance',
        'Diamond Goal',
        );

  print qq(<h2>Badges Earned:</h2>\n);
  print qq(<table border="0" bgcolor="#F8F8F8">);
  my (%badges_earned)= please_to_fetching_unordered(
    sprintf (qq(select badge, earned_date from badges_earned where handle='%s'), $handle),
        'badge', 'earned_date'
        );

      for my $badge (@badge_order) {
        $badge_count++;
        if ($badges_earned{'Silver Badge'}{'badge'}) {
          delete ($badges_earned{'Silver Distance'}{'badge'});
          delete ($badges_earned{'Silver Altitude'}{'badge'});
          delete ($badges_earned{'Silver Duration'}{'badge'});
          }

        if ($badges_earned{'Gold Badge'}{'badge'}) {
          delete ($badges_earned{'Gold Distance'}{'badge'});
          delete ($badges_earned{'Gold Altitude'}{'badge'});
          delete ($badges_earned{'Gold Distance'}{'badge'});
          }

        if ($badges_earned{'Diamond Badge'}{'badge'}) {
          delete ($badges_earned{'Diamond Distance'}{'badge'});
          delete ($badges_earned{'Diamond Altitude'}{'badge'});
          delete ($badges_earned{'Diamond Goal'}{'badge'});
          }


        if ($badges{$badges_earned{$badge}{'badge'}}) {
          printf (qq(<td align="center" valign="top"><img src="%s" alt="%s" width="50"><br>%s<br><font size="-1">%s</font>\n),
                $badges{$badges_earned{$badge}{'badge'}},
                $badges_earned{$badge}{'badge'},
                $badges_earned{$badge}{'badge'},
                $badges_earned{$badge}{'earned_date'}
                );
          }
        elsif ($badges_earned{$badge}{'badge'}) {
          printf (qq(<td>%s<br>%s\n</td>\n),
                $badges_earned{$badge}{'badge'},
                $badges_earned{$badge}{'earned_date'}
                );
          }
      }
    #print qq(</table>\n);

  if ($badge_count < 1) {
    print "<td><i>None</i></td></tr>\n";
    }
  print qq(</table>\n);
  }


sub flight_summary_box {
	# A little table that shows the sums of all the gliders $student
	# has flown at this flying club. 
	# Also has the last date that each glider was flown. 
	# Not as pretty as I'd like, but the output format is nice!
  my ($student) = shift; 
  my (%flight_totals, %flight_dual, %flight_solo, %inst_given, @solo_totals, @dual_totals, @inst_totals, @total_totals, @gliders); 
  my $sql=qq#select distinct glider from flight_info where pilot='$student' or instructor='$student' order by glider#; 
  my $get_info=$dbh->prepare($sql); 
  $get_info->execute(); 
  while (my $ans = $get_info->fetchrow_hashref()) {
    push (@gliders, $ans->{'glider'} ) 
    }
  %flight_totals = please_to_fetching_unordered(sprintf (
		qq#select glider, count(*) as count, sum(flight_time) as flight_time, max(flight_date) as last_date from flight_info where pilot='%s' or instructor='%s' group by glider #, 
		$student, $student),
        'glider', 'count', 'flight_time', 'last_date'
        );

  %flight_solo = please_to_fetching_unordered(sprintf (
		qq#select glider, count(*) as count, sum(flight_time) as flight_time, max(flight_date) as last_date from flight_info where pilot='%s' and instructor='' and passenger='' group by glider#, 
		$student),
        'glider', 'count', 'flight_time', 'last_date'
        );

  %flight_dual = please_to_fetching_unordered(sprintf (
		qq#select glider, count(*) as count, sum(flight_time) as flight_time, max(flight_date) as last_date from flight_info where pilot='%s' and instructor!='' group by glider#, 
		$student),
        'glider', 'count', 'flight_time', 'last_date'
        );

  %inst_given = please_to_fetching_unordered(sprintf (
		qq#select glider, count(*) as count, sum(flight_time) as flight_time, max(flight_date) as last_date from flight_info where instructor='%s' group by glider#, 
		$student), 
        'glider', 'count', 'flight_time', 'last_date'
        );
  @solo_totals = please_to_fetching_single(sprintf (
		qq#select count(*) as count, sum(flight_time) as flight_time, max(flight_date) as last_date from flight_info where (pilot='%s' and instructor='' and passenger='')#, 
		$student, $student), 
	'count', 'flight_time', 'last_date'
	);
  @dual_totals = please_to_fetching_single(sprintf (
		qq#select count(*) as count, sum(flight_time) as flight_time, max(flight_date) as last_date from flight_info where (pilot='%s' and instructor!='')#, 
		$student, $student), 
	'count', 'flight_time', 'last_date'
	);
  @inst_totals = please_to_fetching_single(sprintf (
		qq#select count(*) as count, sum(flight_time) as flight_time, max(flight_date) as last_date from flight_info where (instructor='%s')#, 
		$student), 
	'count', 'flight_time', 'last_date'
	);
  @total_totals = please_to_fetching_single(sprintf (
		qq#select count(*) as count, sum(flight_time) as flight_time, max(flight_date) as last_date from flight_info where (pilot='%s' or instructor='%s')#, 
		$student, $student), 
	'count', 'flight_time', 'last_date'
	);
 


  print qq(<b>Note:</b> The following summary only includes flights since 1 Jan 2005.<br>\n);
  if (length(@gliders) > 0) { # Check to see if dude has any flights at all
    printf qq(<table border="1" cellpadding="2" cellspacing="2" bgcolor="#F8F8F8"><tr bgcolor="#000000"><td align="center" rowspan="2" bgcolor="#000000"><font color="#FFFFFF">Glider</font></td>\n);

    print qq(<td colspan="3" align="center"><font color="#FFFFFF">Solo Flights</font> </td>);
    print qq(<td colspan="3" align="center"><font color="#FFFFFF">With Instructor</font> </td>); 
    printf qq(<td colspan="3" align="center"><font color="#FFFFFF">Instruction Given</font></td>) if (scalar (%inst_given) ne '0' && is_user_instructor($student)); 
    printf qq(<td colspan="3" align="center"><font color="#FFFFFF">Total Flights</font></td>); 
    printf qq(</tr>\n);
    printf qq(<tr bgcolor="#000000">);
    print qq(<td align="right"><font color="#FFFFFF">#</font></td><td align="right"><font color="#FFFFFF">Time</font></td><td align="right"><font color="#FFFFFF">Last Flight</font></td>);
    print qq(<td align="right"><font color="#FFFFFF">#</font></td><td align="right"><font color="#FFFFFF">Time</font></td><td align="right"><font color="#FFFFFF">Last Flight</font></td>);
    print qq(<td align="right"><font color="#FFFFFF">#</font></td><td align="right"><font color="#FFFFFF">Time</font></td><td align="right"><font color="#FFFFFF">Last Flight</font></td>) if (scalar (%inst_given) ne '0' && is_user_instructor($student));
    print qq(<td align="right"><font color="#FFFFFF">#</font></td><td align="right"><font color="#FFFFFF">Time</font></td><td align="right"><font color="#FFFFFF">Last Flight</font></td>);
    print "</tr>\n";
    
    for my $glider (sort @gliders) {
      printf qq(<tr><td align="right">%s</td>\n), 
	$flight_totals{$glider}->{'glider'} 
		if (exists ($flight_solo{$glider}->{'count'}) || exists($flight_dual{$glider}->{'count'}) || exists($inst_given{$glider}->{'count'}) || exists($flight_totals{$glider}->{'count'}));
      printf qq(<td align="right">%s</td><td align="right">%s</td><td>%s</td>), 
	$flight_solo{$glider}->{'count'}, 
	time_snip($flight_solo{$glider}->{'flight_time'}),
	$flight_solo{$glider}->{'last_date'};
      printf qq(<td align="right">%s</td><td align="right">%s</td><td>%s</td>), 
	$flight_dual{$glider}->{'count'}, 
	time_snip($flight_dual{$glider}->{'flight_time'}),
	$flight_dual{$glider}->{'last_date'};
       printf qq(<td align="right">%s</td><td align="right">%s</td><td>%s</td>), 
	$inst_given{$glider}->{'count'}, 
	time_snip($inst_given{$glider}->{'flight_time'}),
	$inst_given{$glider}->{'last_date'}
		if exists($flight_totals{$glider}->{'count'}) && is_user_instructor($student); 
        printf qq(<td align="right">%s</td><td align="right">%s</td><td>%s</td>), 
	$flight_totals{$glider}->{'count'}, 
	time_snip($flight_totals{$glider}->{'flight_time'}),
	$flight_totals{$glider}->{'last_date'};
 
      print "</tr>\n";
      }
    print qq(<tr bgcolor="#E8E8E8" align="right"><td>Totals:</td>\n);
    printf qq(<td>%s</td><td>%s</td><td>%s</td>),
	$solo_totals[0], time_snip($solo_totals[1]), $solo_totals[2];
    printf qq(<td>%s</td><td>%s</td><td>%s</td>),
	$dual_totals[0], time_snip($dual_totals[1]), $dual_totals[2];
    printf qq(<td>%s</td><td>%s</td><td>%s</td>),
	$inst_totals[0], time_snip($inst_totals[1]), $inst_totals[2] if is_user_instructor($student); 
    printf qq(<td>%s</td><td>%s</td><td>%s</td>),
	$total_totals[0], time_snip($total_totals[1]), $total_totals[2];

    print "</table>\n"; 
    }
  else {
    print qq(<i>No flight training at Skyline is on record.</i><br>);
    }

  }


sub please_to_fetching_single {
        # Take SQL string as input
        # send that sql string to db
        # Get output
        # throw output into @answer array, which was @_ minus the SQL
        # This pretty much presumes there's only one row returned from the DB,
        # otherwise your array is going to be super long.
  my ($sql) = shift;
  my (@whatchuwant) = @_;
  my (@answer);
  my $get_info = $dbh->prepare($sql);
  $get_info->execute();
  while (my $ans = $get_info->fetchrow_hashref) {
    for my $key (@whatchuwant) {
      push (@answer, $ans->{$key});
      }
    }
  @answer;
  }


sub please_to_fetching_unordered {
        # Take string as input
        # Take array of the labels you want 
        # send that sql string to db 
        # Get output 
        # throw output into %answer array with @whatchuwant as keys, in order
        # don't be cute, just be easy and simple. 
  my ($sql) = shift;
  my (@whatchuwant) = @_;
  my ($key_on) = $whatchuwant[0];
  my (%answer);
  my $get_info = $dbh->prepare($sql);
  $get_info->execute();
  while (my $ans = $get_info->fetchrow_hashref) {
    for my $key (@whatchuwant) {
      $answer{$ans->{$key_on}}{$key} = $ans->{$key};
      }
    }
  %answer;
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
  print qq(<a href="?">Return to Main</a> / ); 
  show_navigation($student);
  show_badges_earned($student); 
  print h2("Club Qualifications Earned:");
  show_quals($student); 

  if (! has_a_rating($student)) { 
    print qq(<ul><table border="0" bgcolor="#F8F8FF"><tr><td>\n); 
    print qq(According to our records, $handle_to_name{$student} does not have a glider rating. If this is not correct, please notify the Member Meister and the Chief Flight Instructor of any necessary corrections by sending an email to <a href="mailto:membermeister\@skylinesoaring.org">membermeister\@skylinesoaring.org</a> . Flights and instruction not done at Skyline Soaring Club will not be included in this Training Report.<br></td></table></ul>
	) ; 
    print h2("Current Status in the Training Program:");
    }

  else { 
    print h2("Flying Summary:");
    }
  
  flight_summary_box($student);
  print "<br>\n"; 
  
  show_progress_chart($student);

  if (! has_a_rating($student)) {
    print qq(<table border="1">\n); 
    print dude_still_needs($student, today());
    print "</table>\n"; 
    }


  for my $date (reverse sort keys (%answer)) {
    print qq(<a name="$date"></a>); 
    print h3("Flights / Instruction on $date"); 
    print "<ul>\n"; 
    print show_verbose_report($date, $student); 
    print "</ul>\n"; 
    } 
  }

sub show_navigation {
  my $student=shift;
  print qq(<a href="?student=$student&notes=on">Show Instruction Record</a> / <a href="/STATS/?pilot=$student" target="_logbook">Show Flight Log</a> / <a href="?student=$student">Show Instruction Grid</a>\n);
  }


sub time_snip {
        # Take an ugly HHH:MM:00 and convert it to
        # a beautiful HHH:MM.
  my ($input) = shift;
  my ($answer);
  $answer =$input;
  $answer =~ s/^(\d+:\d+):00$/$1/;
  $answer;
  }

sub today {
        # What is today?
	# Used a few times in this program. 
  my @today = localtime (time - 14400); 
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
  my (@flights, @grounds, $flight_count, %report_text);
  my ($sql)=qq#
	select flight_tracking_id from flight_info where pilot='$student' and instructor != '' and flight_date='$date' order by takeoff_time#;
  my $get_info = $dbh->prepare($sql);
  $get_info->execute();
  while (my $ans = $get_info->fetchrow_hashref) {
    push (@flights, $ans->{'flight_tracking_id'}); 
    }
  if (@flights) { 
    $answer .= qq(<table border="1" bgcolor="#FFFFFF">
	<tr bgcolor="#CCCCE0"><td colspan="4"><b>Flight Instruction</b></td></tr>
	<tr bgcolor="#CCCCE0"><td>Glider</td><td>Release</td><td>Flight Time</td><td>Instructor</td></tr>);
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

  $sql=qq#
	select ground_tracking_id as flight_tracking_id from ground_inst where pilot='$student' and instructor != '' and inst_date='$date'#;
  my $get_info = $dbh->prepare($sql);
  $get_info->execute();
  while (my $ans = $get_info->fetchrow_hashref) {
    push (@grounds, $ans->{'flight_tracking_id'}); 
    }
  if (@grounds) { 
    $answer .= qq(<table border="1" bgcolor="#FFFFFF">
	<tr bgcolor="#E0E088"><td colspan="3"><b>Ground Instruction</b></td></tr>
	<tr bgcolor="#E0E088"><td>Location</td><td>Duration</td><td>Instructor</td></tr>);
    for my $flight_id (@grounds) {
      my (%ground_information)=%{get_flight_info($flight_id)}; 
      $answer .= sprintf (qq(<tr><td>%s</td><td>%s</td><td>%s</td></tr>),
	$ground_information{'location'}, 
	$ground_information{'duration'}, 
	$handle_to_name{$ground_information{'instructor'}} 
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
	select distinct number, mode from student_syllabus3 where handle='$student' and signoff_date='$date'#;
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
  $answer .= sprintf qq(<tr><td bgcolor="#cccccc"><i>Progress Towards Solo:</i></td><td>%s</td></tr>\n), percent_complete($student); 
  $answer .= sprintf qq(<tr><td bgcolor="#cccccc"><i>Progress Towards Rating:</i></td><td>%s</td></tr>\n), rating_percent_complete($student); 

  $answer .= qq(<tr><td bgcolor="#cccccc"><i>Needs&nbsp;<img src="/icons/blobs/blob3.png" align="absmiddle">&nbsp;or&nbsp;<img src="/icons/blobs/blob4.png" align="absmiddle">&nbsp;for&nbsp;Solo</i></td><td>);
  my ($output_count)=0;

  for my $field (sort keys (%still_needs)) {
    my ($the_field);
    #if (scalar(keys(%still_needs)) > 15) { 
	#$the_field=$field;
	#}
    #else {
    $the_field = $output_names{$field}; 
	#}
    $answer .= sprintf (qq(<a href="/TRAINING/Syllabus/%s.shtml" target="_syllabus" onmouseover="Tip('%s')" onmouseout="UnTip('')">%s</a>, ), 
		$field,
		$output_names{$field},
		$the_field
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
    my ($the_field);
    if (scalar(keys(%still_needs)) > 15) { 
	$the_field=$field;
	}
    else {
    	$the_field = $output_names{$field}; 
	}
   $answer .= sprintf (qq(<a href="/TRAINING/Syllabus/%s.shtml" target="_syllabus" onmouseover="Tip('%s')" onmouseout="UnTip('')">%s</a>, ), 
		$field,
		$output_names{$field},
		$the_field
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
    $answer .= sprintf ( qq(<a href="https://members.skylinesoaring.org/TRAINING/Syllabus/%s.shtml" 
	target="_lesson"
	onMouseover="Tip('%s');" onMouseout="UnTip('');">%s</a> \n),
	$input[$lesson_number], 
	$field_names{$input[$lesson_number]},
	$input[$lesson_number]
	); 
    }
  $answer; 
  } 

sub populate_javascript {
  return;
	# this doesn't work. poooh. 
  print qq(\n<script language="JavaScript">\n); 
  for my $param (param()) {
    next unless $param =~ /^s\-...?\-/;
    next if (param($param) eq '');
    printf (qq(
	alert('all your base are belong to us'); 
	%s="%s";
	document.getElementById(%s + "-a").src="levels[%s]";
	document.getElementById(%s + "-a").value="%s";
	document.getElementById(%s).value="%s";
	),
	$param, 
	param($param), 
	$param, 
	param($param), 
	$param,
	param($param),
	$param,
	param($param),
	);
    }
  print qq(</script> ); 
  } 
 
sub show_current_syllabus {
	# Just like the subroutine says; show the current syllabus for $user
	# Seems simle enough, eh? 
	# Need to get all of the flights out of the flight_info database. 
  my ($user) = shift;
  my (%flight_cols);			# All the information about a flight per lesson number
  my (@flights);			# All the stuff about the flights for this guy.
  my (%syllabus) = gimme_syllabus();	# All the info about the syllabus in general
  my (%kludge_dd); 			# If the logsheet gets overwritten, the id changes. This sets a 
					# flight_date for each flight_tracking_id that we find. 
  print mini_javascript();		# Just enough javascript to get the blobs to work
  my ($sql) = gimme_sql($user);		# Give me the SQL for given user
  my $get_info = $dbh->prepare($sql);	# Fetch database for that SQL
  print start_form(-id=>'myform');	# The form is named 'myform' do HTML headers for form
  print hidden('handle', $user);	# we have to secretly include the handle
  my ($limit)=param('limit');
  $limit ||= 20; 
  @flights=fetch_flight_info($user,$limit); 
  print <<EOM;
<table border="0" width="50%">  
<tr align="center"><td bgcolor="#888888" colspan="8"><font color="#FFFFFF">Key:</font></td></tr>
<tr><td colspan="8">
<table border="0" width = "100%"> 
<tr>
  <td align="right"><img src="/icons/blobs/blob0.png"></td><td>Not Covered</td>
  <td align="right"><img src="/icons/blobs/blob1.png"></td><td>Demonstrated</td>
  <td align="right"><img src="/icons/blobs/blob2.png"></td><td>Performed</td>
<tr>
  <td align="right"><img src="/icons/blobs/blob3.png"></td><td>Solo Proficient</td>
  <td align="right"><img src="/icons/blobs/blob4.png"></td><td>Rating Proficient</td>
  <td align="right"><img src="/icons/blobs/blob5.png"></td><td>Critical Issue</td></tr>
</tr>
</table>
</td>
</tr>
<td align="center" colspan="8" bgcolor="#888888"><font color="#FFFFFF">Backgrounds</font></td></tr>
<tr>
<td bgcolor="#AAAADD" width="20" height="20">&nbsp;</td><td>Max score,<br> &gt; 20 flights prior</td>
<td bgcolor="#E8E8F8" width="20" height="20">&nbsp;</td><td>Ground or<br>Simulator Training</td>
<td bgcolor="#AADDAA" width="20" height="20">&nbsp;</td><td>Maximum Attained</td>
EOM

  if (is_user_instructor($the_instructor)) {
    printf (qq(
<td bgcolor="#DDDD88" width="20" height="20"></td><td>Please Enter Information</td> <td >&nbsp;</td></tr>
<script>counterz['s-default-0']=1;</script>
<td align="center" colspan=8 bgcolor="#888888"><font color="#FFFFFF">Preferences / Actions</font></td></tr>
)); 

    if ($#flights == 0 && $flights[0]{'instructor'} eq $the_instructor) {
	# First, check to ensure that the instructor is you, and that dude had only 1 flight
	# and that it was with the_instructor. 

	# Once we have established it, fetch the flight information for this student instructor pairing on this date. 
      my ($fl) = column_for_this_flight(
                param('student'),
                $flights[0]->{'instructor'},
                $flights[0]->{'flight_date'},
                $flights[0]->{'days_ago'}
	);
      $flight_colspan{$flights[0]->{'flight_date'}}{$flights[0]->{'instructor'}}=0; # I hate that I have to do that line
		# The above line is kludged in so that the columns don't expand when 	
		# we do this check.  Just pretend you didn't see it, OK? 

	# OK this line here says, "If any of the lines are marked, then tihs isn't valid. 
	# Otherwise, we know that nothing in the syllabus for that line has been marked, 
	# so we can print out the extra button. 
      unless ($fl->{'marked'} ) {
        printf (qq(
<tr><td colspan="7" align = "center">
	<table border="0">
	<td align="left" valign="top">It appears this was the student's first and only flight.  If it was a basic demo flight (like a FAST flight), you may indicate it as such here: %s</td></tr></table>\n),
		submit(
	        -name=>'submit',
		-label=>'Record This as a Default Demo Flight',
		) . 
		qq(<br /><br />Topics that will be automatically listed as 1 - Demonstrated: <ul><li>1C - Use of Controls
<li>1D - Cockpit Familiarization
<li>2D - Airport Procedures
<li>2E - Cockpit Management
<li>2F - Aerotow Release
<li>2H - Normal Takeoff
<li>2I - Normal Aerotow
<li>2k - Normal Landing</ul>)
		);
        }
      }

    printf (qq(<tr><td colspan="7" align="center"><table border="0">
<td align="left" valign="top">Set first click to: %s %s</td></tr></table></td></tr>
	),
	clickey_lesson_ball(1, 'default', 0 ), 
	textfield(
		-default => 'Demonstrated',
		-id => 'default_text',
		-size=> 12,
		-disabled=> 'true',
		)
	);

    print qq(<td align="center" colspan=8 bgcolor="#888888"><font color="#FFFFFF">Navigation</font></td></tr>);
    print qq(<tr><td colspan="8" align="center"><table border="0" cellpadding="3" cellspacing="5"><tr>); 
    if (! param('limit')) {
      printf qq(<td><a href="?student=%s&limit=1000">Show all flights</a><br> (if appropriate)</td> ),
	$user;
      }
    else {
      printf qq(<td><a href="?student=%s">Show 20 most recent flights</a> </td> ),
	$user;
      }
    printf (qq(<td><a href="?">Return to Main</a> ) . 
	qq(<td><a href="?student=$user&notes=on">Show Instruction Record</a></td>) . 
	qq(<td><a href="/STATS/?pilot=$user">Show Flight Log</a></tr>)); 

    }  # End check for "viewer is instructor" check
  else {
    print "<td></td></tr>\n"; 
    }

  print "</table><br>\n";

  print '<table border = "1" bgcolor = "#FFFFFF">' . "\n";
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
    my($id);
    $id=$flights[$flight_number]->{'flight_tracking_id'}; 
    if ($id+0==0) {
      $id=$flights[$flight_number]->{'ground_tracking_id'}; 
      }
    $flight_cols{$id}=column_for_this_flight(
		$user,
		$flights[$flight_number]->{'instructor'},
		$flights[$flight_number]->{'flight_date'},
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
		"https://members.skylinesoaring.org/TRAINING/Syllabus/$lesson_number.shtml",
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
        my ($id); 
        $id=$flights[$flight_number]->{'flight_tracking_id'}; 
        my ($bgcolor); 
        if ($id+0==0) {
          $id=$flights[$flight_number]->{'ground_tracking_id'}; 
          $bgcolor="#E8E8F8";
          }
        else {
          $bgcolor="#FFFFFF";
          }
        my $lesson_ball; 

		# Is the person viewing this form the same instructor for this flight? 
		# Is this flight less than $max_days_ago? (like 30) 
		# Is nothing noted for this flight previously? 
		# If these are all true, then we need a clickey_lesson_ball
		# that is a lesson ball that the instructor dude can click on to record 
		# progress.   Otherwise, it is not a clickey-ball.  
		# No clickeyball means you can just view the progress instead of 
		# clicking to record something. 

        if ($the_instructor eq $flights[$flight_number]->{'instructor'} && 
		$flights[$flight_number]->{'days_ago'} < $max_days_ago &&
		$flight_cols{$id}->{'marked'} < 1) {
	  $lesson_ball=clickey_lesson_ball(
		$flight_cols{$id}->{$lesson_number},
		$lesson_number,
		$id
		);
          warn (sprintf("Sending to clickey_lesson_ball:  '%s', '%s', '%s'\n",
		$flight_cols{$id}->{$lesson_number},
                $lesson_number,
                $id)
		) if $DEBUG;
		#$flights[$flight_number]->{'flight_tracking_id'}
			# For some reason I was using the raw entry there, 
			# instead of the shortcut.  If the program blows up
			# while trying to insert data for flights, this is probably
			# where something subtle went wrong, and I failed. 
			# So #FIXME here temporarily. 
		# And in addition to the clickey lesson ball, the background should be a 
		# yellow puke color that is represented by dddd88
          $bgcolor="#DDDD88";
          $kludge_dd{'dd-' . $id}=$flights[$flight_number]->{'flight_date'};
          }
        else {
	  $lesson_ball=lesson_ball(
		$flight_cols{$id}->{$lesson_number},
		$lesson_number,
		$flight_number
		);
          }
 
        if ($flight_number == $#flights) {
          $bgcolor="#AADDAA";
          }
        elsif ($flight_number == 0 && $#flights == 21) {
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
	# If the lesson number doesn't have a letter in it
	# i.e. if it's lesson number 1 instead of 1a, 
	# then we don't have any clickey balls to click on 
	# or any progress balls to show progress, since the lesson 
	# numbers without letters are just considered to be lesson
	# plan groupings, and not indvidual lesson plans. 
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
  if ($submission > 1) {
    for my $key (sort keys (%kludge_dd)) {
      print hidden($key, $kludge_dd{$key});
      }
	# Somewhere along the way, we have a clickey_lesson ball; 
	# so we need to have a submit button for the instructor to press. 

    print submit(
	-name=>'submit',
	-value=>'Proceed',
	);
    print br;
    }
  populate_javascript(); 
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
	# Just a shortcut to draw all the HTML needed to make the progress ball 
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
	onmouseover="Tip(levels_description[%s])"
	onmouseout="UnTip('')">),
	$blobno,
	$blobno,
	);
  my $answer2 = sprintf (qq(<img border="0" 
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

sub clickey_lesson_ball {
	# Just a shortcut to draw all the HTML needed to make the progresws ball 
	# This one is for when the instructor actually wants to enter data. 
	# so this is the clickey ball, not just a regular ball. 

	# Input is the number 0 through 5 
	# second input is the number of the lesson plan
	# third number is the number of the flight
	# output is HTML to draw the ball of progress 
  my ($input)=shift; 
  my ($lesson_number) = shift;
  my ($flightno) = shift; 
  my ($blobno) = 0+ $input ; 
  my ($answer);
  my ($js_id) = sprintf ("s-%s-%s", $lesson_number, $flightno);
  $submission++;
  $answer = hidden(-id=> "$js_id", -name=>"$js_id");

  $answer .= sprintf (qq(<img 
	onmouseover="InitMeTwo('%s'); Tip(levels_description[counterz['%s']])"
	onmouseout="UnTip('')"
	onclick=" advance('%s'); Tip(levels_description[counterz['%s']])"
	src="/icons/blobs/blob%s.png" 
	id="%s-a" >
	),
	$js_id, #initme
	$js_id, # tip
	$js_id, # advance onclick
	$js_id, # Tip levels-description
	$blobno,# img src
	$js_id  # id
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
  my %answers=('GROB 103' => 'G', 'CAPSTAN' => 'C', 'ASK-21' => 'K', 'N341KS' => 'K', 'N321K' => 'K', 'QQ' => 'Q', 
	'-' => '-', '' => '-', 'Ground' => 'Ground'
	); 
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
  my ($days_ago) = shift; 
  my (%answer); 
  my ($sql);
  $flight_colspan{$flight_date}{$instructor}++; 
  if ($days_ago eq '<i>Max</i>') {
    $sql = sprintf <<EOM;
select number, max(mode) as mode from student_syllabus3 where ( handle='$handle' and mode::integer != 5 )
	group by number;
EOM
    }
  elsif ($days_ago eq '<i>Prev</i>') {
    $sql = sprintf <<EOM;
select number, max(mode) as mode from student_syllabus3 where ( handle='$handle' and signoff_date < '$flight_date' and mode::integer != 5) group by number;
EOM
    }
  else {
    $sql = sprintf <<EOM; 
select number, max(mode) as mode from student_syllabus3 where handle='$handle' and (instructor='$instructor' and signoff_date='$flight_date') group by number;
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

sub fetch_permissions {
	# We need to figure out who is visiting this page
	# and what they are allowed to view.
	# If there is no remote-user, we have serious problems
	# You aren't supposed to be here.  So we'll make them
	# exit with a weird message.
  if ($the_instructor !~ /\w/) {
    print h1("You have to be somebody to view this page");
    print include ('footer.scrap');
    print end_html();
    exit;
    }
	# if this person is an instructor, then put 'instructor' into
	# the %user_permissions assoc.array.  We can expand this
	# later if we want, but currently this assoc.array has only
	# one key-value pair.
  $user_permissions{'instructor'} = is_user_instructor($the_instructor);
  }

sub is_user_instructor {
	# Get information about this user who is logged in
	# see what kind of reports he/she can view.
	# Are you an instructor? If so you can see anything
	# Are you a student? Then you can only see reports about you...
	# ...You can also only see reports that are safe for your virgin
	# eyes to view. (which the instructor determined).

  my $user = shift;
  my $answer;
  my $get_info = $dbh->prepare(qq(select handle from members where handle = '$user' and instructor='true' and rating='CFIG'));
  $get_info->execute();
  while (my $ans = $get_info->fetchrow_hashref) {
    $answer = $ans->{'handle'};
    }
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



sub fetch_members {
        # Fetch an assoc.array of members.
  my %answer;
  my $status = shift; 
  my $row;
  my ($append);
  if ($status eq 'active') {
    $append=qq(where memberstatus != 'I' and memberstatus !='N' ); 
    }
  if ($status eq 'inactive') {
    $append=qq(where memberstatus = 'I' or memberstatus = 'N' ); 
    }
  my $get_info = $dbh->prepare(
	qq(select handle, lastname, firstname, middleinitial, memberstatus, namesuffix from members $append));
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
    $answer {$row->{'handle'}}=~ s/\s*$//g;
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
<!DOCTYPE HTML>
<html>
<head>
  <meta http-equiv="Content-Type" content="text/html; charset=utf-8">
  <link rel="SHORTCUT ICON" href="/favicon.ico">
  <title>$title</title>
EOM
  print include('left-menu.scrap') unless $header eq 'noheader';
  #beta_test();
  print h1($title);
  verbose_output() if $DEBUG;
  }

sub beta_test {
  print qq(<table border=0 bgcolor="FFE8E8"><tr><td><h2>NOTE WELL</h2>This page is going through beta
testing. Any information you enter here may not be permanently stored.  Please immediately report bugs 
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

sub add_qualifications {
	# So this guy did something to add some qualifications? 
	# We'll show what he's got, and what he needs added here. 
	# Not really linked to the flight_info database at all, this sub
	# could stand by its self. 
  my ($endorsement_date)  = shift; 
  my ($handle) = shift; 

  my (%quals) =  please_to_fetching_unordered(
    qq(select name, img_url, description, is_qual from endorsement_roles),
      'name', 'img_url', 'description', 'is_qual'	
    );
  my (%dude_qual) = please_to_fetching_unordered(
    sprintf (qq(select role_name, is_qualified, expires, expiration_date, instructor, notes from quals where handle='%s' and is_qualified=TRUE), $handle), 
	'role_name', 'is_qualified', 'expires', 'expiration_date', 'instructor', 'notes'
	);

  printf qq(%s currently holds these club qualifications:<br>\n), 
	$handle_labels{$handle};
  my ($qual_count) = 0; 
  for my $is_qualified (sort %dude_qual) {
    next if $quals{$is_qualified}{'img_url'} eq '';
    printf (qq(<img src="/INCLUDES/Qual-Icons/%s" alt="%s" width="50" height="50" onmouseover="Tip('%s')" onmouseout="UnTip('')">\n),
	$quals{$is_qualified}{'img_url'},
	$quals{$is_qualified}{'description'},
	$quals{$is_qualified}{'description'},
	);
    $qual_count++; 
    }
  if ($qual_count == 0) {
    print "<i>None</i>\n";
    }
  my ($new_qualcount)=0;
  printf qq(<br>Add new qualifications:<br>\n);
  print qq(<table border="0"><tr>\n);
  for my $qual (sort keys %quals) {
    next if user_has_rating($handle) && $quals{$qual}{'description'} =~ /Student/i;
	# If the dude has a rating, don't allow him to get a student endorsement. 
    next if ! (user_has_rating($handle)) && $quals{$qual}{'description'} =~ /PIC/i;
	# If the dude is a student, don't allow Quals to include PIC. 
    next if ($dude_qual{$qual}{'is_qualified'} eq 1);
    next if ($quals{$qual}{'description'} eq ''); 
    print "<tr>" if ($new_qualcount % 5 ==0);
    print "<td>\n";
    print checkbox (
	-name => 'quals',
	-value => $qual, 
	#-label => $quals{$qual}{'description'}
	-label => ''
	);
   printf (qq(<img src="/INCLUDES/Qual-Icons/%s" alt="%s" width="50" height="50" onmouseover="Tip('%s')" onmouseout="UnTip('')">\n),
		$quals{$qual}{'img_url'},
		$quals{$qual}{'description'},
		$quals{$qual}{'description'});   
    print "<td>\n";
    print "</tr>" if ($new_qualcount % 5 ==4);	# Make the columns only 5 items wide. This prevents the page from getting too wide. 
    $new_qualcount++;
    } 
  print "</table>\n";
  }

sub enter_data_table {
	# The table that you enter your report in. 
	# the elm1 is the super cool javascript that makes all the syntax highlighting, etc. 

  my ($input)=shift; 
  print "<br><b>Enter Any Comments</b> <br>\n";
  print textarea(
	-name => "$input",
	-rows => "15",
	-cols => "80",
	);
  
  }

sub escape {
	# This is a really ghetto way of escaping input. 
	# if i was smart i would use a Perl module that escapes properly. 
  my ($input) =shift;
  my ($answer);
  $answer = $input;
  $answer =~ s/'/&#039;/g;
  $answer =~ s/\?/&#063;/g;
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
