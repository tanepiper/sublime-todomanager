import os
import re
import hashlib
import sublime
import sublime_plugin

# Default todo path if the user doesn't overide it
DEFAULT_TODO_PATH = os.path.expanduser(os.path.join('~', '.todomanager'))

# Show states, called by commands and key bindings
SHOW_STATE_ALL = 1
SHOW_STATE_ACTIVE = 2
SHOW_STATE_DONE = 3

# Actions available to the individial todo item menu
ACTIONS = [
    ['Toggle done status', 'Change the done status of the selected item'],
    ['Edit', 'Edit the raw selected todo line'],
    ['Move', 'Move the item up or down the list'],
    ['Delete', 'Delete the todo from the file']
]

# Todo action mappings
ACTION_DONE_STATE = 0
ACTION_EDIT = 1
ACTION_MOVE = 2
ACTION_DELETE = 3

# Move options
MOVE_OPTIONS = [
    ['Up', 'Move the todo item up the list'],
    ['Down', 'Move the todo item down the list']
]

# Move mappings
MOVE_UP = 0
MOVE_DOWN = 1

# Priority List
TODO_OPTIONS = [
    ['', 'No priority'],
    ['A', 'Set a todo to priority A'],
    ['B', 'Set a todo to priority B'],
    ['C', 'Set a todo to priority C'],
    ['D', 'Set a todo to priority D']
]

# Purge options
PURGE_OPTIONS = [
    ['Confirm Purge', 'This will purge all your done todo items from the list'],
    ['Cancel Purge', 'Cancel purging done todo items']
]


class TodoFile(object):
    """
    The main todo class - this loads in the current todo file and loads all the lines
    into memory.  The view that calls this can then filter on show state. All operations
    with a Todo file are members of this class
    """

    def __init__(self, parent_file_path, settings, show_state=SHOW_STATE_ALL):
        """
        Initialise the Todo file object
        """

        # Full path to the current file in view
        self.parent_file_path = parent_file_path
        # Path as array
        self.parent_file_parts = self.parent_file_path.split(os.path.sep)
        # Filename of the current file in view
        self.parent_filename = self.parent_file_parts[len(self.parent_file_parts) - 1]

        # Home path to save todo, either set or default
        self.home_path = settings.get('todo_path') or DEFAULT_TODO_PATH

        # Output file name for the todo file
        self.output_filepath = '%s%s%s' % (self.home_path, os.path.sep, self.generate_filename())

        # Set the current state as global to the object
        self.show_state = show_state

        # Check the path exists and create it if not, once done read the file into memory
        try:
            if not os.path.exists(self.home_path):
                os.makedirs(self.home_path)
            self.process_lines()
        except IOError:
            return None

    def generate_filename(self):
        """
        Generate the MD5 of a file path to avoid naming collisions
        """
        md5 = hashlib.md5()
        md5.update(self.parent_file_path)
        return '%s-%s.%s' % ('todo', md5.hexdigest(), 'txt')

    def reset(self):
        """
        Reset all the variables of this todo file to do with content
        """
        self.lines = []
        self.total_todos = 0
        self.active_todos = []
        self.done_todos = []

    def process_lines(self):
        """
        Reset an open a file for reading, process active and done lines as well
        """
        self.reset()
        self.open_file('r')
        self.lines = self.file_handler.readlines() or []

        if len(self.lines) > 0:
            self.total_todos = sum(1 for line in self.lines)
            for line in self.lines:
                if line[:1] == '*':
                    self.done_todos.append(line)
                else:
                    self.active_todos.append(line)
        self.close_file()

    def open_file(self, mode):
        """
        Opens a file handler
        """
        self.file_handler = open(self.output_filepath, mode)

    def close_file(self):
        """
        Closes a file handler
        """
        self.file_handler.close()

    def write(self):
        """
        Writes the content to a file
        """
        self.open_file('w')
        self.file_handler.writelines(self.lines)
        self.close_file()

    def create_header_line(self, line, line_index):
        """
        Extract out information from a todo to generate the list item
        """
        todo_header_string = 'Todo %d' % line_index

        match_level = re.match(r'\((\w)\)', line, re.I)
        todo_header_string += ' %s' % match_level.group() if match_level else ''

        match_line_numbers = re.compile('(\~\w+)')
        for match in match_line_numbers.finditer(line):
            todo_header_string += ' %s' % match.group()

        match_functions = re.compile('(\&\w+)')
        for match in match_functions.finditer(line):
            todo_header_string += ' %s' % match.group()

        match_projects = re.compile('(\+\w+)')
        for match in match_projects.finditer(line):
            todo_header_string += ' %s' % match.group()

        match_contexts = re.compile('(\@\w+)')
        for match in match_contexts.finditer(line):
            todo_header_string += ' %s' % match.group()

        return todo_header_string

    def generate_list(self, show_state):
        """
        Based on the show state, generate the output list for a quick panel
        """
        self.current_line_index = 0
        self.current_display_mapping = []
        self.current_display_items = []

        if self.total_todos > 0:
            for line in self.lines:
                if show_state == SHOW_STATE_DONE and line[:1] == '*':
                    self.current_display_mapping.append(self.current_line_index)
                    self.current_display_items.append([self.create_header_line(line, self.current_line_index), line])
                elif show_state == SHOW_STATE_ACTIVE and line[:1] != '*':
                    self.current_display_mapping.append(self.current_line_index)
                    self.current_display_items.append([self.create_header_line(line, self.current_line_index), line])
                elif show_state == SHOW_STATE_ALL:
                    self.current_display_mapping.append(self.current_line_index)
                    self.current_display_items.append([self.create_header_line(line, self.current_line_index), line])
                self.current_line_index = self.current_line_index + 1

        if len(self.current_display_items) == 0:
            self.current_display_items.append(['No todos for this file', 'Select the Todo: Add option to begin adding'])
        return self.current_display_items

    def purge_list(self):
        """
        Delete all done todos from a list
        """
        self.lines = self.active_todos

        self.write()
        self.process_lines()

    def move_line(self, direction):
        """
        Move the current selected todo up or down based on the direction
        variable, 0 is up 1 is down
        """
        line_number = self.current_display_mapping[self.todo_position]
        new_index = line_number + (1 if direction == MOVE_DOWN else -1)

        if new_index > -1:
            self.lines.insert(new_index, self.lines.pop(line_number))
            self.write()

    def mark_todo(self, todo_number):
        """
        Change the done status of a todo
        """
        line_number = self.current_display_mapping[todo_number]
        line = self.lines[line_number]
        if line[:1] != '*':
            self.lines[line_number] = '* %s' % line
        elif line[:1] == '*':
            self.lines[line_number] = '%s' % line.replace('* ', '')
        else:
            self.lines[line_number] = '%s' % line
        self.write()

    def get_line(self, todo_number):
        """
        Return the line at a todo position
        """
        line_number = self.current_display_mapping[todo_number]
        line = self.lines[line_number]
        return line

    def edit_todo(self, todo_number, new_line):
        """
        Edit a todo at a todo position
        """
        line_number = self.current_display_mapping[todo_number]
        self.lines[line_number] = '%s' % new_line
        self.write()

    def delete_todo(self, todo_number):
        """
        Delete a todo at a todo position
        """
        line_number = self.current_display_mapping[todo_number]
        del self.lines[line_number]
        self.write()

    def add_new_todo(self, new_todo):
        self.lines.append("%s\n" % new_todo)
        self.write()


