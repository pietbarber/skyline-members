#!/usr/bin/perl

	# Use edit_page.pl program  to update one of the public website pages. 

system ('/home/httpd/bin/edit_page.pl', 
	qq(Club History (Teen Article)),
	qq(/var/www/skyline/html/HISTORY/content/teen.scrap),
	qq(http://skylinesoaring.org/HISTORY/teen.shtml),
	);
exit;
