<?php
  header ("Content-type: text/plain");
  $title = "List Of <u>All</u> Members";
  $sql = "select * from Members
	where memberstatus != 'N' 
	and memberstatus != 'I'
	order by LastName, FirstName";

  $db = pg_Connect("dbname=skyline");

  if (!$db) {
    echo "Sorry. Connection to database failed. ";
    exit;
    }

$result = pg_Exec($db, $sql);
$num = pg_numrows($result);
$eol = "\n";
if ($mac == 1){
  $eol = "\r";
  }

for ($i=0; $i<$num; $i++) {
  $firstname = '';

  $row = pg_fetch_row($result, $i, 1);
	//  if ($row[handle] == $REMOTE_USER ) {
	//    ++$i;
	//    $row = pg_fetch_row($result, $i, 1);
	//	# Kludgey-man's way of skipping the
	//	# field, so that you don't
	//	# download a palm record of yourself. 
	//    }

  $firstname = $row[firstname];
  if ($row[namesuffix]) {
    $firstname = $row[firstname] . ",  " . $row[namesuffix];
    }

  printf ('"%s", "%s", "%5.5d" %s',
	$row[lastname],
	$firstname,
	$row[zip],
	$eol
	);
  }
?>
