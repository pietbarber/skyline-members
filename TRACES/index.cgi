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
my ($dir) = '/var/www/members/html/FLIGHTS/traces/'; 

if (param('view')) { 
  if (param('view') =~ /^(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z-\d+)\.kmz$|^(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{3}Z-\d+)\.kmz$/) { 
    my ($filename)  = param('view'); 
    if (-r "$dir/$filename" ) {
      print header; 
      print qq(<html><head><title>View 3D Flight</title></head>); 
      print include('left-menu.scrap');
      print qq(<a href="/TRACES/$filename">View the KMZ file with Google Earth</a><br>); 
      print qq(<a href="?">View other Flights</a>); 
      show_map($filename); 
      print include('footer.scrap'); 
      }

    else {
      print header; 
      print qq(<html><head><title>3D Flight Not Found</title></head>);
      print include('left-menu.scrap');
      print h2(qq(Not Found)); 
      print p(qq(Sorry, I couldn't find that flight. $filename )); 
      show_flight_list(); 
      print include('footer.scrap'); 
      }
    } 
  else { 
    print header; 
    print qq(<html><head><title>3D Flight Not Found</title></head>);
    print include('left-menu.scrap');
    print h2(qq(Not Found)); 
    print p(qq(Sorry, I couldn't find that flight. )); 
    show_flight_list(); 
    print include('footer.scrap'); 
    }
  }

else { 
  print header; 
  print qq(<html><head><title>Select Flight</title></head>);
  print include('left-menu.scrap');
  print h2(qq(Choose Flight)); 
  print p(qq(<a href = "/FLIGHTS/upload.cgi">Upload a new flight</a>)); 
  print p(qq(Choose from the flights below )); 
  show_flight_list(); 
  print include('footer.scrap'); 
  }

sub show_flight_list { 
  #my ($dir) = '/var/www/members/html/TRACES'; 
  my ($dir) = '/var/www/members/html/FLIGHTS/traces/'; 
  opendir(DIR, $dir); 
  my (@dir) = readdir(DIR); 
  closedir(DIR); 
  print "<ol>"; 
  for my $file (@dir) { 
    next unless $file =~ /\.kmz$/; 
    print qq(<li> <a href="?view=$file">$file</a>\n); 
    } 
  print "</ol>"; 
  }  


sub show_map {
  my ($input)=shift; 
  print google_header("http://members.skylinesoaring.org/TRACES/$input");
  #print google_header("http://members.skylinesoaring.org/FLIGHTS/traces/$input");
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


sub include {
        # Pull file from the INCLUDES directory
        # output of subroutine is that file.
  my $file = shift;
  my $answer;
  my ($dir, $fulldir);
  use Cwd;
  $fulldir=getcwd;
  $dir = 'skyline' if ($fulldir =~ m#/var/www/skyline#);
  warn ("The pwd is $fulldir\n") if $DEBUG;
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
