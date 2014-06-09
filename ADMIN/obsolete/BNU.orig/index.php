<?php

// -------------------------------------------------------------------------------
//
// FSGuide
//
// (c) 2003-2004, Tamas TURCSANYI
// contact through: http://demoscene.hu/trajic
//
// http://fsguide.sourceforge.net
//
// -------------------------------------------------------------------------------

date_default_timezone_set('UTC'); 
error_reporting(E_ALL);

define('AMP', '&amp;');
define('SP', '&nbsp;');
define('NL',"\n");
define('USERINI_EXPLODECHAR', ',');

include('config/config.inc.php');
include('config/user.common.php');
include( $default['USER_INCLUDE'] );

session_start();
init();

header("Content-Type: text/html; charset=".$default['CHARSET']);
include('translations/lang_'.$default['LOCALE'].'.inc.php');
include('includes/predefine.inc.php');

$todo = '';
if ( isset( $_REQUEST['todo'] ) )
  $todo = htmlspecialchars( $_REQUEST['todo'] );

if ( $todo == 'login' ) 
  login();

authenticate();

switch( $todo ) {
  case 'filelist':    
    include('includes/actions.inc.php');
    show_filelist();     
    break;

  case 'copy':        
    include('includes/actions.inc.php');
    execute_action('copy');   display(); break;
  case 'delete':      
    include('includes/actions.inc.php');
    execute_action('delete'); display(); break;
  case 'move':
    include('includes/actions.inc.php');
    execute_action('move');   display(); break;

  case 'mkdirright':  
    include('includes/actions.inc.php');
      if ( userhasrights( getcurrentuser(), trailing_slash( $dirright ), 'MKDIR' ) )
        $message .= mkdir_form( $dirright ); 
      else
        $message .= STR_ACCESS_MKDIR_DENIED . ':<BR>' . $dirright ;
    display(); break;

  case 'mkdirleft':   
    include('includes/actions.inc.php');
      if ( userhasrights( getcurrentuser(), trailing_slash( $dirleft ), 'MKDIR' ) )
        $message .= mkdir_form( $dirleft ); 
      else
        $message .= STR_ACCESS_MKDIR_DENIED . ':<BR>' . $dirleft;
    display(); break;

  case 'createdir':
    if ( userhasrights( getcurrentuser(), trailing_slash( $_REQUEST['parentdir'] ), 'MKDIR' ) )
      mkdir( $_REQUEST['parentdir'] . '/' . basename($_REQUEST['dirname']) ); 
    else
      $message .= STR_ACCESS_MKDIR_DENIED . ':<BR>' . $_REQUEST['parentdir'];
    display(); break;

  case 'rename':
    include('includes/actions.inc.php');
    $filelist = filelist();
    if (isset($filelist[0])) {
      $filename = $filelist[0][0];
      $targetdir = $dirleft;
    }
    if (!isset($filename) && isset( $filelist[1] ) ) {
      $filename  = $filelist[1][0];
      $targetdir = $dirright;
    }
    if (isset($filename)) {
      if ( userhasrights( getcurrentuser(), trailing_slash( $targetdir ), 'RENAME' ) )
        $message .= rename_form($targetdir . '/' . $filename);
      else
        $message .= STR_ACCESS_RENAME_DENIED . ':<BR>' . $targetdir;
    }
    display();
    break;

  case 'dorename':	
    include('includes/actions.inc.php');
    if ( userhasrights( 
          getcurrentuser(),   
          trailing_slash( dirname($_REQUEST['originame']) ), 
          'RENAME' 
         ) ) {
      rename(
        $_REQUEST['originame'],
        dirname($_REQUEST['originame']) . '/' . basename($_REQUEST['newname'])
      );
    }
    else
      $message .= STR_ACCESS_RENAME_DENIED . ':<BR>' . dirname( $_REQUEST['originame'] );

    display();
    break;

  case 'uploadleft':  
    if ( userhasrights( getcurrentuser(), trailing_slash( $dirleft ), 'UPLOAD' ) ) {
      include('includes/upload.inc.php');
      uploadform($dirleft); 
    }
    else {
      $message .= STR_ACCESS_UPLOAD_DENIED . ':<BR>' . $dirleft;
      display();
    }    
    break;
  case 'uploadright':  
    if ( userhasrights( getcurrentuser(), trailing_slash( $dirright ), 'UPLOAD' ) ) {
      include('includes/upload.inc.php');
      uploadform($dirright); 
    }
    else {
      $message .= STR_ACCESS_UPLOAD_DENIED . ':<BR>' . $dirright;
      display();
    }    
    break;
  case 'upload':
    include('includes/upload.inc.php');
    upload(); display(); break;

  case 'openfile': 
    if ( userhasrights( getcurrentuser(), trailing_slash( fixed_dirname( $_REQUEST['f'] ) ), 'ACCESS' ) ) {
      include('includes/viewer.inc.php');
      display_file( $_REQUEST['f'] ); 
    }
    else {
      $message .= STR_ACCESS_DENIED . ':<BR>' . fixed_dirname( $_REQUEST['f'] );
      display();
    }    
    break;

  case 'download': 
    if ( userhasrights( getcurrentuser(), trailing_slash( fixed_dirname( $_REQUEST['f'] ) ), 'ACCESS' ) ) {
      download( $_REQUEST['f'] ); 
    }
    else {
      $message .= STR_ACCESS_DENIED . ':<BR>' . fixed_dirname( $_REQUEST['f'] );
      display();
    }    
    break;

  case 'edit':            
    if ( userhasrights( getcurrentuser(), trailing_slash( fixed_dirname( $_REQUEST['f'] ) ), 'MODIFY' ) ) {
      include('includes/editor.inc.php'); 
      edit_file( $_REQUEST['f'] ); 
    }
    else {
      $message .= STR_ACCESS_MODIFY_DENIED . ':<BR>' . fixed_dirname( $_REQUEST['f'] );
      display();
    }    
    break;

  case 'save_textfile':   
    if ( userhasrights( getcurrentuser(), trailing_slash( fixed_dirname( $_REQUEST['f'] ) ), 'MODIFY' ) ) {
      include('includes/editor.inc.php'); 
      save_textfile(); 
    }
    else 
      $message .= STR_ACCESS_MODIFY_DENIED . ':<BR>' . fixed_dirname( $_REQUEST['f'] );

    display(); 
    break;

  case 'save_binaryfile': 
    if ( userhasrights( getcurrentuser(), trailing_slash( fixed_dirname( $_REQUEST['f'] ) ), 'MODIFY' ) ) {
      include('includes/editor.inc.php'); 
      save_binaryfile(); 
    }
    else 
      $message .= STR_ACCESS_MODIFY_DENIED . ':<BR>' . fixed_dirname( $_REQUEST['f'] );

    display(); 
    break;

  case 'dialog_select':   
    include('includes/gui.inc.php'); 
    dialog_select(); break;

  case 'logout': 
    logout(); break;

  default:    		  display(); break;
}

