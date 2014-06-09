<?php

// FSGuide release: 0.7
//
// Last update: 2005.04.05
// French translation by Ben Bois
// Contact: ben@hooboo.com

define('STR_RENAME_REMOVE_CHARS',     'Supprimer les caractères de ces fichiers :');
define('STR_RENAME_REMOVE_BUTTON',    'Supprimer');

define('STR_RENAME_REMOVENUMBER', 'Supprimer' );
define('STR_RENAME_REMOVENUMBER_FROM', 'charactères' );
define('STR_RENAME_FROM_BEGINNING', 'à partir du début' );
define('STR_RENAME_FROM_END', 'à partir de la fin' );
define('STR_RENAME_FROM_POSITION', 'à partir de cette position' ); 

define('STR_RENAME_ADD', 'Ajouter ces caractères' ); 
define('STR_RENAME_TO', 'de ' ); 
define('STR_RENAME_TO_BEGINNING', 'au début' );
define('STR_RENAME_TO_END', 'à la fin' );
define('STR_RENAME_TO_POSITION', 'position' ); 
define('STR_RENAME_ADD_BUTTON', 'Ajouter' ); 

define('STR_RENAME_REGEXP', 'Expression régulière remplacer à partir de' ); 
define('STR_RENAME_REPLACE_GLOBAL', 'global' ); 
define('STR_RENAME_REPLACE_IGNORE_CASE', 'ignorer la casse' ); 
define('STR_RENAME_REGEXP_TO', 'de:' ); 
define('STR_RENAME_REPLACE', 'Remplacer' ); 

define('STR_RENAME_CASE_CONVERSION','Convertir');
define('STR_RENAME_CCLOWER','en minuscule');
define('STR_RENAME_CCUPPER','en majuscule');
define('STR_RENAME_CONVERT','Convertir');

define('STR_RENAME_RESET', 'réinitialiser à partir de' );

define('STR_SORT_UP', 'classé par %s, ordre croissant');
define('STR_SORT_DN', 'classé par %s, ordre décroissant');
define('STR_PANEL_CREATED', 'créé(e/s)' );
define('STR_PANEL_LASTACCESS', 'dernier accès' );

define('STR_DO_YOU_WANT_TO_DELETE', 'Souhaitez-vous vraiment effacer l\'élément(les éléments) sélectionné(s) ?');

define('STR_COMPARE',             'comparer');
define('STR_COMPARE_OK',          'ok');
define('STR_COMPARE_CLOSEWINDOW', 'fermer la fenêtre');
define('STR_COMPARE_OPTIONS',     'options');
define('STR_COMPARE_SELECT_DIFFERENT',   'sélectionner les différents fichiers');
define('STR_COMPARE_DESELECT_DIFFERENT', 'désélectionner les différents fichiers');
define('STR_COMPARE_ONLY_FILES_IN_BOTH_PANEL', 'comparer seulement les fichiers existants dans les deux écrans');
define('STR_COMPARE_BY_SIZE', 'comparer la taille des fichiers');
define('STR_COMPARE_BY_TIME', 'comparer la date de modification');

define('STR_JUMP_TO',            'Aller vers:');
define('STR_DOWNLOAD',           'Téléchargement');

define('STR_LOGIN_INFO',         'Pour utiliser FSGuide, veuillez saisir votre identifiant et votre mot de passe donnés par l\'administrateur du système.');
define('STR_LOGIN_ERROR',        'L\identifiant ou le mot de passe est incorrecte.');
define('STR_LOGIN_LOGIN',        'votre identifiant');
define('STR_LOGIN_PASSWORD',     'votre mot de passe');
define('STR_LOGIN_BUTTON',       'identifiant');
define('STR_LOGIN_LOGGEDINAS',   'vous êtes actuellement enregistré en tant que %s.');
define('STR_LOGIN_LOGOUT',       'cliquez ici pour sortir.');
define('STR_LOGIN_DEFAULT_USER', 'vous utilisez FSGuide en tant qu\'utilisateur par défaut');
define('STR_LOGIN_INI_MISSINGDIR',   'Les valeurs du répertoire "%s" pour l\'utilisateur [%s] sont incorrectes (user.ini).');
define('STR_LOGIN_INI_MISSINGSLASH', 'Le chemin "%s" pour l\'utilisateur [%s] est incorrect (user.ini).');

