<?php

// ----------------------------------------------------------------------------
function display_file($filename) {
global $dirright, $dirleft, $default;

  $pager_bytes = $default['PAGER_BYTES'];
  if (isset($_COOKIE['pager_bytes'])) 
    $pager_bytes = $_COOKIE['pager_bytes'];

  $start = 0;
  if (isset($_REQUEST['start'])) $start = $_REQUEST['start'];

  $type = determine_filetype($filename);
  switch ($type) {
    case 'image':	 view_image($filename, $pager_bytes); break;
    case 'audio/mp3':	 view_with_content_type($filename,'audio/mpeg'); break;
    case 'text/plain':   view_text($filename, $start, $pager_bytes); break;
    case 'text/html':    view_html($filename, $start, $pager_bytes); break;
    case 'text/phps':	 view_php($filename, $start, $pager_bytes); break;
    case 'text/msword':	 view_with_content_type($filename,'application/msword'); break;
    case 'text/msexcel': view_with_content_type($filename,'application/msexcel'); break;
    case 'text/pdf': 	 view_with_content_type($filename,'application/pdf'); break;
    case 'text/rtf': 	 view_with_content_type($filename,'application/rtf'); break;
    case 'text/ps': 	 view_with_content_type($filename,'application/postscript'); break;
    default:	         view_binary($filename, $start, $pager_bytes); break;
  }
}

// ----------------------------------------------------------------------------
function view_html($filename, $start, $pager_bytes) {
global $dirleft, $dirright, $sortpass;

  $content = 
    function_exists('file_get_contents') ? 
      file_get_contents($filename) :
      implode('',file($filename));
  $chars  = count_chars($content, 0);

  $nav = 
    "<A HREF='index.php?".
      "lt=$dirleft" . AMP . 
      "rt=$dirright" . AMP . $sortpass . 
      "'>".STR_BACK."</A> ".
    "<A HREF='index.php?todo=edit". AMP . 
      "lt=$dirleft" . AMP . 
      "rt=$dirright" . AMP . 
      $sortpass . AMP .
      "f=".rawurlencode($filename).
      "'>".STR_EDIT."</A>".
    ' '.$filename.' ';

  if (strlen($content) > $pager_bytes) {
    $n = 
      "<A HREF='index.php?".
        "todo=openfile" . AMP . 
        "f=" . $_REQUEST['f'] . AMP . 
        "lt=$dirleft" . AMP . 
        "rt=$dirright" . AMP . 
        "start=%d'>%s</A>";

    $nav .= 
      "- " . 
      ($start ? sprintf($n, $start - $pager_bytes, STR_LESS) : '') . 
      ' ' . 
      ($start + $pager_bytes<strlen($content) ? sprintf($n, $start + $pager_bytes, STR_MORE) : '');
    $content = substr($content, $start, $pager_bytes);
  }

  $content = 
    preg_replace('/\<(\/?[a-z]+.*)\>/msUie', '"!FSGUIDE_TAGSTART!<!FSGUIDE_TAGEND!".highlight_htmltag("\\1")."!FSGUIDE_TAGSTART!>!FSGUIDE_TAGEND!"', $content );

  $replaces = Array(
    '!FSGUIDE_TAGSTART!' 	=> "<FONT COLOR=".$GLOBALS['default']['VIEWER_HTML_COLORS_TAG'].">",
    '!FSGUIDE_TAGEND!'   	=> "</FONT>",
    '!FSGUIDE_TAGNAMESTART!' 	=> "<FONT COLOR=".$GLOBALS['default']['VIEWER_HTML_COLORS_TAGNAME'].">",
    '!FSGUIDE_TAGNAMEEND!'   	=> "</FONT>",
    '!FSGUIDE_PARNAMESTART!' 	=> "<FONT COLOR=".$GLOBALS['default']['VIEWER_HTML_COLORS_PARNAME'].">",
    '!FSGUIDE_PARNAMEEND!'   	=> "</FONT>",
    '!FSGUIDE_PARVALUESTART!' 	=> "<FONT COLOR=".$GLOBALS['default']['VIEWER_HTML_COLORS_PARVALUE'].">",
    '!FSGUIDE_PARVALUEEND!'   	=> "</FONT>"
  );                  

  $content = htmlspecialchars( $content );
  $content = strtr( $content , $replaces );

  echo 
    pageheader(). 
    '<PRE>'.
    $nav.NL.
    '<HR>'.
    ($chars[13]+1) . ' lines'.NL.
    '<HR>'.
    $content.
    '<HR>'.NL.
    $nav.
    '</PRE>'. 
    pagefooter();

}

