#!/usr/bin/perl

use CGI qw(:standard);  # Talk to the CGI stream
use DBI;                # Allows access to DB functions
use strict;             # Create extra hoops to jump through
use URI::Escape;	# Make words URI-safe

			# Comment out the less appropriate of these two: 
my ($DEBUG)=0; 		# Shut yer mouth with yer whinin' 
my ($DEBUG)=1; 		# Be verbose with your whining
my ($dbh); 
start_page("Badge Board");
print p(qq(
<p>Badges shown here are gathered according to the SSA's master badge database and foreign badges earned.  If you see an issue with the A, B, C, or Bronze badges not listed here that needs correcting, please contact the Skyline <a href="mailto:pbarber\@skylinesoaring.org">Chief Flight Instructor</a> first.   </p>

<p>Check out the <a href="http://ssa.org/members/badgesandrecords/USBadges.asp">SSA Website</a> for the official issuance of badges</P>

If you see an issue with Silver badges or above, please contact both the webmaster as well as <a href="mailto:badgeandrecords\@ssa.org">badgeandrecords\@ssa.org</a>. 
)); 
print p(qq(This page is updated quarterly... more or less)); 
show_badge_board(); 
end_page();
exit; 


sub connectify {
	# Just connect to the database. 
  my $driver = "DBI::Pg";
  my $database = 'skyline';
  $dbh = DBI->connect("DBI:Pg:dbname=skyline")
        || die ("Can't connect to database $!\n");
  }

sub start_page {
	# Prints the starting information for the page
	# Like the HTML headers, the DOCtypes,
	# The left-menu-headers, etc.
	# We basically just include the left-menu.scrap
  my $title = shift;
  my $header = shift;
  $title ||= "Badge Board";
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
  print mini_javascript(); 
  print h1($title);
  }

sub end_page {
  print include('footer.scrap');
  exit;
  }

sub include {
	# Pull file from the INCLUDES directory
	# output of subroutine is that file.
  my $file = shift;
  my $title = shift;
  my $answer;
  open (INCLUDE, "/var/www/members/html/INCLUDES/$file") || print "Can't open that file $!";
  while (my $line = <INCLUDE>) {
    $answer .= $line;
    }
  close (INCLUDE);
  $answer;
  }

