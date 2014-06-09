#!/usr/bin/perl

	# Use edit_page.pl program  to update one of the public website pages. 

system ('/home/httpd/bin/edit_page.pl', 
	qq(Weather),
	qq(/var/www/skyline/html/WEATHER/content/weather.scrap),
	qq(http://skylinesoaring.org/WEATHER/),
	);
exit;
