from .app import LinguaFastapiAPI, LinguaFastapiApp

# Backward-compatible alias expected by examples
LinguaSQLFastAPIApp = LinguaFastapiApp
LinguaSQLFastAPIAPI = LinguaFastapiAPI

__all__ = [
    "LinguaFastapiAPI",
    "LinguaFastapiApp",
    "LinguaSQLFastAPIAPI",
    "LinguaSQLFastAPIApp",
]


