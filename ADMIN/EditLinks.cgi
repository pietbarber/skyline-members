#!/usr/bin/perl

	# Use edit_page.pl program  to update one of the public website pages. 

system ('/home/httpd/bin/edit_page.pl', 
	qq(LINKS),
	qq(/var/www/skyline/html/LINKS/content/links.scrap),
	qq(http://skylinesoaring.org/LINKS/),
	);
exit;
