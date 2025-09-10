import inspect
import os

def get_caller_file_abs_path(caller_level: int = 0):
    stack = inspect.stack()
    caller_frame = stack[2 + caller_level]
    caller_filename = caller_frame.filename
    absolute_path = os.path.abspath(caller_filename)

    del stack
    return absolute_path
