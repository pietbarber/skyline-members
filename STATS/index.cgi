#!/usr/bin/perl

	# Nice Web interface to show flights in the 
	# flight_info database. 

	# Uses the database extensively. 
	# 
	# Remaining To-Do list: 

use CGI qw(:standard);  # Talk to the CGI stream
use DBI;                # Allows access to DB functions
use strict;             # Create extra hoops to jump through
my ($dbh);              # Handle for DB connections
my %user_permissions;   # assoc.array to store permissions
connectify();           # Connect to DB
my %handle_labels = fetch_members(); # allows me to convert handles to names
my %instructors = fetch_instructors(); # allows me to convert handles to names
my %towpilots = fetch_towpilots(); # allows me to convert handles to names

	# So now we go through the main list portion of the program
	
	# If this user didn't need to authenticate to get here, then
	# just show them an empty training syllabus, and no form or means
	# to get them to show a student's information, or enter in new info. 
if (!param) {
  start_page("Flight Statistics");
  my_flights();
  end_page();
  exit;
  }

elsif (param('pilot')) {
  start_page("Flights by Pilot");
  flights_by_person(param('pilot'));
  end_page();
  exit;
  }

elsif (param('inst')) {
  start_page("Instruction Statistics");
  top_menu();
  flights_by_instructor(param('inst'));
  end_page();
  exit;
  }

elsif (param('date')) {
  start_page("Flight Statistics by Date");
  print h3(param('date')) unless param('date') eq '1'; 
  top_menu();
  flights_by_date(param('date'));
  end_page();
  exit;
  }

elsif (param('tow')) {
  start_page("Towing Statistics");
  top_menu();
  flights_by_towpilot(param('tow'));
  end_page();
  exit;
  }

elsif (param('ops_days')) {
  start_page("Daily Ops Statistics");
  top_menu();
  flights_by_date();
  end_page();
  exit;
  }

else { 
  start_page("Flight Statistics");
  end_page();
  exit;
  }

exit;


############################
#   Subroutines            #
############################

sub flights_by_towpilot {
	# Show the number of flights by towpilot.
  my ($name) = shift; 
  print h2("Tow Statistics for " . $towpilots{$name});
  my ($row); 	# Database answer handle;
  my ($sql) = qq!select flight_date, count(*) as count, min(takeoff_time) as min, max(takeoff_time) as max from flight_info where towpilot = '$name' group by flight_date order by flight_date desc! ; 
  my $get_info = $dbh->prepare($sql);
  $get_info->execute();
  print "<table bgcolor=\"#FFFFFF\" cellpadding=\"2\" cellspacing=\"2\">\n";
  my ($count);
  my ($column_header) =<<EOM;
<tr bgcolor="#C8C8C8">
	<td><font size="+1">Date</font></td>
	<td><font size="+1">Number</font></td>
	<td><font size="+1">First TO</font></td>
	<td><font size="+1">Last TO</font></td>
</tr>
EOM
  print $column_header;
  while ( my $row = $get_info->fetchrow_hashref ) {
	# Go through each row in the output of the SQL output. 
	# Alternate white and off-white as the background color. 
    my $bgcolor = "#FFFFFF";
    $bgcolor = "#E8E8E8" if (($count++ % 2) == 1);

	# here is the big html print line. 
    printf ("<tr bgcolor=\"$bgcolor\">\n\t<td>%s</td>\n\t<td align=\"right\">%s</td>\n\t<td>%s</td><td>%s</td></tr>\n",
	$row->{'flight_date'},
	$row->{'count'},
	$row->{'min'},
	$row->{'max'},
	);
    }
  print "</table>";
  }

sub trunc_seconds {
	# Postgres stores times like this: 12:00:00
	# I just want this: 12:00
  my ($input) = shift;
  $input =~ s/:00$//;
  if ($input eq '00:00') {
    $input = '<i>Not recorded</i>';
    }
  $input;
  }

