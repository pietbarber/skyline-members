<?php

define('STR_JUMP_TO',          'ugrás:');
define('STR_DOWNLOAD',         'letöltés');

define('STR_LOGIN_INFO',         'Az FSGuide használatához adja meg az adminisztrátortól kapott bejelentkezési nevét és jelszavát.');
define('STR_LOGIN_ERROR',        'A login név vagy a jelszó helytelen');
define('STR_LOGIN_LOGIN',        'login név');
define('STR_LOGIN_PASSWORD',     'jelszó');
define('STR_LOGIN_BUTTON',       'belépés');
define('STR_LOGIN_LOGGEDINAS',   '%s felhasználóként lépett be.');
define('STR_LOGIN_LOGOUT',       'kattintson ide a kilépéshez.');
define('STR_LOGIN_DEFAULT_USER', 'Alapértelmezett felhasználóként használja az FSGuide-ot');
define('STR_LOGIN_INI_MISSINGDIR',   'Az alkönyvtár neve hiányzik a "%s" beállításból a [%s] felhasználó számára a user.ini állományban');
define('STR_LOGIN_INI_MISSINGSLASH', 'Hiányzik a befejezõ / jel a user.ini-bõl a "%s" beállításból a [%s] felhasználóhoz');

define('STR_ACCESS_DENIED',         'Ön nem jogosult hozzáférni ehhez az alkönyvtárhoz');
define('STR_ACCESS_COPY_DENIED',    'Ön nem jogosult másolni ebbe az alkönyvtárba');
define('STR_ACCESS_DELETE_DENIED',  'Ön nem jogosult törölni ebbõl az alkönyvtárból');
define('STR_ACCESS_RENAME_DENIED',  'Ön nem jogosult átnevezni ebben az az alkönyvtárban');
define('STR_ACCESS_MOVEFROM_DENIED','Ön nem jogosult állományokat elmozgatni ebbõl az alkönyvtárból');
define('STR_ACCESS_MOVETO_DENIED',  'Ön nem jogosult állományokat mozgatni (másolni) ebbe az alkönyvtárba');
define('STR_ACCESS_MKDIR_DENIED',   'Ön nem jogosult alkönyvtárat létrehozni ebben az alkönyvtárban');
define('STR_ACCESS_MODIFY_DENIED',  'Ön nem jogosult állományokat módosítani ebben az alkönyvtárban');
define('STR_ACCESS_UPLOAD_DENIED',  'Ön nem jogosult állományokat feltölteni ebbe az alkönyvtárba');
define('STR_ACCESS_FILELIST_DENIED','Ön nem jogosult állományokról listát összeállítani ebben az alkönyvtárban');

define('STR_BACK',	'vissza');
define('STR_LESS',	'visszalapozás');
define('STR_MORE',	'továbblapozás');
define('STR_LINES',	'sor');
define('STR_FUNCTIONLIST', 'Függvénylista');
define('STR_EDIT',	'szerkesztés');
define('STR_VIEW',	'megnéz');

define('STR_RENAME',	'átnevezés');
define('STR_COPY',	'másolás');
define('STR_MOVE',	'mozgatás');
define('STR_MKDIRLEFT',	'új alkönyvtár &lt;');
define('STR_MKDIRRIGHT','új alkönyvtár &gt;');
define('STR_DELETE',	'törlés');
define('STR_FILELIST', 'lista');

define('STR_BOTTOM',	'legalulra');
define('STR_TOP',	'legfelülre');

define('STR_FILENAME',	   'filenév');
define('STR_FILESIZE',	   'méret');
define('STR_LASTMODIFIED', 'utolsó módosítása');
define('STR_SUM', '<B>%s</B> byte <B>%s</B> bejegyzésben');

// %s will contain the parent directory path
define('STR_CREATEDIRLEGEND', 'alkönyvtár létrehozása');
define('STR_CREATEDIR',       'az új alkönyvtár neve:');
define('STR_CREATEDIRBUTTON', 'létrehozás');

// %s will contain the original name of the file
define('STR_RENAMELEGEND',       'átnevezés');
define('STR_RENAMEENTERNEWNAME', 'új név %s számára:');
define('STR_RENAMEBUTTON',       'átnevezés');

define('STR_SYNCLEFTTORIGHT','a bal panel alkönyvtárának megnyitása a jobb panelben');
define('STR_SYNCRIGHTTOLEFT','a jobb panel alkönyvtárának megnyitása a bal panelben');

define('STR_ERROR_DIR','az alkönyvtár nem elérhetõ');

define('STR_AUDIO',            'audio');
define('STR_COMPRESSED',       'tömörített');
define('STR_EXECUTABLE',       'futtatható');
define('STR_IMAGE',            'kép');
define('STR_SOURCE_CODE',      'forráskód');
define('STR_TEXT_OR_DOCUMENT', 'szöveg vagy dokumentum');
define('STR_WEB_ENABLED_FILE', 'weben használatos file');
define('STR_VIDEO',            'video');
define('STR_DIRECTORY',        'alkönyvtár');
define('STR_PARENT_DIRECTORY', 'szülõkönyvtár');

