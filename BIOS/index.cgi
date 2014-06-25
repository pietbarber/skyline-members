#!/usr/bin/perl
	# Bio Edit program
	# Outline: 
	# 	Connect to database
	# 	pre-load a list of the member's handles
	# 	pre-load a list of admins, based off of the access table
	# 	Check the param from CGI
	# 	if param for 'member' is set, show that member's biography
	#	if param for 'edit' is set, and your'e an admin
	#		or edit is set and you're the same user
	#		then edit that user 
	# 	if you're an admin, and you don't say anything
	# 		show a list of users to edit
	#	If you're not an admin, and you don't say anything
	#		show a list of members to view
	#	If param commit is present, 
	# 		throw all the junk in edit_bio into the DB. 

	# Always Flush Output Buffers
$|++;
	# Always be strict in what you say
use strict;
	# Use CGI stuff
use CGI qw/:standard/;
	# Do some connectivity to the database. 
use DBI;
	# This variable will be used for database transactions
my ($dbh);
	# Please to be connecting to the database
connectify();
	# And fetch all users and admins, throw them in an assoc.array. 
my (%username) = fetch_members();
my %admins = fetch_admins(); 

	##################################
	#          Main IF tree:         # 
	##################################

if (param('member')) {
		# View bio if the 'member' variable has something in it. 
	starter(sprintf("%s",$username{param('member')}), 1);
  	view_bio(param('member')); 
	print p(qq(<a href="?view_list=1">See All Member Bios</a>)); 
	footer();
  	}

elsif (param('edit') && (param('edit') eq $ENV{'REMOTE_USER'} || $admins{$ENV{'REMOTE_USER'}})) {
		# If you're an admin and you're editing somebody
		# or if you're a nobody and you're editing yourself
	starter("Edit Biography");
	edit_member(param('edit'));
	footer();
	}

elsif ((param('handle') eq $ENV{'REMOTE_USER'} && param('Commit') && param('edit_bio'))) {
		# So you're updating yourself, and you said "Commit"? 
		# OK, we'll let you write to the database. 
		# And then we should print out your bio when done. 
	starter ("Saving Bio for " . $username{param('handle')},1);
	commit_bio(param('handle'));
	print_bio(param('edit_bio'));
	footer();
	}

elsif ((param('handle') && $admins{$ENV{'REMOTE_USER'}} && param('Commit') && param('edit_bio'))) {
	starter ("Saving Bio for " . $username{param('handle')},1);
	commit_bio(param('handle'));
	print_bio(param('edit_bio'));
	footer();
	}

elsif (param('view_list')) {
		# So you want to see who we got, eh? 

	if ($admins{$ENV{'REMOTE_USER'}}) {
			# If you're an admin
			# And you specified That you want to view
			# the list of members (param('view_list')), 
			# Then we'll show you whoze got a bio. 
			# And let you edit them too
		starter("Edit Member Bios",1);
		print h2("Active Members");
		show_members_to_edit('active');
		print h2("Inactive Members");
		show_members_to_edit('inactive');
		}
	else {
			# If you're not an admin
			# And you specified That you want to view
			# the list of members (param('view_list')), 
			# Then we'll show you whoze got a bio. 
		starter("Member Biographies");
		print h2("Active Members");
		show_members_list('active');
		print h2("Inactive Members");
		show_members_list('inactive');
		}
	footer();
	}

else {
	starter("Showing Your Biography",1);
	show_bio();
	footer();
	}


	##################################
	#          Subroutines           #
	##################################

sub commit_bio {
		# The commit_bio can come from two forms: 
		# if the fetched_status field is set, then we presume that we have to update the record
		# instead of inserting it. 
	my ($user) = shift;
	my ($time) = scalar(localtime (time)); 
	if (param('fetched_status')) {
		my ($sth) = $dbh->prepare(sprintf qq(
			delete from bios where handle='%s'
			), $user) or die $dbh->errstr;
		$sth->execute() or die $dbh->errstr;
		}
		my ($sth) = $dbh->prepare(q(
			insert into bios (handle, lastupdated, bio_body) values (?, ?, ?)
			)) or die $dbh->errstr;
		$sth->execute($user, $time, param('edit_bio'))
			or die $dbh->errstr;
	print p(q(Successfully submitted to the database. ));
	print p(qq(<a href="?view_list=1">See All Member Bios</a>)); 
	footer();
	}

sub fetch_admins {
        # Fetch an assoc.array of people in the access table
	# who have 't' for edit_members. 
	# If they can edit members, 
	# then they can edit bios too.
  my %answer;
  my $row;

  my $get_info = $dbh->prepare(
        qq(select handle from access where edit_member=true));
  $get_info->execute();

  while ( my $row = $get_info->fetchrow_hashref ) {
    $answer{$row->{'handle'}}= 1; 
    }
  %answer;
  }
 


