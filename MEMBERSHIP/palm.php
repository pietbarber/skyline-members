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
$eol = "\r\n";
if ($mac == 1){
  $eol = "\r";
  }

for ($i=0; $i<$num; $i++) {
  $jobs = '';
  $address = '';
  $firstname = '';

  $row = pg_fetch_row($result, $i, 1);
	//  if ($row[handle] == $_SERVER[REMOTE_USER] ) {
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

  if ($row[address2]) {
    $address = $row[address1] . $eol . $row[address2];
    }

  if ($address == '') {
    $address = $row[address1];
    }
  $jobs='';
  if ($row[director] == 't') {
    $jobs .= " Board of Directors ";
    }

  if ($row[dutyofficer] == 't') {
    $jobs .= " Duty Officer ";
    }

  if ($row[towpilot] == 't') {
    $jobs .= " Tow Pilot ";
    }

  if ($row[ado] == 't') {
    $jobs .= " Asst Duty Officer ";
    }

  if ($row[instructor] == 't') {
    $jobs .= " Instructor ";
    }

  if ($row[memberstatus] == 'M') {
    $memberstatus = 'Standard Member';
    }

  if ($row[memberstatus] == 'S') {
    $memberstatus = 'Service Member';
    }

  if ($row[memberstatus] == 'P') {
    $memberstatus = 'Probationary Member';
    }

  elseif ($row[memberstatus] == 'Q') {
    $memberstatus = 'Family Member';
    }

  elseif ($row[memberstatus] == 'H') {
    $memberstatus = 'Honorary Member';
    }

  elseif ($row[memberstatus] == 'F') {
    $memberstatus = 'Founding Member';
    }
  $glider_owned='';
  if ($row[glider_owned2]) {
    $glider_owned = $eol . "Glider owned: $row[glider_owned] and $row[glider_owned2]";
    }

  elseif ($row[glider_owned]) {
    $glider_owned = $eol . "Glider owned: $row[glider_owned]";
    }

  printf ('"%s","%s", "%s", "%s", "%s", "%s", "%s", "%s", "%s", "%s", "%s", "%s", "%s", "%s", "%s", "%s", "%s", "%s", "%s", "%s"' . $eol, 
	$row[lastname],
	$firstname,
	$row[official_title],
	'',	// Company
	$row[phone2],
	$row[phone1],
	'',
	$row[cell_phone],	// Mobile
	$row[email],
	$address, 
	$row[city],
	$row[state],
	$row[zip],
	'', 	// Country
	$jobs,
        '',
	'',
	'',
	'Joined Club: ' . $row[joindate] . $eol . 
	"Current status: " . 
	$memberstatus . $eol . 
	"This record last updated on " . 
        date("F j, Y, g:i a", $row[lastupdated]) . 
	$eol . "This record downloaded on " . 
        date("F j, Y, g:i a") . $glider_owned,
	'0'
	);
  }
?>
