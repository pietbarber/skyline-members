<html>
  <head>
    <title>Skyline Soaring Mailing Lists</title>

<?php

include ("../INCLUDES/left-menu.scrap");
?>


<a name = "TOP"></a>
[<a href = "#members@skylinesoaring.org">Members</a>]
[<a href = "#webmasters@skylinesoaring.org">Webmasters</a>]
[<a href = "#dutyofficers@skylinesoaring.org">Duty Officers</a>]
[<a href = "#towpilots@skylinesoaring.org">Tow Pilots</a>]
[<a href = "#instructors@skylinesoaring.org">Instructors</a>]
[<a href = "#directors@skylinesoaring.org">Directors</a>]
<br>
<!--[<a href = "#cap@skylinesoaring.org">CAP</a>]-->
<!--[<a href = "#cap-towpilots@skylinesoaring.org">CAP Towpilots</a>]-->

<p>For the Charters of each mailing list, please view the mailing-lists charter page.</p>

<hr>
<p> <b>NOTE:</b> The Weekdays Mailing list is no longer maintained by Skyline Soaring Club Webmasters.<br>
To subscribe to the Weekdays list, please go to this link: <a href = "http://skylinesoaring.org/mailman/listinfo/weekdays">Mailman Weekday List</a></p>
<hr>
<p> <b>NOTE:</b> The Misc. Mailing list is no longer maintained by Skyline Soaring Club Webmasters.<br>
To subscribe to the Miscellaneous list, please go to this link: <a href = "http://skylinesoaring.org/mailman/listinfo/misc">Mailman Misc List</a></p>
<hr>
<?php

  $db = pg_Connect ("dbname=skyline");
  if (!$db) {
    echo "Connection to database failed. ";
    include("../INCLUDES/footer.scrap");
    exit;
    }

  echo "<table border=\"0\" bgcolor = \"#FFFFFF\">\n";

  generate ($db, 'members@skylinesoaring.org', 
	"select * from members where (memberstatus != 'I' 
	 and memberstatus != 'N' and email != '' 
	 and email != 'none')
	 or mailinglist = 't'
	 order by lastname, firstname");

  ?>


<?php

//  generate ($db, 'misc@skylinesoaring.org', 
//	"select * from members where misc_list = 't' 
//	 order by lastname, firstname");

  print "Misc List information can be found at:
<a href=\"http://skylinesoaring.org/listinfo/misc\">http://skylinesoaring.org/listinfo/misc</a><br>";


  generate ($db, 'webmasters@skylinesoaring.org', 
	"select * from members where 
	 webmaster = TRUE 
	 order by lastname, firstname");

  generate ($db, 'dutyofficers@skylinesoaring.org', 
	"select * from members where 
	 dutyofficer = 't'
	 and memberstatus != 'I' 
	 and memberstatus != 'N' and email != '' 
	 and email != 'none' 
	 order by lastname, firstname");

  generate ($db, 'towpilots@skylinesoaring.org', 
	"select * from members where 
	 towpilot = 't'
	 and memberstatus != 'I' 
	 and memberstatus != 'N' and email != '' 
	 and email != 'none' 
	 order by lastname, firstname");

  generate ($db, 'instructors@skylinesoaring.org', 
	"select * from members where 
	 instructor = 't'
	 and memberstatus != 'I' 
	 and memberstatus != 'N' and email != '' 
	 and email != 'none' 
	 order by lastname, firstname");

  generate ($db, 'directors@skylinesoaring.org', 
	"select * from members where 
	 (  director = TRUE
	    or secretary = TRUE
	    or treasurer = TRUE )
	 and memberstatus != 'I' 
	 and memberstatus != 'N' and email != '' 
	 and email != 'none' 
	 order by lastname, firstname");


  generate ($db, 'students@skylinesoaring.org', 
	"select * from members where 
	 (rating = 'S' or rating = 'CFIG')
	 and memberstatus != 'I' 
	 and memberstatus != 'N' 
	 and email != '' 
	 and email != 'none' 
	 order by lastname, firstname");

  ?>

<p><i><b>Note: </b> Anyone in the club with a CFIG rating is on the
students list, too. (so the students will actually get some
answers!)</i></p>

<?php

//  generate ($db, 'cap@skylinesoaring.org', 
//	"select * from members where 
//	 capmember = 't' and email != '' 
//	 and email != 'none' 
//	 order by lastname, firstname");

//  generate ($db, 'cap-towpilots@skylinesoaring.org', 
//	"select * from members where 
//	 ((towpilot = 't'
//	   and capmember = 't' )
//	 or (handle = 'jkellett'))
//	 and email != '' 
//	 and email != 'none' 
//	 order by lastname, firstname");
//  print "<i>Jim Kellett is not a towpilot, but he's hard-coded into the cap-towpilots mailing list.</a>";

  include ("../INCLUDES/footer.scrap");


function magfx ($handle) {
  $ans = '<a href = "/MEMBERSHIP/viewmember2.cgi?' . $handle . '">' . 
	'<img src = "/IMAGES/mag.png" width = 16 height = 16 border = 0">' . 
  	'</a>';
  return $ans;
  }

function generate ($db, $title, $sql) {
  print "<a name = \"$title\"></a>";
  print "<table border = 1>\n";
  printf ("<Caption><h3>%s</h3></caption>", $title);
  print "
	<tr bgcolor =\"#C0C0C0\">
	  <td valign = \"top\"><font size=\"+1\"><b>Name</b></font><br></td>
	  <td valign = \"top\"><font size=\"+1\"><b>Email</b></font><br></td>
          <td>&nbsp;</td>
	  <td valign = \"top\"><font size=\"+1\"><b>Name</b></font><br></td>
	  <td valign = \"top\"><font size=\"+1\"><b>Email</b></font><br></td>
	</tr>\n\n";
  $result = pg_Exec($db, $sql);
  $num = pg_numrows($result); 

  for ($i=0; $i<$num; $i++) { 
    $row = pg_fetch_row($result, $i, 1); 
    if ($i % 4 == 2) {
      $bgcolor = "#FFFFFF";
      }
    else {
      $bgcolor ="#E0E0E0";
      }

    if ($i % 2 == 0) {
      print "\n</tr>\n\n<tr bgcolor =\"$bgcolor\">\n";
      }

    if ($i % 2 == 1 && $i %4 !=2) {
      print "\n<td>&nbsp</td>\n";
      }

    printf ("<td><b>%s %s %s %s</b></td>\n",
      magfx($row['handle']),
      $row['firstname'], $row['lastname'], $row['namesuffix']);

    printf ("<td><a href =\"mailto:%s\">%s</a></td>",
      $row['email'], $row['email']);
    }
  echo "</table>\n";
  printf ("(Total of %s)<br>\n", $i);
  print "<a href =\"#TOP\">Return to Top</a>\n";
  print "<br><br>\n";
  }


?>