sub fetch_members {
        # Fetch an assoc.array of members.
	# No regard to if this person was active or not.  Even temporary or full. 
	# If he's in our DB, he gets a handle. 
  my %answer;
  my $get_info = $dbh->prepare(
        qq(select handle, lastname, firstname, middleinitial, memberstatus, namesuffix from members));
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

sub connectify {
	# Please to be connecting to the database 
	# and putting handle for connectionage
	# into $dbh; 
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
	print $answer;
	}

sub javascript {
	# There is lots of ugly JavaScript that needs to be included in the headers. 
	# This is just that javascript included nicely. 
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
		relative_urls : false,
        	convert_urls: false,
		});
</script>
EOM
  $answer;
  }



sub starter{
	# Gets the HTML started, prints the HTTP headers
	# Prints the HTML Headers
	# Prints the skyline left menu
	my $title=shift;
	my $nojs=shift;
	my $javascript=javascript() unless $nojs;
	$title ||= "Member Biographies";
	print header();
	print join ("\n",
		"<html><head><title>$title</title>\n",
		$javascript,
		"</head>\n",
		);
        include('left-menu.scrap'),
	print h1("$title");
  	}

sub footer {
	# Wraps up any HTML
	# Includes the Skyline Footer
	# Always exits.
 
	include ('footer.scrap');
	print end_html();
	exit;
  	}

