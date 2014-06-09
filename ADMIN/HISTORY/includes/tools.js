// ----------------------------------------------------------------------------
function selector(sideflag) {
// file select dialog script

  forminputs    = window.opener.document.getElementsByTagName('INPUT');
  parentform    = window.opener.document.forms.theform;

  // find the method of selection (regexp, extension, extension group)
  selectiontype = '';
  with ( document.forms.selectdialog )
    for ( i = 0; i < i_selecttype.length; i++ )
      if ( i_selecttype[ i ].checked )
        selectiontype = i_selecttype[ i ].value;

  typestoselect = '';

  // by extension group
  if ( selectiontype == 'extgroup' )
    with ( document.forms.selectdialog ) 
      for ( i = 0; i < i_byextgrp.length; i++ )
        if ( i_byextgrp[ i ].selected == true ) 
          typestoselect += ',' + i_byextgrp[ i ].value + ',';

  // by extension
  if ( selectiontype == 'extension' )
    with ( document.forms.selectdialog )
      for ( i = 0; i < i_byext.length; i++ )
        if ( i_byext[ i ].selected == true )
          typestoselect += ',' + i_byext[ i ].value + ',';

  userregexp  = new RegExp( document.forms.selectdialog.i_byregexp.value, "gi" );
  fsmin       = parseInt( document.forms.selectdialog.i_byfilesizemin.value );
  fsmax       = parseInt( document.forms.selectdialog.i_byfilesizemax.value );
  if ( isNaN( fsmin ) ) fsmin = 0; 
  if ( isNaN( fsmax ) ) fsmax = 999999999999;

  // prepare date/time options: parse input fields

  with ( document.forms.selectdialog ) {

    // 'realminimum' and 'realmaximum' are the original UTC timestamps
    // passed by FSGuide panels through $_GET to the dialog function,
    // appearing in the form as hidden values

    dt = i_mindate.value + ' ' + i_mintime.value;

    if ( validDateTime( dt ) ) { 
      dt.match("^([0-9]{4})([-])([0-9]{1,2})([-])([0-9]{1,2}) ([0-9]{1,2}):([0-9]{2}):([0-9]{2})$");
      datemin = new Date( RegExp.$1, RegExp.$3 - 1, RegExp.$5, RegExp.$6, RegExp.$7, RegExp.$8 );
    }
    else {
      if ( !confirm( JS_MINDATE_PARSE_ERROR ) ) 
        return;
      datemin = new Date( document.forms.selectdialog.originaldateminimum.value * 1000 );
    }

    dt = i_maxdate.value + ' ' + i_maxtime.value;

    if ( validDateTime( dt ) ) { 
      dt.match("^([0-9]{4})([-])([0-9]{1,2})([-])([0-9]{1,2}) ([0-9]{1,2}):([0-9]{2}):([0-9]{2})$");
      datemax = new Date( RegExp.$1, RegExp.$3 - 1, RegExp.$5, RegExp.$6, RegExp.$7, RegExp.$8 );
    }
    else {
      if ( !confirm( JS_MAXDATE_PARSE_ERROR ) ) 
        return;
      datemax = new Date( document.forms.selectdialog.originaldatemaximum.value * 1000 );
    }

  }

  for ( j = 0; j < forminputs.length; j++ ) {

    if (
         ( forminputs[ j ].name.substr( 0, 6 ) == ( 'props' + sideflag ) ) &&
         ( parentform[ 'cbx' + forminputs[ j ].name.substr( 5 ) ] != undefined )
       ) {

      // checkaction controls whether to give value to the checkbox of
      // the file examined or not (checkbox value (check/uncheck) is 
      // determined by user)

      checkaction     = false;
      props           = forminputs[ j ].value.split(',');
      props['name']   = props[0];
      props['ext']    = props[1];
      props['size']   = props[2];
      props['rights'] = props[3];
      props['mtime']  = new Date( props[4] * 1000 );

      switch ( selectiontype ) {

        case 'extension':
        case 'extgroup': 
          if (
               ( props[ 'ext' ].length > 0 ) &&
               ( typestoselect.indexOf( ',' + props['ext'] + ',' ) != -1  )
             )
            checkaction = true;
          break;

        case 'regexp':
          if ( ( props[ 'name' ].search( userregexp ) != -1 ) )
            checkaction = true;
          break;

      }

      if ( checkaction == true ) {

        // filesize option check

        checkaction = 
          ( parseInt( props[ 'size' ] ) >= fsmin ) &&
          ( parseInt( props[ 'size' ] ) <= fsmax )
        ;

        // permission options check

        with ( document.forms.selectdialog ) {

          checkaction = checkaction 
            &&
            (
              permissioncheckboxes(
                props['rights'], 'r', i_permry.checked, i_permrn.checked
              )
              ||
              permissioncheckboxes(
                props['rights'], 'w', i_permwy.checked, i_permwn.checked
              )
              ||
              permissioncheckboxes(
                props['rights'], 'x', i_permxy.checked, i_permxn.checked
              )
            )
          ;

        }

        // date/time options check

        checkaction =
          checkaction && 
          ( props['mtime'] >= datemin ) && 
          ( props['mtime'] <= datemax )
        ;

        // finally fill checkboxes with selected value (select/deselect radio)
        // if needed

        if ( checkaction == true ) 
          parentform[ 'cbx' + forminputs[ j ].name.substr( 5 ) ].checked =
            document.forms.selectdialog.i_select[ 0 ].checked == true ;

      }

    }

  }

}

