#!/usr/bin/perl

	# I hate this program and want to re-write it so that:
	# it doesn't make me nervous with all these database writes. 
	# it uses strict. 

main: {
  Init();
  if (!$edit_ok) {
    print $q->redirect("/ERROR/no-access.shtml");
    }
  elsif ($q->param('keywords')) {
    print $q->header;
    read_from_db($q->param('keywords'));
    include ("left-menu.scrap");
    print_form();
    include ("footer.scrap");
    }

  elsif ($q->param('m')) {
    print $q->header;
    read_from_db($q->param('m'));
    include ("left-menu.scrap");
    print_form();
    include ("footer.scrap");
    }
  elsif ($q->param('submit') eq 'Update Member') {
    print $q->header;
    insert_into_db();
    }

  elsif ($q->param('submit') eq 'Reset Password') {
    print $q->header;
	warn "Resetting Password Screen\n" if $DEBUG;
    reset_password();
    }

  elsif ($q->param('delete') eq 'Delete Member!') {
    print $q->header;
    remove_from_db();    
    }
  else {
    print $q->redirect("/MEMBERSHIP/");
    }
  };

sub present_error {
    print <<EOM;
<html>
  <head>
    <title>Member Manager: Bad Input</title>
EOM
  include("left-menu.scrap");
  print <<EOM;
<table border = 2 bgcolor = "#FFD0D0">
<tr><td colspan = 2><h1>Input Errors</h1></td></tr>
EOM
  for (@error) {
    t_row ("&nbsp;", $_ );
    }
  print "</table>";
  }

sub sanitize_data {
  local(%okay_to_skip) = (
    'address2' => 1,
    'phone2' => 1,
    'middleinitial' => 1,
    'namesuffix' => 1,
    'official_title' => 1,
    'glider_owned' => 1,
    'glider_owned2' => 1
    );
  for ($q->param) {
    if ($q->param($_) eq ""
	&& $okay_to_skip{$_} != 1) {
      $error[$errorcount++] = "Missing Required Field: $_<br>";
      }
    }
  }

sub Init {
  $|++;
  use CGI;
  $q=new CGI;
  if (system ("/home/httpd/bin/ok_access.pl " .
        $ENV{REMOTE_USER} .  
        ' edit_member quiet') == 0) {
    $edit_ok = 1;
    }
  else {
    $edit_ok = 0;
    }  
  }

