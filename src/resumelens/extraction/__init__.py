# Makes "extraction" a Python package and allows a shorter import:
#   from resumelens.extraction import extract_info
# instead of
#   from resumelens.extraction.extractor import extract_info
from .patterns import PATTERNS, QUALIFICATION_CATEGORIES
from .extractor import extract_info, extract_from_file, get_skills, save_result
