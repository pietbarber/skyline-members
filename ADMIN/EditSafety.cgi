#!/usr/bin/perl

	# Use edit_page.pl program  to update one of the public website pages. 

system ('/home/httpd/bin/edit_page.pl', 
	qq(Safety),
	qq(/var/www/skyline/html/TRAINING/content/safety.scrap),
	qq(http://skylinesoaring.org/TRAINING/Safety.shtml),
	);
exit;
