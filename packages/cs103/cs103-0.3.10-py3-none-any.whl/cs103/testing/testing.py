import inspect
from typing import Any

# Constants
DEFAULT_DELTA = 1e-6
COLORS = {
    "red":   "\033[91m",
    "green": "\033[92m",
    "bold":  "\033[1m",
    "reset": "\033[0m"
}

# Global variables
total = 0
passed = 0

# Utils
def within(actual: float, expected: float, tolerance: float = DEFAULT_DELTA) -> bool:
    """
    Returns true if the given numbers are within `tolerance` of
    each other.
    """
    return abs(actual - expected) <= tolerance

def expect(actual: Any, expected: Any) -> None:
    """
    checks to see whether actual is equal to expected, allowing some leeway
    when comparing floats (since, e.g., 0.1 + 0.1 + 0.1 != 0.3 because of the
    way floats are represented internally!)
    
    test results are printed for Jupyter Notebook display and also recorded
    for later summarization by the summary function. Use start_testing() to start
    a new block of tests.
    """
    global total, passed
    if not compare(actual, expected):
        curr = inspect.currentframe()
        caller = inspect.getouterframes(curr)[1]
        line = str(caller[2])
        code = caller[4]
        if (code is not None):
            print(
                COLORS["red"] + "Test failed:" + COLORS["reset"] +
                " expected " + str(expected) + " but got " + str(actual))
            print(
                " " * (6 - len(line)) +
                COLORS["bold"] + "Line " + line + ": " + COLORS["reset"] +
                code[0].strip() +
                ("..." if len(code) > 1 else "")
            )
    else:
        passed += 1
    total += 1

def compare(a, b):
    if (type(a) is float or type(b) is float):
        try:
            return within(a, b)
        except TypeError:
            return False
    if (type(a) is tuple or type(b) is tuple):
        return (type(a) is type(b) and a == b)
    else:
        return a == b

def summary() -> None:
    """
    summarizes the most recent block of tests (all since the last start_testing)
    """
    
    color = COLORS["green"] if (total == passed) else COLORS["red"]
    print(color + str(passed) + " of " + str(total) + " tests passed" + COLORS["reset"])
    reset()

def reset():
    global total, passed
    passed = 0
    total = 0

def start_testing() -> None:
    """
    begins a new block of tests. critically, resets the counts of tests and
    passed tests for the next call to the summary function 
    """
    
    reset()

# be aware that the overall cs103 library has its own __all__
__all__ = ['start_testing', 'expect', 'summary']