// ----------------------------------------------------------------------------
function download( $filename ) { 
global $default;
 
  $size = filesize( $filename );

  if ( $size ) {

    // using fopen-fread to try being backward-compatible 
    $filehandle = fopen( $filename, 'rb');

    if ( is_resource( $filehandle ) ) {

      include('includes/browser.php');
      $browser = new Browser();
      $browser->downloadheaders( 
        basename( $filename ), 
        null, 
        null, 
        filesize( $filename ) 
      );

      $remaining = $size;

      while ( $remaining > 0 ) {
        $contents = fread( $filehandle, $default['DOWNLOAD_CHUNKSIZE'] );
        echo $contents;
        $remaining = $remaining - $default['DOWNLOAD_CHUNKSIZE'];
        if ( $default['DOWNLOAD_CHUNKSLEEP'] > 0 )
          sleep( $default['DOWNLOAD_CHUNKSLEEP'] );
      }
      fclose( $filehandle );

    }
  }

} 

// ----------------------------------------------------------------------------
function authenticate() { 

  if ( $GLOBALS['default']['USER_AUTHENTICATION'] ) {
    // we need authentication

    if ( 
      !isset( $_SESSION['fsguideuser'] ) ||
      !is_array( $_SESSION['fsguideuser'] )
    ) 
      showloginform( '' );

  }

}

// ----------------------------------------------------------------------------
function logout() {

  if ( isset( $_SESSION['fsguideuser'] ) ) 
    unset( $_SESSION['fsguideuser'] );
  header("Location: index.php");

}

// ----------------------------------------------------------------------------
function login() {

  if ( 
       ( $_POST['i_login'] == 'default' ) || 
       !checkpassword( $_POST['i_login'], $_POST['i_password'] )
     )

    showloginform( '<B>' . STR_LOGIN_ERROR . '</B><BR>' );

  else {

    $_SESSION['fsguideuser'] = Array(
      'user' => $_POST['i_login']
    );

    loadusersettings( getcurrentuser() );
    init();

  }

}

// ----------------------------------------------------------------------------
function showloginform( $message ) {

  echo 
    pageheader() .
    '<FORM METHOD=POST ACTION="index.php">' . NL . 
    getparams() .
    '<INPUT TYPE=HIDDEN NAME="todo" VALUE="login">' . NL .
    '<CENTER>'. NL .
    '<H1>FSGuide</H1>' . NL .
    STR_LOGIN_INFO . '<BR>' . NL . 
    $message . 
    '<TABLE>'. NL .
    '<TR><TD>' . STR_LOGIN_LOGIN . '</TD><TD><INPUT TYPE=TEXT NAME="i_login"></TD></TR>'. NL .
    '<TR><TD>' . STR_LOGIN_PASSWORD . '</TD><TD><INPUT TYPE=PASSWORD NAME="i_password"></TD></TR>'. NL .
    '<TR><TD></TD><TD><INPUT TYPE=SUBMIT VALUE="' . STR_LOGIN_BUTTON . '"></TD></TR>' . NL .
    '</TABLE>' . NL .
    '</FORM>' .
    '</CENTER>'. NL .
    pagefooter();

  die();

}

// ----------------------------------------------------------------------------
function getcurrentuser() {

  if ( $GLOBALS['default']['USER_AUTHENTICATION'] ) { 

    if ( isset( $_SESSION['fsguideuser']['user'] ) ) 
      return $_SESSION['fsguideuser']['user'];
    else
      return 'default';

  }
  else
    return 'default';

}

// ----------------------------------------------------------------------------
function fsguideErrorHandler ($errno, $errstr, $errfile, $errline) { 

  if ( !isset( $GLOBALS['message'] ) ) 
    $GLOBALS['message']  = "<LI>" . $errstr . NL;
  else
    $GLOBALS['message'] .= "<LI>" . $errstr . NL;

  if ( defined( 'DISPLAY_ERRORS' ) )
    echo "<LI>" . $errstr . NL;

} 

// ----------------------------------------------------------------------------
function init() {
global
  $default, $sortpass, $panelfiletypes, 
  $message, $current, $dirleft, $dirright;

  // setting commonly used global variables
  $message = '';
  $old_error_handler = set_error_handler("fsguideErrorHandler"); 

  $sortpasses   = Array();
  $sortpasses[] = 'sortby0=' .(isset($_REQUEST['sortby0'])  ? $_REQUEST['sortby0']  : $default['PANEL_SORTBY']);
  $sortpasses[] = 'sortdir0='.(isset($_REQUEST['sortdir0']) ? $_REQUEST['sortdir0'] : $default['PANEL_SORTDIRECTION']);
  $sortpasses[] = 'sortby1=' .(isset($_REQUEST['sortby1'])  ? $_REQUEST['sortby1']  : $default['PANEL_SORTBY']);
  $sortpasses[] = 'sortdir1='.(isset($_REQUEST['sortdir1']) ? $_REQUEST['sortdir1'] : $default['PANEL_SORTDIRECTION']);

  $sortpass     = implode(AMP, $sortpasses); // sorting parameters for GET

  // DISGUSTING HACK FOR INTERNET EXPLORER
  // 
  // When a form has multiple submit buttons with the same NAME attribute, 
  // IE posts the VALUE attribute (the label of them). However, for
  // national characters, this causes problems, so it's not a good choice.
  //
  // There would be a better solution:
  //   <BUTTON TYPE=SUBMIT NAME='todo' VALUE='filelist'>filelist button label</BUTTON> 
  //   <BUTTON TYPE=SUBMIT NAME='todo' VALUE='rename'>rename button label</BUTTON> 
  // would be great - unfortunately, it does not work well under IE. IE does not care about 
  // standards, and is not submitting the selected submit button's value field. 
  // Instead, a (randomly???) selected button value is submitted.
  // 
  // So the only working option is to use different NAME attributes for 
  // the submit buttons, and find out if such a button was pressed (=present in $_REQUEST)
  //

  if ( !isset( $_REQUEST['todo'] ) ) 
    // if we have a standard todo parameter set, we do not need
    // to find out if there was a named submit button pressed
    foreach ( $_REQUEST as $key => $value ) {
      if ( preg_match( '/^todo(.+)$/', $key, $matches ) ) {
        $_REQUEST['todo'] = $matches[ 1 ];
      }
    }

  $panelfiletypes    = Array();
    // an array holding filetypes (extensions) for each panel
    // this array is used in the advanced selection dialog

  loadusersettings( getcurrentuser() );

  $current  = _r(getcwd());
  $dirleft  = isset($_REQUEST['lt']) ? $_REQUEST['lt'] :
          (
           isset( $default['STARTDIR_LEFT'] ) &&
           strlen( $default['STARTDIR_LEFT'] )
           ?
             strip_trailing_slash( _r($default['STARTDIR_LEFT']) )
           :
              $current
          );

  $dirright = isset($_REQUEST['rt']) ? $_REQUEST['rt'] :
          (
           isset( $default['STARTDIR_RIGHT'] ) &&
           strlen( $default['STARTDIR_RIGHT'] ) 
           ?
             strip_trailing_slash( _r($default['STARTDIR_RIGHT']) )
           :
             $current
          );

}

