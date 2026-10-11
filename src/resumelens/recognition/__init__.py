# Makes "recognition" a Python package and allows a shorter import:
#   from resumelens.recognition import recognize
from .profiles import PROFILES
from .automata import (build_transitions, build_automaton, automaton_type, accepts,
                       formal_definition, draw_automaton, save_diagrams)
from .recognizer import recognize, accepted_profiles, save_result
 