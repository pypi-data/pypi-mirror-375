import os
from typing import Literal

import pandas as pd
import pyreadr

from .translate_data import translateData


Games = Literal["maismilionaria", "megasena", "lotofacil", "quina", "lotomania", "duplasena", "diadesorte"]
Types = Literal["numbers", "winners", "dezenas", "ganhadores"]
Languages = Literal["eng", "ptbr"]

class InvalidGameError(ValueError):
    """Raised when an invalid game is provided."""
    def __init__(self, game: str):
        super().__init__(f"Invalid game: {game}. Must be one of {', '.join(Games.__args__)}.")

class InvalidTypeError(ValueError):
    """Raised when an invalid type is provided."""
    def __init__(self, type: str):
        super().__init__(f"Invalid type: {type}. Must be one of {', '.join(Types.__args__)}.")

class InvalidLanguageError(ValueError):
    """Raised when an invalid language is provided."""
    def __init__(self, language: str):
        super().__init__(f"Invalid type: {language}. Must be one of {', '.join(Languages.__args__)}.")

def get_data(
    game: Games = "megasena", 
    type: Types = "winners",
    language: Languages = "eng",
) -> pd.DataFrame:
    """
    Retrieves lottery data for a specified game and data type.

    This function fetches data from the LotteryBrasilDATA repository on GitHub for a given lottery game
    and data type ('numbers' or 'winners').

    Parameters:
        game (Games, optional): The name of the lottery game. Defaults to "megasena".
            Allowed values:
                - 'maismilionaria': Mais Milionária
                - 'megasena': Mega-Sena
                - 'lotofacil': Lotofácil
                - 'quina': Quina
                - 'lotomania': Lotomania
                - 'duplasena': Dupla Sena
                - 'diadesorte': Dia de Sorte
        type (Types, optional): The type of data to retrieve. Defaults to "winners".
            Allowed values:
                - 'numbers': Drawn numbers data
                - 'winners': Winners data
                - 'dezenas' (Portuguese): Equivalent to 'numbers'
                - 'ganhadores' (Portuguese): Equivalent to 'winners'
        language (Languages, optional): The language for the returned data. Defaults to "eng".
            Allowed values:
                - 'eng': English
                - 'ptbr': Portuguese (Brasil)

    Returns:
        pd.DataFrame: A DataFrame containing the loaded data.

    Raises:
        InvalidGameError: If an invalid game name is provided.
        InvalidTypeError: If an invalid data type is provided.
        InvalidLanguageError: If an invalid language is provided.
        ValueError: If there's an error downloading or loading the data.

    Examples:
        Get drawn numbers data for Mega-Sena in English:

        ```python
        df = get_data('megasena', 'numbers')
        print(df.head())
        ```

        Get winners data for Lotofácil in Portuguese:

        ```python
        df = get_data('lotofacil', 'ganhadores', 'ptbr')
        print(df.head())
        ```
    """
    valid_games = {"maismilionaria", "megasena", "lotofacil", "quina", "lotomania", "duplasena", "diadesorte"}
    valid_languages = ("eng", "ptbr")
    valid_types = {"numbers", "winners", "dezenas", "ganhadores"}

    if game not in valid_games:
        raise InvalidGameError(game)

    if type not in valid_types:
        raise InvalidTypeError(type)
    
    if language not in valid_languages:
        raise InvalidLanguageError(language)
    
    match type:
        case 'numbers':
            type_str = 'dezenas'
        case 'winners':
            type_str = 'ganhadores'
        case 'dezenas':
            type_str = 'dezenas'
        case 'ganhadores':
            type_str = 'ganhadores'

    url = f"https://github.com/tomasbp2/LotteryBrasilDATA/blob/main/{game}/{type_str}.rds?raw=true"

    try:
        module_dir = os.path.dirname(os.path.abspath(__file__))
        dst_dir = os.path.join(module_dir, "..", "dataset", game)

        if not os.path.exists(dst_dir):
            os.makedirs(dst_dir)

        dst_path = os.path.join(dst_dir, f"{type_str}.rds")
        pyreadr.download_file(url, dst_path)
        result = pyreadr.read_r(dst_path)
        df = result[None]
        
    except Exception as e:
        raise ValueError(f"Error while importing data: {e}")
    
    if language == 'ptbr':
        df = translateData(df, game, type)

    return df
