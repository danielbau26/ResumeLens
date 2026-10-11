# Stage 1 - Information extraction with regular expressions.
# Applies the regexes from patterns.py to the résumé and returns a dictionary
# with everything found. From that dictionary, get_skills() builds the list
# that stage 2 receives, and the full dictionary is used by stage 4.
import re
import json

from .patterns import PATTERNS, QUALIFICATION_CATEGORIES, EMAIL_REGEX, URL_REGEX


# Recibe el texto completo de la hoja de vida. splitlines() parte el texto en lineas
# y el for las recorre una por una. Devuelve la primera linea que si tiene texto
# (la del nombre). Si el texto esta vacio devuelve "".
def get_name(text):
    # El nombre es la primera linea con texto (lo necesita la etapa 4)
    for line in text.splitlines():
        if line.strip():
            return line.strip()
    return ""


# Funcion principal de la etapa 1. Recibe el texto del CV, aplica cada regex
# y devuelve un diccionario categoria -> lista de coincidencias sin repetir.
def extract_info(text):
    # Crea el diccionario donde se va a guardar todo y de una vez le mete el nombre
    data = {"name": get_name(text)}

    # Copia del texto sin correos ni links,
    # para que "github.com/jperez" no saque "GitHub" como herramienta.
    # re.sub(patron, reemplazo, texto) busca todo lo que cumpla el patron y lo
    # reemplaza. Aqui cambia correos y links por un espacio. El resultado es una
    # copia, el texto original no se toca.
    clean_text = re.sub(EMAIL_REGEX, " ", text)
    clean_text = re.sub(URL_REGEX, " ", clean_text, flags=re.IGNORECASE)

    # Recorre el diccionario PATTERNS. En cada vuelta, category es un nombre:
    # "emails", "phones", "urls", "programming_languages", ...
    for category in PATTERNS:
        # Saca la regex de esa categoria
        pattern = PATTERNS[category]

        # Decide en que texto buscar: correos, telefonos y links se buscan en el
        # texto ORIGINAL (en la copia limpia ya los borramos). Lo demas se busca
        # en el texto limpio. (Al telefono no se le borra nada, asi que da igual.)
        if category in ("emails", "phones", "urls"):
            source = text
        else:
            source = clean_text

        # Estudios sin IGNORECASE: esta regex depende de la mayuscula para saber
        # donde termina el nombre de la carrera (mirar ACADEMIC_REGEX).
        # Con IGNORECASE se tragaria palabras de mas: "MSc in Computer Science from the"
        if category == "academic_qualifications":
            matches = re.findall(pattern, source)
        # Lo demas normal con IGNORECASE: "JS", "js" y "Js" se detectan igual
        else:
            matches = re.findall(pattern, source, re.IGNORECASE)

        # Lista vacia donde van a quedar los resultados sin repetir
        values = []
        # Recorre cada cosa que encontro la regex
        for value in matches:
            # split() parte por espacios y join los une con uno solo,
            # asi se quitan espacios dobles o saltos de linea ("Spring   Boot" -> "Spring Boot")
            value = " ".join(value.split())
            # value tiene que tener algo.
            # [v.lower() for v in values] crea una lista con lo que ya guardamos pero en
            # minuscula. Si value.lower() no esta ahi, es nuevo. Asi Git y git cuentan
            # como lo mismo y se queda con la primera forma que aparecio.
            if value and value.lower() not in [v.lower() for v in values]:
                values.append(value)

        # Guarda la lista en el diccionario,
        # por ejemplo data["tools_technologies"] = ["Git", "Docker"]
        data[category] = values

    return data

# Ejemplo del diccionario con todas las categorias:
# {"name": "Wednesday Addams", "emails": [], ..., "databases": ["Postgres"], ...}


# Recibe el diccionario de extract_info y crea una lista vacia de habilidades.
# Junta las habilidades en una sola lista. ESTO es lo que recibe la etapa 2:
# ["JS", "React.js", "NodeJS", "Postgres", "Git"]
def get_skills(data):
    skills = []
    # Recorre solo las 4 categorias tecnicas (lenguajes, frameworks, bd, herramientas).
    # extend pega todos los elementos de una lista al final de otra; es como append
    # pero con varios elementos.
    for category in QUALIFICATION_CATEGORIES:
        skills.extend(data[category])
    return skills


# Abre el .txt (utf-8 para que las tildes se lean bien). file.read() lee todo el
# contenido como texto y se lo pasa a extract_info. El with cierra el archivo
# solo al terminar.
def extract_from_file(path):
    with open(path, encoding="utf-8") as file:
        return extract_info(file.read())


# Abre (o crea) el archivo en modo escritura ("w") y json.dump escribe el diccionario
# como JSON. indent=2 lo deja ordenado y ensure_ascii=False guarda bien las tildes.
# Cumple el "keep the extracted information in a file" del enunciado.
def save_result(data, path):
    with open(path, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=2, ensure_ascii=False)