define('STR_ACCESS_DENIED',         'vous n\'avez pas les permissions pour accéder à ce répertoire');
define('STR_ACCESS_COPY_DENIED',    'vous n\'avez pas les permissions pour copier à l\'intérieur de ce répertoire');
define('STR_ACCESS_DELETE_DENIED',  'vous n\'avez pas les permissions pour effacer dans ce répertoire');
define('STR_ACCESS_RENAME_DENIED',  'vous n\'avez pas les permissions pour renommer dans ce répertoire');
define('STR_ACCESS_MOVEFROM_DENIED','vous n\'avez pas les permissions pour déplacer des fichiers vers ce répertoire');
define('STR_ACCESS_MOVETO_DENIED',  'vous n\'avez pas les permissions pour déplacer (ou copier) des fichiers de ce répertoire');
define('STR_ACCESS_MKDIR_DENIED',   'vous n\'avez pas les permissions pour créer dans ce répertoire');
define('STR_ACCESS_MODIFY_DENIED',  'vous n\'avez pas les permissions pour modifier des fichiers dans ce répertoire');
define('STR_ACCESS_UPLOAD_DENIED',  'vous n\'avez pas les permissions pour télécharger des fichiers de ce répertoire');
define('STR_ACCESS_FILELIST_DENIED','vous n\'avez pas les permissions pour assembler la liste de fichiers dans ce répertoire');

define('STR_BACK',	'retour');
define('STR_LESS',	'moins');
define('STR_MORE',	'plus');
define('STR_LINES',	'lignes');
define('STR_FUNCTIONLIST', 'Listes des fonctions');
define('STR_EDIT',	'éditer');
define('STR_VIEW',	'voir');

define('STR_RENAME',	'renommer');
define('STR_COPY',	'copier');
define('STR_MOVE',	'déplacer');
define('STR_MKDIRLEFT',	'créer un répertoire &lt;');
define('STR_MKDIRRIGHT','créer un répertoire &gt;');
define('STR_DELETE',	'effacer');
define('STR_FILELIST',  'liste de fichiers'); /* new */

define('STR_BOTTOM',	'bas');
define('STR_TOP',	'haut');

define('STR_FILENAME',	   'nom');
define('STR_FILESIZE',	   'taille');
define('STR_LASTMODIFIED', 'dernière modification');
define('STR_SUM', '<B>%s</B> byte(s) pour <B>%s</B> élément(s)');

// %s will contain the parent directory path
define('STR_CREATEDIRLEGEND', 'créer un répertoire');
define('STR_CREATEDIR',       'nom du répertoire à créer :');
define('STR_CREATEDIRBUTTON', 'créer');

// %s will contain the original name of the file 
define('STR_RENAMELEGEND',       'renommer');
define('STR_RENAMEENTERNEWNAME', 'entrer le nouveau nom pour %s:');
define('STR_RENAMEBUTTON',       'renommer');

define('STR_SYNCLEFTTORIGHT','ouvrir le contenu de la fenêtre de gauche dans celle de droite');
define('STR_SYNCRIGHTTOLEFT','ouvrir le contenu de la fenêtre de droite dans celle de gauche');

define('STR_ERROR_DIR','Impossible d\'afficher le contenu du répertoire');

define('STR_AUDIO',            'audio');
define('STR_COMPRESSED',       'compressé');
define('STR_EXECUTABLE',       'exécutable');
define('STR_IMAGE',            'image');
define('STR_SOURCE_CODE',      'code source');
define('STR_TEXT_OR_DOCUMENT', 'texte ou document');
define('STR_WEB_ENABLED_FILE', 'fichier web');
define('STR_VIDEO',            'vidéo');
define('STR_DIRECTORY',        'répertoire');
define('STR_PARENT_DIRECTORY', 'répertoire parent');

define('STR_EDITOR_SAVE',      'enregistrer le fichier');
define('STR_EDITOR_SAVE_ERROR','le fichier <I>%s</I> ne peut être enregistré ou n\'existe pas');
define('STR_EDITOR_SAVE_ERROR_WRONG_VALUE','Quand le fichier <I>%s</I> a été édité, vous avez donné la valeur suivante à la position #%s : %s.');
define('STR_EDITOR_SAVE_ERROR_HEX_VALUE_NEEDED','En accord avec les paramètres, vous devez saisir une value hexadécimale positive comprise entre 00 et FF.');
define('STR_EDITOR_SAVE_ERROR_DEC_VALUE_NEEDED','En accord avec les paramètres, vous devez saisir un entier hexadécimal positif compris entre 0 et 255.');

