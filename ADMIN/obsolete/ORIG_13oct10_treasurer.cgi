#!/usr/bin/perl 

use strict;
use CGI qw(:standard);
print header;
print start_html (
	-title => "Skyline Soaring Club Invoice Utility"
	);

my $dbh; 

if (param('uploaded_file')) {
  print h1("Processing file...");
  my $filename=param('uploaded_file');
  my $fh = upload('uploaded_file');
  print "<table>";
  connectify();
  while (my $line = <$fh>) {
	#print $line . "<br>\n";
	my (%user_info);
 	chomp ($line);
	my ($lastname, $firstname, $amount, $middleinitial, $namesuffix);

 	if ($line =~ /"([A-Za-z\-]+), ([\-A-Za-z]+)",\s*\"?(-?[\,0-9-.]+)\s*\"?/) {
		$lastname=$1; 
		$firstname=$2; 
		$amount=$3;
		$amount =~ s/\,//g;
		#print "F: $lastname F: $firstname A: $amount\n<br>";
		}

 	elsif ($line =~ /"([A-Za-z\-]+), ([\-A-Za-z]+) ([A-Za-z\.]+)",\s*\"?(-?[0-9-.\,]+\s*\"?)/) {
		$lastname=$1; 
		$firstname=$2; 
		$middleinitial=$3;
		$amount=$4;
		$amount =~ s/\,//g;
		#print "L: $lastname M: $middleinitial F: $firstname A: $amount\n<br>";
		}
	else {
		print "Unable to figure out this line: $line <br>\n";
		}

	if ($middleinitial) {
          %user_info = lookup_three($lastname, $firstname, $middleinitial);
          }

	if (!%user_info) {
	        %user_info = lookup_both($lastname, $firstname); 
		}

	if (!%user_info) {
	        %user_info = lookup($lastname); 
		}

	if (!%user_info) {
		print "<tr><td>I can't grok this line:  <tt>$line</tt></td></tr>\n";
		}

        if ($user_info{'email'} !~ /\@/ || !$user_info{'email'}) {
 		printf "<tr><td>Unable to email to %s %s <%s></td></tr>\n",
			$user_info{'firstname'},
			$user_info{'lastname'},
			$user_info{'email'};
		}

	elsif ($amount == 0) {
		printf "<tr><td>Sent zero balance notice to %s %s <%s>.\n",
			$user_info{'firstname'},
			$user_info{'lastname'},
			$user_info{'email'};

		email_zero_balance($user_info{'lastname'},
				$user_info{'firstname'},
				$user_info{'email'}
				);
		}

	elsif ($amount > 0) {

		email_invoice(  $user_info{'lastname'},
				$user_info{'firstname'}, 
				$user_info{'email'}, 
				$amount
				);
		printf "<tr><td>Sent invoice to %s %s <%s> for the amount of\$$amount</td></tr>\n",
			$user_info{'firstname'}, 
			$user_info{'lastname'}, 
			$user_info{'email'};
		}
        elsif ($amount < 0) {
		email_balance(  $user_info{'lastname'}, 
				$user_info{'firstname'}, 
				$user_info{'email'}, 
				$amount
				);
		printf "<tr><td>Sent credit notice to %s %s <%s> for the amount of\$$amount</td></tr>\n",
			$user_info{'firstname'}, 
			$user_info{'lastname'}, 
			$user_info{'email'};
		}
	}

  print "</table>";
  }

elsif (! param()) {
  print h1("Upload");
  print "Upload your .csv file here:<br>";
  print start_multipart_form(); 
  print filefield(
	-name=>'uploaded_file',
	-default=>'Export.csv',
	-size=>50,
	-maxlength=>80
	);
  print "<br><i>Click Submit when ready.</i>";
  print submit(
	-name =>'submit'
	);
  }
exit;

sub connectify {
  use DBI;
  my $database = 'skyline';
  $dbh = DBI->connect("DBI:Pg:dbname=skyline")
        || die ("Can't connect to database $!\n");
  } 

