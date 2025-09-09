"""
I believe this is the source for the CSV file: https://www.kaggle.com/datasets/rounakbanik/pokemon/data
"""

import pandas as pd
import os

directory = os.path.dirname(__file__)
df = pd.read_csv(os.path.join(directory, "pokemon.csv"))

def get_pokemon_name(id: int) -> str: 
    """
    Returns the name of the Pokemon with the given ID
    """
    try:
        return df[df["pokedex_number"] == id]["name"].iloc[0]
    except IndexError:
        raise ValueError(f"The Pokemon with ID {id} could not be found.")

def get_pokemon_attack(name: str) -> int:
    """
    Returns the attack of the Pokemon with the given name
    """
    try:
        return int(df[df["name"] == name]["attack"].iloc[0])
    except IndexError:
        raise ValueError(f"The Pokemon with name '{name}' could not be found.")

def get_pokemon_defense(name: str) -> int:
    """
    Returns the defense of the Pokemon with the given name
    """
    try:
        return int(df[df["name"] == name]["defense"].iloc[0])
    except IndexError:
        raise ValueError(f"The Pokemon with name '{name}' could not be found.")

def get_pokemon_height(name: str) -> int:
    """
    Returns the height of the Pokemon with the given name in centimetres
    """
    try:
        return int(df[df["name"] == name]["height_m"].iloc[0] * 100)
    except IndexError:
        raise ValueError(f"The Pokemon with name '{name}' could not be found.")

def get_pokemon_weight(name: str) -> int:
    """
    Returns the weight of the Pokemon with the given name in kilograms
    """
    try:
        return round(df[df["name"] == name]["weight_kg"].iloc[0])
    except IndexError:
        raise ValueError(f"The Pokemon with name '{name}' could not be found.")

def get_pokemon_num_types(name: str) -> int:
    """
    Returns the number of types that the Pokemon with the given name has.
    """
    if df[df["name"] == name]["type1"].any():
        if df[df["name"] == name]["type2"].any():
            return 2
        return 1
    raise ValueError(f"The Pokemon with name '{name}' could not be found.")

def get_pokemon_type1(name: str) -> str:
    """
    Returns the first type of the Pokemon with the given name.
    """
    try:
        return df[df["name"] == name]["type1"].iloc[0]
    except IndexError:
        raise ValueError(f"The Pokemon with name '{name}' could not be found.")

def get_pokemon_type2(name: str) -> str:
    """
    Returns the second type of the Pokemon with the given name.
    If the Pokemon does not have a second type, an error will be raised.
    """
    try:
        if df[df["name"] == name]["type2"].any():
            return df[df["name"] == name]["type2"].iloc[0]
        else: 
            raise ValueError(f"The Pokemon with name '{name}' does not have a second type.")
    except IndexError:
        raise ValueError(f"The Pokemon with name '{name}' could not be found.")


__all__ = [
    'get_pokemon_name',
    'get_pokemon_attack',
    'get_pokemon_defense',
    'get_pokemon_height',
    'get_pokemon_weight',
    'get_pokemon_num_types',
    'get_pokemon_type1',
    'get_pokemon_type2'
]