sub mini_javascript {
  my $answer =<<EOM;
<!--ToolTip headers-->
<script language="JavaScript" type="text/javascript" src="/INCLUDES/wz_tooltip.js"></script>
<!--Spr specific headers-->
<script language="JavaScript" type="text/javascript" src="/INCLUDES/spr_header.js"></script>
EOM
  $answer;
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

sub show_badge_board { 
	# 
  connectify();           # Connect to DB

  my (%badges) = (
 	'A' => '/images/A-Badge.png',  
	'B' => '/images/B-Badge.png',  
	'C' => '/images/C-Badge.png', 
 	'Bronze Badge' => '/images/Bronze%20Badge.png', 
 	'Silver Badge' => '/images/Silver%20Badge.png',
 	'Gold Badge' => '/images/Gold%20Badge.png', 
 	'Diamond Badge' => '/images/Diamond%20Badge.png', 
	);

  my (@badge_order) = ( 
 	'A',
	'B',
	'C',
 	'Bronze Badge',
 	'Silver Badge',
 	'Silver Altitude',
 	'Silver Distance',
 	'Silver Duration',
 	'Gold Altitude',
 	'Gold Distance',
 	'Gold Badge',
 	'Diamond Altitude',
 	'Diamond Distance',
 	'Diamond Badge',
 	'Diamond Goal',
	); 

  my($order, $members_list)=please_to_fetching(
	qq(
	  select members.handle, members.firstname, members.middleinitial, 
	  members.lastname, members.namesuffix, badge_link.url 
	  from badge_link inner join members on members.handle = badge_link.handle 
	  where members.memberstatus != 'T' 
		and members.memberstatus != 'I' 
		and members.memberstatus != 'N' 
	  order by members.lastname, members.firstname),
	'handle', 'firstname', 'middleinitial', 'lastname', 'namesuffix', 'url'
	);

  my($order, $active_members)=please_to_fetching(
	qq(
	  select members.handle, members.firstname, members.middleinitial, 
	  members.lastname, members.namesuffix
	  from members 
	  where members.memberstatus != 'T' 
		and members.memberstatus != 'I' 
		and members.memberstatus != 'N' 
	  order by members.lastname, members.firstname),
	'handle', 'firstname', 'middleinitial', 'lastname', 'namesuffix'
	);
  my ($throwaway, $has_he_soloed)=please_to_fetching(
     "select flight_info.pilot as handle, count(*) as solo_count from flight_info inner join members on flight_info.pilot = members.handle
	where flight_info.instructor ='' 
		and flight_info.passenger='' 
		or (members.rating !='S'
		and members.rating !='N/A')
	group by flight_info.pilot",
	'handle', 'solo_count'
	);
  my (@order) = @{$order}; 
  my (%members_list) = %{$members_list};
  my (%active_members) = %{$active_members};
  my (%has_he_soloed) = %{$has_he_soloed};
  
  print qq(<table border="1" style="background-color : #F8F8F8">\n);
  for my $handle (@order) { 

    if (! $has_he_soloed{$handle}{'solo_count'} && ! exists ($members_list{$handle}{'url'})) {
      printf (qq(<tr><td>%s %s %s %s</td><td>No Rating, Never Soloed</td></tr>\n),
	$active_members{$handle}{'firstname'},
	$active_members{$handle}{'middleinitial'},
	$active_members{$handle}{'lastname'},
	$active_members{$handle}{'namesuffix'},
	$has_he_soloed{$handle}{'handle'},
	$has_he_soloed{$handle}{'solo_count'}
	);
      }
    elsif (! exists ($members_list{$handle}{'url'})) {
      printf (qq(<tr><td>%s %s %s %s</td><td>Should have something [<a href="http://ssa.org/members/badgesandrecords/USBadges.asp?badge=1&first=%s&last=%s&issued=0&action=+OK+" target=SSA>Check SSA</a>]</td></tr>\n),
	$active_members{$handle}{'firstname'},
	$active_members{$handle}{'middleinitial'},
	$active_members{$handle}{'lastname'},
	$active_members{$handle}{'namesuffix'},
	uri_escape($active_members{$handle}{'firstname'}),
	uri_escape($active_members{$handle}{'lastname'}),
	);
      }
    elsif ($members_list{$handle}{'url'} ne '') { 
      printf (qq(<tr><td><a href = "%s" target="SSA">%s %s %s %s</a></td><td>\n),
	$members_list{$handle}{'url'}, 
	$members_list{$handle}{'firstname'}, 
	$members_list{$handle}{'middleinitial'}, 
	$members_list{$handle}{'lastname'}, 
	$members_list{$handle}{'namesuffix'}, 
	);

      print qq(<table border="0">); 
      my ($order, $badges_earned)= please_to_fetching(
	sprintf (qq(select badge, earned_date from badges_earned where handle='%s'), $handle),
	'badge', 'earned_date'
	);
      my (%badges_earned) = %{$badges_earned};

      for my $badge (@badge_order) {
        if ($badges_earned{'Silver Badge'}{'badge'}) {
          delete ($badges_earned{'Silver Distance'}{'badge'});
          delete ($badges_earned{'Silver Altitude'}{'badge'});
          delete ($badges_earned{'Silver Duration'}{'badge'});
          }

        if ($badges_earned{'Gold Badge'}{'badge'}) {
          delete ($badges_earned{'Gold Distance'}{'badge'});
          delete ($badges_earned{'Gold Altitude'}{'badge'});
          delete ($badges_earned{'Gold Distance'}{'badge'});
          }

        if ($badges{$badges_earned{$badge}{'badge'}}) {
          printf (qq(<td align="center" valign="top"><img src="%s" alt="%s" width="50"><br>%s<br><font size="-1">%s</font>\n), 
		$badges{$badges_earned{$badge}{'badge'}},
		$badges_earned{$badge}{'badge'}, 
		$badges_earned{$badge}{'badge'}, 
		$badges_earned{$badge}{'earned_date'}
		);
          }
        elsif ($badges_earned{$badge}{'badge'}) { 
          printf (qq(<td>%s<br>%s\n</td>\n), 
		$badges_earned{$badge}{'badge'}, 
		$badges_earned{$badge}{'earned_date'}
		);
          }

        }
      print qq(</table>\n); 
      }
    }
  print qq(</table>\n);
  } 

sub please_to_fetching {
	# Take string as input
	# Take array of the labels you want 
	# send that sql string to db 
	# Get output 
	# throw output into %answer array with @whatchuwant as keys, in order
	# don't be cute, just be easy and simple. 
  my ($sql) = shift; 
  my (@whatchuwant) = @_; 
  my ($key_on) = $whatchuwant[0]; 
  my (@order); 
  my (%answer); 
    my $get_info = $dbh->prepare($sql);
  $get_info->execute();
  while (my $ans = $get_info->fetchrow_hashref) {
    push (@order, $ans->{$key_on}); 
    for my $key (@whatchuwant) { 
      $answer{$ans->{$key_on}}{$key} = $ans->{$key}; 
      } 
    }
  (\@order, \%answer); 
  } 


__END__
