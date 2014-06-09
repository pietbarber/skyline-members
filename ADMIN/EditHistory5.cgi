#!/usr/bin/perl

	# Use edit_page.pl program  to update one of the public website pages. 

system ('/home/httpd/bin/edit_page.pl', 
	qq(Club History (Chapter V)),
	qq(/var/www/skyline/html/HISTORY/content/history-5.scrap),
	qq(http://skylinesoaring.org/HISTORY/history-5.shtml),
	);
exit;
