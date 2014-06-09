#!/usr/bin/perl

	# Use edit_page.pl program  to update one of the public website pages. 

system ('/home/httpd/bin/edit_page.pl', 
	qq(Region IV),
	qq(/var/www/skyline/html/LINKS/content/region4.scrap),
	qq(http://skylinesoaring.org/LINKS/REGIONIV/),
	);
exit;