sub lookup_three {
  my ($lastname) = shift;
  my ($firstname) = shift;
  my ($middleinitial) = shift;
  my (%answer);
  my ($fetchrow)=0;
  my ($sql) = qq/
	select handle, lastname, firstname, email
	from members where 
	lastname = '$lastname'
	and firstname = '$firstname'
	and ( middleinitial = '$middleinitial' or namesuffix = '$middleinitial')/;
  my $check_handle = $dbh->prepare($sql);
  $check_handle->execute();
  while (my $ref = $check_handle->fetchrow_hashref()) {
    $fetchrow++;
    %answer=(
		'handle' => $ref->{'handle'}, 
		'lastname' => $ref->{'lastname'}, 
		'firstname' => $ref->{'firstname'}, 
		'email' => $ref->{'email'}
		);
    }
  if ($fetchrow == 1) {
    return %answer;
    }
  "";
  }

sub lookup_both {
  my ($lastname) = shift;
  my ($firstname) = shift;
  my (%answer);
  my ($fetchrow)=0;
  my ($sql) = qq/
	select handle, lastname, firstname, email
	from members where 
	lastname = '$lastname'
	and firstname = '$firstname'/;
  my $check_handle = $dbh->prepare($sql);
  $check_handle->execute();
  while (my $ref = $check_handle->fetchrow_hashref()) {
    $fetchrow++;
    %answer=(
		'handle' => $ref->{'handle'}, 
		'lastname' => $ref->{'lastname'}, 
		'firstname' => $ref->{'firstname'}, 
		'email' => $ref->{'email'}
		);
    }
  if ($fetchrow == 1) {
    return %answer;
    }
  "";
  }

sub lookup {
  my ($lastname) = shift;
  my (%answer);
  my ($fetchrow)=0;
  my ($sql) = qq/
	select handle, lastname, firstname, email
	from members where 
	lastname = '$lastname'/;
  my $check_handle = $dbh->prepare($sql);
  $check_handle->execute();
  while (my $ref = $check_handle->fetchrow_hashref()) {
    $fetchrow++;
    %answer=(
		'handle' => $ref->{'handle'}, 
		'lastname' => $ref->{'lastname'}, 
		'firstname' => $ref->{'firstname'}, 
		'email' => $ref->{'email'}
		);
    }
  if ($fetchrow == 1) {
    return %answer;
    }
  "";
  }

