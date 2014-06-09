<?php

include('user.common.php');
if ( 
     ( 
       $user_auth_file 
         =
       @parse_ini_file( $GLOBALS['default']['USER_CONFIGFILE'], true )
     ) 
       === 
     false
   )
  die(
    'FSGuide error: could not open user.ini file: ' . 
    $GLOBALS['default']['USER_CONFIGFILE'] .
    '. Install and configure FSGuide properly.'
  );

// ----------------------------------------------------------------------------
function loadusersettings( $user ) {
global $default, $user_auth_file;

  foreach ( $user_auth_file[ $user ] as $key => $value ) {
    $default[ strtoupper( $key ) ] = $value;
  }

}

// ----------------------------------------------------------------------------
function checkpassword( $user, $password ) {
  return 
    isset( $GLOBALS['user_auth_file'][ $user ] ) && 
    isset( $GLOBALS['user_auth_file'][ $user ]['password'] ) && 
    ( $GLOBALS['user_auth_file'][ $user ]['password'] == $password );

}

// ----------------------------------------------------------------------------
function userhasrights( $user, $dir, $right ) {
global $user_auth_file, $user_rights_implemented; 

  $acl = Array();
  foreach ( $user_auth_file[ $user ] as $key => $value ) {
  
    if ( substr( $key, 0, 3 ) == 'dir' ) {

      $parts   = explode(USERINI_EXPLODECHAR, $value );
      $aclrule = Array();

      if ( strlen( $parts[ 0 ] ) == 0 ) 
        die( 
          pageheader() .
          sprintf( STR_LOGIN_INI_MISSINGDIR, $key, $user ) .
          pagefooter()
        );

      if ( substr( $parts[ 0 ], strlen( $parts[ 0 ] ) - 1, 1 ) != '/' ) 
        die( 
          pageheader() .
          sprintf( STR_LOGIN_INI_MISSINGSLASH, $key, $user ) .
          pagefooter()
        );
        
      $aclrule['target'] = $parts[ 0 ] ;
      $aclrule['rights'] = Array();

      // if only a dirname is specified, or there's a +ALL
      // specified, start with all the rights enabled
      if ( 
           ( count( $parts ) == 1 ) ||
           in_array( '+ALL', $parts )
         ) {
        foreach ( $user_rights_implemented as $thisright )
          $aclrule['rights'][ $thisright ] = '+';
      }

      if ( 
           ( count( $parts ) == 1 ) ||
           in_array( '-ALL', $parts )
         ) {
        foreach ( $user_rights_implemented as $thisright )
          $aclrule['rights'][ $thisright ] = '-';
      }

      foreach ( $parts as $thisright ) {
        switch ( substr( $thisright, 0, 1 ) ) {
          case '-':
          case '+':
            $righttype = substr( $thisright, 0, 1 );
            $rightname = substr( $thisright, 1 );
            if ( in_array( $rightname, $user_rights_implemented ) )
              $aclrule['rights'][ $rightname ] = $righttype;
            break;
        }

      }

      $acl[] = $aclrule;

    }
  }

  $aclapplied           = Array();
  $aclapplied['target'] = '';
  $aclapplied['rights'] = Array();

  foreach ( $acl as $aclrule ) {
    
    // if the acl rule target being processed fits the directory in 
    // question and if it's closer to the dir in question than
    // than the target of $aclapplied
    if ( 
         ( substr( $dir, 0, strlen( $aclrule['target'] ) ) == 
           $aclrule['target'] ) 
         &&
         (
           strlen( $aclapplied['target'] ) 
             < 
           strlen( $aclrule['target'] )
         )
       ) {
      $aclapplied['target'] = $aclrule['target'];
      $aclapplied['rights'] = 
        array_merge( $aclapplied['rights'], $aclrule['rights'] );
    }
  }

//  echo "<PRE>" . $dir  .' ' .$right . ' ' ;
//  print_r($aclapplied);
//  echo "</PRE>";

  return
    isset( $aclapplied['rights'][ $right ] ) && 
    $aclapplied['rights'][ $right ] == '+';

}

?>