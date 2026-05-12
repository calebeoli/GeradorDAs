import streamlit as st
import pandas as pd
import pdfkit
import os
import io # <-- Importante para simular o arquivo em memória

# 0. Configuração da Página (Deixa a aba do navegador bonita)
st.set_page_config(page_title="Gerador de DA", page_icon="📄", layout="centered")

# Detecta se está rodando no Docker (Linux) ou local (Windows)
if os.name == 'nt':  # Se for Windows
    caminho_wkhtmltopdf = r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe'
else:  # Se for Linux (Docker)
    caminho_wkhtmltopdf = '/usr/bin/wkhtmltopdf'

try:
    config = pdfkit.configuration(wkhtmltopdf=caminho_wkhtmltopdf)
except Exception as e:
    st.error(f"Erro ao configurar wkhtmltopdf: {e}")

# 2. Classe auxiliar para fingir que o PDF gerado é um arquivo upado pelo usuário
class PDFEmMemoria(io.BytesIO):
    def __init__(self, buffer, name):
        super().__init__(buffer)
        self.name = name
        self.type = "application/pdf"

@st.cache_data
def loading_orgao():
    df = pd.read_csv("MAPA_ORGAO.csv",sep=",").drop(columns=["ID","fk"])
    return df

df = loading_orgao()

# 3. Inicialização do Session State
if "mensagem_toast" in st.session_state and st.session_state.mensagem_toast != "":
    st.toast(st.session_state.mensagem_toast, icon=st.session_state.icone_toast)
    st.session_state.mensagem_toast = ""

if "cofre_nomes" not in st.session_state:
    st.session_state.cofre_nomes = {}

if "lista_arquivos" not in st.session_state:
    st.session_state.lista_arquivos = []

# Cabeçalho da Aplicação
st.title("📄 Gerador de DA")
st.markdown("Faça o upload e organize seus documentos para gerar o sumário.")
st.write("") # Espaçamento

# 4. Upload de Arquivos
if len(st.session_state.lista_arquivos) == 0:
    st.info("Nenhum arquivo carregado. Por favor, adicione seus documentos abaixo.")
    Files = st.file_uploader(label="Arraste uma pasta ou escolha os arquivos", accept_multiple_files=True)
    if Files: 
        st.session_state.lista_arquivos = list(Files)
        st.rerun() # Dá um refresh na tela para sumir com o uploader
else:
    # Mostra um painel bonitinho com a quantidade de arquivos e o botão de reset
    col_info, col_reset = st.columns([3, 1], vertical_alignment="center")
    with col_info:
        st.success(f"**{len(st.session_state.lista_arquivos)}** arquivo(s) carregado(s) com sucesso!")
    with col_reset:
        if st.button("🔄 Escolher novos", use_container_width=True):
            st.session_state.lista_arquivos = []
            st.rerun()

st.divider() # Substitui o st.write("---")

# 5. Lógica de Conversão HTML
tem_html = any(arq.name.lower().endswith(".html") for arq in st.session_state.lista_arquivos)

