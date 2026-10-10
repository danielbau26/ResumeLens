# Optional: tests stages 1, 2 and 3 from the terminal, without Streamlit.
#   python -m resumelens.recognition ../data/sample_resumes/wednesday_addams.txt
import sys
import json
 
from ..extraction import extract_from_file, get_skills
from ..normalization import normalize
from .recognizer import recognize, accepted_profiles
 
data = extract_from_file(sys.argv[1])
skills = get_skills(data)
normalized = normalize(skills)
results = recognize(normalized["by_profile"])
 
print(json.dumps(results, indent=2, ensure_ascii=False))
print("\naccepted profiles:", accepted_profiles(results))

#corre las 3 etapa seguidas para pruebas parciales