#!/usr/bin/perl 

# Upload a GCX file (from Garmin) or TCX file 
# and convertify it into an IGC and KML file. 
# Use the IGC for future reference, 
# Use the KML to view in Google Maps


use strict; 
use CGI qw(:standard); 
use Time::Local; 
my @track; 	# Place all of the flight information into this. 
my (%flight); 	# interesting information about the flight. 
my ($DEBUG)=2;
my ($DEBUG)=0;

if (param('flightlog_upload')) { 
	# Process the uploaded flightlog. 
  print header;
  print qq(<html><head><title>Here is your flight log</title></head>);
  print include('left-menu.scrap'); 
  my ($filename) = param('flightlog_upload');
  my ($contents);
  while (my $line=<$filename>) {
    $contents .= $line;
    }
  param('flightlog_contents', $contents);
  my ($filename) = time;
  if ($contents =~ /<Activities>/ ) {
	# It's a TCX, maybe. 

    open (OUTFILE, ">traces/$filename.tcx"); 
    print OUTFILE $contents; 
    close (OUTFILE); 
    print "Starting process<br>" if $DEBUG; 
    process_tcx ($contents); 
    output_kml();
    print "<br>finished process" if $DEBUG; 
    }
  elsif ($contents =~ /^A/ ) { 
	# It's an IGC... maybe
    open (OUTFILE, ">traces/$filename.igc"); 
    print OUTFILE $contents; 
    close (OUTFILE); 
    print "Starting process<br>" if $DEBUG; 
    process_igc ($contents); 
    output_kml();
    print "<br>finished process" if $DEBUG; 
    
    } 
  print include('footer.scrap'); 
  } 

elsif (param) {
  print header;
  print start_html (
	-title => 'Weird.'
	); 
  print include('left-menu.scrap'); 
  print h2(qq(weird));
  print include('footer.scrap'); 
  }

