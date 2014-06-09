<?php

// ----------------------------------------------------------------------------
function show_filelist() {
global $dirleft, $dirright, $sortpass, $message;

  echo 
    pageheader() . "<BR>" . 
    "<A HREF='index.php?lt=$dirleft" . AMP . 
      "rt=$dirright" . AMP . 
      $sortpass . "'>" . STR_BACK .
    "</A>" . NL;

  $include_path      = (isset($_REQUEST['include_path'])     && ($_REQUEST['include_path']=='on'));
  $include_size      = (isset($_REQUEST['include_size'])     && ($_REQUEST['include_size']=='on'));
  $include_datetime  = (isset($_REQUEST['include_datetime']) && ($_REQUEST['include_datetime']=='on'));
  $include_attribs   = (isset($_REQUEST['include_attribs'])  && ($_REQUEST['include_attribs']=='on'));

  // RENDER THE FILELIST INTO AN ARRAY, FIND COLUMNS WITH MAXIMUM LENGTH 

  $counter           = 0;
  $files             = Array();
  $filelist_to_pass  = '';
  $textarea_contents = '';
  $maxnamelength     = 0;
  $maxsizelength     = 0;
  $message           = '';
  $filelist = filelist();

  foreach ( $filelist as $sideflag => $sidefiles ) {

    $sourceDir = $sideflag ? $dirright : $dirleft;
    if ( userhasrights( getcurrentuser(), trailing_slash( $sourceDir ), 'FILELIST' ) )
    foreach($sidefiles as $f) {

      $filelist_to_pass .= 
        '<INPUT TYPE=HIDDEN NAME="cbx' . $sideflag . $counter . '" VALUE="' . $f . '">' . NL;

      $files[ $counter ]['name'] = $include_path ? $sourceDir . '/' . $f : $f;
      $files[ $counter ]['stat'] = stat( $sourceDir . '/' . $f );

      if ( $include_attribs )
        $files[ $counter ]['rights'] = 
        '[' .
          (is_readable( $sourceDir . '/' . $f ) ? 'r' : SP) .
          (is_writable( $sourceDir . '/' . $f ) ? 'w' : SP) .
          (function_exists('is_executable') ?
            (is_executable( $sourceDir . '/' . $f ) ? 'x' : SP) 
            : 
            SP
            ) .
        ']';

      if ( strlen( $files[ $counter ]['name'] ) > $maxnamelength )
        $maxnamelength = strlen( $files[ $counter ]['name'] );

      if ( strlen( $files[ $counter ]['stat']['size'] ) > $maxsizelength )
        $maxsizelength = strlen( $files[ $counter ]['stat']['size'] );

      $counter++;

    }
    else {
      $message .= 
      STR_ACCESS_FILELIST_DENIED . ':<BR>' . $sourceDir . '<BR>';
    }

  }

  // RENDER FILELIST

  foreach($files as $onefile) {

    $row        = '';
    $row       .= str_pad( $onefile['name'], $maxnamelength, ' ', STR_PAD_RIGHT );

    if ( $include_size )     $row .= ' ' . str_pad( $onefile['stat']['size'], $maxsizelength, ' ', STR_PAD_LEFT );
    if ( $include_datetime ) $row .= ' ' . date("Y-m-d H:i:s", $onefile['stat']['mtime'] );
    if ( $include_attribs )  $row .= ' ' . $onefile['rights'];

    $textarea_contents .= trim( $row ) . NL;

  }

  echo 
    '<FORM METHOD=POST NAME="filelistform" ACTION="index.php">' . NL .
    $filelist_to_pass . 
    getparams() . 
    '<INPUT TYPE=HIDDEN NAME="todo" VALUE="' . STR_FILELIST . '">' . NL .
    $message .
    '<TEXTAREA NAME="textarea" COLS=80 ROWS=15>' . 
      trim( $textarea_contents ) . 
    '</TEXTAREA><BR>' .
    '<INPUT TYPE=BUTTON ONCLICK="document.forms.filelistform.textarea.select();" VALUE="' . STR_FILELIST_SELECT_ALL . '">' . NL .
    STR_FILELIST_DISPLAY_THESE_FIELDS . ': ' .
    '<INPUT TYPE=CHECKBOX ' . ( $include_path     ? 'CHECKED' : '' ) . ' NAME="include_path">'     . STR_FILELIST_PATH . NL .
    '<INPUT TYPE=CHECKBOX ' . ( $include_size     ? 'CHECKED' : '' ) . ' NAME="include_size">'     . STR_FILELIST_SIZE . NL .
    '<INPUT TYPE=CHECKBOX ' . ( $include_datetime ? 'CHECKED' : '' ) . ' NAME="include_datetime">' . STR_FILELIST_DATETIME . NL .
    '<INPUT TYPE=CHECKBOX ' . ( $include_attribs  ? 'CHECKED' : '' ) . ' NAME="include_attribs">'  . STR_FILELIST_ATTRIBS . NL .
    '<INPUT TYPE=SUBMIT VALUE="' . STR_FILELIST . '">' . NL .
    '</FORM>'
  ;

  echo pagefooter();

}