// ----------------------------------------------------------------------------
function determine_filetype($filename) {
global $default;

  // DETERMINE BY EXTENSION ---------------------------------------------------

  if (eregi('^.*\.(mp3)$',$filename))     	return 'audio/mp3';

  if (eregi('^.*\.(inc|phtml|php(3-4)?)$',$filename)) 
  						return 'text/phps';
  if (eregi('^.*\.(htm|html)$',$filename)) 
  						return 'text/html';
  if (eregi('^.*\.(doc|dot)$',$filename))       return 'text/msword';
  if (eregi('^.*\.(xls|xlt)$',$filename))       return 'text/msexcel';
  if (eregi('^.*\.rtf$',$filename))     	return 'text/rtf';
  if (eregi('^.*\.pdf$',$filename))     	return 'text/pdf';
  if (eregi('^.*\.ps$',$filename))      	return 'text/ps';

  // DETERMINE BY FILE CONTENTS -----------------------------------------------
  //
  // ... using the first $default['PAGER_BYTES'] bytes of the file
  // (we have to avoid reading the entire file into memory)

  $content = '';
  $file    = fopen($filename,'r');
  $content = fread($file, $default['PAGER_BYTES']);
  fclose($file);

  // IMAGE by content -------------------------------
     $dimensions = strlen($content) ? getimagesize($filename) : '';
     if (is_array($dimensions))
       return 'image';

  // BINARY by content ------------------------------
     if (preg_replace('/[^\x09\x0c\x0d\x0a\x20-\x7f\x9f-\xfe]/',
           '.', $content) != $content)
       return 'binary';

  // WHEN IT'S NOT BINARY NOR A KNOWN FILETYPE => TEXT

  return 'text/plain';

}

