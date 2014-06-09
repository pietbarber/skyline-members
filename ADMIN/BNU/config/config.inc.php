<?php

// ------------ USER AUTHENTICATION -------------------------------------------

// include file containing all the functions needed to handle users
// default one is a portable .ini user handler that needs
// no database access
//
// this is a system setting, cannot be overridden in user.ini
//
$default['USER_INCLUDE'] = 'config/user.ini.php';

// it this is set to true, user login name and password 
// is required to use FSGuide. if it's set to false,
// then no login is required, and the settings of the [default]
// user will be used from user.ini
//
// this is a system setting, cannot be overridden in user.ini
//
$default['USER_AUTHENTICATION'] = false;

// placement and name of user.ini file
//
// VERY IMPORTANT:
//
// 1) move user.ini outside of document root!
//    if you leave it in /config/user.ini, users can 
//    download it easily by typing 
//      http://example.com/fsguide_url/config/user.ini
//
// 2) disable access to the folder containing this ini file
//    by configuring an access control rule in user.ini
//    example:
//    
//    setting here:
//    $default['USER_CONFIGFILE'] = 'c:/safe/directory/user.ini';
//      (for Linux/Unix:
//       $default['USER_CONFIGFILE'] = '/safe/directory/user.ini';)
//
//    access control rule:
//      dir9=c:/safe/directory/,-ALL
//      (for Linux/Unix: 
//       dir9=/safe/directory/,-ALL) 
//

// for security reasons, FSGuide won't start with the default settings.
// 
// instead, use something like:
// $default['USER_CONFIGFILE'] = 'c:/some/safe_place/user.ini';
// $default['USER_CONFIGFILE'] = '/some/safe_place/user.ini';

$default['USER_CONFIGFILE'] = '/var/www/members/configuration/boardnotes.ini';

// ------------ LANGUAGE AND LAYOUT -------------------------------------------
//
// all these settings can be overridden in user.ini
//
// default language file to use
//   - by default (English), it's 'en' 	=> translation/lang_en.inc.php
//   - for Hungary, it's 'hu' 		=> translation/lang_hu.inc.php
//
// this language file will be used upon startup (eg. login screen)
// and even for the interface - if it's not overridden by the user
// settings (in user.ini)

$default['LOCALE']  = 'en';

// Here you can specify the charset to be used in HTTP headers
// to display 
//   iso-8859-1 is Western (Latin-1)
//   iso-8859-2 is Central European (Latin-2)

$default['CHARSET'] = 'iso-8859-1';

// icon sets: you can choose which icon set to use.
// Actually, the iconset name you set here is the folder name 
// under images/icons, so take care of letter case if you 
// use another icon set and the OS is case sensitive for the filenames.
//
// From version 0.4, the following icon sets are available:
// - noia (GNOME Noia theme - a nice, colorful 24x24 pixel icon set), 
// - bk (Landscapes Icon Set created by Barbara Kaemper, high contrast icons), 
// - ben (icon set sent by Ben of hooboo.com),
// - qicons (QIcons 0.1 by Andi Peredri)
// - apache (yee old Apache webserver icon set)

$default['ICONSET'] 		= 'noia';

// extension for the images in the iconset

$default['ICONSET_EXTENSION'] 	= 'png';

// ------------ PANEL CONTENTS ------------------------------------------------

// all these settings can be overridden in user.ini

// show directories first in the panels (true or false)
$default['PANEL_DIRSFIRST']          = true;

// default sort field ('name', 'size', or 'mtime')
$default['PANEL_SORTBY']             = 'name';

// default sort direction
//
// if you want to set it in user.ini:
//   - use 4 instead of SORT_ASC  (ascending order)
//   - use 3 instead of SORT_DESC (descending order)
// (these are default PHP constants)

$default['PANEL_SORTDIRECTION']      = SORT_ASC;   // SORT_ASC, SORT_DESC

// too long filenames are cut, you can specify maximum filename length
$default['PANEL_FILENAME_MAXLENGTH'] = 21;

// you may append a string (eg. '...', '&gt;' or anything else)
// when a filename is cut
$default['PANEL_FILENAME_APPEND']    = '...'; 

// if you want to see the current directory file in subdirectories 
// (the '.' file), change this to true
$default['PANEL_SHOW_ONEDOTFILE']    = false;

// ------------ EDITOR --------------------------------------------------------

// all these settings can be overridden in user.ini

// size of textarea field for text editing
$default['EDITOR_COLS'] = 80;
$default['EDITOR_ROWS'] = 25;

