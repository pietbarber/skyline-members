#!/usr/bin/perl

	# Very Stripped down version of the original training Syllabus
	# program, only has enough to actually print the table of the 
	# syllabus and that's about it. 


use CGI qw(:standard);  # Talk to the CGI stream
use DBI;                # Allows access to DB functions
use strict;             # Create extra hoops to jump through
my ($dbh);              # Handle for DB connections
my (%syllabus);		# Contains the syllabus

connectify();           # Connect to DB

my $arg1 = shift (@ARGV);
if (!$ENV{'REMOTE_ADDR'} && $arg1 eq 'tracking') {
  show_current_syllabus(); 
  exit;
  } 
elsif (!$ENV{'REMOTE_ADDR'} && $arg1 eq 'progress') {
  show_tracking_sheet(); 
  exit; 
  } 


# Main: 
  start_page('Skyline Soaring Club Training Syllabus', header());
  print <<EOM; 
The Complete Skyline Soaring Syllabus is also available in:
<ul>
 <li><a href="syllabus.pdf">PDF Format</a>
 <li><a href="/TRAINING/Syllabus/full-syllabus.shtml">Full Syllabus</a> (One page)
</ul>
EOM
  print syl_include('intro.scrap'); 
  print syl_include('materials.scrap'); 
  #show_current_syllabus();
  print syl_include('training-tracking.scrap'); 
  print syl_include('flight-progress-tracking.scrap'); 
  print syl_include('training-affirmation.scrap'); 
  end_page();

# End Main 



# Subroutines Lie here. 

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
    for my $key ('number', 'title', 'description', 'far_requirement', 'pts_aoa', 'description') {
      $answer{$ans->{'number'}}{$key}=$ans->{$key};
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
  my ($dir, $fulldir);
  open (INCLUDE, "/var/www/members/INCLUDES/$file") || print "Can't open that file $!";
  while (my $line = <INCLUDE>) {
    $answer .= $line;
    }
  close (INCLUDE);
  $answer;
  }


sub syl_include {
	# Pull file from the SYLLABUS directory
	# output of subroutine is that file.
  my $file = shift;
  my $title = shift;
  my $answer;
  return if $file =~ /\.\./;
  open (INCLUDE, "/var/www/members/TRAINING/Syllabus/$file") || print "Can't open that file $!";
  while (my $line = <INCLUDE>) {
    $answer .= $line;
    }
  close (INCLUDE);
  $answer;
  }

