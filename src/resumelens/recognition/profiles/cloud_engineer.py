# Etapa 3 - Patron del perfil Cloud Engineer (definido por el equipo).
# Nube -> Contenedores -> Infraestructura como codigo -> [CI/CD]
# -> Sistema operativo y scripting -> [Base de datos] -> Git.
# CI/CD y base de datos son opcionales.
 
PROFILE = {
    "name": "Cloud Engineer",
    "groups": [
        {"name": "Cloud platform", "symbols": ["AWS", "AZURE", "GCP"], "optional": False},
        {"name": "Containers", "symbols": ["DOCKER", "KUBERNETES", "HELM"], "optional": False},
        {"name": "Infrastructure as code", "symbols": ["TERRAFORM", "ANSIBLE"], "optional": False},
        {"name": "CI/CD", "symbols": ["JENKINS", "GITHUB", "GITLAB"], "optional": True},
        {"name": "OS & scripting", "symbols": ["LINUX", "PYTHON", "GO"], "optional": False},
        {"name": "Database", "symbols": ["POSTGRESQL", "MYSQL", "MONGODB", "REDIS", "SQL"], "optional": True},
        {"name": "Version control", "symbols": ["GIT"], "optional": False},
    ],
    "extras": [],
}
 