sub flights_by_date {
  my ($date) = shift; 
  my ($row); 	# Database answer handle;
  my ($sql);
  if ($date !~ /^\d{4}\-\d{2}-\d{2}$/) {
    $sql = qq#select flight_date, count(*) as num_flights, min(takeoff_time) as first_to, max(landing_time) as last_landing from flight_info group by flight_date order by flight_date desc#;
    my $get_info = $dbh->prepare($sql);
    $get_info->execute();
    print "<table bgcolor=\"#FFFFFF\">\n";
    my ($count);
    my ($column_header) =<<EOM;
<tr bgcolor="#C8C8C8">
	<td><font size="+1">Date</font></td>
	<td><font size="+1"># of Flt.</font></td>
	<td><font size="+1">First TO</font></td>
	<td><font size="+1">Last Landing</font></td>
	<td><font size="+1"></font></td>
</tr>
EOM
    print $column_header;
    while ( my $row = $get_info->fetchrow_hashref ) {
	# Go through each row in the output of the SQL output. 
      my $bgcolor = "#FFFFFF";
      $bgcolor = "#E8E8E8" if (($count++ % 2) == 1);

	# here is the big html print line. 
      printf ("<tr bgcolor=\"$bgcolor\">\n\t<td>
	<a href = \"?date=%s\">%s</a></td>\n\t<td align=\"right\">%s</td>\n\t<td align=\"right\">%s</td>\n\t<td align=\"right\">%s</td>\n\t<td>%s</td>\n\t<td>%s</td>\n\t<td>%s</td>\n\t<td>%s</td></tr>\n",
	$row->{'flight_date'},
	$row->{'flight_date'},
	$row->{'num_flights'},
	trunc_seconds($row->{'first_to'}),
	trunc_seconds($row->{'last_landing'})
	);
      }
    print "</table>";

    }

  else {
    logsheet_link ($date); 
    duty_guys($date); 
    ops_flights($date);
    print h2("Tow Plane Information"); 
    my $sql = qq!select distinct field from ops_days where flight_date = '$date'!; 
    my $get_info = $dbh->prepare($sql);
    my (%fields, %towplanes); 
    $get_info->execute();
    while ( my $ans = $get_info->fetchrow_hashref ) {
      $fields{$ans->{'field'}}++; 
      }
    my $sql = qq!select distinct towplane from towplane_data where flight_date = '$date'!; 
    my $get_info = $dbh->prepare($sql);
    $get_info->execute();
    while ( my $ans = $get_info->fetchrow_hashref ) {
      $towplanes{$ans->{'towplane'}}++; 
      }
    for my $field (sort keys (%fields)) {
      for my $towplane (sort keys (%towplanes)) {
        tow_info ($towplane, $date, $field); 
        }
      }
    new_contacts ($date); 
    }
  }

sub logsheet_link {
  my ($date) = shift; 
  printf (qq(<br><a href="/LOGSHEET/LOG-SEARCH/?date=%s">Logsheet for %s</a>), 
	$date, 
	$date
	); 
  } 