sub print_form {
  print <<EOM;
<h1>Member Manager:</h1>
<div><dd><h2>Update User Information</h2></div>
<table border = 1 bgcolor = "#E0E0E0">
<caption align = top>
[ <a href = "/MEMBERSHIP/viewmember2.cgi?$handle">View this Member</a> ] <br>
[ <a href = "/MEMBERSHIP/">Back to Member List</a> ] 
</caption>
<!--starting t-row-->
EOM
  print $q->start_form;

  t_row ("handle" . $q->hidden('handle'), 
	'&nbsp;<font face="Helvetica"><b>'. $handle . "</b></font>");

  t_row ("SSA Member Number", 
	$q->textfield(
	  -name => "ssa_id",	
	  -size => 11,
	  -maxlength => 11
	  )
	);

  t_row ("Last Name", 
	$q->textfield(
	  -name => "lastname",	
	  -size => 20,
	  -maxlength => 20
	  )
	);

  t_row ("First Name", 
	$q->textfield(
	  -name => "firstname",	
	  -size => 20,
	  -maxlength => 20
	  )
	);

  t_row ("Middle Initial", 
	$q->textfield(
	  -name => "middleinitial",
	  -size => 1, 
	  -maxlength => '1'
	  )
	);

  t_row ("Name Suffix", 
	$q->textfield(
	  -name => "namesuffix",
	  -size => '4', 
	  -maxlength => '4'
	  )
	);

  t_row ("Club Title/Position", 
	$q->textfield(
	  -name => "official_title",
	  -size => '20', 
	  -maxlength => '50'
	  )
	);

  t_row ("Address Line 1", 
	$q->textfield(
	  -name => "address1",	
	  -size => 50,
	  -maxlength => 50
	  )
	);

  t_row ("Address Line 2", 
	$q->textfield(
	  -name => "address2",	
	  -size => 50,
	  -maxlength => 50
	  )
	);

  t_row ("City", 
	$q->textfield(
	  -name => "city",	
	  -size => 20,
	  -maxlength => 20
	  )
	);

  t_row ("State", 
	$q->textfield(
	  -name => "state",	
	  -size => 2,
	  -maxlength => 2
	  )
	);

  t_row ("Zip", 
	$q->textfield(
	  -name => "zip",
	  -size => 10,
	  -maxlength => 10
	  )
	);

  t_row ("Email", 
	$q->textfield(
	  -name => "email",
	  -size => 40,
	  -maxlength => 128
	  )
	);

  t_row ("Phone 1", 
	$q->textfield(
	  -name => "phone1",
	  -size => 12,
	  -maxlength => 12
	  )
	);

  t_row ("Phone 2", 
	$q->textfield(
	  -name => "phone2",
	  -size => 12,
	  -maxlength => 12
	  )
	);
  
  t_row ("Cell Phone", 
	$q->textfield(
	  -name => "cell_phone",
	  -size => 12,
	  -maxlength => 12
	  )
	);

  %rating_labels = (
	'S'	=>	"Student",
	'CPL'	=>	'Commercial',
	'PPL'	=> 	'Private',
	'CFIG'	=>	'Instructor',
	'F'	=>	'Foreign',
	'N/A'	=>	'N/A or Other'
	);


  t_row ("Glider Rating", 
	$q->popup_menu(
	  -name => "rating",
	  -values => ['S','PPL','CPL','CFIG','F','N/A'],
	  -labels => \%rating_labels
	  )
	);

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

  t_row ("Membership Status", 
	$q->popup_menu(
	  -name => "memberstatus",
	  -values => ['M','F','P','S','H','Q','T','I', 'N', 'E'],
	  -labels => \%member_labels
	  )
	);

  %yes_no = (
	"0" => "No",
	"1" => "Yes"
	);


  t_row ("Director?", 
	$q->popup_menu(
	  -name => "director",
	  -values => ['0', '1'],
	  -labels => \%yes_no
	  )
	);

  t_row ("Towpilot?", 
	$q->popup_menu(
	  -name => "towpilot",
	  -values => ['0', '1'],
	  -labels => \%yes_no
	  )
	);

  t_row ("Instructor?", 
	$q->popup_menu(
	  -name => "instructor",
	  -values => ['0', '1'],
	  -labels => \%yes_no
	  )
	);

  t_row ("Duty Officer?", 
	$q->popup_menu(
	  -name => "dutyofficer",
	  -values => ['0', '1'],
	  -labels => \%yes_no
	  )
	);

  t_row ("Asst. Duty Officer?", 
	$q->popup_menu(
	  -name => "ado",
	  -values => ['0', '1'],
	  -labels => \%yes_no
	  )
	);

  t_row ("Other Duties?", 
	$q->popup_menu(
	  -name => "otherduties",
	  -values => ['0', '1'],
	  -labels => \%yes_no
	  )
	);

  t_row ("Stay Subscribed to Members List?", 
	$q->popup_menu(
	  -name => "mailinglist",
	  -values => ['0', '1'],
	  -labels => \%yes_no
	  ) . 
	"(Only applicable if member is inactive)"
	);

  t_row ("Subscribe to Misc?", 
	$q->hidden(
	  -name => "misc_list",
	  -value => '1'
	  ). "(Obsolete)"
	);


  t_row ("Subscribe to Weekday List?", 
	$q->hidden(
	  -name => "weekday_list",
	  -value => '1',
	  ) . "(Obsolete)"
	);

  t_row ("Is his bio online?", 
	$q->hidden(
	  -name => "bio_online",
	  -value => '1',
	  ) . "(Obsolete)"
	);


  t_row ("Is his mugshot available?", 
	$q->popup_menu(
	  -name => "mugshot",
	  -values => ['0', '1'],
	  -labels => \%yes_no
	  )
	);

  t_row ("Secretary?",
        $q->popup_menu(
          -name => "secretary",
          -values => ['1', '0'],  
          -labels => \%yes_no,   
          -default => '0'
          )
        ); 

  t_row ("Treasurer?",
        $q->popup_menu(
          -name => "treasurer",
          -values => ['1', '0'],
          -labels => \%yes_no,    
          -default => '0'
          )
        ); 

  t_row ("Webmaster?",
        $q->popup_menu(
          -name => "webmaster",
          -values => ['1', '0'],
          -labels => \%yes_no,  
          -default => '0'
          )
        ); 

  t_row ("Glider Owned", 
	$q->textfield(
	  -name => "glider_owned",
	  -size => 20, 
	  -maxlength => '30'
	  )
	);

  t_row ("Second Glider", 
	$q->textfield(
	  -name => "glider_owned2",
	  -size => 20, 
	  -maxlength => '30'
	  )
	);

  if ($q->param("lastupdated")) {
    $Lu = scalar(localtime($q->param("lastupdated")));
    }

  t_row ("Last Updated" . $q->hidden("lastupdated"), 
	'&nbsp;<font face="Helvetica"><b>'. $Lu  . "</b></font>");

  t_row ("Joined Club", 
	$q->textfield(
	  -name => "joindate",
	  -size => 20, 
	  -maxlength => '30'
	  )
	);


  t_row ("Emergency Contact Information</i>", 
	$q->textarea(
	  -name => "emergency_contact",
	  -columns => 50, 
	  -rows => 6, 
	  )
	);


  t_row ("Public Notes <br><i>(Viewable by any Club Member)</i>", 
	$q->textarea(
	  -name => "public_notes",
	  -columns => 50, 
	  )
	);

  t_row ("Private Notes<br><i>(Viewable only by Membership Weenie and Webmaster)</i>", 
	$q->textarea(
	  -name => "private_notes",
	  -columns => 50, 
	  )
	);

  print "<tr><td colspan = 2 align = \"center\">";
  print $q->submit(
	-name => "submit",
	-label => "Update Member"
	);
  print "</td></tr>";
  print "<tr><td colspan=2><br><br><br><br></td></tr>\n";
  print "<tr><td colspan = 2 bgcolor = \"#888800\" align = \"center\">";
  print $q->submit(
	-name => "submit",
	-label => "Reset Password"
	);
  print "<tr><td colspan=2><br><br><br><br></td></tr>\n";
  print "<tr><td colspan = 2 bgcolor = \"#FF0000\" align = \"center\">";
  print $q->submit(
	-name => "delete",
	-label => "Delete Member!"
	) . "<br><b>Warning!</b> There's no back-out for this procedure!";
  print "</td></tr>";
  print "</table>";
  include ("footer.scrap");
  }

