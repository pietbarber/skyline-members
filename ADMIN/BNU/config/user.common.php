<?php

$user_rights_implemented = Array(
  'ACCESS',		// enable dirlist and view files in directory
  'RENAME',		// enable renaming files in directory 

  'MOVEFROM',		// enable moving files FROM directory 
  			// moving also needs copy privileges in target 
  			// directory!!!

  'COPY',		// enable copying TO current directory from other panel
  'DELETE',		// enable deleting files in directory
  'MKDIR',		// enable creating a directory in directory
  'MODIFY',		// enable file modifications (edit) in directory
  'UPLOAD',		// enable file uploads to current directory
  'FILELIST'		// enable filelist in current directory
);

?>