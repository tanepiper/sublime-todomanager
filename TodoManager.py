import os, sublime, sublime_plugin, re

TODOMANAGER_HOME_DIR = os.path.expanduser(os.path.join('~', '.todomanager'))

if not os.path.exists(TODOMANAGER_HOME_DIR):
  os.makedirs(TODOMANAGER_HOME_DIR)

__file__ = os.path.normpath(os.path.abspath(__file__))
__path__ = os.path.dirname(__file__)


TASK_OPTIONS = [
  ['', 'No priority'],
  ['(A) ', 'Set a todo to priority A'],
  ['(B) ', 'Set a todo to priority B'],
  ['(C) ', 'Set a todo to priority C'],
  ['(D) ', 'Set a todo to priority D']
]

# Get the total number of lines in a file, add 1 because it's 0 index
def total_lines(fname):
  return sum(1 for line in open(fname)) + 1

def get_file_name(command):
  path = command.window.active_view().file_name().split(os.path.sep)
  return '%s' % path[len(path) - 1]

# Get the full path of the todo text file
def get_file_path(command):
  path = command.window.active_view().file_name().split(os.path.sep)
  return '%s\%s-%s.%s' % (TODOMANAGER_HOME_DIR, 'todo', path[len(path) - 1], 'txt')

def create_header_line(line, line_index):
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



class TodoManagerOpen(sublime_plugin.WindowCommand):
  """
  TodoManagerOpen opens the todo.txt file for the current open file
  """
  def run(self):
    """
    Open a new window with the todo file of the current open file
    """
    self.window.open_file(get_file_path(self))


class TodoManagerAdd(sublime_plugin.WindowCommand):
  """
  TodoManagerAdd handles the flow of adding a new task to the file
  """

  # The output string that will be saved to the text file
  ouput_string = None

  at_line = 0

  def on_cancel(self):
    pass

  def on_done(self):
    todo_path_file = open(get_file_path(self), 'a+')
    todo_path_file.write("%s\n" %  self.ouput_string)
    todo_path_file.close()

    self.window.active_view().set_status('todomanager', 'Todo saved: ' + self.ouput_string)

  def on_contexts(self, contexts):
    if contexts != '':
      contexts_list = contexts.split(' ')
      for context in contexts_list:
        self.ouput_string += ' @%s' % context

    self.on_done()

  def on_projects(self, projects):
    if projects != '':
      projects_list = projects.split(' ')
      for project in projects_list:
        self.ouput_string += ' +%s' % project

    self.window.show_input_panel("Enter Contexts", '', self.on_contexts, None, self.on_cancel)


  def on_line_number(self, line_number):
    if line_number != '':
      self.ouput_string += ' ~%s' % line_number

    self.window.show_input_panel("Enter Projects", '', self.on_projects, None, self.on_cancel)

  def on_task(self, task):
    if task != '':
      self.ouput_string += task
      self.window.show_input_panel("Enter Line Number", str(self.at_line) if self.at_line > 0 else '', self.on_line_number, None, self.on_cancel)
    else:
      pass

  def on_priority(self, priority):
    self.ouput_string += TASK_OPTIONS[priority][0]
    self.window.show_input_panel("Enter Todo", '', self.on_task, None, self.on_cancel)

  # Get the user to set the priority first
  def run(self, at_line):
    self.at_line = 0
    line, column = self.window.active_view().rowcol(self.window.active_view().sel()[0].begin())
    if at_line is True:
      self.at_line = line
    self.ouput_string = ''
    self.window.show_quick_panel(TASK_OPTIONS, self.on_priority)


class TodoManagerEdit(sublime_plugin.WindowCommand):

  current_task_position = None

  def on_cancel(self, task):
    pass

  def on_task(self, task):
    lines = open(get_file_path(self), 'r').readlines()
    lines[self.current_task_position] = '%s' % task
    open(get_file_path(self), 'w').writelines(lines)

  def on_task_selection(self, task):
    self.current_task_position = task
    lines = open(get_file_path(self), 'r').readlines()
    self.window.show_input_panel("Edit Todo", lines[int(task)], self.on_task, None, self.on_cancel)

  def run(self):
    self.current_task_position = None
    lines = None
    try:
      lines = open(get_file_path(self), 'r').readlines()
    except IOError:
      self.window.show_quick_panel(['No todos for this file'], self.on_cancel)

    if lines:
      self.window.show_quick_panel(lines, self.on_task_selection)
    else:
      pass


