<html>
  <head>
    <title>Skyline Soaring Club Members List</title>


<?php

  exec ("/home/httpd/bin/ok_access.pl $_SERVER[REMOTE_USER] edit_member", $ret); 
  if ($ret[0] == 0) {
    $edit_ok=1;
    }

function print_links() {
  $program = '';
  print "<table border = 1 >";
  print "<tr><td>\n";
  printf ('[<a href = "/MEMBERSHIP/%s?search=%s">All Members</a>]',
	$program, 'all');
  print "<br>\n";
  printf ('[<a href = "/MEMBERSHIP/%s?search=%s">Active</a>]',
	$program, 'active');
  printf ('[<a href = "/MEMBERSHIP/%s?search=%s">Inactive</a>]',
	$program, 'inactive');
  printf ('[<a href = "/MEMBERSHIP/%s?search=%s">Family</a>]',
	$program, 'family');
  printf ('[<a href = "/MEMBERSHIP/%s?search=%s">Probationary</a>]',
	$program, 'probationary');
  printf ('[<a href = "/MEMBERSHIP/%s?search=%s">Service</a>]',
	$program, 'service');
  print "<br>\n";
  printf ('[<a href = "/MEMBERSHIP/%s?search=%s">Directors</a>]',
        $program, 'directors');
  printf ('[<a href = "/MEMBERSHIP/%s?search=%s">Instructors</a>]',
	$program, 'instructors');
  printf ('[<a href = "/MEMBERSHIP/%s?search=%s">Towpilots</a>]',
	$program, 'towpilots');
  printf ('[<a href = "/MEMBERSHIP/%s?search=%s">Duty Officers</a>]',
	$program, 'duty');
  printf ('[<a href = "/MEMBERSHIP/%s?search=%s">ADOs</a>]',
	$program, 'ado');
  print "<br>\n";
  printf ('[<a href = "/MEMBERSHIP/%s?search=%s">Students</a>]',
	$program, 'students');


  printf ('[<a href = "/MEMBERSHIP/%s?search=%s">Transient Members</a>]',
	$program, 'trans');
  printf ('[<a href = "/MEMBERSHIP/%s?search=%s">Temporary Members</a>]',
	$program, 'temps');
  printf ('[<a href = "/MEMBERSHIP/%s?search=%s">Non-Members</a>]<br>',
	$program, 'non');

#  print ('[<a href = "/MEMBERSHIP/CAP/">CAP Participants</a>]');
  print "</td>\n";
  print '<td>[ <a href = "/MEMBERSHIP/excelgen.cgi">Generate Excel Spreadsheet of Members List</a> ]<br>';
  print '[ <a href = "/MEMBERSHIP/vcard-export.php">Export Members to VCARDs</a> ]<br>';
  print '[ <a href = "/MEMBERSHIP/excelgen.cgi?verbose">Generate VERBOSE Spreadsheet</a> ]</td></tr></table>';


  }


include ("../INCLUDES/left-menu.scrap");

if ($_GET['search'] == "all") {
  $title = "List Of <u>All</u> Members";
  $sql = "select * from Members
	where memberstatus != 'N'
	order by LastName, FirstName";
  }

elseif ($_GET['search'] == "instructors") {
  $title = "List Of All Active Instructors";
  $sql = "select * from Members
	where Instructor = 'Y'
	and memberstatus != 'I' 
	and memberstatus != 'N'
	order by LastName, FirstName";
  }  

elseif ($_GET['search'] == "inactive") {
  $title = "List Of All Inactive Members";
  $sql = "select * from Members
	where memberstatus = 'I' 
	and memberstatus != 'N'
	order by LastName, FirstName";
  }  

elseif ($_GET['search'] == "duty") {
  $title = "List of Duty Officers";
  $sql = "select * from Members
	where dutyofficer='Y'
	and memberstatus != 'I' 
	and memberstatus != 'N'
	order by LastName, FirstName";
  }  