if tem_html:
    for i in range(len(st.session_state.lista_arquivos)):
        arquivo = st.session_state.lista_arquivos[i]
        
        if arquivo.name.lower().endswith(".html"):
            try:
                try:
                    conteudo_html = arquivo.getvalue().decode("utf-8")
                except UnicodeDecodeError:
                    conteudo_html = arquivo.getvalue().decode("latin-1")
                
                with st.spinner(f"Convertendo {arquivo.name}..."):
                    if "column-headers-background" in conteudo_html.lower():
                        opcoes_pdf = {
                            'enable-local-file-access': '', 
                            'encoding': 'UTF-8',            
                            'javascript-delay': '3000',     
                            'orientation': 'Landscape',     
                            'zoom': '0.8',                  
                            'margin-top': '5mm',
                            'margin-right': '5mm',
                            'margin-bottom': '5mm',
                            'margin-left': '5mm'
                        }
                        pdf_bytes = pdfkit.from_string(conteudo_html, False, configuration=config, options=opcoes_pdf)
                        st.info(f"📊 '{arquivo.name}' foi identificado como Tabela (PDF gerado em Paisagem).")
                    else: 
                        opcoes_pdf = {
                            'enable-local-file-access': '', 
                            'encoding': 'UTF-8',            
                            'javascript-delay': '3000',
                            'orientation': 'Portrait'       
                        }
                        pdf_bytes = pdfkit.from_string(conteudo_html, False, configuration=config, options=opcoes_pdf)
                
                # Cria o objeto falso com as propriedades de arquivo
                nome_pdf = arquivo.name.replace(".html", ".pdf")
                novo_arquivo_pdf = PDFEmMemoria(pdf_bytes, nome_pdf)
                
                # Substitui o HTML pelo PDF novo na lista
                st.session_state.lista_arquivos[i] = novo_arquivo_pdf
                
            except Exception as e:
                st.error(f"Erro ao converter o arquivo {arquivo.name}: {e}")
    
    st.success("✨ Conversão concluída!")
    st.rerun() # Recarrega a tela para os arquivos passarem a ter a extensão .pdf

if tem_html: # Só plota esse divider se tiver havido bloco de conversão
    st.divider()

# 6. Organização e Renomeação dos Arquivos
if len(st.session_state.lista_arquivos) > 0:
    st.subheader("🗂️ Ordem do Sumário")
    
    for index, Arquivo in enumerate(st.session_state.lista_arquivos):
        # Utilizar um container com borda cria um efeito visual de "Cartão" muito mais limpo
        with st.container(border=True): 
            # Dividi as colunas para os botões ficarem lado a lado (4 proporções pra nome, 1 pra subir, 1 pra descer)
            col_nome, col_up, col_down = st.columns([4, 1, 1], vertical_alignment="bottom")

            with col_nome:
                # Correção de segurança: Se o nome não tiver "/", evita que o código quebre
                nome_sem_extensao = Arquivo.name.split(".")[0]
                if "/" in nome_sem_extensao:
                    nome_original = nome_sem_extensao.split("/")[1]
                else:
                    nome_original = nome_sem_extensao
                    
                sugestao_segura = st.session_state.cofre_nomes.get(Arquivo.name, nome_original)
                nome_final = st.text_input("Nome no sumário:", value=sugestao_segura, key=f"input_sumario_{Arquivo.name}")
                st.session_state.cofre_nomes[Arquivo.name] = nome_final

            with col_up:
                desativar_subir = (index == 0)
                if st.button("⬆️ Subir", key=f"btn_subir_{Arquivo.name}", use_container_width=True, disabled=desativar_subir):
                    Aux = st.session_state.lista_arquivos.pop(index)
                    st.session_state.lista_arquivos.insert(index - 1, Aux)
                    st.session_state.mensagem_toast = f"'{Arquivo.name}' movido para cima!"
                    st.session_state.icone_toast = "⬆️"
                    st.rerun()

            with col_down:
                desativar_descer = (index == len(st.session_state.lista_arquivos) - 1)
                if st.button("⬇️ Descer", key=f"btn_descer_{Arquivo.name}", use_container_width=True, disabled=desativar_descer):
                    Aux = st.session_state.lista_arquivos.pop(index)
                    st.session_state.lista_arquivos.insert(index + 1, Aux)
                    st.session_state.mensagem_toast = f"'{Arquivo.name}' movido para baixo!"
                    st.session_state.icone_toast = "⬇️"
                    st.rerun()

    st.write("") # Pequeno respiro antes do botão final
    
    # Botão de avançar com destaque visual (type="primary")
    col_vazia, col_next_button = st.columns([3, 1])
    with col_next_button:
        if st.button("Ver prévia ➡️", type="primary", use_container_width=True):
            st.switch_page("Pages/Form.py")