# """Defines our app using the create_app function in backend/__init__.py"""

from os import path

basedir = path.abspath(path.dirname(__file__))
is_running_locally = 'pycharm' in basedir.lower()