sub email_zero_balance {
  my ($lastname, $firstname, $email) = @_;
  my ($date) = scalar localtime; 
  my $invoice =<<EOM;
From: "Skyline Soaring Club Treasurer" <treasurer\@skylinesoaring.org>
To: "$firstname $lastname" <$email>
X-Accept-Language: en-us, en
MIME-Version: 1.0
Subject: Skyline Soaring Zero Balance Notice
Content-Type: multipart/alternative;
 boundary="------------030206090606080704090500"
Status: O

This is a multi-part message in MIME format.
--------------030206090606080704090500
Content-Type: text/plain; charset=ISO-8859-1; format=flowed
Content-Transfer-Encoding: 7bit

logo <http://skylinesoaring.org/> 	Skyline Soaring Club, Inc.
/Skyline Soaring Club Zero Balance Notice/
$date

Dear $firstname $lastname
The treasurer's accounts indicate that your accounts are all settled with the club.
Your current balance is zero. 


--------------030206090606080704090500
Content-Type: multipart/related;
 boundary="------------060802060109030504000007"


--------------060802060109030504000007
Content-Type: text/html; charset=ISO-8859-1
Content-Transfer-Encoding: 7bit

<\!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN">
<html>
<head>
  <meta content="text/html;charset=ISO-8859-1" http-equiv="Content-Type">
  <title></title>
</head>
<body bgcolor="#ffffff" text="#000000">
<br>
<table border="1" cellpadding="2" cellspacing="2">
  <tbody>
    <tr>
      <td align="center" bgcolor="#7777e7" valign="top"><a
 href="http://skylinesoaring.org/"><img
 src="cid:part1.01060106.05030909\@skylinesoaring.org" name="logo" alt="logo"
 border="0" height="95" width="120"></a></td>
      <td align="center" bgcolor="#7777e7" valign="top"><font color="#ffffff"><i><big><big>Skyline Soaring Club Zero Balance Notice</big></big></i></font><br>
      </td>
    </tr>
    <tr>
      <td colspan="2" valign="top">
$date<br><br>
Dear $firstname $lastname<br>
The treasurer's accounts indicate that your accounts are all settled with the Club.<br>
Your current balance is zero. 
      </td>
    </tr>
  </tbody>
</table>
<br>
<br>
</body>
</html>

--------------060802060109030504000007
Content-Type: image/gif;
 name="logo"
Content-Transfer-Encoding: base64
Content-ID: <part1.01060106.05030909\@skylinesoaring.org>
Content-Disposition: inline;
 filename="logo"

R0lGODlheABfAOcAAHd34v///yUlf5yc6piY6nt75ZWV6ouL6I6O6JKS6H9/5YOD5Xd35YeH
6J+f6iUlg4eH5bKy78PD8eLi+NPT9vHx/fv7/xkZf5KS6v39/8zM9PT0/ZWV6Kmp7eDg+Pb2
/e3t+8HB8c7O9NbW9urq+97e+Li476Ki7dnZ9rW17/j4/+jo+6ys7cnJ9KWl7QAAe7u78b6+
8VtbwcbG9Pj4/eXl+wAAANvb+O/v/dvb9tHR9HNz4K+v7e/v+2FhwRkZN1BQsq+v7xkZe3Nz
xtHR9hkZL1tbtbu773Nz3iUlReXl+HNz4iUlSzc3jvj4+zc3h29v2z4+e0VFg29v2ZiYuOrq
73Nz22Zm0fv7+8bG8UtLi1BQnODg6PT0+AAAGS8vVmFhxm9v02trziUlUKKi6ouLr6WlwVBQ
oktLlc7O29nZ4j4+jqyswzc3ZiUlNz4+i7u7zi8vg2FhwwAAJVtbrGtrzD4+d29v1hkZPmFh
te/v9GZmnOXl7dPT4GFhvhkZJS8vW0VFi4eH4P39/X9/qTc3c8nJ2T4+ZsHB0WZmvnNz04eH
3i8vh1BQlVZWlWtrnIuL4IeHrzc3UN7e5VZWqZ+fuz4+czc3Wy8vYVBQg1BQkn9/xnd3pYOD
zktLe1tbnC8vUJiY5Xt7046O22FhuG9vtVBQtTc3b2ZmuHd33ltbkvT09rKyyXNzoo6O4I6O
tbW1yYuL03d34H9/4D4+lWtrxmFhmGtroltbslZWnIOD03d32XNzzEtLc3d3xnNzvj4+b1BQ
rEtLkoODqYeH2Xt7qVtbmHt7zJWV4EVFop+f7YuL5VBQi2Zmry8vZltbopWVtYOD6MPD1qKi
wXt70YOD2S8vi8bG1m9vzoOD4EVFe0VFc3t74mtr0y8vRVtbuCUlVktLg2ZmtZKS5W9vrzc3
knt7vn9/21tbi2Zmpbi4zltbqXNzrD4+nCUlh1ZWuHt7uHNz0QAAf6+vyays729vyWFhzG9v
w3Nz2VZWshkZRT4+h3Nzw8PD9Li48S8vjiH+GlNreWxpbmUgU29hcmluZyBDbHViLCBJbmMu
ACwAAAAAeABfAAAI/gCXAAAgkCADgggNGhRYEOESBgwHPixI8WBEhQIhStyoMSFFjwA0Zvz4
0aFJkw89Qsw4EKNIiyATynwJsuLIjSlzhizpECbGnyQ3xry5MCTOlihryry4JKLTpE8nHg0a
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
ekNGXJ6MipHSHijIYpuzkMElKUwrEwEBADs=
--------------060802060109030504000007
--------------030206090606080704090500--
EOM

  open (SENDMAIL, "|-")
	|| exec ('/usr/sbin/sendmail', '-t', '-oi');
  print SENDMAIL $invoice; 
  close (SENDMAIL);
  }


