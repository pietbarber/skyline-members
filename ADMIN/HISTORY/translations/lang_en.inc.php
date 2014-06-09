<?php

define('STR_JUMP_TO',            'Jump to:');
define('STR_DOWNLOAD',           'download');

define('STR_LOGIN_INFO',         'To use FSGuide, please enter your login name and password you\'ve received from your system administrator.');
define('STR_LOGIN_ERROR',        'The login name or the password is incorrect');
define('STR_LOGIN_LOGIN',        'your login name');
define('STR_LOGIN_PASSWORD',     'your password');
define('STR_LOGIN_BUTTON',       'login');
define('STR_LOGIN_LOGGEDINAS',   'you are currently logged in as %s.');
define('STR_LOGIN_LOGOUT',       'click here to logout.');
define('STR_LOGIN_DEFAULT_USER', 'you\'re using FSGuide as the default user');
define('STR_LOGIN_INI_MISSINGDIR',   'Directory specification is missing in setting "%s" for user [%s] in user.ini');
define('STR_LOGIN_INI_MISSINGSLASH', 'Trailing slash is missing in setting "%s" for user [%s] in user.ini');

define('STR_ACCESS_DENIED',         'you have no permission to access this directory');
define('STR_ACCESS_COPY_DENIED',    'you have no permission to copy into this directory');
define('STR_ACCESS_DELETE_DENIED',  'you have no permission to delete in this directory');
define('STR_ACCESS_RENAME_DENIED',  'you have no permission to rename in this directory');
define('STR_ACCESS_MOVEFROM_DENIED','you have no permission to move files from this directory');
define('STR_ACCESS_MOVETO_DENIED',  'you have no permission to move files (copy to) this directory');
define('STR_ACCESS_MKDIR_DENIED',   'you have no permission to create directory in this directory');
define('STR_ACCESS_MODIFY_DENIED',  'you have no permission to alter (modify) files in this directory');
define('STR_ACCESS_UPLOAD_DENIED',  'you have no permission to upload files to this directory');
define('STR_ACCESS_FILELIST_DENIED','you have no permission to assemble filelist in this directory');

define('STR_BACK',	'back');
define('STR_LESS',	'less');
define('STR_MORE',	'more');
define('STR_LINES',	'lines');
define('STR_FUNCTIONLIST', 'Function list');
define('STR_EDIT',	'edit');
define('STR_VIEW',	'view');

define('STR_RENAME',	'rename');
define('STR_COPY',	'copy');
define('STR_MOVE',	'move');
define('STR_MKDIRLEFT',	'mkdir &lt;');
define('STR_MKDIRRIGHT','mkdir &gt;');
define('STR_DELETE',	'delete');
define('STR_FILELIST',  'filelist');

define('STR_BOTTOM',	'bottom');
define('STR_TOP',	'top');

define('STR_FILENAME',	   'filename');
define('STR_FILESIZE',	   'size');
define('STR_LASTMODIFIED', 'last modified');
define('STR_SUM', '<B>%s</B> byte(s) in <B>%s</B> item(s)');

// %s will contain the parent directory path
define('STR_CREATEDIRLEGEND', 'create a directory');
define('STR_CREATEDIR',       'name of directory to create:');
define('STR_CREATEDIRBUTTON', 'create directory');

// %s will contain the original name of the file 
define('STR_RENAMELEGEND',       'rename');
define('STR_RENAMEENTERNEWNAME', 'enter new name for %s:');
define('STR_RENAMEBUTTON',       'rename');

define('STR_SYNCLEFTTORIGHT','open left panel\'s directory in the right panel');
define('STR_SYNCRIGHTTOLEFT','open right panel\'s directory in the left panel');

define('STR_ERROR_DIR','could not read directory contents');

define('STR_AUDIO',            'audio');
define('STR_COMPRESSED',       'compressed');
define('STR_EXECUTABLE',       'executable');
define('STR_IMAGE',            'image');
define('STR_SOURCE_CODE',      'source code');
define('STR_TEXT_OR_DOCUMENT', 'text or document');
define('STR_WEB_ENABLED_FILE', 'web-enabled file');
define('STR_VIDEO',            'video');
define('STR_DIRECTORY',        'directory');
define('STR_PARENT_DIRECTORY', 'parent directory');

