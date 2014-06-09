#!/usr/bin/perl

	# Use edit_page.pl program  to update one of the public website pages. 

system ('/home/httpd/bin/edit_page.pl', 
	qq(Videos),
	qq(/var/www/skyline/html/VIDEOS/content/videos.scrap),
	qq(http://skylinesoaring.org/VIDEOS/),
	);
exit;