// ----------------------------------------------------------------------------
function display() {
global 
  $dirleft, $dirright, $message, $sortpass;

  $leftpanel  = gui_panel($dirleft,  0); // sets $leftpanel_enabled
  $rightpanel = gui_panel($dirright, 1); // sets $rightpanel_enabled

  $leftpanel_enabled  = $GLOBALS['leftpanel_enabled'];
  $rightpanel_enabled = $GLOBALS['rightpanel_enabled'];

  $hiddenparameters = 
    "<INPUT TYPE=HIDDEN NAME='lt' VALUE= '$dirleft'>".NL.
    "<INPUT TYPE=HIDDEN NAME='rt' VALUE= '$dirright'>".NL.
    '<INPUT TYPE=HIDDEN VALUE="on" NAME="include_path">'.NL.
    '<INPUT TYPE=HIDDEN VALUE="on" NAME="include_size">'.NL.
    '<INPUT TYPE=HIDDEN VALUE="on" NAME="include_datetime">'.NL.
    '<INPUT TYPE=HIDDEN VALUE="on" NAME="include_attribs">'.NL.
    getparams(Array('sortby0','sortdir0','sortby1','sortdir1'));

  $columnskeleton = 
    '<TD VALIGN=TOP WIDTH="50%%">'.NL.
    '  <TABLE CELLPADDING=2 CELLSPACING=0 WIDTH="100%%">'.NL.
    '    <CAPTION CLASS="headerfooter">%s</CAPTION>'.NL.
    '%s'.
    '</TABLE>'.NL.
    '</TD>';

  // IF THE OTHER PANEL IS ENABLED TO COPY TO
  $copy_enabled = 
    ( $leftpanel_enabled  && 
      userhasrights( getcurrentuser(), trailing_slash( $dirright ), 'COPY' ) )
  ||
    ( $rightpanel_enabled && 
      userhasrights( getcurrentuser(), trailing_slash( $dirleft ), 'COPY' ) )
  ;

  // IF RENAME IS ENABLED IN ONE OF THE PANELS
  $rename_enabled = 
    ( $leftpanel_enabled &&
      userhasrights( getcurrentuser(), trailing_slash( $dirleft ), 'RENAME' ) )
  || 
    ( $rightpanel_enabled &&
      userhasrights( getcurrentuser(), trailing_slash( $dirright ), 'RENAME' ) )
  ;

  $move_enabled = 
    $leftpanel_enabled && 
    $rightpanel_enabled && 
    (
      ( userhasrights( getcurrentuser(), trailing_slash( $dirleft ),  'MOVEFROM' ) && 
        userhasrights( getcurrentuser(), trailing_slash( $dirright ), 'COPY' ) )
    ||
      ( userhasrights( getcurrentuser(), trailing_slash( $dirright ),  'MOVEFROM' ) && 
        userhasrights( getcurrentuser(), trailing_slash( $dirleft ), 'COPY' ) )
    )
  ;

  $mkdirleft_enabled   = $leftpanel_enabled  && userhasrights( getcurrentuser(), trailing_slash( $dirleft ),  'MKDIR' ) ;
  $mkdirright_enabled  = $rightpanel_enabled && userhasrights( getcurrentuser(), trailing_slash( $dirright ), 'MKDIR' ) ;
  $uploadleft_enabled  = $leftpanel_enabled  && userhasrights( getcurrentuser(), trailing_slash( $dirleft ),  'UPLOAD' ) ;
  $uploadright_enabled = $rightpanel_enabled && userhasrights( getcurrentuser(), trailing_slash( $dirright ), 'UPLOAD' ) ;

  $filelist_enabled =
    ( $leftpanel_enabled && 
      userhasrights( getcurrentuser(), trailing_slash( $dirleft ),  'FILELIST' ) )
    ||
    ( $rightpanel_enabled &&
      userhasrights( getcurrentuser(), trailing_slash( $dirright ),  'FILELIST' ) )
    ;

  $delete_enabled =
    ( $leftpanel_enabled && 
      userhasrights( getcurrentuser(), trailing_slash( $dirleft ),  'DELETE' ) )
    ||
    ( $rightpanel_enabled &&
      userhasrights( getcurrentuser(), trailing_slash( $dirright ),  'DELETE' ) )
    ;

  $menu = indent(
    '<CENTER>' . NL .
    '<TABLE WIDTH="100%%" CELLSPACING=2 CELLPADDING=0 BORDER=0>' . NL .
    '<TR>' . 
      '<TD WIDTH="30%%" ROWSPAN=2>'.
        '<TABLE CELLPADDING=0 CELLSPACING=0 BORDER=0 WIDTH="100%%">'.
        '<TR><TD><A CLASS="small" HREF="#%s">%s</A></TD><TD CLASS="small" VALIGN=MIDDLE ALIGN=CENTER>%s</TD></TR>'.
        '</TABLE>' .
      '</TD>'.
      '<TD CLASS="small" WIDTH="40%%" ALIGN=CENTER COLSPAN=2>'.
      ( $rename_enabled ? 
          '<INPUT TYPE=SUBMIT CLASS="menubutton" NAME="todorename" VALUE="'.STR_RENAME.'">&nbsp;'
        : '' ) .
      ( $copy_enabled ? 
          '<INPUT TYPE=SUBMIT CLASS="menubutton" NAME="todocopy"   VALUE="'.STR_COPY.'">&nbsp;'
        : '' ) .
      ( $move_enabled ? 
          '<INPUT TYPE=SUBMIT CLASS="menubutton" NAME="todomove" VALUE="'.STR_MOVE.'">&nbsp;'
        : '' ) .
      ( $delete_enabled ? 
          '<INPUT TYPE=SUBMIT CLASS="menubutton" NAME="tododelete"   VALUE="'.STR_DELETE.'">&nbsp;'
        : '' ) .
      ( $filelist_enabled ? 
          '<INPUT TYPE=SUBMIT CLASS="menubutton" NAME="todofilelist" VALUE="'.STR_FILELIST.'">&nbsp;'
        : '' ) .
      '</TD>'.
      '<TD WIDTH="30%%" ROWSPAN=2 ALIGN=RIGHT>'. NL .
        '<TABLE CELLPADDING=0 CELLSPACING=0 BORDER=0 WIDTH="100%%">'. NL .
        '<TR><TD CLASS="small" VALIGN=MIDDLE ALIGN=CENTER>%s</TD><TD ALIGN=RIGHT><A CLASS="small" HREF="#%s">%s</A></TD></TR>' . NL .
        '</TABLE>' . NL .
      '</TD>' . NL .
    '</TR>' . NL .
    '<TR>' . NL .
      '<TD CLASS="small" WIDTH="20%%" VALIGN=TOP ALIGN=RIGHT>'. NL .
      ( $leftpanel_enabled ? 
          ($mkdirleft_enabled ?
              '<INPUT TYPE=SUBMIT CLASS="menubutton" NAME="todomkdirleft" VALUE="'.STR_MKDIRLEFT.'">&nbsp;'
            : '') .
          ( $uploadleft_enabled && ini_get('file_uploads') ? 
              '<INPUT TYPE=SUBMIT CLASS="menubutton" NAME="todouploadleft" VALUE="'.STR_FILE_UPLOAD_LEFT.'">'
            : '')
        :
          ''
      ).
      '</TD>'. NL .
      '<TD CLASS="small" WIDTH="20%%" VALIGN=TOP>' . NL .
      ( $rightpanel_enabled ? 
          ( $uploadright_enabled && ini_get('file_uploads') ? 
              '<INPUT TYPE=SUBMIT CLASS="menubutton" NAME="todouploadright" VALUE="'.STR_FILE_UPLOAD_RIGHT.'">&nbsp;'
            : '') .
          ( $mkdirright_enabled ? 
              '<INPUT TYPE=SUBMIT CLASS="menubutton" NAME="todomkdirright" VALUE="'.STR_MKDIRRIGHT.'">'
            : '') 
        :
          '') .
      '</TD>' .
    '</TR>'.
    '</TABLE>'. NL.
    '</CENTER>'.NL,
    '  ');

  define('DISPLAY_ERRORS', 1);

  if ( $GLOBALS['default']['USER_AUTHENTICATION'] ) 
    $userinfo  = 
      sprintf( STR_LOGIN_LOGGEDINAS, getcurrentuser() ) . ' ' .
      sprintf( 
        '<A HREF="index.php?todo=logout'. AMP .
          'lt=' . $dirleft . AMP . 
          'rt=' . $dirright . AMP . 
          $sortpass . '">%s</A>', 
        STR_LOGIN_LOGOUT );
  else
    $userinfo = STR_LOGIN_DEFAULT_USER;

  $copyright =
    '&copy; 2003-2004, <A TARGET="_blank" HREF="http://demoscene.hu/trajic/">trajic</A>';

  $ratingcode =
   NL . 
   '<table align=center width=150 border="0" cellpadding="3" cellspacing="0" bgcolor="#e0e0e0">
      <tr>
        <td align=center>
          <a class="small" 
             href="http://www.hotscripts.com/cgi-bin/rate.cgi?ID=28614" 
             target="_blank">If you like FSGuide, please rate it! Click here!</a>
        </td>
      </tr>
    </table>' . NL ;

  if ( $message )
    if ( strpos( '<LI>', $message ) !== false )
      $message = "<UL>" . $message . "</UL>";

  echo
    pageheader() .

    (strlen($message) ?
      sprintf( $message, $hiddenparameters) . NL : '') .

    "<FORM METHOD=POST NAME='theform' ACTION='index.php'>" . NL .
      $hiddenparameters . NL .
      sprintf( $menu, 
        'bottom', STR_BOTTOM, 
        $userinfo, 
        '',
        'bottom', STR_BOTTOM 
      ) . NL .
    "  <TABLE WIDTH='100%' CELLPADDING=0 CELLSPACING=2 CLASS='blackborder'>".NL.
    "    <TR>" . NL.

        // left panel

        indent(
          sprintf(
            $columnskeleton,
            gui_navigatorline($dirleft,  0) . gui_bookmarks( 0 ),
            indent( $leftpanel, '    ')),
          '      ') . NL .

        // divider

    "      <TD CLASS='divider'>".
             gui_synchronize(0) . '<BR>' .
             gui_synchronize(1) .
          "</TD>".NL.

        // right panel

        indent(
          sprintf(
            $columnskeleton, 
            gui_navigatorline($dirright, 1) . gui_bookmarks( 1 ), 
            indent( $rightpanel,'    ')),
          '      ') . NL .

    "    </TR>". NL .
    "  </TABLE>". NL .
      sprintf( $menu, 
        'top', STR_TOP, $copyright,
        $ratingcode, 'top', STR_TOP
      ) . NL .

    "</FORM>" . NL .

    pagefooter();
}