define('STR_EDITOR_SAVE',      'save file');
define('STR_EDITOR_SAVE_ERROR','the file <I>%s</I> is not writable or does not exist');
define('STR_EDITOR_SAVE_ERROR_WRONG_VALUE','while editing the file <I>%s</I>, you have given the following value at byteposition #%s: %s.');
define('STR_EDITOR_SAVE_ERROR_HEX_VALUE_NEEDED','according to the settings, you have to provide a positive hexadecimal value between 00 and FF.');
define('STR_EDITOR_SAVE_ERROR_DEC_VALUE_NEEDED','according to the settings, you have to provide a whole, positive decimal value between 0 and 255.');

define('STR_FILE_UPLOAD', 'upload');
define('STR_FILE_UPLOAD_DISABLED', 'file upload is disabled in php.ini');
define('STR_FILE_UPLOAD_LEFT', STR_FILE_UPLOAD . ' &lt;');
define('STR_FILE_UPLOAD_RIGHT',STR_FILE_UPLOAD . ' &gt;');
define('STR_FILE_UPLOAD_DESC','Choose files you would like to upload. Choose desired action to accomplish upon succesful upload.');
define('STR_FILE_UPLOAD_FILE','File');
define('STR_FILE_UPLOAD_TARGET','Upload file(s) to');
define('STR_FILE_UPLOAD_ACTION','when upload is complete:');
define('STR_FILE_UPLOAD_NOTHING','do nothing');
define('STR_FILE_UPLOAD_DROPFILE','delete the uploaded file when the selected action is finished');
define('STR_FILE_UPLOAD_MAXFILESIZE','Allowed filesize maximum currently (in php.ini) is');

define('STR_FILE_UPLOAD_ERROR',        'Error: Unable to move file %s to directory %s');
define('STR_FILE_UPLOAD_CHDIR_ERROR',  'Error: Unable to switch (chdir) to %s directory. File being processed: %s');
define('STR_FILE_UPLOAD_UNLINK_ERROR', 'Error: Unable to delete %s after processing.');
define('STR_FILE_UPLOAD_ERROR_FILE_EXCEEDS_INI_SIZE', 'Error: The uploaded file %s exceeds the upload_max_filesize directive in php.ini - %s');
define('STR_FILE_UPLOAD_ERROR_FILE_EXCEEDS_FORM_SIZE','Error: size of uploaded file %s exceeds the HTML FORM settings');
define('STR_FILE_UPLOAD_ERROR_FILE_PARTIAL',          'Error: The uploaded file %s was only partially uploaded');

define('STR_FILELIST_DISPLAY_THESE_FIELDS',	'Display these fields in filelist');
define('STR_FILELIST_PATH',			'path'); 
define('STR_FILELIST_SIZE',			'filesize'); 
define('STR_FILELIST_DATETIME',			'date and time'); 
define('STR_FILELIST_ATTRIBS',			'attributes'); 
define('STR_FILELIST_SELECT_ALL',		'select all'); 

define('STR_SELECTOR_SELECT_ALL',		'select all'); 
define('STR_SELECTOR_SELECT_NONE',		'select none'); 
define('STR_SELECTOR_SELECT_INVERT',		'invert selection'); 
define('STR_SELECTOR_SELECT_DIALOG',		'select dialog'); 

define('STR_SELECTOR_OK', 			'ok');
define('STR_SELECTOR_CLOSEWINDOW', 		'close window');
define('STR_SELECTOR_YES', 			'yes');
define('STR_SELECTOR_NO', 			'no');
define('STR_SELECTOR_SELECT', 			'select');
define('STR_SELECTOR_DESELECT', 		'deselect');
define('STR_SELECTOR_SELECTFILES',		'select files');
define('STR_SELECTOR_OPTIONS',			'options');
define('STR_SELECTOR_BYREGEXP',			'by regexp');
define('STR_SELECTOR_BYEXTENSION',		'by extension');
define('STR_SELECTOR_BYEXTGROUP',		'by extension group');
define('STR_SELECTOR_BYFILESIZE',		'by filesize');   // keep this string short
define('STR_SELECTOR_BYPERMISSION',		'by permission'); // keep this string short
define('STR_SELECTOR_BYDATETIME',		'by date/time');  // keep this string short
define('STR_SELECTOR_READABLE',			'readable');
define('STR_SELECTOR_WRITEABLE',		'writeable');
define('STR_SELECTOR_EXECUTABLE',		'executable');

define('JS_MAXDATE_PARSE_ERROR',		'The maximum date/time is in wrong format (you should keep it in the YYYY-MM-DD HH:MM:SS format). Continue selection by using the maximum available timestamp taken from the file panel?');
define('JS_MINDATE_PARSE_ERROR',		'The minimum date/time is in wrong format (you should keep it in the YYYY-MM-DD HH:MM:SS format). Continue selection by using the maximum available timestamp taken from the file panel?');

?>