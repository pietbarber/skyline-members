#!/usr/bin/perl
warn "Beginning program. ";
########################################

# To Do:

# Don't use shitty Berkely DB


########################################

# Done:

# Allow multiple towpilots per day
# - The sort uniq routine doesn't work. (does now)
# - Preview mode: Edit button doesn't work. :(
# - Insert cool RosterFuhrer picture
#   Ensure that RosterFuhrer has the u umlaut instead of just 'u'
# - Ensure it's documented well. (Ongoing)
# - Get roster stuff to 'commit' to dbm
	# Done, but used CGI instead -- the dbm
	# required WAY too much programming. 
	# and I'm lazy.  (19 April 2000)
# - put in a box at the top where the RosterFuhrer speaks:
	# This textbox will appear at the top of any roster 
	# list. It will print the comic strip picture
	# of the RosterFuhrer if there is anything
	# to be said.  I think this is really cool. :)
# - Put month headers, wherever there is a new month.
	# Done for preview mode
	# Done final mode
	# Done for the data input mode. 
##########################################

main: {
  Init();

  get_info();

  if ($q->param('Commit All Changes to Duty Roster') ||
	$q->param('submit_status') eq 'Commit') {
    write_roster();
    template('write');
    template();

    system ('cp', '/var/www/skyline/html/ROSTER/index.shtml',
	sprintf('/var/www/skyline/html/ROSTER/old/backup-%s.shtml', time));
    }

  elsif ($q->param('submit_status') eq 'Commit and Email') {
    write_roster();
    template('write');
    print <<EOM;
<script language="JavaScript">
<!--
alert ('Sending Email... Email to Membership Sent.');
alert ('The roster has been updated.');
//-->
</script>
EOM
    template();
    mkmail();
    }

  elsif ($q->param('submit_status') eq 'Edit Ops Days'
	|| $q->param('submit_status') eq "Update Days") {
    edit_ops_day();
    }

  elsif ($q->param('submit_status') eq 'Edit') {
    edit_roster();
    }

  elsif ($q->param('submit_status') eq "Return to Start") {
    $q->delete_all();
    read_roster();
    edit_roster();
    }    

  elsif ($q->param) {
	java_alert("Showing preview.");
    template('preview');
    }

  else {
    $q->delete_all();
    read_roster();
    edit_roster();
    }

  show_form();  
  exit;
  };


sub mkmail {
  system ("/home/httpd/bin/mkmail.pl");
  }

sub get_info {
	# Gets information out of the dbm
	# files.  Does not get the information
	# about who does duty on which day, 
	# but rather, brings forth the information
	# on what days are duty days, what persons are
	# available for the duty of towpilot,
	# instructor, etc.,  and how many 
	# times each person has done duty on 
	# a specific day. 

	# fer instance: $towpilots{'Bentley'} == 0
	# There is a towpilot named Bentley, he
	# has done towpilot chores once this year. 
	
	# print $duty{'Barber'}	
	# would show how many times Barber has done
	# Do Duty this year. 

  %towpilots = fetch_db ('towpilot');	
  %towpilots1 = fetch_db ('towpilot');	
  %towpilots2 = fetch_db ('towpilot');	

  %instructors = fetch_db ('instructor');
  %inst2 = fetch_db ('instructor');

  %duty = fetch_db ('dutyofficer');

  %ados = fetch_db ('ado');

  dbmopen (%ROSTER, "$dbdir/roster", 0666) || die ("Unable to open \%ROSTER $dbdir/roster $!\n");
  %roster = %ROSTER;
  dbmclose (%ROSTER);
  }



sub uniq {
  local (@outarray, $arr);
  for $arr (0..$#_) {
    unless ($_[$arr] eq $_[$arr-1]) {
      push (@outarray, $_[$arr]);
      }
    }
  @outarray;
  }

sub by_num {
  $a <=> $b;
  }

sub tp_sort {
  $towpilots{$a} <=> $towpilots{$b} 
	||
  $a cmp $b;
  }

sub inst_sort {
	# When we need to sort by the times
	# an instructor has done duty, followed
	# by alphabetical listing. lowest number
	# of duties at the beginning of the sorted
	# answer. 

	# Fer instance:
	# So if Bentley and Kellett both have done	
	# duty 3 times, then Bentley would be listed
	# before Kellett, but both would be listed 
	# above Neitzey, because he has only 1 instructor
	# duty this year. 

  $instructors{$a} <=> $instructors{$b}
	||
  $a cmp b;
  }

sub do_sort {
  $duty{$a} <=> $duty{$b}
	||
  $a cmp $b;
  }

