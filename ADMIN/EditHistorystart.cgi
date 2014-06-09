#!/usr/bin/perl

	# Use edit_page.pl program  to update one of the public website pages. 

system ('/home/httpd/bin/edit_page.pl', 
	qq(Club History (Foreward)),
	qq(/var/www/skyline/html/HISTORY/content/start.scrap),
	qq(http://skylinesoaring.org/HISTORY/start.shtml),
	);
exit;
