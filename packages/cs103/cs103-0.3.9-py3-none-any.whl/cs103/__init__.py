from .testing.testing import *
#from .iofunc.iofunc import *  # no longer in use
from .image.image import *
from .custom.custom import *
from .parsing.parsing import *
from .typecheck.typecheck import *
from .pokemon.pokemon import *
from .submit import submit

start_testing()  # reset the test counts

__all__ = [
    'Image',
    'above',
    'beside',
    'circle',
    'custom_init',
    'draw',
    'ellipse',
    'empty_image',
    'expect',
    'get_pokemon_name',
    'get_pokemon_attack',
    'get_pokemon_defense',
    'get_pokemon_height',
    'get_pokemon_weight',
    'get_pokemon_num_types',
    'get_pokemon_type1',
    'get_pokemon_type2',
    'image_height',
    'image_width',
    'overlay',
    'parse_float',
    'parse_int',
    'rectangle',
    'square',
    'start_testing',
    'submit',
    'summary',
    'triangle',
    'typecheck'
    ]