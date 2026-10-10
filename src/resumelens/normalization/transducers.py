# Etapa 2 - Transductores de estado finito con pyformlang.
#
# Un transductor es como un automata, pero ademas de leer, ESCRIBE una salida.
# Aqui cada transductor lee una palabra letra por letra y escribe su forma canonica.
#
# Ejemplo: transductor de JAVASCRIPT con las variantes "js" y "javascript"
#
#   q0 --j/JAVASCRIPT--> q1 --s/ε--> q2 (final)          lee "js"
#                        q1 --a/ε--> q3 --v/ε--> ... --t/ε--> q11 (final)   lee "javascript"
#
#   - En la PRIMERA letra escribe JAVASCRIPT; en las demas no escribe nada (ε).
#   - Si dos variantes empiezan igual ("js" y "javascript" empiezan con 'j'),
#     comparten ese pedazo del camino. Por eso desde cada estado hay maximo una
#     transicion por letra: el transductor es DETERMINISTA.
#   - Si la palabra no es una variante, se queda sin camino o no termina en un
#     estado final, y translate() no devuelve nada.
import graphviz
from pyformlang.fst import FST

from .transformations import VARIANTS

# recive la forma canonica ("REACT") y sus variantes. crea las listas vacias
def build_transitions(canonical, variants):
    transitions = [] #lugar donde van las tuplas (desde, letra entrada, hacia, [salida])
    finals = [] #los estados finales
    paths = {} # un diccionario que recuerda que flechas ya existen. guarda (estado, letra) -> estado al que llega

    count = 1 # contador para nombrar los estados nuevos, arranca en 1 porque q0 ya existe

    #recorre cada variante y cada una empieza en q0.
    for word in variants:
        current = "q0"
        #recorre la palabra en variante letra por letra. enumerate da la posicion y la letra (i, letter)
        # para “react” da (0, "r"), (1, "e")
        for i, letter in enumerate(word):
            # si desde el estado actual ya existe una flecha con esa letra (en path donde guardamos las felchas)
            #solo avanza sin crear nada
            # Esto pasa con “react.js”: las letras r-e-a-c-t ya las creó “react” (otra variante), así que las reutiliza.
            if (current, letter) in paths:
                current = paths[(current, letter)]
            else:
            # si la flecha no existe la crea:
            ##arma el nombre del estado nuevo y sube el contador
                new_state = "q" + str(count)
                count += 1
                # decide la salida: si es la primera letra, escribe la canonica
                if i == 0:
                    output = canonical    # primera letra → escribe "REACT"
                else:
                    output = ""           # las demás → no escribe nada
                # y le meto la tupla ("q0", "r", "q1", ["REACT"])
                transitions.append((current, letter, new_state, [output]))
                #guardamos en paths que ese camino ya existe. y avanza al estado nuevo
                paths[(current, letter)] = new_state
                current = new_state
        # cuando termina la palabra, el estado donde quedo es final
        if current not in finals:
            finals.append(current)
    #al final devuelve las transiciones (la tupla) y los finales
    return transitions, finals

#crea el transductor. saca las variantes de esa forma canonica de la tabla y arma las transiciones
# crea el FST vacio, le mete la transiciones, marca q0 como inicial y marca cada estado final
# devuelve el transductor listo
def build_transducer(canonical):
    transitions, finals = build_transitions(canonical, VARIANTS[canonical])
    transducer = FST()
    transducer.add_transitions(transitions)
    transducer.add_start_state("q0")
    for state in finals:
        transducer.add_final_state(state)
    return transducer

# crea todos los transductores de una
#for canonical in VARIANTS: recorre las claves de la tabla: "JAVASCRIPT", "TYPESCRIPT", "REACT"...
#TRANSDUCERS[canonical] = build_transducer(canonical) crea el transductor de esa forma canónica y
# lo guarda con su nombre como clave. Al final queda {"JAVASCRIPT": FST, "TYPESCRIPT": FST, "REACT": FST, ...}.
TRANSDUCERS = {}
for canonical in VARIANTS:
    TRANSDUCERS[canonical] = build_transducer(canonical)

