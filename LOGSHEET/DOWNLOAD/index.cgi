#!/usr/bin/perl 
	# Simple program to take the existing logsheet zipfile from Jon Kans
	# and insertify the appropriate .txt files, sub directories
	# and create a modern members.txt file
	# and create a modern tempmemb.txt file
	# and include the last 30 days worth of the last logsheet uploaded
	# and make it easy for the dude to download the logsheet
	# without having to past in text files and whatnot. 

	# We've needed this functionality for a while. :( 


use strict;
	# We gonna use the DB
use DBI;
	# We gonna use CGI
use CGI qw/:standard/; 

#############################
#   Debugging!   
#############################

my ($DEBUG) = 1; # I need more output 
#my ($DEBUG) = 0; # Shut yer mouth, i don't want you yappin about everything. 
	# Comment out whichever above is less appropriate. 

my ($dbh); # Database handle 
my (%working_dir);
$working_dir{'pc'}='/var/www/members/html/LOGSHEET/.WORKING/PC'; 
$working_dir{'mac'}='/var/www/members/html/LOGSHEET/.WORKING/MAC'; 



sub the_main: {
  db_connectify();
  print header();
  start_html( 'Download Logsheet Program');
  print include('left-menu.scrap');
  print h2(qq(Download Logsheet Program));
  print p(qq(Download the logsheet program, with the latest information about club members, prices, etc.)); 
  gliders_output("$working_dir{'pc'}/ssclog/tables/gliders.txt"); 
  members_output("$working_dir{'pc'}/ssclog/tables/members.txt"); 
  tempmembers_output("$working_dir{'pc'}/ssclog/tables/tempmemb.txt"); 
  gliders_output("$working_dir{'mac'}/ssclog/tables/gliders.txt"); 
  members_output("$working_dir{'mac'}/ssclog/tables/members.txt"); 
  tempmembers_output("$working_dir{'mac'}/ssclog/tables/tempmemb.txt"); 
  old_logs();
  zip_up_directory('pc');
  print qq(<li><a href="/LOGSHEET/.WORKING/PC/ssclog.zip">Download Logsheet Program for MS Windows or Linux</a>); 
  make_some_hash('pc'); 
  make_working_hash('pc'); 
  zip_up_directory('mac');
  make_some_hash('mac'); 
  print qq(<li><a href="/LOGSHEET/.WORKING/MAC/ssclog.zip">Download Logsheet Program for MAC</a>); 
  make_working_hash('mac'); 
  print qq(</ul><p>Supported Operating systems: Anything later than Windows 95, anything later than Mac OS X (even the older ones might work, too), any version of Linux (or FreeBSD running the Linux emulator). );
  
  print include('footer.scrap');
  exit;
  }

the_main();


#########################################
#     Subroutines!
#########################################

sub fetch_owners {
	# Input: glider name
	# output: array of real names of people who own this glider.
  my $input=shift;
  my (@answer); 
  my (%members) = fetch_member_handles();
  my $sql = qq(select 
	handle
	from logsheet_glider_owners where glider_name='$input');
  my($get_info) = $dbh->prepare($sql); 
  $get_info->execute();
  while (my $ans = $get_info->fetchrow_hashref()) {
    push (@answer, $members{$ans->{'handle'}});
    }
  @answer; 
  }

sub gliders_output {
	# New! (2012-11-13)
	# Output gliders.txt in following format: 
	# - glider name, registration, rental per minute, rental per flight, number of seats, max time charged per day, fly for free owners
	# All that gunk is in a table 
  my ($filename) = shift; 
  open (OUTFILE, ">$filename") || die ("Unable to write to $filename! $!\n"); 
  my $date = scalar localtime(time); 
  my $user = $ENV{'REMOTE_USER'}; 
  print OUTFILE qq(- glider name, registration, rental per minute, rental per flight, number of seats, max time charged per day, fly for free owners
- Automatically generated by $user on $date UTC
);
  my $sql = qq(select 
	glider_name, registration, rental_per_minute, rental_per_flight, number_of_seats, max_time_charged_per_day, owners
	from logsheet_gliders ORDER BY rental_per_minute DESC);
  my($get_info) = $dbh->prepare($sql); 
  $get_info->execute();
  while (my $ans = $get_info->fetchrow_hashref()) {
    my (@owners); 
    if ($ans->{'owners'} == 1) {
      @owners = fetch_owners($ans->{'glider_name'}); 
      }

    printf OUTFILE ("%s\t%s\t%4.2f\t%s\t%s\t%s\t%5.5s\r\n", 
	$ans->{'glider_name'},
	$ans->{'registration'},
	$ans->{'rental_per_minute'},
	$ans->{'rental_per_flight'},
	$ans->{'number_of_seats'},
	$ans->{'max_time_charged_per_day'},
	join (', ', @owners)
	);
    }

  close (OUTFILE); 
  }