sub ops_flights {
	#########################
	# Print out the flights  
	#########################
  my ($date) = shift; 
  my ($count); 

  print h2("Operations"); 

  my $sql = qq!select * from flight_info where flight_date = '$date' order by takeoff_time ! ; 
  my $get_info = $dbh->prepare($sql);
  $get_info->execute();
  print "<table bgcolor=\"#FFFFFF\">\n";
  my (%flight_types) = (qw(
	free-demo	FD
	demo	D
	instruction	I
	fast-lesson	F
	regular	R
	));
  my ($column_header) =<<EOM;
<tr bgcolor="#C8C8C8">
	<td><font size="+1">#</font></td>
	<td><font size="+1">Glider</font></td>
	<td><font size="+1">Field</font></td>
	<td><font size="+1">Type</font></td>
	<td><font size="+1">Alt.</font></td>
	<td><font size="+1">Pilot</font></td>
	<td><font size="+1">Instructor</font></td>
	<td><font size="+1">Passenger</font></td>
	<td><font size="+1">Tow Pilot</font></td>
	<td><font size="+1">Flt. Time</font></td>
	<td><font size="+1">Cost</font></td>
</tr>
EOM

  print $column_header;
  while ( my $row = $get_info->fetchrow_hashref ) {
	# Go through each row in the output of the SQL output. 
    my ($flight_time) = $row->{'flight_time'};
    my $alt=$row->{'release_altitude'}; 
    if ($row->{'towpilot'} =~ /Winch/) {
      $alt .= ' (W) ';
      }
    $flight_time =~ s/\:00$//;
    if ($flight_time eq '00:00') {
	# Dont' list 00:00 as a flight time
	# Just say it wasn't recorded. 
        $flight_time = '<i>not recorded</i>';
      }
	# Alternate white and off-white as the background color. 
    my $bgcolor = "#FFFFFF";
    $bgcolor = "#E8E8E8" if (($count++ % 2) == 1);

	# here is the big html print line. 
    printf ("<tr bgcolor=\"$bgcolor\">\n\t<td>%s</td>\n\t<td>%s</td>\n\t<td>%s</td>\n\t<td>%s</td>\n\t<td>%s</td>\n\t<td>%s</td>\n\t<td>%s</td>\n\t<td>%s</td>\n\t<td>%s</td><td>%s</td><td>%s</td></tr>\n",
	#$row->{'flight_date'},
	$count,
	$row->{'glider'},
	$row->{'field'},
	$flight_types{$row->{'flight_type'}},
	$alt,
	$handle_labels{$row->{'pilot'}} || $row->{'pilot'},
	$handle_labels{$row->{'instructor'}} || $row->{'instructor'},
	$handle_labels{$row->{'passenger'}} || $row->{'passenger'},
	$handle_labels{$row->{'towpilot'}} || $row->{'towpilot'},
	$flight_time,
	$row->{'total_cost'},
	);
    }
  print "</table>";
  }

sub duty_guys {
	##################################################
	# Print out the info about duty roles  
	##################################################
  my ($date) = shift; 
  print h2("Assigned Duty"); 
  my $sql = qq!select distinct field from ops_days where flight_date = '$date'!; 
  my $get_info = $dbh->prepare($sql);
  $get_info->execute();
  while ( my $ans = $get_info->fetchrow_hashref ) {
    duty_guy_table($ans->{'field'}, $date); 
    }
  } 

