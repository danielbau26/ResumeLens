import streamlit as st
from textx.exceptions import TextXSyntaxError

from resumelens.extraction import extract_info, get_skills
from resumelens.normalization import normalize
from resumelens.recognition import recognize
from resumelens.grammar import generate_candidate, validate_candidate
from resumelens.visualization import generate_markdown


# Configura la ventana de la aplicación.
st.set_page_config(
    page_title="ResumeLens",
    page_icon="https://play-lh.googleusercontent.com/QlnSSg4CYOsocZBeUEBoSzgnZUlbTDX84P8WUekDxJP-pTNL42kijyloe51HFqPWSR4iVhWJsd5jVgU2hFj84Q",
    layout="centered"
)

st.title("ResumeLens")
st.write("Check a resume and see which job profiles it matches.")

# Permite elegir cómo ingresar la hoja de vida.
input_method = st.radio(
    "How do you want to add your resume?",
    ["Paste text", "Upload a file"]
)

text = ""

if input_method == "Paste text":
    # Guarda el texto que escribe o pega el usuario.
    text = st.text_area(
        "Resume text",
        height=300,
        placeholder="Write the candidate's name on the first line."
    )

else:
    # Permite subir un archivo de texto.
    uploaded_file = st.file_uploader(
        "Choose a resume file (.txt)",
        type=["txt"]
    )

    if uploaded_file is not None:
        try:
            # Convierte los bytes del archivo en texto.
            text = uploaded_file.getvalue().decode("utf-8-sig")
            st.text_area("File content", value=text, height=300)

        except UnicodeDecodeError:
            st.error("Please save the file using UTF-8 encoding.")


# Ejecuta las cuatro etapas cuando el usuario pulsa el botón.
if st.button("Analyze", type="primary"):
    if not text.strip():
        st.warning("Please paste a resume or upload a file first.")

    else:
        try:
            # Etapa 1: extrae los datos y reúne las habilidades.
            data = extract_info(text)
            skills = get_skills(data)

            # Etapa 2: normaliza y ordena las habilidades.
            normalized = normalize(skills)

            # Etapa 3: comprueba los perfiles del candidato.
            results = recognize(normalized["by_profile"])

            # Etapa 4: genera y valida el perfil estructurado.
            candidate_text = generate_candidate(data, normalized, results)
            candidate = validate_candidate(candidate_text)

            # Genera la ficha usando el candidato validado.
            markdown = generate_markdown(candidate)

            st.success("Candidate profile created and validated.")

            # Muestra los resultados de los cuatro perfiles.
            st.subheader("Profile results")

            for profile_key in results:
                profile_result = results[profile_key]
                name = profile_result["profile"]

                if profile_result["result"] == "ACCEPTED":
                    st.success(name + ": ACCEPTED")
                else:
                    st.info(name + ": REJECTED")

            # Muestra la ficha Markdown en la interfaz.
            st.subheader("Candidate summary")
            st.markdown(markdown)

            # Permite descargar la ficha sin abrir VS Code.
            st.download_button(
                label="Download summary (Markdown)",
                data=markdown,
                file_name="candidate.md",
                mime="text/markdown"
            )

            # Permite revisar el texto que validó textX.
            with st.expander("View structured profile"):
                st.code(candidate_text, language="text")

        except TextXSyntaxError as error:
            st.error("The candidate profile does not follow the grammar rules.")
            st.code(str(error))

        except Exception as error:
            st.error("Could not complete the analysis.")
            st.code(str(error))