sub fetch_member_handles {
        # Fetch an assoc.array of members.
  my %answer;
  my $status = shift;
  my $row;
  my ($append);
  if ($status eq 'active') {
    $append=qq(where memberstatus != 'I' and memberstatus !='N' );
    }
  my $get_info = $dbh->prepare(
        qq(select handle, lastname, firstname, middleinitial, memberstatus, namesuffix from members $append));
  $get_info->execute();

  while ( my $row = $get_info->fetchrow_hashref ) {
    $answer{$row->{'handle'}}= sprintf ("%s %s",
        $row->{'firstname'},
	$row->{'lastname'},
	);
    }
  %answer;
  }

sub members_output {
	# in members.txt, we have a file that has the dude's name
	# followed by a tab, 
	# followed by a list of his jobs concatenated together. 
	# Piet Barber\tI
	# Craig Bendorf\tCT
	# See the first print OUTFILE statement to understand what 
	# each letter represents. 

  my ($filename) = shift; 
  open (OUTFILE, ">$filename") || die ("Unable to write to $filename! $!\n"); 
  my $date = scalar localtime(time); 
  my $user = $ENV{'REMOTE_USER'}; 
  print OUTFILE qq(- member name, job
- A assistant duty officer, C commercial demo pilot, D duty officer,
- I instructor, T towpilot, P provisional member, S service member
- Automatically generated by $user on $date UTC
);
  my $sql = qq(select 
	handle, firstname, lastname, namesuffix, dutyofficer, ado, rating, instructor, towpilot, memberstatus
	from members
	where memberstatus != 'N' and memberstatus !='I'
	order by LastName, FirstName);
  my($get_info) = $dbh->prepare($sql); 
  $get_info->execute();
  while (my $ans = $get_info->fetchrow_hashref()) {
    my ($jobs); 

    if ($ans->{'instructor'} == 1) {
      $jobs .= "D";
      $jobs .= "I";
      }
    if ($ans->{'towpilot'} ==1 ) {
      $jobs .= "T";
      }
    if ($ans->{'dutyofficer'} == 1) {
      $jobs .= "D"; 
      $jobs .= "A"; 
      }
    if ($ans->{'memberstatus'} eq 'E') {
      $jobs .= "P"; 
      }
    if ($ans->{'ado'} == 1) {
      $jobs .= "D";
      $jobs .= "A"; 
      }
    if ($ans->{'rating'} eq 'CPL') {
      #$jobs .= "C";
      #	# We recently decided that we don't want commercial pilots
      #	showing up as instructors in the instructor pull down list. 
      }
    my ($firstname);  
    $firstname=$ans->{'firstname'}; 
    if ($ans->{'middleinitial'} =~ /\w/) { 
      $firstname .= " " . $ans->{'middleinitial'}; 
      }
      
    my ($lastname);  
    $lastname=$ans->{'lastname'}; 
    if ($ans->{'namesuffix'} =~ /\w/) {
      $lastname .= " " . $ans->{'namesuffix'}; 
      }

    printf OUTFILE ("%s %s\t%s\n", 
	$firstname,
	$lastname,
	$jobs
	);
    }
  print OUTFILE "N/A Self-Launch	T"; 
  close (OUTFILE); 
  } 

sub tempmembers_output { 
  my (%answer); 
  my ($filename) = shift; 
  open (OUTFILE, ">$filename") || die ("Unable to write to $filename! $!\n"); 
  my $date = scalar localtime(time); 
  my $user = $ENV{'REMOTE_USER'}; 
  print OUTFILE qq(- Temporary Members list. Format: 
- name, last valid date
- Automatically generated by $user on $date UTC
); 

  my $sql = qq( set DateStyle TO 'SQL, YMD'; select members.firstname, members.middleinitial, members.lastname, members.namesuffix, members.handle, (new_contacts.join_date + 30) as valid_till from new_contacts inner join members on members.handle = new_contacts.handle where new_contacts.join_date < CURRENT_DATE and members.memberstatus='T' or members.memberstatus='E'
	order by members.LastName, members.FirstName);
  my($get_info) = $dbh->prepare($sql); 
  $get_info->execute();
  while (my $ans = $get_info->fetchrow_hashref()) {
    my ($firstname, $lastname); 
    $firstname=$ans->{'firstname'}; 
    if ($ans->{'middleinitial'} =~ /\w/) { 
      $firstname .= " " . $ans->{'middleinitial'}; 
      }
      
    $lastname=$ans->{'lastname'}; 
    if ($ans->{'namesuffix'} =~ /\w/) {
      $lastname .= " " . $ans->{'namesuffix'}; 
      }

    printf OUTFILE ("%s %s\t%s\n", 
	$firstname,
	$lastname, 
	$ans->{'valid_till'}
	);
     }
  close (OUTFILE); 
	# Since we did that set DateStyle above, I would rather
	# just disconnect, and reconnect, to revert any of the 
	# SET commands used above. 
  $dbh->disconnect();
  db_connectify(); 
  }

