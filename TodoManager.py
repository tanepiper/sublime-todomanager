import os, sublime, sublime_plugin, re

DEFAULT_TODO_PATH = os.path.expanduser(os.path.join('~', '.todomanager'))



if not os.path.exists(DEFAULT_TODO_PATH):
  os.makedirs(DEFAULT_TODO_PATH)

__file__ = os.path.normpath(os.path.abspath(__file__))
__path__ = os.path.dirname(__file__)





class TodoFile(object):

  SHOW_STATE_ALL = 1
  SHOW_STATE_ACTIVE = 2
  SHOW_STATE_DONE = 3

  ACTION_DONE_STATE = 0
  ACTION_EDIT = 1
  ACTION_DELETE = 2

  TASK_OPTIONS = [
    ['', 'No priority'],
    ['(A) ', 'Set a todo to priority A'],
    ['(B) ', 'Set a todo to priority B'],
    ['(C) ', 'Set a todo to priority C'],
    ['(D) ', 'Set a todo to priority D']
  ]


 

  total_todos = 0

  active_todos = []

  done_todos = []

  def __init__(self, parent_file_path, settings, show_state=SHOW_STATE_ALL):
    self.parent_file_path = parent_file_path
    self.parent_file_parts = self.parent_file_path.split(os.path.sep)
    self.parent_filename = self.parent_file_parts[len(self.parent_file_parts) - 1]

    self.home_path = settings.get('todo_path') or DEFAULT_TODO_PATH
    self.output_filepath = '%s%s%s-%s.%s' % (self.home_path, os.path.sep, 'todo', self.parent_filename, 'txt')

    self.show_state = show_state 

    print self.output_filepath
    try:
      if not os.path.exists(DEFAULT_TODO_PATH):
        os.makedirs(DEFAULT_TODO_PATH)
      self.open_file('r')
      self.process_lines()
      self.close_file()

    except IOError:
      return None

  def process_lines(self):
    self.lines = self.file_handler.readlines() or []
    self.active_todos = []
    self.done_todos = []

    if len(self.lines) > 0:
      self.total_todos = sum(1 for line in self.lines)
      for line in self.lines:
        if line[:1] == '*':
          self.done_todos.append(line)
        else:
          self.active_todos.append(line)
    else:
      self.total_todos = 0

  def open_file(self, mode):
    self.file_handler = open(self.output_filepath, mode)

  def close_file(self):
    self.file_handler.close()

  def write(self):
    self.open_file('w')
    self.file_handler.writelines(self.lines)
    self.close_file()

  # def write_file(self):
  #   self.open_file('w')
  #   line_position = self.line_mappings[self.task_position][1]
  #   line = self.lines[line_position]

  def create_header_line(self, line, line_index):
    todo_header_string = 'Task %d' % line_index

    match_level = re.match(r'\((\w)\)', line, re.I)
    todo_header_string += ' %s' % match_level.group() if match_level else ''

    match_projects = re.compile('(\+\w+)')
    for match in match_projects.finditer(line):
      todo_header_string += ' %s' % match.group()

    match_contexts = re.compile('(\@\w+)')
    for match in match_contexts.finditer(line):
      todo_header_string += ' %s' % match.group()

    return todo_header_string

  def generate_list(self, show_state):
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
    else:
      self.current_display_items.append(['No todos for this file', 'Select the Todo: Add option to begin adding'])
    return self.current_display_items

  def mark_task(self, task_number):

    line_number = self.current_display_mapping[task_number]
    line = self.lines[line_number]
    if line[:1] != '*':
      self.lines[line_number] = '* %s' % line
    elif line[:1] == '*':
      self.lines[line_number] = '%s' % line.replace('* ', '')
    else:
      self.lines[line_number] = '%s' % line
    self.write()

  def get_line(self, task_number):
    line_number = self.current_display_mapping[task_number]
    line = self.lines[line_number]
    return line

  def edit_task(self, task_number, new_line):
    line_number = self.current_display_mapping[task_number]
    self.lines[line_number] = '%s' % new_line
    self.write()

  def delete_task(self, task_number):
    line_number = self.current_display_mapping[task_number]
    del self.lines[line_number]
    self.write()



class TodoManagerList(sublime_plugin.WindowCommand):
  """
  WindowCommand for the following features:
    * Todo: All
    * Todo: Active
    * Todo: Done
  These three options generate the list of items that are displayed.  Contexts
  and projects are extracted from them to aid search, and clicking on a list item
  gives you a futher three options
    * Mark (Un)Done - Toggle the done/undone state of the task
    * Edit - Edit the task in raw mode
    * Delete - Delete the task
  """

  # The show state of the view is one of SHOW_STATE_ALL, SHOW_STATE_ACTIVE and
  # SHOW_STATE_DONE
  show_state = 0

  # The todo file object that is generated
  todo_file = None

  # Line mappings for display to real lines
  line_mappings = []

  # The current selected task position for option functions
  task_position = None

  def on_edit_task(self, new_task_line):
    """
    When the user has edited the task this method is called to edit
    the line and save the file
    """
    self.todo_file.edit_task(self.todo_file.task_position, new_task_line)

  def on_cancel(self):
    """
    Generic cancel handler
    """
    pass

  def on_task_action(self, option):
    """
    Calls the appropriate functionality to continue based on action selection. Action is
    one of ACTION_DONE_STATE, ACTION_EDIT or ACTION_DELETE
    """
    if option > -1:
      if option == ACTION_DONE_STATE:
        self.todo_file.mark_task(self.todo_file.self.task_position)
      elif option == ACTION_EDIT:
        self.window.show_input_panel("Edit Todo",  self.todo_file.get_line(self.todo_file.task_position), self.on_edit_task, None, self.on_cancel)
      elif option == ACTION_DELETE:
        self.todo_file.delete_task(self.todo_file.self.task_position)
    else:
      pass
     


  def on_task_selection(self, option):
    """
    When a task from the presented list has been selected, the action selection menu is shown
    """
    if option > 0 or option == 0 and self.todo_file.total_todos > 0:
      self.todo_file.task_position = option
      self.window.show_quick_panel(['Mark (Un)Done', 'Edit', 'Delete'], self.on_task_action)
    else:
      pass


  def on_none_selection(self, option):
    pass

  def run(self, show_state):
    """
    Generates a new instance of the todo class, loads settings
    and the todo file (or creates it if it doesn't exist)
    Then presents a quick panel with the generated list.

    Takes argument for show state which determines if SHOW_STATE_ALL, SHOW_STATE_ACTIVE
    or SHOW_STATE_DONE
    """
    settings = sublime.load_settings('TodoManager.sublime-settings')
    self.todo_file = TodoFile(self.window.active_view().file_name(), settings, show_state)

    message = 'Total active todos: %d Total done todos: %s Total todos: %d' % ( len(self.todo_file.active_todos), len(self.todo_file.done_todos), self.todo_file.total_todos )
    self.window.active_view().set_status('todomanager', message)
    items = self.todo_file.generate_list(show_state)
    self.window.show_quick_panel(items, self.on_task_selection)
