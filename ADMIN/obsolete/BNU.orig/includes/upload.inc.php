<?php

// ----------------------------------------------------------------------------
function upload() {
global $message, $dirleft, $dirright;

  if ( !userhasrights( getcurrentuser(), trailing_slash( $_POST['targetdir'] ), 'UPLOAD' ) ) {
    $message .= STR_ACCESS_UPLOAD_DENIED . ':<BR>' . $_POST['targetdir'];
    return;
  }  

  for ($i = 1; $i < $GLOBALS['default']['UPLOAD_NUMBER_OF_FILE_CONTROLS']; $i++ ) {

    if ( isset( $_FILES[ 'file' . $i ] ) ) {
      $thisfile = $_FILES[ 'file' . $i ];
      $failed   = 0;

      if ( $thisfile['error'] != 0 ) {
        switch ( $thisfile['error'] ) {
          case 1: $message .= '<LI>'. sprintf(STR_FILE_UPLOAD_ERROR_FILE_EXCEEDS_INI_SIZE, $thisfile['name'], ini_get('upload_max_filesize') ); break;
          case 2: $message .= '<LI>'. sprintf(STR_FILE_UPLOAD_ERROR_FILE_EXCEEDS_FORM_SIZE, $thisfile['name'] ); break;
          case 3: $message .= '<LI>'. sprintf(STR_FILE_UPLOAD_ERROR_FILE_PARTIAL, $thisfile['name'] ); break;
        }
      }
      else {

        if ( $_POST[ 'app' . $i ] != '-' ) {

          if (
               !move_uploaded_file(
                 $thisfile['tmp_name'], 
                 $_POST['targetdir'] . '/' . $thisfile['name']
               )
             ) 
             $failed = 1;
          else {

            $replaces = Array(
              '%fullname' => $_POST['targetdir'] . '/' . $thisfile['name'],
              '%filename' => $thisfile['name'],
              '%dir'      => $_POST['targetdir']
            );

            $commandline = 
              strtr( 
                $GLOBALS['default']['UPLOAD_APPLICATIONS'][ $_POST[ 'app' . $i ] ] ['commandline'], 
                $replaces
              );

            if ( !eregi( '^.*WIN.*$', PHP_OS ) ) 
              $commandline = escapeshellcmd( $commandline );
              
            if ( !chdir( $_POST['targetdir'] ) )
              $failed = 2;
            else {
              exec( $commandline, $output );

              $message .= 
                '<LI>' . 
                $commandline . '<BR>' . NL . 
                '<TEXTAREA COLS=80 ROWS=4>' . 
                implode( NL, $output ) . 
                '</TEXTAREA><BR>';

              if ( isset( $_POST[ 'drop' . $i ] ) && ( $_POST[ 'drop' . $i ] == 'on' ) ) {
                if (!unlink( $_POST['targetdir'] . '/' . $thisfile['name'] ))
                  $failed = 3;
              }
            }

          }
        }
        else 
          if (
               !move_uploaded_file(
                 $thisfile['tmp_name'], 
                 $_POST['targetdir'] . '/' . $thisfile['name']
               )
             ) 
             $failed = 1;

        switch ($failed) {
          case 1: $message .= '<LI>' . sprintf( STR_FILE_UPLOAD_ERROR, $thisfile[ 'name' ], $_POST['targetdir'] ); break;
          case 2: $message .= '<LI>' . sprintf( STR_FILE_UPLOAD_CHDIR_ERROR, $_POST['targetdir'], $thisfile[ 'name' ] ); break;
          case 3: $message .= '<LI>' . sprintf( STR_FILE_UPLOAD_UNLINK_ERROR, $_POST['targetdir'], $thisfile[ 'name' ] ); break;
        }
      }
    }
  }
}

// ----------------------------------------------------------------------------
function uploadform($targetdir) {
global $default, $dirleft, $dirright, $sortpass;

  $nav  =
    '<A HREF="index.php?'.
      'lt='.$dirleft . AMP .
      'rt='.$dirright . AMP .
      $sortpass . '">'.STR_BACK.'</A> ';

  if (!ini_get('file_uploads')) {

    echo 
      pageheader().
      '<PRE>'.
      $nav .
      '</PRE>'.
      STR_FILE_UPLOAD_DISABLED.
      pagefooter();
    return;

  }
  else {

    $files      = '';
    $colorclass = 0;
    $appselect  = '<OPTION VALUE="-">'. STR_FILE_UPLOAD_NOTHING;
     
     for ($i = 0; $i < count( $GLOBALS['default']['UPLOAD_APPLICATIONS'] ); $i++ ) 
      $appselect .= '<OPTION VALUE="' . $i . '">' . $GLOBALS['default']['UPLOAD_APPLICATIONS'][ $i ]['name'];

    for ($i = 1; $i <= $GLOBALS['default']['UPLOAD_NUMBER_OF_FILE_CONTROLS']; $i++ ) {
      $colorclass = 1 - $colorclass;
      $files .=
       '<TR ' . ( $colorclass ? 'CLASS="alternate"' : '') . '>'.
       '<TD VALIGN=TOP>' .

         STR_FILE_UPLOAD_FILE . ' '.$i.': ' .
           '<INPUT TYPE=FILE NAME="file'.$i.'"></TD><TD>' .

         '<LABEL FOR="appselect' . $i . '">' . STR_FILE_UPLOAD_ACTION . '</LABEL><BR>' .
           '<SELECT NAME="app'.$i.'" ID="appselect'.$i.'">' .  
           $appselect .
           '</SELECT><BR>' .

         '<INPUT TYPE=CHECKBOX ID="dropcbx' . $i . '" NAME="drop'.$i.'">'.
         '<LABEL FOR="dropcbx'.$i.'">'. STR_FILE_UPLOAD_DROPFILE . '</LABEL>' .
         '</TD></TR>'
      ;
    }

    echo
      pageheader().
      '<PRE>'.
      $nav.
      '</PRE>'.
      '<FORM METHOD=POST ENCTYPE="multipart/form-data" ACTION="index.php">'.NL.
      '<INPUT TYPE=HIDDEN NAME="todo" VALUE="upload">'.NL.
      '<INPUT TYPE=HIDDEN NAME="targetdir" VALUE="'.$targetdir.'">'.NL.
      getparams() .
      '<B>'.STR_FILE_UPLOAD_TARGET.': '.$targetdir.'</B><BR>'.NL.
      '<BR>'.
      STR_FILE_UPLOAD_DESC.'<BR>'.NL.
      STR_FILE_UPLOAD_MAXFILESIZE.': '.ini_get('upload_max_filesize').'<BR><BR>'.NL.
      '<TABLE CELLPADDING=3 CELLSPACING=0 BORDER=0>'.NL.
      $files.
      '</TABLE>'.
      '<BR>'.
      '<INPUT TYPE=SUBMIT VALUE="'.STR_FILE_UPLOAD.'">'.
      '</FORM>'.
      '<HR>'.
      pagefooter();
  }
}

?>