else {
  print header; 
  print start_html (
	-title => 'Upload a flight log'
	); 
  print include('left-menu.scrap'); 
  print h2(qq(Upload a flight log)); 
  print qq(Uploading a IGC or a Garmin TCX file will convert it to a Google Earth KMZ file, which can be downloaded for later review, or viewed with the <a href="http://www.google.com/earth/explore/products/plugin.html"> Google Earth Plugin</a>. Use the form below to get started. <br/> Currently, this system only supports standard IGC as well as Garmin TCX files, but will later support Garmin GCX files if the demand requires it. <br /> In the future, the system will be able to identify the uploaded log file and associate it with flights in the club's flight information database.  The 3d representations of the flights will be stored in the database for future reference and review.<br/><br/><p><a href="/FLIGHTS/view-flight.cgi">View other flights</a></p> );
  print_multipart_form(); 
  print include('footer.scrap'); 
  }

sub print_multipart_form {
  print start_multipart_form();
  my ($default_filename)='2011-01-23.tcx'; 
  printf (qq(
<table border="1" bgcolor="#F8F8F*">
<tr><td>Choose File to Upload:</td><td>%s</td>
</tr><td colspan="2" align="center">%s</td></tr></table>
        ),
        filefield (
                -name => 'flightlog_upload',
                -default => $default_filename,
                -size => 20,
                ),
        submit (
                -value => "Submit for processing"
                )
        );
  }


sub process_igc {
	# Take IGC file
	# and see if we can make any flight information out of it. 
	# IGC File Format reference: 
	# http://carrier.csi.cam.ac.uk/forsterlewis/soaring/igc_file_format/igc_format_2008.html#link_3.3

  my ($input)=shift; 
	# This is the unique-like ID that is associated with this flight: 
	# We'll combind the Recorder specifics along with the HFDTE. 
	# Hope this works... :\ It might not work if dude does multiple flights
	# in a day, so I'll refer to my IGCs from other flights and try to 
	# come up with something. 

  if ($input =~ /^A(.+)\n/) { 
    $flight{'Recorder'} = $1; 
    } 
  if ($input =~ /\WHFDTE(\d{6})\W/ ) {
    $flight{'DTE'} = $1 ; 
    print "HF DTE: " . $flight{'DTE'} if $DEBUG; 
    }

	# Time Format is "HFDTE"DDMMYY
	# two digit year field is an abomination.  Clearly this format came out
	# before y2k.  blech. 

  print "ping! 1<br>" if $DEBUG; 
	# OK here we go, we'll go through the IGC file one by one. 
  for my $line (split (/\n/, $input)) { 
    chomp $line; 
                 # B H H    M M   S S   D D  M.MMMM N     D D D   M MM MM    E    V    P P P P P G G G G G CR LF
    if ($line =~ /^B(\d\d)(\d\d)(\d\d)(\d\d)(\d{5})(N|S)(\d\d\d)(\d\d\d\d\d)(E|W)(A|V)(\d{5})(\d{5})/) {
	# Plot line has been encountered. 
	# We'll strip out the useful data and plug it right back into the %flight. 
      next if $line =~ /0000000N00000000E/; # Don't import 0N0E coordinates. We're not flying near Ascension Island
      if ($DEBUG) { 
        print "<pre>";  
        print "B H H M M S S D D M MM MM N D D D M MM MM E V P P P P P G G G G G CR LF<br>\n"; 
        print 'B $1 $2 $3 $4 $5 $6 $7 $8 $9 $10 $11 $12 $13 $14 $15 $16 $17 $18 $19<br>' . "\n"; 
        print "B $1 $2 $3    $4 $5      $6 $7   $8      $9 $10 $11     $12 <br>\n"; 
        print "</pre>";  
        } 
      $flight{'ID'}||= make_ISO8601(that_dte($1, $2, $3)); 
      $flight{'previoustime'} ||= that_dte( $1, $2, $3);
      $flight{'thistime'} = that_dte( $1, $2, $3 );
      my ($altitude) = $11; 
      if ($altitude == 0) {
        $altitude = $12; 
        }
      my ($climb)=($altitude - $flight{'prevalt'}); 
      $flight{'prevalt'} = $altitude; 
      my ($interval)=$flight{'thistime'}-$flight{'previoustime'};
      if ($interval < 1) { 
        print "Looks like interval is < 1. ($interval)<br>\n" if $DEBUG; 
        print "previous time: " . $flight{'previoustime'} .  "\n"; 
        print "this time: " . $flight{'thistime'} .  "\n"; 
        $flight{'previoustime'} = $flight{'thistime'};
        $flight{'prevalt'} = $altitude; 
        next; 
        }

      push(@track, {
        'Time' => make_ISO8601(that_dte($1, $2, $3)), 
        'Lat' => latlong($4, $5, $6), 
        'Long'=> latlong ($7, $8, $9), 
        'Alt' => $altitude,
        'Interval'=> $interval,
        'Climb' => $climb/$interval,
        });
      $flight{'previoustime'} = $flight{'thistime'};
      $flight{'prevalt'} = $altitude; 
      }
    else {
      #print "<pre>$line\n</pre>";
      }
    } 
  }

sub process_tcx {
	# Take wild, hairy Gpx file, 
	# and see if we can make any flight information out of it. 
	# All using XML.  The Geo::Gpx module was utterly useless
	# So I had to do all this XML manually, which kind of sucked.
	# Thankfully, the Logsheet program got me used to dealing wth
	# XML like this, so I'm not too flustered. 

	# First, take the input, which is the uploaded content, essentially. 
	# Then run it into XML::Bare. 
	# Do some initial tests to make sure that it looks like XML. 
	# Then start parsing through the multiple levels of nesting till 
	# we get into all teh goodies in teh cookie jar. 
	# We throw information about the maxes and mins and stuff like that 
	# into the junkey assoc.array %flight. 

  my ($input)=shift; 
  use XML::Bare;
  my $xml = new XML::Bare( text => $input); 
  my ($root) = $xml->parse();
  if (ref($root) ne 'HASH') { 
    print "Doesn't look like XML to me, dude. <br>\n"; 
    exit; 
    } 
  else { 
    print "Looks like valid XML... continuing...<br>\n" if $DEBUG; 
    } 
	# This is the unique-like ID that is associated with this flight: 
	# It looks like this in the XML: 
	#       <Id>2011-01-23T17:50:45Z</Id>
  $flight{'ID'}=$root->{'TrainingCenterDatabase'}->{'Activities'}->{'Activity'}->{'Id'}->{'value'};

	# Time Format is ISO8601 
	# DateTime-Format-ISO8601
	#     YYYY-MM-DDThh:mm:ssZ
	#               ^        ^
	# See the XML at the bottom after __END__ to see 
	# what kind of stuff we are importing here. 
	# also to see what the print statement looks like. 

  print "ping! 1<br>" if $DEBUG; 
  if (ref($root->{'TrainingCenterDatabase'}->{'Activities'}->{'Activity'}->{'Lap'}) eq 'ARRAY') { 
  print "ping! 2 (multiple laps)<br> " if $DEBUG; 
    for my $lap ($root->{'TrainingCenterDatabase'}->{'Activities'}->{'Activity'}->{'Lap'}) { 
  print "ping! 3 (multiple laps)<br>" if $DEBUG; 
      for my $this_lap (@{$lap}) { 
        if (ref($this_lap->{'Track'}) eq 'ARRAY'){ 
          for my $track (@{$this_lap->{'Track'}}) { 
            print keys(%{$track->{'Trackpoint'}}); 
            print "OK! Processing snippet.\n"; 
            process_snippet($track); 
            print "OK! Snippet processing complete. ($#track) \n"; 
            }
          }
        #print keys (%{$this_lap->{'Track'}}); 
        }
      }
    }

  elsif (ref($root->{'TrainingCenterDatabase'}->{'Activities'}->{'Activity'}->{'Lap'}) eq 'HASH') { 
  print "ping! 2 (single lap)<br>" if $DEBUG; 
    my $track=$root->{'TrainingCenterDatabase'}->{'Activities'}->{'Activity'}->{'Lap'}; 
  print "ping! 3 (single lap)<br>" if $DEBUG; 
    if (ref($track->{'Track'}) eq 'HASH') {
      for my $trackpoint (%{$track->{'Track'}}) {
        print "ping! 4a(single lap)<br>" if $DEBUG; 
        if (ref($trackpoint) eq 'ARRAY') {
          print "ping! 5a(single lap)<br>" if $DEBUG; 
          for my $thistrack ( @{$trackpoint}) {
            process_snippet($thistrack); 
            }   
          }
        }
      }
    else {
      print "ping! 4b(multiple laps)<br>" if $DEBUG; 
      for my $trackpoint (@{$track->{'Track'}}) {
        print "REF:" . ref($trackpoint) . "\n"; 
        if (ref($trackpoint) eq 'ARRAY') {
          print "ping! 5b(multiple laps)<br>" if $DEBUG; 
          for my $thistrack ( @{$trackpoint}) {
            process_snippet($thistrack); 
            }   
          }
        }
      }
    }
  }

sub process_snippet {
  my $thistrack=shift;  
  print keys(%{$thistrack}); 
  $flight{'previoustime'} ||= that_time($thistrack->{'Time'}->{'value'});
  $flight{'thistime'} = that_time($thistrack->{'Time'}->{'value'});
  $flight{'prevalt'} ||= $thistrack->{'AltitudeMeters'}->{'value'};
  my ($interval) = $flight{'thistime'}-$flight{'previoustime'};
	# I don't want to be alerted of divide by zero issues. So if there is no interval, there is no plot. 
  next if ($interval == 0 || $interval < 0); 
	# I don't want these if there are no lat/logs available. 
  next unless ($thistrack->{'Position'}->{'LatitudeDegrees'}->{'value'});
  next unless ($thistrack->{'Position'}->{'LongitudeDegrees'}->{'value'});
  my ($climb) = $thistrack->{'AltitudeMeters'}->{'value'} - $flight{'prevalt'};
  push(@track, {
	'Time' => $thistrack->{'Time'}->{'value'},
	'Long'=> $thistrack->{'Position'}->{'LongitudeDegrees'}->{'value'},
	'Lat' =>  $thistrack->{'Position'}->{'LatitudeDegrees'}->{'value'},
	'Alt' => $thistrack->{'AltitudeMeters'}->{'value'},
	'Interval'=> $interval, 
	'Climb' => $climb/$interval,
	}); 
  printf ("Time: %s Lat: %s Long: %s Alt (m): %s Interval: %s Vario: %6.4f GS: %6.4f<br>\n", 
	$thistrack->{'Time'}->{'value'}, 
	$thistrack->{'Position'}->{'LatitudeDegrees'}->{'value'},
	$thistrack->{'Position'}->{'LongitudeDegrees'}->{'value'},
	$thistrack->{'AltitudeMeters'}->{'value'},
	$interval,
	$climb/$interval,
	) if $DEBUG;
		
  $flight{'maxclimb'} = $climb/$interval if ($climb/$interval > $flight{'maxclimb'}); 
  $flight{'maxsink'} = $climb/$interval if ($climb/$interval < $flight{'maxsink'}); 
  $flight{'previoustime'} = $flight{'thistime'}; 
  $flight{'prevalt'} = $thistrack->{'AltitudeMeters'}->{'value'};
  }  

sub that_time {
	# Given an ISO8601 time like YYYY-MM-DDThh:mm:ssZ
	# output the seconds since 1970. 
  my ($input) = shift; 
  my ($answer); 
  if ($input =~ /^(\d{4})-(\d{2})-(\d{2})T(\d{2}):(\d{2}):(\d{2})Z$/) {
    $answer = timegm($6,$5,$4,$3,($2-1),$1)
    }
  if ($input =~ /^(\d{4})-(\d{2})-(\d{2})T(\d{2}):(\d{2}):(\d{2})\.(\d{3})Z$/) {
    $answer = timegm($6,$5,$4,$3,($2-1),$1)
    }
  $answer; 
  } 

sub latlong {
	# Take 4 inputs, output a lat or a long that is decimalized
	# instead of D M S (N/S) or D M S (E/W)
  my ($degrees, $minutes, $hemisphere) = @_; 
  my ($answer); 
  my ($hemi) = 1; 
  if ($hemisphere eq 'W' || $hemisphere eq 'S') { 
    $hemi=-1
    } 
  my $decimalmin = ($minutes/60000); 
  my $answer=sprintf("%8.10f", ($degrees+$decimalmin) * $hemi); 

  $answer; 
  } 

sub make_ISO8601 {
	# Take an epoch time, and output 
	# an ISO 8601 date format, just like what the TCX files give us. 
  my ($epochtime) = shift; 
  my (@date)=gmtime($epochtime); 
  my ($answer) = sprintf ("%4.4d-%2.2d-%2.2dT%2.2d:%2.2d:%2.2dZ", 
	(1900+$date[5]), 
	(1+$date[4]),
	$date[3],
	$date[2],
	$date[1],
	$date[0]
	);
  print "Date is $answer" if $DEBUG; 
  $answer; 
  } 

sub that_dte {
	# Like that_time, but expects the IGC's brain-dead DTE format instead. 
  my @date; 
  my ($hour) = shift; 
  my ($min) = shift; 
  my ($sec) = shift; 
  my ($answer); 
  if ($flight{'DTE'} =~ /^(\d\d)(\d\d)(\d\d)$/) {
                        # Day   Month  Year (2 digit)
    $date[3]=$1; # Day
    $date[4]=$2-1; # Month
    $date[5]=($3);  # Year
    }
  $date[0]=$sec; 
  $date[1]=$min; 
  $date[2]=$hour;
  $answer=timegm(@date); 
  print "epoch time is $answer" if $DEBUG; 
  $answer; 
  } 

sub output_kml{ 
	# Take @track and %flight, and output that sucker 
	# to a google readable KMZ file. 
	# file
  my ($outfile); 

  my (@colors) = (
	 { '-desc' => 'Climb > 1000 fpm', 
		'-val' => '00ff00' },
	 { '-desc' => 'Climb 800 - 999', 
		'-val' => '44ff44' },
	 { '-desc' => 'Climb 600 - 799', 
		'-val' => '88ff88' },
	 { '-desc' => 'Climb 400 - 599', 
		'-val' => 'aaffaa' },
	 { '-desc' => 'Climb 200 - 399', 
		'-val' => 'd8ffd8' },
	 { '-desc' => 'Climb 0 - 199', 
		'-val' => 'fdfffd' },

	 { '-desc' => 'Sink 1 - 199', 
		'-val' => 'fffdfd' },
	 { '-desc' => 'Sink 200 - 399', 
		'-val' => 'ffd8d8' },
	 { '-desc' => 'Sink 400 - 599', 
		'-val' => 'ffaaaa' },
	 { '-desc' => 'Sink 600 - 799', 
		'-val' => 'ff8888' },
	 { '-desc' => 'Sink 800 - 999', 
		'-val' => 'ff4444' },
	 { '-desc' => 'Sink > 1000 fpm', 
		'-val' => 'ff0000' },

	); 
  if ($flight{'ID'} =~ /^(\d{4})-(\d{2})-(\d{2})T(\d{2}):(\d{2}):(\d{2})(\.\d{3})?Z$/) {
    $outfile=$flight{'ID'}; 
    }
  else {
    print "Unable to create flight ID file due to flight file name funkiness. $outfile<br> "; 
    return;
    }
  my ($outfile_rand) = time; 
  $outfile_rand =~ s/^\d+(\d\d\d)$/$1/; 
  open (OUTFILE, ">traces/$outfile-$outfile_rand.kml") || die ("Unable to write to $outfile-$outfile_rand.\n");  
  print "traces/$outfile-$outfile_rand.kml is our outfile... <br>\n" if $DEBUG; 
  print OUTFILE qq(<?xml version="1.0" standalone="yes"?>
<kml xmlns="http://earth.google.com/kml/2.2">
  <Document>
    <Folder id="Legend">
);
  for my $key (0..$#colors) {
    printf OUTFILE qq(      <Placemark>
        <name><![CDATA[<span style="color:#%s;"><b>%s</b></span>]]></name>
        <styleUrl>#gv_legend</styleUrl>
        <visibility>1</visibility>
      </Placemark>
),
	$colors[$key]{'-val'},
	$colors[$key]{'-desc'}
    }
  print OUTFILE qq(    <name>Legend: Climb rate [est.] (fpm)</name>
      <open>1</open>
      <visibility>1</visibility>
    </Folder>
    <Folder id="Tracks">
      <Folder id="track 1">
        <Folder id="track 1 paths">
);

	# Print the lines between the points. Make colors for climb rates. 
  my $count=0;
  my (%prev); 
  print "\@track is $#track items long..." if $DEBUG; 
  for my $line (@track) {
    $count++; 
    if ($prev{'Long'} !~ /\w/) { 
      $prev{'Long'} = $line->{'Long'}; 
      $prev{'Lat'} = $line->{'Lat'}; 
      $prev{'Alt'} = $line->{'Alt'}; 
      next;
      } 
  printf OUTFILE (qq(          <Placemark>
            <LineString>
              <altitudeMode>absolute</altitudeMode>
              <coordinates>%s,%s,%s %s,%s,%s</coordinates>
              <tessellate>0</tessellate>
            </LineString>
            <Style>
              <LineStyle>
                <color>FF%s</color>
                <width>4</width>
              </LineStyle>
            </Style>
            <name><![CDATA[<span style="color:#%s;">trkpt %d</span>]]></name>
          </Placemark>
),
		$prev{'Long'},
		$prev{'Lat'},
		$prev{'Alt'},
		$line->{'Long'},
		$line->{'Lat'},
		$line->{'Alt'},
		colorize($line->{'Climb'}),
		colorize($line->{'Climb'}),
		$count
		); 
    $prev{'Long'} = $line->{'Long'}; 
    $prev{'Lat'} = $line->{'Lat'}; 
    $prev{'Alt'} = $line->{'Alt'}; 
    } 
  print OUTFILE qq(      <name>Paths</name>
        </Folder>
        <Folder id="track 1 points">
);

	# print the points between the lines
  my $count=0;
  for my $line (@track) {
    $count++; 
  printf OUTFILE (qq(          <Placemark>
            <name>Track #%s</name>
            <Point>
              <altitudeMode>absolute</altitudeMode>
              <coordinates>%s,%s,%s</coordinates>
            </Point>
            <Snippet></Snippet>
            <Style>
              <IconStyle>
                <color>FF%s</color>
              </IconStyle>
	      <LabelStyle>
                <color>FF%s</color>
	      </LabelStyle>
            </Style>
            <TimeStamp>
              <when>%s</when>
            </TimeStamp>
	    <description><![CDATA[<b>trackpoint #%s</b><br/><i>Latitude:</i> %6.4f &#176;<br/> <i>Longitude:</i> %6.4f &#176;<br/> <i>Elevation:</i> %d ft<br/> <i>Time:</i> %s <br/> <i>Climb rate:</i> %d fpm]]></description>
            <styleUrl>#gv_trackpoint</styleUrl>
          </Placemark>
),
		$count,
		$line->{'Long'},
		$line->{'Lat'},
		$line->{'Alt'},
		colorize($line->{'Climb'}),
		colorize($line->{'Climb'}),
		$line->{'Time'},
		$count,
		$line->{'Lat'},
		$line->{'Long'},
		($line->{'Alt'} * 3.2808399),
		$line->{'Time'},
		($line->{'Climb'} * 196),
	); 
    } 

          print OUTFILE qq(      <name>Points</name>
        </Folder>
        <Folder id="track 1 shadow">
);


  my $count=1;
  my (%prev); 

	# print the shadow for the line

  for my $line (@track) {
    $count++; 
    if ($prev{'Long'} !~ /\w/) { 
      $prev{'Long'} = $line->{'Long'}; 
      $prev{'Lat'} = $line->{'Lat'}; 
      $prev{'Alt'} = $line->{'Alt'}; 
      next;
      } 
  printf OUTFILE (qq(          <Placemark>
            <LineString>
              <altitudeMode>clampToGround</altitudeMode>
              <coordinates>%s,%s,%s %s,%s,%s</coordinates>
              <tessellate>0</tessellate>
            </LineString>
            <Style>
              <LineStyle>
                <color>7F000000</color>
                <width>4</width>
              </LineStyle>
            </Style>
            <name>trkpt %d</name>
          </Placemark>
),
		$prev{'Long'},
		$prev{'Lat'},
		$prev{'Alt'},
		$line->{'Long'},
		$line->{'Lat'},
		$line->{'Alt'},
		$count
		); 
    $prev{'Long'} = $line->{'Long'}; 
    $prev{'Lat'} = $line->{'Lat'}; 
    $prev{'Alt'} = $line->{'Alt'}; 
    } 

	# Now the junk that defines how the blobs and lines and words look. 
	# Basically an imbedded CSS page in this XML. 
	# I just copied this, so if it looks like crap, don't blame me.  
  printf OUTFILE qq(        <name>[shadow]</name>
          <visibility>1</visibility>
        </Folder>
        <Snippet></Snippet>
        <description></description>
        <name></name>
      </Folder>
      <name>Tracks</name>
      <open>0</open>
      <visibility>1</visibility>
    </Folder>
    <Snippet><![CDATA[created on <a href="https://members.skylinesoaring.org/">https://members.skylinesoaring.org/</a>]]></Snippet>
        <Style id="gv_legend">
      <IconStyle>
        <Icon>
          <href>http://maps.google.com/mapfiles/kml/pal2/icon26.png</href>
        </Icon>
      </IconStyle>
    </Style>
    <Style id="gv_waypoint_normal">
      <BalloonStyle>
        <text><![CDATA[<p align="left" style="white-space:nowrap;"><font size="+1"><b>\$[name]</b></font></p> <p align="left">\$[description]</p>]]></text>
      </BalloonStyle>
      <IconStyle>
        <Icon>
          <href>http://maps.google.ca/mapfiles/kml/pal4/icon56.png</href>
        </Icon>
        <color>FFFFFFFF</color>
        <hotSpot x="0.5" xunits="fraction" y="0.5" yunits="fraction" />
      </IconStyle>
      <LabelStyle>
        <color>FFFFFFFF</color>
        <scale>1</scale>
      </LabelStyle>
    </Style>
    <Style id="gv_waypoint_highlight">
      <BalloonStyle>
        <text><![CDATA[<p align="left" style="white-space:nowrap;"><font size="+1"><b>\$[name]</b></font></p> <p align="left">\$[description]</p>]]></text>
      </BalloonStyle>
      <IconStyle>
        <Icon>
          <href>http://maps.google.ca/mapfiles/kml/pal4/icon56.png</href>
        </Icon>
        <color>FFFFFFFF</color>
        <hotSpot x="0.5" xunits="fraction" y="0.5" yunits="fraction" />
        <scale>1.2</scale>
      </IconStyle>
      <LabelStyle>
        <color>FFFFFFFF</color>
        <scale>1</scale>
      </LabelStyle>
    </Style>
    <Style id="gv_trackpoint_normal">
      <BalloonStyle>
        <text><![CDATA[<p align="left" style="white-space:nowrap;"><font size="+1"><b>\$[name]</b></font></p> <p align="left">\$[description]</p>]]></text>
      </BalloonStyle>
      <IconStyle>
        <Icon>
          <href>http://maps.google.ca/mapfiles/kml/pal2/icon26.png</href>
        </Icon>
        <scale>0.3</scale>
      </IconStyle>
      <LabelStyle>
        <scale>0</scale>
      </LabelStyle>
    </Style>
    <Style id="gv_trackpoint_highlight">
      <BalloonStyle>
        <text><![CDATA[<p align="left" style="white-space:nowrap;"><font size="+1"><b>\$[name]</b></font></p> <p align="left">\$[description]</p>]]></text>
      </BalloonStyle>
      <IconStyle>
        <Icon>
          <href>http://maps.google.ca/mapfiles/kml/pal2/icon26.png</href>
        </Icon>
        <scale>0.4</scale>
      </IconStyle>
      <LabelStyle>
        <scale>1</scale>
      </LabelStyle>
    </Style>
    <StyleMap id="gv_waypoint">
      <Pair>
        <key>normal</key>
        <styleUrl>#gv_waypoint_normal</styleUrl>
      </Pair>
      <Pair>
        <key>highlight</key>
        <styleUrl>#gv_waypoint_highlight</styleUrl>
      </Pair>
    </StyleMap>
    <StyleMap id="gv_trackpoint">
      <Pair>
        <key>normal</key>
        <styleUrl>#gv_trackpoint_normal</styleUrl>
      </Pair>
      <Pair>
        <key>highlight</key>
        <styleUrl>#gv_trackpoint_highlight</styleUrl>
      </Pair>
    </StyleMap>
    <name><![CDATA[Skyline Soaring Club Flight %s]]></name>
    <open>1</open>
    <visibility>1</visibility>
  </Document>
</kml>
), 
	$flight{'ID'};

  close (OUTFILE); 
  open (ZIP, "-|") ||
	exec ("/usr/bin/zip", "traces/$outfile-$outfile_rand.kmz", "traces/$outfile-$outfile_rand.kml");
  my $zip_output=<ZIP>; 
  close (ZIP); 
  print qq(<a href="traces/$outfile-$outfile_rand.kmz">View the KMZ file</a>); 
  print qq(<br><a href="view-flight.cgi?view=$outfile-$outfile_rand.kmz">URL for future reference</a>); 
  show_map("$outfile-$outfile_rand"); 
  print h2(qq(Upload another flight track)); 
  print_multipart_form(); 
  }


sub show_map {
  my ($input)=shift; 
  print google_header("https://members.skylinesoaring.org/FLIGHTS/traces/$input.kmz");
  print qq(
    <br /><img src="/icons/small/blank.png" onload="init()"><br />
    <div id="sample-ui"></div>
    <div id="map3d" style="width:800;height:800;"></div>
    <br>
    <div>Installed Plugin Version: <span id="installed-plugin-version" style="font-weight: bold;">Loading...</span></div>
  );
  }


sub google_header {
  my $input=shift; 
  my $answer = qq(
  <script src="http://www.google.com/jsapi?key=ABQIAAAAAdJaFgvhg9JdRzEqvv7ZVRT-vVvShPJRzs9yB40liSA3WcKVhRTNWyTFZJ2kkre9cVgTdyczGDeDoA" type="text/javascript"></script>
    <script type="text/javascript">
      function addSampleButton(caption, clickHandler) {
        var btn = document.createElement('input');
        btn.type = 'button';
        btn.value = caption;
        
        if (btn.attachEvent)
          btn.attachEvent('onclick', clickHandler);
        else
          btn.addEventListener('click', clickHandler, false);

        // add the button to the Sample UI
        document.getElementById('sample-ui').appendChild(btn);
      }
      
      function addSampleUIHtml(html) {
        document.getElementById('sample-ui').innerHTML += html;
      }
    </script>
    <script type="text/javascript">
    var ge;
    
    google.load("earth", "1");
    
    function init() {
      google.earth.createInstance('map3d', initCallback, failureCallback);
    
    
    }
    
    function initCallback(instance) {
      ge = instance;
      ge.getWindow().setVisibility(true);
    
      // add a navigation control
      ge.getNavigationControl().setVisibility(ge.VISIBILITY_AUTO);
    
      // add some layers
      ge.getLayerRoot().enableLayerById(ge.LAYER_BORDERS, true);
      ge.getLayerRoot().enableLayerById(ge.LAYER_ROADS, true);
    
      createNetworkLink();
    
      document.getElementById('installed-plugin-version').innerHTML =
        ge.getPluginVersion().toString();
    }
    
    function failureCallback(errorCode) {
    }
    
    function createNetworkLink() {
      var networkLink = ge.createNetworkLink("");
      networkLink.setDescription("NetworkLink open to fetched content");
      networkLink.setName("Open NetworkLink");
      networkLink.setFlyToView(true);
    
      // create a Link object
      var link = ge.createLink("");
      link.setHref("$input");
    
      // attach the Link to the NetworkLink
      networkLink.setLink(link);
    
      // add the NetworkLink feature to Earth
      ge.getFeatures().appendChild(networkLink);
    }
    
    function buttonClick() {
      createNetworkLink();
    }
    
    </script>
  );
  $answer;
  } 


sub colorize {
  my ($input) = shift; 

  my (@colors) = ('00ff00', '44ff44', '88ff88', 'aaffaa', 'fdfffd', 'd8ffd8', 
		'ffd8d8', 'ff8888', 'ffaaaa', 'ff8888', 'ff4444', 'ff0000');

  $input > 5.08 && return ($colors[0]);  # < 1000 fpm
  $input > 4.064 && return ($colors[1]); # 800 fpm
  $input > 3.048 && return ($colors[2]); # 600 fpm
  $input > 2.032 && return ($colors[3]); # 400 fpm 
  $input > 1.016 && return ($colors[4]); # 200 fpm 
  $input > -1.016 && return ($colors[5]); # -200 fpm
  $input > -2.032 && return ($colors[6]); # -400 fpm
  $input > -3.048 && return ($colors[7]); # -600 fpm
  $input > -4.064 && return ($colors[8]); # -800 fpm 
  return ($colors[9]); # < -1000 fpm 

  }



sub include {
        # Pull file from the INCLUDES directory
        # output of subroutine is that file.
  my $file = shift;
  my $answer;
  my ($dir, $fulldir);
  use Cwd;
  $fulldir=getcwd;
  $dir = 'skyline' if ($fulldir =~ m#/var/www/skyline#);
  #warn ("The pwd is $fulldir\n") if $DEBUG;
  $dir ||= 'members';
  open (INCLUDE, "/var/www/$dir/html/INCLUDES/$file") || print "Can't open that file $!";
  while (my $line = <INCLUDE>) {
    $answer .= $line;
    }
  close (INCLUDE);
  $answer;
  }





__END__

 

Sample imported XML for a flight on 23 Jan 2011 by Piet Barber. 
This never got specified as flying, so, as far as the tracking device watch
was concerned, this was "running" (i run fast) 

Activities -> Activity 
   -> Id
   -> Lap
      +-> Track
          +-> Trackpoint
               +-> Stuff we want



<TrainingCenterDatabase xmlns="http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2 http://www.garmin.com/xmlschemas/TrainingCenterDatabasev2.xsd">

  <Activities>
    <Activity Sport="Running">
      <Id>2011-01-23T17:50:45Z</Id>
      <Lap StartTime="2011-01-23T17:50:45Z">
        <TotalTimeSeconds>61.3000000</TotalTimeSeconds>
        <DistanceMeters>1609.3470459</DistanceMeters>
        <MaximumSpeed>30.3522758</MaximumSpeed>
        <Calories>34</Calories>
        <Intensity>Active</Intensity>
        <TriggerMethod>Distance</TriggerMethod>
        <Track>
          <Trackpoint>
            <Time>2011-01-23T17:50:46Z</Time>
            <Position>
              <LatitudeDegrees>38.9617571</LatitudeDegrees>
              <LongitudeDegrees>-78.3150431</LongitudeDegrees>
            </Position>
            <AltitudeMeters>1344.0605469</AltitudeMeters>
            <DistanceMeters>38.8236885</DistanceMeters>
            <SensorState>Absent</SensorState>
          </Trackpoint


Output from primitive print command from process_gpx: 
Time: 2011-01-23T17:50:50Z Lat: 38.9620463 Long: -78.3158176 Alt (m): 1346.4638672 Distance (m): 114.0436401 Interval: 4 Vario: 0.6008 GS: 18.8050
Time: 2011-01-23T17:50:55Z Lat: 38.9623688 Long: -78.3169334 Alt (m): 1323.3920898 Distance (m): 216.3120117 Interval: 5 Vario: -4.6144 GS: 20.4537
Time: 2011-01-23T17:50:59Z Lat: 38.9625938 Long: -78.3179455 Alt (m): 1303.2043457 Distance (m): 307.5228882 Interval: 4 Vario: -5.0469 GS: 22.8027
Time: 2011-01-23T17:51:04Z Lat: 38.9628414 Long: -78.3193699 Alt (m): 1283.0166016 Distance (m): 435.4419861 Interval: 5 Vario: -4.0375 GS: 25.5838




<!-- End Meat -->
      </td>
    </tr>
  </tbody>
</table>
</body>
</html>`