// ----------------------------------------------------------------------------
function highlight_htmltag( $string ) {
  $string = stripslashes( $string );

  $string = 
    preg_replace('/([a-z]+)=([^ >]+)/msi','!FSGUIDE_PARNAMESTART!\\1!FSGUIDE_PARNAMEEND!=!FSGUIDE_PARVALUESTART!\\2!FSGUIDE_PARVALUEEND!', $string);

  return '!FSGUIDE_TAGNAMESTART!' . $string . '!FSGUIDE_TAGNAMEEND!';
  
}

// ----------------------------------------------------------------------------
function view_text($filename, $start, $pager_bytes) {
global $dirleft, $dirright, $sortpass;

  $content = 
    function_exists('file_get_contents') ? 
      file_get_contents($filename) :
      implode('',file($filename));
  $chars  = count_chars($content, 0);

  $nav = 
    "<A HREF='index.php?".
      "lt=$dirleft" . AMP . 
      "rt=$dirright" . AMP . $sortpass . 
      "'>".STR_BACK."</A> ".
    "<A HREF='index.php?todo=edit". AMP . 
      "lt=$dirleft" . AMP . 
      "rt=$dirright" . AMP . 
      $sortpass . AMP .
      "f=".rawurlencode($filename).
      "'>".STR_EDIT."</A>".
    ' '.$filename.' ';

  if (strlen($content) > $pager_bytes) {
    $n = 
      "<A HREF='index.php?".
        "todo=openfile" . AMP . 
        "f=" . $_REQUEST['f'] . AMP . 
        "lt=$dirleft" . AMP . 
        "rt=$dirright" . AMP . 
        "start=%d'>%s</A>";

    $nav .= 
      "- " . 
      ($start ? sprintf($n, $start - $pager_bytes, STR_LESS) : '') . 
      ' ' . 
      ($start + $pager_bytes<strlen($content) ? sprintf($n, $start + $pager_bytes, STR_MORE) : '');
    $content = substr($content, $start, $pager_bytes);
  }

  $content = htmlspecialchars($content);
  echo 
    pageheader(). 
    '<PRE>'.
    $nav.NL.
    '<HR>'.
    ($chars[13]+1) . ' lines'.NL.
    '<HR>'.
    $content.
    '<HR>'.NL.
    $nav.
    '</PRE>'. 
    pagefooter();

}

// ----------------------------------------------------------------------------
function view_binary($filename, $start, $pager_bytes) {
global $default, $dirleft, $dirright, $sortpass;

  $nav = 
    "<A HREF='index.php?lt=$dirleft" . AMP . 
      "rt=$dirright" . AMP . 
      $sortpass . 
      "'>".STR_BACK."</A> ".

    "<A HREF='index.php?todo=edit". AMP . 
      "lt=$dirleft" . AMP . 
      "rt=$dirright" . AMP . 
      $sortpass . AMP .
      "f=".rawurlencode($filename).
      "'>".STR_EDIT."</A>".
      " $filename ";

  // we have to avoid reading the entire file into memory

  $content = '';
  $file = fopen($filename,'r');
  fseek($file, $start);
  $content = fread($file, $default['PAGER_BYTES']);
  fclose($file);

  if (filesize($filename) > $pager_bytes) {
    $navskeleton = 
      "<A HREF='index.php?". 
        "todo=openfile" . AMP . 
        "f=" . $_REQUEST['f'] . AMP . 
        "lt=$dirleft" . AMP . 
        "rt=$dirright" . AMP . 
        "start=%d'>%s</A>";

    $nav .= 
      "- " . 
      ($start ? 
        sprintf($navskeleton, $start - $pager_bytes, STR_LESS) : '') 
      . ' ' . 
      ($start + $pager_bytes<filesize($filename) ? 
        sprintf($navskeleton, $start + $pager_bytes, STR_MORE) : '');

  }

  $content = 
    htmlspecialchars(
      wordwrap(
        preg_replace('/[\x00-\x20\x7f-\x9f]/', '.', $content), 
        80, 
        "\n", 
        1));

  echo 
    pageheader(). 
    '<PRE>'.$nav.NL.
    '<HR>'.
    $content.
    '<HR>'.
    $nav.
    '</PRE>' . 
    pagefooter();

}