class TodoManagerDelete(sublime_plugin.WindowCommand):

  def on_cancel(self, task):
    pass

  def on_task_selection(self, task):
    lines = open(get_file_path(self), 'r').readlines()
    del lines[int(task)]
    open(get_file_path(self), 'w').writelines(lines)

  def run(self):
    lines = None
    try:
      lines = open(get_file_path(self), 'r').readlines()
    except IOError:
      self.window.show_quick_panel(['No todos for this file'], self.on_cancel)

    if lines:
      self.window.show_quick_panel(lines, self.on_task_selection)
    else:
      pass


class TodoManagerList(sublime_plugin.WindowCommand):
  """
  The class that deals will all functions when a user wants to list todo items.
  As well as displaying todos, this is also a jumping point off to managing
  todos, such as marking them done, editing or deleting them
  """

  # The lines that have been read in from the todo file
  lines = None

  # List to contain the mapping of lines to quick panel entries
  line_mappings = []

  # The currently selected task position in the quick panel
  task_position = None

  def on_cancel(self, task):
    """
    Function to be called when a request is cancelled
    """
    pass

  def on_task(self, task):
    """

    """
    line_position = self.line_mappings[self.task_position][1]
    self.lines[line_position] = '%s' % task
    open(get_file_path(self), 'w').writelines(self.lines)

  def on_action(self, action):
    if action == 0:
      line_position = self.line_mappings[self.task_position][1]
      line = self.lines[line_position]
      if line[:1] == '*':
        self.lines[line_position] = '%s' % self.lines[line_position].replace('* ', '')
      else:
        self.lines[line_position] = '* %s' % self.lines[line_position]

      open(get_file_path(self), 'w').writelines(self.lines)
    if action == 1:
      line_position = self.line_mappings[self.task_position][1]
      line = self.lines[line_position]
      self.window.show_input_panel("Edit Todo", line, self.on_task, None, self.on_cancel)
    if action == 2:
      line_position = self.line_mappings[self.task_position][1]
      del self.lines[int(line_position)]
      open(get_file_path(self), 'w').writelines(self.lines)

  def on_task_selection(self, task_position):
    self.task_position = task_position
    self.window.show_quick_panel(['Mark (Un)Done', 'Edit', 'Delete'], self.on_action)

  def run(self, show_done):
    """
    Function called when a command is passed, takes a parameter of show_done
    which decides if the user wants to display done or active items
    """

    # Reset the lines to none
    self.lines = None

    # Reset the line mappings to a empty list
    self.line_mappings = []

    # Open a file or display a message about no file
    try:
      self.lines = open(get_file_path(self), 'r').readlines()
    except IOError:
      sublime.error_message('There is no todo file for %s' % get_file_name(self))
      return

    # Keep a list of active lines for display
    active_lines = []
    # Check for done items
    panel_index = 0
    # Keep a note of the line index
    line_index = 0
    text = ''
    # Loop over the line
    for line in self.lines:
      todo_header_string = ''
      if show_done == True:
        text = 'done'
        if line[:1] == '*':
          self.line_mappings.append([panel_index, line_index])
          active_lines.append([create_header_line(line, line_index), line])
          panel_index = panel_index + 1
      else:
        text = 'active'
        if line[:1] != '*':
          self.line_mappings.append([panel_index, line_index])
          active_lines.append([create_header_line(line, line_index), line])
          panel_index = panel_index + 1
      line_index = line_index + 1

    if len(active_lines) > 0:
      self.window.show_quick_panel(active_lines, self.on_task_selection)
    else:
      sublime.error_message('There are no %s todos for %s' % ( text, get_file_name(self) ) )