// ----------------------------------------------------------------------------
function gui_panel($dir, $sideflag) {
global 
  $default, $sortpass, $dirleft, $dirright, 
  $message, $filetypes, $filealts, 
  $leftpanel_enabled, $rightpanel_enabled;

  if (!($hnd = @opendir($dir)))
    return '<TR><TD>'.STR_ERROR_DIR.'</TD></TR>';

  $dirleftparent      = fixed_dirname( $dirleft );
  $dirrightparent     = fixed_dirname( $dirright );
  $panelfiletypes     = Array();

  $GLOBALS['leftpanel_enabled']  = 1;
  $GLOBALS['rightpanel_enabled'] = 1;

  if ( ( $sideflag == 0 )  && !userhasrights( getcurrentuser(), trailing_slash( $dirleft ), 'ACCESS' ) ) {
    $GLOBALS['leftpanel_enabled'] = 0;
    return ( '<TR><TD>' . STR_ACCESS_DENIED . ':<BR>' . trailing_slash( $dirleft ) . '</TD></TR>' );
  }

  if ( ( $sideflag == 1 ) && !userhasrights( getcurrentuser(), trailing_slash( $dirright ), 'ACCESS' ) ) {
    $GLOBALS['rightpanel_enabled'] = 0;
    return ( '<TR><TD>' . STR_ACCESS_DENIED . ':<BR>' . trailing_slash( $dirright ) . '</TD></TR>' );
  }

  // COLLECT DIRECTORY INFORMATION
  //
  // $files is a kinda pervert multi-dimensional array
  // (uses eg. $files['filesize'][$number_of_file] instead of
  // $files[$number_of_file]['filesize'])
  // but I had to use this approach because the multisort() function
  // expects arrays of this structure 

  $files = Array(
    'rowbegin' => Array(),  'icon'      => Array(),  'dir' => Array(),
    'isdotdir' => Array(),  'isdotdir1' => Array(),  'sortname' => Array(),
    'filename' => Array(),  'size'      => Array(),  'link' => Array(),
    'ctime' =>    Array(),  'atime'     => Array(),  'mtime' => Array(),
    'rights' =>   Array()
  );

  $i = 0;
  $sum['size']  = 0;
  $sum['files'] = 0;
  $mtime_min    = time();
  $mtime_max    = 0;

  while(($filename = readdir($hnd))!==false) {

    $isdotdir1 = ($filename == '.');
    $isdotdir2 = ($filename == '..');
    $isdotdir  = $isdotdir1 || $isdotdir2;

    $dir = is_dir(($sideflag ? $dirright : $dirleft) . '/' . $filename );

    $passdirright = $dirright;
    $passdirleft  = $dirleft;

    if ($sideflag  && $dir) 
      $passdirright = 
        $isdotdir2 ?
          $dirrightparent 
          : 
          $dirright . ($isdotdir1 ? '' : '/' . $filename);

    if (!$sideflag && $dir) 
      $passdirleft = 
        $isdotdir2 ? 
          $dirleftparent 
          : 
          $dirleft . ($isdotdir1 ? '' : '/' . $filename);

    $icon    = '';
    $iconalt = '';

    eregi("^(.*)(\.([^\.]+))$", $filename, $nameparts);
    $ext     = '';

    if ( isset( $nameparts[ 3 ] ) ) {
      $ext = strtolower( $nameparts[ 3 ] );

      foreach ($filetypes as $key => $value) {
        $extensions = explode(',' , $value);
        if (in_array( $ext, $extensions )) {
          $icon    = $key;
          $iconalt = $filealts[$key];
        }
      }

      if ( 
           strlen( $nameparts[ 1 ] ) &&       // file isn't a linux hidden file
           !in_array( $ext, $panelfiletypes ) // extension is not yet stored
         ) 
       $panelfiletypes[] = $ext;

      unset($nameparts);
    }

    if ($dir && !$isdotdir) { $icon = 'folder'; $iconalt = $filealts['folder']; }
    if ($isdotdir2) 	    { $icon = 'back';   $iconalt = $filealts['parentdir']; }

    $thisfileWithPath = trailing_slash( $sideflag ? $dirright : $dirleft ) . $filename;
    $stat             = stat( $thisfileWithPath );

    $link = "index.php". 
              "?lt=" . rawurlencode( $passdirleft ) . 
              AMP . "rt=" . rawurlencode( $passdirright ) . 
              AMP . $sortpass .
      ($dir ?
        '' 
        : 
       AMP . 'todo=openfile' . AMP . 'f=' . rawurlencode( $thisfileWithPath ) 
      );

    $linkdownload = '';

    if ( 
         !$dir && 
         is_readable( $thisfileWithPath ) && 
         ( $stat['size'] > 0 ) 
       )
      $linkdownload = 
        "index.php?". 
          'lt=' . rawurlencode( $passdirleft ) . AMP . 
          'rt=' . rawurlencode( $passdirright ) . AMP . 
          'todo=download' . AMP . 
          'f=' . rawurlencode( $thisfileWithPath ) . AMP . 
          $sortpass
      ;

    if ( !$isdotdir ) {
      $sum['size']  += $stat['size'];
      $sum['files']++;
    }

    $files['icon'][$i]      = 
      (
        strlen($icon) ? 
          "<IMG BORDER=0 ALT='$iconalt' TITLE='$iconalt' SRC='images/iconsets/" . 
           $GLOBALS['default']['ICONSET'] . '/' . 
           $icon . '.' . $GLOBALS['default']['ICONSET_EXTENSION'] . "'>"
         : 
           SP
      );
    $files['extension'][$i]    = $ext;
    $files['dir'][$i]          = $dir;
    $files['isdotdir'][$i]     = $isdotdir;
    $files['isdotdir1'][$i]    = $isdotdir1;
    $files['filename'][$i]     = $filename;
    $files['sortname'][$i]     = strtoupper($filename);
    $files['link'][$i]         = $link;
    $files['linkdownload'][$i] = $linkdownload;
    $files['size'][$i]         = $stat['size'];
    $files['ctime'][$i]        = $stat['ctime'];
    $files['atime'][$i]        = $stat['atime'];
    $files['mtime'][$i]        = $stat['mtime'];
    $files['rights'][$i]       =
          (is_readable($thisfileWithPath) ? 'r' : SP) .
          (is_writable($thisfileWithPath) ? 'w' : SP) .
          (function_exists('is_executable') ?
            (is_executable($thisfileWithPath) ? 'x' : SP) 
            : 
            SP
            ) 
        ;

    if ( $stat['mtime'] < $mtime_min ) 
      $mtime_min = $stat['mtime'] ;

    if ( $stat['mtime'] > $mtime_max ) 
      $mtime_max = $stat['mtime'] ;

    $i++;
  }

  closedir($hnd);

  // SORT CONTENTS ------------------------------------------------------------

  // 'sort by' field per side and 'sort by' field of current panel ------------
  $sortby0 = $default['PANEL_SORTBY'];
  $sortby1 = $default['PANEL_SORTBY'];

  if (isset($_REQUEST['sortby0']) && in_array($_REQUEST['sortby0'],Array('name','size','mtime')))
    $sortby0 = $_REQUEST['sortby0'];
  if (isset($_REQUEST['sortby1']) && in_array($_REQUEST['sortby1'],Array('name','size','mtime')))
    $sortby1 = $_REQUEST['sortby1'];
  $sortby = $sideflag == 0 ? $sortby0 : $sortby1;

  // 'sort direction' per side and 'sort direction' of current panel ----------

  $sortdir0 = $default['PANEL_SORTDIRECTION'];
  $sortdir1 = $default['PANEL_SORTDIRECTION'];

  if (isset($_REQUEST['sortdir0']) && ($_REQUEST['sortdir0']=='desc'))
    $sortdir0 = SORT_DESC;
  if (isset($_REQUEST['sortdir1']) && ($_REQUEST['sortdir1']=='desc'))
    $sortdir1 = SORT_DESC;
  $sortdir = $sideflag == 0 ? $sortdir0 : $sortdir1;

  // the $sort array is going to be a two-dimensional array.
  // it's gonna contain arrays that are containing the parameter-
  // triples for multisort():
  //
  //   $sort[n] = Array('field_name_of_files_array', sort_direction, sort_type);
  //
  // as defined below ($bydir, $byfilename, etc.)
  // these arrays are going to be inserted into the $sort array
  // in the order needed
  //
  $bydir      = Array('dir',      SORT_DESC, SORT_STRING);
  $byfilename = Array('sortname', SORT_ASC,  SORT_STRING);
  $bysize     = Array('size',     SORT_ASC,  SORT_NUMERIC);
  $bymtime    = Array('mtime',    SORT_ASC,  SORT_STRING);

  $sort = Array();

  // in the parameter-array corresponding the user-chosen sort 
  // field (eg. $by...) we always change the second field (the
  // sort direction), that's what $by...[1] = $sortdir; is for.
  // other fields' sort order are used as defaults

  // if the user wants to see the directories first,
  // we only have to change the order of arrays

  if ($default['PANEL_DIRSFIRST']) 
    switch ($sortby) {
      case 'size':  $bysize[1]  = $sortdir;     $sort = Array($bydir, $bysize, $byfilename, $bymtime); break;
      case 'mtime': $bymtime[1] = $sortdir;     $sort = Array($bydir, $bymtime, $byfilename, $bysize); break;
      default:      $byfilename[1]  = $sortdir; $sort = Array($bydir, $byfilename, $bysize, $bymtime); break;
    }
  else
    switch ($sortby) {                          
      case 'size':  $bysize[1]  = $sortdir;     $sort = Array($bysize, $byfilename, $bymtime, $bydir); break;
      case 'mtime': $bymtime[1] = $sortdir;     $sort = Array($bymtime, $byfilename, $bysize, $bydir); break;
      default:      $byfilename[1]  = $sortdir; $sort = Array($byfilename, $bysize, $bymtime, $bydir); break;
    }

  array_multisort(
    // 'dot directories' (eg. '.' and '..') are always
    // in the first place
    $files['isdotdir'],  SORT_DESC, SORT_STRING,
    $files['isdotdir1'], SORT_DESC, SORT_STRING,

    $files[ $sort[0][0] ], $sort[0][1], $sort[0][2], 
    $files[ $sort[1][0] ], $sort[1][1], $sort[1][2], 
    $files[ $sort[2][0] ], $sort[2][1], $sort[2][2], 
    $files[ $sort[3][0] ], $sort[3][1], $sort[3][2], 

    /* 
       we have to include remaining fields in the sorting procedure
       too, to keep the multi-dimensional array consistent 
    */

    $files['atime'],
    $files['ctime'],
    $files['rights'],
    $files['icon'],
    $files['link'],
    $files['linkdownload'],
    $files['filename'],
    $files['extension']
  );

  // RENDERING FILEPANEL

  $out = '';

  $rightsformatting = Array(
    'r' => '<FONT CLASS="green">r</FONT>',
    'w' => '<FONT CLASS="red">w</FONT>',
    'x' => '<FONT CLASS="blue">x</FONT>'
  );

  for ($i = 0; $i < count($files['filename']); $i++) {

    // check if current file is the '.' filename, and whether to show
    // it or not

    if ( 
         ( $files['filename'][ $i ] != '.' ) 
         || 
         ( 
           ( $files['filename'][ $i ] == '.' ) && 
           $default['PANEL_SHOW_ONEDOTFILE'] 
         )
       ) {
    $showname = $files['filename'][$i];
    if (strlen($showname) > $default['PANEL_FILENAME_MAXLENGTH'])
      $showname = substr($files['filename'][$i],0, $default['PANEL_FILENAME_MAXLENGTH']) . $default['PANEL_FILENAME_APPEND'];

    $out .=
      '<TR '.($i % 2 == 0 ? 'CLASS="alternate" ' : '').'>'. NL .
      '  <TD CLASS="borderright" WIDTH=10>' .
        "<INPUT TYPE=HIDDEN NAME='props$sideflag$i' " .
        "VALUE='" .
          $files['filename'][$i] . "," .
          strtolower( $files['extension'][$i] ) . "," .
          $files['size'][$i] . "," .
          $files['rights'][$i] . "," .
          $files['mtime'][$i] . 
        "'>" .
        (!$files['isdotdir'][$i] ? 
          "<INPUT TYPE=CHECKBOX NAME='cbx$sideflag$i' VALUE='".$files['filename'][$i]."'>" : '') .
        '&nbsp;'.
      '</TD>' . NL .

      '  <TD WIDTH="20" CLASS="borderright">' .
        $files['icon'][$i] .
      '</TD>' . NL .

      '  <TD CLASS="borderright">' .
        "<A TITLE=\"" . htmlspecialchars( $files['filename'][$i] ) . "\" ".
          "HREF='" . $files['link'][$i] . "'>" .
          ($files['dir'][$i] ? '<B>'.$showname.'</B>' : $showname) . "</A>" .
      '</TD>' . NL .

      '  <TD CLASS="borderright">' .
        (
          strlen( $files['linkdownload'][$i] ) ?
            '<A TITLE="' . 
                  htmlspecialchars( 
                    STR_DOWNLOAD . ' ' . $files['filename'][$i] 
                  ) . '" '.
               'HREF="' . $files['linkdownload'][$i] . '">' .
            '<IMG BORDER=0 ALT="' . htmlspecialchars( STR_DOWNLOAD ) . '" '. 
               'SRC="images/iconsets/' . $GLOBALS['default']['ICONSET'] . '/' . 
                 'download.' . $GLOBALS['default']['ICONSET_EXTENSION'] . 
            '">' .
            '</A>'
          :
            '&nbsp;'
        ) .
      '</TD>' . NL .

      '  <TD CLASS="borderright" ALIGN=RIGHT>' .
        (!$files['isdotdir'][$i] && !$files['dir'][$i] ? number_format($files['size'][$i]) : SP) .
      '</TD>' . NL .

      '  <TD CLASS="small borderright" ALIGN=CENTER TITLE="created: '.
        date( "Y-m-d H:i:s", $files['ctime'][$i] ) . ', last access:'.
        date( "Y-m-d H:i:s", $files['atime'][$i] ) . '">' .
        date( "Y-m-d H:i:s", $files['mtime'][$i] ) .
      '</TD>' . NL .

      '  <TD WIDTH=20 CLASS="mono">' .
        strtr( $files['rights'][$i], $rightsformatting ) .
      '</TD>' . NL .
      '</TR>' . NL;
    } // dot filename

  } // for cycle

  // APPLY HEADER AND FOOTER ON THE CURRENT PANEL -----------------------------

  $sortdir  = $sortdir  == 4 ? 'asc' : 'desc';
  $sortdir0 = $sortdir0 == 4 ? 'asc' : 'desc';
  $sortdir1 = $sortdir1 == 4 ? 'asc' : 'desc';

  $sortlink = str_replace( '%', '%%',
      '<A HREF="index.php?'.
         'lt=' . rawurlencode( $dirleft ) . AMP .
         'rt=' . rawurlencode( $dirright ) . AMP
  );

  if ($sideflag == 0) 

    $sortlink .= 
      'sortby1='.  $sortby1 .AMP.
      'sortdir1='. $sortdir1.AMP.
      'sortby0=%s'.AMP.
      'sortdir0=%s">%s</A>';

  else

    $sortlink .=
      'sortby0='.  $sortby0 .AMP.
      'sortdir0='. $sortdir0.AMP.
      'sortby1=%s'.AMP.
      'sortdir1=%s">%s</A>';

  $passtypes = implode(',', $panelfiletypes );

  $checkbox_gadgets = 

    "<TABLE BORDER=0 CELLSPACING=2 CELLPADDING=0>" . NL . 
    "<TR>" . NL .

    "<TD><A CLASS='highlight' TITLE='" . STR_SELECTOR_SELECT_ALL .    "' ".
      "HREF='javascript:void(0);' ONCLICK='fill_checkboxes($sideflag, true)'>".
      "<IMG ALT='" . STR_SELECTOR_SELECT_ALL .    "' SRC='images/select_all.png' BORDER=0></A></TD>" . NL .

    "<TD><A CLASS='highlight' TITLE='" . STR_SELECTOR_SELECT_NONE .   "' ".
      "HREF='javascript:void(0);' ONCLICK='fill_checkboxes($sideflag, false)'>".
      "<IMG ALT='" . STR_SELECTOR_SELECT_NONE .   "' SRC='images/select_none.png' BORDER=0></A></TD>" . NL .

    "</TR><TR>" . 

    "<TD><A CLASS='highlight' TITLE='" . STR_SELECTOR_SELECT_INVERT . "' ".
      "HREF='javascript:void(0);' ONCLICK='alternate_checkboxes($sideflag)'>".
      "<IMG ALT='" . STR_SELECTOR_SELECT_INVERT . "' SRC='images/select_invert.png' BORDER=0></A></TD>" . NL .

    "<TD><A CLASS='highlight' TITLE='" . STR_SELECTOR_SELECT_DIALOG . "' ".
      "HREF='javascript:void(0);' ONCLICK='javascript:window.open(\"".
        "index.php?todo=dialog_select".
          "&amp;types=".$passtypes.
          "&amp;sideflag=$sideflag".
          "&amp;mtime_min=".$mtime_min.
          "&amp;mtime_max=".$mtime_max.
        "\",\"dialogselect\",\"height=500,width=300,toolbars=no,resizable=yes\");'>".
      "<IMG ALT='" . STR_SELECTOR_SELECT_DIALOG . "' SRC='images/select_dialog.png' BORDER=0></A></TD>". NL .

    "</TR></TABLE>" . NL
    ;

  $out =
    '<TR CLASS="headerfooter">'. NL .
    '<TD CLASS="borderright borderhoriz">' . $checkbox_gadgets . '</TD>' . NL .
    '<TD CLASS="borderright borderhoriz">'.SP.'</TD>'.NL.
    '<TD CLASS="borderright borderhoriz">'.STR_FILENAME.'&nbsp;'.
       sprintf($sortlink,'name', 'asc', sprintf(SORT_UP, STR_FILENAME)).
       sprintf($sortlink,'name', 'desc',sprintf(SORT_DN, STR_FILENAME)).'</TD>'.NL.
    '<TD CLASS="borderright borderhoriz">'.SP.'</TD>'.NL.
    '<TD CLASS="borderright borderhoriz">'.STR_FILESIZE.
       sprintf($sortlink,'size', 'asc', sprintf(SORT_UP, STR_FILESIZE)).
       sprintf($sortlink,'size', 'desc',sprintf(SORT_DN, STR_FILESIZE)).'</TD>'.NL.
    '<TD CLASS="borderright borderhoriz">'.STR_LASTMODIFIED.'&nbsp;'.
       sprintf($sortlink,'mtime','asc', sprintf(SORT_UP, STR_LASTMODIFIED)).
       sprintf($sortlink,'mtime','desc',sprintf(SORT_DN, STR_LASTMODIFIED)).'</TD>'.NL.
    '<TD CLASS="borderhoriz">'.SP.'</TD>'.NL.
    '</TR>'.NL.

      $out . 

    '<TR CLASS="headerfooter">'. NL .
    '<TD CLASS="borderright borderhoriz">' . $checkbox_gadgets . '</TD>'.NL.
    '<TD COLSPAN=4 CLASS="borderright borderhoriz" ALIGN=CENTER>'.
       sprintf(STR_SUM, number_format( $sum['size'] ), $sum['files'] ).
       '</TD>'.NL.
    '<TD CLASS="borderright borderhoriz">'.SP.'</TD>'.NL.
    '<TD CLASS="borderhoriz">'.SP.'</TD>'.NL.
    '</TR>'.NL;

  // hunt and replace the image of the current order to an inverted image
  // by finding the link around it 
  // (sort_up.gif => sort_inv_up.gif, sort_dn.gif => sort_inv_dn.gif )
  // [it's much easier than placing dozens of 'if' or ' ? : ' structures
  //  in the previous block]

  $regexp = 
    "(<A.*" . "sortby"  . $sideflag . "=" . $sortby . ".*".
              "sortdir" . $sideflag . "=" . $sortdir . 
          ".*SRC=.*)sort_(.*) (.*<\/A>)";

  $out    = preg_replace("/$regexp/U","\\1sort_inv_\\2 \\3",$out);

  return $out;

}

