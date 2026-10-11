# Opcional: sirve para probar las etapas 1 y 2 desde la terminal, sin Streamlit.
#   python -m resumelens.normalization ../data/sample_resumes/wednesday_addams.txt
import sys
import json

from ..extraction import extract_from_file, get_skills
from .normalizer import normalize

data = extract_from_file(sys.argv[1])
skills = get_skills(data)
print("Etapa 1:", skills)

result = normalize(skills)
print(json.dumps(result, indent=2, ensure_ascii=False))