#traduce una palabra, recibe por eje: react.js y devuelve su forma canonica
def translate(word):
    #limpia los espacios y pasa todo a minuscula
    word = " ".join(word.split()).lower()
    # prueba la palabra en cada transductor
    # recordemos que dije que quedaba asi donde guardo los transducers. {"JAVASCRIPT": FST, "TYPESCRIPT": FST, "REACT": FST, ...}.
    # entonces canonical es la clave
    for canonical in TRANSDUCERS:
        transducer = TRANSDUCERS[canonical]
        results = []
        #transducer.translate(word) es la función de pyformlang, hace que el transductor lea la palabra letra por letra
        #Si la acepta (llega a un estado final), devuelve lo que fue escribiendo en el camino,
        #  como una lista de pedazos: ["REACT", "", "", "", "", "", "", ""]. Si no la acepta, no devuelve nada.
        #recorre lo que devolvio
        for output in transducer.translate(word):
            #join une los pedazos en un solo texto: "REACT" + "" + "" + ... = "REACT", si no lo acepto pues queda vacio
            results.append("".join(output))
        # devuelve si lo acepto
        if results:
            return results[0]
    return None

#arma la 7 tupla
def formal_definition(canonical):
    
    transitions, finals = build_transitions(canonical, VARIANTS[canonical])

    states = ["q0"]
    for start, letter, end, output in transitions:
        if end not in states:
            states.append(end)

    alphabet = []
    for start, letter, end, output in transitions:
        if letter not in alphabet:
            alphabet.append(letter)

    delta = []
    omega = []
    for start, letter, end, output in transitions:
        delta.append(f"δ({start}, '{letter}') = {end}")

        if output[0] == "":
            written = "ε"
        else:
            written = output[0]

        omega.append(f"ω({start}, '{letter}') = {written}")
        #"δ(q0, 'r') = q1" y "ω(q0, 'r') = REACT"
    return {
        "Q": states,
        "Σ": alphabet,
        "Γ": [canonical], #es solo la canonica porque es la unica salida del transductor
        "δ": delta,
        "ω": omega,
        "q0": "q0",
        "F": finals,
    }


def draw_transducer(canonical):
    transitions, finals = build_transitions(canonical, VARIANTS[canonical])
    # crea un dibujo con flechas de izquierda a derecha
    dot = graphviz.Digraph(engine="dot")
    dot.attr(rankdir="LR")
    dot.attr("node", fontname="Helvetica")

    # crea un nodo invisible y una flecha de el a q0, que es la del estado inciial
    dot.node("__init__", shape="none", label="", width="0", height="0")
    dot.edge("__init__", "q0")
    dot.node("q0", shape="circle", style="filled", fillcolor="lightblue")
    #por cada transicion: si el estado es final, lo dibuja con doble circulo
    # sino con circulo normal.
    for start, letter, end, output in transitions:
        if end in finals:
            shape = "doublecircle"
        else:
            shape = "circle"
        dot.node(end, shape=shape)
        #si la letra es un espacio se cambia por ␣ para que la flecha se vea con letra 
        if letter == " ":
            label = "␣"
        else:
            label = letter

        if output[0] == "":
            written = "ε"
        else:
            written = output[0]
        #dibuja la flecha de start a end con la etiqueta
        dot.edge(start, end, label=f" {label} / {written} ")

    return dot


def save_diagrams(folder):
    # por cada forma canonica, crea el archivo REACT.dot por ejemplo y asi con todas
    # y escribe ahi el texto del dibujo .source es ese texto en formato DOT
    for canonical in VARIANTS:
        with open(f"{folder}/{canonical}.dot", "w", encoding="utf-8") as file:
            file.write(draw_transducer(canonical).source)
