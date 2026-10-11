import pytest
from textx.exceptions import TextXSyntaxError

from resumelens.grammar import generate_candidate, validate_candidate
from resumelens.visualization import generate_markdown, save_markdown


# Texto válido que usamos como base para las pruebas.
VALID_TEXT = """
candidate "Daniel Bautista" {
    contact {
        email "daniel@example.com"
        phone "+57 300 123 4567"
        url "https://github.com/daniel"
    }
    education {
        study "Bachelor in Computer Science"
    }
    experience {
        job "3 years of experience developing web applications"
    }
    skills {
        skill JAVASCRIPT
        skill REACT
        skill NODE_JS
        skill POSTGRESQL
        skill GIT
    }
    accepted_profiles {
        profile full_stack
    }
}
"""


# Comprueba que un texto válido se convierta en un objeto.
def test_valid_candidate():
    candidate = validate_candidate(VALID_TEXT)

    assert candidate.name == "Daniel Bautista"
    assert candidate.contacts[0].kind == "email"
    assert candidate.contacts[0].value == "daniel@example.com"
    assert candidate.education[0].description == "Bachelor in Computer Science"
    assert candidate.skills[0].name == "JAVASCRIPT"
    assert candidate.profiles[0].name == "full_stack"


# Los bloques son obligatorios, pero pueden estar vacíos.
def test_empty_lists():
    text = """
    candidate "Daniel" {
        contact {}
        education {}
        experience {}
        skills {}
        accepted_profiles {}
    }
    """

    candidate = validate_candidate(text)

    assert candidate.contacts == []
    assert candidate.education == []
    assert candidate.experiences == []
    assert candidate.skills == []
    assert candidate.profiles == []


# Comprueba que se puedan guardar varios elementos por bloque.
def test_multiple_entries():
    text = """
    candidate "Daniel" {
        contact {
            email "daniel@example.com"
            email "otro@example.com"
        }
        education {
            study "Bachelor in Computer Science"
            study "Master in Data Science"
        }
        experience {
            job "2 years of experience in web development"
            job "1 year of experience in data processing"
        }
        skills {
            skill PYTHON
            skill SQL
        }
        accepted_profiles {
            profile machine_learning
            profile ai_engineer
        }
    }
    """

    candidate = validate_candidate(text)

    assert len(candidate.contacts) == 2
    assert len(candidate.education) == 2
    assert len(candidate.experiences) == 2
    assert [skill.name for skill in candidate.skills] == ["PYTHON", "SQL"]
    assert [profile.name for profile in candidate.profiles] == [
        "machine_learning",
        "ai_engineer"
    ]


# Debe rechazar un texto sin la llave final.
def test_missing_closing_brace():
    text = VALID_TEXT.strip()[:-1]

    with pytest.raises(TextXSyntaxError):
        validate_candidate(text)


# Debe rechazar un texto sin el bloque education.
def test_missing_required_block():
    text = VALID_TEXT.replace(
        'education {\n        study "Bachelor in Computer Science"\n    }',
        ""
    )

    with pytest.raises(TextXSyntaxError):
        validate_candidate(text)


# Debe rechazar los bloques en un orden diferente.
def test_wrong_block_order():
    text = """
    candidate "Daniel" {
        contact {}
        education {}
        skills {}
        experience {}
        accepted_profiles {}
    }
    """

    with pytest.raises(TextXSyntaxError):
        validate_candidate(text)


# Las habilidades deben estar escritas en mayúsculas.
def test_lowercase_skill():
    text = VALID_TEXT.replace("skill JAVASCRIPT", "skill javascript")

    with pytest.raises(TextXSyntaxError):
        validate_candidate(text)


# Solo se permiten los cuatro perfiles definidos.
def test_unknown_profile():
    text = VALID_TEXT.replace("profile full_stack", "profile doctor")

    with pytest.raises(TextXSyntaxError):
        validate_candidate(text)


# Solo se permiten email, phone y url como tipos de contacto.
def test_invalid_contact_kind():
    text = VALID_TEXT.replace(
        'email "daniel@example.com"',
        'fax "123456"'
    )

    with pytest.raises(TextXSyntaxError):
        validate_candidate(text)


# El nombre debe estar entre comillas.
def test_name_without_quotes():
    text = VALID_TEXT.replace(
        'candidate "Daniel Bautista"',
        "candidate Daniel"
    )

    with pytest.raises(TextXSyntaxError):
        validate_candidate(text)


# Comprueba la conexión entre el generador y el validador.
def test_generator_only_includes_accepted_profiles():
    data = {
        "name": "Daniel Bautista",
        "emails": ["daniel@example.com"],
        "phones": [],
        "urls": [],
        "academic_qualifications": ["Bachelor in Computer Science"],
        "professional_experience": ["3 years of experience"]
    }

    normalized = {
        "canonical": [
            "JAVASCRIPT",
            "REACT",
            "NODE_JS",
            "POSTGRESQL",
            "GIT"
        ]
    }

    results = {
        "full_stack": {"result": "ACCEPTED"},
        "machine_learning": {"result": "REJECTED"},
        "ai_engineer": {"result": "REJECTED"},
        "cloud_engineer": {"result": "REJECTED"}
    }

    text = generate_candidate(data, normalized, results)
    candidate = validate_candidate(text)

    assert candidate.name == data["name"]
    assert candidate.contacts[0].value == data["emails"][0]
    assert candidate.education[0].description == data["academic_qualifications"][0]
    assert candidate.experiences[0].description == data["professional_experience"][0]

    assert [skill.name for skill in candidate.skills] == normalized["canonical"]
    assert [profile.name for profile in candidate.profiles] == ["full_stack"]


# Comprueba que las comillas internas no rompan el texto generado.
def test_generator_escapes_quotes():
    data = {
        "name": 'Daniel "Danny" Bautista',
        "emails": [],
        "phones": [],
        "urls": [],
        "academic_qualifications": [],
        "professional_experience": ['Experience in "web" development']
    }

    normalized = {"canonical": []}

    text = generate_candidate(data, normalized, {})
    candidate = validate_candidate(text)

    assert candidate.name == data["name"]
    assert candidate.experiences[0].description == data["professional_experience"][0]
    assert candidate.profiles == []


# Comprueba que la ficha incluya los datos del objeto validado.
def test_markdown_output():
    candidate = validate_candidate(VALID_TEXT)
    markdown = generate_markdown(candidate)

    assert "# Daniel Bautista" in markdown
    assert "daniel@example.com" in markdown
    assert "+57 300 123 4567" in markdown
    assert "https://github.com/daniel" in markdown
    assert "Bachelor in Computer Science" in markdown
    assert "3 years of experience developing web applications" in markdown
    assert "JAVASCRIPT" in markdown
    assert "Full Stack Developer" in markdown


# tmp_path es una carpeta temporal que pytest crea para esta prueba.
def test_save_markdown(tmp_path):
    candidate = validate_candidate(VALID_TEXT)
    markdown = generate_markdown(candidate)

    path = tmp_path / "candidate.md"
    save_markdown(markdown, path)

    assert path.exists()
    assert path.read_text(encoding="utf-8") == markdown