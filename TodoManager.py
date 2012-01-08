import os, sublime, sublime_plugin

TODOMANAGER_HOME_DIR = os.path.expanduser(os.path.join('~', '.todomanager'))

if not os.path.exists(TODOMANAGER_HOME_DIR):
  os.makedirs(TODOMANAGER_HOME_DIR)

__file__ = os.path.normpath(os.path.abspath(__file__))
__path__ = os.path.dirname(__file__)


TASK_OPTIONS = [
  ['', 'No priority'],
  ['(A) ', 'Set a task to priority A'],
  ['(B) ', 'Set a task to priority B'],
  ['(C) ', 'Set a task to priority C'],
  ['(D) ', 'Set a task to priority D']
]

# Get the total number of lines in a file, add 1 because it's 0 index
def total_lines(fname):
  return sum(1 for line in open(fname)) + 1

# Get the full path of the todo text file
def get_file_name(command):
  path = command.window.active_view().file_name().split(os.path.sep)
  return '%s\%s-%s.%s' % (TODOMANAGER_HOME_DIR, 'todo', path[len(path) - 1], 'txt')


class TodoManagerOpen(sublime_plugin.WindowCommand):

  def run(self):
    self.window.open_file(get_file_name(self))


class TodoManagerAdd(sublime_plugin.WindowCommand):

  # The output string that will be saved to the text file
  ouput_string = ''

  def on_cancel(self):
    pass

  def on_contexts(self, contexts):
    if contexts != '':
      contexts_list = contexts.split(' ')
      for context in contexts_list:
        self.ouput_string += ' @%s' % context

    todo_path_file = open(get_file_name(self), 'a+')
    todo_path_file.write("%s\n" %  self.ouput_string)
    todo_path_file.close()

  def on_projects(self, projects):
    if projects != '':
      projects_list = projects.split(' ')
      for project in projects_list:
        self.ouput_string += ' +%s' % project

    self.window.show_input_panel("Enter Contexts", '', self.on_contexts, None, self.on_cancel)


  def on_task(self, task):
    self.ouput_string += task
    self.window.show_input_panel("Enter Projects", '', self.on_projects, None, self.on_cancel)

  def on_priority(self, priority):
    self.ouput_string += TASK_OPTIONS[priority][0]
    self.window.show_input_panel("Enter Task", '', self.on_task, None, self.on_cancel)

  # Get the user to set the priority first
  def run(self):
    self.window.show_quick_panel(TASK_OPTIONS, self.on_priority)


class TodoManagerDelete(sublime_plugin.WindowCommand):

  def on_cancel(self, task):
    pass

  def on_task_selection(self, task):
    lines = open(get_file_name(self), 'r').readlines()
    del lines[int(task)]
    open(get_file_name(self), 'w').writelines(lines)

  def run(self):
    lines = None
    try:
      lines = open(get_file_name(self), 'r').readlines()
    except IOError:
      self.window.show_quick_panel(['No tasks for this file'], self.on_cancel)

    if lines:
      self.window.show_quick_panel(lines, self.on_task_selection)
    else:
      pass


class TodoManagerList(sublime_plugin.WindowCommand):

  def on_cancel(self, task):
    pass

  # def on_edit(self, task):
  #   lines = open(get_file_name(self), 'r').readlines()
  #   lines[int(self.current_task_position)] = '%s' % task
  #   open(get_file_name(self), 'w').writelines(lines)

  # def on_selection(self, option):
  #   if option == 0:
  #     lines = open(get_file_name(self), 'r').readlines()
  #     self.window.show_input_panel("Edit Task", self.active_lines[self.current_task_position], self.on_edit, None, None)

  #   elif option == 1:
  #     lines = open(get_file_name(self), 'r').readlines()
  #     lines[int(self.current_task_position)] = '* %s' % lines[int(self.current_task_position)]
  #     open(get_file_name(self), 'w').writelines(lines)

  #   elif option == 2:
  #     lines = open(get_file_name(self), 'r').readlines()
  #     del lines[int(self.current_task_position)]
  #     open(get_file_name(self), 'w').writelines(lines)

  def on_task_selection(self, task):
    pass
    # self.current_task_position = task
    # self.window.show_quick_panel(['Done', 'Delete'], self.on_selection)

  def run(self, show_done):
    lines = None
    try:
      lines = open(get_file_name(self), 'r').readlines()
    except IOError:
      self.window.show_quick_panel(['No tasks for this file'], self.on_cancel)

    if lines:
      active_lines = []

      # Check for done items
      count = 1
      for line in lines:
        if show_done == True:
          if line[:1] == '*':      
            active_lines.append([str(count), line])
        else:
          if line[:1] != '*':
            active_lines.append([str(count), line])
        count = count + 1

      if len(active_lines) > 0:
        self.window.show_quick_panel(active_lines, self.on_task_selection)
      else:
        self.window.show_quick_panel(['No tasks for this file'], self.on_cancel)
    else:
      pass
