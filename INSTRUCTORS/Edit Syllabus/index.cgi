#!/usr/bin/perl

	# Little program to allow the Instructors
	# to edit the Training Syllabus Lesson Plans
	# that are located on the club website
	# under http://skylinesoaring.org/TRAINING/Syllabus/

$|++;
use CGI qw(:standard);
use DBI;
use strict;
my ($dbh);
connectify();
	# The description for all the fields in the syllabus are stored in 
	# the database, so we'll go fetch those now, and put them into %lesson_plans
my %lesson_plans = fetch_lessons('select number, title from syllabus_contents');
my $javascript=javascript();

	# If the commit button has been pressed, we'll be inserting the new stuff 
	# into the text file for that field, email the differences. 
if (param('Commit')) {
  print header();
  print join ("\n", 
	start_html(
		-title => "Commit Page Changes"
		),
	include('left-menu.scrap'),
	h1("Committing Changes"),
	);
  email_differences();  
  commit_finished_page();
  }
	# Show what the page would look like after the commit. 
elsif (param('Preview')) {
  print	header();
  print join ("\n", 
	"<html><head><title>Preview Your Changes</title>\n",
	$javascript,
	"</head>\n",
	include('left-menu.scrap'),
	h1("Preview Changes"),
	);
  show_content();
  enter_data_table();
  }

elsif (param('edit_lesson')) {
  print	header();
  print	join ("\n", (
	"<html><head><title>Update Syllabus Page</title>\n",
	$javascript,
	"</head>\n",
	include('left-menu.scrap'),
	h1("Update Syllabus Page"),
	p("Edit The lesson plan below. Once done, either hit 'preview' or 'Commit'")
	));
  read_lesson_plan_file(param('edit_lesson'));
  enter_data_table();
  print h2("Or, if you want to edit a different lesson...");
  }

else {
    print join ("\n",
        header(),
	start_html(-title => "Select a lesson Plan"),
        include('left-menu.scrap'),
        h1("Select a Lesson Plan to Edit"),
        );
  }

select_lesson_plan();
print include ('footer.scrap');
print end_html();
exit;


sub show_content {
  print "The final product will look much like what you see in this box. If you like it, hit the 'Commit' button below.  If it needs further editing, feel free to update what is necessary in the edit area below. "; 
  print '<table border="1">';
  print "\n<tr><td>\n";
  #print open_lesson_plan(param('edit_lesson'));
  print param('text');
  print "</td></tr>\n";
  print "</table>";
  }

sub commit_finished_page {
  print p("OK, trying to save your work...");
  my ($filename) = sprintf ("/var/www/skyline/html/TRAINING/Syllabus/%s.scrap",
	param('edit_lesson')
	);
  if ( ! exists $lesson_plans{param('edit_lesson')}) {
    h1("Hey! I can't edit that lesson plan " . param('edit_lesson') . " ($filename) What kind of trickery are you doing here?" ); 
    }
  if ( ! -w $filename) {
    h1("Your knuckleheaded webmaster doesn't permit this program to write to that Syllabus file. Shame on him.  Save failed.");
    }
  open (OUTPUT, ">$filename" )
	|| die ("Something unexpected happened when I tried to write.  This was supposed to work. !$ \n");
  print OUTPUT param('text');
  close (OUTPUT);
  print h1("Page saved.");
  printf '<a target="new_window" href="http://skylinesoaring.org/TRAINING/Syllabus/%s.shtml">view your finished product.</a>',
	param('edit_lesson');
  print h1("Edit Another Lesson Plan");
  }


sub today {
	# What is today?
  my @today = localtime; 
  sprintf ("%4.4d-%2.2d-%2.2d", $today[5]+1900, $today[4]+1, $today[3]);
  }

sub select_lesson_plan {
	# Please to selecting the lesson plan you wanna work on. 
  print start_form();
  print "<br><b>Select Lesson Plan: </b>\n";
  print popup_menu (
	-name => 'edit_lesson', 
	-values => [sort keys (%lesson_plans)],
	-labels => \%lesson_plans
	);
  print submit(
	-name => 'Select',
	-value => 'Select'
	);
  print "\n";
  print end_form();
  }

