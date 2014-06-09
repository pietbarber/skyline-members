#!/usr/bin/perl

	# Use edit_page.pl program  to update one of the public website pages. 

system ('/home/httpd/bin/edit_page.pl', 
	qq(Club History (Bill Anders Article)),
	qq(/var/www/skyline/html/HISTORY/content/anders.scrap),
	qq(http://skylinesoaring.org/HISTORY/Anders.shtml),
	);
exit;