// ----------------------------------------------------------------------------
function gui_synchronize ($sideflag) {
global $dirleft, $dirright;

  if ($sideflag == 0)
    return '<A CLASS="highlight" TITLE="'.STR_SYNCLEFTTORIGHT.'" HREF="index.php?lt='.$dirleft.AMP.'rt='.$dirleft.'">&raquo;</A>';
  else
    return '<A CLASS="highlight" TITLE="'.STR_SYNCRIGHTTOLEFT.'" HREF="index.php?lt='.$dirright.AMP.'rt='.$dirright.'">&laquo;</A>';

}

// ----------------------------------------------------------------------------
function gui_navigatorline($dir, $sideflag) {
global $sortpass, $dirleft, $dirright;

  $linkformat =
    "<A HREF='index.php?lt=%s" . AMP . "rt=%s" . AMP . $sortpass . "'>%s</A>";

  if ( ereg('^([a-zA-Z]?:?\/?)$', $dir, $results )) {
    $dir = $results[1];
    return 
      sprintf( 
        $linkformat, 
        ($sideflag == 1 ? $dirleft : $dir), 
        ($sideflag == 1 ? $dir : $dirright), 
        $dir
      );
  }
  else {
    $dirbase  = basename( $dir );
    $dir      = fixed_dirname( $dir );
    $finaldir = $dir == '/' ? $dir . $dirbase : "$dir/$dirbase";
    return 
      gui_navigatorline( $dir, $sideflag ) . 
      ( $dir == '/' ? '' : '/' ) . 
        sprintf(
          $linkformat, 
          ($sideflag == 1 ? $dirleft : $finaldir), 
          ($sideflag == 1 ? $finaldir : $dirright), 
          $dirbase
        );
  }
}

