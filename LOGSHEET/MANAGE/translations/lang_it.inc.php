<?php

// FSGuide release: 0.7
//
// Last update: 2005.04.02
// Italian translation by Marco Ponti
// Contact: marco@aspbridges.net 

define('STR_RENAME_REMOVE_CHARS',     'Rimuovi questi caratteri dai nomi dei files:');
define('STR_RENAME_REMOVE_BUTTON',    'Rimuovi');

define('STR_RENAME_REMOVENUMBER', 'Rimuovi' );
define('STR_RENAME_REMOVENUMBER_FROM', 'caratteri' );
define('STR_RENAME_FROM_BEGINNING', 'dall\'inizio' );
define('STR_RENAME_FROM_END', 'dalla fine' );
define('STR_RENAME_FROM_POSITION', 'dalla posizione' ); 

define('STR_RENAME_ADD', 'Aggiungi questa stringa' ); 
define('STR_RENAME_TO', 'dalla ' ); 
define('STR_RENAME_TO_BEGINNING', 'inizio' );
define('STR_RENAME_TO_END', 'fine' );
define('STR_RENAME_TO_POSITION', 'posizione' ); 
define('STR_RENAME_ADD_BUTTON', 'Aggiungi' ); 

define('STR_RENAME_REGEXP', 'Sostituisci la "Regular expression"' ); 
define('STR_RENAME_REPLACE_GLOBAL', 'globale' ); 
define('STR_RENAME_REPLACE_IGNORE_CASE', 'ignora MAI/min' ); 
define('STR_RENAME_REGEXP_TO', 'con:' ); 
define('STR_RENAME_REPLACE', 'Sostituisci' ); 

define('STR_RENAME_CASE_CONVERSION','Converti');
define('STR_RENAME_CCLOWER','in minuscolo');
define('STR_RENAME_CCUPPER','in maiuscolo');
define('STR_RENAME_CONVERT','Converti');

define('STR_RENAME_RESET', 'Azzera form' );

define('STR_SORT_UP', 'ordina per %s, crescente');
define('STR_SORT_DN', 'ordina per %s, decrescente');
define('STR_PANEL_CREATED', 'creato' );
define('STR_PANEL_LASTACCESS', 'ultimo accesso' );

define('STR_JUMP_TO',             'Vai a:');
define('STR_DOWNLOAD',            'download');

define('STR_DO_YOU_WANT_TO_DELETE', 'Vuoi veramente cancellare gli elementi selezionati ?');

define('STR_COMPARE',             'confronta');
define('STR_COMPARE_OK',          'ok');
define('STR_COMPARE_CLOSEWINDOW', 'chiudi finestra');
define('STR_COMPARE_OPTIONS',     'opzioni');
define('STR_COMPARE_SELECT_DIFFERENT',   'seleziona files differenti');
define('STR_COMPARE_DESELECT_DIFFERENT', 'deseleziona files differenti');
define('STR_COMPARE_ONLY_FILES_IN_BOTH_PANEL', 'confronta solo i files che esistono in entrambi i pannelli');
define('STR_COMPARE_BY_SIZE', 'confronta dimensione');
define('STR_COMPARE_BY_TIME', 'confronta ora di modifica');

define('STR_LOGIN_INFO',         'Per usare FSGuide, digitare nome e password ricevute dal vostro system administrator.');
define('STR_LOGIN_ERROR',        'Il nome o la password sono errate');
define('STR_LOGIN_LOGIN',        'Nome');
define('STR_LOGIN_PASSWORD',     'Password');
define('STR_LOGIN_BUTTON',       'Login');
define('STR_LOGIN_LOGGEDINAS',   'attualmente sei logato come %s.');
define('STR_LOGIN_LOGOUT',       'clicca qui per uscire.');
define('STR_LOGIN_DEFAULT_USER', 'stai usando FSGuide come utente generico');
define('STR_LOGIN_INI_MISSINGDIR',   'La specifica delle cartelle manca nel settaggio "%s" per l\'utente [%s] nel file user.ini');
define('STR_LOGIN_INI_MISSINGSLASH', 'Manca la "Trailing slash" nel settaggio "%s" per l\'utente [%s] nel file user.ini');

