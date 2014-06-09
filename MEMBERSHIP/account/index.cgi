#!/usr/bin/perl

main: {
  Init();

	# If the username to get to this page
	# exists
	# and both password fields are completed...

  if ($ENV{'REMOTE_USER'} eq 'demo') {
    print "Content-type: text-plain\n\n";
    print "You are a demo user.  You can't change any of this stuff. Go back now.";
    }
  elsif ($ENV{'REMOTE_USER'}
	&&
      $q->param('password1')
	&&
      $q->param('password2')
	) {
    $password1 = $q->param('password1');
    $password2 = $q->param('password2');
    print $q->header;

	# Check database to ensure that user
	# is in the database.

    read_from_db($ENV{'REMOTE_USER'});
    include ("left-menu.scrap");

	# Run check to ensure password passess all checks.
	# If no gripes from password checker, 
    if (!check_pw(
	$password1,
	$password2
	)) {

		# Insert the password into the databse
      insert_password($password1);
		# Write the password file to the .htpasswd
		# file in this directory (for now).
      write_pw_file();
      }

	# Display output
    print_form();
    include ("footer.scrap");
    }


	# If the password fields aren't
	# filled in -- 

  elsif ($ENV{'REMOTE_USER'}) {
    print $q->header;
    read_from_db($ENV{'REMOTE_USER'});
    include ("left-menu.scrap");
	# Tell user what we expect out of
	# a good password
    pw_syntax();
	# Just show the page with the password 
	# fields, along with his user information.
    print_form();
    include ("footer.scrap");
    }

	# If there is no REMOTE User
	# environment variable, something
	# screwey has happend, so we redirect
	# the screwball to the Member Maintenance page.
  else {
    print $q->redirect("/MEMBERSHIP/");
    }
  };

sub Init {
  $|++;
  use CGI;
  $q=new CGI;
  }

sub pw_syntax {
  print <<EOM;
<table bgcolor = "#7777e7" border = 1>
<tr>
  <td><h1><font color = "#FFFFFF">Password</font></h1></td>
  <td><font color = "#FFFFFF">Enter a password for access to member-restricted services to this 
webpage.<br>
This program expects that you enter a good password. A password should follow these criteria:
<ul>
  <li> 8 characters or more
  <li> No words that you would find in a dictionary
  <li> Don't use your username, this is called a 'smoking Joe' or 'easy target'
  <li> At least one character should be something that is not a letter.
  <li> Password generation is case-sensitive
</ul>
</font>
</tr>
</table>

EOM
  }

sub write_pw_file {
  system ('/home/httpd/bin/pwgen.pl');
  print <<EOM;
<table bgcolor = "#88FF88">
<tr>
<td bgcolor = "#FFFFFF"><h1>Result:</h1></td>
<td><font color = "#FFFFFF"><h1>Password successfully 
updated.</h1></td>
</tr>
</table>
EOM
  }

