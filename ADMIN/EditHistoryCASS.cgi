#!/usr/bin/perl

	# Use edit_page.pl program  to update one of the public website pages. 

system ('/home/httpd/bin/edit_page.pl', 
	qq(Club History (CASS Warrenton Article)),
	qq(/var/www/skyline/html/HISTORY/content/CASSWarrenton.scrap),
	qq(http://skylinesoaring.org/HISTORY/CASSWarrenton.shtml),
	);
exit;