sub ado_sort {
  $ados{$a} <=> $ados{$b}
	||
  $a cmp $b;
  }



sub show_roster {

	# This subroutine shows the roster in its printed format. 
	# you can use this within any other HTML.  The scope
	# of this HTML is just to print the title, and 
	# valid information.  Javascripts, applets, html headers,
	# stuff like that aren't addressed in this subroutine. 
	
	# This subroutine takes two different arguments --
	# If 'preview' is an argument, the header information
	# is a little different.  The title says "preview"
	# and we tell teh Rosterfuhrer that it hasn't been submitted yet.


	# print out the (Preview Mode) header, if we're
	# showing the preview version.

  local($last_month);

  if ($_[0] eq 'preview') {
    print "<h1>Duty Roster for Skyline Soaring Club (Preview)</h1>\n";
    print $q->start_form;
    }

	# Print out the regular version if it's not preview mode. 

  else {
    print "<h1>Duty Roster for Skyline Soaring Club</h1>\n";
    printf ("<h2>Last Updated by %s on %s</h2>\n", 
	$ENV{'REMOTE_USER'}, 
	scalar(localtime(time)));
    }

	# Start printing out the table with all the information.

  print "<table border = 1>\n";

  if ($_[0] eq 'preview') {
    print <<EOM;
<script language="JavaScript">
alert('RosterMeister: Preview mode. To save all info, hit "commit" in the control panel.');
</script>

EOM
    }


	# If the RosterFuhrer has something to say, make
	# the icon for the RF on the left, and make a cartoon
	# bubble with what he has to say.  If there is nothing
	# to be said, the RF icon won't show up at all. 

	# We take the RFs input, and massage it a lot to make it 
	# suitable for HTML prime time. 
	
	# First, convert any <'s to &lt;s, and >'s to &gt;s
	# this way, he won't inadvertently make an HTMl tag
	# that does nothing, and doesn't show up. 
	
	# Next convert any carriage-return newline combinations to
	# the html <p> tag. 

	# Next convert any word RosterFuhrer to RosterFuhrer with
	# the u umlaut. 

	# Convert any "http://stuff" to a real URL. 
	
	# Last, convert any mail addresses to hyperlinked 
	# email addresses. 

  if ($q->param('RosterMeister') =~ /\w/) {
    local ($tempval) = $q->param('RosterMeister');
    $tempval =~ s#<#&lt;#g;
    $tempval =~ s#>#&gt;#g;
    $tempval =~ s#\r\n+#\n<p>#g;
    $tempval =~ s#RosterFuhrer#RosterF&uuml;hrer#gi;
    $tempval =~ s#\s(http://\S+)\s# <a href = "$1">$1</a> #g;
    $tempval =~ s#\s(\S+\@[A-Za-z0-9\-\.]+)\s*# <a href = "mailto:$1">$1</a> #g;

	# Here's where we actually print out the left icon
	# of the RosterFuhrer, along with the text that he has
	# to say.   Remember, we won't be here unless the 
	# field 'RosterFuhrer' has something in it. 

    print "<tr><td colspan = 6><font size=+2><b>The RosterMeister Speaks</b></font><br>\n";
    print "<table border = 0 cellpadding = 0><tr valign = top width = 90%><td valign = top rowspan=2>\n";
    print qq!<img src = "/IMAGES/rf-yap.png" width = 120 height =151></td>\n!;
    print qq!<td height=30><img src = "/IMAGES/rf-line.png" width = 400></td></tr>\n!;
    printf ("<tr valign = top><td valign = top height=121><p>%s</td>\n</tr></table>\n</td></tr>\n", $tempval);
    }


	# Print the RosterFuhrer control panel if in preview
	# Mode. 
    $roster_linecount=0; 
    if ($_[0] eq 'preview') {
      print "<tr bgcolor = \"#E0E0E0\" valign = middle>";
      print "<td colspan = 2><h2>RosterMeister Control Panel:</h2></td>\n";
      printf "<td colspan = 4 align = left>Keep Changes:<br> %s | %s | %s <br>\n".
	"Lose Changes:<br> %s | %s</td></tr>",
	$q->submit(
		-label => 'Edit',
		-value => 'Edit',
		-name => 'submit_status',
		),
	$q->submit(
		-label => 'Commit',
		-value => 'Commit',
		-name => 'submit_status',
		),

	$q->submit(
		-label => 'Commit and Send Email',
		-value => 'Commit and Email',
		-name => 'submit_status',
		),

	$q->submit(
		-label => 'Edit Ops Days',
		-value => 'Edit Ops Days',
		-name => 'submit_status',
		),


      }


	# The keys for the roster  assoc.array were
	# defined in the get_info subroutine. 
	# those were defined in the dbm file that was
	# created by the program create_list.pl
	# which was created once, and should never 
	# need to be run again. 

	# Each key consists of a long string of numbers.
	# those numbers just happen to be the number of seconds
	# since 1970 on midnight of the date of a particular 
	# day of duty. 

	# Why did I choose this method?  It may sound stupid, 
	# but it's really quite powerful. Because it allows
	# me to use the perl function 'localtime()' which easily	
	# calculates dates based on seconds, I don't have to figure
	# out if the month of February has 28 or 29 days, if March has
	# 30 or 31, or August has 30 or 31.  I can also
	# quickly calculate what day of the week is involved many
	# many years in advance, quite easily. 

	# By adding 86400 to $_ we can get the next day (but I don't
	# do this anywhere in this subroutine)

	# Another advantage of this is I don't have to worry about 
	# unforseen problems, kind of like how the Y2K problem
	# was unforseen until it was almost too late. 

  for (sort by_num keys %roster)  {
	# The key is $_
	# Find out what the date is for the $_ field. 
    @date = gmtime($_);

	# calculate what the year, month, day, day of week
	# is for this value of $_;  Stuff it all into @dates;
    @dates = ($dotw[$date[6]], $date[4]+1, $date[3], $date[5]+1900);

	# Don't do anything earlier than today.
	# it doesn't make much sense to show
	# duty lists for previous duty days. 
    next if (($_+86400) < time); 


	# If we get here, and $first_month is blank,
	# then set it to the month for the date 
	# through this part of the for loop. 
	# This is a neat way of getting the 
	# calendar to stop when we get 3 months
	# ahead. 

    $first_month ||= $date[4];

	# And don't bother showing any more stuff
	# if we've elapsed three months of duty
	# Rosters. 

    last
	if ($date[4] == ($first_month + 3));

	# Below, Don't bother showing all these fields if
	# nothing is in them.  Note 'nothing' is not
	# the same thing as 'unassigned'.

    next if ($q->param('towpilot1-'.$_) eq '' &&
    	$q->param('instructor-'.$_) eq '' &&
    	$q->param('inst2-'.$_) eq '' &&
	$q->param('duty-'.$_) eq '' &&
	$q->param('ados-'.$_) eq '' );

	# If the field we're showing is not the
	# same as the last month, then 
	# we will print the header for the 
	# New month. 



    if ($date[4] > $last_month) {
      $last_month = $date[4];
      printf ("<tr><td colspan = 6 bgcolor = \"#444444\">&nbsp;<font ".
	"size=+2 color = \"#FFFFFF\"><b>%s</b></font></td></tr>\n", 
		$month[$date[4]]);

	# When we do that, we will print
	# the HTML column headers, so we are reminded
	# which column belongs to which job.

      print "<tr align = center>\n";
      print "<td align = right><b>Date</b></td>\n";
      print "<td><b>Tow Pilot 1</b></td>\n";
      #print "<td><b>Tow Pilot 2</b></td>\n";
      print "<td><b>Instructor</b></td>\n";
      print "<td><b>2nd Inst</b></td>\n";
      print "<td><b>Duty Officer</b></td>\n";
      print "<td><b>Asst. Duty Officer</b></td></tr>\n";

      }

	# By default, each row is only one high. 
    $rowspan = 1;

	# Except when we have a note for the day.  In 
	# That event, we have two rows per each  date
	# row header. That way, comments end up on the
	# next line in the same virtual row. 

    $rowspan = 2
	if ($q->param('notes-'.$_));

	# Print the table's row, with the date in the first cell,
	# which will be $rowspan cells high, with the date printed
	# out, like "Thursday, 12 April, 2000" or something like that.

    printf ("<tr>\n\t<td align = right rowspan=%s>%s,<br> %2.2d/%2.2d/%4.4d</td>\n", 
        $rowspan,
	@dates
	);



	# If duty is canceled for this day, 
	# Then say that duty is canceled. 
	# and don't show any persons on duty for that day. 

    if ($q->param('cancel-' . $_) eq 'ON') {
      print "<td colspan = 5 bgcolor = \"#F0DDDD\" align = center>".
	"<b> * * * Operations Canceled * * *</b></td>\n";
      if ($q->param('notes-' . $_)) {
        if ($q->param('notes-' . $_) =~ /<|>/) {
          local $tempval = $q->param('notes-' . $_);
          $tempval =~ s/</&lt;/g;
          $tempval =~ s/>/&gt;/g;
          $q->param('notes-' . $_, $tempval);
          }
        printf ("</tr>\n<tr><td align = left colspan=5 bgcolor = \"#F0DDDD\">" . 
	  "<b>Notes:</b> %s</td></tr>\n",
		$q->param('notes-'. $_)
		);
        }
      }


	# Otherwise, if we're not canceled, show
	# who is on duty for what job.  The columns
	# are in the order of towpilot, instructor,
	# duty officer, and ADO. 
    else {
      @duty_list = ( 
	$q->param('towpilot1-'.$_), 
	$q->param('instructor-'.$_), 
	$q->param('inst2-'.$_), 
	$q->param('duty-'.$_), 
	$q->param('ados-'.$_)
	);


	# For each item in the duty_list, 
	# change the output for (Open) to (Open) in red letters,
	# change the output for (Unassigned) to same, but 
	# italicized. 

      for (@duty_list) {
        s/(Open)/<span style="background-color: #FFFF00"><b>open<\/b><\/span><\/font>/;
        s/(Unassigned)/<i>Unassigned<\/i><\/font>/;
        }


	# print the fields in duty_list, one name per
	# each cell. 
      printf ("\t<td align = center>%s</td>\n\t<td align = center>%s</td>".
	      "\n\t<td align = center>%s</td>\n\t<td align = center>%s</td>\n".
	      "\n\t<td align = center>%s</td>\n",
		@duty_list
		);


	# If there are any notes for the day, 	
	# we will print them out now. 
	# Convert <'s to &lt;s and >'s to &gt;s. 

      if ($q->param('notes-' . $_)) {
        if ($q->param('notes-' . $_) =~ /<|>/) {
          local $tempval = $q->param('notes-' . $_);
          $tempval =~ s/</&lt;/g;
          $tempval =~ s/>/&gt;/g;
          $q->param('notes-' . $_, $tempval);
          }

        printf ("</tr>\n<tr><td align = left colspan=5><b>Notes:</b> %s</td></tr>\n",
		$q->param('notes-'. $_)
		);
        }
      }
	# End the row. 
    print "</tr>\n\n";


	# If the date is Sunday, 
	# Print an empty line for spacing. 
	# to separate it from the next week of duty. 

    printf "<tr><td colspan = 6>&nbsp;</td></tr>\n"
	if ($date[6] == 0);

	# Don't bother showing duty days till the end 
	# of time, 40 skyline soaring sessions ought 
	# to be enough.  We can expand this if we feel
	# it's necessary. 

    last
	if ($date[4] == ($first_month + 3));


	# Untested, supposed to not print out the next 
	# year's roster during the end of this year's flying
	# Season.  No sense in showing empty fields 
	# In January or February. 

    last
	if ($date[4] == 1 &&
	    $first_month > 10);
    $roster_linecount++;
    }

	# We're all done printing the information, 
	# so now it's time to close up the table. 

  print "</table>\n";

	# if we're in preview mode (from $_[0])
	# then print out all the hidden variables
	# that are applicable. 

  if ($_[0] eq 'preview') {
    $q->delete('Preview Page');

    include_hidden();
	## Fixme Need protections against early submit
	## without complete form being displayed.

    print $q->end_form;
    }
  print "* Denotes the ADO is also capable of being a Duty Officer\n<br>"; 
  }




	# Instead of writing another fully-featured	
	# subroutine, just run the same show_roster
	# subroutine with the 'review' argument. 