elseif ($_GET['search'] == "students") {
  $title = "List of Active Students";
  $sql = "select * from Members
	where Rating = 'S'
	and memberstatus != 'I' 
	and memberstatus != 'N'
	order by LastName, FirstName";
  }  

elseif ($_GET['search'] == "towpilots") {
  $title = "List of Active Towpilots";
  $sql = "select * from Members
	where Towpilot = 'Y'
	and memberstatus != 'I' 
	and memberstatus != 'N'
	order by LastName, FirstName";
  }  

elseif ($_GET['search'] == "family") {
  $title = "List of Family Members";
  $sql = "select * from Members
	where MemberStatus = 'Q'
	order by LastName, FirstName";
  }

elseif ($_GET['search'] == "probationary") {
  $title = "List of Probationary Members";
  $sql = "select * from Members
	where MemberStatus = 'P'
	order by LastName, FirstName";
  }

elseif ($_GET['search'] == "service") {
  $title = "List of Service Members";
  $sql = "select * from Members
	where MemberStatus = 'S'
	order by LastName, FirstName";
  }

elseif ($_GET['search'] == "ado") {
  $title = "Assistant Duty Officers";
  $sql = "select * from Members
	where ADO = 'Y'
	and memberstatus != 'I' 
	and memberstatus != 'N'
	order by LastName, FirstName";
  }

elseif ($_GET['search'] == "directors") {
  $title = "Board Members / Directors";
  $sql = "select *
        from Members
        where Director = 't'
        and MemberStatus != 'I'
        and MemberStatus != 'N'
        order by LastName, FirstName";
  }

elseif ($_GET['search'] == "non") {
  $title = "Non-Members";
  $sql = "select * from Members
	where memberstatus = 'N'
	order by LastName, FirstName";
  }

elseif ($_GET['search'] == "trans") {
  $title = "Transient Members";
  $sql = "select * from Members
	where memberstatus = 'T' 
	order by LastName, FirstName";
  }

elseif ($_GET['search'] == "temps") {
  $title = "Temporary Members";
  $sql = "select * from Members
	where memberstatus = 'E' 
	order by LastName, FirstName";
  }


else {
  $title = "List of all Active (+Family) Members";
  $sql = "select * from Members
	where memberstatus != 'I' 
	and memberstatus != 'N'
	order by LastName, FirstName";
  }

$sql2 = "select handle from bios";

echo "<h1>$title</h1>";
$program = 'index.php';

print_links();

echo "<table border=\"0\" bgcolor = \"#FFFFFF\">\n";

if ($edit_ok) {

  echo '<caption align = "bottom">
	[<a href = "/ADMIN/newmember2.cgi">Add New Member</a>]
	</caption>';
  }

print "<tr bgcolor =\"#C0C0C0\">
        <td valign = \"top\"><font size=\"+1\"><b>Name</b></font><br>
            <font size=\"-1\"><i>(Directors in Red)</i></font><br>
            </b>[Title]</b><br></td>
        <td valign = \"top\"><font size=\"+1\"><b>Residence<hr>Phone</b></font><br></td>
        <td valign = \"top\"><font size=\"+1\"><b>Duties</b></font><br>
	</td>
        <td valign = \"top\"><font size=\"+1\"><b>Email</b></font><br></td>
        </tr>";

$db = pg_Connect("dbname=skyline");

if (!$db) {
  echo "Connection to database failed. ";
  include ("../INCLUDES/footer.scrap");
  exit;
  }
	// Gawd I hate PHP.  What was I thinking. 
	// I could have used Perl

$result = pg_Exec($db, $sql);
$bios_result = pg_exec ($db, $sql2);
$num = pg_numrows($result);
$bios_num = pg_numrows($bios_result);

for ($i=0; $i<$bios_num; $i++) {
  $bio_row=pg_fetch_row($bios_result, $i, 1);
  $bio_true[$bio_row['handle']]='t';
  }