// ----------------------------------------------------------------------------
function mkdir_form($parentdir) {

  $skeleton = "<INPUT TYPE='%s' NAME='%s' VALUE='%s'>";

  // %s is replaced later in the page builder function 
  // with the default parameters to be passed (left dir, right dir, sorting)

  return  
    '<FORM ACTION="index.php">%s'.
    '<FIELDSET><LEGEND>'.STR_CREATEDIRLEGEND.'</LEGEND>'.NL.
    sprintf(STR_CREATEDIR, $parentdir) . NL .
    '<BR><FONT CLASS="mono">&nbsp;&nbsp;' . $parentdir . '/</FONT>' . 
    sprintf($skeleton, 'HIDDEN', 'todo',      'createdir') . NL .
    sprintf($skeleton, 'HIDDEN', 'parentdir', $parentdir) . NL .
    sprintf($skeleton, 'TEXT',   'dirname',   '') . NL .
    '<BR>'. NL .
    sprintf($skeleton, 'SUBMIT', '',          STR_CREATEDIRBUTTON) . NL .
    '</FIELDSET></FORM>' . NL;

}

// ----------------------------------------------------------------------------
function rename_form($originame) {

  $skeleton = "<INPUT TYPE='%s' NAME='%s' VALUE='%s'>";

  // %s is replaced later in the page builder function
  // with the default parameters to be passed (left dir, right dir)

  return 
    '<FORM ACTION="index.php">%s'.
    '<FIELDSET><LEGEND>'.STR_RENAMELEGEND.'</LEGEND>'.NL.
    sprintf(STR_RENAMEENTERNEWNAME, '<FONT CLASS="mono">'.basename($originame).'</FONT>') . NL .

    sprintf($skeleton, 'HIDDEN', 'originame', $originame) . NL .
    sprintf($skeleton, 'HIDDEN', 'todo',      'dorename') . NL .
    sprintf($skeleton, 'TEXT',   'newname',   basename($originame)) . NL .
    '<BR>'. NL .
    sprintf($skeleton, 'SUBMIT', '',          STR_RENAMEBUTTON) . NL .
    '</FIELDSET></FORM>' . NL;

}

// ----------------------------------------------------------------------------
function filesystem_action($from, $to, $actionType) {
global $message;

  if (is_dir($from)) {

    $thisdir = opendir($from);

    while ($thisobject = readdir($thisdir))
      if (!ereg('^\.{1,2}$', $thisobject)) {

        if (is_dir("$from/$thisobject")) {
          $fullname = "$to/$thisobject";
          if ($actionType != 2) 
            mkdir($fullname);

          filesystem_action("$from/$thisobject", $fullname, $actionType);

          if ($actionType)
            rmdir("$from/$thisobject");
        }
        else
          filesystem_action("$from/$thisobject", $to, $actionType);
      }
    closedir($thisdir);
  }
  else { 
    $to .= "/" . basename($from);
    switch ($actionType) {
      case 0:  copy($from, $to); break;
      case 1:  rename($from, $to); break;
      case 2:  unlink($from); break;
      default: $message .= "undefined action"; break;
    }
  }
}

// ----------------------------------------------------------------------------
function execute_action($action) {
global $dirleft, $dirright, $message;

  $filelist = filelist();
  foreach($filelist as $sideflag => $sidefiles) {
    $sourceDir      = $sideflag ? $dirright : $dirleft;
    $destinationDir = $sideflag ? $dirleft  : $dirright;

    foreach($sidefiles as $f) {

      switch ($action) {
        case 'copy':   
          if ( !userhasrights( getcurrentuser(), trailing_slash( $destinationDir ), 'COPY' ) ) {
            $message .= 
              STR_ACCESS_COPY_DENIED . ':<BR>' . trailing_slash( $destinationDir )
            ;
            return;
          }
          $passAction = 0; 
          break;

        case 'move':
          if ( !userhasrights( getcurrentuser(), trailing_slash( $sourceDir ), 'MOVEFROM' ) ) {
            $message .=
              STR_ACCESS_MOVEFROM_DENIED . ':<BR>' . trailing_slash( $sourceDir )
            ;
            return;
          }
          if ( !userhasrights( getcurrentuser(), trailing_slash( $destinationDir ), 'COPY' ) ) {
            $message .=
              STR_ACCESS_MOVETO_DENIED . ':<BR>' . trailing_slash( $destinationDir )
            ;
            return;
          }
          $passAction = 1;
          break;

        case 'delete': 
          if ( !userhasrights( getcurrentuser(), trailing_slash( $sourceDir ), 'DELETE' ) ) {
            $message .=
              STR_ACCESS_DELETE_DENIED . ':<BR>' . trailing_slash( $sourceDir )
            ;
            return;
          }
          $passAction = 2; 
          break;
        default:       
          $message .= 'Undefined action:' . $action . "<BR>\n";
          return;
          break;
      }

      $source = "$sourceDir/$f";
      $source_is_dir = is_dir($source);
      $destination = $destinationDir;

      if ( $source_is_dir && ( $passAction < 2 ) ) {
        $destination .= "/$f";
        mkdir($destination);
      }

      filesystem_action($source, $destination, $passAction);

      if ( ($passAction > 0) && $source_is_dir )
        rmdir($source);
    }
  }
}

?>