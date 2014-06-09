#!/usr/bin/perl

	# Use edit_page.pl program  to update one of the public website pages. 

system ('/home/httpd/bin/edit_page.pl', 
	qq(Training),
	qq(/var/www/skyline/html/TRAINING/content/training.scrap),
	qq(http://skylinesoaring.org/TRAINING/),
	);
exit;
