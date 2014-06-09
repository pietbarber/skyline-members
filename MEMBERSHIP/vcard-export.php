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
  $address = '';
  $name = '';
  $row = pg_fetch_row($result, $i, 1);
  echo 'BEGIN:VCARD' . $eol;
  echo 'VERSION:3.0' . $eol;
  printf ('FN:%s %s' . $eol, $row['firstname'], $row['lastname'] );

  printf ('N:%s;%s;;;' . $eol, 
	$row['lastname'], 
	$row['firstname'] 
	); 

  printf ('EMAIL;TYPE=INTERNET:%s'. $eol,
	$row['email']
	);

  if ($row['phone1'] != '' && $row['phone1'] != ' ') {
    printf ('TEL;TYPE=HOME:%s'. $eol,
	$row['phone1']
	);
    }
  if ($row['phone2'] != '' && $row['phone2'] != ' ') {
    printf ('TEL;TYPE=WORK:%s'. $eol,
	$row['phone2']
	);
    }
  if ($row['cell_phone'] != '' && $row['cell_phone'] != ' ') {
  printf ('TEL;TYPE=CELL:%s'. $eol,
	$row['cell_phone']
	);
    }
  printf ('ADR;TYPE=HOME:%s;%s;%s;%s;%s;' . $eol,
	$row['address1'],
	$row['address2'],
	$row['city'],
	$row['state'],
	$row['zip']
	);
  echo 'END:VCARD' . $eol;

  //printf ('"%s", "%s", "%s", "%s", "%s", "%s", "%s", "%s", "%s"' . $eol,
  //printf ('"%s", "%s", "%s", "%s", "%s", "%s", "%s", "%s", "%s"' . $eol,
        //$name,
        //$row['phone2'],
        //$row['phone1'],
        //$row['cell_phone'],       // Mobile
        //$row['email'],
        //$address,
        //$row['city'],
        //$row['state'],
        //$row['zip']
        //);
  }
?>
