#!/usr/bin/perl

	# CGI Program that shows details about 
	# a specific member. 
	# takes one ARGUMENT, or returns you to
	# the membership list, if ARGV is empty.

use strict;
use CGI qw/:standard/;
use DBI;
my ($dbh);
db_connectify();
my %admins = fetch_admins();
#my %admins = ();
#

my (%quals) = (
	'ASK-Front'	=> {img => 'ASK-Front.jpg', desc => 'ASK-Front Seat PIC'},
	'ASK-Back'	=> {img => 'ASK-Back.jpg', desc => 'ASK-Back Seat PIC'},
	'Grob-Front'	=> {img => 'Grob-Front.jpg', desc => 'Grob Front Seat PIC'},
	'Grob-Back'	=> {img => 'Grob-Back.jpg', desc => 'Grob Back Seat PIC'},
	'ASK-Student'	=> {img => 'ASK-Student.jpg', => 'Student Solo ASK-21'},
	'Grob-Student'	=> {img => 'Grob-Student', => 'Student Solo Grob 103'},
	'Sprite-Student'	=> {img => 'Sprite-Student.jpg', desc => 'Student Solo Sprite'},
	'Sprite'	=> {img => 'Sprite.jpg', desc => 'Sprite PIC'},
	'TowPilot'	=> {img => 'TowPilot.jpg', desc => 'Tow Pilot'},
	'Pawnee'	=> {img => 'Pawnee.jpg', desc => 'Pawnee Tow Pilot'},
	'Husky'		=> {img => 'Husky.jpg', desc => 'Husky Tow Pilot'},
	'WingRunner'	=> {img => 'Wingrunner.jpg', desc => 'Wing-Runner Qualified'},
	'CFI'		=> {img => 'Instructor.jpg', desc => 'Club Flight Instructor'},
	'Cirrus'	=> {img => 'Cirrus.jpg', desc => 'Cirrus PIC and Assembly'},
	'DutyOfficer'	=> {img => 'DutyOfficer.jpg', desc => 'Duty Officer and Logsheets'},
	'ADO'		=> {img => 'ADO.jpg', desc => 'Assistant Duty Officer'},
	'SafetyMeeting' => {img => 'SafetyMeeting.jpg', desc => 'Attended Safety Meeting'},
	);


my (%status) = (
        'M'     =>      'Standard Member',
        'F'     =>      "Founding Member",
        'P'     =>      'Probationary Member',
        'S'     =>      'Service Member',
        'H'     =>      'Honorary Member',
        'Q'     =>      'Family Member',
        'T'     =>      'Transient Member',
        'I'     =>      'Inactive Member',
        'E'     =>      'Introductory Member',
        'N'     =>      'Not a Member'
        );

my (%ratings) = (
        'S'     =>      "Student",
        'CPL'   =>      'Commercial',
        'PPL'   =>      'Private',
        'CFIG'  =>      'Instructor',
        'F'     =>      'Foreign',
        'N/A'   =>      'N/A or Other'
        );

print header; 
print "<html><head><title>View Member</title>\n";
my (%answers) = read_from_db(param('keywords'));
include("left-menu.scrap");
#for my $key (sort keys (%answers)) {
  #printf ("%s => %s<br>\n",
	#$key, 
	#$answers{$key}
	#);
  #}
print_output();

include("footer.scrap");
exit;