// ----------------------------------------------------------------------------
function gui_bookmarks( $sideflag ) {
global $default, $dirright, $dirleft, $sortpass;

  $out  = '';
  
  if ( isset( $default['BOOKMARKS'] ) && strlen( $default['BOOKMARKS'] ) ) {

    $bookmarks = explode( USERINI_EXPLODECHAR, $default['BOOKMARKS'] );

    foreach ( $bookmarks as $bookmark ) {

      $link = 
        'index.php?'.
        'lt='.($sideflag==0 ? rawurlencode( $bookmark ) : $dirleft) .
        AMP .
        'rt='.($sideflag==1 ? rawurlencode( $bookmark ) : $dirright) .
        AMP .
        $sortpass;

      $selected = '';
      if ( 
           ( ( $bookmark == $dirleft  ) && $sideflag == 0 ) ||
           ( ( $bookmark == $dirright ) && $sideflag == 1 ) 
         )
        $selected = 'SELECTED';

      $out .= 
        '<OPTION ' . $selected . ' VALUE="' . $link . '">' . 
        $bookmark . '</OPTION>' . NL;
    }

    $out = 
      '<BR>' .
      '<SELECT ONCHANGE="if ( this[this.selectedIndex].value.length ) location.href=this[this.selectedIndex].value;">' . NL .
      '<OPTION VALUE="">' . STR_JUMP_TO . '</OPTION>' . NL .
        $out.
      '</SELECT>'.NL;

  }

  return $out;
}

