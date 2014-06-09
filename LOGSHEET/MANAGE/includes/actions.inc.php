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
    '<TEXTAREA NAME="textarea" COLS=90 ROWS=15>' . 
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
function rename_form( $directory, $filelist ) {

  if ( !count( $filelist ) ) 
    return '';

  $skeleton = '<INPUT TYPE="%s" NAME="%s" VALUE="%s">';

  // %s is replaced later in the page builder function
  // with the default parameters to be passed (left dir, right dir)

  $filters = 
    '<TABLE CLASS="headerfooter" CELLPADDING=5 CELLSPACING=0 BORDER=1>' . NL . 
    '<TR><TD CLASS="dialog">' . 
      STR_RENAME_REMOVE_CHARS . ' ' . 
      '<input CLASS="dialog" size="5" maxlength="10" type="text" name="removechars"> '.
      '<input CLASS="dialog" value="' . STR_RENAME_REMOVE_BUTTON . '" type="button" onclick="renamedialog(\'removechars\');"> '.
      '</TD></TR><TR><TD CLASS="dialog">' .
      STR_RENAME_REMOVENUMBER . ' ' .
      '<input CLASS="dialog" value="1" size="5" maxlength="3" type="text" name="removecharsnumber"> ' .
      STR_RENAME_REMOVENUMBER_FROM . ' ' .
      '<input type="radio" id="rt1" checked="checked" name="removetype" value="beginning"><label for="rt1"> ' . STR_RENAME_FROM_BEGINNING . '</label> ' .
      '<input type="radio" id="rt2" name="removetype" value="end"><label for="rt2"> ' . STR_RENAME_FROM_END . '</label> ' .
      '<input type="radio" id="rt3" name="removetype" value="position"><label for="rt3"> ' . STR_RENAME_FROM_POSITION. ': ' .
      '<input type="text"  CLASS="dialog" name="position" value="1" onfocus="document.forms.renameform.removetype[2].checked = 1;" size="3" maxlength="3"></label> ' .
      '<input CLASS="dialog" value="' . STR_RENAME_REMOVE_BUTTON . '" type="button" onclick="renamedialog(\'removecharsnumber\');"> ' .
      '</TD></TR><TR><TD CLASS="dialog">' .
      STR_RENAME_ADD . ' ' .
      '<input CLASS="dialog" size="5" maxlength="3" type="text" name="addstring"> ' .
      STR_RENAME_TO . ' ' .
      '<input type="radio" id="at1" checked="checked" name="addtype" value="beginning"><label for="at1"> ' . STR_RENAME_TO_BEGINNING . '</label> ' .
      '<input type="radio" id="at2" name="addtype" value="end"><label for="at2"> ' . STR_RENAME_TO_END . '</label> ' .
      '<input type="radio" id="at3" name="addtype" value="position"><label for="at3"> ' . STR_RENAME_TO_POSITION. ': ' .
      '<input type="text"  CLASS="dialog" name="addposition" value="1" onfocus="document.forms.renameform.addtype[2].checked = 1;" size="3" maxlength="3"></label> ' .
      '<input CLASS="dialog" value="' . STR_RENAME_ADD_BUTTON . '" type="button" onclick="renamedialog(\'addstring\');"><br> ' .
      '</TD></TR><TR><TD CLASS="dialog">' .
      STR_RENAME_REGEXP . ' ' .
      '<input type="text"  CLASS="dialog" name="research" value="(.*)"> ' .
      '( ' .
      '<input type="checkbox" checked="checked" id="reglobal"     name="reglobal"><label for="reglobal"> ' . STR_RENAME_REPLACE_GLOBAL . '</label> ' .
      '<input type="checkbox" checked="checked" id="reignorecase" name="reignorecase"><label for="reignorecase"> ' . STR_RENAME_REPLACE_IGNORE_CASE . '</label> ' .
      ') ' .
      STR_RENAME_REGEXP_TO . ' ' .
      '<input type="text"  CLASS="dialog" name="rereplace" value="$1"> ' .
      '<input CLASS="dialog" value="' . STR_RENAME_REPLACE . '" type="button" onclick="renamedialog(\'rereplace\');"><br> ' .
      '</TD></TR><TR><TD CLASS="dialog">' .
      STR_RENAME_CASE_CONVERSION . ' ' .
      '<input type="radio" id="cclower" checked="checked" name="caseconversion" value="cclower"><label for="cclower"> ' . STR_RENAME_CCLOWER . '</label> ' .
      '<input type="radio" id="ccupper" name="caseconversion" value="ccupper"><label for="ccupper"> ' . STR_RENAME_CCUPPER . '</label> ' .
      '<input CLASS="dialog" value="' . STR_RENAME_CONVERT . '" type="button" onclick="renamedialog(\'caseconversion\');"><br> ' .
    '</TD>'. NL . 
    '</TR>'. NL . 
    '</TABLE>';

  $files = '';
  foreach ( $filelist as $file ) {
    $files .=
      '<TR><TD><FONT CLASS="mono">' . basename( $file ) . '</FONT></TD><TD>' . NL .
      sprintf($skeleton, 'TEXT',   'newname[' . $directory . '/' . $file . ']', 
        basename( $file ) 
      ) . '</TD></TR>' . NL
    ;
  }

  $out = 
    '<FIELDSET>' . NL .
    '<LEGEND>' . STR_RENAMELEGEND . ' <img src="images/spacer.gif" name="renameicon"></LEGEND>'. NL .
    '<FORM NAME="renameform" ACTION="index.php">%s'.
    sprintf( $skeleton, 'HIDDEN', 'todo', 'dorename') . NL .
    '<TABLE>' . NL . 
      '<TR><TD VALIGN="TOP"><TABLE>'. NL .
         $files .
      '</TABLE></TD>'.
      '<TD VALIGN="TOP">'. NL .
         $filters .
      '</TD></TR>' . NL .
    '</TABLE>'. NL .
    sprintf($skeleton, 'SUBMIT', '', STR_RENAMEBUTTON) . NL .
    sprintf($skeleton, 'RESET', '', STR_RENAME_RESET) . NL .
    '</FIELDSET></FORM>' . NL;

  return $out;

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