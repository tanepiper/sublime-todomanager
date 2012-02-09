================
Sublime Text 2 Todo Manager
================

* Sourcecode: https://github.com/tanepiper/sublime-todomanager
* Sublime Text 2 forum thread: http://www.sublimetext.com/forum/viewtopic.php?f=5&t=4491
* Release: 1.1.10
* Author: Tane Piper

Is available via the package manager for install.  Please note that SublimeTODO
(https://github.com/robcowie/SublimeTODO) is a different package and provides
different functionality (so they won't clash).

Commands available through the command palate are:

* Todo: Add/Add at Line/Add at Function
* Todo: List All/Active/Done
* Todo: Open file
* Todo: Purge

All have keybindings for Windows, Mac and Linux (untested) and the add functions
also now include context menu items so you can quickly add at the current location
with the right click of a mouse.  Windows and Linux commands are done with
`Ctrl+Alt+t` followed by `Ctrl+Alt+<letter>`.  On the Mac commands are
`⌘+Ctrl+t` followed by `⌘+Ctrl+<letter>`.

All commands act up on the todo file for the current active tab in Sublime Text 2
and cannot be used on files that are closed or being previewed.

Adding a todo
-------------

Adding a todo is done in one simple way, but provides two convenience functions
to speed up input. The first way is to just add a todo `(Ctrl+Alt+t, Ctrl+Alt+a)`
- this takes you through the following steps

1. Select a piority from A-D, or none
2. Enter the task text
3. Enter the line number `~` of the todo
4. Enter the function name `&` of the todo
5. Enter any projects entries `+` as space seperated entries
6. Enter any contexts entries `@` as space seperated entries

The line will then be appended to the bottom of the list.  The two additional
functions are Add-at-line `(Ctrl+Alt+t,Ctrl+Alt+s)` and Add-at-function
`(Ctrl+Alt+t,Ctrl+Alt+f)` which autofill the lines or function box depending on
which is selected.  The function name is always the block of code you are in.

Viewing and filtering todos
---------------------------

Viewing todos is done with the following commands:

* List All `(Ctrl+Alt+t,Ctrl+Alt+j)`
* List Active `(Ctrl+Alt+T,Ctrl+Alt+l)`
* List Done `(Ctrl+Alt+t,Ctrl+Alt+k)` commands.

When you view a list, you can navigate up and down the items.  Pressing enter on
any item will present the item menu, with the following options

* Toggle done status - Change the todo display from active to done, or vice-versa
* Edit - Edit the todo in raw mode, a text box with the full todo item
* Move - Move the item up or down the list, you will be presented with Up or Down options
* Delete - Delete the item from the list, you will be asked to confirm this

To filter items, when you have a list open the command palate allows further
keypresses.  For example if you have the line:

  `* (A) Finish off refactoring ~45 +MyProject @refactor @release`

If you wanted to find this item by it's line number you would type `~45` and the
list will be filtered to display only this item, or all items with a `~45` next
to them.

Purge done items and opening files
----------------------------------

Purging done items `(Ctrl+Alt+t,Ctrl+Alt+p)` removes all done items from the todo
file.  You will be asked before you want to do this.

Opening the file `(Ctrl+Alt+t,Ctrl+Alt+o)` opens the file as a plain text file to
be edited in Sublime Text 2

File location
-----------------------------

In the settings file, you can change the `todo_home` option, currently set to none.
This is the location you wish to save the files - it might be somewhere like a
dropbox folder.

The default folder is `$HOME/.todomanager`

Files are kept in the name format 'todo-<filename-md5>.txt' base on the current
active file - this means you have a todo per file.  If you want the contents of
the todo file, it's best to just open it via the command.

Future features
---------------

* UI for changing priority
* Search over todo file contents
* List all todo files
* Provide way to mark source with todo information
* Support for start/end dates in todos, with filtering
