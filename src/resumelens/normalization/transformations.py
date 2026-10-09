# Etapa 2 - Tabla de transformaciones.
# A la izquierda esta la forma canonica: el nombre "oficial" que escribe el transductor.
# A la derecha estan las variantes: las formas en que puede venir escrito en la hoja
# de vida, en minuscula (el texto se pasa a minuscula antes de traducir, asi
# "JS", "js" y "Js" son la misma entrada).
#
# Cada fila de este diccionario se convierte en UN transductor (ver transducers.py).

VARIANTS = {
    #  lenguajes
    "JAVASCRIPT": ["js", "javascript"],
    "TYPESCRIPT": ["ts", "typescript"],
    "PYTHON": ["python"],
    "JAVA": ["java"],
    "CPP": ["c++"],
    "CSHARP": ["c#"],
    "GO": ["golang"],
    "RUBY": ["ruby"],
    "PHP": ["php"],
    "KOTLIN": ["kotlin"],
    "SWIFT": ["swift"],
    "RUST": ["rust"],
    "SCALA": ["scala"],
    "BASH": ["bash"],

    #  frontend
    "REACT": ["react", "react.js", "reactjs"],
    "ANGULAR": ["angular"],
    "VUE": ["vue", "vue.js", "vuejs"],

    #backend
    "NODE_JS": ["node", "node.js", "nodejs"],
    "EXPRESS": ["express"],
    "DJANGO": ["django"],
    "FLASK": ["flask"],
    "FASTAPI": ["fastapi"],
    "SPRING_BOOT": ["spring boot", "springboot"],
    "REST_API": ["rest api", "rest apis", "restapi", "restapis"],
    "GRAPHQL": ["graphql"],

    # datos y machine learning
    "PANDAS": ["pandas"],
    "NUMPY": ["numpy"],
    "SCIKIT_LEARN": ["scikit-learn", "scikit learn", "scikitlearn", "sklearn"],
    "TENSORFLOW": ["tensorflow", "tensor flow"],
    "PYTORCH": ["pytorch", "py torch"],
    "KERAS": ["keras"],
    "SPARK": ["spark", "pyspark"],
    "HUGGING_FACE": ["hugging face", "huggingface"],

    # bases de datos
    "POSTGRESQL": ["postgres", "postgresql"],
    "MYSQL": ["mysql"],
    "SQLITE": ["sqlite"],
    "MONGODB": ["mongodb", "mongo"],
    "REDIS": ["redis"],
    "ORACLE": ["oracle"],
    "NOSQL": ["nosql"],
    "SQL": ["sql"],

    #  herramientas y nube
    "GIT": ["git"],
    "GITHUB": ["github"],
    "GITLAB": ["gitlab"],
    "DOCKER": ["docker"],
    "KUBERNETES": ["kubernetes", "k8s"],
    "HELM": ["helm"],
    "JENKINS": ["jenkins"],
    "TERRAFORM": ["terraform"],
    "ANSIBLE": ["ansible"],
    "AWS": ["aws"],
    "AZURE": ["azure"],
    "GCP": ["gcp"],
    "LINUX": ["linux"],
}
