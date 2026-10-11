import sys

from ..extraction import extract_from_file, get_skills
from ..normalization import normalize
from ..recognition import recognize
from ..visualization import generate_markdown, save_markdown

from .generator import generate_candidate
from .validator import validate_candidate


def main():
    # Comprueba que se haya recibido la ruta del archivo.
    if len(sys.argv) != 2:
        print("Uso: python -m resumelens.grammar ruta_del_cv.txt")
        return

    # Obtiene la ruta escrita en la terminal.
    path = sys.argv[1]

    # Etapa 1: extrae la información del archivo.
    data = extract_from_file(path)
    skills = get_skills(data)

    # Etapa 2: normaliza y ordena las habilidades.
    normalized = normalize(skills)

    # Etapa 3: evalúa los cuatro perfiles.
    results = recognize(normalized["by_profile"])

    # Etapa 4: genera el texto y lo valida con textX.
    text = generate_candidate(data, normalized, results)
    candidate = validate_candidate(text)

    # Genera y guarda la ficha usando el objeto validado.
    markdown = generate_markdown(candidate)
    save_markdown(markdown, "candidate.md")

    print("Candidate profile saved to candidate.md")


if __name__ == "__main__":
    main()