sub email_invoice {
  my ($lastname, $firstname, $email, $amount) = @_;
  my ($amountable) = sprintf("%4.2f", $amount);
  my ($date) = scalar localtime; 
  my $invoice =<<EOM;
From: "Skyline Soaring Club Treasurer" <treasurer\@skylinesoaring.org>
To: "$firstname $lastname" <$email>
X-Accept-Language: en-us, en
MIME-Version: 1.0
Subject: Skyline Soaring Club Invoice
Content-Type: multipart/alternative;
 boundary="------------030206090606080704090500"
Status: O

This is a multi-part message in MIME format.
--------------030206090606080704090500
Content-Type: text/plain; charset=ISO-8859-1; format=flowed
Content-Transfer-Encoding: 7bit

logo <http://skylinesoaring.org/> 	Skyline Soaring Club, Inc.
/Skyline Soaring Club Billing Invoice/
$date

Dear $firstname $lastname
The treasurer's accounts indicate that you have an account 
balance with the flying club.  Please send a check for the amount of 
\$$amountable to the Skyline Soaring Club Treasurer at this address:

Skyline Soaring Club
c/o Vern Kline
14269 Silverdale Dr
Woodbridge, VA 22193

If you have any issues with the above balance, please contact the club 
treasurer by email to:
treasurer\@skylinesoaring.org, or by phone: 571-765-0024




--------------030206090606080704090500
Content-Type: multipart/related;
 boundary="------------060802060109030504000007"


--------------060802060109030504000007
Content-Type: text/html; charset=ISO-8859-1
Content-Transfer-Encoding: 7bit

<\!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN">
<html>
<head>
  <meta content="text/html;charset=ISO-8859-1" http-equiv="Content-Type">
  <title></title>
</head>
<body bgcolor="#ffffff" text="#000000">
<br>
<table border="1" cellpadding="2" cellspacing="2">
  <tbody>
    <tr>
      <td align="center" bgcolor="#7777e7" valign="top"><a
 href="http://skylinesoaring.org/"><img
 src="cid:part1.01060106.05030909\@skylinesoaring.org" name="logo" alt="logo"
 border="0" height="95" width="120"></a></td>
      <td align="center" bgcolor="#7777e7" valign="top"><font color="#ffffff"><i><big><big>Skyline Soaring Club Billing
Invoice</big></big></i></font><br>
      </td>
    </tr>
    <tr>
      <td colspan="2" valign="top">
$date<br><br>
Dear $firstname $lastname<br>
The treasurer's accounts indicate that you have an account
balance with the flying club.&nbsp; Please send a check for the amount of
<b>\$$amountable</b> to the Skyline Soaring Club Treasurer at this address: <br>
      <br>
      <tt>Skyline Soaring Club <br>
c/o Vern Kline<br>
14269 Silverdale Dr<br>
Woodbridge, VA 22193 <br>
      <br>
If you have any issues with the above balance, please contact the club
treasurer by email to: <br>

<a class="moz-txt-link-abbreviated" href="mailto:treasurer\@skylinesoaring.org">treasurer\@skylinesoaring.org</a>, or by phone: 571-765-0024<br>
      <br>
      </td>
    </tr>
  </tbody>
</table>
<br>
<br>
</body>
</html>

--------------060802060109030504000007
Content-Type: image/gif;
 name="logo"
Content-Transfer-Encoding: base64
Content-ID: <part1.01060106.05030909\@skylinesoaring.org>
Content-Disposition: inline;
 filename="logo"

R0lGODlheABfAOcAAHd34v///yUlf5yc6piY6nt75ZWV6ouL6I6O6JKS6H9/5YOD5Xd35YeH
6J+f6iUlg4eH5bKy78PD8eLi+NPT9vHx/fv7/xkZf5KS6v39/8zM9PT0/ZWV6Kmp7eDg+Pb2
/e3t+8HB8c7O9NbW9urq+97e+Li476Ki7dnZ9rW17/j4/+jo+6ys7cnJ9KWl7QAAe7u78b6+
8VtbwcbG9Pj4/eXl+wAAANvb+O/v/dvb9tHR9HNz4K+v7e/v+2FhwRkZN1BQsq+v7xkZe3Nz
xtHR9hkZL1tbtbu773Nz3iUlReXl+HNz4iUlSzc3jvj4+zc3h29v2z4+e0VFg29v2ZiYuOrq
73Nz22Zm0fv7+8bG8UtLi1BQnODg6PT0+AAAGS8vVmFhxm9v02trziUlUKKi6ouLr6WlwVBQ
oktLlc7O29nZ4j4+jqyswzc3ZiUlNz4+i7u7zi8vg2FhwwAAJVtbrGtrzD4+d29v1hkZPmFh
te/v9GZmnOXl7dPT4GFhvhkZJS8vW0VFi4eH4P39/X9/qTc3c8nJ2T4+ZsHB0WZmvnNz04eH
3i8vh1BQlVZWlWtrnIuL4IeHrzc3UN7e5VZWqZ+fuz4+czc3Wy8vYVBQg1BQkn9/xnd3pYOD
zktLe1tbnC8vUJiY5Xt7046O22FhuG9vtVBQtTc3b2ZmuHd33ltbkvT09rKyyXNzoo6O4I6O
tbW1yYuL03d34H9/4D4+lWtrxmFhmGtroltbslZWnIOD03d32XNzzEtLc3d3xnNzvj4+b1BQ
rEtLkoODqYeH2Xt7qVtbmHt7zJWV4EVFop+f7YuL5VBQi2Zmry8vZltbopWVtYOD6MPD1qKi
wXt70YOD2S8vi8bG1m9vzoOD4EVFe0VFc3t74mtr0y8vRVtbuCUlVktLg2ZmtZKS5W9vrzc3
knt7vn9/21tbi2Zmpbi4zltbqXNzrD4+nCUlh1ZWuHt7uHNz0QAAf6+vyays729vyWFhzG9v
w3Nz2VZWshkZRT4+h3Nzw8PD9Li48S8vjiH+GlNreWxpbmUgU29hcmluZyBDbHViLCBJbmMu
ACwAAAAAeABfAAAI/gCXAAAgkCADgggNGhRYEOESBgwHPixI8WBEhQIhStyoMSFFjwA0Zvz4
0aFJkw89Qsw4EKNIiyATynwJsuLIjSlzhizpECbGnyQ3xry5MCTOlihryry4JKLTpE8nHg0a
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
ekNGXJ6MipHSHijIYpuzkMElKUwrEwEBADs=
--------------060802060109030504000007
--------------030206090606080704090500--
EOM

  open (SENDMAIL, "|-")
	|| exec ('/usr/sbin/sendmail', '-t', '-oi');
  print SENDMAIL $invoice; 
  close (SENDMAIL);
  }