sub print_output {
  print h1(sprintf ("View Member for %s %s %s",
	$answers{'firstname'},
	$answers{'middleinitial'},
	$answers{'lastname'}
	));
  print qq(<!--ToolTip headers-->
<script language="JavaScript" type="text/javascript" src="/INCLUDES/wz_tooltip.js"></script>);
  if ($admins{$ENV{'REMOTE_USER'}}) {
    printf (qq([ <a href ="/ADMIN/editmember2.cgi?%s">Edit This Member</a> ]\n),
	$answers{'handle'}
	);
    }
  print qq(<br>[ <a href="/MEMBERSHIP/">Back to Members List</a> ]\n);
  print qq(<table border=1 bgcolor="#F8F8F8">\n);

  if ($answers{'bio_online'} && $admins{$ENV{'REMOTE_USER'}}) {
    t_row("Biography is Online.", 
		"Last Updated " . $answers{'bio_updated_on'} . 
		br . 
		a( {href => "/BIOS/?member=" . $answers{'handle'}}, "View") .
		" / " . 
		a( {href => "/BIOS/?edit=" . $answers{'handle'}}, 
		"Edit")
		);
    }

  elsif ($answers{'bio_online'}) {
    t_row("Biography is Online.", 
		"Last Updated " . $answers{'bio_updated_on'} . 
		br . 
		a( {href => "/BIOS/?member=" . $answers{'handle'}}, "View")
		);
    }
 
  elsif ($answers{'handle'} eq $ENV{'REMOTE_USER'}) {
    t_row("Create Biography Now:", a({href=>"/BIOS/"}, "Create One Now"));
    }
  else {
    t_row("Biography Online?", "No");
    }
  my @member_quals = fetch_quals($answers{'handle'});

  t_row("Address", 
	sprintf ("%s %s<br>%s, %s %s",
		$answers{'address1'},
		($answers{'address2'} && "<br>" . $answers{'address2'}),
		$answers{'city'},
		$answers{'state'},
		$answers{'zip'},
		$answers{'country'}
		));
  t_row("Club Title / Position", $answers{'official_title'});
  t_row("Email", a(
		{href=>"mailto:" . $answers{'email'}}, 
		$answers{'email'}
	));
  t_row("Phone #1", $answers{'phone1'});
  t_row("Phone #2", $answers{'phone2'});
  t_row("Mobile", $answers{'cell_phone'});
  t_row("Glider Rating", $ratings{$answers{'rating'}});
  t_row("Membership Status", $status{$answers{'memberstatus'}});
  t_row("Duties", 
	join (" ", 
		($answers{'director'} != 0 && "Director"),
		($answers{'instructor'} != 0 && "Instructor"),
		($answers{'towpilot'} != 0 && "Tow Pilot"),
		($answers{'ado'} != 0 && "Assistant Duty Officer"),
		($answers{'dutyofficer'} != 0 && "Duty Officer"),
		($answers{'otherduties'} != 0 && "Other Duties")
		)
	);
  t_row("Qualifications", @member_quals); 
  t_row("Glider(s) Owned", $answers{'glider_owned'} . " "  . $answers{'glider_owned2'});
  t_row("This Record Last Updated", scalar localtime ($answers{'lastupdated'}));
  t_row("Joined Club" , $answers{'joindate'});
  t_row("Emergency Contact Information", "<pre>" . $answers{'emergency_contact'} . "</pre>"); 
  t_row("Notes" , $answers{'public_notes'});
  if ($admins{$ENV{'REMOTE_USER'}}) {
    t_row("Private Notes" , $answers{'private_notes'});
    }

  }

sub db_connectify {
        # Please to be connecting to the database 
        # and putting handle for connectionage
        # into $dbh; 
        $dbh = DBI->connect("DBI:Pg:dbname=skyline")
                || die ("Can't connect to database $!\n");
        }

sub fetch_quals {
	# Subroutine to get the qualifications 
	# That $input has. 
  my $input = shift; 
  my $answer; 
  my $get_info = $dbh->prepare(
	qq(select role_name, expires, expiration_date from quals where handle='$input' and is_qualified=TRUE)); 
  $get_info->execute(); 
  my $count=0;
  while ( my $row = $get_info->fetchrow_hashref ) {
    $answer .= sprintf (qq(<img src="/INCLUDES/Qual-Icons/%s" alt="%s" width="70" height="70" onmouseover="Tip('%s')" onmouseout="UnTip('')">&nbsp), 
	$quals{$row->{'role_name'}}{'img'}, 
	$quals{$row->{'role_name'}}{'desc'},
	$quals{$row->{'role_name'}}{'desc'}
	);
    if ($count++ % 5 == 4) {
      $answer .= "<br>\n"; 
      }
    }
  $answer;
  }

sub fetch_admins {
        # Fetch an assoc.array of people in the access table
        # who have 't' for edit_members. 
        # If they can edit members, 
        # then they can edit bios too.
  my %answer;
  my $get_info = $dbh->prepare(
        qq(select handle from access where edit_member=true));
  $get_info->execute();

  while ( my $row = $get_info->fetchrow_hashref ) {
    $answer{$row->{'handle'}}= 1;
    }
  %answer;
  }


sub t_row {
  my ($answer) = "<tr>";
  my($count);
  my ($align);
  for (@_) {
    $align = 'left';
    if ($count % 2 == 0) {
      $align = 'right';
      }
    $answer .= "\t<td align = \"$align\">" . $_ . "&nbsp;</td>\n";
    $count++;
    }
  $answer .="</tr>\n";
  print $answer;
  }

sub include {
	# Include left menu and such.
  my($file) = shift;
  open (INCLUDE, "../INCLUDES/" . $file)
	|| die ("Can't include left menu! $!\n");
  for (<INCLUDE>) {
    print;
    }
  close (INCLUDE);
  }