define('STR_ACCESS_DENIED',         'non ti è permesso accedere a questa directory');
define('STR_ACCESS_COPY_DENIED',    'non ti è permesso copiare in questa directory');
define('STR_ACCESS_DELETE_DENIED',  'non ti è permesso cancellare in questa directory');
define('STR_ACCESS_RENAME_DENIED',  'non ti è permesso rinominare in questa directory');
define('STR_ACCESS_MOVEFROM_DENIED','non ti è permesso spostare file da questa directory');
define('STR_ACCESS_MOVETO_DENIED',  'non ti è permesso spostare files (copiare) in questa directory');
define('STR_ACCESS_MKDIR_DENIED',   'non ti è permesso creare directory in questa directory');
define('STR_ACCESS_MODIFY_DENIED',  'non ti è permesso to modificare files in questa directory');
define('STR_ACCESS_UPLOAD_DENIED',  'non ti è permesso inviare files in questa directory');
define('STR_ACCESS_FILELIST_DENIED','non ti è permesso generare filelist in questa directory');

define('STR_BACK',	'indietro');
define('STR_LESS',	'meno');
define('STR_MORE',	'più');
define('STR_LINES',	'righe');
define('STR_FUNCTIONLIST', 'Lista Funzioni');
define('STR_EDIT',	'modifica');
define('STR_VIEW',	'visualizza');

define('STR_RENAME',	'rinomina');
define('STR_COPY',	'copia');
define('STR_MOVE',	'sposta');
define('STR_MKDIRLEFT',	'mkdir &lt;');
define('STR_MKDIRRIGHT','mkdir &gt;');
define('STR_DELETE',	'cancella');
define('STR_FILELIST',  'filelist');

define('STR_BOTTOM',	'fine pagina');
define('STR_TOP',	'inizio pagina');

define('STR_FILENAME',	   'nome');
define('STR_FILESIZE',	   'dimensione');
define('STR_LASTMODIFIED', 'ultima modifica');
define('STR_SUM', '<B>%s</B> byte(s) in <B>%s</B> elemento(i)');

// %s will contain the parent directory path
define('STR_CREATEDIRLEGEND', 'crea una directory');
define('STR_CREATEDIR',       'nome della directory da creare:');
define('STR_CREATEDIRBUTTON', 'crea directory');

// %s will contain the original name of the file 
define('STR_RENAMELEGEND',       'rinomina');
define('STR_RENAMEENTERNEWNAME', 'inserisci il nuovo nome per %s:');
define('STR_RENAMEBUTTON',       'rinomina');

define('STR_SYNCLEFTTORIGHT','apri la directory del pannello sinistro nel pannello destro');
define('STR_SYNCRIGHTTOLEFT','apri la directory del pannello destro nel pannello sinistro');

define('STR_ERROR_DIR','non posso leggere il contenuto della directory');

define('STR_AUDIO',            'audio');
define('STR_COMPRESSED',       'compressi');
define('STR_EXECUTABLE',       'eseguibili');
define('STR_IMAGE',            'immagini');
define('STR_SOURCE_CODE',      'codice sorgente');
define('STR_TEXT_OR_DOCUMENT', 'documenti o testi');
define('STR_WEB_ENABLED_FILE', 'web-enabled file');
define('STR_VIDEO',            'video');
define('STR_DIRECTORY',        'directory');
define('STR_PARENT_DIRECTORY', 'directory superiore');

define('STR_EDITOR_SAVE',      'salva file');
define('STR_EDITOR_SAVE_ERROR','il file <I>%s</I> è protetto in scrittura o non esiste');
define('STR_EDITOR_SAVE_ERROR_WRONG_VALUE','mentre editavi il file <I>%s</I>, hai dato il seguente valore al byte #%s: %s.');
define('STR_EDITOR_SAVE_ERROR_HEX_VALUE_NEEDED','in accordo con il settaggio, devi fornire un valore esadecimale positivo compreso fra 00 e FF.');
define('STR_EDITOR_SAVE_ERROR_DEC_VALUE_NEEDED','in accordo con il settaggio, devi fornire un valore decimale positivo compreso fra 0 e 255.');

