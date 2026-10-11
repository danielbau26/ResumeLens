

def generate_markdown(candidate):
    # Lista donde se construye la ficha del candidato.
    lines = [
        "# " + candidate.name,
        "",
        "## Contacto",
        ""
    ]

    # Agrega los contactos del candidato.
    for contact in candidate.contacts:
        line = "- " + contact.kind + ": " + contact.value
        lines.append(line)

    # Agrega los estudios.
    lines.append("")
    lines.append("## Formación académica")
    lines.append("")

    for study in candidate.education:
        lines.append("- " + study.description)

    # Agrega las experiencias.
    lines.append("")
    lines.append("## Experiencia")
    lines.append("")

    for experience in candidate.experiences:
        lines.append("- " + experience.description)

    # Agrega las habilidades normalizadas.
    lines.append("")
    lines.append("## Habilidades")
    lines.append("")

    for skill in candidate.skills:
        lines.append("- " + skill.name)

    # Relaciona las claves de los perfiles con sus nombres.
    profile_names = {
        "full_stack": "Full Stack Developer",
        "machine_learning": "Machine Learning Engineer",
        "ai_engineer": "AI Engineer",
        "cloud_engineer": "Cloud Engineer"
    }

    # Agrega los perfiles aceptados.
    lines.append("")
    lines.append("## Perfiles aceptados")
    lines.append("")

    if candidate.profiles:
        for profile in candidate.profiles:
            name = profile_names[profile.name]
            lines.append("- " + name)
    else:
        lines.append("Ningún perfil aceptado.")

    # Une las líneas y devuelve la ficha como un string.
    return "\n".join(lines)


def save_markdown(text, path):
    # Guarda la ficha en un archivo Markdown.
    with open(path, "w", encoding="utf-8") as file:
        file.write(text)