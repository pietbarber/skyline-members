#!/usr/bin/perl

	# Use edit_page.pl program  to update one of the public website pages. 

system ('/home/httpd/bin/edit_page.pl', 
	qq(Kudos),
	qq(/var/www/skyline/html/ABOUT/content/kudos.scrap),
	qq(http://skylinesoaring.org/ABOUT/kudos.shtml),
	);
exit;
