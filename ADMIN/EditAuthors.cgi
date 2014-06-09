#!/usr/bin/perl

	# Use edit_page.pl program  to update one of the public website pages. 

system ('/home/httpd/bin/edit_page.pl', 
	qq(Authors),
	qq(/var/www/skyline/html/AUTHORS/content/authors.scrap),
	qq(http://skylinesoaring.org/AUTHORS/),
	);
exit;