sub show_preview {
  show_roster('preview');
  }
  
sub java_alert {
return;
  for (@_) {
    chomp;
    }
  printf <<EOM, join (" ", @_);
<script Language="JavaScript">
<!--
alert('%s');
//-->
</script>
EOM
  }

sub edit_ops_day {
	# Subroutine to set up a special day of operations
	# Say there is a special Friday that we wouldn't
	# normally operate. 

  for (0..250) {
    $theday = (time+(86400 * $_)-(time % 86400));
    local($date) = scalar(gmtime($theday));
    $ops{$theday}=$dotw[$date[6]];
    $ops{$theday}=$date;
    }

  for (sort by_num keys (%ops)) {
    if ($q->param('del-' . $_) eq "ON") {
      java_alert("Deleting operations for ". scalar(gmtime($_)));
      delete($roster{$_});
      dbmopen (%ROSTER, "$dbdir/roster", 0666)
	|| java_alert ("Couldn't open the roster database!\n");
      %ROSTER=%roster;
      dbmclose(%ROSTER);
      }
    elsif ($q->param('add-' . $_) eq "ON") {
      java_alert(
	"Adding operations for", scalar(gmtime($_)), "\n");
      $roster{$_}=0;
      dbmopen (%ROSTER, "$dbdir/roster", 0666)
	|| java_alert ("Couldn't open the roster database!\n");
      %ROSTER=%roster;
      dbmclose(%ROSTER);
      }
    }

  print "<h1>Add/Delete Ops Days</h1>\n";
  print <<EOM;

<p><b>Instructions:</b> Below are the next 250 days of operations. <br>

<p>For the odd day that we need to create operations, like a Monday
holiday, or a special Wednesday operations, this is the page to use for
entering that information.  Just click on any days that need to be added,
and when you are done, you can hit the "Update Days" button at the bottom
of this page. Days that already have operations scheduled will be in
grey boxes.  If you feel the need to delete them, you may do so by
checking on the appropriate checkbox named "Delete."</p>

<p>After hitting update, you will return to this page, and you will notice
that the new operations days will be in grey boxes. To get back to the
"Edit Roster Page", just hit the 'Return to Start' button. </p>

<p>Deleting entries from this page removes them entirely from the roster
page.  After a day is deleted, it won't even show up on a roster duty
page at all.  So if you plan on cancelling operations for a day, you
should use the "Cancel Ops" checkbox instead.  The "Cancel Ops" checkbox 
is on the "Edit Roster" Page (Where you normally edit daily operations.</p>

EOM
  print "<table border =1>\n";
  print $q->start_form;
  $count = 0;
  for (sort by_num keys %ops) {
    local(@thisday) = gmtime($_);

    if (($count == 0) && ($thisday[6] != 0)) {
      print "<tr>\n";
      for (0..($thisday[6]-1)) {
        print "<td>&nbsp;</td>\n";
        }
      }
    $count++;

    if ($thisday[6] == 0) {
      print "<tr>\n";
      }
    elsif ($thidsay[6] == 6) {
      print "</tr>\n";
      }

    if (exists($roster{$_})) {
      $bgcolor = "#D8D8D8";
      $ops_day=1;
      $checkbox = $q->checkbox(
	  -label => " Delete", 
	  -value => "ON",
	  -name => "del-$_"
	  );
      }

    else {
      $bgcolor = "#FFFFFF";
      $ops_day=0;
      $checkbox = $q->checkbox(
	  -label => " Add", 
	  -value => "ON",
	  -name => "add-$_"
	  );

      }

    printf "<td bgcolor = \"%s\">%s: %s/%s/%2.2d<br>%s</td>", 
	$bgcolor, 
	$dotw[$thisday[6]], ($thisday[4] +1), 
	$thisday[3], (($thisday[5] + 1900) % 100),
	$checkbox;
#    printf "%s => %s<br>\n", $_, $ops{$_};
    }  

  printf "<tr><td colspan = 7 align = center>%s / %s</td></tr>",
    $q->submit (
      -label => "Update This Page",
      -value => "Update Days",
      -name => "submit_status"
      ),
    $q->submit (
      -value => "Return to Start",
      -label => "Return to Start",
      -name => "submit_status"
      );

  print "</table>\n";
  }


sub edit_roster {

	# This is the subroutine to actually select
	# which users get the duty for each
	# day, and which days worth of operations
	# have been canceled, and which notes are
	# applicable for which days of duty,
	# and a little place for the RF to indicate
	# little love/hate notes at the top
	# of the roster. 

	# First, print the title, the form_header,
	# and the beginning of the table. 

  print "<h1>Edit the Duty Roster for Skyline Soaring Club</h1>\n";
  print $q->start_form;
  print "<table border = 1>\n";

	# We will define the name of the rosterfuhrer's
	# comment field.  I like 80cols by 20 rows. 
	# the size really doesn't matter. 
	# the 'wrap => on' is experimental, 
	# it's supposed to make it so that when RF
	# types, the thing will auto wordwrap. 
	# Change to wrap => 'soft' on 19 February 2008 [pb]

  local ($field) = $q->textarea(
	-name =>'RosterMeister',
	-rows => 20,
	-cols => 80,
	-wrap => 'soft',
	);

	# Print to stdout until you see EOM again. 
	# Replace %s with the value of $field. 

  printf <<EOM, $field;
<tr align = center>
  <td colspan = 6><font size=+2><b>The RosterMeister Speaks</b></font></td>
</tr>

<tr>
  <td colspan = 6> 
<p align = left>In this textarea, you should enter
RosterMeister words of wisdom, complaints, solicitations for duty
swaps and any pieces of information that you need to send to the membership.
</p>

<p align = left>The message you enter here will also be sent at the top of
the duty reminder that is mailed to the membership. </p>

<p align = left>You may also wish to leave this textarea blank.<br> If the
program discovers blankness, the RosterF&uuml;hrer cartoon at the top of
the duty roster page will not appear.</p>

<b>Tips:</b><br>
<uL align = left>
<li align = left>Type regular email addresses, and they will be
hyperlinked.</p>
<li align = left>Type regular URLs, and they will automatically be
hyperlinked. Make sure the URLs start with "http://"</p>
</ul>
</td></tr>
<tr>
<td align = center colspan = 6>%s</td>
</tr>

EOM


	# Print submit buttons.
	# There are two different modes for 
	# submitting, previewing, and 
	# committing.  The difference on how
	# they are acted upon is differentiated
	# in the main: block at the top of the program. 

  printf ("<tr align = center><td colspan = 5>%s / %s <br> %s / %s / %s </td></tr>", 
	$q->submit (
		-name => 'Preview Page'
		),
	$q->submit (
		-name => 'Commit All Changes to Duty Roster'
		),

	$q->submit(
		-label => 'Commit and Send Email',
		-value => 'Commit and Email',
		-name => 'submit_status',
		),

	$q->submit(
		-label => 'Create Special Ops Day',
		-value => 'Edit Ops Days',
		-name => 'submit_status',
		),
	);

	# This is wacky.  I spend a week in Japan, and my writing
	# skills denigrate to that of a broken English speaker. 
	# I wonder if there is a scientific term for this. 

  print <<EOM;
<tr>
  <td colspan = 5><font size=+2><b>Roster Selection Section</b></font></td>
  </td>
</tr>
<tr>
  <td colspan = 5><p>In the fields below, select each member for the
appropriate job. If the operations need to be canceled, select the
"Cancel Ops, (date)" checkbox. If you feel the need to express some
news about a day's operations, enter it in the
"Notes" section. </p>

<p>On the final Duty Roster, canceled days of operations will appear in a
pink box with bolded notice of the operations being canceled.  If
applicable, any notes for the day will also be shown for canceled
operations. </p>

<p>When you are done with editing operations, you may preview the changes
with the Preview button. Submit changes to the duty roster by using the
"Commit" button.  If you feel the need to send the document to the club by
means of email, hit "Commit and Email". </p>

<p>If you need to add a special day of operations, like an odd Friday, or
an odd Monday, use the "Edit Ops" button above. You can also delete
days of operations with that button. </p>

<p>If you need to promote/demote the jobs that members serve, use the
Membership maintenance tool found elsewhere on this website. </P>
</p>

</td>
  </td>
</tr>
</table>
<table border = 1 align = center>
EOM
  

	# For each key in the %roster assoc.array,
	# (each field will be a long number, which 
	#  corresponds to a the time of midnight
	#  on a particular date, that being the 
	#  date that we will do operations).

  for (sort by_num keys %roster)  {
    local (@date, @dates);

	# @date array is what day time, dotw, etc 
	# is for the time in $_.

    @date = gmtime($_);
    @dates = ($dotw[$date[6]], $date[4]+1, $date[3], $date[5]+1900);


	# Don't do anything for a value that is 
	# earlier than today.
    next if (($_+86400) < time); 


    $first_month ||= $date[4];

    last
	if ($date[4] == ($first_month + 4));


    if ($date[4] == ($first_month + 3) &&
        !$rf_message) {
      print "<tr><td colspan = 6 height = 50 bgcolor = \"#F08888\">".
	"<blink><b>Note:</b></blink> RF, you can edit ".
	"stuff for the days ahead, but they won't show up on the ".
	"roster until next month!</td></tr>\n";
      $rf_message = 1;
      }



	# Print an empty row.  (for spacing)

    print "<tr><td colspan = 6 height = 50>&nbsp;</td></tr>\n";
    

	# Print the month, (if at the beginning of a month)

    if ($date[4] > $last_month || $roster_linecount==0) {
      $last_month = $date[4];
      printf ("<tr><td colspan = 6 bgcolor = \"#444444\">&nbsp;<font ".
	"size=+2 color = \"#FFFFFF\"><b>%s</b></font></td></tr>\n", 
		$month[$date[4]]);
      }


	# Make the background kind of grey. 
	# Print the words, "Date", "Towpilot", 
	# "Instructor", "DO", and "ADO" in 
	# their own respective table cells. 
	# this is the column header. 

    print "<tr bgcolor = \"#E8E8E8\">\n";
    print "<td><b>Date</b></td><td><b>Tow Pilot 1</b></td>\n";
    #print "<td><b>Tow Pilot 2</b></td>\n";
    print "<td><b>Instructor</b></td>\n";
    print "<td><b>2nd Inst</b></td>\n";
    print "<td><b>Duty Officer</b></td>\n";
    print "<td><b>Asst. Duty Officer</b></td></tr>\n";

	# Print the date for this row, at the beginning of
	# the row.

    printf ("<tr><td align = right rowspan=2>%s,<br>\n %2.2d/%2.2d/%4.4d</td>\n", 
	@dates
	);


	# Define a local array, which has
	# the instructions for building a pull-down
	# menu, with the name of 'towpilot-xxxxxxxx'
	# where xxxxxxx is the value of $_, which 
	# is a big long number associated with 
	# a duty day. 
	# The values for  this pulldown are 
	# the values that we got from the 
	# get_info subroutine. 
	
	# Do this for all 4 categories of duty. 

    local(@pull_list) = (

	$q->popup_menu(
		-name => 'towpilot1-' .$_,
		-default => $duty_list[0],
		-values => ['(Unassigned)', '(Open)', (sort tp_sort (keys %towpilots))]
		),

	$q->popup_menu(
		-name => 'instructor-' .$_,
		-default => $duty_list[2],
		-values => ['(Unassigned)', '(Open)', (sort inst_sort (keys %instructors))]
		),

	$q->popup_menu(
		-name => 'inst2-' .$_,
		-default => $duty_list[2],
		-values => ['(Unassigned)', '(Open)', (sort inst_sort (keys %instructors))]
		),

	$q->popup_menu(
		-name => 'duty-' .$_,
		-default => $duty_list[3],
		-values => ['(Unassigned)', '(Open)', (sort do_sort (keys %duty))]
		),
	$q->popup_menu(
		-name => 'ados-' .$_,
		-default => $duty_list[4],
		-values => ['(Unassigned)', '(Open)', (sort ado_sort (keys %ados))]
		)
    );

	# Print all that stuff that we just defined,
	# onto one row in the HTML table. 
    printf ("<td align = center>%s</td><td align = center>%s</td>".
	      "<td align = center>%s</td><td align = center>%s</td>".
	      "<td align = center>%s</td>",
		@pull_list
		);
	# End the row. 
    print "</tr>\n";

	# Allow the RF the opportunity to put in notes
	# for this duty day.  Notes are stuff like 
	# "Thanksgiving operations, Volunteer staff"
	# and Missing a towpilot, need help. 
	# there is always some sort of time when the 
	# RF needs to express himself.  Now he can 
	# do it for individual dates. 

	# Also, on the same line, the RF has the 
	# ability to cancel operations for that day. 
	# this is done by checkbox. 

    printf ("<tr><td colspan = 5 align = Center> <b>Notes: </b>%s %s", 
      $q->textfield (
	-name => 'notes-' . $_,
	-size => '40'
	),
      $q->checkbox(
	-label => (sprintf (' Cancel Ops, %s/%s', $date[4]+1, $date[3])),
	-name => 'cancel-' . $_,
	-value => 'ON',
        ));
    print "</td></tr>\n";


	# print a spacer line if the last one was Sunday.
    print "<tr><td colspan = 6></tr>\n"
	if ($date[6] == 0);

	# don't bother showing any more than 40
	# entries.  We can expand on this if we 
	# want to.



#    last
#	if (++$count == 40);

    }


	# Another suite of submit buttons. 
    printf ("<tr align = center><td colspan = 6>%s / %s</td></tr>", 
	$q->submit (
		-name => 'Preview Page'
		),
	$q->submit (
		-name => 'Commit All Changes to Duty Roster'
		));

	# End the table.
  print "</table>\n";
  }



sub include_hidden {
	# Subroutine to include all parameters
	# as hidden variables. 
  print "<!-- Hidden Variables Follow -->\n";
  for (sort $q->param) {
    printf ("%s\n", $q->hidden($_));
    }
  print "<!-- End Hidden Variables -->\n";
  }


sub write_roster {
	# Subroutine to take what is in 
	# the $q->param, and put it in the
	# local file named 'roster-info.database'.
	# we can later read it in when we 
	# do a '$q=new CGI(INPUT);' call.

	# This function is documented fully in the
	# CGI module.

  open (OUTPUT, ">$dbdir/roster-info.database")
	|| 
     exception ('Unable to write to the database file');
  $q->save(OUTPUT);
  close (OUTPUT);  
  }

sub exception {
	# This subroutine is to 
	# quit the program abruptly	
	# when something goes terribly wrong. 
  print (@_);
  die (@_);
  }

	# When we need to read what the 
	# database currently has, 
	# we create a new $q variable 
	# (after blowing away the old one)
	# and read the file named 'roster-info.database",
	# and populate the fields with the
	# appropriate pull-down fields.

sub read_roster {
  undef $q;
  open (INPUT, "$dbdir/roster-info.database")
	|| die('blammo');
  $q= new  CGI(INPUT);
  close (INPUT);

  }



sub show_form {
	# I don't remember what I 
	# was supposed to do here. 
  }


sub Init {
	# The initialization subroutine. 
	# We set up the modules we need
	# to use, and we set up some of the
	# most default behaviours. 
	# we also define the names of the week
	# and the months of the year. 

  use DBI;
  $database = 'skyline';
  $dbh = DBI->connect("dbi:Pg:dbname=$database");


  $dbdir="/home/httpd/db";
  use CGI;
  $q = new CGI;
  print $q->header();
  chdir ("/var/www/members/cgi-bin")
	|| die ("Can't chdir to /var/www/members/cgi-bin $!\n");

	# Maybe I should send this part down to the subroutines.

  print $q->start_html(
	-title => "RosterMeister Roster Interface",
	-bgcolor => "#FFFFFF"
	);

  @dotw = qw(
	Sunday
	Monday
	Tuesday
	Wednesday
	Thursday
	Friday
	Saturday
	);

  @month = qw(
	January
	February
	March
	April
	May
	June
	July
	August
	September
	October
	November
	December
	);

  }


sub template {
	# This subroutine takes the 
	# output of the show_roster
	# subroutine, and sandwiches it
	# between the HTML that the rest of 
	# our website uses.  If we make major
	# changes to the left menu, stuff liek that, 
	# then we make a change to this subroutine
	# in the program. 

	# If we are writing (judging by the 
	# argument we received when this sub	
	# was called, then we write the output of
	# this program to the filehandle named
	# OUTPUT, which is the .../skyline/ROSTER/default.html
	# file. 

if ($_[0] eq 'write') {
  java_alert("Writing to the html file... \n");
  open (OUTPUT, ">/var/www/skyline/html/ROSTER/index.shtml")
	|| java_alert("Can't write to the html file! $! \n");
  select OUTPUT;
  }

	# If we're not writing, then we just send to STDOUT.
	# If we're writing, we're still writing to the
	# OUTPUT filehandle, which is the default.html	
	# file.   Keep printing until we see "EOM"

print <<EOM;
<html>
  <head>
    <title>Club Duty Roster</title>
EOM

if ($_[0] eq 'write') {
  print qq(<!--#INCLUDE virtual="/INCLUDES/left-menu.scrap"-->\n);
  }
else {
  open (SCRAP, "/var/www/skyline/html/INCLUDES/left-menu.scrap")
	|| die ("Can't open scrap page!");
  for (<SCRAP>) {
    print;
    }
  close (SCRAP);
  }

	# Run the show_roster subroutine
	# if we're writing, stuff is still going to 
	# OUTPUT, otherwise, STDOUT is our destination. 

show_roster($_[0]);

	# Wrap up what the rest of the HTML page looks
	# like.  Keep printing until you see "EOM"
print qq!<a href = "/ROSTER/old"> Show all of the old Duty Rosters</a>\n!;
if ($_[0] eq 'write') {
  print qq(<!--#INCLUDE virtual="/INCLUDES/footer.scrap"-->\n);
  }
else {
  open (SCRAP, "/var/www/skyline/html/INCLUDES/footer.scrap")
	|| die ("Can't open scrap page!");
  for (<SCRAP>) {
    print;
    }
  close (SCRAP);
  }

	# If we are writing, 
	# stop writing to the file, and resume
	# writing to STDOUT. 

  if ($_[0] eq 'write') {
    close (OUTPUT);
    select (STDOUT);
    java_alert("Webpage Roster Successfully Updated.");
    
    }
  }

sub fetch_db {
	# Go to the database, find everybody who is a $type
	# store their rostername as the key, 
	# or if they don't have a rostername, store it by their lastname

  local (%answer);
  $type  = shift;
  $sql = qq(select rostername, lastname from members 
	where $type = true  
        and memberstatus != 'I'
        and memberstatus != 'N'
	);
  #warn "SQL: $sql";
  $get_info = $dbh->prepare($sql);
  $get_info -> execute();
  while ( $ans = $get_info->fetchrow_hashref ) {
    if ($ans->{'rostername'}) {
      $answer{$ans->{'rostername'}} = 1;
      }
    elsif ($ans->{'lastname'}) {
      $answer{$ans->{'lastname'}} = 1;
      }
    }

  if ($type eq 'ado') { 
	# If this is an ADO, we can put the DOs in there too. 
    for (keys (%duty))  {
      $answer{'* ' . $_} = 1; 
      }
    }
  %answer;
  }
	#End of program. 
	# not too bad! 

__END__


