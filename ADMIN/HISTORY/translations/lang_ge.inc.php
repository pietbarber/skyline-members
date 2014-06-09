<?php

// FSGuide release: 0.5
//
// Last update: 2004.03.05 (update for version 0.5)
// German translation by Christopher Kramer
// Contact: crazy4chrissi@yahoo.de
// Viel Spaß!

define('STR_JUMP_TO',            'Gehe zu:');
define('STR_DOWNLOAD',           'Download');

define('STR_LOGIN_INFO',         'Um FSGuide zu nutzen geben Sie bitte den Login-Namen und das Passwort ein, das Sie von Ihrem Administrator erhalten haben.');
define('STR_LOGIN_ERROR',        'Der Login-Name oder das Passwort ist falsch.');
define('STR_LOGIN_LOGIN',        'Ihr Login-Name');
define('STR_LOGIN_PASSWORD',     'Ihr Passwort');
define('STR_LOGIN_BUTTON',       'Login');
define('STR_LOGIN_LOGGEDINAS',   'Sie sind momentan als %s angemeldet.');
define('STR_LOGIN_LOGOUT',       'Hier klicken um sich abzumelden.');
define('STR_LOGIN_DEFAULT_USER', 'Sie sind nicht angemeldet');
define('STR_LOGIN_INI_MISSINGDIR',   'Ordner-Einstellungen fehlen in "%s" f&uuml;r User [%s] in der user.ini');
define('STR_LOGIN_INI_MISSINGSLASH', 'Abschliessender Schr&auml;gstrich fehlt in der Einstellung "%s" f&uuml;r User [%s] in der user.ini');

define('STR_ACCESS_DENIED',         'Der Zugriff auf diesen Ordner ist Ihnen nicht gestattet');
define('STR_ACCESS_COPY_DENIED',    'Ihnen fehlt die Berechtigung, in diesem Ordner zu Kopieren');
define('STR_ACCESS_DELETE_DENIED',  'Ihnen fehlt die Berechtigung, in diesem Ordner zu L&ouml;schen');
define('STR_ACCESS_RENAME_DENIED',  'Ihnen fehlt die Berechtigung, in diesem Ordner Dateien umzubenennen');
define('STR_ACCESS_MOVEFROM_DENIED','Ihnen fehlt die Berechtigung, Dateien aus diesem Ordner zu verschieben');
define('STR_ACCESS_MOVETO_DENIED',  'Ihnen fehlt die Berechtigung, Dateien in diesen Ordner zu verschieben');
define('STR_ACCESS_MKDIR_DENIED',   'Ihnen fehlt die Berechtigung, in diesem Ordner neue Ordner zu erstellen');
define('STR_ACCESS_MODIFY_DENIED',  'Ihnen fehlt die Berechtigung, Dateien in diesem Ordner zu ver&auml;ndern.');
define('STR_ACCESS_UPLOAD_DENIED',  'Ihnen fehlt die Berechtigung, dateien in diesen Ordner hochzuladen.');
define('STR_ACCESS_FILELIST_DENIED','Ihnen fehlt die Berechtigung, eine Dateiliste dieses Ordners zusammenzusetzen.');

define('STR_BACK',	'Zur&uuml;ck');
define('STR_LESS',	'Zur&uuml;ck');
define('STR_MORE',	'Weiter');
define('STR_LINES',	'Zeilen');
define('STR_FUNCTIONLIST', 'Function Liste');
define('STR_EDIT',	'&Auml;ndern');
define('STR_VIEW',	'Anzeigen');

define('STR_RENAME',	'Umbenennen');
define('STR_COPY',	'Kopieren');
define('STR_MOVE',	'Verschieben');
define('STR_MKDIRLEFT',	'Ordner erstellen &lt;');
define('STR_MKDIRRIGHT','Ordner erstellen &gt;');
define('STR_DELETE',	'L&ouml;schen');
define('STR_FILELIST',  'Dateiliste');

define('STR_BOTTOM',	'Nach unten');
define('STR_TOP',	'Nach oben');