sub read_from_db {
  my $handle = shift;
  my %answer;
  my $dbh = DBI->connect("DBI:Pg:dbname=skyline")
	|| die ("Can't connect to database $!\n");
  my $get_info = $dbh->prepare("Select * from Members " . 
	"where handle = '$handle';");
  $get_info->execute();
  while ( my $row = $get_info->fetchrow_hashref ) {
    %answer=%{$row};
    }

  my ($get_info) = $dbh->prepare("Select handle, lastupdated from bios where handle='$handle'"); 
  $get_info->execute();
  while (my $row = $get_info->fetchrow_hashref ) {
    if ($row->{'handle'} eq $handle) {
      $answer{'bio_online'}=1;
      $answer{'bio_updated_on'}=$row->{'lastupdated'};
      }
    }
  $dbh->disconnect();
  %answer;
  }




__END__

address1 => 2451 Midtown Avenue #310
address2 =>
ado => 1
bio_online => 0
cell_phone =>
city => Alexandria
country =>
director => 0
dutyofficer => 0
email => ganthony91@aol.com
firstname => Geoffrey
glider_owned =>
glider_owned2 =>
handle => ganthony
instructor => 0
joindate => June 20, 2007
lastname => Anthony
lastupdated => 1188755202
mailinglist => 0
md5_password => $apr1$CD6FmZ6z$CDu2FC9AOkgUSeutNvxpQ.
memberstatus => P
middleinitial =>
misc_list => 1
mugshot => 0
namesuffix =>
newsletter => 1
official_title =>
otherduties => 0
phone1 => 760-586-8764
phone2 =>
private_notes => Became a probationary member on July 21, 2007.
public_notes =>
rating => S
rostername =>
secretary => 0
ssa_id => 573848
state => VA
towpilot => 0
treasurer => 0
webmaster => 0
weekday_list => 1
zip => 22303

  %member_labels = (
        'M'     =>      'Standard Member',
        'F'     =>      "Founding Member",
        'P'     =>      'Probationary Member',
        'S'     =>      'Service Member',
        'H'     =>      'Honorary Member',
        'Q'     =>      'Family Member',
        'T'     =>      'Transient Member',
        'I'     =>      'Inactive Member',
        'E'     =>      'Introductory Member',
        'N'     =>      'Not a Member'
        );

# Argh, all that code I just can't stand to look at anymore. 


sub Init {
	# I want output immediately. 
	# No output buffers, please. 
  $|++;
  use CGI;
  $q=new CGI;
  }

	# If the viewer of this 
	# page has write access, as determined
	# by the ok_access.pl program,
	# you get the option of updating dude. 

