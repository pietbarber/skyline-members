#!/usr/bin/perl

main: {
  Init();
  print $q->header;
  if ($q->param) {
    sanitize_data();
    if (scalar(@error)) {
      present_error();
      }
    else {
      insert_into_db();
      mail_welcome_page();
      }
    }
  else {
    print <<EOM;
<html>
  <head>
    <title>Member Manager: Insert Member</title>
EOM
    include("left-menu.scrap");
    }
  print_form();
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
    'cell_phone' => 1,
    'address2' => 1,
    'phone2' => 1,
    'middleinitial' => 1,
    'namesuffix' => 1,
    'official_title' => 1,
    'glider_owned' => 1,
    'glider_owned2' => 1,
    'misc_list' => 1,
    'military_rank' => 1,
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
  }

sub print_form {
  print <<EOM;
<h1>Member Manager:</h1>
<div><dd><h2>Insert User Information</h2></div>
<table border = 1 bgcolor = "#E0E0E0">
<!--starting t-row-->
EOM
  print $q->start_form;

  t_row ("SSA Number", 
	$q->textfield(
	  -name => "ssa_id",	
	  -size => 10,
	  -maxlength => 10,
	  -default => 0
	  )
	);


#  t_row ("Military Rank (opt)", 
#	$q->textfield(
#	  -name => "military_rank",	
#	  -size => 20,
#	  -maxlength => 20
#	  )
#	);


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

  t_row ("Middle Initial <br>(only if needed for uniqueness)", 
	$q->textfield(
	  -name => "middleinitial",
	  -size => 1, 
	  -maxlength => '1'
	  )
	);

  t_row ("Name Suffix <br>(only if needed for uniqueness)", 
	$q->textfield(
	  -name => "namesuffix",
	  -size => '4', 
	  -maxlength => '4'
	  )
	);



  t_row ("Club Title/Position", 
	$q->textfield(
	  -name => "official_title",
	  -size => '30', 
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

  t_row ("Email<br>(If absent, please leave blank)", 
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
	'P'	=> 	'Probationary Member',
	'M'	=>	'Standard Member',
	'F'	=>	"Founding Member",
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
	  -values => ['P','M','F','H','Q','T','I','N','E'],
	  -labels => \%member_labels
	  )
	);

  %yes_no = (
	"0" => "No",
	"1" => "Yes"
	);

  #t_row ("Receives Paper Newsletter?", 
	#$q->popup_menu(
	  #-name => "newsletter",
	  #-values => ['0', '1'],
	  #-labels => \%yes_no,
	  #-default => '1'
	  #)
	#);


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

  t_row ("Other Duties", 
	$q->popup_menu(
	  -name => "otherduties",
	  -values => ['0', '1'],
	  -labels => \%yes_no
	  )
	);

#  t_row ("Subscribe to misc?", 
#	$q->popup_menu(
#	  -name => "misc_list",
#	  -values => ['1', '0'],
#	  -labels => \%yes_no
#	  )
#	);

  t_row ("Subscribe to weekday list?", 
	$q->popup_menu(
	  -name => "weekday_list",
	  -values => ['1', '0'],
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

  t_row ("Second Glider Owned", 
	$q->textfield(
	  -name => "glider_owned2",
	  -size => 20, 
	  -maxlength => '30'
	  )
	);

  t_row ("Joined Club", 
        $q->textfield(
          -name => "joindate",
          -size => 20, 
          -maxlength => '30'
          )
        );

  t_row ("Emergency Contact Information", 
        $q->textarea(
          -name => "emergency_contact",
          -rows => 12, 
          -columns => 80
          )
        );


  print "<tr><td colspan = 2>";
  print $q->submit(
	-label => "Insert Member"
	);
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

sub insert_into_db {
  $handle = $q->param("firstname");
  $handle =~ s/^([A-Za-z]).+$/$1/;
  $handle .= $q->param("lastname");
  $handle =~ tr/A-Z/a-z/;
  $handle =~ s/\s$//g;
  use DBI;
  $driver = "DBI::Pg";
  $database = 'skyline';
  $dbh = DBI->connect("DBI:Pg:dbname=skyline")
	|| die ("Can't connect to database $!\n");

  while (!$unique_Handle) {
    $check_handle = 
	$dbh->prepare("Select handle from members where handle = '$handle';");
    $check_handle->execute();
    local($fetchrow) = 0;
    while (my $ref = $check_handle->fetchrow_hashref()) {
      $fetchrow++;
      }
    if (!$fetchrow) {
      $unique_Handle = 1;
      }
    else {
      if ($handle =~ /\D$/) {
        $handle.="1";
        }
      else {
        $handle++;
        }
      }
    }

  $check_duplicate = 
	$dbh->prepare("Select handle from members where ".
	"lastname = '" . $q->param("lastname") . "' and " . 
	"firstname = '" . $q->param("firstname") . "' and ".
	"namesuffix = '" . $q->param("namesuffix") . "'");
  $check_duplicate->execute();
  local($fetchrow) = 0;
  while (my $ref = $check_duplicate->fetchrow_hashref()) {
    $fetchrow++;
    }
  if ($fetchrow) {
    $error[0] = "User last and first names are already in Database. Do you want to modify instead?";
    }

  if (@error) {
#    $check_duplicate->finish;
#    $dbh->disconnect();
    present_error();
    print_form();
    exit;
    }


  print <<EOM;
<html>
  <head>
    <title>Member Manager: Insert Member</title>
EOM
  include ("left-menu.scrap");
  print ("insert into members values (" . ultra_join() . ");");
  $insert_new = $dbh->prepare("insert into members values (" . ultra_join() . ");");
  if ($insert_new->execute()) {
    print "<h2>User added.</h2>";
    print "<p>View Database to see the user you just added. " . 
	'[<a href = "/MEMBERSHIP/">Go</a>]' . "</p>";
    print "<p>Add another user" . 
 	'[<a href = "?">Go</a>]' . "</p>";
    print ("insert into members values (" . ultra_join() . ");");

    }
  else {
    $error[0] = "Unable to insert information into database. Tell the webmaster. Show him this: <br>\n".
	"<pre>insert into members values (" . ultra_join() . ")</pre>";
    }
#  $check_handle->finish;
#  $dbh->disconnect();
  include ("footer.scrap");
  system ("/home/httpd/bin/pwgen.pl");
  exit;
  };

sub ultra_join {
  local $answer;
  $q->param("handle", $handle);
  $q->param("roster_name", $q->param("lastname"));
  $q->param("misc_list", '1');
  if ($q->param('mailinglist') eq "") {
    $q->param("mailinglist", '0');
    }
  if ($q->param('ssa_id') ne /^\d+$/) {
    $q->param("ssa_id", 0);
    }

  if ($q->param('bio_online') eq "") {
    $q->param("bio_online", '0');
    }

  if ($q->param('mugshot') eq "") {
    $q->param("mugshot", '0');
    }
  if ($q->param('mailinglist') eq "") {
    $q->param("mailinglist", '1');
    }

  $q->param('newsletter', 0);
  $q->param("lastupdated", time);
  $q->param("lastupdated", time);
  $q->param("md5_password", '!!');
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
	mugshot		public_notes
	private_notes	cell_phone
	emergency_contact
	)) {


    if ($q->param($_) =~ /\'/) {
      local ($temp) = $q->param($_);
      $temp =~ s/'/\\'/g;
      $q->param($_, $temp);
      }

    printf "<!-- $_ => '%s' -->\n", $q->param($_);
    if ($answer) {
      $answer .= ", '" . $q->param($_) . "'";
      }
    else {
      $answer .= "'" . $q->param($_) . "'";
      }
    }
  $answer;
  }


sub mail_welcome_page {
  	# Page that allows for a new member to get the welcome
	# E-mail
  $email = $q->param('email');
  $fname = $q->param('firstname');
    
  }

__END__
  print t_row ();

  print t_row ("foo", "bar");
  print t_row ();
  print t_row ("First Name", 
	$q->textfield(
	  -name => "FirstName",	
	  -size => 20,
	  -maxlength => 20
	  )
	);

  print t_row ("Address Line 1", 
	$q->textfield(
	  -name => "Address1",	
	  -size => 50,
	  -maxlength => 50
	  )
	);

  print t_row ("Address Line 2", 
	$q->textfield(
	  -name => "Address2",	
	  -size => 50,
	  -maxlength => 50
	  )
	);
  print t_row ("foo", "bar");

