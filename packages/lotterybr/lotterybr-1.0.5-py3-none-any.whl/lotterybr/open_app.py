from typing import Literal

from .app_ptbr import app_br as ptbr
from .app_eng import app_en as eng

Languages = Literal["eng", "ptbr"]

class InvalidLanguageError(ValueError):
    """Raised when an invalid language is provided."""
    def __init__(self, language: str):
        super().__init__(f"Invalid type: {language}. Must be one of {', '.join(Languages.__args__)}.")

def open_app(language = "eng"):
    """
    Opens the lottery shiny in the specified language.

    This function allows users to choose between the English (eng) and Brazilian Portuguese (ptbr) versions of the lottery shiny.

    Parameters
    ----------
    language : Languages, default="eng"
        The language to use for the application. Must be one of:
            - "eng" for English
            - "ptbr" for Brazilian Portuguese

    Raises
    ----------
    InvalidLanguageError
        If an unsupported language is provided.

    Examples
    --------
    Open the application in English:

    >>> open_app()

    Open the application in Brazilian Portuguese:

    >>> open_app(language="ptbr")
    """
    valid_languages = ("eng", "ptbr")
    if language not in valid_languages:
        raise InvalidLanguageError(language)
    
    if language == "eng":
        eng.run()
    elif language == "ptbr":
        ptbr.run()