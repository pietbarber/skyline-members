#!/usr/bin/perl 
	# A simple program to show what is in logsheet_verbose

use strict;
	# We gonna use the DB
use DBI;
	# We gonna use CGI
use CGI qw/:standard/; 
my ($dbh);

#############################
#   Debugging!   
#############################

#my ($DEBUG) = 1; # I need more output 
my ($DEBUG) = 0; # Shut yer mouth, i don't want you yappin about everything. 
	# Comment out whichever above is less appropriate. 



	# If we had a logsheet uploaded here, then do this stuff. 
if (param('date') ne /\w/) {
	# On the off chance that this was an upload with the 
	# upload field, convert it into the logsheet_contents variable. 
  show_logsheet(param('date'), param('submit_time'));
  exit;
  }

else {
  print header();
  start_html('Logsheet Search');
  print include('left-menu.scrap');
  print h2(qq(Show Uploaded Logsheets));
  show_verbose_logsheet_list();
  print include('footer.scrap');
  exit;
  }


#########################################
#     Subroutines!
#########################################

sub show_logsheet {
	# Can take one or two params
	# only one param? Just show a list of all the logsheets for that day. 
	# Two params? Show the actual contents of the logsheet. 
  my $input_date=shift; 
  my $submit_date=shift; 
  if ($submit_date !~ /\w/) {
    print header();
    start_html('Logsheets for $input_date');
    print include('left-menu.scrap'); 
    if ($input_date !~ /^\d{4}\-\d{2}\-\d{2}$/) {
      print "Not a valid input date. \n";
      }
    else {
      db_connectify(); 
      print qq(<table border="1">); 
      my (@bgcolor)=('#FFFFFF', '#E8E8E8');
      my ($get_info); 
      print h2("Logsheets for $input_date");
      print qq(<a href="?">Return to Logsheet List</a>\n);  
    print qq(<br><a href="/LOGSHEET/">Return to Logsheets page</a>\n);
      print qq(<tr bgcolor="#C8C8C8"><td><b>Submitter</b></td><td><b>Submit Time</b></td></tr>); 
      my ($sql) = qq(select handle, submit_time from logsheet_verbose where logsheet_date = '$input_date' order by submit_time desc);
      my ($get_info) = $dbh->prepare($sql); 
      $get_info->execute();
      my $count;
      use URI::Escape;
      while (my $ans=$get_info->fetchrow_hashref()) {
        $count++;
        my $bgcolor=($bgcolor[$count % 2]); 
        printf (qq(<tr bgcolor="$bgcolor"><td>%s</td><td><a href="?date=%s&submit_time=%s">%s</a></td></tr>\n), 
		who_dat($ans->{'handle'}), 
		$input_date, 
		uri_escape($ans->{'submit_time'}), 
		$ans->{'submit_time'}, 
		);
        }
      print qq(</table>); 
      }
    print include('footer.scrap'); 
    } 

  else {
    print header('text/plain');
    my ($get_info); 
    db_connectify(); 
    my ($sql) = qq(select logsheet_contents from logsheet_verbose where logsheet_date = '$input_date' and submit_time='$submit_date' );
    my ($get_info) = $dbh->prepare($sql); 
    $get_info->execute();
    my $count;
    while (my $ans=$get_info->fetchrow_hashref()) {
      print $ans->{'logsheet_contents'}, 
      }
    }
  }

sub handle_search {
  	# do a select for this handle, 
	# return 1 if it exists, 
	# return 0 if it doesn't. 
  my ($input) = shift;
  my ($answer);
  warn(" Doing this here SQL: select handle for members where handle ='$input'") if $DEBUG;
  my($get_info) = $dbh->prepare("select handle from members where handle ='$input'");
  $get_info->execute();
  while (my $ans = $get_info->fetchrow_hashref()) {
    $answer = $ans->{'handle'};
    }
  if ($answer > 0) {
    return 1;
    }
  else {
    return 0;
    }
  0;
  }

sub who_dat {
	# Give me a handle, I'll give you his name. 
  my ($input) = shift; 
  my ($answer); 
  #if (! handle_search($input)) {
    #return $input;
    #}
  my($get_info) = $dbh->prepare("select firstname, middleinitial, lastname, namesuffix from members where handle ='$input'");
  $get_info->execute();
  while (my $ans = $get_info->fetchrow_hashref()) {
    $answer = sprintf("%s %s %s %s", 
	$ans->{'firstname'}, 
 	$ans->{'middleinitial'}, 
	$ans->{'lastname'}, 
	$ans->{'namesuffix'}
	); 
    }
  $answer; 
  }

sub show_verbose_logsheet_list {
	# Print out a pretty table with hyperlinks
	# the pretty table has all of the days of operation
	# along with a list of how many logsheets were uploaded 
	# for each day. 
  db_connectify(); 
  print qq(<table border="1" cellspacing="2" cellpadding="1">); 
  my (@bgcolor)=('#FFFFFF', '#E8E8E8');
  my ($get_info); 
  my ($limit_number)=50;
  if (param('unlimited') eq 'on'){
    $limit_number=3000;
    print qq(All results are shown. <a href="?">Show only 50 logsheets</a>\n);
    print qq(<br><a href="/LOGSHEET/">Return to Logsheets page</a>\n);
    }
  else {
    print qq(First 50 results are shown. <a href="?unlimited=on">Show all logsheets</a>\n);
    print qq(<br><a href="/LOGSHEET/">Return to Logsheets page</a>\n);
    }
  print qq(<tr bgcolor="#C8C8C8"><td><b>Date</b></td><td><b>Count</b></td><td><b>Operations</b></tr>); 
  my ($sql) = qq(select logsheet_date, count(*) as number from logsheet_verbose group by logsheet_date order by logsheet_date desc limit $limit_number);
  my ($get_info) = $dbh->prepare($sql); 
  $get_info->execute();
  my $count;
  use URI::Escape;
  while (my $ans=$get_info->fetchrow_hashref()) {
    $count++;
    my $bgcolor=($bgcolor[$count % 2]); 
    printf (qq(<tr bgcolor="$bgcolor"><td><a href="?date=%s">%s</a></td><td align="right"><tt>%d</tt></td><td><a href="/STATS/?date=%s">Summary</a></td></tr>\n), 
	$ans->{'logsheet_date'}, 
	$ans->{'logsheet_date'}, 
	$ans->{'number'},
	uri_escape($ans->{'logsheet_date'}), 
	);
    }
  print qq(</table>); 
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