sub email_balance {
  my ($lastname, $firstname, $email, $amount) = @_;
  my ($balance) = $amount * -1 unless $amount > 0; 
  my ($amountable) = sprintf ("%4.2f", $balance);
  my ($date) = scalar localtime; 
  my $invoice =<<EOM;
From: "Skyline Soaring Club Treasurer" <treasurer\@skylinesoaring.org>
To: "$firstname $lastname" <$email>
X-Accept-Language: en-us, en
MIME-Version: 1.0
Subject: Skyline Soaring Club Credit Notice
Content-Type: multipart/alternative;
 boundary="------------030206090606080704090500"
Status: O

This is a multi-part message in MIME format.
--------------030206090606080704090500
Content-Type: text/plain; charset=ISO-8859-1; format=flowed
Content-Transfer-Encoding: 7bit

logo <http://skylinesoaring.org/> 	Skyline Soaring Club, Inc.
/Skyline Soaring Club Billing Credit Notice/
$date

Dear $firstname $lastname
The treasurer's records indicate that you have a credit with the club.

Current Credit: \$$amountable

If you have any issues with the above balance, please contact the club 
treasurer by email to:
treasurer\@skylinesoaring.org, or by phone: 571 765-0024

--------------030206090606080704090500
Content-Type: multipart/related;
 boundary="------------060802060109030504000007"


--------------060802060109030504000007
Content-Type: text/html; charset=ISO-8859-1
Content-Transfer-Encoding: 7bit

<\!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN">
<html>
<head>
  <meta content="text/html;charset=ISO-8859-1" http-equiv="Content-Type">
  <title></title>
</head>
<body bgcolor="#ffffff" text="#000000">
<br>
<table border="1" cellpadding="2" cellspacing="2">
  <tbody>
    <tr>
      <td align="center" bgcolor="#7777e7" valign="top"><a
 href="http://skylinesoaring.org/"><img
 src="cid:part1.01060106.05030909\@skylinesoaring.org" name="logo" alt="logo"
 border="0" height="95" width="120"></a></td>
      <td align="center" bgcolor="#7777e7" valign="top"><font color="#ffffff"><i><big><big>Skyline Soaring Club Billing
Invoice</big></big></i></font><br>
      </td>
    </tr>
    <tr>
      <td colspan="2" valign="top">
$date<br><br>
Dear $firstname $lastname<br>
<p>The treasurer's records indicate that you have a credit with the club.</p>

<p>Current Credit:<b>\$$amountable</b></p>

If you have any issues with the above balance, please contact the club
treasurer by email to: <br>

<a class="moz-txt-link-abbreviated" href="mailto:treasurer\@skylinesoaring.org">treasurer\@skylinesoaring.org</a>, or by phone: 571 765-0024<br>
      <br>
      </td>
    </tr>
  </tbody>
</table>
<br>
<br>
</body>
</html>

--------------060802060109030504000007
Content-Type: image/gif;
 name="logo"
Content-Transfer-Encoding: base64
Content-ID: <part1.01060106.05030909\@skylinesoaring.org>
Content-Disposition: inline;
 filename="logo"

R0lGODlheABfAOcAAHd34v///yUlf5yc6piY6nt75ZWV6ouL6I6O6JKS6H9/5YOD5Xd35YeH
6J+f6iUlg4eH5bKy78PD8eLi+NPT9vHx/fv7/xkZf5KS6v39/8zM9PT0/ZWV6Kmp7eDg+Pb2
/e3t+8HB8c7O9NbW9urq+97e+Li476Ki7dnZ9rW17/j4/+jo+6ys7cnJ9KWl7QAAe7u78b6+
8VtbwcbG9Pj4/eXl+wAAANvb+O/v/dvb9tHR9HNz4K+v7e/v+2FhwRkZN1BQsq+v7xkZe3Nz
xtHR9hkZL1tbtbu773Nz3iUlReXl+HNz4iUlSzc3jvj4+zc3h29v2z4+e0VFg29v2ZiYuOrq
73Nz22Zm0fv7+8bG8UtLi1BQnODg6PT0+AAAGS8vVmFhxm9v02trziUlUKKi6ouLr6WlwVBQ
oktLlc7O29nZ4j4+jqyswzc3ZiUlNz4+i7u7zi8vg2FhwwAAJVtbrGtrzD4+d29v1hkZPmFh
te/v9GZmnOXl7dPT4GFhvhkZJS8vW0VFi4eH4P39/X9/qTc3c8nJ2T4+ZsHB0WZmvnNz04eH
3i8vh1BQlVZWlWtrnIuL4IeHrzc3UN7e5VZWqZ+fuz4+czc3Wy8vYVBQg1BQkn9/xnd3pYOD
zktLe1tbnC8vUJiY5Xt7046O22FhuG9vtVBQtTc3b2ZmuHd33ltbkvT09rKyyXNzoo6O4I6O
tbW1yYuL03d34H9/4D4+lWtrxmFhmGtroltbslZWnIOD03d32XNzzEtLc3d3xnNzvj4+b1BQ
rEtLkoODqYeH2Xt7qVtbmHt7zJWV4EVFop+f7YuL5VBQi2Zmry8vZltbopWVtYOD6MPD1qKi
wXt70YOD2S8vi8bG1m9vzoOD4EVFe0VFc3t74mtr0y8vRVtbuCUlVktLg2ZmtZKS5W9vrzc3
knt7vn9/21tbi2Zmpbi4zltbqXNzrD4+nCUlh1ZWuHt7uHNz0QAAf6+vyays729vyWFhzG9v
w3Nz2VZWshkZRT4+h3Nzw8PD9Li48S8vjiH+GlNreWxpbmUgU29hcmluZyBDbHViLCBJbmMu
ACwAAAAAeABfAAAI/gCXAAAgkCADgggNGhRYEOESBgwHPixI8WBEhQIhStyoMSFFjwA0Zvz4
0aFJkw89Qsw4EKNIiyATynwJsuLIjSlzhizpECbGnyQ3xry5MCTOlihryry4JKLTpE8nHg0a
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
ekNGXJ6MipHSHijIYpuzkMElKUwrEwEBADs=
--------------060802060109030504000007
--------------030206090606080704090500--
EOM

  open (SENDMAIL, "|-")
	|| exec ('/usr/sbin/sendmail', '-t', '-oi');
  print SENDMAIL $invoice; 
  close (SENDMAIL);
  }


__END__


