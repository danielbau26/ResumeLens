# Stage 2 - Finite-state transducers (FST) built with pyformlang.
# For each canonical form we build one character-level transducer: it reads a
# word one character at a time and, if the word is one of the known variants,
# it outputs the canonical form. This is the formal model required by the
# assignment (the 7-tuple M = (Q, Σ, Γ, δ, ω, q0, F)).

import shutil
import subprocess
from pathlib import Path

from pyformlang.fst import FST

from .transformations import TRANSFORMATIONS


# Construye UN transductor para una forma canonica y sus variantes.
# Ejemplo: build_transducer("JAVASCRIPT", ["JavaScript", "JS"])
def build_transducer(canonical, variants):
    fst = FST()
    # q0 = estado inicial, qf = estado final (de aceptacion)
    fst.add_start_state("q0")
    fst.add_final_state("qf")

    # counter da nombres unicos a los estados intermedios, asi las variantes
    # no se mezclan entre si por accidente.
    counter = 0
    for variant in variants:
        # casefold() pasa a minusculas: "JS" -> ['j', 's']. Asi "JS" y "js"
        # recorren el mismo camino y no hay que duplicar variantes.
        symbols = list(variant.casefold())
        if not symbols:
            continue
        current = "q0"
        for index, symbol in enumerate(symbols):
            is_last = index == len(symbols) - 1
            # el ultimo caracter lleva al estado final; los demas a uno nuevo
            target = "qf" if is_last else f"{canonical}_{counter}"
            counter += 1
            # emite la forma canonica SOLO en el primer caracter; el resto emite nada
            output = [canonical] if index == 0 else []
            fst.add_transition(current, symbol, target, output)
            current = target
    return fst


# Construye un transductor por cada forma canonica del catalogo.
# Devuelve un diccionario {canonico: FST}.
def build_all():
    return {canonical: build_transducer(canonical, variants)
            for canonical, variants in TRANSFORMATIONS.items()}


# Une todos los transductores en una sola maquina (la vista de "un transductor").
def combined_transducer():
    fst = None
    for canonical, variants in TRANSFORMATIONS.items():
        current = build_transducer(canonical, variants)
        fst = current if fst is None else fst.union(current)
    return fst if fst is not None else FST()


# Cache a nivel de modulo: los transductores se construyen una sola vez.
_TRANSDUCERS = {}


# Traduce un token a su forma canonica, o None si ningun transductor lo acepta.
def normalize_token(token):
    if not _TRANSDUCERS:
        _TRANSDUCERS.update(build_all())
    symbols = list(token.strip().casefold())
    for canonical, fst in _TRANSDUCERS.items():
        # translate() ejecuta el FST sobre los caracteres del token
        for output in fst.translate(symbols):
            if output:
                return output[0]
    return None


# Exporta un diagrama Graphviz (.dot) por transductor, y .png si "dot" esta instalado.
# Es la representacion grafica que pide el enunciado.
def export_diagrams(dest_dir, canonicals=None):
    destination = Path(dest_dir)
    destination.mkdir(parents=True, exist_ok=True)
    transducers = build_all()
    if canonicals is not None:
        transducers = {c: transducers[c] for c in canonicals if c in transducers}

    dot_binary = shutil.which("dot")
    written = []
    for canonical, fst in transducers.items():
        dot_path = destination / f"{canonical}.dot"
        fst.write_as_dot(str(dot_path))
        written.append(dot_path)
        if dot_binary:
            png_path = destination / f"{canonical}.png"
            subprocess.run([dot_binary, "-Tpng", str(dot_path), "-o", str(png_path)], check=False)
            if png_path.exists():
                written.append(png_path)
    return written
