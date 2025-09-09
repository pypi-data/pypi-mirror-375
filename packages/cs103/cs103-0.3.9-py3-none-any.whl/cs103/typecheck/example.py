from typecheck import *
from typing import *

Person = NamedTuple('Person', [('name', str), ('age', int)])

@typecheck
def majority_age(p: Person) -> bool:
    """
    This function's name and doc string should be preserved, even though it is decorated with @typecheck.
    """
    return p.name  # incorrect: typechecker should error out

try:
    majority_age(123)  # incorrect arg type: should error
except Exception as e:
    print(e)

try:
    majority_age(Person('Gerald', 23))  # should give ReturnError above
except Exception as e:
    print(e)

@typecheck
def noop() -> None:
	return

try:
	noop()
except Exception as e:
	print(e)


try:
    print(majority_age.__name__) # should give "majority_age"
    help(majority_age) # should describe majority_age, including its name and doc_string, not typecheck
except Exception as e:
    print(e)


try:
    @typecheck
    def no_parm_type(x, y:int) -> float:
        return 3.14

    no_parm_type("hello", 2) # should give an error on x having no type specified

    print("FIRST PARAM TYPE CHECK REACHED THIS POINT, which it should not")
except Exception as e:
    print(e)


try:
    @typecheck
    def no_parm_type2(x: str, y) -> float:
        return 3.14

    no_parm_type2("hello", 2) # should give an error on y having no type specified

    print("SECOND PARAM TYPE CHECK REACHED THIS POINT, which it should not")
except Exception as e:
    print(e)


try:
    @typecheck
    def no_return_type(x: str, y: int):
        return 3.14

    no_return_type("hello", 2) # should give an error on no return type specified

    print("RETURN TYPE CHECK REACHED THIS POINT, which it should not")
except Exception as e:
    print(e)