sub print_form {
  if (system ("/home/httpd/bin/ok_access.pl " .  
	$ENV{REMOTE_USER} .  
	' edit_member quiet') == 0) {
    $edit = qq([ <a href = "/ADMIN/editmember2.cgi?$handle">Update this Member</a> ]<br>);
    }
  else {
    $edit = '';
    }

  print <<EOM;
<h1>Member Manager:</h1>
<div><dd><h2>View Member Information</h2></div>
<table border = 1 bgcolor = "#E0E0E0">
<caption align = top>
$edit
[ <a href = "/MEMBERSHIP/">Back to Members List</a> ]<br>
$back_cap
</caption>

EOM


	# Special considerations if dude has a 
	# middle initial, like making spaces and such. 

  if($q->param("middleinitial") =~ /\w/) {
    $middleinitial = $q->param("middleinitial") . '.';
    }

  #$mugshot = '';
  #if ($q->param('mugshot')) {
    #$mugshot = sprintf ('<a href = "/SNAPSHOTS/index.cgi?mode=search&searchstring=%s
#"><img src = "mugshot.png" border="0" width="45" height="36"
#align = "absmiddle">', 
	#$q->param('lastname'));
    #}

  print ("<tr><td colspan = 2 align = \"right\"><font size=+2><b>",
	join " ", (
	$q->param("firstname"), 
	$middleinitial,
	$q->param("lastname"),
	$q->param("namesuffix"),
        $mugshot), 
	"</td></tr>\n");
	
	# If dude has an address line 2,
	# Make special considerations for it, 
	# Like putting a line-break where appropriate.


  if ($q->param('address2') =~ /\w/) {
    t_row ("Address", 
	$q->param("address1") . "<br>" . 
	$q->param("address2") . "<br>" . 
	$q->param('city') . ", " . 
	$q->param('state') . " " . 
	$q->param('zip')
	);
    }

  else {
    t_row ("Address", 
	$q->param("address1") . "<br>" . 
	$q->param('city') . ", " . 
	$q->param('state') . " " . 
	$q->param('zip')
	);
    }

  t_row ("Club Title/Position", $q->param("official_title") || "&nbsp;");

  if ($q->param("email") ne "none") {
    t_row ("Email", 		qq(<a href = "mailto:) . 
	$q->param("email") . qq(">) . 
	$q->param("email") . qq(</a>));
    }

  else {
    t_row ("Email", 		"<i>None</i>");
    }

  if ($q->param("cell_phone") =~ /\d/) {
    $q->param("cell_phone", $q->param("cell_phone") . " <i>(cell)</i> ");
    }

  t_row ("Phone", 		$q->param("phone1") . "<br>" .  
				$q->param("phone2") . "<br>" .
				$q->param("cell_phone"));
  %rating_labels = (
	'S'	=>	"Student",
	'CPL'	=>	'Commercial',
	'PPL'	=> 	'Private',
	'CFIG'	=>	'Instructor',
	'F'	=>	'Foreign',
	'N/A'	=>	'N/A or Other'
	);
  t_row ("Glider Rating", 	$rating_labels{$q->param("rating")});
  if ($q->param('ssa_id')) {
    t_row ("SSA Member Number", 	$q->param("ssa_id"));
    }

  %member_labels = (
	'M'	=>	'Standard Member',
	'F'	=>	"Founding Member",
	'P'	=> 	'Probationary Member',
	'S'	=> 	'Service Member',
	'H'	=>	'Honorary Member',
	'Q'	=>	'Family Member',
	'T'	=>	'Transient Member',
	'I'	=>	'Inactive Member',
	'E'	=>	'Introductory Member',
	'N'	=>	'Not a Member'
	);

  t_row ("Membership Status", $member_labels{$q->param("memberstatus")});

	# Instead of me typing that URL for the <img>
	# tag for each of these if statements, 
	# I'm going to put the <img> tag 
	# in this asssociative array. 

  %yes_no = (
	"0" => qq(<img src = "/IMAGES/ecks.png" width = 16 height = 16>),
	"1" => qq(<img src = "/IMAGES/check.png" width = 16 height = 16>),
	);

  print <<EOM;
<tr>
<td align = right>Duties</td>
<td align = center>
<table border = 0 bgcolor = "#FFFFFF">
<tr>
  <td><font size=-1>Dir</font></td>
  <td><font size=-1>Tow</font></td>
  <td><font size=-1>Inst</font></td>
  <td><font size=-1>DO</font></td>
  <td><font size=-1>ADO</font></td>
  <td><font size=-1>Oth</font></td>
</tr>
<tr>
EOM

	# Print an X or a check 
	# based off of what this guy can do.

  for (qw(director towpilot instructor dutyofficer ado otherduties)) {
    printf "<td>%s</td>\n",
	$yes_no{$q->param($_)};
    }
  print "</table>\n\n";

  t_row ("Glider Owned", 	
	$q->param("glider_owned") || "&nbsp;");

	# If dude owns two gliders, 
	# make special considerations.

  if ($q->param('glider_owned2')) {
  t_row ("Second Glider Owned", 	
	$q->param("glider_owned2"));
    }


	# Convert string of numbers in last updated field
	# to a sensible string. 
	
  if ($q->param("lastupdated")) {
    $Lu = scalar(localtime($q->param("lastupdated")));
    }

  t_row ("Last Updated",
	'<font face="Helvetica"><b>'. $Lu  . "&nbsp;</b></font>");
  t_row ("Joined Club", $q->param("joindate") || "&nbsp;");

  if ($q->param('secretary') eq '1') {
    print "<tr><td colspan = 2 align = center>" .
	"<i>Club Secretary</i></td></tr>\n";
    }

  if ($q->param('treasurer') eq '1') {
    print "<tr><td colspan = 2 align = center>" .
	"<i>Club Treasurer</i></td></tr>\n";
    }

  if ($q->param('webmaster') eq '1'){
    print "<tr><td colspan = 2 align = center>" .
	"<i>Club Webmaster</i></td></tr>\n";
    }

  if ($q->param('public_notes')) {
    print "<tr><td colspan = 2 bgcolor = \"#F8eeee\" align =\"center\"><p><b>Notes:</b> ".
	$q->param('public_notes') . "</p></td></tr>";
    }

  print "</table>";
  }





