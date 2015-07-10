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

my (%quals) =  please_to_fetching_unordered(
      qq(select name, img_url, description, is_qual from endorsement_roles),
        'name', 'img_url', 'description', 'is_qual'
      );

my (%status) = get_member_labels();

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

sub get_member_labels {
  my (%answer);
  my ($sql) = 'select role, role_name from memberstatus';
  my $get_info = $dbh->prepare($sql);
  $get_info->execute();
  while (my $ans = $get_info->fetchrow_hashref) {
    $answer{$ans->{'role'}} = $ans->{'role_name'};
    }
  %answer;
  }

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
  t_row("Phone #1", tel($answers{'phone1'}));
  t_row("Phone #2", tel($answers{'phone2'}));
  t_row("Mobile", tel($answers{'cell_phone'}));
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
    next if user_has_rating($input) && $quals{$row->{'role_name'}}{'description'} =~ /Student/i;
        # If the dude has a rating, don't allow him to get a student endorsement.
    next if ! (user_has_rating($input)) && $quals{$row->{'role_name'}}{'description'} =~ /PIC/i;
        # If the dude is a student, don't allow Quals to include PIC.

    $answer .= sprintf (qq(<img src="/INCLUDES/Qual-Icons/%s" alt="%s" width="70" height="70" onmouseover="Tip('%s')" onmouseout="UnTip('')">&nbsp), 
	$quals{$row->{'role_name'}}{'img_url'}, 
	$quals{$row->{'role_name'}}{'description'},
	$quals{$row->{'role_name'}}{'description'}
	);
    if ($count++ % 5 == 4) {
      $answer .= "<br>\n"; 
      }
    }
  $answer;
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


sub tel {
  my $input = shift; 
  next if $input =~ /href/;
  my $answer=$input;
  $answer=~ s#(.+)#<a href ="tel://$1">$1</a>#;
  $answer;
  }

