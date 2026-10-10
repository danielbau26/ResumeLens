import json


def generate_candidate(data, normalized, results):

    # Pone el texto entre comillas y escapa comillas internas.
    def quote(value):
        return json.dumps(value, ensure_ascii=False)

    lines = ["candidate " + quote(data["name"]) + " {","    contact {"]

    # Contactos extraídos en la etapa 1.
    contact_categories = {
        "emails": "email",
        "phones": "phone",
        "urls": "url"
    }

    # Recorre las categorías de contacto
    for category in contact_categories:

        # Obtiene la palabra que se usa en el lenguaje: "email", "phone" o "url".
        kind = contact_categories[category]

        # Obtiene la lista de contactos de esa categoría extraídos en la etapa 1
        values = data[category]

        # Recorre cada contacto de la lista
        for value in values:

            # Pone el contacto entre comillas y escapa las comillas internas
            quoted_value = quote(value)

            # Construye la línea, por ejemplo: email "daniel@example.com".
            # Los espacios iniciales son la sangría para que el texto quede ordenado
            line = "        " + kind + " " + quoted_value

            # Agrega la línea a la lista que forma el texto del candidato.
            lines.append(line)


    lines.append("    }")

    # Estudios extraídos en la etapa 1.
    lines.append("    education {")

    for study in data["academic_qualifications"]:
        lines.append("        study " + quote(study))

    lines.append("    }")

    # Experiencias extraídas en la etapa 1.
    lines.append("    experience {")

    for experience in data["professional_experience"]:
        lines.append("        job " + quote(experience))

    lines.append("    }")

    # Habilidades normalizadas en la etapa 2.
    lines.append("    skills {")

    for skill in normalized["canonical"]:
        lines.append("        skill " + skill)

    lines.append("    }")

    # Solo los perfiles aceptados en la etapa 3.
    lines.append("    accepted_profiles {")

    for profile_key in results:
        if results[profile_key]["result"] == "ACCEPTED":
            lines.append("        profile " + profile_key)

    lines.append("    }")
    lines.append("}")

    #une todas las lineas de la lista
    #Ejmeplo:
    '''
    candidate "Wednesday Addams" {
        contact {
            email "wednesday@example.com"
            phone "+57 300 123 4567"
            url "https://github.com/wednesday"
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
    '''
    return "\n".join(lines)