define('STR_FILE_UPLOAD', 'télécharger');
define('STR_FILE_UPLOAD_DISABLED', 'le fichier téléchargé n\'est pas autorisé par php.ini');
define('STR_FILE_UPLOAD_LEFT', STR_FILE_UPLOAD . ' &lt;');
define('STR_FILE_UPLOAD_RIGHT',STR_FILE_UPLOAD . ' &gt;');
define('STR_FILE_UPLOAD_DESC','Choisissez les fichiers que vous voulez télécharger. Choisissez les tâches à réaliser une fois le téléchargement terminé.');
define('STR_FILE_UPLOAD_FILE','Fichier');
define('STR_FILE_UPLOAD_TARGET','Téléchargement de fichier(s) dans ');
define('STR_FILE_UPLOAD_ACTION','quand le téléchargement est terminé :');
define('STR_FILE_UPLOAD_NOTHING','ne rien faire');
define('STR_FILE_UPLOAD_DROPFILE','effacer les fichiers téléchargés quand les tâches sont terminées');
define('STR_FILE_UPLOAD_MAXFILESIZE','La taille maximum authorisée (dans php.ini) est ');

define('STR_FILE_UPLOAD_ERROR',        'Erreur : Impossible de déplacer le fichier %s dans le répertoire %s');
define('STR_FILE_UPLOAD_CHDIR_ERROR',  'Erreur : Impossible de changer (chdir) de répertoire ( %s ). Fichier en cours d\'utilisation : %s');
define('STR_FILE_UPLOAD_UNLINK_ERROR', 'Erreur : Impossible d\'effacer %s après la fin de la tâche.');
define('STR_FILE_UPLOAD_ERROR_FILE_EXCEEDS_INI_SIZE', 'Erreur : Le fichier téléchargé %s dépasse la taille authorisée (directive upload_max_filesize) par php.ini - %s');
define('STR_FILE_UPLOAD_ERROR_FILE_EXCEEDS_FORM_SIZE','Erreur : La taille du fichier téléchargé %s dépasse la taille du champ de formulaire HTML');
define('STR_FILE_UPLOAD_ERROR_FILE_PARTIAL',          'Erreur : Le fichier %s est partiellement téléchargé');

define('STR_FILELIST_DISPLAY_THESE_FIELDS',	'Afficher ces champs dans la liste de fichiers');
define('STR_FILELIST_PATH',			'chemin'); 
define('STR_FILELIST_SIZE',			'taille de fichier'); 
define('STR_FILELIST_DATETIME',			'date et heure'); 
define('STR_FILELIST_ATTRIBS',			'attributs'); 
define('STR_FILELIST_SELECT_ALL',		'tout sélectionner'); 

define('STR_SELECTOR_SELECT_ALL',		'tout sélectionner'); 
define('STR_SELECTOR_SELECT_NONE',		'sélectionner un élément'); 
define('STR_SELECTOR_SELECT_INVERT',		'inverser la sélection'); 
define('STR_SELECTOR_SELECT_DIALOG',		'fenêtre de sélection'); 

define('STR_SELECTOR_OK', 			'ok');
define('STR_SELECTOR_CLOSEWINDOW', 		'fermer la fenêtre');
define('STR_SELECTOR_YES', 			'oui');
define('STR_SELECTOR_NO', 			'non');
define('STR_SELECTOR_SELECT', 			'sélectionner');
define('STR_SELECTOR_DESELECT', 		'désélectionner');
define('STR_SELECTOR_SELECTFILES',		'sélectionner des fichiers');
define('STR_SELECTOR_OPTIONS',			'options');
define('STR_SELECTOR_BYREGEXP',			'par expr. régulière');
define('STR_SELECTOR_BYEXTENSION',		'par extension');
define('STR_SELECTOR_BYEXTGROUP',		'par groupe d\'extensions');
define('STR_SELECTOR_BYFILESIZE',		'par taille');   // keep this string short
define('STR_SELECTOR_BYPERMISSION',		'par perm.'); // keep this string short
define('STR_SELECTOR_BYDATETIME',		'par date');  // keep this string short
define('STR_SELECTOR_READABLE',			'lisible');
define('STR_SELECTOR_WRITEABLE',		'inscriptible');
define('STR_SELECTOR_EXECUTABLE',		'exécutable');

define('JS_MAXDATE_PARSE_ERROR',		'le format de la date et de l\'heure maximum sont mauvais (le format doit être de la forme YYYY-MM-DD HH:MM:SS). Continuer en sélectionnant le temps le plus ancien de la fenêtre ?');
define('JS_MINDATE_PARSE_ERROR',		'le format de la date et de l\'heure minimum sont mauvais (le format doit être de la forme YYYY-MM-DD HH:MM:SS). Continuer en sélectionnant le temps le plus récent de la fenêtre ?');
?>