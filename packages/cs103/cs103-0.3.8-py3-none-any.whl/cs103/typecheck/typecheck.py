from typing import *
from enum import Enum
from cs103 import Image
from functools import wraps
import os
import sys
import traceback
import inspect

# NOTE: There was a breaking change in Python 3.7. See
# https://www.python.org/dev/peps/pep-0560/#backwards-compatibility-and-impact-on-users-who-don-t-use-typing
#
# The relevant piece is "The only two exceptions are that currently issubclass(List[int], List) returns True, 
# while with this proposal it will raise TypeError, and ..."
#
# We used exactly this type of code. We have switched to using hasattr(tb, '__origin__') and issubclass(tb.__origin__, list),
# although this requires relying on "dunders" that Python prefers we not exploit.

class TypecheckError(TypeError):
    def __init__(self, val, a, b, fn, name):
        self.fn = fn
        message_format_string = 'while checking %s: \x1b[32m%s\x1b[0m is %s, not %s'
        if pretype(a) == pretype(b):
            message_format_string += '\nIf this message appears to say a value both is and is not of a type,' + \
                                     '\nconsider selecting "Restart and Run All" from the "Kernel" menu.'
        return super().__init__(message_format_string%(name,val,pretype(a),pretype(b)))
        
    def _render_traceback_(self):
        print('\x1b[31m')
        print('-'*75)
        print(type(self).__name__)
        print('\n' + str(self) + '\n')
        print(traceback.format_tb(sys.exc_info()[2])[1])
        print('as expected in\n\x1b[34m')
        print(''.join(['  ' + x for x in inspect.getsourcelines(self.fn)[0]]))
        print('\x1b[0m')
        super()._render_traceback_()

def pretype(s: str) -> str:
    pre = 'a'
    if s[0].lower() in ['a', 'e', 'i', 'o']:
        pre = 'an'
    return pre + ' \x1b[36m%s\x1b[0m'%s

def ustr(t: Union) -> str:
    try:
        params = t.__union_params__
    except AttributeError:
        params = t.__args__

    if len(params) == 2 and params[1] is type(None):
        return 'Optional[%s]'%params[0].__name__
    return 'Union[' + ', '.join([x.__name__ for x in params]) + ']'

def astr(t: Any) -> str:
    # TODO: gloss NoneType in a special way?
    try:
        if issubclass(t, Image):
            return 'Image'
        else:
            return (hasattr(t, '__name__') and t.__name__) or str(t)
    except:
        return (hasattr(t, '__name__') and t.__name__) or str(t)

def subtype(value_description: str, va: Any, tb: Any, fn: Any = None, strict: bool = False, error_type: Any = TypecheckError) -> bool:
    ta = type(va)
    name = astr(ta)
    fn_name = fn.__name__

    if tb == None:
        if va != None:
            # TODO: should I convert this to an error_type, as in, not sure about NoneType:
            # error_type(va, name, "NoneType", fn, value_description)
            raise TypeError("The return type of the function \x1b[34m%s\x1b[0m is None, but it returned %s" % (fn_name, str(va)))
        else:
            return True

    if hasattr(tb, '__name__') and tb.__name__ == "cs103.image":
        # TODO: Should this be a typecheck error? See comments above.
        raise TypeError("The return type of the function \x1b[34m%s\x1b[0m is \x1b[36mimage\x1b[0m; did you mean \x1b[36mImage\x1b[0m?" % fn_name)
    
    if type(tb) is type(Union) or (hasattr(tb, '__origin__') and tb.__origin__ == Union):
        if sys.version_info >= (3,6):
            if not (ta == tb or any(subtype(value_description,va,t,fn) for t in tb.__args__)):
                raise error_type(va,name,ustr(tb),fn,value_description)
        else:
            if not (ta == tb or any(subtype(value_description,va,t,fn) for t in tb.__union_params__)):
                raise error_type(va,name,ustr(tb),fn,value_description)
    elif hasattr(tb, '__origin__') and issubclass(tb.__origin__, list):  # was: issubclass(tb, List). There seems to be no good way to manage this now!
        if ta is not list:
            raise error_type(va,name,astr(tb), fn,value_description)
        all(subtype(value_description,v, tb.__args__[0], fn, True) for v in va)
    elif tb is float:
        rv = ta is int or ta is float
        if strict and not rv:
            raise error_type(va,name,astr(tb), fn,value_description)
        return rv
    elif ta is bool and tb is int:
        if strict:
            raise error_type(va,name,astr(tb), fn,value_description)
        return False
    elif not issubclass(ta, tb):
        if strict:
            raise error_type(va,name,astr(tb), fn,value_description)
        return False
        
    return True

def typecheck(fn):
    """
    Annotate a function with @typecheck to check that it takes in the correct
    types of arguments for its parameters and returns the correct type of
    value as its result when it is run. (No checking is does except at each
    moment the function is run.)
    """
    
    @wraps(fn) # preserves attributes of wrapped function (like name and docstring)
    def wrapper(*args):
        # WARNING: This assumes for now that all parameters are positional!
        
        types = get_type_hints(fn)
        sig = inspect.signature(fn)
        parm_names = sig.parameters.keys()
        if len(parm_names) != len(args):
            raise TypeError(("The function \x1b[34m%s\x1b[0m expects %s parameter(s) but was called with %s argument(s)." + \
                             " Be sure to supply one argument for each parameter!")
                             % (fn.__name__, str(len(parm_names)), str(len(args))))
        for (name, val) in zip(parm_names, args):
            if name in types:
                subtype("parameter %s" % name, val, types[name], fn, True)
            else:
                # Type missing for a parameter.
                raise TypeError("The function \x1b[34m%s\x1b[0m is missing a type for the parameter %s." % (fn.__name__, name))

        retval = fn(*args)
        if 'return' in types:
            subtype("the returned value", retval, types['return'], fn, True)
        else:
            # Type missing for the result.
            raise TypeError("The function \x1b[34m%s\x1b[0m is missing a return type." % fn.__name__)

        return retval
    return wrapper

# be aware that the overall cs103 library has its own __all__
__all__ = ['typecheck']  # 'subtype' used to also be exported