$people_count=0;
for ($i=0; $i<$num; $i++) {
  $row = pg_fetch_row($result, $i, 1);
  if ($i % 2 == 0) {
    $bgcolor = "#FFFFFF";
    }
   else {
    $bgcolor ="#E0E0E0";
    }

  $address2="";
  if ($row['address2']) {
    $address2 = "<br>" . $row['address2'];
    }
  print "<tr bgcolor =\"$bgcolor\">";

    if ($row['director'] == 't') {
      printf ("<td><font color = \"#990000\"><b>%s %s %s</b></font>",
        $row['firstname'], $row['lastname'], $row['namesuffix'] );
      }
    else {
      printf ("<td><b>%s %s %s</b> ",
        $row['firstname'], $row['lastname'], $row['namesuffix']);
      }

    #if ($row['mugshot'] == 't') {
      #printf ("&nbsp;&nbsp;&nbsp;<a href = \"/SNAPSHOTS/index.cgi?mode=search&searchstring=%s\" target = \"Mugshot\"><img src=\"mugshot.png\" border=\"0\" width= \"27\" height=\"21\" align=\"middle\"></a>\n",
	#$row['lastname']);
      #}

   
    if ($row['official_title']) {
      printf ("<br>[<i>%s</i>]\n",  $row['official_title']);
      }


    if ($bio_true[$row['handle']] == 't') {
      printf ("<br>[<a href = \"/BIOS/?member=%s\">Bio</a>]\n",
	$row['handle']);
      }

    if ($_SERVER['REMOTE_USER'] == $row['handle'] && !$bio_true[$row['handle']]) {
      print ("<br>[<a href= \"/BIOS/?\">Create Your Bio Now!\n");
      }

    if ($row['memberstatus'] == "E") {
      print ("<i>Introductory Member</i>\n");
      }
    print ("</td>\n");
      

  if ($row['cell_phone'] != '' && $row['cell_phone'] != ' ') {
    $row['cell_phone'] .= " <i>(cell)</i> ";
    }
  printf ("<td align=\"top\" nowrap align=center valign=middle>%s %s<br>\n%s, %s %s\n<hr>%s<br>%s<br>%s</td>",
	$row['address1'], $address2, $row['city'],
	$row['state'], $row['zip'], $row['phone1'], $row['phone2'], $row['cell_phone']); 

  print "<td>";

  if ($row['director'] == 't') {
    print 'Director<br>';
    }

  if ($row['towpilot'] == 't') {
    print 'Towpilot<br>';
    }

  if ($row['instructor'] == 't') {
    print 'Instructor<br>';
    }

  if ($row['dutyofficer'] == 't') {
    print "DO<br>";
    }

  if ($row['ado'] == 't') {
    print 'ADO<br>';
    }

  if ($row['otherduties'] == 't') {
    print "Other<br>";
    }

    if ($row['memberstatus'] == "E") {
      printf ("<i>Introductory Member<br>Joined on<br>%s<i>\n", 
	$row['joindate']);
      }

  print "</td>";

  if ($row['email'] == 'none' || $row['email'] == '') {
    print "<td><i>none</i></td>\n";
    }
  else {
    printf ("<td><a href =\"mailto:%s\">%s</a></td>",
	$row['email'], $row['email']);
    }
  print "<td bgcolor = \"#FFFFFF\" valign =middle align = center>\n";
  $mag = '<img src = "/IMAGES/mag.png" width="45" height="41" border = 0>';
  $edit = '<img src = "/IMAGES/edit.png" width="38" height="46" border = 0>';

  if ($edit_ok) {
    printf ("<a href = \"/ADMIN/editmember2.cgi?%s\">%s</a>",
	$row['handle'], $edit);
      }
  printf ("<a href = \"/MEMBERSHIP/viewmember2.cgi?%s\">%s</a>",
	$row['handle'], $mag);

  echo "</td></tr>\n";
  $people_count++;
  }
  echo "</table>\n";
  printf ("A total of %d people", 
	$people_count
	);
  include ("../INCLUDES/footer.scrap");
?>
