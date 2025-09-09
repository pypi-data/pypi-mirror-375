from typing import Optional
from ..testing.testing import *
from ..typecheck.typecheck import *
import math

@typecheck
def parse_int(s: str) -> Optional[int]:
    """
    return s as an integer, if possible; returns None if s is not an integer
    
    For example, parse_int('3') returns 3, but parse_int('3.2') and 
    parse_int('argh') both return None.
    """
    
    if type(s) is not int and type(s) is not str:
        return None
    try:
        return int(s)
    except ValueError:
        return None

@typecheck
def parse_float(s: str) -> Optional[float]:
    """
    return s as a float, if possible; returns None if s is not a float
    
    For example, parse_float('3') returns 3.0 and parse_float('3.2') returns 3.2, 
    but parse_float('argh') returns None.
    
    NOTE: parse_float('NaN') returns None, even though technically NaN is a 
    special float value meaning 'not a number'.
    """

    if type(s) is not float and type(s) is not str:
        return None
    try:
        f = float(s)
        if math.isnan(f):
            return None
        else:
            return f
    except ValueError:
        return None

    
    
# We tried to follow bool() functionality for a parse_bool() but we never exported it. So now we decided to remove the function entirely :(  

# be aware that the overall cs103 library has its own __all__
__all__ = ['parse_int', 'parse_float']  



#parse_int tests
start_testing()
expect(parse_int("3"), 3) #regular case
expect(parse_int("3276"), 3276) #different funky regular case
expect(parse_int("0"), 0) #0 tends to act funky 
expect(parse_int("3.4"), None) #correct type but slightly incorrect value
expect(parse_int("three"), None) #correct type but incorrect value
#expect(parse_int(False), None) #incorrect type  # Now handled by @typecheck
#summary() #These are commented out so that summaries are not show when the cs103 library is imported

#parse_float tests
start_testing()
expect(parse_float("12.4"), 12.4) #regular case
expect(parse_float("3.1415926535897932384626433"), 3.1415926535897932384626433) # very funky case
expect(parse_float("73826473.0"), 73826473.0) #ints technichally count
expect(parse_float("3276"), 3276) #ints technichally count
expect(parse_float("0"), 0) #0 tends to act funky 
expect(parse_float("three and a half"), None) #correct type but incorrect value
#expect(parse_float(False), None) #incorrect type  # Now handled by @typecheck
#summary()  #These are commented out so that summaries are not show when the cs103 library is imported


