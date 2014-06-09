#!/usr/bin/perl
$dbdir="/home/httpd/db";

dbmopen (%A, "$dbdir/towpilots", 0666);
@authors_1=sort keys(%A);
dbmclose (%A);

dbmopen (%A, "$dbdir/instructors", 0666);
@authors_2=sort keys(%A);
dbmclose (%A);

dbmopen (%A, "$dbdir/do", 0666);
@authors_3=sort keys(%A);
dbmclose (%A);

dbmopen (%A, "$dbdir/ado", 0666);
@authors_4=sort keys(%A);
dbmclose (%A);

@authors = (sort @authors_1, @authors_2, @authors_3, @authors_4);

print (join "\n", @authors);

