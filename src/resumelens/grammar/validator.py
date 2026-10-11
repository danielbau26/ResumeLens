from pathlib import Path
from textx import metamodel_from_file


# Obtiene la ruta de candidate.tx en la misma carpeta de este archivo.
GRAMMAR_PATH = Path(__file__).parent / "candidate.tx"

# Lee la gramática y prepara el analizador del lenguaje.
metamodel = metamodel_from_file(str(GRAMMAR_PATH))


def validate_candidate(text):
    # Analiza el texto usando las reglas de candidate.tx.
    # Si es válido, devuelve un objeto con los datos del candidato.
    # Si es inválido, textX lanza un error.
    candidate = metamodel.model_from_str(text)

    return candidate