sub enter_data_table {
  print h2("Lesson Plan " . $lesson_plans{param('edit_lesson')});
  print start_form();
  print "<b>Edit Content:</b><br>\n";
  print hidden ('edit_lesson');
  print textarea(
	-name => "text",
	-rows => "30",
	-cols => "80",
	-scroll => "auto",
	-id => 'elm1'
	);

  print "<b>Briefly describe what you're changing (Won't be stored)</b><br>\n";
  print textfield (
	-name => "description", 
	-size => 80,
	-maxlength => 80
	);

  print "\n<br>Preview before commit: ";
  print submit(
	-name => 'Preview',
	-value => 'Preview'
	);
  print "\n";

  print "\n<br>Save and Commit: ";
  print submit(
	-name => 'Commit',
	-value => 'Commit'
	);
  print "\n";
  print end_form();
  }

sub open_lesson_plan {
  my ($lesson_plan) = shift;
  my ($answer);
  open (LESSON, "/var/www/skyline/html/TRAINING/Syllabus/$lesson_plan.scrap")
	|| die ("Unfortunately, I couldn't open the lesson plan file. (/var/www/skyline/html/TRAINING/Syllabus/$lesson_plan.scrap)  Doh. $!"); 
  while (my $line = <LESSON>) {
    $answer .= $line; 
    }
  close(LESSON);
  $answer;
  }

sub read_lesson_plan_file {
  my $lesson_plan = shift; 
	warn ("I'm going to read $lesson_plan from /var/www/skyline/html/TRAINING/Syllabus/$lesson_plan.scrap");
  my $answer;
  if ($lesson_plans{$lesson_plan}) {
    $answer=open_lesson_plan($lesson_plan);
    }
  else {
    die ("You tryin to hack me? There's no such lesson plan!\n");
    }
  if (param('text') !~ /\w/ ) { 
    param('text', $answer);
    }
  $answer;
  }


sub connectify {
	# Just connect to the database. 
  my $driver = "DBI::Pg";
  my $database = 'skyline';
  $dbh = DBI->connect("DBI:Pg:dbname=skyline")
        || die ("Can't connect to database $!\n");
  }


sub include {
	# Pull file from the INCLUDES directory
	# output of subroutine is that file.
  my $file = shift;
  my $title = shift;
  my $answer;
  open (INCLUDE, "/var/www/members/html/INCLUDES/$file"); 
  while (my $line = <INCLUDE>) {
    $answer .= $line;
    }
  close (INCLUDE);
  $answer;
  }


sub javascript {
  my $answer=<<EOM;
<!-- TinyMCE -->
<script src="//tinymce.cachefly.net/4.0/tinymce.min.js"></script>
<script>
	tinymce.init({
		selector: "textarea",
			plugins: [
				"advlist autolink lists link image charmap print preview anchor",
				"searchreplace visualblocks code fullscreen",
				"insertdatetime media table contextmenu paste"
			],
		toolbar: "insertfile undo redo | styleselect | bold italic underline superscript subscript| alignleft aligncenter alignright alignjustify | bullist numlist outdent indent | link image",
		autosave_ask_before_unload: false,
		});
</script>
EOM
  $answer;
  }



sub fetch_lessons {
        # Fetch an assoc.array of members.
  my %answer;
  my $row;

  my $get_info = $dbh->prepare(
        qq(select number,title from syllabus_contents;));
  $get_info->execute();
  $answer{'intro'}='Introduction Essay'; 
  $answer{'materials'}='Required Materials'; 
  while ( my $row = $get_info->fetchrow_hashref ) {
    next if ($row->{'number'} !~ /[a-zA-Z]$/);	# We can only edit the ones with letters in them, like 1d, 1e, etc.
    $answer{$row->{'number'}}= sprintf ("%s -- %s", $row->{'number'}, $row->{'title'});
    }
  %answer;
  }