define('STR_FILENAME',	   'Dateiname');
define('STR_FILESIZE',	   'Gr&ouml;&szlig;e');
define('STR_LASTMODIFIED', 'Letzte &Auml;nderung');
define('STR_SUM', '<B>%s</B> Byte in <B>%s</B> Obejekten');

// %s will contain the parent directory path
define('STR_CREATEDIRLEGEND', 'Einen Ordner erstellen');
define('STR_CREATEDIR',       'Name des zu erstellenden Ordners:');
define('STR_CREATEDIRBUTTON', 'Ordner erstellen');

// %s will contain the original name of the file 
define('STR_RENAMELEGEND',       'Umbenennen');
define('STR_RENAMEENTERNEWNAME', 'Neuer Name f&uuml;r %s:');
define('STR_RENAMEBUTTON',       'Umbenennen');

define('STR_SYNCLEFTTORIGHT','Linken Ordner rechts &ouml;ffnen');
define('STR_SYNCRIGHTTOLEFT','Rechten Ordner links &ouml;ffnen');

define('STR_ERROR_DIR','Inhalt des Verzeichnisses konnte nicht gelesen werden!');

define('STR_AUDIO',            'Audio-Datei');
define('STR_COMPRESSED',       'Komprimierte Datei');
define('STR_EXECUTABLE',       'Anwendung');
define('STR_IMAGE',            'Bild-Datei');
define('STR_SOURCE_CODE',      'Quelltext');
define('STR_TEXT_OR_DOCUMENT', 'Text oder Dokument');
define('STR_WEB_ENABLED_FILE', 'Internet-Dokument');
define('STR_VIDEO',            'Video');
define('STR_DIRECTORY',        'Ordner');
define('STR_PARENT_DIRECTORY', 'parent directory');

define('STR_EDITOR_SAVE',      'Datei speichern');
define('STR_EDITOR_SAVE_ERROR','Die Datei <I>%s</I> ist schreibgesch&uuml;tzt oder fehlt.');
define('STR_EDITOR_SAVE_ERROR_WRONG_VALUE','W&auml;hrend dem &Auml;ndern der Datei <I>%s</I>, haben Sie folgenden Wert f&uuml;r Byteposition #%s angegeben: %s.');
define('STR_EDITOR_SAVE_ERROR_HEX_VALUE_NEEDED','Laut Einstellungen m&uuml;ssen Sie einen postiven Hexadecimal-Wert zwischen 00 und FF angeben.');
define('STR_EDITOR_SAVE_ERROR_DEC_VALUE_NEEDED','Laut Einstellungen m&uuml;ssen Sie einen ganzen, positiven Dezimalwert zwischen 0 und 255 angeben.');

define('STR_FILE_UPLOAD', 'Upload');
define('STR_FILE_UPLOAD_DISABLED', 'Dateiupload deaktiviert (in php.ini)');
define('STR_FILE_UPLOAD_LEFT', STR_FILE_UPLOAD . ' &lt;');
define('STR_FILE_UPLOAD_RIGHT',STR_FILE_UPLOAD . ' &gt;');
define('STR_FILE_UPLOAD_DESC','W&auml;hlen Sie die Dateien, die Sie hochladen m&ouml;chten, und evtl. eine Aktion die nach dem Upload erfolgen soll.');
define('STR_FILE_UPLOAD_FILE','Datei');
define('STR_FILE_UPLOAD_TARGET','Datei(en) an folgende Stelle hochladen');
define('STR_FILE_UPLOAD_ACTION','Nach Upload:');
define('STR_FILE_UPLOAD_NOTHING','nichts tun');
define('STR_FILE_UPLOAD_DROPFILE','Hochgeladene Datei nach gew&auml;hlter Aktion l&ouml;schen');
define('STR_FILE_UPLOAD_MAXFILESIZE','Maximale Dateigr&ouml;&szlig;e (laut php.ini)');

