# Etapa 3 - Patron del perfil AI Engineer (definido por el equipo).
# Python -> Datos -> ML/Deep learning -> Big data e IA generativa -> [Base de datos]
# -> Despliegue -> Git. La base de datos es opcional.
# Se diferencia de ML Engineer porque exige Spark o Hugging Face y despliegue.
 
PROFILE = {
    "name": "AI Engineer",
    "groups": [
        {"name": "Language", "symbols": ["PYTHON"], "optional": False},
        {"name": "Data processing", "symbols": ["PANDAS", "NUMPY"], "optional": False},
        {"name": "ML / Deep learning", "symbols": ["SCIKIT_LEARN", "TENSORFLOW", "PYTORCH", "KERAS"], "optional": False},
        {"name": "Big data & GenAI", "symbols": ["SPARK", "HUGGING_FACE"], "optional": False},
        {"name": "Database", "symbols": ["SQL", "POSTGRESQL", "MONGODB", "REDIS"], "optional": True},
        {"name": "Deployment", "symbols": ["DOCKER", "KUBERNETES", "AWS", "GCP"], "optional": False},
        {"name": "Version control", "symbols": ["GIT"], "optional": False},
    ],
    "extras": [],
}
 