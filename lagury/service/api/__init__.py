from bottle import Bottle


api_app = Bottle()

# load APIs
from .task_manager import *