sub t_row {
  $answer = "<tr>";
  local($count);
  for (@_) {
    local ($align) = 'left';
    if ($count % 2 == 0) {
      $align = 'right';
      }
    $answer .= "\t<td align = \"$align\">" . $_ . "</td>\n";
    $count++;
    }
  $answer .="</tr>\n";
  print $answer;
  }

sub include {
  local($file) = shift;
  open (INCLUDE, "../INCLUDES/" . $file)
	|| die ("Can't include left menu! $!\n");
  for (<INCLUDE>) {
    print;
    }
  close (INCLUDE);
  }

sub read_from_db {

  @structure = (qw(
        handle          ssa_id
        firstname       lastname
        middleinitial   namesuffix
        official_title  rostername
        address1        address2
        city            state
        zip             country
        email           phone1
        phone2          director
        treasurer       secretary
        webmaster       instructor
        towpilot        dutyofficer
        ado             otherduties
        memberstatus    rating
        glider_owned    glider_owned2
        joindate        lastupdated
        md5_password    newsletter
        mailinglist     misc_list
        weekday_list    bio_online
	mugshot		public_notes
	private_notes	cell_phone
	emergency_contact
	));

  $handle ||= shift;

  use DBI;
  $driver = "DBI::Pg";
  $database = 'skyline';

  $dbh = DBI->connect("DBI:Pg:dbname=skyline")
	|| die ("Can't connect to database $!\n");

  $get_info = $dbh->prepare("Select * from Members " . 
	"where handle = '$handle';");

#  print ("Select * from Members " . 
#	"where handle = '$handle'");

  $get_info->execute();

  while ( @row = $get_info->fetchrow_array ) {
    for (0..$#row) {
      $q->param($structure[$_], $row[$_]);
      }
    }
#  $dbh->disconnect();
  }

