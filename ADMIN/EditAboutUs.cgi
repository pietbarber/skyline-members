#!/usr/bin/perl
	# Use edit_page.pl program  to update one of the public website pages. 

system ('/home/httpd/bin/edit_page.pl', 
	qq(About Us),
	qq(/var/www/skyline/html/ABOUT/content/about.scrap),
	qq(http://skylinesoaring.org/ABOUT/),
	);
exit;
