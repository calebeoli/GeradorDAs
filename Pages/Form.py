import streamlit as st
import pandas as pd
from datetime import datetime
from Pages.UploadDocs import loading_orgao

df = loading_orgao()

# Título da página melhorado
st.title("📝 Detalhes do Documento")
st.markdown("Por favor, preencha as informações do cabeçalho. Campos marcados com `*` são obrigatórios.")

campos = ["Num_DA","Desc_titulo","Coordenador","Revisor","lotacao_usuario"
          ,"num_processo", "desc_processo", "jurisdicionados", "NA", "ref_planejamento","num_barramento"]

campos_opcionais_tabela = [
    "jurisdicionados",
    "NA",
    "ref_planejamento",
    "num_barramento"
]

for campo in campos:
    if campo not in st.session_state:
        st.session_state[campo] = None

if "index_lotacao" not in st.session_state:
    st.session_state.index_lotacao = None

options = df.iloc[:,0]

# ----------------- INÍCIO DA ORGANIZAÇÃO VISUAL -----------------

# BLOCO 1: Informações da Fiscalização
with st.container(border=True):
    st.subheader("📋 Informações da Fiscalização")
    col1, col2 = st.columns(2)
    
    with col1:
        lotacao_escolhida =  st.selectbox("*Divisão:", options=options, index=st.session_state.index_lotacao, placeholder="Escolha sua lotação")
        st.session_state.lotacao_usuario = lotacao_escolhida if lotacao_escolhida is not None else st.session_state.lotacao_usuario
        if st.session_state.lotacao_usuario in options:
            st.session_state.index_lotacao = options.index(st.session_state.lotacao_usuario)
        else:
            st.session_state.index_lotacao = None

        st.session_state.num_processo = st.text_input("*Processo nº:", value=st.session_state.num_processo)
        
    with col2:
        st.session_state.desc_processo = st.text_input("*Descrição da fiscalização:", value=st.session_state.desc_processo)
        st.session_state.jurisdicionados = st.text_input("Jurisdicionados:", value=st.session_state.jurisdicionados)

# BLOCO 2: Dados do Documento
with st.container(border=True):
    st.subheader("📄 Dados do Documento")
    col3, col4 = st.columns(2)
    
    with col3:
        st.session_state.Num_DA = st.text_input("*Informe o número do DA:", value=st.session_state.Num_DA)
        st.session_state.Desc_titulo = st.text_input("*Informe Título do DA:", value=st.session_state.Desc_titulo)
        st.session_state.num_barramento = st.text_input("*Informe o número do barramento:", value=st.session_state.num_barramento)
        
    with col4:
        st.session_state.NA = st.text_input("Nota de auditoria nº:", value=st.session_state.NA)
        st.session_state.ref_planejamento = st.text_input("Referência do planejamento:", value=st.session_state.ref_planejamento)

# BLOCO 3: Responsáveis
with st.container(border=True):
    st.subheader("👥 Responsáveis")
    col5, col6 = st.columns(2)
    
    with col5:
        st.session_state.Coordenador = st.text_input("*Elaborado por:", value=st.session_state.Coordenador)
    with col6:
        st.session_state.Revisor = st.text_input("*Revisado por:", value=st.session_state.Revisor)

# ----------------- FIM DA ORGANIZAÇÃO VISUAL -----------------

campos_obrigatorios = []
for campo in campos:
    if campo not in campos_opcionais_tabela:
        campos_obrigatorios.append(campo)

desable = False 
desable = any(st.session_state[campo] in [None, ""] for campo in campos_obrigatorios)

st.divider()

# Dá um aviso visual ao usuário explicando por que o botão está bloqueado
if desable:
    st.info("⚠️ Preencha todos os campos obrigatórios (marcados com *) para liberar a próxima etapa.")

# Proporção das colunas: Botão Voltar (1) | Espaço Vazio (4) | Botão Próximo (1)
col_voltar, col_espaco, col_next = st.columns([1, 4, 1])

with col_voltar:
    if st.button("⬅️ Voltar", use_container_width=True):
        st.switch_page("Pages/UploadDocs.py")

with col_next:
    if st.button("Próximo ➡️", disabled=desable, type="primary", use_container_width=True):
        st.session_state.nomes_para_preview = [arq.name for arq in st.session_state.lista_arquivos]
        st.switch_page("Pages/pre_view.py")
