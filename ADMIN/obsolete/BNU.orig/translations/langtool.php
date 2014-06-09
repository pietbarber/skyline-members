<?php

// you have to change the language infix of the language file
// you want to compare to the reference language file (English)

$compare_language = 'fr';

// that's all, now open this script in your browser.

// ----------------------------------------------------------------------------

$reference    = getDefinesFrom( 'lang_en.inc.php' );
$compare_with = getDefinesFrom( 'lang_' . $compare_language . '.inc.php');
$compare_with = array_flip( $compare_with );

echo 
  "<HTML>". "\n" .
  "<HEAD>". "\n" .
  "<STYLE TYPE='text/css'>body { font-family: Arial; }</STYLE>". "\n" .
  "</HEAD>". "\n" .
  "<BODY>". "\n" .
  "<H1>Language tool for FSGuide</H1>". "\n" .
  "The following strings are missing from " . 
  "lang_" . $compare_language . ".inc.php:". "\n" .
  "<UL>\n";

$counter = 0;

foreach ( $reference as $word ) {
  if ( !isset( $compare_with[ $word ] ) ) {
    echo "<LI>" . $word . "\n";
    $counter++;
  }
}

echo 
  "</UL>\n" . 
  $counter . " string[s] missing altogether (compared to the English language file).". "\n" .
  "</BODY>". "\n" .
  "</HTML>";

// ----------------------------------------------------------------------------
function getDefinesFrom( $languagefile ) {

  $sourcearray = @file( $languagefile ) or die('<HTML><BODY>Can\'t open language file: ' . $languagefile . "</BODY></HTML>");
  $source = implode('', $sourcearray);
  $tokens = token_get_all( $source );
  $words  = Array();

  foreach ($tokens as $token) { 
    if (!is_string($token)) { 

      list($id, $text) = $token; 
      switch($id) { 
        case T_CONSTANT_ENCAPSED_STRING:
          if ( substr( $text, 0, 5 ) == "'STR_" )
            $words[] = $text;
          break;
        default: break; 
      } 
    } 
  } 

  return $words;

}
?>