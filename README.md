================
Sublime Text 2 Todo Manager
================

https://github.com/tanepiper/sublime-todomanager

My new plugin for Sublime Text 2. It's a simple Todo manager that is on a per-file basis.

  Release:1.1.0

Commands available through the command palate are:

  * Todo: Add/Add at Line/Add at Function
  * Todo: List All/Active/Done
  * Todo: Open file
  * Todo: Purge

All have keybindings for Windows, Mac and Linux (untested).

When you now go into a list item, you can mark it done or undone, can simply edit it or delete it.  Add at line will automatically set the line number in the current file selection (but you can edit it in the steps), same with add at function (it will select the function name of the code block you are in)

When adding a new task you will first be presented with a list of priority settings, you can hit Esc if you don't want one, or select none - but I give a sensible list of A-D here.  Next you enter the text of the todo item, next the line mapping.  Line mapping and function name is not in the todo.txt format but is stored with a `~` character for line number and `&` character for function and I hope to add support for this in the future.

Adding projects and contexts allows you to tag items with a project (`+`) prefix or context (`@`) prefix - just enter them space separated, you don't need to add the `+` or `@` these will be automatically added.  Marked items are marked with a `*` at the beginning.  The plugin uses the autosearch facility of the query panel to allow you to filter content. I'll be looking to add date support at a later date as well.

Editing, currently you will be presented with just the whole text string of the todo to edit - and delete is pretty self explanatory.

The plugin creates a .todomanager folder in your home directory to keep them self contained, in the name format 'todo-<filename-md5>.txt' base on the current active file - this means you have a todo per file.  There is plans to add search over todo files as well.

You can purge all done items with the Todo: Purge command, this will confirm the action then delete all entries marked done.

Is available via the package manager

Comments and suggestions welcome