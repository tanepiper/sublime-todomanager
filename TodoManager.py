import os, sublime, sublime_plugin

CODEINTEL_HOME_DIR = os.path.expanduser(os.path.join('~', '.todomanager'))
__file__ = os.path.normpath(os.path.abspath(__file__))
__path__ = os.path.dirname(__file__)


def total_lines(fname):
  return sum(1 for line in open(fname)) + 1


class TodoManagerAdd(sublime_plugin.WindowCommand):

  def on_done(self, task):
    view = self.window.active_view()
    path = view.file_name().split(os.path.sep)

    todo_filename = 'todo-' + path[len(path) - 1] + '.txt'
    todo_path_file = open(todo_filename, 'a+')

    todo_path_file.write("%d %s\n" % (total_lines(todo_filename), task))
    todo_path_file.close()


  def run(self):
    self.window.show_input_panel("New Task", '', self.on_done, None, None)


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

  def on_done(self, option):
    pass

  def run(self):
    view = self.window.active_view()
    path = view.file_name().split(os.path.sep)
    todo_filename = 'todo-' + path[len(path) - 1] + '.txt'

    lines = open(todo_filename, 'r').readlines()

    self.window.show_quick_panel(lines, self.on_done)
