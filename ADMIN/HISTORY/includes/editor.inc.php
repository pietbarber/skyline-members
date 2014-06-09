<?php

// ----------------------------------------------------------------------------
function edit_file($filename) {
global $dirright, $dirleft, $default;

  $start = 0;
  if (isset($_REQUEST['start'])) $start = $_REQUEST['start'];

  $type = determine_filetype($filename);
  switch ($type) {
    case 'text/plain':   edit_text($filename); break;
    case 'text/phps':    edit_text($filename); break;
    default:	         edit_binary($filename); break;
  }
}

// ----------------------------------------------------------------------------
function save_textfile() {
global $message;

  if ( is_writable( $_REQUEST[ 'f' ] ) ) {
    $f = fopen ( $_REQUEST[ 'f' ], 'w' );
    fputs ( $f, $_REQUEST['contents'] ) ;
    fclose ( $f ) ;
  }
  else
    $message .= sprintf( STR_EDITOR_SAVE_ERROR, $_REQUEST[' f '] );

}

// ----------------------------------------------------------------------------
function save_binaryfile() {
global $message, $default;

  if (is_writable($_REQUEST['f'])) {
    $string = '';

    $start = $_REQUEST['start'];
    $i = $start;
    while (isset($_REQUEST['i_'.$i])) {
      if ($default['EDITOR_BINEDITOR_DECIMAL_EDIT'])
        // decimal edit
        $check = ereg('^[0-9]{1,2}$',$_REQUEST['i_'.$i]);
      else
   	// hexadecimal editing
        $check = ereg('^[0-9a-fA-F]{1,2}$',$_REQUEST['i_'.$i]);

      if (!$check) {
        $message .= sprintf(
          STR_EDITOR_SAVE_ERROR_WRONG_VALUE .
          (
           $default['EDITOR_BINEDITOR_DECIMAL_EDIT'] ?
           STR_EDITOR_SAVE_ERROR_DEC_VALUE_NEEDED :
           STR_EDITOR_SAVE_ERROR_HEX_VALUE_NEEDED
          ),
          $_REQUEST['f'], $i, $_REQUEST['i_'.$i]
        );
        unset($_REQUEST['i_'.$i]);
      }
      else {
        $string .= chr(hexdec(trim($_REQUEST['i_'.$i])));
        $i++;
      }
    }

    if (!strlen($message)) {
      $f = fopen( $_REQUEST['f'], 'rb+' );
      flock($f, LOCK_EX);
      fseek($f, $start);
      fputs($f, $string, strlen($string));
      flock($f, LOCK_UN);
      fclose($f);
    }
  }
  else
    $message .= sprintf(STR_EDITOR_SAVE_ERROR,$_REQUEST['f']);

}