// use decimal values in binary editor?
$default['EDITOR_BINEDITOR_DECIMAL_EDIT'] = 0;

// recommended [default]: 256 bytes per page and 16 bytes per line
$default['EDITOR_BINEDITOR_BYTES_PERSCREEN'] = 256;
$default['EDITOR_BINEDITOR_BYTES_PERLINE']   = 16;

// there's a page selector select box when editing binary files
// you can specify the resolution of this pager in percents
//
// (having a 120kb file, and a 10% setting you'll have a select option
// at every 12kbs)
$default['EDITOR_BINEDITOR_PAGER_PERCENTS']  = 5;

// ------------ VIEWER --------------------------------------------------------

// all these settings can be overridden in user.ini

// the 'built-in PHP viewer' creates a function list
// you can specify the number of functions in the listing table per row
$default['VIEWER_FUNCTIONS_PER_LINE'] = 8;

// number of bytes (characters) to display - both for binary files and
// textfiles
$default['PAGER_BYTES']               = 20000;

// HTML highlighter colors: 

  // HTML tag delimiter ( the '<' and '>' characters)
  $default['VIEWER_HTML_COLORS_TAG']      = '#808080';

  // HTML tag name ( eg. BODY )
  $default['VIEWER_HTML_COLORS_TAGNAME']  = '#0000FF';

  // HTML parameter name ( eg. WIDTH )
  $default['VIEWER_HTML_COLORS_PARNAME']  = '#000080';

  // HTML parameter value ( eg. "100%" )
  $default['VIEWER_HTML_COLORS_PARVALUE'] = '#800000';

// ------------ FILE UPLOADER -------------------------------------------------

// defines how much file inputs to show when uploading a file
// this setting can be overridden in user.ini
$default['UPLOAD_NUMBER_OF_FILE_CONTROLS'] = 5;

// applications offered to run upon successful file upload
// you can use the following replacements:
//   
//   %fullname - the full file path and filename of the uploaded file
//		 in the target directory (eg. /uploaded/files/example.zip)
//   %filename - only the filename of the uploaded file (eg. example.zip)
//   %dir      - only the target directory path, no trailing slash
//		 (eg. /uploaded/files)
//
// you cannot override this setting in user.ini

$default['UPLOAD_APPLICATIONS'] =
  Array(
    Array(
      'name' 		=> 'unzip with PKZIP (Windows, PKZIP (R) v2.50 FAST! by PKWARE Inc.)', 
      'commandline' 	=> 'pkzip32 -nofix -ext -dir -overwrite -nozipextension "%fullname" "%dir" 2>&1'
    ),
    Array(
      'name' 		=> 'unzip with unzip (Linux, unzip 5.5 by Info-ZIP)', 
      'commandline' 	=> 'unzip -o -L %fullname" -d %dir 2>&1'
    ),
    Array(
      'name' 		=> 'unzip with gzip (Linux, GNU gzip)', 
      'commandline' 	=> 'gzip -d %fullname 2>&1'
    ),
    Array(
      'name' 		=> 'untar with tar (Linux, GNU tar)',
      'commandline' 	=> 'tar -xvf --directory %dir %fullname 2>&1'
    )
  );

// ------------ FILE DOWNLOAD -------------------------------------------------

// file download reads up the file to be downloaded in blocks 
// (chunks, whatever). you can specify the size of a single chunk,
// though normally you do not have to change this value
// - do not set it too low, keep it above some 10000s to provide
//   reasonable performance
// - do not set it too high (try to keep it below ~500000, that's ~0.5MB)
//   because in this case the script will use that memory size for
//   a single variable which leads to performance issues
$default['DOWNLOAD_CHUNKSIZE']  = 150000;

// you can specify a sleep-time which will be used to hang up downloading
// for some seconds between echoing the download-chunks. 
//
// it can be used as a simple 'bandwidth-control':
//  - if you set it to 1, then after sending   
//    every DOWNLOAD_CHUNKSIZE bytes to the user, there'll be 1 seconds 
//    wait. downloading a 100MB file this way will take 
//      raw_dl_time_in_seconds + ( 100MB / 50Kb ) * one_second_per_chunk
//    seconds (that's raw_download_time_in_seconds + ~20 seconds)
//
// - use only integer numbers, no floating points (we use the 
//   multiplatform sleep() function which requires an integer). 
//   if you want to finetune downloading, you can still use
//   larger/smaller chunks and longer/shorter sleep-times
//
// - set it to 0 to disable

$default['DOWNLOAD_CHUNKSLEEP'] = 0;

?>