sub insert_password {
  $user = $ENV{'REMOTE_USER'};
  $password = shift;
  use Crypt::PasswdMD5;
  @allow_chars = ('a'..'z', 0..9, 'A'..'Z', '.');
  for (1..8) {
    $salt .= $allow_chars[int(rand($#allow_chars))];
    }
  
  use DBI;
  $driver = "DBI::Pg";
  $database = 'skyline';
  $dbh = DBI->connect("DBI:Pg:dbname=skyline")
	|| die ("Can't connect to database $!\n");
#  $salt = 'jWsRMawx';
#  my( $tmp) = apache_md5_crypt($password, $salt);
#  open( TEMP, '>/usr/tmp/eraseme.SSC'); print TEMP ">$tmp<\n>$salt<\n>$password<"; close TEMP;
  $update = sprintf(
	"update members set md5_password = '%s' where handle = '%s'",
		apache_md5_crypt($password, $salt), 
		$ENV{'REMOTE_USER'}
		);
  $dbh->do($update);
  }

sub check_pw {
  $pw1 = shift;
  $pw2 = shift;

  if ($pw1 ne $pw2) {
    $pwcheck = qq(The passwords you entered don't match.<br>\n);
    }

  if ($pw1 eq $ENV{'REMOTE_USER'}) {
    $pwcheck = qq(You're trying to get my site hacked, aren't you?  Don't use your username as your password!<br>\n);
    }

  if (length($pw1) < 8) {
    $pwcheck .= qq(I require at least 8 characters in your password.<br>\n);
    }

  if ($pw1 !~ /[^a-zA-z]/) {
    $pwcheck .= qq(You need at least one non-alphabetical character. (something that's not a-z)<br>\n);
    }

  for (split (/\W/, $pw1)) {
    $pw_word_count++;
    local($dictwords, $chkpw);
    $chkpw = `grep -i $_ /usr/share/dict/words |wc -l`;
#    open (pwcheck, ">>/tmp/pwchk.out") ; 
#    print pwcheck $_;
#    print pwcheck $chkpw;
#    print pwcheck "\n";
    chomp ($chkpw);
    $dictcount++ if ($chkpw == 1);
    }
  if ($pw_word_count == 1 && $dictcount) {
    $pwcheck .= qq(You chose a word in the dictionary.  Bad form! Be more creative!);
    }

  $pwcheck;
  }

sub print_form {
  print "<dd><h2>Member Maintenance</h2>\n";
  if($pwcheck) {
  print <<EOM;
<table bgcolor = "#FF8888">
<tr>
<td bgcolor = "#FFFFFF"><h1>Result:</h1></td>
<td><font color = "#FFFFFF">
<h2>
$pwcheck
<br>Password NOT updated
</h2></td>
</tr>
</table>
EOM

    }
  $q->delete('password1');
  $q->delete('password2');
  print <<EOM;

<table border = 1 bgcolor = "#E0E0E0">

<!--starting t-row-->
EOM


  if($q->param("middleinitial") =~ /\w/) {
    $middleinitial = $q->param("middleinitial") . '.';
    }

  print ("<tr><td colspan = 2 align = \"right\"><font size=+1><b>",
	join " ", (
	$q->param("military_rank"),
	$q->param("firstname"), 
	$middleinitial,
	$q->param("lastname"),
	$q->param("namesuffix")), 
	"</td></tr>\n");

  if ($q->param('md5_password') eq '') {
    $message = "Password NOT set:<br><i>Enter one now</i>";
    }
  else {
    $message = "Password set:<br><i>To change, enter new Password.</i>";
    }

  print $q->start_form;
  t_row($message,
	$q->password_field(
		-name => 'password1',
		-size => 16,
		-maxlength => 24
		)
	);

  t_row("<i>Enter again</i>",
	$q->password_field(
		-name => 'password2',
		-size => 16,
		-maxlength => 24
		)
	);

  t_row("Commit Password",
	$q->submit(
		-name => '.submit',
		-label => 'Update Password',
		)
	);


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
	'H'	=>	'Honorary Member',
	'Q'	=>	'Family Member',
	'T'	=>	'Transient Member',
	'I'	=>	'Inactive Member',
	'E'	=>	'Temporary Member',
	'N'	=>	'Not a Member'
	);

  t_row ("Membership Status", $member_labels{$q->param("memberstatus")});

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

  for (qw(director towpilot instructor dutyofficer ado otherduties)) {
    printf "<td>%s</td>\n",
	$yes_no{$q->param($_)};
    }
  print "</table>\n\n";

  t_row ("Glider Owned", 	
	$q->param("glider_owned") || "&nbsp;");

  if ($q->param('glider_owned2')) {
  t_row ("Second Glider Owned", 	
	$q->param("glider_owned2"));
    }

  if ($q->param("lastupdated")) {
    $Lu = scalar(localtime($q->param("lastupdated")));
    }

  t_row ("Last Updated",
	'<font face="Helvetica"><b>'. $Lu  . "&nbsp;</b></font>");
  t_row ("Joined Club", $q->param("joindate") || "&nbsp;");

  if ($q->param('public_notes')) {   
    print "<tr><td colspan = 2 align = center>" .
        "<i>Notes:</i><br>". 
	$q->param('public_notes') . 
	"</td></tr>\n";
    }
        
  if ($q->param('secretary') eq '1') {
    print "<tr><td colspan = 2 align = center>" .
        "<i>Club Secretary</i></td></tr>\n";
    }

  if ($q->param('treasurer') eq '1') {
    print "<tr><td colspan = 2 align = center>" .
        "<i>Club Treasurer</i></td></tr>\n";
    }

  if ($q->param('webmaster') eq '1') {
    print "<tr><td colspan = 2 align = center>" .
        "<i>Club Webmaster</i></td></tr>\n";
    }

  print "</table>";
  print qq(<p>Please notify the membership meister of any necessary changes of the above information. 
<a href="mailto:welcome\@skylinesoaring.org">welcome\@skylinesoaring.org</a></p>); 
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
    $answer .= "\t<td align = \"$align\">" . $_ . "&nbsp;</td>\n";
    $count++;
    }
  $answer .="</tr>\n";
  print $answer;
  }

sub include {
  local($file) = shift;
  open (INCLUDE, "../../INCLUDES/" . $file)
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
	));

  $handle ||= $_[0];

  if (!$dbh) {
    use DBI;
    $driver = "DBI::Pg";
    $database = 'skyline';

    $dbh = DBI->connect("DBI:Pg:dbname=skyline")
	|| die ("Can't connect to database $!\n");
    }

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