// ----------------------------------------------------------------------------
function view_php($filename) {
global $dirleft, $dirright, $sortpass, $default;
  
  pageheader();

  $nav = 
    "<A HREF='index.php?".
      "lt=$dirleft" . AMP . 
      "rt=$dirright" . AMP . $sortpass . 
      "'>".STR_BACK."</A> ".
    "<A HREF='index.php?todo=edit". AMP . 
      "lt=$dirleft" . AMP . 
      "rt=$dirright" . AMP . 
      $sortpass . AMP .
      "f=".rawurlencode($filename).
      "'>".STR_EDIT."</A>".
    ' '.$filename.' ';


  $content  = highlight_file($filename, true);
  $charfreq = count_chars($content, 0);
  $content = 
    preg_replace(
      "/((function\s+)(<.*>)?([a-z0-9_]+?))/Ui", 
      "\\2\\3<A NAME='\\4'>\\4</A>",
      $content
    );

  preg_match_all("/<A NAME='([a-z0-9_]+)'>/Ui", $content, $results);

  $bookmarks = Array();
  foreach ($results[1] as $value) 
    $bookmarks[] = "<A CLASS='small' TITLE='function $value' HREF='#$value'>$value</A>";

  $function_list = '';
  if (count($bookmarks)) {
    $i = 1;
    foreach ($bookmarks as $value) {
      $function_list .= 
        '<TD>'.$value.'</TD>';
      if ($i % $default['VIEWER_FUNCTIONS_PER_LINE'] == 0) 
        $function_list .= '</TR><TR>';
      $i++;
    }
    if ($i % $default['VIEWER_FUNCTIONS_PER_LINE'] == 0)
      $function_list .= '</TR><TR>';

    $function_list =
      STR_FUNCTIONLIST.NL.
        '<TABLE CELLSPACING=10 CELLPADDING=0 ALIGN=CENTER><TR>'.$function_list.'</TABLE>'.'<HR>'.NL;
  }

  echo
    pageheader().
    '<PRE>'.
      $nav.NL.
    '<HR>'.
    ($charfreq[13]+1) . ' lines'. NL.
    $function_list . 
    $content.NL.
    '<HR>'.NL.
    $nav.NL.
    '</PRE>'.
    pagefooter();

}

// ----------------------------------------------------------------------------
function view_image($filename) {
global $dirleft, $dirright;

  $content = 
    function_exists('file_get_contents') ? 
      file_get_contents($filename) :
      implode('',file($filename));

  $dimensions = strlen($content) ? getimagesize($filename) : '';

  if (is_array($dimensions)) {
    header("Content-type: " . $dimensions['mime']);
    echo $content;
  }

}

// ----------------------------------------------------------------------------
function view_with_content_type($filename, $content_type) {
global $dirleft, $dirright;

  $content = 
    function_exists('file_get_contents') ? 
      file_get_contents($filename) :
      implode('',file($filename));

  header('Content-Disposition: inline; filename="'.basename($filename).'"');
  header('Content-Type: '   . $content_type . '; name="'.basename($filename).'"');
  header('Content-Length: ' . strlen($content));
  echo $content;

}

?>