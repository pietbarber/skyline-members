<html>
  <head>
    <title>Skyline Soaring Administration</title>

<?php
include ("../INCLUDES/left-menu.scrap");

  $db = pg_Connect ("dbname=skyline");
  if (!$db) {
    echo "Connection to database failed. ";
    include("../INCLUDES/footer.scrap");
    exit;
    }

  $sql = 'select lastname, firstname, director, webmaster, secretary from members where handle = \'' . 
	$_SERVER[REMOTE_USER] . '\';';
  $result = pg_Exec($db, $sql);
  $num = pg_numrows($result);
  for ($i=0; $i<$num; $i++) {
    $row = pg_fetch_row($result, $i, 1);
    }
  print "<h1>Welcome, $row[firstname] $row[lastname]</h1>";

  if ($row['director'] == 't') {
    $usage_stats = 1;
    }
  elseif ($row['webmaster'] == 't') {
    $usage_stats = 1;
    } 
  elseif ($row['secretary'] == 't') {
    $usage_stats = 1;
    }

?>

<h2>Administrative Tools You May Access:</h2> 
<table border = 1>

<?php
  $sql = 'select * from access where handle = \'' . 
	$_SERVER[REMOTE_USER] . '\';';
  $result = pg_Exec($db, $sql);
  $num = pg_numrows($result);
  for ($i=0; $i<$num; $i++) {
    $row = pg_fetch_row($result, $i, 1);
    }

  if ($usage_stats == 1) {
    print "<tr><td><h3>Restricted to Board Members</h3><ul>\n";
    print link_to('/BoardNotes/', 'View Board Notes');
    print "</ul></td></tr>";
    }

  if ($row['edit_member'] == 't') {
    print "<tr><td><h3>Member Edit Functions</h3><ul>\n";
    print link_to('/MEMBERSHIP/', 'View Editable Members List');
    print "</ul></td></tr>";
    }

  if ($row['board_notes'] == 't') {
    print "<tr><td><h3>Edit/Upload Board Notes</h3><ul>\n";
    print link_to('http://members.skylinesoaring.org/ADMIN/BNU/index.php?lt=/var/www/members/html/BoardNotes/&rt=/var/www/members/html/BoardNotes/&sortby0=name&sortdir0=4&sortby1=name&sortdir1=4', 'Edit/Upload Board Notes');
    print "</ul></td></tr>";
    }

  if ($row['edit_roster'] == 't') {
    print "<tr><td><h3>Roster Edit Functions</h3><ul>\n";
    print link_to('/ADMIN/rostermake.cgi', 'Edit Roster');
    print link_to('/ROSTER/', 'View Roster');
    print "</ul></td></tr>";
    }

  if ($row['web_edit'] == 't') {
    print "<tr><td><h3>Web Edit Functions</h3><ul>\n";
    print link_to('/ADMIN/EditJoinUs.cgi', 'Edit "Join Us" Page');
    print link_to('/ADMIN/EditAboutUs.cgi', 'Edit "About" Page');
    print link_to('/ADMIN/EditKudos.cgi', 'Edit "Kudos" Page (linked from About Us)');
    print link_to('/ADMIN/EditAuthors.cgi', 'Edit "Authors" Page');
    print link_to('/ADMIN/EditTraining.cgi', 'Edit "Training" Page');
    print link_to('/ADMIN/EditSafety.cgi', 'Edit "Safety" Page');
    print link_to('/ADMIN/EditRegionIV.cgi', 'Edit "RegionIV" Page');
    print link_to('/ADMIN/EditVideos.cgi', 'Edit "Videos" Page');
    print link_to('/ADMIN/EditLinks.cgi', 'Edit "Links" Page');
    print link_to('/ADMIN/EditWeather.cgi', 'Edit "Weather" Page');
    print "History Pages:<br>\n";
    print "<ol>\n";
    print link_to('/ADMIN/EditHistorystart.cgi', 'Edit "History" (Foreward)');
    print link_to('/ADMIN/EditHistory1.cgi', 'Edit "History" (Chapter I)');
    print link_to('/ADMIN/EditHistory2.cgi', 'Edit "History" (Chapter II)');
    print "<ul>\n";
    print link_to('/ADMIN/EditHistoryTeen.cgi', 'Edit "Teen Article"'); 
    print link_to('/ADMIN/EditHistoryCASS.cgi', 'Edit "CASS Warrenton Article"'); 
    print '(Linked from Chapter II)';
    print "</ul>\n";
    print link_to('/ADMIN/EditHistory3.cgi', 'Edit "History" (Chapter III)');
    print "<ul>\n";
    print link_to('/ADMIN/EditHistoryAnders.cgi', 'Edit "Bill Anders Article"'); 
    print '(Linked from Chapter III)';
    print "</ul>\n";
    print link_to('/ADMIN/EditHistory4.cgi', 'Edit "History" (Chapter IV)');
    print link_to('/ADMIN/EditHistory5.cgi', 'Edit "History" (Chapter V)');
    print "</ol>\n";
    print "</ul></td></tr>";
    }




function link_to ($link, $desc) {
  $a = sprintf ("<li>" . 
    '<a href = "%s">%s</a>' . 
    "</li>\n", $link, $desc);
  return $a;
  }

?>

</table>

<?php
include ("../INCLUDES/footer.scrap");
?>