sub show_tracking_sheet { 
  %syllabus = gimme_syllabus();
  print "Student Name: <br>\n"; 
  
  print '<table border = "1" bgcolor = "#FFFFFF">' . "\n";
  my ($a_block)=qq(<td width="50">&nbsp;</td>);
  my ($a_grey_block)=qq(<td bgcolor="#888888" width="70">&nbsp;</td>);

  print '<tr bgcolor="#D8D8D8">' . "\n";
  print qq(<td colspan="2" align="right">Instructor's Initials</td>);
  print $a_block x 7; 
  print qq(<td bgcolor="#888888">Max</td>);
  print "</tr>\n";

  print '<tr bgcolor="#D8D8D8">' . "\n";
  print qq(<td colspan="2" align="right">Date of Flight</td>);
  print $a_block x 7; 
  print $a_grey_block;
  print "</tr>\n";

  print '<tr bgcolor="#D8D8D8">' . "\n";
  print qq(<td colspan="2" align="right">Number of Flights</td>);
  print $a_block x 7; 
  print $a_grey_block;
  print "</tr>\n";

  for my $key (sort keys %syllabus) {
    next if ($key =~ /^\d$/); 
    printf (qq(<tr><td align="right">%s</td><td align="right"><a href="https://members.skylinesoaring.org/TRAINING/Syllabus/%s.shtml">%s</a></td>),
	$syllabus{$key}{'number'},
	$syllabus{$key}{'number'},
	$syllabus{$key}{'description'} || $syllabus{$key}{'title'}
	);
    print $a_block x 7; 
    print $a_grey_block;
    print "</tr>\n";
    }
  print '</table>' . "\n";
  } 

sub show_current_syllabus {
  %syllabus = gimme_syllabus();
  print '<table border = "1" bgcolor = "#FFFFFF">' . "\n";
  print '<tr bgcolor="#444444">' . "\n";
	# Print out some table headers
  for my $key ('Lesson','Phase&nbsp;&nbsp;', 'FAR Requirement', 'PTS Area', 'Instructor Sign-Off and Date') {
    printf ('<td align="right"><font color ="#FFFFFF" size="+1">%s</font></td>', $key);
    }
  for my $key (sort keys %syllabus) {
	# Go through each item through the syllabus; each $key is actually the number
	# of the syllabus entry. 
    print "<tr>\n";
    for my $val ('number', 'title', 'far_requirement', 'pts_aoa', 'signoff') {
      my($bgcolor)   = '#FFFFFF';
      my($fontcolor) = '#000000';
      my($fontsize) = '+0';
      my($align) = 'left';
      $align = 'right' if ($val =~ /signoff|title|far_requirement|pts_aoa|number/);
      $fontsize = '-1' if ($val =~ /signoff|title|far_requirement|pts_aoa/);
      $fontsize = '+1' if ($key =~ /\d$/);
	# Some columns, if they only have a number, don't have filled in boxes.
	# THey're just grey across.  Here's where we specify the grey.
      $bgcolor   = '#888888' if ($key =~ /\d$/);
      $fontcolor = '#FFFFFF' if ($key =~ /\d$/);
      my ($colspan); 
      if ($val =~ /title/ && $key !~ /\d$/) {
	# Titles also have a hyperlink to the syllabus page. 
        printf <<EOM, $syllabus{$key}{'number'}, $syllabus{$key}{$val};
<td bgcolor="$bgcolor" align="$align"><a href="https://members.skylinesoaring.org/TRAINING/Syllabus/%s.shtml">%s</a>&nbsp;</td>
EOM
	next;
        }
	# all the goo gets stored up in $answer, which will be blurted out later. 

      $bgcolor   = '#D8D8D8';
      $bgcolor   = '#888888' if ($key =~ /\d$/);
      $bgcolor   = '#FFFFFF' if ($key !~ /\d$/ && $val eq 'signoff');
      printf <<EOM, $syllabus{$key}{$val};
<td bgcolor="$bgcolor" align="$align"><font size="$fontsize" color="$fontcolor">%s</font>&nbsp;</td>
EOM
      }
    print "</tr>\n";
    }
  print '</table>' . "\n";
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

sub connectify {
        # Just connect to the database.
  my $driver = "DBI::Pg";
  my $database = 'skyline';
  $dbh = DBI->connect("DBI:Pg:dbname=$database")
	|| die ("Can't connect to database $!\n");
  }


__END__


skyline=> \d student_syllabus2
         Table "public.student_syllabus2"
    Column    |         Type          | Modifiers
--------------+-----------------------+-----------
 handle       | character varying(20) | not null
 number       | character varying(3)  | not null
 mode         | character varying(4)  | not null
 instructor   | character varying(20) | not null
 signoff_date | date                  | not null


skyline=> \d syllabus_contents
          Table "public.syllabus_contents"
     Column      |         Type          | Modifiers
-----------------+-----------------------+-----------
 number          | character varying(5)  | not null
 title           | character varying(80) |
 description     | text                  |
 far_requirement | character varying(20) |
 pts_aoa         | character varying(20) |
Indexes: syllabus_contents_number_key unique btree (number)


skyline=> select * from syllabus_contents ;
 number |                           title                           | description |  far_requirement  |   pts_aoa
--------+-----------------------------------------------------------+-------------+-------------------+-------------
 1      | Before We Fly                                             |             |                   |
 1a     | Preflight Planning/Overview                               |             | 61.87(i)(1)       | I
 1b     | Aeromedical Factors Discussion                            |             |                   |
 1c     | Use of Controls                                           |             |                   |
 1d     | Cockpit Familiarization                                   |             |                   |
 1g     | Glider Ground Handling - Hangar to Flightline             |             | 61.87(i)(2)       | II(B)
 1h     | Glider Ground Handling - Flightline to Hangar             |             | 61.87(i)(2)       | II(B)
 2      | First Flights                                             |             |                   |
 2a     | Pre Takeoff Checklist                                     |             | 61.87(i)(1)       | IV(A)
 2b     | Attitude Flying/Scanning                                  |             | 61.87(i)(6)       |
 2c     | Glider Daily Inspection                                   |             | 61.87(i)(1)       | I, II(C)
 2d     | Airport Procedures (Traffic Pattern, Taxiways)            |             | 61.87(i)(5)       | III(A,B,C)
 2e     | Cockpit Management                                        |             |                   | II(D)
 2g     | Launch Signals                                            |             | 61.87(i)(11)      | II(E)
 2h     | Normal Takeoff                                            |             | 61.87(i)(3)       | IV(B)
 2i     | Normal Aerotow                                            |             | 61.87(i)(12)      | IV(C)
 2j     | Straight Glide                                            |             | 61.87(i)(4), (15) | VII(A)
 2k     | Shallow, Medium, Steep Turns                              |             | 61.87(i)(4),(15)  | VII(C)
 2l     | Normal Landing                                            |             | 61.87(i)(16)      | IV(Q)
 3      | The Core Flights                                          |             |                   |
 3a     | Transition Between High and Low Tow Position              |             | 61.87(i)(12)      | IV(C)
 3b     | Before-landing Checklist                                  |             | 61.87(i)(16)      | IV(Q)(8)
 3d     | Minimum Controllable Airspeed                             |             | 61.87(i)(8)       | V(A), IX(A)
 3e     | Turns to Heading                                          |             |                   | VII(B)
 4      | Polishing Performance                                     |             |                   |
 4b     | Radio Procedures                                          |             |                   | III(A)
 4c     | Minimum Sink/MCA                                          |             | 61.87(i)(8)       | V(A)
 4d     | Slips: Forward, Side, Turning (w/ & w/o airbrakes)        |             | 61.87(i)(7)       |
 4e     | Best L/D; Speed-to-fly                                    |             | 61.87(i)(8)       | V(B)
 4f     | Boxing the Wake                                           |             | 61.87(i)(12)      | IV(E)
 4g     | Crosswind Takeoff                                         |             | 61.87(i)(3)       | IV(B)
 4h     | Crosswind Landing                                         |             | 61.87(i)(16)      | IV(Q)
 4i     | Unassisted Takeoff                                        |             | 61.87(i)(3)       | IV(G)
 4j     | Pre-Solo Written Test                                     |             | 61.87(b)          |
 4k     | Covered Instrument Landings                               |             | 61.87(i)(9)       | X(A)
 4l     | Precision Landings and Stops                              |             | 61.87(i)(16)      | X(A)
 4m     | Slips to Landing (w/ & w/o airbrakes)                     |             | 61.87(i)(17)      | IV(R)
 4n     | Rope Breaks                                               |             | 61.87(i)(9),(19)  | IV(G)
 4o     | The "A" Badge                                             |             |                   |
 5      | Emergencies and Unusual Attitudes                         |             |                   |
 5a     | Slack Line                                                |             | 61.87(i)(9),(19)  | IV(D)
 5b     | Aerotow Emergency Procedures                              |             | 61.87(i)(9),(19)  | IV(G)
 5c     | Maneuvering Speed                                         |             | 61.87(i)(8)       | V
 5d     | Structural Cruising Speed                                 |             | 61.87(i)(8)       | V
 5e     | Never-exceed Speed                                        |             | 61.87(i)(8)       | V
 6      | Soaring Techniques                                        |             |                   |
 6a     | Thermal                                                   |             | 61.87(i)(18)      | VI(A)
 6b     | Ridge                                                     |             |                   | VI(B)
 6c     | Wave                                                      |             |                   | VI(C)
 7      | Getting Practice/Teaching Yourself                        |             |                   |
 7a     | The B Badge                                               |             |                   |
 7b     | The C Badge                                               |             |                   |
 8      | The Finishing Touches                                     |             |                   |
 8a     | Downwind Landing                                          |             | 61.87(i)(16)      | IV(S)
 8b     | Taxiing and Clearing Runway                               |             | 61.87(i)(2)       | XI
 9      | Filling in the Gaps                                       |             |                   |
 9a     | Assembly                                                  |             | 61.87(i)(13)      | II(A)
 9b     | Postflight Inspection                                     |             |                   | XI(A)
 9c     | Disassembly                                               |             | 61.87(i)(13)      | XI(A)
 1e     | Positive Control Check                                    |             | 61.87(i)(1)       | II(C)
 1f     | Release Mechanisms (Schweizer, Tost)                      |             | 61.87(i)(1)       | II(C)
 3f     | Forward Stall Entry, Stall, Recovery w/ and w/o airbrakes |             | 61.87(i)(14)      | IX(B)
 3g     | Turning Stall Entry, Stall, Recovery w/ and w/o airbrakes |             | 61.87(i)(14)      | IX(B)
 3h     | Spirals and Descents (w/ and w/o airbrakes                |             | 61.87(i)(15)      |
 4a     | Collision, Windshear & Wake Turbulence Avoidance          |             | 61.87(i)(6)       | IV(G)
 2f     | Aerotow Release                                           |             | 61.87(i)(11)      | IV(F)
 3c     | Traffic Pattern                                           |             | 61.87(i)(16)      | IV(Q)
(67 rows)