define('STR_FILE_UPLOAD', 'upload');
define('STR_FILE_UPLOAD_DISABLED', 'l\'invio di file è disabilitato in php.ini');
define('STR_FILE_UPLOAD_LEFT', STR_FILE_UPLOAD . ' &lt;');
define('STR_FILE_UPLOAD_RIGHT',STR_FILE_UPLOAD . ' &gt;');
define('STR_FILE_UPLOAD_DESC','Scegli i file che desideri inviare. Scegli l\'azione desiderata da eseguire una volta terminato l\'invio.');
define('STR_FILE_UPLOAD_FILE','File');
define('STR_FILE_UPLOAD_TARGET','Invia file(s) a');
define('STR_FILE_UPLOAD_ACTION','quando l\'invio è completo:');
define('STR_FILE_UPLOAD_NOTHING','non fare nulla');
define('STR_FILE_UPLOAD_DROPFILE','cancella il file inviato quando l\'azione selezionata è completata');
define('STR_FILE_UPLOAD_MAXFILESIZE','La massima dimenzione ammessa attualmentec (in php.ini) è');

define('STR_FILE_UPLOAD_ERROR',        'Errore: Impossibile spostare file %s nella directory %s');
define('STR_FILE_UPLOAD_CHDIR_ERROR',  'Errore: Impossibile passare alla directory %s . File elaborati: %s');
define('STR_FILE_UPLOAD_UNLINK_ERROR', 'Errore: Impossibile cancella %s dopo elaborazione.');
define('STR_FILE_UPLOAD_ERROR_FILE_EXCEEDS_INI_SIZE', 'Errore: Il file inviato(%s) supera la direttiva upload_max_filesize in php.ini - %s');
define('STR_FILE_UPLOAD_ERROR_FILE_EXCEEDS_FORM_SIZE','Errore: La dimensione del file inviato (%s) supera il settaggio della FORM HTML');
define('STR_FILE_UPLOAD_ERROR_FILE_PARTIAL',          'Errore: Il file %s è stato inviato solo parzialmente');

define('STR_FILELIST_DISPLAY_THESE_FIELDS',	'Visualizza questi campi nella filelist');
define('STR_FILELIST_PATH',			'percorso'); 
define('STR_FILELIST_SIZE',			'dimensione'); 
define('STR_FILELIST_DATETIME',			'data e ora'); 
define('STR_FILELIST_ATTRIBS',			'attributi'); 
define('STR_FILELIST_SELECT_ALL',		'seleziona tutti'); 

define('STR_SELECTOR_SELECT_ALL',		'seleziona tutti'); 
define('STR_SELECTOR_SELECT_NONE',		'seleziona nessuno'); 
define('STR_SELECTOR_SELECT_INVERT',		'inverti selezione'); 
define('STR_SELECTOR_SELECT_DIALOG',		'finestra di selezione'); 

define('STR_SELECTOR_OK', 			'ok');
define('STR_SELECTOR_CLOSEWINDOW', 		'chiudi finestra');
define('STR_SELECTOR_YES', 			'si');
define('STR_SELECTOR_NO', 			'no');
define('STR_SELECTOR_SELECT', 			'seleziona');
define('STR_SELECTOR_DESELECT', 		'deseleziona');
define('STR_SELECTOR_SELECTFILES',		'seleziona files');
define('STR_SELECTOR_OPTIONS',			'opzioni');
define('STR_SELECTOR_BYREGEXP',			'per regexp');
define('STR_SELECTOR_BYEXTENSION',		'per estensione');
define('STR_SELECTOR_BYEXTGROUP',		'per gruppo di estensione');
define('STR_SELECTOR_BYFILESIZE',		'per dimensione');   // keep this string short
define('STR_SELECTOR_BYPERMISSION',		'per permessi'); // keep this string short
define('STR_SELECTOR_BYDATETIME',		'per data/ora');  // keep this string short
define('STR_SELECTOR_READABLE',			'lettura');
define('STR_SELECTOR_WRITEABLE',		'scrittura');
define('STR_SELECTOR_EXECUTABLE',		'eseguibile');

define('JS_MAXDATE_PARSE_ERROR',		'Il formato della data/ora massima è sbagliato (dovresti metterlo nel formato YYYY-MM-DD HH:MM:SS format). Continuo la selezione usando il massimo valore disponibile nel pannello dei file?');
define('JS_MINDATE_PARSE_ERROR',		'Il formato della data/ora minima è sbagliato (dovresti metterlo nel formato YYYY-MM-DD HH:MM:SS format). Continuo la selezione usando il minimo valore disponibile nel pannello dei file?');

?>