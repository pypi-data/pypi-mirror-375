from pokemon import *
import unittest


class PokemonTest(unittest.TestCase):
    """
    Make sure the functions work for every combination of Pokemon
    """

    def test_get_pokemon_name(self):
        for i in range(1, 801):
            self.assertTrue(get_pokemon_name(i))

    def test_get_pokemon_stats(self):
        for i in range(1, 801):
            n = get_pokemon_name(i)
            get_pokemon_attack(n)
            get_pokemon_defense(n)
            get_pokemon_height(n)
            get_pokemon_num_types(n)
            get_pokemon_type1(n)
            try:
                get_pokemon_type2(n)
            except ValueError as e:
                if 'does not have a second type' not in str(e):
                    raise ValueError()
            get_pokemon_weight(n)


if __name__ == "__main__":
    unittest.main()
