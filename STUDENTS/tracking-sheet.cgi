#!/usr/bin/perl 


	# So Molumphry said somethign like "I like to see this 
	# piece of dead tree showing that a candidate has completed 
	# All of the training in these areas. " 
	#
	# FIne.  Whatever. 
	#

use CGI qw(:standard);  		# Talk to the CGI stream
use DBI;               		 	# Allows access to DB functions
use strict;             		# Create extra hoops to jump through
my ($dbh);              		# Handle for DB connections
connectify();           		# Connect to DB
my %handle_labels = fetch_members();	# allows me to convert handles to names
my %handle_to_name = fetch_straight_members(); # allows me to convert handles to fname,lname format names
my %instructors = fetch_instructors();	# Gets me a list of the instructors
my %syllabus = gimme_syllabus();	# All the info about the syllabus in general
my $DEBUG=0;				# Increase to 1 for more output. 



#####################################################
#   MAIN!
#####################################################


if ($handle_to_name{$ENV{'REMOTE_USER'}}) {
	# Presuming the student field has a handle, if that matches 
	# up with a name in the database, then we'll show the affirmation
	# sheet for that student. 
  show_sheet($ENV{'REMOTE_USER'});
  }
else {
  start_page('howd you get here?');
  } 
 




####################################################
#   Subroutines! 
####################################################

sub beta_test {
  print qq(<table border=0 bgcolor="FFE8E8"><tr><td><h2>NOTE WELL</h2>This page is going through beta
testing. Any information you enter here may not be permanently stored.  Please immediately report bugs
or any feedback you have to Piet Barber (<a href="mailto:pb\@pietbarber.com">pb\@pietbarber.com</a>)</td></tr></table>
        );
  }

sub show_sheet {
	# Shows the Training Affirmation Sheet for the student. 
	# This is just basically all of the items in the syllabus
	# and for each field, we'll find the latest signoff for 4
	# and write the instructor's name and signoff-date.
  my ($student)=shift; 
  start_page(sprintf('Checkride Preparation for %s',
		$handle_to_name{$student}
	 ));
  #beta_test();
  my (%signoffs); 
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
  for my $number (keys %max_signoff) {
    $max_signoff{$number}{'instructor'} = please_to_fetching_scalar(
	sprintf(qq(select instructor from student_syllabus3 where handle='%s' and number = '%s' and signoff_date = '%s' limit 1),
		$student, 
		$max_signoff{$number}{'number'},
		$max_signoff{$number}{'signoff_date'}
		), 'instructor'
	);
    }

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
        print qq(<td bgcolor="#E8E888" align="right">&nbsp;</td>\n); 
        }
      }

    print qq(</tr>\n);
    }

  
  print qq(</table><br>\n); 
  end_page();
  } 



sub needed_for_rating {
	# For a given handle, go through the syllabus.  i
	# Find any items that are called out in 
	# the PTS for a checkride.   Find any items not listed, return them in an assoc_array. 
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
  my $sql = qq(select number from syllabus_contents where pts_aoa != ''); 
  my $get_info = $dbh->prepare($sql);
  $get_info->execute();
  while (my $ans = $get_info->fetchrow_hashref()) {
    $required{$ans->{'number'}}++; 
    }
  my $sql = qq( select number, mode from student_syllabus3 where handle='$handle' and mode::integer = 4);
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



sub today {
        # What is today?
	# Used a few times in this program. 
  my @today = localtime (time - 14400); 
  sprintf ("%4.4d-%2.2d-%2.2d", $today[5]+1900, $today[4]+1, $today[3]);
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
  my (%still_needed) = needed_for_rating($input); 
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
  $answer=sprintf(qq(<table cellspacing="0" border="0" cellpadding="0"><tr><td height="10" width="%d" bgcolor="#44FF44"></td>
	<td width="%d" bgcolor="#888888"></td></tr></table>),
	$done,
	$yet,
	$done
	);

  $answer;
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
  my ($input) = shift;
  my ($status_append);
  my (%solo_count);

  if ($input eq 'active student' or $input eq 'active post-solo student') {
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
  print <<EOM;
<tr>
  <td bgcolor="#000000" align="right"><font color="#FFFFFF">Pilot</font></td>
  <td bgcolor="#000000" align="center"><font color="#FFFFFF">Reports</font></td>
  <td bgcolor="#000000" align="center"><font color="#FFFFFF">Rating Progress</font></td>
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
  if ($input eq 'active post-solo student') {
    %solo_count = please_to_fetching_unordered(qq(select pilot, count(*) as count from flight_info where instructor='' group by pilot), 
	'pilot', 'count');
    for my $dude (keys %answer) {
      delete($answer{$dude}) if $solo_count{$dude}{'count'} < 1; 
      }
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
  <td align="right">%s</a></td>
  <td><a href="?student=%s">Tracking Page</a></td>
  <td align="center">%s</td>
</tr>),
	$user,
	$key, 
	((($input =~ /active .*student/) || $input eq 'inactive student') && percent_complete($key)),
	($last_date{$key} || '<i>None</i> ')
	); 
    }
  print '</table>' . "\n";
   }


sub list_of_students {
 
	# If the page is loaded with no parameters, 
  start_page('Checkride Progress Preparation' );
	# First pring a listing of all the instructor's pending reports
  #beta_test();
  print qq(<table border = "0"><tr valign="top"><td>);
  print br, hr; 
  print h2("Active Post-Solo Students");
  show_student_list('active post-solo student');
  print qq(</td><td>&nbsp;&nbsp;&nbsp;</td><td valign="top">\n);
  print qq(</td></tr>\n);
  print qq(</table><br>\n); 
  end_page();
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

sub end_page {
  print include('footer.scrap');
  exit;
  }

sub by_lastname {
        # Sort the list by the person's last name
  $handle_labels{$a} cmp $handle_labels{$b};
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


sub include {
	# Pull file from the INCLUDES directory
	# output of subroutine is that file.
  my $file = shift;
  my $title = shift;
  my $answer;
  open (INCLUDE, "/var/www/members/INCLUDES/$file") || print "Can't open that file $!";
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