define('STR_EDITOR_SAVE',      'file mentése');
define('STR_EDITOR_SAVE_ERROR','a(z) <I>%s</I> nevû file nem írható vagy nem létezik');
define('STR_EDITOR_SAVE_ERROR_WRONG_VALUE','a <I>%s</I> nevû file szerkesztése közben a %s pozíción a következõ érvénytelen értéket adta meg: %s.');
define('STR_EDITOR_SAVE_ERROR_HEX_VALUE_NEEDED','a beállítások alapján hexadecimális (16-os számrendszerbeli) értékre van szükség az adott pozíción, mely minimum 00, maximum FF között lehet.');
define('STR_EDITOR_SAVE_ERROR_DEC_VALUE_NEEDED','a beállítások alapján decimális (10-es számrendszerbeli) értékre van szükség az adott pozíción, mely minimum 0, maximum 255 lehet.');

define('STR_FILE_UPLOAD', 'feltöltés');
define('STR_FILE_UPLOAD_DISABLED', 'az állományok feltöltését a php.ini segítségével letiltották.');
define('STR_FILE_UPLOAD_LEFT', STR_FILE_UPLOAD . ' &lt;');
define('STR_FILE_UPLOAD_RIGHT',STR_FILE_UPLOAD . ' &gt;');
define('STR_FILE_UPLOAD_DESC','Válassza ki a feltöteni kívánt állományokat, valamint amennyiben szükséges, a sikeres feltöltést követõen végrehajtani kívánt mûveletet.');
define('STR_FILE_UPLOAD_FILE','Állomány');
define('STR_FILE_UPLOAD_TARGET','Állományok feltöltésének helye:');
define('STR_FILE_UPLOAD_ACTION','Ha a feltöltés megtörtént:');
define('STR_FILE_UPLOAD_NOTHING','ne csináljon semmit');
define('STR_FILE_UPLOAD_DROPFILE','törölje a feltöltött állományt, ha a mûvelet végrehajtása megtörtént');
define('STR_FILE_UPLOAD_MAXFILESIZE','A (php.ini-ben) megengedett maximális feltölthetõ állományméret');

define('STR_FILE_UPLOAD_ERROR',        'Hiba történt a(z) %s állomány %s könyvtárba mozgatása során.');
define('STR_FILE_UPLOAD_CHDIR_ERROR',  'Hiba történt a(z) %s alkönyvtárba lépés (chdir) során a(z) %s állomány feldolgozása során.');
define('STR_FILE_UPLOAD_UNLINK_ERROR', 'Hiba történt a(z) %s állomány törlése során.');
define('STR_FILE_UPLOAD_ERROR_FILE_EXCEEDS_INI_SIZE', 'Hiba: a(z) %s állomány mérete meghaladja az upload_max_filesize php.ini beállítást, amely %s maximális méretet ír elõ.');
define('STR_FILE_UPLOAD_ERROR_FILE_EXCEEDS_FORM_SIZE','Hiba: a feltöltött állomány (%s) mérete meghaladja a HTML FORM beállításokat.');
define('STR_FILE_UPLOAD_ERROR_FILE_PARTIAL',          'Hiba: a feltöltött állomány (%s) csak részben került feltöltésre.');

define('STR_FILELIST_DISPLAY_THESE_FIELDS',	'A következõ mezõket tartalmazza az állománylista');
define('STR_FILELIST_PATH',			'elérési út'); 
define('STR_FILELIST_SIZE',			'állomány mérete'); 
define('STR_FILELIST_DATETIME',			'dátum és idõ'); 
define('STR_FILELIST_ATTRIBS',			'attribútumok'); 
define('STR_FILELIST_SELECT_ALL',		'mindent kijelöl'); 

define('STR_SELECTOR_SELECT_ALL',		'mindent kijelöl');
define('STR_SELECTOR_SELECT_NONE',		'mindent kijelöletlenre vált');
define('STR_SELECTOR_SELECT_INVERT',		'kijelöléseket invertál');
define('STR_SELECTOR_SELECT_DIALOG',		'kijelölés párbeszédablak'); 

define('STR_SELECTOR_OK', 			'ok');
define('STR_SELECTOR_CLOSEWINDOW', 		'ablak bezárása');
define('STR_SELECTOR_YES', 			'igen');
define('STR_SELECTOR_NO', 			'nem');
define('STR_SELECTOR_SELECT', 			'kiválasztás');
define('STR_SELECTOR_DESELECT', 		'választás törlése');
define('STR_SELECTOR_SELECTFILES',		'állományok kiválasztása');
define('STR_SELECTOR_OPTIONS',			'opciók');
define('STR_SELECTOR_BYREGEXP',			'reguláris kifejezéssel');
define('STR_SELECTOR_BYEXTENSION',		'kiterjesztés alapján');
define('STR_SELECTOR_BYEXTGROUP',		'kiterjesztéscsoport alapján');
define('STR_SELECTOR_BYFILESIZE',		'fileméret');
define('STR_SELECTOR_BYPERMISSION',		'engedélyek');
define('STR_SELECTOR_BYDATETIME',		'dátum/idõ');
define('STR_SELECTOR_READABLE',			'olvasható');
define('STR_SELECTOR_WRITEABLE',		'írható');
define('STR_SELECTOR_EXECUTABLE',		'futtatható');

define('JS_MAXDATE_PARSE_ERROR',		'A maximum dátum/idõ nem értelmezhetõ (ÉÉÉÉ-HH-NN ÓÓ:PP:MM formátum betartása kötelezõ). Folytassuk a kijelölést az állománypanelrõl vett legnagyobb idõponttal?');
define('JS_MINDATE_PARSE_ERROR',		'A minimum dátum/idõ nem értelmezhetõ (ÉÉÉÉ-HH-NN ÓÓ:PP:MM formátum betartása kötelezõ). Folytassuk a kijelölést az állománypanelrõl vett legkisebb idõponttal?');

?>