sub email_differences { 
	# First, get input, which is nothing. 
	# second, scrape through param
	# third, fetch previous stuff in database 
	# fourth, compare and contrast differences
	# fifth, construct these differences in an email 
	# sixth, send out into the email stream for 
	#        the instructors to read at their leisure. 

	# If this is a new question, don't bother making a comparison. 
	#   just crow about the new question and the available options. 

	# Make sure to include a link for the instructors to let them 
	# log right back in and update it if they feel it's necessary. 

  my ($email_to) ='instructors@skylinesoaring.org'; 
  my ($syllabus_list) ='syllabus@skylinesoaring.org'; 
  #my ($email_to) ='pbarber@skylinesoaring.org'; 
  #my ($email_to) ='testers@skylinesoaring.org'; 

  my ($random_num);
  my (@allow_chars) = (0..9);
  for (1..24) {
    $random_num .= $allow_chars[int(rand($#allow_chars))];
    }
  my $content; 
  my $old_content=read_lesson_plan_file(param('edit_lesson'));
  my $new_content=param('text'); 
  my $description=param('description'); 
  my %handle_labels = fetch_members(); # allows me to convert handles to names
  my $user=$handle_labels{$ENV{'REMOTE_USER'}};
  my ($qnum) = param('qnum'); 
  $content =<<EOM; 
Training Syllabus content has been updated:
<h2>Update By:</h2>
$user
<h2>Description of Changes</h2>
$description
<h2>Old Content</h2>
<table border="1" bgcolor="#e8e8e8">
$old_content
</table>
<h2>New Content</h2>
<table border="1" bgcolor="#e8e8e8">
$new_content
</table>

EOM

  open (SENDMAIL, "|-") || exec ('/usr/sbin/sendmail', '-t', '-oi'); 
  printf SENDMAIL <<EOM;
From: "Skyline Instructors" <webmaster\@skylinesoaring.org>
MIME-Version: 1.0
X-Accept-Language: en-us, en
To: <$email_to>
CC: <$syllabus_list>
Subject: Training Syllabus Content Update
Content-Type: multipart/alternative;
 boundary="------------$random_num"
This is a multi-part message in MIME format.
--------------$random_num
Content-Type: text/html; charset=ISO-8859-1
Content-Transfer-Encoding: 7bit

<body bgcolor="#ffffff" text="#000000">
$content

Skyline Instructors may Update Syllabus Content by going to: <br>
<a href = "http://members.skylinesoaring.org/INSTRUCTORS/Edit%20Syllabus/">http://members.skylinesoaring.org/INSTRUCTORS/Edit%20Syllabus/</a>
--------------$random_num--

EOM

  close (SENDMAIL);
  print "Email sent detailing the changes. "; 
  } 

sub fetch_members {
        # Fetch an assoc.array of members.
  my %answer;
  my $status = shift;
  my $row;
  my ($append);
  if ($status eq 'active') {
    $append=qq(where memberstatus != 'I' and memberstatus !='N' );
    }
  my $get_info = $dbh->prepare(
        qq(select handle, lastname, firstname, middleinitial, memberstatus, namesuffix from members $append));
  $get_info->execute();

  while ( my $row = $get_info->fetchrow_hashref ) {
    if ($row->{'namesuffix'} =~ /\w/) {
    $answer{$row->{'handle'}}= sprintf ("%s %s, %s %s",
        $row->{'lastname'},
        $row->{'namesuffix'},
        $row->{'firstname'},
        $row->{'middleinitial'},
        );
      }
    else {
    $answer{$row->{'handle'}}= sprintf ("%s, %s %s",
        $row->{'lastname'},
        $row->{'firstname'},
        $row->{'middleinitial'},
        );
      }
    }
  %answer;
  }


__END__

        Table "public.instructor_reports"
    Column    |         Type          | Modifiers
--------------+-----------------------+-----------
 handle       | character varying(20) |
 firstname    | character varying(20) |
 lastname     | character varying(20) |
 report_date  | date                  |
 instructor   | character varying(20) |
 lastupdated  | integer               |
 report       | text                  |
 show_student | boolean               |
