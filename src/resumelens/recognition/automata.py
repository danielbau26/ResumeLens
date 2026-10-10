# Stage 3 - Finite automata built with pyformlang, one per profile.
# Each group of the profile is one step: from state q(i) the automaton moves to
# q(i+1) by reading any symbol of the group, and q(i+1) has a loop with the same
# symbols in case the candidate has several of them (e.g. PANDAS and NUMPY).
# An optional group also has an ε-transition that allows skipping it.
# Extras are loops on the final state.
# A profile without optional groups is a DFA; with optional groups it is an ε-NFA.
import graphviz
from pyformlang.finite_automaton import (DeterministicFiniteAutomaton, EpsilonNFA,
                                         State, Symbol, Epsilon)
 
from .profiles import PROFILES
 
# este metodo arma las flechas del automata, como en el del transducer
def build_transitions(profile_key):
    
    profile = PROFILES[profile_key]  # name, groups y extras del perfil
    groups = profile["groups"] # saca los pasos que debe cumplir, grupo del perfil
    transitions = [] #lista de ; flechas. Cada flecha va a ser una tupla (desde, símbolo, hacia).

    # recorre los pasos, enumerate da la posicion y el paso
    for i, group in enumerate(groups):
        #para el primer paso i=0, entonces conecta q0 -> q1 ... 
        before = "q" + str(i)
        after = "q" + str(i + 1)

        #para cada palabra del paso agrega 2 flechas
        #(before, symbol, after) es la flecha que avanza. Por ejemplo, ("q1", "PANDAS", "q2").
        #(after, symbol, after) es el bucle, que sale de q2 y vuelve a q2. Por ejemplo, ("q2", "NUMPY", "q2"). 
        # Sirve para cuando el candidato tiene varias cosas del mismo paso (PANDAS y NUMPY).
        for symbol in group["symbols"]:
            transitions.append((before, symbol, after))
            transitions.append((after, symbol, after))
        # si el paso es opcional, agrega una flecha ε de la casilla de antes a la de despues, 
        # que permite pasar sin leer nada, aqui "ε", es solo un texto de marca; mas abajo en 
        # build, se cambia por Epsilon()
        if group["optional"]:
            transitions.append((before, "ε", after))
    # la casilla del final es el ultimo paso, si hay cinco estas irian de q0 a q5. 
    final = "q" + str(len(groups))
    # por cada extra que haya al final agrega un bucle en la meta
    # eje: ("q5", "DOCKER", "q5")
    for symbol in profile["extras"]:
        transitions.append((final, symbol, final))
    # Al final devuelve la lista de flechas y el nombre del estado final qx.
    return transitions, final

# decide si es DFA o ε-NFA
def automaton_type(profile_key):
    profile = PROFILES[profile_key]
    groups = profile["groups"] 
    # reocrre los pasos del perfil , apenas encuentra uno opcional, devuelve ε-NFA
    for group in groups:
        if group["optional"]:
            return "ε-NFA"
    return "DFA"

#crea el automata con pyformlang
def build_automaton(profile_key):
    # solo llamo metodos
    # me da las felchas y el nombre del estado final 
    transitions, final = build_transitions(profile_key)
    # crea el automata dependiendo del tipo 
    if automaton_type(profile_key) == "DFA":
        automaton = DeterministicFiniteAutomaton()
    else:
        automaton = EpsilonNFA()
    #Marca q0 como estado inicial y la meta como estado final.
    automaton.add_start_state(State("q0"))
    automaton.add_final_state(State(final))

    # recorre las flechas en sus tres partes, si el simbolo es "ε"
    # agrega la transicion con EPsilon(), si no con el simbolo
    # al final devuelve el automata listo.
    for start, symbol, end in transitions:
        if symbol == "ε":
            automaton.add_transition(State(start), Epsilon(), State(end))
        else:
            automaton.add_transition(State(start), Symbol(symbol), State(end))
 
    return automaton
 
#Crea los 4 autómatas una sola vez, al importar el archivo, y los guarda en un
#  diccionario: {"full_stack": autómata, "machine_learning": autómata, ...}
AUTOMATA = {}
for profile_key in PROFILES:
    AUTOMATA[profile_key] = build_automaton(profile_key)