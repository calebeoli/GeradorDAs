import streamlit as st

st.set_page_config(initial_sidebar_state="collapsed", page_title="Gerador de DA")


esconder_barra_lateral = """
    <style>
        /* Esconde a barra lateral inteira */
        [data-testid="stSidebar"] {
            display: none !important;
        }
        /* Esconde o botão/setinha de expandir a barra */
        [data-testid="collapsedControl"] {
            display: none !important;
        }
        /* Ajusta o espaçamento do topo para não ficar um buraco vazio */
        .block-container {
            padding-top: 2rem !important;
        }
    </style>
"""
st.markdown(esconder_barra_lateral, unsafe_allow_html=True)

pg = st.navigation([
    st.Page("Pages/UploadDocs.py",title="Inicio"),
    st.Page("Pages/Form.py",title="Formulario"),
    st.Page("Pages/pre_view.py",title="Pré visualização")
])

pg.run()