// ----------------------------------------------------------------------------
function filelist() {

  $f = Array();
  foreach( $_REQUEST as $key => $value )
    if (ereg('^cbx([01]{1})[0-9]+$', $key, $results))
      $f[ $results[1] ][] = $value;
  return $f;

}

// ----------------------------------------------------------------------------
function strip_trailing_slash( $dir ) {

  if ( 
       ( strlen( $dir ) > 0 ) &&
       ( substr( $dir, strlen( $dir ) - 1, 1 ) == '/' ) 
     )
    return substr( $dir, 0, strlen( $dir ) - 1 );
  else
    return $dir;

}

// ----------------------------------------------------------------------------
function trailing_slash( $dir ) {

  if ( substr( $dir, strlen( $dir ) - 1, 1 ) == '/' ) 
    return $dir;
  else
    return $dir . '/';

}

// ----------------------------------------------------------------------------
function fixed_dirname($s) {

  $s = _r( dirname( $s ) );
  if (ereg("([A-Za-z]:)/$", $s, $r))
    $s = $r[1];
  return $s;

}

// ----------------------------------------------------------------------------
function _r($s) {
  return str_replace('\\', '/', $s);
}

// ----------------------------------------------------------------------------
function indent($string, $indent) {
  return preg_replace('/^(.*)$/m', $indent . "\\1", $string );
}

// ----------------------------------------------------------------------------
function pageheader( $js_localization = false ) {
global $default;

  $additional_script = '';

  if ( $js_localization ) {

    $defines    = get_defined_constants();

    foreach ( $defines as $key => $value ) {
      if ( substr( $key, 0, 3 ) == 'JS_' )
        $additional_script = $key . ' = "' . constant( $key ) . '"' . NL;
    }

    if ( strlen( $additional_script ) )
      $additional_script = 
        "<SCRIPT TYPE='text/javascript'>" . NL . 
        $additional_script . NL . 
        "</SCRIPT>" . NL;
  }

  return 
  '<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN">' . NL .
  '<HTML>' . NL .
  NL .
  '<HEAD>' . NL .
  '  <LINK REL="StyleSheet" TYPE="text/css" HREF="fsguide.css">'. NL . 
  '  <SCRIPT LANGUAGE="JavaScript" SRC="includes/tools.js" TYPE="text/javascript"></SCRIPT>' . NL . 
  '  <META HTTP-EQUIV="Content-Type" CONTENT="text/html; charset='.$default['CHARSET'].'">'. NL .
  $additional_script . 
  '  <TITLE>FSGuide 0.5</TITLE>' . NL .
  '</HEAD>' . NL .
  NL .
  '<BODY>' . NL .
  '<A NAME="top"></A>' . NL;
}

// ----------------------------------------------------------------------------
function pagefooter() {
  return
    '<A NAME="bottom"></A>'.NL.
    '</BODY></HTML>';
}

// ----------------------------------------------------------------------------
function getparams
  (
    $params = Array('lt','rt','sortby0','sortdir0','sortby1','sortdir1','f')
  ) {
  // returns default variables in hidden inputs 

  $out = '';
  foreach ( $params as $value ) {
    if (isset($_REQUEST[$value]))
      $out .= '<INPUT TYPE=HIDDEN NAME="'.$value.'" VALUE="'.htmlspecialchars($_REQUEST[$value]).'">' . NL;
  }
  return $out;

}

?>
