#!/usr/bin/perl

	# Use edit_page.pl program  to update one of the public website pages. 

system ('/home/httpd/bin/edit_page.pl', 
	qq(Join Us),
	qq(/var/www/skyline/html/JOIN/content/joinus-content.scrap),
	qq(http://skylinesoaring.org/JOIN/),
	);
exit;