// ----------------------------------------------------------------------------
function edit_binary($filename) {
global $default, $sortpass, $dirleft, $dirright;

  $file = fopen($filename,'r');
  if ($file) {
    $start = 0;
    if (isset($_REQUEST['start']))
      $start = $_REQUEST['start'];

    fseek($file, $start);

    $content   = fread($file, $default['EDITOR_BINEDITOR_BYTES_PERSCREEN'] );
    $perline   = $default['EDITOR_BINEDITOR_BYTES_PERLINE'];
    $fieldlen  = $default['EDITOR_BINEDITOR_DECIMAL_EDIT'] ? 3 : 2;
    $form      = "<TABLE BORDER=1 CELLPADDING=1 CELLSPACING=0>";

    $thisedit  = '';
    $thisline  = '';

    $i         = $start;
    $cellcount = 0;

    while (($i-$start) < $default['EDITOR_BINEDITOR_BYTES_PERSCREEN']) {

      if (($i != $start) && ($cellcount == $perline)) {
        $form .=
          '<TR>'.
          '<TD>'.
            strtoupper(str_pad(dechex($i-$perline),8,'0',STR_PAD_LEFT)).
          '</TD>'.
            $thisedit.
          '<TD CLASS="mono">'.
            preg_replace('/[\x00-\x20\x7f-\x9f]/', '.', htmlspecialchars(substr($content, ($i-$start)-$perline, $perline))).
          '</TD>'.
          '</TR>' . NL ;
        $thisedit = '';
        $cellcount = 0;
      }

      $value =
        $default['EDITOR_BINEDITOR_DECIMAL_EDIT'] ?
          ord(substr($content,($i-$start),1)) :
          strtoupper(bin2hex(substr($content,($i-$start),1)));

      $thisedit .=
        '<TD><INPUT NAME="i_'.$i.'" VALUE="'.$value.'" SIZE='.$fieldlen.' MAXLENGTH='.$fieldlen.' TYPE=TEXT></TD>';
      $i++;
      $cellcount++;
    }

    $form .=
      '<TR>'.
        '<TD>'.
          strtoupper(str_pad(dechex($i - $cellcount),8,'0',STR_PAD_LEFT)).
        '</TD>'.
        $thisedit.
        str_repeat('<TD></TD>',$perline - $cellcount).
      '<TD CLASS="mono">'.
          preg_replace('/[\x00-\x20\x7f-\x9f]/', '.', htmlspecialchars(substr($content, ($i-$start) - $cellcount, $perline))).
      '</TD>'.
      '</TR>';

    $form .= "</TABLE>";

    $i = 0;
    $pager    = '';
    $filesize = filesize($filename);
    $optcount = 0;
    $current  = round($start / $default['EDITOR_BINEDITOR_BYTES_PERSCREEN']);
    $all      = floor($filesize / $default['EDITOR_BINEDITOR_BYTES_PERSCREEN']);
    $limits   = ceil($all * ($default['EDITOR_BINEDITOR_PAGER_PERCENTS']/100));

    while ($i < $filesize) {
      if (
          ($optcount < 1) ||
          (abs($current-$optcount) <= 5) ||
          ($optcount % $limits == 0 ) ||
          ($optcount == $all)
         )
        $pager .=
          '<OPTION VALUE="'.$i.'">0x'.
            str_pad(dechex($i),8,'0',STR_PAD_LEFT).
            '&nbsp;|&nbsp;'.
            str_pad($i,10,'.',STR_PAD_LEFT).
            '&nbsp;|&nbsp;#'.
            str_pad($optcount,5,'.',STR_PAD_LEFT).
            '&nbsp;|&nbsp;'.
            str_pad(round(100 * $i / $filesize),3,'.',STR_PAD_LEFT) . '%' .
          '</OPTION>' . NL;

      $i = $i + $default['EDITOR_BINEDITOR_BYTES_PERSCREEN'];
      $optcount++;
    }

    $pager = str_replace('VALUE="'.$start.'"','VALUE="'.$start.'" SELECTED',$pager);

    $nav =
      '<A HREF="index.php?'.
        'lt='.$dirleft . AMP .
        'rt='.$dirright . AMP .
        $sortpass . '">'.STR_BACK.'</A> '.
      '<A HREF="index.php?todo=openfile'. AMP .
        'f='.$filename . AMP .
        'lt='.$dirleft . AMP .
        'rt='.$dirright . AMP .
        $sortpass . '">'.STR_VIEW.'</A> '.
        $filename. ' ';

    if ($filesize > $default['EDITOR_BINEDITOR_BYTES_PERSCREEN']) {
      $n =
        "<A HREF='index.php?".
          "todo=edit" . AMP .
          "f=" . $_REQUEST['f'] . AMP .
          "lt=$dirleft" . AMP .
          "rt=$dirright" . AMP .
          $sortpass . AMP .
          "start=%d'>%s</A>";

      $nav .=
        "- " .
        ($start ? sprintf($n, $start - $default['EDITOR_BINEDITOR_BYTES_PERSCREEN'], STR_LESS) : '') .
        ' ' .
        ($start + $default['EDITOR_BINEDITOR_BYTES_PERSCREEN']<$filesize ? sprintf($n, $start+$default['EDITOR_BINEDITOR_BYTES_PERSCREEN'], STR_MORE) : '');
    }

    echo
      pageheader().
      '<PRE>'.
      $nav.
      '</PRE>'.
      '<FORM METHOD=POST ACTION="index.php">'.NL.
      '<INPUT TYPE=HIDDEN NAME="todo" VALUE="edit">'.NL.
      getparams() .
      '<SELECT CLASS="mono" NAME="start">'. NL .
        '<OPTION VALUE="0">'.
            'hex offset'.          '&nbsp;|&nbsp;'.
            'dec offset'.          '&nbsp;|&nbsp;&nbsp;&nbsp;'.
            'page'.                '&nbsp;|&nbsp;'.
            'percent'.
        '</OPTION>' . NL.
      str_replace('.','&nbsp;',$pager) .
      '</SELECT>'. NL .
      '<INPUT TYPE=SUBMIT VALUE="open">'.
      '</FORM>'.
      '<HR>'.
      '<FORM METHOD=POST ACTION="index.php">'.
      '<INPUT TYPE=HIDDEN NAME="todo" VALUE="save_binaryfile">'.NL.
      '<INPUT TYPE=HIDDEN NAME="start" VALUE="'.$start.'">'.NL.
      getparams().
      $form .
      '<INPUT TYPE=SUBMIT VALUE="'.STR_EDITOR_SAVE.'">'.NL.
      '</FORM>'.
      pagefooter();
  }
}

// ----------------------------------------------------------------------------
function edit_text($filename) {
global $dirleft, $dirright, $sortpass, $default;

  $content =
    function_exists('file_get_contents') ?
      file_get_contents($filename) :
      implode('',file($filename));

  $chars  = count_chars($content, 0);

  $nav =
    "<A HREF='index.php?lt=$dirleft" . AMP .
         "rt=$dirright" . AMP .
         $sortpass . "'>".STR_BACK.
         "</A> " .
    "<A HREF='index.php?todo=openfile". AMP .
      "lt=$dirleft" . AMP .
      "rt=$dirright" . AMP .
      $sortpass . AMP .
      "f=".rawurlencode($filename).
      "'>".STR_VIEW."</A>".
    ' '.$filename.' ';

  $content = htmlspecialchars($content);
  echo
    pageheader().
    '<PRE>'.
    $nav.NL.
    '</PRE>'.
    '<HR>'.
    ($chars[13]+1) . ' '.STR_LINES.NL.
    '<HR>'.NL.
    '<FORM METHOD=POST ACTION="index.php">'.NL.
    '<INPUT TYPE=HIDDEN NAME="todo" VALUE="save_textfile">'.NL.
    getParams().
    '<TEXTAREA COLS='.$default['EDITOR_COLS'].' ROWS='.$default['EDITOR_ROWS'].' NAME="contents">'.
    $content.
    '</TEXTAREA><BR>'.NL.
    '<INPUT TYPE=SUBMIT VALUE="'.STR_EDITOR_SAVE.'">'.NL.
    '</FORM>'.NL.
    '<HR>'.NL.
    '<PRE>'.
    $nav.
    '</PRE>'.
    pagefooter();

}

?>