define('STR_FILE_UPLOAD_ERROR',        'Fehler: Datei %s kann nicht in Ordner %s verschoben werden');
define('STR_FILE_UPLOAD_CHDIR_ERROR',  'Fehler: Zu Ordner %s kann nicht gewechselt werden. Bearbeitete Datei: %s');
define('STR_FILE_UPLOAD_UNLINK_ERROR', 'Fehler: Datei %s konnte nach der Verarbeitung nicht gel&ouml;scht werden');
define('STR_FILE_UPLOAD_ERROR_FILE_EXCEEDS_INI_SIZE', 'Fehler: Die hochzuladende Datei %s &uuml;berschritt die maximale Dateigr&ouml;ße f&uuml;r Uploads die in der php.ini angegeben ist - %s');
define('STR_FILE_UPLOAD_ERROR_FILE_EXCEEDS_FORM_SIZE','Fehler: Gr&ouml;&szlig;e der hochzuladenden Date %s &uuml;bertrifft die HTML FORM-Einstellungen');
define('STR_FILE_UPLOAD_ERROR_FILE_PARTIAL',          'Fehler: Die hochzuladende Datei %s wurde nur teilweise hochgeladen');

define('STR_FILELIST_DISPLAY_THESE_FIELDS',	'In der Dateiliste aufnehmen');
define('STR_FILELIST_PATH',			'Pfad');
define('STR_FILELIST_SIZE',			'Gr&ouml;&szlig;e');
define('STR_FILELIST_DATETIME',			'Datum / Uhrzeit');
define('STR_FILELIST_ATTRIBS',			'Attribute');
define('STR_FILELIST_SELECT_ALL',		'Markieren');

define('STR_SELECTOR_SELECT_ALL',		'Alle ausw&auml;hlen');
define('STR_SELECTOR_SELECT_NONE',		'Nichts ausw&auml;hlen');
define('STR_SELECTOR_SELECT_INVERT',		'Auswahl umkehren');
define('STR_SELECTOR_SELECT_DIALOG',		'Dialog ausw&auml;hlen');

define('STR_SELECTOR_OK', 			'Ok');
define('STR_SELECTOR_CLOSEWINDOW', 		'Fenster schlie&szlig;en');
define('STR_SELECTOR_YES', 			'Ja');
define('STR_SELECTOR_NO', 			'Nein');
define('STR_SELECTOR_SELECT', 			'Ausw&auml;hlen');
define('STR_SELECTOR_DESELECT', 		'Nicht ausw&auml;hlen');
define('STR_SELECTOR_SELECTFILES',		'Dateien ausw&auml;hlen');
define('STR_SELECTOR_OPTIONS',			'Optionen');
define('STR_SELECTOR_BYREGEXP',			'Nach regexp');
define('STR_SELECTOR_BYEXTENSION',		'Nach Dateiendung');
define('STR_SELECTOR_BYEXTGROUP',		'Nach Endungs-Gruppe');
define('STR_SELECTOR_BYFILESIZE',		'Nach Dateigr&ouml;&szlig;e');   // keep this string short
define('STR_SELECTOR_BYPERMISSION',		'Nach Zugriff'); // keep this string short
define('STR_SELECTOR_BYDATETIME',		'Nach Datum/Uhrzeit');  // keep this string short
define('STR_SELECTOR_READABLE',			'Lesbar');
define('STR_SELECTOR_WRITEABLE',		'Schreibbar');
define('STR_SELECTOR_EXECUTABLE',		'Ausf&uuml;hrbar');

define('JS_MAXDATE_PARSE_ERROR',		'Das maximale Datum / die maximale Zeit ist im falschen Format angegeben worden (verwenden Sie folgendes Format: YYYY-MM-DD HH:MM:SS). Mit Benutzung der maximalen Zeit aus dem Datei-Panel weiter machen?');
define('JS_MINDATE_PARSE_ERROR',		'Das minimale Datum / die minimale Zeit ist im falschen Format angegeben worden (verwenden Sie folgendes Format: YYYY-MM-DD HH:MM:SS). Mit Benutzung der maximalen Zeit aus dem Datei-Panel weiter machen?');

?>
