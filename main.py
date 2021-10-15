# """Defines our app using the create_app function in backend/__init__.py"""

from os import path
from backend import create_app
from backend.config import Config

# Initialize the Flask app
app = create_app()

basedir = path.abspath(path.dirname(__file__))
is_running_locally = "pycharm" in basedir.lower()


if __name__ == "__main__" and is_running_locally:
    app.run(host="localhost", port=Config.BOUND_PORT, debug=True)
    # logger.info(f"Running locally via __main__: http://localhost:{Config.BOUND_PORT}")
    print(f"Running locally via __main__: http://localhost:{Config.BOUND_PORT}")
