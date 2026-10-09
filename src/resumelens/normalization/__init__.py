# Hace que "normalization" sea un paquete y permite importar mas corto:
#   from resumelens.normalization import normalize
from .transformations import VARIANTS
from .transducers import (build_transducer, translate, formal_definition,
                          draw_transducer, save_diagrams)
from .ordering import PROFILE_ORDER, sort_skills, sort_for_all_profiles
from .normalizer import normalize, save_result