sub duty_guy_table { 
  my ($field) = shift; 
  my ($date) = shift; 
  my ($count); 
  my (%role_today); 
  my (%role_types) = (
	'instructor' => 'Instructor', 
	'dutyofficer' => 'Duty Officer', 
	'assistant' => 'Asst. Duty Officer', 
	'towpilot' => 'Tow Pilot', 
	'am_towpilot' => 'AM Tow Pilot', 
	'pm_towpilot' => 'PM Tow Pilot', 
	);
  my $sql = qq!select * from ops_days where flight_date = '$date' and field='$field'!; 
  my $get_info = $dbh->prepare($sql);
  $get_info->execute();
  print h3($field); 
  print qq(<table bgcolor=\"#FFFFFF\" cellspacing="2" cellpadding="2">\n);
  while ( my $row = $get_info->fetchrow_hashref ) {
	# Go through each row in the output of the SQL output. 
	# Alternate white and off-white as the background color. 
    for my $role (keys (%role_types)) {
      $role_today{$role}=$row->{$role}; 
      }
    }
  for my $role (qw(towpilot am_towpilot pm_towpilot)) { 
    if ($role_today{$role} !~ /\w/) { 
      delete ($role_today{$role}); 
      } 
    }
  $count=1; 
  #for my $role (qw(dutyofficer instructor towpilot assistant am_towpilot pm_towpilot)) {
  for my $role (keys (%role_today)) { 
    my $bgcolor = "#FFFFFF";
    $bgcolor = "#E8E8E8" if (($count++ % 2) == 1);
    printf (qq(<tr bgcolor="$bgcolor">\n\t<td align="right">%s</td>\n\t<td>%s</td></tr>\n),
	$role_types{$role},
	($handle_labels{$role_today{$role}} || "<i>None</i>\n")
	);
    }
  print "</table><br>";
  }

sub new_contacts {
  my $date=shift; 
  my $sql; 
  my $count=1;
  my (@answers);
  my ($answer_count); 
  $sql = qq!select handle from new_contacts where join_date = '$date'!; 
  my $get_info = $dbh->prepare($sql);
  $get_info->execute();
  print qq(<table bgcolor=\"#FFFFFF\" cellspacing="2" cellpadding="2">\n);

  while ( my $row = $get_info->fetchrow_hashref ) {
    $answer_count++;
    push (@answers, $row->{'handle'}); 
    }

  if ($answer_count) {
    print h3('New Contacts'); 
      print "<ul>\n"; 
      for my $handle (@answers) {
	next unless ($handle_labels{$handle}); 
        printf (qq(<li><a href="/MEMBERSHIP/viewmember2.cgi?%s">%s</a></li>\n),
	  $handle,
	  $handle_labels{$handle}
	  );
        }
    print "</ul><br>";
    }
  }

sub tow_info {
	##################################################
	# Print out the towplane information
	##################################################

  my $towplane=shift; 
  my $date=shift; 
  my $field=shift; 
  my $sql; 
  my $count;
  my ($answer_count); 
  my (%tow_types) = (
	'start_tach' => 'Start Tach', 
	'stop_tach' => 'Stop Tach', 
	'tach_time' => 'Tach Time', 
	'gas_added' => 'Gas Added', 
	'towpilot_comments' => 'Tow Pilot Comments',
	'tows' => 'Number of Tows',
	);
  my (%tow_vals); 
  $sql = qq!select * from towplane_data where flight_date = '$date' and towplane='$towplane' and field='$field'!; 
  my $get_info = $dbh->prepare($sql);
  $get_info->execute();
  print qq(<table bgcolor=\"#FFFFFF\" cellspacing="2" cellpadding="2">\n);

  while ( my $row = $get_info->fetchrow_hashref ) {
    $answer_count++;
    for my $key (keys (%tow_types)) {
      $tow_vals{$key}=$row->{$key}; 
      }
    }
  if ($answer_count) {
    print h3($towplane); 
    for my $key (qw(
	towplane start_tach stop_tach tach_time gas_added towpilot_comments tows
	)) {
      my $bgcolor = "#FFFFFF";
      $bgcolor = "#E8E8E8" if (($count++ % 2) == 1);
      printf (qq(<tr bgcolor="$bgcolor">\n\t<td align="right">%s</td>\n\t<td>%s</td></tr>\n),
	$tow_types{$key},
	$tow_vals{$key}
	);
      }
    print "</table><br>";
    }
  }

sub flights_by_instructor {
  my ($name) = shift; 
  my ($row); 	# Database answer handle;
  my $get_info = $dbh->prepare(
	qq!select * from flight_info where instructor = ? order by flight_date desc, flight_tracking_id desc!
	); 
  $get_info->execute($name);
  print "<table bgcolor=\"#FFFFFF\">\n";
  my (%flight_types) = (qw(
	free-demo	FD
	demo	D
	instruction	I
	regular	R
	));
  my ($count);
  my ($column_header) =<<EOM;
<tr bgcolor="#C8C8C8">
	<td><font size="+1">Date</font></td>
	<td><font size="+1">Glider</font></td>
	<td><font size="+1">Type</font></td>
	<td><font size="+1">Alt.</font></td>
	<td><font size="+1">Pilot</font></td>
	<td><font size="+1">Instructor</font></td>
	<td><font size="+1">Passenger</font></td>
	<td><font size="+1">Flt. Time</font></td>
</tr>
EOM
  print $column_header;
  while ( my $row = $get_info->fetchrow_hashref ) {
	# Go through each row in the output of the SQL output. 
    my ($flight_time) = $row->{'flight_time'};
    my $alt=$row->{'release_altitude'}; 
    if ($row->{'towpilot'} =~ /Winch/) {
      $alt .= ' (W) ';
      }
    $flight_time =~ s/\:00$//;
    if ($flight_time eq '00:00') {
	# Dont' list 00:00 as a flight time
	# Just say it wasn't recorded. 
      $flight_time = '<i>not recorded</i>';
      }
	# Alternate white and off-white as the background color. 
    my $bgcolor = "#FFFFFF";
    $bgcolor = "#E8E8E8" if (($count++ % 2) == 1);

	# here is the big html print line. 
    printf ("<tr bgcolor=\"$bgcolor\">\n\t<td>%s</td>\n\t<td>%s</td>\n\t<td>%s</td>\n\t<td>%s</td>\n\t<td>%s</td>\n\t<td>%s</td>\n\t<td>%s</td>\n\t<td>%s</td></tr>\n",
	$row->{'flight_date'},
	$row->{'glider'},
	$flight_types{$row->{'flight_type'}},
	$alt,
	$handle_labels{$row->{'pilot'}} || $row->{'pilot'},
	$handle_labels{$row->{'instructor'}} || $row->{'instructor'},
	$handle_labels{$row->{'passenger'}} || $row->{'passenger'},
	$flight_time,
	$row->{'total_cost'}
	);
    }
  print "</table>";
  }

sub flights_by_person {
	# Will give a breakdown in HTML of the flights that this user has
	# in the database, reverse chronological order. 
  my ($name) = shift; 
  my ($row); 	# Database answer handle;
  my ($sql) = qq!select * from flight_info where pilot = '$name' or passenger = '$name' or instructor = '$name' order by flight_date desc, flight_tracking_id desc! ; 
  my $get_info = $dbh->prepare($sql);
  $get_info->execute();
  print "<table bgcolor=\"#FFFFFF\">\n";
  my (%flight_types) = (qw(
	free-demo	FD
	demo	D
	instruction	I
	regular	R
	));
  my ($count);
  my ($column_header) =<<EOM;
<tr bgcolor="#C8C8C8">
	<td><font size="+1">Date</font></td>
	<td><font size="+1">Glider</font></td>
	<td><font size="+1">Type</font></td>
	<td><font size="+1">Alt.</font></td>
	<td><font size="+1">Pilot</font></td>
	<td><font size="+1">Instructor</font></td>
	<td><font size="+1">Passenger</font></td>
	<td><font size="+1">Flt. Time</font></td>
	<td><font size="+1">Flt. Cost</font></td>
</tr>
EOM
  print $column_header;
  while ( my $row = $get_info->fetchrow_hashref ) {
	# Go through each row in the output of the SQL output. 
    my ($flight_time) = $row->{'flight_time'};
    my $alt=$row->{'release_altitude'}; 
    if ($row->{'towpilot'} =~ /Winch/) {
      $alt .= ' (W) ';
      }
    $flight_time =~ s/\:00$//;
    if ($flight_time eq '00:00') {
	# Dont' list 00:00 as a flight time
	# Just say it wasn't recorded. 
      $flight_time = '<i>not recorded</i>';
      }
	# Alternate white and off-white as the background color. 
    my $bgcolor = "#FFFFFF";
    $bgcolor = "#E8E8E8" if (($count++ % 2) == 1);

	# here is the big html print line. 
    printf ("<tr bgcolor=\"$bgcolor\">\n\t<td>%s</td>\n\t<td>%s</td>\n\t<td>%s</td>\n\t<td>%s</td>\n\t<td>%s</td>\n\t<td>%s</td>\n\t<td>%s</td>\n\t<td>%s</td><td>%s</td></tr>\n",
	$row->{'flight_date'},
	$row->{'glider'},
	$flight_types{$row->{'flight_type'}},
	$alt,
	$handle_labels{$row->{'pilot'}} || $row->{'pilot'},
	$handle_labels{$row->{'instructor'}} || $row->{'instructor'},
	$handle_labels{$row->{'passenger'}} || $row->{'passenger'},
	$flight_time,
	$row->{'total_cost'}
	);
    }
  print "</table>";
  }

sub my_flights {
  print h2("My Flight History");
  top_menu();
  flights_by_person($ENV{'REMOTE_USER'}); 
  }

sub top_menu {
  print qq!<a href = "?date=1">Operations by Date</a><br>\n!;

  if ($instructors{$ENV{'REMOTE_USER'}}) {
    print qq!<a href = "?inst=$ENV{'REMOTE_USER'}">My Instruction History</a><br>\n!;
    }
  if ($towpilots{$ENV{'REMOTE_USER'}}) {
    print qq!<a href = "?tow=$ENV{'REMOTE_USER'}">My Towing History</a><br>\n!;
    }
  if (param('date')) { 
    print "<br>\n"; 
    day_ops('Next', param('date'));  
    day_ops('Previous', param('date'));  
    }
  }

sub day_ops { 
	# Look up the prior day's operations and print out a hyperlink to it. . 
	# Or look up the next day's operations an dprint a hyperlink to it, if it exists. 
  my $mode = shift; 
  my $date = shift; 
  my $modedate; 
  my ($sql); 

  $sql = qq(select max(flight_date) as flight_date from flight_info where flight_date < '$date') 
	if $mode eq 'Previous'; 
  $sql = qq(select min(flight_date) as flight_date from flight_info where flight_date > '$date') 
	if $mode eq 'Next'; 

  my $get_info = $dbh->prepare($sql);
  $get_info->execute();
  while ( my $row = $get_info->fetchrow_hashref ) {
    $modedate=$row->{'flight_date'}; 
    }

  if ($modedate) {
    printf (qq(<a href="?date=%s">Show %s Day (%s)</a><br>), 
	$modedate,
	$mode,
	$modedate
	);
    }
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

sub by_lname {
  $handle_labels{$a} cmp $handle_labels{$b};
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
    $answer{$row->{'handle'}}= sprintf ("%s %s %s %s",
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

sub fetch_instructors {
        # Fetch an assoc.array of instructors.
  my %answer;
  my $row;

  my $get_info = $dbh->prepare(
	qq(select handle, lastname, firstname, middleinitial, memberstatus from members where instructor='true'));
  $get_info->execute();

  while ( my $row = $get_info->fetchrow_hashref ) {
    $answer{$row->{'handle'}}= sprintf ("%s %s %s",
	$row->{'firstname'},
	$row->{'middleinitial'},
	$row->{'lastname'},
	);
    }
  %answer;
  }

sub fetch_towpilots {
        # Fetch an assoc.array of instructors.
  my %answer;
  my $row;

  my $get_info = $dbh->prepare(
	qq(select handle, lastname, firstname, middleinitial, memberstatus from members where towpilot='true'));
  $get_info->execute();

  while ( my $row = $get_info->fetchrow_hashref ) {
    $answer{$row->{'handle'}}= sprintf ("%s %s %s",
	$row->{'firstname'},
	$row->{'middleinitial'},
	$row->{'lastname'},
	);
    }
  %answer;
  }



sub connectify {
        # Just connect to the database.
  my $driver = "DBI::Pg";
  my $database = 'skyline';
  $dbh = DBI->connect("DBI:Pg:dbname=$database")
	|| die ("Can't connect to database $!\n");
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


sub include {
	# Pull file from the INCLUDES directory
	# output of subroutine is that file.
  my $file = shift;
  my $title = shift;
  my $answer;
  my ($dir, $fulldir);
  open (INCLUDE, "/var/www/members/INCLUDES/$file") || print "Can't open that file $!";
  while (my $line = <INCLUDE>) {
    $answer .= $line;
    }
  close (INCLUDE);
  $answer;
  }

sub today {         # What is today?
  my @today = localtime;
  sprintf ("%4.4d-%2.2d-%2.2d", $today[5]+1900, $today[4]+1, $today[3]);
  }


__END__

                                Table "public.flight_info"
       Column       |          Type          |                  Modifiers                  
--------------------+------------------------+---------------------------------------------
 flight_tracking_id | integer                | default nextval('flight_tracking_id'::text)
 flight_date        | date                   | not null
 pilot              | character varying      | 
 passenger          | character varying      | 
 glider             | character varying(20)  | 
 instructor         | character varying(20)  | 
 towpilot           | character varying(20)  | default 'Not Specified'::character varying
 flight_type        | character varying(20)  | 
 takeoff_time       | time without time zone | 
 landing_time       | time without time zone | 
 flight_time        | time without time zone | 
 release_altitude   | integer                | 
 flight_cost        | money                  | 
 tow_cost           | money                  | 
 total_cost         | money                  | 
Indexes:
    "flight_info_idx" btree (flight_date)