// ----------------------------------------------------------------------------
function permissioncheckboxes( rights, checkright, alloweds, disalloweds) {
// helper function for selector()

  if ( alloweds && disalloweds )
    return true;

  if ( alloweds )
    return rights.search( checkright ) != -1;

  if ( disalloweds )
    return rights.search( checkright ) == -1;

}

// ----------------------------------------------------------------------------
function selecttype(value) {
// checks a radiobutton (identified by value parameter) 
// when a select dialog input control is focused on

  with ( document.forms.selectdialog )

    for ( i = 0; i < i_selecttype.length; i++ ) {
      if ( i_selecttype[ i ].value == value )
        i_selecttype[ i ].checked = true;
      else
        i_selecttype[ i ].checked = false;
    }

}

// ----------------------------------------------------------------------------
function alternate_checkboxes(boxid) {

  form = document.getElementsByTagName('INPUT');
  for (i = 0; i < form.length; i++ ) {
    if ( form[ i ].name.substr( 0,4 ) == ( 'cbx' + boxid ) ) {
      form[ i ].checked = !form[ i ].checked;
    }
  }
  
}

// ----------------------------------------------------------------------------
function fill_checkboxes(boxid, value) {

  form = document.getElementsByTagName('INPUT');
  for ( i = 0; i < form.length; i++ ) {
    if ( form[ i ].name.substr( 0,4 ) == ( 'cbx' + boxid ) ) {
      form[ i ].checked = value;
    }
  }
  
}

// ----------------------------------------------------------------------------
function validDateTime(dt) {
  res = dt.match('^([0-9]{4}-[0-9]{2}-[0-9]{2}) ([0-9]{2}:[0-9]{2})(:[0-9]{2})?$');
  ms  = RegExp.$2 + RegExp.$3;

  return validDate(RegExp.$1, "YYYY-MM-DD") && 
           (validTime(ms, "HH:MM") || validTime(ms, "HH:MM:SS"));
}

// ----------------------------------------------------------------------------
function validDate(d,format) {

//
// this function checks if the date string is valid against the format
// specified
//
// recognized format strings: 
// "YYYY-MM-DD"  "MM-DD-YYYY"  "DD-MM-YYYY"
//
// - day and month might be 1 or 2 chars long
// - the separator must be the - sign
// - function checks the followings also:
//   (1000 <= year <= 9999, 1 <= month <=12, 1 <= days <= days_in_month
//
// - valid examples:	2002-01-2,  2002-1-1, 1951-12-31, 2000-02-29
// - invalid examples:	2002-02-29, 2000-0-1, 200-0-1,	  2000-abc

  daysOfMonth = new Array(31,28,31,30,31,30,31,31,30,31,30,31);

  if (format=='YYYY-MM-DD') {
    res = d.match("^([0-9]{4})([-])([0-9]{1,2})([-])([0-9]{1,2})$");
    year  = RegExp.$1; month = RegExp.$3; days	= RegExp.$5;
    sep1  = RegExp.$2; sep2  = RegExp.$4; 
  }    
  else if (format=='MM-DD-YYYY') {
    res = d.match("^([0-9]{1,2})([-])([0-9]{1,2})([-])([0-9]{4})$");
    year  = RegExp.$5; month = RegExp.$1; days	= RegExp.$3;
    sep1  = RegExp.$2; sep2  = RegExp.$4; 
  }
  else if (format=='DD-MM-YYYY') {
    res = d.match("^([0-9]{1,2})([-])([0-9]{1,2})([-])([0-9]{4})$");
    year  = RegExp.$5; month = RegExp.$3; days	= RegExp.$1;
    sep1  = RegExp.$2; sep2  = RegExp.$4; 
  }
  else return false; // format not supported
  if (!res) { return false; }

  if (sep1 != sep2)				{ return false; } 
  if ((year % 4) == 0)				{ daysOfMonth[1]=29; }
  if ((month <= 0) || (month>12))		{ return false; }
  if ((days<=0) || (days>daysOfMonth[month-1])) { return false; }

  return true;
}

// ----------------------------------------------------------------------------
function validTime(time, format) {

// this function checks the time against the format specified  
// known format string: HH:MM and HH:MM:SS
// HH:MM	-> 0:00    ... 23:59	or 00:00 ... 23:59
// HH:MM:SS	-> 0:00:00 ... 23:59:59 or 00:00 ... 23:59:59
//
// (MM and SS has to be exactly two characters long)

  if (format=='HH:MM') {
    res = time.match("^([0-9]{1,2}):([0-9]{2})$");
    hour = RegExp.$1; min = RegExp.$2; 
  }
  else if (format=='HH:MM:SS') {
    res = time.match("^([0-9]{1,2}):([0-9]{2}):([0-9]{2})$"); 
    hour = RegExp.$1; min = RegExp.$2; sec = RegExp.$3;
    if ((sec<0) || (sec>59)) { return false; }
  }  
  else return false; // format not supported

  if (!res) { return false; }

  if ((hour<0) || (hour>23)) { return false; }
  if ((min<0) || (min>59)) { return false; }

  return true; 
}
