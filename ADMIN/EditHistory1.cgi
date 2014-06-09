#!/usr/bin/perl

	# Use edit_page.pl program  to update one of the public website pages. 

system ('/home/httpd/bin/edit_page.pl', 
	qq(Club History (Chapter I)),
	qq(/var/www/skyline/html/HISTORY/content/history-1.scrap),
	qq(http://skylinesoaring.org/HISTORY/history-1.shtml),
	);
exit;
