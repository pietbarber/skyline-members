#!/usr/bin/perl

main: {
  Init();
  if ($q->param) {
    print "do something!";
    %magic = (
	'image/jpg' => '.jpg',
	'image/jpeg' => '.jpg'
	);

    for ($q->param) {
      printf "%s => %s<br>", $_, $q->param($_);
      }
    umask ('002');
    $filename = $q->upload(file_upload);
    $filedir = "/var/www/skyline/html/INCOMING/";
    $canonical_name = $q->param('filename');
    $canonical_name =~ s/[^A-Za-z\.\-0-9]//g;
    $canonical_name =~ s/^\.*//g;
    $canonical_name =~ s/(\..+)$//;
    $canonical_extension = $magic{$q->uploadInfo($filename)->{'Content-Type'}};
    print $q->uploadInfo($filename)->{'Content-Type'};
    $fileout = $filedir . $canonical_name . $canonical_extension;
    print "<br>Fileout: $fileout<br>";
    open (OUTFILE, ">$fileout")
	|| die ("Couldn't write file! $!\n");
    while (<$filename>) {
      print OUTFILE $_;
      }
    close OUTFILE;
    print qq(<img src = "/INCOMING/) . $canonical_name . 
	$canonical_extension .	  qq("><br>);
    }
  print_form();
  };



sub Init {
  use CGI;
  $q=new CGI;
  print $q->header;
  }


sub print_form {
  if ($q->param) {
    print $q->start_html (
	-title => "Upload a file",
	-bgcolor => "#FFFFFF"
        );
    }
  printf qq(
%s
<h1>Please do not upload logsheets here</h1>
<table border =1 bgcolor ="#F0F0F0">\n
<tr>
  <td>Input Filename:</td>
  <td>%s</td>
</tr>
<tr>
  <td>Upload File:</td>
  <td>%s</td>
</tr>

<tr>
  <td colspan =2 >%s</td>
</tr>
</table>
%s
),
	$q->start_multipart_form,
	$q->textfield(
		-name =>'filename',
		-size => 30
		),
	$q->filefield(
		-name =>'file_upload', 
		-default => 'foo.html',
		-size => 50,
		-maxlength => 80
		),
        $q->submit,
	$q->end_form;
  }