sub remove_from_db {

  print <<EOM;
<html>
  <head>
    <title>Member Manager: Delete Member</title>
EOM
  include ("left-menu.scrap");

  for ($q->param) {
    $entered_value{$_} = $q->param($_);
    }
  $handle = $q->param('handle');
  $q->delete_all();
  $q->param('keywords', $handle);
  read_from_db();
  $handle = $q->param('handle');

  for (keys %entered_value) {
    if ($entered_value{$_} ne $q->param($_)) {
      next if /submit/;
      $updated{$_} = $entered_value{$_};
      printf "$entered_value{$_}: <b>" . $q->param($_);
      print "</b><br>";
      }
    }
  if (!$handle) {
    print "</table>";
    exit;
    }

  print("<BR>delete from members where handle = '$handle';");
  $dbh->do("delete from members where handle = '$handle';");
    
    print "<h2>User Deleted.</h2>";
    print "<p>Add a new user " . 
	'[<a href = "/ADMIN/newmember2.cgi">Go</a>]' . "</p>";
    $get_info->finish;
    $dbh->disconnect();

  include ("footer.scrap");
  exit;
  }

sub generate_random_pw {
  $user = $ENV{'REMOTE_USER'};
  use Crypt::PasswdMD5;
  @allow_chars = ('a'..'z', 0..9, 'A'..'Z', '.');
  @pw_chars = (0..9, 'A'..'Z');
  for (1..11) {
    $salt .= $allow_chars[int(rand($#allow_chars))];
    }
  for (1..8) {
    $random_pw .= $pw_chars[int(rand($#pw_chars))];
    }
  $entered_value{'md5_password'} = apache_md5_crypt($random_pw, $salt);
  }

sub e_mail_password {
  $name=$q->param('firstname') . " "  . $q->param('lastname');
  $email_to=$q->param('email');
  $handle=$q->param('handle');
  system ("/home/httpd/bin/pwgen.pl");
  local($sendmail) = '/usr/sbin/sendmail';
  $message = sprintf <<EOM, $name, $email_to, $random_pw, $handle;
From: Skyline Webmasters <webmaster\@skylinesoaring.org>
To: %s <%s>
Subject: Password Reset

Please note that the password you use to log into the members-only
portion of the Skyline Soaring Club's website has been reset. 

New Password:
%s

Note that the password contains no lower-case characters. 

Please use the userid '%s' and the password presented above
to log into the Skyline Soaring Club's website.

Please change this password to something more memorable to you 
by going to:

http://members.skylinesoaring.org/MEMBERSHIP/account/


-----------------------------------------------------------------

If you see any information that we have about you that is incorrect, 
please notify the Membermeister at welcome\@skylinesoaring.org.  There 
is currently no way for you to update that information. 
-----------------------------------------------------------------

Notes to Introductory Members: 
Welcome!  You've probably had your first introduction to Skyline
Soaring Club in the past few days.  A part of the introductory
membership is access to the club website during the time that you 
are an introductory member. If you choose to convert your introductory
membership into a full membership, great!  If not, we are happy to have 
met you, and hope to see you again in the future.  If you have any
feedback about your experience at Skyline, (good or bad), please
write a note to welcome\@skylinesoaring.org.
-----------------------------------------------------------------

Notes about E-mail Lists: 
All active and introductory members are automatically subscribed to 
the members mailing list.  The content on the mailing list is limited 
to information about the club's activities and upcoming events. Once
you stop being an active member or introductory member, you are 
automatically unsubscribed from the mailing lists. The content of what
is sent to the members mailing list is not moderated, and will
be sent to the membership within about 5 minutes of sending a note to
members\@skylinesoaring.org

Separate from our members mailing list is the monthly newsletter, 
"Skylines".  We send out an announcement of each month's issue, usually 
right at the beginning of the month.  Anybody can subscribe to the 
newsletter announcement list by sending an email to 
newsletter-announce-subscribe\@skylinesoaring.org
-----------------------------------------------------------------

Notes about the Student Progress Reports
Whether you are a student pilot or a rated glider pilot, you will 
find the instructor's records of your flights in the STUDENTS link
on the members-only section of the website.  The depth of detail
available to you on your progress toward solo is unrivaled by any
other soaring establishment in the country (or maybe the world). 
If you have questions about any of your instruction reports, or how
the system works, please write to instructors\@skylinesoaring.org  

At that part of the website, you can also see a list of all the 
flights you have had at Skyline Soaring Club, along with a list of 
each area of instruction you will have to learn before soloing or 
getting a rating Students are highly encouraged to read through all 
of the sample lesson plans, and do their bookwork before showing 
up at the field for flight instruction. 
-----------------------------------------------------------------

Notes about Spam and Email:
We have lots of filters to prevent spam from getting to the members
lists, instructors lists, or any of our mailing lists.  The 
automated systems we have in place filter out approximately 200-300
spams sent to the membership per day.  (yes, really)

Some things to keep of note: 
1) Sending attachments that are XLS, DOC, or other rich formats will 
be discarded without telling you it was rejected (due to a huge number 
of viruses that propagate through email attachments of complex formats). 

2) Sending emails to the mailing lists from an email address that we 
don't know about will probably be rejected, or held for moderation 
until a webmaster can manually figure out if the email is a spam or not. 
Once the webmaster approves a message from you to a mailing list, you 
won't have your mail held up for approval again. There is no spam
filtering for emails sent to the webmasters.

3) We have a lot of mailing lists outside of the members list. 
Guidlines to posting to the lists are found here: 
http://members.skylinesoaring.org/MEMBERSHIP/mailing-lists.shtml

-----------------------------------------------------------------

Biographies On-line:
You can view the biographies members have posted, so you can help to 
get to know them better.  How better for members to get to know you
than to have you post a bio about yourself?  The biographies are only 
viewable by Skyline Soaring Club members.  The interface to create 
your biography is quite simple to use. Introductory members aren't
expected to post a biography, but you can still snoop around and read
the other people's articles about themselves. 
Find the biographies of club members by going to: 
http://members.skylinesoaring.org/BIOS/
-----------------------------------------------------------------

Notes about Duty:
Introductory members are NOT expected to perform any specific duties
with the club.  However, if you convert to a full member, there are 
some duty dates that will be assigned to you, based on your experience
levels. This is not a commercial operation, and relies on volunteer
work to help keep it running.  This is how we keep the flying so 
affordable.  Most introductory members start out as an Assistant Duty 
Officer (ADO). Please read the Operations Manual for details on these 
roles: Section 1.1 Member Responsibilities of our Operations Manual
http://members.skylinesoaring.org/docs/Manuals_OperationsManual.pdf

The Duty Roster is mailed out every Tuesday, and is available on 
the public-facing portion of the Skyline Soaring Club website. 




EOM
  
  open (SENDMAIL, "|-")
	|| exec ($sendmail, '-t', '-oi');
  print SENDMAIL $message;
  close (SENDMAIL);
  

  $message = sprintf <<EOM, $handle, $handle;
From: Skyline Webmasters <webmaster\@skylinesoaring.org>
To: Skyline Webmasters <webmaster\@skylinesoaring.org>
Subject: Password Reset '%s'


Automated message:

Please note that the password for %s has been reset and 
mailed to that person. 

EOM

  open (SENDMAIL, "|-")
	|| exec ($sendmail, '-t', '-oi');
  print SENDMAIL $message;
  close (SENDMAIL);

  }

sub write_pw_file {
  system ("/home/httpd/bin/pwgen.pl");
  }

sub reset_password {

  print <<EOM;
<html>
  <head>
    <title>Member Manager: Password Reset</title>
EOM
  include ("left-menu.scrap");

  for ($q->param) {
    $entered_value{$_} = $q->param($_);
    }
  $handle = $q->param('handle');
  $q->delete_all();
  $q->param('keywords', $handle);
  read_from_db();
  generate_random_pw();
  $handle = $q->param('handle');
  for (keys %entered_value) {
    if ($entered_value{$_} ne $q->param($_)) {
      next if /submit/;
      $updated{$_} = $entered_value{$_};
      printf "$entered_value{$_}: <b>" . $q->param($_);
      print "</b><br>";
      }
    }
  warn "Got this far. \n" if $DEBUG;
  print "Handle is '$handle'" if $DEBUG;
  if (!$handle) {
    print "</table>";
    exit;
    }
  print("update Members set " . update_join() . " where handle = '$handle';");
  $dbh->do("update Members set " . update_join() . " where handle = '$handle';");
    
    print "<h2>User Updated.</h2>";
    print "<p>View Database to see the user you just edited. " . 
	'[<a href = "/MEMBERSHIP/">Go</a>]' . "</p>";
    print "<p>View entry for $handle. " . 
	"[<a href = \"/MEMBERSHIP/viewmember2.cgi?$handle\">Go</a>]</p>";
    print "<p>Add a new user " . 
	'[<a href = "/ADMIN/newmember2.cgi">Go</a>]' . "</p>";

    $get_info->finish;
    $dbh->disconnect();

  write_pw_file();
  e_mail_password ();
  #e_mail_password ($q->param('firstname') . " " . $q->param('lastname'), $q->param('email'), $random_pw);

  include ("footer.scrap");
  exit;

  }




sub insert_into_db {

  print <<EOM;
<html>
  <head>
    <title>Member Manager: Update Member</title>
EOM
  include ("left-menu.scrap");
  print ultra_join();

  for ($q->param) {
    $entered_value{$_} = $q->param($_);
    }
  $handle = $q->param('handle');
  $q->delete_all();
  $q->param('keywords', $handle);
  read_from_db();
  $handle = $q->param('handle');
  for (keys %entered_value) {
    if ($entered_value{$_} ne $q->param($_)) {
      next if /submit/;
      $updated{$_} = $entered_value{$_};
      printf "$entered_value{$_}: <b>" . $q->param($_);
      print "</b><br>";
      }
    }
  warn "Got this far. \n" if $DEBUG;
  print "Handle is '$handle'";
  if (!$handle) {
    print "</table>";
    exit;
    }
  print("update Members set " . update_join() . " where handle = '$handle';");
  $dbh->do("update Members set " . update_join() . " where handle = '$handle';");
    
    print "<h2>User Updated.</h2>";
    print "<p>View Database to see the user you just edited. " . 
	'[<a href = "/MEMBERSHIP/">Go</a>]' . "</p>";
    print "<p>View entry for $handle. " . 
	"[<a href = \"/MEMBERSHIP/viewmember2.cgi?$handle\">Go</a>]</p>";
    print "<p>Add a new user " . 
	'[<a href = "/ADMIN/newmember2.cgi">Go</a>]' . "</p>";
    $get_info->finish;
    $dbh->disconnect();
  include ("footer.scrap");
  exit;
  };

sub update_join {
  local($answer);
  $updated{"lastupdated"} = time unless $random_pw;
  for (keys %updated) {
    if ($answer) {
      $answer .= ", " . $_ . ' = ' . "'" . $updated{$_} . "'";
      }
    else {
      $answer .= $_ . ' = ' . "'" . $updated{$_}. "'";
      }
    }
  $answer;
  }

sub ultra_join {
  local($answer);
  $q->param("lastupdated", time);
  for (qw(
        handle          ssa_id
        firstname       lastname
        middleinitial   namesuffix
        official_title  rostername
        address1        address2
        city            state
        zip             country
        email           phone1
        phone2          director
        treasurer       secretary
        webmaster       instructor
        towpilot        dutyofficer
        ado             otherduties
        memberstatus    rating
        glider_owned    glider_owned2
        joindate        lastupdated
        md5_password    newsletter
        mailinglist     misc_list
        weekday_list    bio_online
	mugshot
	)) {

    #if ($q->param($_) =~ /\'/) {
      #local ($temp) = $q->param($_);
      #$temp =~ s/'/\\'/g;
      #$q->param($_, $temp);
      #}

    if ($answer) {
      $answer .= ", '" . $q->param($_) . "'";
      }
    else {
      $answer .= "'" . $q->param($_) . "'";
      }
    }
  $answer;
  }


__END__
