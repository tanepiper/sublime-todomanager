import os, sublime, sublime_plugin

CODEINTEL_HOME_DIR = os.path.expanduser(os.path.join('~', '.todomanager'))
__file__ = os.path.normpath(os.path.abspath(__file__))
__path__ = os.path.dirname(__file__)


TASK_OPTIONS = [
  ['', 'No priority'],
  ['(A) ', 'Set a task to priority A'],
  ['(B) ', 'Set a task to priority B']
]

def total_lines(fname):
  return sum(1 for line in open(fname)) + 1


class TodoManagerAdd(sublime_plugin.WindowCommand):

  ouput_string = ''

  def on_done(self, task):

    self.ouput_string += task

    view = self.window.active_view()
    path = view.file_name().split(os.path.sep)

    todo_filename = 'todo-' + path[len(path) - 1] + '.txt'
    todo_path_file = open(todo_filename, 'a+')

    todo_path_file.write("%s\n" %  self.ouput_string)
    todo_path_file.close()

  def on_priority(self, priority):

    self.ouput_string += TASK_OPTIONS[priority][0]

    self.window.show_input_panel("Enter Task", '', self.on_done, None, None)

  def run(self):
    self.window.show_quick_panel(TASK_OPTIONS, self.on_priority)
    #self.window.show_input_panel("Set Priority (Enter letter A/B/C/D", '', self.on_priority, None, None)


class TodoManagerDelete(sublime_plugin.WindowCommand):

  def on_done(self, num):

    view = self.window.active_view()
    path = view.file_name().split(os.path.sep)
    todo_filename = 'todo-' + path[len(path) - 1] + '.txt'

    lines = open(todo_filename, 'r').readlines()
    del lines[int(num) - 1]
    open(todo_filename, 'w').writelines(lines)

  def run(self):
    self.window.show_input_panel("Delete Task", '', self.on_done, None, None)


class TodoManagerList(sublime_plugin.WindowCommand):

  def on_edit(self, task):
    pass

  def on_selection(self, option):
    if option == 0:
      view = self.window.active_view()
      path = view.file_name().split(os.path.sep)
      todo_filename = 'todo-' + path[len(path) - 1] + '.txt'

      lines = open(todo_filename, 'r').readlines()

      self.window.show_input_panel("Edit Task", lines[option], self.on_edit, None, None)

    elif option == 1:
      view = self.window.active_view()
      path = view.file_name().split(os.path.sep)
      todo_filename = 'todo-' + path[len(path) - 1] + '.txt'

      lines = open(todo_filename, 'r').readlines()
      lines[int(option)] = '* %s' % lines[int(option)]
      open(todo_filename, 'w').writelines(lines)

    elif option == 2:
      view = self.window.active_view()
      path = view.file_name().split(os.path.sep)
      todo_filename = 'todo-' + path[len(path) - 1] + '.txt'

      lines = open(todo_filename, 'r').readlines()
      del lines[int(option)]
      open(todo_filename, 'w').writelines(lines)

  def open_file(self, option):
    #pass
    self.window.show_quick_panel(['Edit', 'Done', 'Delete'], self.on_selection)

  def on_list_cancel(self, option):
    pass

  def run(self, show_done):
    print show_done
    view = self.window.active_view()
    path = view.file_name().split(os.path.sep)
    todo_filename = 'todo-' + path[len(path) - 1] + '.txt'

    lines = open(todo_filename, 'r').readlines()

    # Check for done items
    active = []
    for line in lines:
      if show_done == 'true':
        if line[:1] == '*':      
          active.append(line)
      else:
        if line[:1] != '*':
          active.append(line)

    if len(lines) > 0:
      self.window.show_quick_panel(active, self.open_file)
    else:
      self.window.show_quick_panel(['No tasks for this file'], self.on_list_cancel)
