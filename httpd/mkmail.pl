#!/usr/bin/perl

main: {
  Init();
  open_db();
  massage_data();
  create_mail();
  };

##################
#   Subroutines  # 
##################

#To: Skyline Membership <pbarber\@skylinesoaring.org>
#Pseudo-To: Skyline Membership <members\@skylinesoaring.org>
#To: Piet Barber <pbarber\@skylinesoaring.org>

sub create_mail {
  use MIME::Base64;
  open (SENDMAIL, "|-") || exec ('/usr/lib/sendmail' , '-t', '-oi');
  print SENDMAIL <<EOM;
From: Chief Roster Manager <roster\@skylinesoaring.org>
X-Mailer: Piet Barber Mailer Made from Perl Program 1.0
X-Accept-Language: en-US
MIME-Version: 1.0
To: Skyline Membership <pb\@pietbarber.com>
Subject: Duty Roster
Content-Type: multipart/alternative;
 boundary="------------AF7713C64D2FED12BEDA245E"


EOM
  print SENDMAIL <<EOM;
--------------AF7713C64D2FED12BEDA245E
Content-Type: text/plain; charset=us-ascii
Content-Transfer-Encoding: base64

EOM
  print SENDMAIL encode_base64($txt);

print SENDMAIL <<EOM;



--------------AF7713C64D2FED12BEDA245E
Content-Type: text/html; charset=us-ascii
Content-Transfer-Encoding: base64

EOM
  print SENDMAIL encode_base64($html);
  print SENDMAIL <<EOM;

--------------AF7713C64D2FED12BEDA245E--


EOM
  close (SENDMAIL);
  }

sub massage_data {
  $today = time - (time %86400);
  $today_date = scalar(localtime(time));
  $txt .= sprintf "The RosterMeister speaks!\n%s\n", 
	$q->param('RosterMeister');

  $rf_says = $q->param('RosterMeister');
  $rf_says =~ s/</&lt;/;
  $rf_says =~ s/>/&gt;/;
  $rf_says =~ s/Rosterf.hrer/RosterMeister/gi;

  $html = <<EOM;
<!doctype html public "-//w3c//dtd html 4.0 transitional//en">
<html>
<body bgcolor = "#FFFFFF">
<table border = 1 align = center>
<caption>Duty Roster Last Updated on $today_date</caption>
EOM

  $html .= sprintf "<tr><td colspan = 7><h1>The RosterMeister ".
	"speaks!</h1></td></tr>\n<tr><td colspan = 7>%s</td></tr>\n", 
	$rf_says;

  dbmopen (%dates, "$dbdir/roster2", 0666)
    || die ("Can't read roster database! $!\n");

  $txt .= sprintf "%8.8s %14.14s %14.14s %14.14s %14.14s %14.14s %14.14s\n%70.70s\n", 
	"", "Towpilot", "Surge Tow", "Instructor", "Surge Inst.", "Duty Officer", "Asst. DO",
	("-" x 70);

  $html .= qq(<tr><td><b>Date</b></td><td><b>Towpilot</b></td><td><b>Surge Tow</b></td><td><b>Instructor</b></td><td><b>Surge Inst</b></td>\n); 
  $html .= qq(<td><b>Duty Officer</b></td><td><b>ADO</b></td></tr>\n); 

  for (sort keys %dates) {
    next if (time > $_);
    @date = gmtime($_);
    $date = ($date[4]+1) . "/" . 
    $date[3] . "/" . sprintf ("%2.2d", (($date[5] +1900) % 100));
    if ($q->param('cancel-' . $_)) {
      $txt .= sprintf "%8.8s %40.40s \n%60.60s\n", 
	 $date,
         "**** Operations canceled ****",
	 $q->param('notes-'. $_);

      $html .= sprintf "<tr>\n<td>%s</td>\n<td colspan=5>%s</td>\n".
	"\n</tr><tr><td></td><td colspan = 4>%s</td>\n</tr>\n", 
	 $date,
         "**** Operations canceled ****",
	 $q->param('notes-'. $_);
      next;
      }
    $txt .= sprintf "%8.8s %14.14s %14.14s %14.14s %14.14s %14.14s %14.14s\n%60.60s\n", 
	$date,
	$q->param('towpilot1-'. $_), 
	$q->param('towpilot2-'. $_), 
	$q->param('instructor-'. $_),
	$q->param('inst2-'. $_),
	$q->param('duty-'. $_),
	$q->param('ados-'. $_),
	$q->param('notes-'. $_);

    if ( $q->param('towpilot1-'. $_) eq "(Unassigned)"
	&&
	$q->param('towpilot2-'. $_) eq "(Unassigned)"
	&&
	$q->param('instructor-'. $_) eq "(Unassigned)"
	&&
	$q->param('inst2-'. $_) eq "(Unassigned)"
	&&
	$q->param('duty-'. $_) eq "(Unassigned)"
	&&
	$q->param('ados-'. $_) eq "(Unassigned)") {
      $unassigned++;
      }

    if ($unassigned >= 6) {
      next;
      }

    #                            date              tow1        tow2         inst1         inst2  
    $html .= sprintf "<tr>\n<td><b>%s</b></td>\n<td>%s</td>\n<td>%s</td> \n<td>%s</td>\n<td>%s</td>\n" . 
    #       duty         ados         (newrow)   (empty)              notes 
	"<td>%s</td>\n<td>%s</td></tr>\n<tr><td></td><td colspan = 6>%s</td></tr>\n",
	$date,
	$q->param('towpilot1-'. $_), 
	$q->param('towpilot2-'. $_), 
	$q->param('instructor-'. $_),
	$q->param('inst2-'. $_),
	$q->param('duty-'. $_),
	$q->param('ados-'. $_),
	$q->param('notes-'. $_);
    }
  $html .= "</table>\n";
  $html .= "</html>\n";
  }

sub open_db {
  open (READ_DB, "$dbdir/roster-info2.database")
    || warn ("Couldn't open the roster info database! $!\n");
  $q = new CGI(READ_DB);
  close (READ_DB);
  }

sub Init {
  use CGI;
  $dbdir="/home/httpd/db";
  }


__END__
To: Piet Barber <pbarber\@skylinesoaring.org>

To: Skyline Membership <members\@skylinesoaring.org>
