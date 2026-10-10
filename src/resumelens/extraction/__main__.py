# Optional: lets you test stage 1 from the terminal, without Streamlit.
#   python -m resumelens.extraction ../data/sample_resumes/wednesday_addams.txt
# It is not used for deployment (Streamlit only runs app.py).
import sys
import json

from .extractor import extract_from_file, get_skills

# sys.argv[1] is the file path typed in the terminal
data = extract_from_file(sys.argv[1])
# json.dumps turns the dictionary into JSON-formatted text to print it
print(json.dumps(data, indent=2, ensure_ascii=False))
print("\nFor stage 2:", get_skills(data))
