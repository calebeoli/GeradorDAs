import streamlit as st
from datetime import datetime
from Pages.UploadDocs import loading_orgao
import os
import io
import glob
from pypdf import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib.colors import black
from reportlab.lib.utils import ImageReader
from reportlab.lib.colors import black, HexColor
import base64


df = loading_orgao()

try:
    # Cabeçalho da página de visualização
    st.title("📄 Prévia e Geração")
    st.markdown("Confira como ficará o cabeçalho e o sumário do seu documento antes de gerar o arquivo final.")
    st.write("")
        
    # 1. Pegamos os valores do session_state garantindo que não fiquem nulos
    processo = st.session_state.num_processo if st.session_state.num_processo else " "
    desc = st.session_state.desc_processo if st.session_state.desc_processo else " "
    ref = st.session_state.ref_planejamento if st.session_state.ref_planejamento else " "
    na_num = st.session_state.NA if st.session_state.NA else " "
    jurisdicionados = st.session_state.jurisdicionados if st.session_state.jurisdicionados else " "
    lotacao = df.loc[df['SIGLA_ORGAO'] == st.session_state.lotacao_usuario, 'ORGAO_SELECIONADO'].iloc[0]
    Secretaria = df.loc[df['SIGLA_ORGAO'] == st.session_state.lotacao_usuario, 'ORGAO_SUPERIOR'].iloc[0]
    Barramento = st.session_state.num_barramento if st.session_state.num_barramento else " "
        
    # Pegando as variáveis novas que você adicionou:
    num_da = st.session_state.Num_DA if st.session_state.Num_DA else " "
    desc_titulo = st.session_state.Desc_titulo if st.session_state.Desc_titulo else " "
    coordenador = st.session_state.Coordenador if st.session_state.Coordenador else " "
    revisor = st.session_state.Revisor if st.session_state.Revisor else " "

    campos_opcionais_tabela = {
        "jurisdicionados": "Jurisdicionados",
        "NA": "NA nº",
        "ref_planejamento": "Referência do planejamento",
        "num_barramento":"Nº Processo barramento"
    }

    cabecalho = "" # Inicia a variável vazia

    for chave, rotulo in campos_opcionais_tabela.items():
        valor_salvo = st.session_state.get(chave)
        valor_digitado = "" if valor_salvo is None else str(valor_salvo).strip()
        if valor_digitado: 
            cabecalho += f"""<tr>
    <td style="border: 1px solid black; padding: 8px; font-weight: bold; width: 40%;">{rotulo}</td>
    <td style="border: 1px solid black; padding: 8px;">{valor_digitado}</td>
    </tr>
    """
    # 2. Construímos as linhas do sumário dinamicamente
    linhas_sumario = ""
    # O preview agora olha APENAS para os nomes que salvamos, e não para os arquivos deletados
    if "nomes_para_preview" in st.session_state and len(st.session_state.nomes_para_preview) > 0:
        for nome_completo in st.session_state.nomes_para_preview:
            nome_original = nome_completo.split(".")[0]
            nome_final = st.session_state.cofre_nomes.get(nome_completo, nome_original)

            # Injetamos na tabela
            linhas_sumario += f"""<tr>
    <td style="border: 1px solid black; padding: 5px;">{nome_final}</td>
    <td style="border: 1px solid black; padding: 5px; text-align: center;">-- / --</td>
    </tr>"""
    else:
        # Tabela de exemplo (cai aqui apenas se realmente não houver nada)
        linhas_sumario = """<tr>
    <td style="border: 1px solid black; padding: 5px;">arquivo_exemplo_1.pdf</td>
    <td style="border: 1px solid black; padding: 5px; text-align: center;">1 / 3</td>
    </tr>
    <tr>
    <td style="border: 1px solid black; padding: 5px;">arquivo_exemplo_2.pdf</td>
    <td style="border: 1px solid black; padding: 5px; text-align: center;">4 / 5</td>
    </tr>"""

    # 3. Renderiza o HTML dentro do Streamlit
    st.markdown(f"""
    <div style="border: 1px solid #ccc; padding: 40px; font-family: 'Arial', sans-serif; background-color: white; color: black; max-width: 800px; margin: auto; box-shadow: 2px 2px 10px rgba(0,0,0,0.1);">
    <div style="display: flex; align-items: center; margin-bottom: 40px;">
    <div style="margin-right: 15px; font-weight: 900; color: #005A9C; font-size: 22px; line-height: 1;">
    <img src="data:image/png;base64,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" alt="Ponto vermelho" />
    </div>
    <div style="line-height: 1.3;">
    <strong style="font-size: 16px;">Tribunal de Contas do Distrito Federal</strong><br>
    <span style="font-size: 13px; text-transform: uppercase;">{Secretaria}</span><br>
    <span style="font-size: 12px; text-transform: uppercase;">{lotacao}</span>
    </div>
    </div>
    <table style="width: 100%; border-collapse: collapse; margin-bottom: 30px; font-size: 14px;">
    <tr>
    <td style="border: 1px solid black; padding: 8px; font-weight: bold; width: 40%;">Processo nº {processo}</td>
    <td style="border: 1px solid black; padding: 8px;">{desc}</td>
    </tr>
    {cabecalho}
    </table>
    <h3 style="text-align: center; margin-bottom: 20px; font-size: 18px;">
    Documento de Auditoria DA nº {num_da} - {desc_titulo if desc_titulo.strip() else 'Descrição a definir'}
    </h3>
    <table style="width: 100%; border-collapse: collapse; margin-bottom: 80px; font-size: 14px;">
    <tr style="background-color: #d8e4d8;">
    <td colspan="2" style="border: 1px solid black; padding: 8px; text-align: center; font-weight: bold;">Sumário</td>
    </tr>
    <tr style="background-color: #d8e4d8;">
    <td style="border: 1px solid black; padding: 8px; text-align: center; font-weight: bold;">Descrição</td>
    <td style="border: 1px solid black; padding: 8px; text-align: center; font-weight: bold; width: 15%;">Páginas</td>
    </tr>
    {linhas_sumario}
    </table>
    <div style="display: flex; justify-content: space-between; font-size: 12px; margin-top: 50px;">
    <div>
    Elaborado por: {coordenador}<br>
    Data: {datetime.now().strftime("%d/%m/%Y")}
    </div>
    <div>
    Revisado por: {revisor}
    </div>
    </div>
    </div>
    """, unsafe_allow_html=True)

    st.divider()

    # Layout de colunas para os botões nas extremidades
    col_voltar, col_vazia, col_next_button = st.columns([1, 4, 1])

    with col_voltar:
        if st.button("⬅️ Voltar", use_container_width=True):
            st.switch_page("Pages/Form.py")

    with col_next_button:
        if st.button("Gerar DA ➡️", type="primary", use_container_width=True):
            
            if "lista_arquivos" not in st.session_state or len(st.session_state.lista_arquivos) == 0:
                st.error("Erro: Nenhum arquivo PDF encontrado. Volte e faça o upload.")
            else:
                with st.spinner("⏳ Processando e unificando o Documento de Auditoria..."):
                    # ------------------------------------------------------------------
                    # CONFIGURAÇÕES ORIGINAIS DO SEU UNIFICADO.PY
                    # ------------------------------------------------------------------
                    logo = "data:image/png;base64,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"
                    info_processo = processo
                    info_tecnica = desc
                    info_referencia = ref
                    info_tempo = jurisdicionados
                    desc_Titulo = desc_titulo
                    Num_DA = num_da
                    Num_barramento = Barramento
                    Nome_cod = coordenador
                    Nome_revisor = revisor
                    data = datetime.now().strftime("%d/%m/%Y")
                    
                    def criar_capa(buffer_saida, descricao):
                        c = canvas.Canvas(buffer_saida, pagesize=A4)
                        largura, altura = A4
                        c.setStrokeColor(black)
                        c.setLineWidth(1)
                        c.rect(1 * cm, 1 * cm, largura - 2 * cm, altura - 2 * cm)
                        c.setFont("Helvetica-Bold", 20)
                        titulo = f"{descricao}"
                        c.drawCentredString(largura / 2, altura / 2, titulo)
                        c.save()

                    def criar_sumario(buffer_saida, itens_sumario, logo_b64):
                        c = canvas.Canvas(buffer_saida, pagesize=A4)
                        largura, altura = A4
                        margem_esq = 2 * cm
                        topo_y = altura - 3 * cm

                        def desenhar_rodape_e_bordas(ultima_pagina = False):

                            
                            c.setStrokeColor(black)
                            c.setLineWidth(1)
                            c.rect(1 * cm, 1 * cm, largura - 2 * cm, altura - 2 * cm) 
                            if ultima_pagina:
                                y_rodape = 1.5 * cm
                                c.setFont("Helvetica", 10)
                                c.drawString(margem_esq, y_rodape + 12, f"Elaborado por: {Nome_cod}")
                                c.drawString(margem_esq, y_rodape, f"Data: {data}")
                                margem_dir = largura - margem_esq 
                                c.drawRightString(margem_dir, y_rodape + 12, f"Revisado por: {Nome_revisor}")
                        if logo_b64:
                            try:
                                if "base64," in logo_b64:
                                    base64_data = logo_b64.split("base64,")[1]
                                else:
                                    base64_data = logo_b64
                                img_bytes = base64.b64decode(base64_data)
                                img_buffer = io.BytesIO(img_bytes)
                                logo_img = ImageReader(img_buffer)
                                c.drawImage(logo_img, margem_esq, topo_y - 1*cm, width=1.5*cm, height=1.5*cm, mask='auto')
                            except Exception as e:
                                print(f"Erro ao inserir logo Base64: {e}") 
                        
                        texto_x = margem_esq + 2 * cm
                        c.setFont("Helvetica-Bold", 12)
                        c.drawString(texto_x, topo_y, "Tribunal de Contas do Distrito Federal")
                        c.setFont("Helvetica", 10)
                        c.drawString(texto_x, topo_y - 15, Secretaria)
                        c.drawString(texto_x, topo_y - 30, lotacao)

                        y_tabela = topo_y - 2.5 * cm
                        altura_linha = 1 * cm
                        largura_col1 = 8 * cm
                        largura_col2 = largura - margem_esq * 2 - largura_col1

                        linhas_tabela = [
                            ("Processo nº", info_processo),
                            ("Descrição da ficalização:", info_tecnica)
                        ]
                        
                        # Adiciona ao PDF apenas se o campo não estiver vazio
                        if info_referencia.strip():
                            linhas_tabela.append(("Referência ao Planejamento:", info_referencia))
                            
                        if info_tempo.strip(): # jurisdicionados
                            linhas_tabela.append(("Jurisdicionados:", info_tempo))
                            
                        if na_num.strip(): # Incluído porque estava no preview Markdown
                            linhas_tabela.append(("NA nº", na_num))

                        if Num_barramento.strip(): # Incluído porque estava no preview Markdown
                            linhas_tabela.append(("Nº Processo barramento", Num_barramento))

                        # Conta dinamicamente quantas linhas teremos
                        qtd_linhas = len(linhas_tabela)

                        c.setLineWidth(1)
                        y_atual = y_tabela
                        
                        # Desenha o retângulo usando a quantidade de linhas calculada
                        c.rect(margem_esq, y_atual - (qtd_linhas * altura_linha), largura_col1 + largura_col2, qtd_linhas * altura_linha)
                        
                        for i, (col1, col2) in enumerate(linhas_tabela):
                            y_linha = y_tabela - (i * altura_linha)
                            if i > 0:
                                c.line(margem_esq, y_linha, margem_esq + largura_col1 + largura_col2, y_linha)
                            c.line(margem_esq + largura_col1, y_linha, margem_esq + largura_col1, y_linha - altura_linha)

                            c.setFont("Helvetica-Bold", 9)
                            if "\n" in col1:
                                partes = col1.split("\n")
                                c.drawString(margem_esq + 0.2*cm, y_linha - 12, partes[0])
                                c.drawString(margem_esq + 0.2*cm, y_linha - 22, partes[1])
                            else:
                                c.drawString(margem_esq + 0.2*cm, y_linha - 15, col1)
                                
                            c.setFont("Helvetica", 9)
                            c.drawString(margem_esq + largura_col1 + 0.2*cm, y_linha - 15, col2)

                        # O título do sumário também desce dinamicamente com a tabela
                        y_titulo_sumario = y_tabela - (qtd_linhas * altura_linha) - 1.5 * cm
                        c.setFont("Helvetica-Bold", 14)
                        c.drawCentredString(largura / 2, y_titulo_sumario, f"Documento de Auditoria DA nº {Num_DA} - {desc_Titulo}")
                        
                        y_sumario = y_titulo_sumario - 1.0 * cm 
                        largura_total_sumario = largura - (margem_esq * 2)
                        largura_col_desc = largura_total_sumario * 0.85 
                        largura_col_pag = largura_total_sumario * 0.15  
                        altura_linha_sum = 0.7 * cm

                        def desenhar_cabecalho_sumario(y_pos):
                            c.setFillColor(HexColor("#d9ead3")) 
                            c.rect(margem_esq, y_pos - (2 * altura_linha_sum), largura_total_sumario, 2 * altura_linha_sum, fill=1, stroke=1)
                            c.setFillColor(black) 
                            c.setFont("Helvetica-Bold", 11)
                            c.drawCentredString(largura / 2, y_pos - 0.5 * cm, "Sumário")
                            c.line(margem_esq, y_pos - altura_linha_sum, margem_esq + largura_total_sumario, y_pos - altura_linha_sum)
                            c.line(margem_esq + largura_col_desc, y_pos - altura_linha_sum, margem_esq + largura_col_desc, y_pos - (2 * altura_linha_sum))
                            c.drawCentredString(margem_esq + (largura_col_desc / 2), y_pos - altura_linha_sum - 0.5 * cm, "Descrição")
                            c.drawCentredString(margem_esq + largura_col_desc + (largura_col_pag / 2), y_pos - altura_linha_sum - 0.5 * cm, "Páginas")
                            return y_pos - (2 * altura_linha_sum)

                        y_itens = desenhar_cabecalho_sumario(y_sumario)
                        c.setFont("Helvetica", 10)
                        
                        for item in itens_sumario:
                            texto_item = f"{item['descricao']}"
                            paginas_item = f"{item['pg_inicio']} / {item['pg_fim']}" 
                            c.rect(margem_esq, y_itens - altura_linha_sum, largura_col_desc, altura_linha_sum)
                            c.rect(margem_esq + largura_col_desc, y_itens - altura_linha_sum, largura_col_pag, altura_linha_sum)
                            c.drawString(margem_esq + 0.2 * cm, y_itens - 0.5 * cm, texto_item)
                            c.drawCentredString(margem_esq + largura_col_desc + (largura_col_pag / 2), y_itens - 0.5 * cm, paginas_item)
                            y_itens -= altura_linha_sum
                            
                            if y_itens < 3.5 * cm:
                                desenhar_rodape_e_bordas() 
                                c.showPage()
                                y_itens = altura - 3 * cm
                                y_itens = desenhar_cabecalho_sumario(y_itens) 
                                c.setFont("Helvetica", 10)
                        
                        desenhar_rodape_e_bordas(ultima_pagina=True)
                        c.save()

                    arquivos_preparados = []
                    
                    # PASSAGEM 1: Gerar capas e contar as páginas de cada documento 
                    # (sem definir o número da página de início/fim ainda)
                    for arq in st.session_state.lista_arquivos:
                        nome_completo = arq.name
                        descricao = st.session_state.cofre_nomes.get(nome_completo, nome_completo.split(".")[0])
                        
                        capa_buffer = io.BytesIO()
                        criar_capa(capa_buffer, descricao)
                        capa_buffer.seek(0)
                        
                        pdf_original_buffer = io.BytesIO(arq.getvalue())
                        
                        qtd_paginas_capa = len(PdfReader(capa_buffer).pages)
                        qtd_paginas_arquivo = len(PdfReader(pdf_original_buffer).pages)
                        total_paginas_conjunto = qtd_paginas_capa + qtd_paginas_arquivo
                        
                        arquivos_preparados.append({
                            "descricao": descricao,
                            "capa_buffer": capa_buffer,
                            "pdf_buffer": pdf_original_buffer,
                            "total_paginas": total_paginas_conjunto
                        })

                    # PASSAGEM 2: Criar um sumário "Falso" só para descobrir quantas páginas ele vai ocupar
                    itens_sumario_falso = []
                    for arq in arquivos_preparados:
                        itens_sumario_falso.append({
                            "descricao": arq["descricao"],
                            "pg_inicio": 0, # Números falsos, só queremos ver o tamanho do texto
                            "pg_fim": 0
                        })
                        
                    sumario_falso_buffer = io.BytesIO()
                    criar_sumario(sumario_falso_buffer, itens_sumario_falso, logo)
                    sumario_falso_buffer.seek(0)
                    
                    # Descobre o tamanho real do sumário!
                    qtd_paginas_sumario = len(PdfReader(sumario_falso_buffer).pages)
                    
                    # PASSAGEM 3: Calcular a numeração matemática real das páginas
                    itens_sumario_reais = []
                    pagina_atual = qtd_paginas_sumario + 1 # Começa a contar logo DEPOIS do sumário
                    
                    for arq in arquivos_preparados:
                        pg_inicio = pagina_atual
                        pg_fim = pagina_atual + arq["total_paginas"] - 1
                        
                        itens_sumario_reais.append({
                            "descricao": arq["descricao"],
                            "pg_inicio": pg_inicio,
                            "pg_fim": pg_fim
                        })
                        
                        pagina_atual = pg_fim + 1 # Atualiza para o próximo documento
                        
                    # PASSAGEM 4: Criar o Sumário Real e Mesclar tudo no arquivo final
                    sumario_real_buffer = io.BytesIO()
                    criar_sumario(sumario_real_buffer, itens_sumario_reais, logo)
                    sumario_real_buffer.seek(0)
                    
                    merger = PdfWriter()
                    merger.append(sumario_real_buffer) # Adiciona o sumário verdadeiro na frente
                    
                    for arq in arquivos_preparados:
                        arq["capa_buffer"].seek(0)
                        merger.append(arq["capa_buffer"]) # Adiciona a capa
                        
                        arq["pdf_buffer"].seek(0)
                        merger.append(arq["pdf_buffer"]) # Adiciona o arquivo
                        
                    final_pdf_bytes = io.BytesIO()
                    merger.write(final_pdf_bytes)
                    merger.close()

                    # SALVANDO NA MEMÓRIA
                    st.session_state.pdf_gerado_bytes = final_pdf_bytes.getvalue()
                    st.session_state.pronto_download = True

    # VERIFICAÇÃO FORA DOS BOTÕES PARA MANTER A TELA VIVA
    if st.session_state.get("pronto_download", False) == True:
        st.success("✨ Seu Documento de Auditoria foi gerado com sucesso e está pronto para download!")
        
        # Cria um "cartão" elegante para a área de download
        with st.container(border=True):
            st.subheader("📥 Download do Arquivo Consolidado")
            col_input, col_btn = st.columns([3, 2], vertical_alignment="bottom")
            
            with col_input:
                # Define um valor padrão, mas o usuário pode apagar e escrever o que quiser
                nomeArquivo = st.text_input("Defina o nome do arquivo PDF:", value=f"DA_{num_da}")
                
            with col_btn:
                st.download_button(
                    label="Baixar Documento",
                    data=st.session_state.pdf_gerado_bytes,
                    file_name=f"{nomeArquivo}.pdf",
                    mime="application/pdf",
                    use_container_width=True,
                    type="primary" # Destaca o botão final
                )

except Exception as e:
    st.error("🚨 Ocorreu um problema ao gerar a visualização ou o documento.")
    st.info("Por favor, retorne à página inicial, verifique os arquivos enviados e tente novamente.")
    
    with st.expander("Ver detalhes técnicos do erro"):
        st.code(str(e))

    if st.button("🔄 Voltar ao Início"):
        st.switch_page("Pages/UploadDocs.py")