sub show_bio {
		# User is defined as the remote user
		# Go to the database with fetch_bio and git it. 
		# If tehre's something from the fetch_bio, 
		# print it out. 
		# If not, give the user the opportunity to create a Biography. 

	my ($user) = $ENV{'REMOTE_USER'};
	my (%answer)=fetch_bio($user);

	if ($answer{'bio_body'}) {
		print_bio($answer{'bio_body'});
		print p(qq(<a href="?edit=$user">Update this Bio</a>));
		print p(qq(<a href="?view_list=1">See All Member Bios</a>)); 
		footer();
		}

	elsif ($user eq $ENV{'REMOTE_USER'}) {
		print h2(qq(You don't have a biography here!\n));
		print start_form();
		print hidden ('edit', $ENV{'REMOTE_USER'});
		print submit (
			-value=> "Start One Now"
			); 
		print end_form();
		print footer();
		}
	else {
		print h2(qq($user doesn't have a Bio.)); 
		}
  	}

sub show_members_to_edit {
		# For those with the power, 
		# This allows a user to view a list of the biographies on-line. 
		# Should be just a table with names, and the status of the bio (or not)
		# And some way for us to edit each of these fellows. 
	if ($admins{$ENV{'REMOTE_USER'}} !=1 ) {
		h1(qq(You are not suposed to be here. ));
		footer();
		}	
	my (%answer);
 	my ($sql_input)=q(members.memberstatus != 'I' and members.memberstatus != 'N');
	my ($input) = shift; 
	if ($input eq 'inactive') {
 		$sql_input=q(members.memberstatus = 'I' or members.memberstatus = 'N');
		}
	my $get_info = $dbh->prepare(
	#qq(select handle, lastupdated from bios));
	qq(select bios.handle, bios.lastupdated::date, members.memberstatus from bios inner join members on members.handle=bios.handle
		where $sql_input));
	$get_info->execute();
	print qq(<table border="1">\n);
	printf qq(<tr bgcolor="#C8C8C8"><td>Name</td><td>Edit</td><td>View</td><td>Last Updated</td></tr>\n);
	while ( my $row = $get_info->fetchrow_hashref ) {
		$answer{$username{$row->{'handle'}}} = 
			sprintf (qq(<tr><td>%s</td><td><a href="?edit=%s">Edit</a></td><td><a href="?member=%s">View</a></td><td>%s</td></tr>\n),
			$username{$row->{'handle'}},
			$row->{'handle'},
			$row->{'handle'},
			$row->{'lastupdated'}
			);
		}
	for (sort keys (%answer)) {
		print $answer{$_}
		}
	print qq(</table>\n);
	print start_form();
	print popup_menu (
		-name	=> "edit",
		-values => ["Create Bio", sort by_val keys (%username)],
		-labels => \%username
		);
	print submit (
		-value=> "Go"
		); 
	print end_form();

  	}

sub by_val {
	# A subroutine to sort the handles in the %username array
	# but sorted by the persons' last name, first name instead of the contents of the handle. 

	# Only good for the %username associative array, unfortunately. 
	$username{$a} cmp $username{$b};
	}

sub show_members_list {
		# For the muggles, 
		# This allows a user to view a list of the biographies on-line. 
		# Should be just a table with names, and the status of the bio (or not)
	my ($input) = shift; 
 	my ($sql_input)=q(members.memberstatus != 'I' and members.memberstatus != 'N');
	if ($input eq 'inactive') {
 		$sql_input=q(members.memberstatus = 'I' or members.memberstatus = 'N');
		}
	my (%answer);
	my $get_info = $dbh->prepare(
	#qq(select handle, lastupdated from bios));
	qq(select bios.handle, bios.lastupdated::date, members.memberstatus from bios inner join members on members.handle=bios.handle
		where $sql_input));
	$get_info->execute();
	print qq(<table border="1">\n);
	printf qq(<tr bgcolor="#C8C8C8"><td>Name</td><td>Last Updated</td></tr>\n);
	while ( my $row = $get_info->fetchrow_hashref ) {
		$answer{$username{$row->{'handle'}}} = 
			sprintf (qq(<tr><td><a href="?member=%s">%s</a></td><td>%s</td></tr>\n),
			$row->{'handle'},
			$username{$row->{'handle'}},
			$row->{'lastupdated'}
			);
		}
	for (sort keys (%answer)) {
		print $answer{$_}
		}
	print qq(</table>\n);


  	}

sub print_bio {
	my ($bio) = shift;
	printf qq(<table border="0"> <tr><td>$bio</td></tr></table>\n),
	}


sub view_bio {
	my ($user) = shift; 
	my (%answer);
	if (param('edit_bio')) {
		print_bio(param('edit_bio'));
		}
	else {
		%answer = fetch_bio($user);
		print_bio($answer{'bio_body'}); 
		}
  	}

sub fetch_bio {
		# For any given User, fetch his handle from the database. 
		# Print his bio out to the screen. 
	my ($user) = shift; 
	my (%answer);
	my $get_info = $dbh->prepare(
	qq(select handle, lastupdated, bio_body from bios where handle='$user'));
	$get_info->execute();
	while ( my $row = $get_info->fetchrow_hashref ) {
		$answer{'bio_body'}= $row->{'bio_body'};
		$answer{'lastupdated'}=$row->{'lastupdated'};
		}
	$answer{'fetched_status'} =1; 
	%answer;
	}

sub edit_member {
	my $user = shift; 	# Should be in the form of a handle (userid)
	my %fetched_bio = fetch_bio($user);
	param('edit_bio', $fetched_bio{'bio_body'}); 
	print h2(sprintf("Edit Bio for %s", $username{$user})); 
	print h3(sprintf("This bio was last updated on %s", $fetched_bio{'lastupdated'})) if ($fetched_bio{'lastupdated'});
	print start_form();
	print hidden('fetched_status', 1) if $fetched_bio{'fetched_status'};
	print p(qq(In order for the rich editing,), strong("Popups Have to Be Enabled!"), qq(Sorry, I hate pop-ups too, but you will lose all the functionality of this rich text editor if you have popups blocked for members.skylinesoaring.org.  You will have equal loss in functionality if you have Javascript disabled. \n)); 
	print p("Edit Content in the textarea below.  If you have Javascript enabled, you can do all sorts of mark-up, including pictures, HTML, pasting in word documents.  If you don't know what a button does, just put your mouse over the icon for a few seconds, and a hint for the function will show.  Once You're done, hit Preview to review the content, or Commit to save your work in the database.  \n");
	print p(qq(Do you want to put a picture on your bio?\n));
	print p(qq(You can also use a free photo upload service like <a href="http://picasaweb.google.com">Google's Picasa</a>, <a href="http://www.imgur.com">Imgur</a>, or <a href="http://www.flickr.com">Flickr</a> to upload pictures. We can even have a link to a facebook picture, if you so choose. Once you have the URL for your photo, you can include the image in-line within your bio page. \n));  
	print p(qq(Further help can be found <a href="javascript:tinyMCE.execInstanceCommand('mce_editor_0','mceHelp',false);">here</a>.  If you need a tutorial, please ask <a href="mailto:webmaster\@skylinesoaring.org">webmaster\@skylinesoaring.org</a>\n));
	print hidden ('handle', $user);
	print textarea (
		-name => "edit_bio",
		-rows => "30",
		-cols => "80",
		-scroll => "auto", 
		-id => 'elm1'
		);
	print "\n<br>Preview Before Commit: "; 
	print button (
		-name => 'Preview', 
		-value => 'Preview',
		-onclick => "javascript:tinyMCE.execInstanceCommand('mce_editor_0','mcePreview');"
		);
	print "\n";
	print submit (
		-name => 'Commit',
		-value => 'Commit',
		);
	print "\n";
	print end_form();
	}

__END__




