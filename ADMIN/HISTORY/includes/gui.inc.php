<?php

// ----------------------------------------------------------------------------
function dialog_select() {
global $filetypes;

  $sideflag = $_REQUEST['sideflag'];

  $types    = explode( ',', $_REQUEST['types'] );
  asort( $types );

  $extoptions = '';
  foreach ( $types as $value )
    $extoptions .= "<OPTION VALUE='$value'>$value</OPTION>".NL;

  $extgrpoptions = '';
  foreach ( $filetypes as $key => $value )
    $extgrpoptions .= "<OPTION VALUE='$value'>$key</OPTION>".NL;

  echo 
    pageheader( true ) .

    "<FORM ACTION='index.php' NAME='selectdialog'>" . NL .
    "<INPUT TYPE=HIDDEN NAME='originaldateminimum' VALUE='" . $_REQUEST['mtime_min'] . "'>" . NL . 
    "<INPUT TYPE=HIDDEN NAME='originaldatemaximum' VALUE='" . $_REQUEST['mtime_max'] . "'>" . NL . 
    "<CENTER>" . NL .
    "<INPUT ID='doselect'   TYPE=RADIO CHECKED NAME='i_select' VALUE='1'> " .
      "<LABEL FOR='doselect'>". STR_SELECTOR_SELECT . '</LABEL>' . NL .
    "<INPUT ID='dodeselect' TYPE=RADIO NAME='i_select' VALUE='0'> " . 
      "<LABEL FOR='dodeselect'>". STR_SELECTOR_DESELECT . '</LABEL>' . NL .
    "</CENTER>" . NL .

    "<FIELDSET>" . NL .
    "<LEGEND>". STR_SELECTOR_SELECTFILES . "</LEGEND>" . NL .

    "<TABLE ALIGN=CENTER>" . NL .

    "<TR>" . NL .
      "<TD CLASS='dialog'>".
        "<INPUT ID='i_selecttype1' CHECKED TYPE=RADIO NAME='i_selecttype' VALUE='regexp'> ".
        "<LABEL FOR='i_selecttype1'>" . STR_SELECTOR_BYREGEXP . "</LABEL>" . NL .
      ":</TD>" . NL .
      "<TD CLASS='dialog'>".
        "<INPUT CLASS='dialog' ONFOCUS='selecttype(\"regexp\");' TYPE=TEXT NAME='i_byregexp' VALUE='.*'></TD>" . NL .
    "</TR>" . NL .

    "<TR>" . NL .
      "<TD CLASS='dialog'>".
        "<INPUT ID='i_selecttype2' TYPE=RADIO NAME='i_selecttype' VALUE='extension'>".
        "<LABEL FOR='i_selecttype2'>" . STR_SELECTOR_BYEXTENSION . "</LABEL>" . NL .
      ":</TD>" . NL .
      "<TD CLASS='dialog'>".
        "<SELECT CLASS='dialog' ONFOCUS='selecttype(\"extension\");' NAME='i_byext' MULTIPLE=MULTIPLE>$extoptions</SELECT></TD>" . NL .
    "</TR>" . NL .

    "<TR>" . NL .
      "<TD CLASS='dialog'>".
        "<INPUT ID='i_selecttype3' TYPE=RADIO NAME='i_selecttype' VALUE='extgroup'>".
        "<LABEL FOR='i_selecttype3'>" . STR_SELECTOR_BYEXTGROUP . "</LABEL>" . NL .
      ":</TD>" . NL .
      "<TD CLASS='dialog'><SELECT CLASS='dialog' ONFOCUS='selecttype(\"extgroup\");' NAME='i_byextgrp' MULTIPLE=MULTIPLE>$extgrpoptions</SELECT></TD>" . NL .
    "</TR>" . NL .

    "</TABLE>" . NL .
    "</FIELDSET>" . NL .

    "<FIELDSET>" . NL .
    "<LEGEND>" . STR_SELECTOR_OPTIONS . "</LEGEND>" . NL .
    "<TABLE ALIGN=CENTER>" . NL .
    "<TR>" . NL .
      "<TD CLASS='dialog' ><LABEL FOR='i_min'>" . STR_SELECTOR_BYFILESIZE. ":</LABEL></TD>" . NL .
      "<TD CLASS='dialog' >" .
        "<TABLE CELLPADDING=0 CELLSPACING=2>" . NL .
          "<TR><TD CLASS='dialog'><LABEL FOR='i_min'>min =</LABEL></TD><TD><INPUT ID='i_min' CLASS='dialog' SIZE=10 MAXLENGTH=18 TYPE=TEXT VALUE='0' NAME='i_byfilesizemin'></TD></TR>" . NL .
          "<TR><TD CLASS='dialog'><LABEL FOR='i_max'>max =</LABEL></TD><TD><INPUT ID='i_max' CLASS='dialog' SIZE=10 MAXLENGTH=18 TYPE=TEXT VALUE='999999999' NAME='i_byfilesizemax'></TD></TR>" . NL .
        "</TABLE>" . NL .
      "</TD>" . NL .
    "</TR>" . NL .
    "<TR>" . NL .
      "<TD CLASS='dialog'><LABEL FOR='i_mindate'>" . STR_SELECTOR_BYDATETIME . ":</LABEL></TD>" . NL .
      "<TD>".
        "<TABLE CELLPADDING=0 CELLSPACING=2>" . NL .
          "<TR><TD CLASS='dialog'><LABEL FOR='i_mindate'>min =</LABEL></TD><TD>".
          "<INPUT ID='i_mindate' CLASS='dialog' SIZE='10' MAXLENGTH='10' TYPE=TEXT NAME='i_mindate' VALUE='" . date("Y-m-d", $_REQUEST['mtime_min'] ) . "'>" . NL . 
          "<INPUT CLASS='dialog' SIZE='8' MAXLENGTH='8' TYPE=TEXT NAME='i_mintime' VALUE='" . date("H:i:s", $_REQUEST['mtime_min'] ) . "'>" . NL . 
          "</TD></TR>" . 
          "<TR><TD CLASS='dialog'><LABEL FOR='i_maxdate'>max =</LABEL></TD><TD>".
          "<INPUT ID='i_maxdate' CLASS='dialog' SIZE='10' MAXLENGTH='10' TYPE=TEXT NAME='i_maxdate' VALUE='" . date("Y-m-d", $_REQUEST['mtime_max'] ) . "'>" . NL . 
          "<INPUT CLASS='dialog' SIZE='8' MAXLENGTH='8' TYPE=TEXT NAME='i_maxtime' VALUE='" . date("H:i:s", $_REQUEST['mtime_max'] ) . "'>" . NL . 
          "</TD></TR>" . 
        "</TABLE>" . NL .
      "</TD>" . NL .
    "<TR>" . NL .
      "<TD CLASS='dialog'>" . STR_SELECTOR_BYPERMISSION . ":</TD>" . NL .
      "<TD>" .
      "<TABLE CELLPADDING=2 CELLSPACING=0>".
      "<TR>".
        "<TD CLASS='dialog'>" . STR_SELECTOR_YES . "</TD>" . 
        "<TD CLASS='dialog'>" . STR_SELECTOR_NO . "</TD>" . 
      "</TR>" .
      "<TR>" .
        "<TD><INPUT TYPE=CHECKBOX CHECKED NAME='i_permry'></TD>" . 
        "<TD><INPUT TYPE=CHECKBOX CHECKED NAME='i_permrn'></TD>" . 
        "<TD CLASS='dialog'>" . STR_SELECTOR_READABLE . "</TD>" . NL .
      "</TR>".
      "<TR>".
        "<TD><INPUT TYPE=CHECKBOX CHECKED NAME='i_permwy'></TD>" . 
        "<TD><INPUT TYPE=CHECKBOX CHECKED NAME='i_permwn'></TD>" . 
        "<TD CLASS='dialog'>" . STR_SELECTOR_WRITEABLE. "</TD>" . NL .
      "</TR>".
      "<TR>".
        "<TD><INPUT TYPE=CHECKBOX CHECKED NAME='i_permxy'></TD>" . 
        "<TD><INPUT TYPE=CHECKBOX CHECKED NAME='i_permxn'></TD>" . 
        "<TD CLASS='dialog'>" . STR_SELECTOR_EXECUTABLE . "</TD>" . NL .
      "</TR>".
      "</TABLE>".
      "</TD>" . NL .
    "</TR>" . NL .
    "</TABLE>" . NL .
    "</FIELDSET>" . NL .
    "<BR>". NL .
    "<CENTER>" . NL .
    "<INPUT TYPE=BUTTON VALUE='" . STR_SELECTOR_OK . "' ONCLICK='selector(" . $sideflag . ");'>" . NL .
    "<INPUT TYPE=BUTTON VALUE='" . STR_SELECTOR_CLOSEWINDOW . "' ONCLICK='window.close();'>" . NL .
    "</CENTER>" . NL .
    "</FORM>" .
    pagefooter();
}

?>