class TodoManagerAdd(sublime_plugin.WindowCommand):
    """
    Command to add a todo
    """
    def get_current_function(self):
        """
        Helper class to get the current function for the block of code the cursor is in
        """
        view = self.window.active_view()
        sel = view.sel()[0]
        functionRegs = view.find_by_selector('entity.name.function')
        cf = None
        for r in reversed(functionRegs):
            if r.a < sel.a:
                cf = view.substr(r)
                break

        return cf

    def on_cancel(self):
        """
        Generic cancel handler
        """
        pass

    def on_done(self):
        """
        Append the line to the todo and save
        """
        self.todo_file.add_new_todo(self.output_string)
        self.window.active_view().set_status('todomanager', 'Todo saved')

    def on_contexts(self, contexts):
        """
        Split the context string and add formatting
        """
        if contexts != '':
            contexts_list = contexts.split(' ')
            for context in contexts_list:
                self.output_string += ' @%s' % contexts
        self.on_done()

    def on_projects(self, projects):
        """
        Split the projects string and add formatting
        """
        if projects != '':
            projects_list = projects.split(' ')
            for project in projects_list:
                self.output_string += ' +%s' % project
        self.window.show_input_panel("Enter Contexts", '', self.on_contexts, None, self.on_cancel)

    def on_function(self, function):
        """
        Add formatting to any function names
        """
        if function != '':
            self.output_string += ' &%s' % function
        self.window.show_input_panel("Enter Projects", '', self.on_projects, None, self.on_cancel)

    def on_line_number(self, number):
        """
        Add any formatting to line numbers
        """
        if number != '':
            self.output_string += ' ~%s' % number
        self.window.show_input_panel("Enter Function Name", '%s' % self.at_function if self.at_function is not False else '', self.on_function, None, self.on_cancel)

    def on_todo_entry(self, text):
        """
        Add the main todo text
        """
        if text != '':
            self.output_string += ' %s' % text
        self.window.show_input_panel("Enter Line Number", '%s' % self.at_line if self.at_line is not False else '', self.on_line_number, None, self.on_cancel)

    def on_priority(self, option):
        """
        Add the priority to the todo
        """
        if option > 0:
            self.output_string += '(%s)' % TODO_OPTIONS[option][0]
        self.window.show_input_panel("Enter the text of the todo", '', self.on_todo_entry, None, self.on_cancel)

    def run(self, at_line=False, at_function=False):
        """
        Start a new todo entry
        """
        if self.window.active_view():
            self.at_line = at_line
            self.at_function = at_function

            settings = sublime.load_settings('TodoManager.sublime-settings')
            self.todo_file = TodoFile(self.window.active_view().file_name(), settings)

            self.output_string = ''

            if at_line is True:
                line, column = self.window.active_view().rowcol(self.window.active_view().sel()[0].begin())
                self.at_line = line

            if at_function and self.get_current_function() is not None:
                self.at_function = self.get_current_function()

            self.window.show_quick_panel(TODO_OPTIONS, self.on_priority)
        else:
            sublime.error_message('Todo Manager: You have no file open')
            pass