sub make_working_hash {
  my $input=shift;  
  my $tables=$working_dir{$input} . '/ssclog/tables'; 
  chdir ($tables) || die ("Can't chdir to that dir $tables $!\n"); 
  system ('/usr/bin/sha1sum *.txt >checksums.txt'); 
  } 

sub make_some_hash {
	# From:  Ertan Tete
	# 11:09 PM (11 hours ago)
	# to Piet 
	# Could you generate in the same location where ssclog.zip is generated a file, say ssclog.zip.hash,
	# containing a hash of the content of ssclog.zip. This file would have to be regenerated every time ssclog.zip is generated
	# Git uses sha1 for file content hash, but for a small file like ssclog.zip md5 should be ok.
	# One question is what would trigger the hash file generation? If I understand correctly ssclog.zip is
	# created on demand (i.e. when somebody hits the ssclog.zip link).

	# sha1sum has same effect as 'openssl sha1', except sha1sum has the filename following the output
  my $input=shift;  
  chdir ($working_dir{$input}) || die ("Can't chdir to that dir $input $!\n"); 
  open (SHAOUT, ">ssclog.zip.hash"); 
  open (SHA, "-|") ||
	exec ('/usr/bin/sha1sum', 'ssclog.zip'); 
  while (my $line = <SHA> ){
    print SHAOUT $line . "\n"; 
    } 
  close (SHAOUT); 
  close (SHA); 
  } 

sub zip_up_directory {
  my $input=shift; 
  print p(qq(Zipping up directory for $input...))  if $DEBUG; 
  chdir ($working_dir{$input}) || die ("Can't chdir to that dir $input $!\n"); 
  open (ZIP, "-|") || 
	exec ('/usr/bin/zip', '-r', 'ssclog.zip', 'ssclog'); 
  while (my $line=<ZIP>) { 
    print $line . "<br>\n" if $DEBUG; 
    } 
  close (ZIP); 
  } 

