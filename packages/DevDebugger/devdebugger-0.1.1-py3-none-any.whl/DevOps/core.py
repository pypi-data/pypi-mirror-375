from types import FunctionType
from typing import Callable, Any
from pprint import pp, pformat
import time
import sys

__all__ = [
    "hook_method",
    "time_method",
    "CallLog",
    "CatchExceptions",
    "enable_stack_trace",
    "disable_stack_trace"
]

# Hook Method to override library methods
def hook_method(original_function: FunctionType, replacement: FunctionType) -> tuple[Callable[[tuple[Any, ...], dict[str, Any]], Any], FunctionType]:
    """
    Hooks the original method with the replacement, and passes the original function and the called params to the replacement function
    :param original_function:
    :param replacement:
    :return: new wrapper method to replace orignal function, original function
    """
    def _wrapper(*args, **kwargs):
        return replacement(original_function, *args, **kwargs)
    return _wrapper, original_function

# Method timer to track how long functions are taking
def time_method(method: FunctionType):
    def _wrapper(*args, **kwargs):
        start = time.time()
        out = method(*args, **kwargs)
        print(f"Method '{method.__name__}' took {time.time() - start}s")
        return out
    return _wrapper

# Method Logger
def CallLog(method: FunctionType):
    """
    Decorator to Log method call params and return values
    :param method: method to log
    :return: wrapper method to call
    """
    def _wrapper(*args, **kwargs):
        print(f"[CALL] {method.__name__} args={args} kwargs={kwargs}")
        result = method(*args, **kwargs)
        print(f"[RETURN] {method.__name__} -> {result}")
        return result
    return _wrapper

# Exception Catcher
def CatchExceptions(method: FunctionType):
    """
    Decorator to Log method call params and return values
    :param method: method to log
    :return: wrapper method to call
    """
    def _wrapper(*args, **kwargs):
        try:
            result = method(*args, **kwargs)
            return result
        except Exception as e:
            print("Exception:", e)
            _ = CALL_STACK.copy()
            print("Call Stack:")
            stack_str = pformat(_)
            print('\n'.join(["\t"+l for l in stack_str.split("\n")]))
            return None
    return _wrapper

# Call Stack Tracer
CALL_STACK = []
def _trace(frame, event, arg):
    if event == "call":
        code = frame.f_code
        CALL_STACK.append((code.co_name, frame.f_locals))
    elif event == "return":
        code = frame.f_code
        CALL_STACK.pop()
    return _trace  # keep tracing deeper calls
def _trace_and_log(frame, event, arg):
    if event == "call":
        code = frame.f_code
        CALL_STACK.append((code.co_name, frame.f_locals))
        print(f"\n[CALL] {code.co_name}")
        print("Call Stack:")
        pp(CALL_STACK)
    elif event == "return":
        code = frame.f_code
        print(f"\n[RETURN] {code.co_name}")
        CALL_STACK.pop()
        pp(CALL_STACK)

    return _trace_and_log  # keep tracing deeper calls
def enable_stack_trace():
    """
    Enables the stack tracer and logging
    :return:
    """
    sys.settrace(_trace_and_log)
def disable_stack_trace():
    """
    Disables the stack tracer and logging
    :return:
    """
    sys.settrace(_trace)
sys.settrace(_trace)

# Block Timer
class BlockTimer:
    def __init__(self, Name: str):
        self.name = Name
    def __enter__(self):
        self.start = time.time()
    def __exit__(self, exc_type, exc_val, exc_tb):
        print(f"Code Block '{self.name}' took {time.time() - self.start}s")