class TodoManagerList(sublime_plugin.WindowCommand):
    """
    WindowCommand for the following features:
    * Todo: All
    * Todo: Active
    * Todo: Done
    These three options generate the list of items that are displayed.  Contexts
    and projects are extracted from them to aid search, and clicking on a list item
    gives you a futher three options
    * Mark (Un)Done - Toggle the done/undone state of the todo
    * Edit - Edit the todo in raw mode
    * Delete - Delete the todo
    """

    def on_edit_todo(self, new_todo_line):
        """
        When the user has edited the todo this method is called to edit
        the line and save the file
        """
        self.todo_file.edit_todo(self.todo_file.todo_position, new_todo_line)

    def on_cancel(self):
        """
        Generic cancel handler
        """
        pass

    def on_move_action(self, option):
        """
        Calls the function to move the selected line up or down based on the option
        """
        if option > -1:
            self.todo_file.move_line(option)
        else:
            pass

    def on_todo_action(self, option):
        """
        Calls the appropriate functionality to continue based on action selection. Action is
        one of ACTION_DONE_STATE, ACTION_EDIT or ACTION_DELETE
        """
        if option > -1:
            if option == ACTION_DONE_STATE:
                self.todo_file.mark_todo(self.todo_file.todo_position)
            elif option == ACTION_EDIT:
                self.window.show_input_panel("Edit Todo",  self.todo_file.get_line(self.todo_file.todo_position), self.on_edit_todo, None, self.on_cancel)
            elif option == ACTION_DELETE:
                self.todo_file.delete_todo(self.todo_file.todo_position)
            elif option == ACTION_MOVE:
                self.window.show_quick_panel(MOVE_OPTIONS, self.on_move_action)
            else:
                pass

    def on_todo_selection(self, option):
        """
        When a todo from the presented list has been selected, the action selection menu is shown
        """
        if option > 0 or option == 0 and self.todo_file.total_todos > 0:
            self.todo_file.todo_position = option
            self.window.show_quick_panel(ACTIONS, self.on_todo_action)
        else:
            pass

    def run(self, show_state):
        """
        Generates a new instance of the todo class, loads settings
        and the todo file (or creates it if it doesn't exist)
        Then presents a quick panel with the generated list.
        Takes argument for show state which determines if SHOW_STATE_ALL, SHOW_STATE_ACTIVE
        or SHOW_STATE_DONE
        """
        if self.window.active_view():
            settings = sublime.load_settings('TodoManager.sublime-settings')
            self.todo_file = TodoFile(self.window.active_view().file_name(), settings, show_state or SHOW_STATE_ALL)
            message = "Total active todos: %d Total done todos: %s Total todos: %d" % (len(self.todo_file.active_todos), len(self.todo_file.done_todos), self.todo_file.total_todos)
            self.window.active_view().set_status('todomanager', message)
            items = self.todo_file.generate_list(show_state)
            self.window.show_quick_panel(items, self.on_todo_selection)
        else:
            sublime.error_message('Todo Manager: You have no file open')
            pass


class TodoManagerPurge(sublime_plugin.WindowCommand):
    """
    Command to purge all done entries from a list
    """
    def on_purge_selection(self, option):
        if option > -1:
            if option == 0:
                self.todo_file.purge_list()
        else:
            pass

    def run(self):
        """
        Opens a options quick panel with confirm options to purge the file
        """
        if self.window.active_view():
            settings = sublime.load_settings('TodoManager.sublime-settings')
            self.todo_file = TodoFile(self.window.active_view().file_name(), settings, SHOW_STATE_DONE)
            self.window.show_quick_panel(PURGE_OPTIONS, self.on_purge_selection)
        else:
            sublime.error_message('Todo Manager: You have no file open')
            pass


class TodoManagerOpen(sublime_plugin.WindowCommand):
    """
    TodoManagerOpen opens the todo.txt file for the current open file
    """
    def run(self):
        """
        Open a new window with the todo file of the current open file
        """
        if self.window.active_view():
            settings = sublime.load_settings('TodoManager.sublime-settings')
            self.todo_file = TodoFile(self.window.active_view().file_name(), settings, SHOW_STATE_DONE)
            self.window.open_file(self.todo_file.output_filepath)
        else:
            sublime.error_message('Todo Manager: You have no file open')
            pass


class CheckTodoFile(sublime_plugin.EventListener):
    def on_load(self, view):
        settings = sublime.load_settings('TodoManager.sublime-settings')
        self.todo_file = TodoFile(view.file_name(), settings, SHOW_STATE_ALL)
        active_todos = len(self.todo_file.active_todos)
        if active_todos > 0:
            view.set_status('todomanger', '%s currently has %s active todos' % (self.todo_file.parent_filename, active_todos))
