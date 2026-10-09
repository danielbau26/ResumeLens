# Stage 2 - Transformation catalogue (our own transformations).
# The same qualification is written in many ways across résumés
# (JS / Javascript / JavaScript). This dictionary maps each canonical form
# to the surface variants that must become it. These canonical symbols are
# the output alphabet of the finite-state transducers built in transducers.py.
#
# TRANSFORMATIONS[canonical] = [variants...]   (UPPER_SNAKE canonical -> surface forms)

TRANSFORMATIONS = {
    # programming languages
    "JAVASCRIPT": ["JavaScript", "Javascript", "JS"],
    "TYPESCRIPT": ["TypeScript", "TS"],
    "PYTHON": ["Python", "Py"],
    "JAVA": ["Java"],
    "CPP": ["C++"],
    "CSHARP": ["C#"],
    "GO": ["Go", "Golang"],
    "RUBY": ["Ruby"],
    "PHP": ["PHP"],
    "KOTLIN": ["Kotlin"],
    "SWIFT": ["Swift"],

    # frameworks and libraries
    "REACT": ["React", "React.js", "ReactJS"],
    "ANGULAR": ["Angular"],
    "VUE": ["Vue", "Vue.js", "VueJS"],
    "NODE_JS": ["NodeJS", "Node.js", "Node"],
    "DJANGO": ["Django"],
    "FLASK": ["Flask"],
    "FASTAPI": ["FastAPI"],
    "SPRING_BOOT": ["Spring Boot", "SpringBoot", "Spring"],
    "EXPRESS": ["Express", "Express.js", "ExpressJS"],
    "PANDAS": ["Pandas", "pandas"],
    "NUMPY": ["NumPy", "Numpy"],
    "SCIKIT_LEARN": ["Scikit-learn", "scikit learn", "sklearn"],
    "TENSORFLOW": ["TensorFlow", "Tensor Flow"],
    "PYTORCH": ["PyTorch", "Py Torch"],
    "KERAS": ["Keras"],
    "SPARK": ["Apache Spark", "PySpark", "Spark"],
    "HUGGING_FACE": ["Hugging Face", "HuggingFace"],

    # databases
    "POSTGRESQL": ["PostgreSQL", "Postgres"],
    "MYSQL": ["MySQL"],
    "MARIADB": ["MariaDB"],
    "SQLITE": ["SQLite"],
    "MONGODB": ["MongoDB", "Mongo"],
    "REDIS": ["Redis"],
    "NOSQL": ["NoSQL"],
    "SQL": ["SQL"],

    # tools and technologies
    "GIT": ["Git"],
    "GITHUB": ["GitHub"],
    "GITLAB": ["GitLab"],
    "DOCKER": ["Docker"],
    "KUBERNETES": ["Kubernetes", "K8s"],
    "JENKINS": ["Jenkins"],
    "TERRAFORM": ["Terraform"],
    "ANSIBLE": ["Ansible"],
    "HELM": ["Helm"],
    "AWS": ["AWS", "Amazon Web Services"],
    "AZURE": ["Azure"],
    "GCP": ["GCP", "Google Cloud"],
    "REST_API": ["REST API", "REST APIs", "REST"],
    "GRAPHQL": ["GraphQL"],
    "LINUX": ["Linux"],
}


# Returns the list of canonical output symbols (the output alphabet).
def canonical_forms():
    return list(TRANSFORMATIONS)