sub include {
        # Pull file from the INCLUDES directory
        # output of subroutine is that file.
  my $file = shift;
  my $answer;
  my ($dir, $fulldir);
  use Cwd;
  $fulldir=getcwd;
  $dir = 'skyline' if ($fulldir =~ m#/var/www/skyline#);
  warn ("The pwd is $fulldir\n") if $DEBUG;
  $dir ||= 'members';
  open (INCLUDE, "/var/www/$dir/html/INCLUDES/$file") || print "Can't open that file $!";
  while (my $line = <INCLUDE>) {
    $answer .= $line;
    }
  close (INCLUDE);
  $answer;
  }

sub db_connectify {
        # Just connect to the database.
  my $driver = "DBI:Pg";
  my $database = 'skyline';
  $dbh = DBI->connect("$driver:dbname=$database")
        || error_out ("Can't connect to $driver database $database $!\n");
  }


sub old_logs { 
	# This subroutine populates the logs directory with the last 20 operations days
	# worth of logsheets.  First we have to destroy the old logs in the directory
	
	# First, destroy obsolete logsheet cruft hanging around in those directories... 
  for my $dir ('mac', 'pc') {
    opendir (DIR, $working_dir{$dir} . '/ssclog/logs/'); 
    for my $file (readdir (DIR)) {
      next if $file eq '..' or $file eq '.'; 
      unlink ($working_dir{$dir} . '/ssclog/logs/' . $file) || warn "Unable to unlink pc log files... $! " . $working_dir{$dir} . "/ssclog/logs/$file" . "\n";
      }
    }


  my ($answer);
  my (@logsheet_days, %logsheet_days);
  if (!$dbh) {
    db_connectify();
    }

	# Then we have to get the last 20 logsheet days of operation from the database, 
	# and the latest submitted data for that logsheet for that date. 
	# Put everything into %logsheet_days; 
  my($get_info) = $dbh->prepare(qq(
	select logsheet_date, max(submit_time) as submit_time
		from logsheet_verbose 
		group by logsheet_date 
		order by logsheet_date desc 
		limit 20
		));

  $get_info->execute();
  while (my $ans = $get_info->fetchrow_hashref()) {
    $logsheet_days{$ans->{'logsheet_date'}} = $ans->{'submit_time'};
    }

	# Now that we have all of the logsheet date names in %logsheet_days, 
	# let's do a database hit for each one of those days, and find out what the 
	
  for my $date (keys %logsheet_days) { 
    $get_info = $dbh->prepare(qq(select max(submit_time) as submit_time from logsheet_verbose where logsheet_date='$date'));
    $get_info->execute();
    while (my $ans = $get_info->fetchrow_hashref()) {
      $logsheet_days{$date}=$ans->{'submit_time'};
      }
    }
  for my $date (keys %logsheet_days) { 
    my ($filename) = $working_dir{'pc'} . '/ssclog/logs/' . $date . '.txt'; 
    open (OUTFILE1, ">$filename") ||
	die ("Not able to write to (pc) $filename"); 
    my ($filename) = $working_dir{'mac'} . '/ssclog/logs/' . $date . '.txt'; 
    open (OUTFILE2, ">$filename") ||
	die ("Not able to write to (mac) $filename"); 

    $get_info = $dbh->prepare(qq(select logsheet_contents from logsheet_verbose 
	where logsheet_date='$date' and submit_time='$logsheet_days{$date}'));
    $get_info->execute();
    while (my $ans = $get_info->fetchrow_hashref()) {
      print OUTFILE1 $ans->{'logsheet_contents'};
      print OUTFILE2 $ans->{'logsheet_contents'};
      }
    close(OUTFILE1); 
    close(OUTFILE2); 
    }

  }

__END__

skyline=> \d logsheet_verbose
               Table "public.logsheet_verbose"
      Column       |            Type             | Modifiers
-------------------+-----------------------------+-----------
 handle            | character varying(20)       | not null
 submit_time       | timestamp without time zone | not null
 logsheet_date     | date                        | not null
 logsheet_contents | character varying           | not null

skyline=> \q



#!/usr/bin/php -q 
- member name, job
- A assistant duty officer, C commercial demo pilot, D duty officer,
- I instructor, T towpilot, S service member
<?
$sql = "select firstname, lastname, namesuffix, dutyofficer, ado, rating, instructor, towpilot from Members
	where memberstatus != 'N' and memberstatus !='I'
	order by LastName, FirstName";

$db = pg_Connect("dbname=skyline");

if (!$db) {
  echo "Connection to database failed. ";
  exit;
  }

$result = pg_Exec($db, $sql);
$num = pg_numrows($result);
for ($i=0; $i<$num; $i++) {
  $row = pg_fetch_row($result, $i, 1);
  $jobs='';
  if ($row['instructor'] == 't') {
    $jobs = "I";
    }
  if ($row['towpilot'] == 't') {
    $jobs .= "T";
    }
  if ($row['dutyofficer'] == 't' or $row['lastname'] =='Kellett') {
    $jobs .= "D"; 
    }
  if ($row['ado'] == 't') {
    $jobs .= "A"; 
    }
  if ($row['rating'] == 'CPL') {
    $jobs .= "C";
    }


  print $row['firstname'] . " " . $row['lastname'] . " " . $row['namesuffix'] . "\t" . $jobs . "\n";
  } 
?>
#!/usr/bin/php -q 
- name, last valid date
<?
$sql = "set DateStyle TO 'SQL, YMD'; select members.firstname, members.middleinitial, members.lastname, members.namesuffix, members.handle, (new_contacts.join_date + 30) as valid_till from new_contacts inner join members on members.handle = new_contacts.handle where new_contacts.join_date < CURRENT_DATE and members.memberstatus='T' or members.memberstatus='E'"; 

$db = pg_Connect("dbname=skyline");

if (!$db) {
  echo "Connection to database failed. ";
  exit;
  }

$result = pg_Exec($db, $sql);
$num = pg_numrows($result);




$result = pg_Exec($db, $sql);
$num = pg_numrows($result);
for  ($i=0; $i<$num; $i++) {
  $row = pg_fetch_row($result, $i, 1);
  if ($row['namesuffix'] != '' && $row['namesuffix'] != ' ') { 
    print $row['firstname'] . " " . $row['lastname'] . " " . $row['namesuffix'] . "\t" .  $row['valid_till'] . "\n";
    }
  else {
    print $row['firstname'] . " " . $row['lastname'] . "\t" .  $row['valid_till'] . "\n";
    }
  } 
?>
