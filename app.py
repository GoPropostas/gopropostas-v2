import base64
import io
import os
import textwrap
import zipfile
from datetime import date, datetime
from pathlib import Path
import time

import pandas as pd
import requests
import streamlit as st
from openpyxl import load_workbook
from openpyxl.styles import Alignment
from supabase import Client, create_client
import aspose.cells as cells  # Biblioteca para gerar o PDF de forma estável

st.set_page_config(
    page_title="GoPropostas V2",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="expanded",
)

LOGO_PADRAO = "logo_padrao.png"
MODELO_PROPOSTA_PADRAO = "modelo_proposta.xlsx"
MODELO_CONTRATO_PADRAO = "Contrato de Intermediação (3).xlsx"

# --- FUNÇÕES DE NÚCLEO ---

@st.cache_resource
def get_supabase() -> Client:
    return create_client(
        st.secrets["SUPABASE_URL"].strip(),
        st.secrets["SUPABASE_KEY"].strip(),
    )

def img_to_base64(path: str) -> str:
    p = Path(path)
    if not p.exists():
        return ""
    return base64.b64encode(p.read_bytes()).decode()

def excel_para_pdf(arquivo_excel):
    """Converte Excel para PDF usando Aspose.Cells (Funciona em Nuvem/Streamlit Cloud)"""
    try:
        workbook = cells.Workbook(arquivo_excel)
        arquivo_pdf = arquivo_excel.replace(".xlsx", ".pdf")
        
        save_options = cells.PdfSaveOptions()
        save_options.one_page_per_sheet = True # Garante que o conteúdo caiba na folha
        
        workbook.save(arquivo_pdf, save_options)
        return arquivo_pdf
    except Exception as e:
        st.error(f"Erro técnico na conversão para PDF: {e}")
        return None

# --- ESTILIZAÇÃO E UI ---

def aplicar_tema(imob=None):
    cor_primaria = "#0C6D84"
    cor_secundaria = "#F97316"
    bg_inicio = "#062B36"
    bg_fim = "#0A4C5B"

    if imob:
        cor_primaria = imob.get("cor_primaria") or cor_primaria
        cor_secundaria = imob.get("cor_secundaria") or cor_secundaria
        bg_inicio = imob.get("background_inicio") or bg_inicio
        bg_fim = imob.get("background_fim") or bg_fim

    st.markdown(
        f"""
<style>
.stApp {{ background: linear-gradient(180deg, {bg_inicio} 0%, {bg_fim} 100%); }}
[data-testid="stSidebar"] {{ background: linear-gradient(180deg, {bg_inicio} 0%, {bg_fim} 100%); }}
.gp-card {{ background: #F8FBFD; border-radius: 24px; padding: 22px 24px; box-shadow: 0 12px 28px rgba(0,0,0,0.16); border: 1px solid rgba(12,109,132,0.10); margin-bottom: 18px; color: #062B36 !important; }}
.gp-card * {{ color: #062B36 !important; }}
.gp-card-dark {{ background: linear-gradient(135deg, {bg_inicio} 0%, {cor_primaria} 100%); color: white; border-radius: 24px; padding: 22px 24px; margin-bottom: 18px; }}
.gp-title {{ color: #F4F7FA; font-size: 2rem; font-weight: 800; margin: 0; }}
.gp-subtitle {{ color: rgba(244,247,250,0.82); font-size: 0.98rem; }}
.stButton > button {{ background: linear-gradient(90deg, {cor_secundaria} 0%, {cor_primaria} 100%) !important; color: white !important; border-radius: 14px !important; font-weight: 800 !important; }}
</style>
        """,
        unsafe_allow_html=True,
    )

def render_topbar(imob=None):
    titulo = imob["nome"] if imob else "GoPropostas V2"
    logo_base64 = img_to_base64(LOGO_PADRAO)
    html = f"""
<div style="margin-bottom:20px;padding:18px 24px;border-radius:24px;background:rgba(255,255,255,0.06);display:flex;align-items:center;gap:18px;">
    {"<img src='data:image/png;base64," + logo_base64 + "' style='max-height:78px;' />" if logo_base64 else ""}
    <div><div class="gp-title">{titulo}</div><div class="gp-subtitle">Sistema de Propostas Imobiliárias</div></div>
</div>
"""
    st.markdown(textwrap.dedent(html), unsafe_allow_html=True)

# --- GESTÃO DE ESTADO E AUTH ---

def init_state():
    defaults = {
        "logado": False, "usuario_id": "", "usuario_email": "", "usuario_nome": "",
        "role_global": "usuario", "sb_access_token": "", "sb_refresh_token": "",
        "imobiliaria_id": "", "imobiliaria_nome": "", "cargo_imobiliaria": "", "status_vinculo": ""
    }
    for k, v in defaults.items():
        if k not in st.session_state: st.session_state[k] = v

def logout():
    if st.sidebar.button("🚪 Sair", use_container_width=True):
        for k in list(st.session_state.keys()): del st.session_state[k]
        st.rerun()

# --- BANCO DE DADOS (SUPABASE) ---

def buscar_profile_por_id(user_id: str):
    resp = get_supabase().table("profiles").select("*").eq("id", user_id).limit(1).execute()
    return resp.data[0] if resp.data else None

def listar_imobiliarias_ativas():
    resp = get_supabase().table("imobiliarias").select("*").eq("ativa", True).order("nome").execute()
    return resp.data or []

def buscar_imobiliaria_por_id(imobiliaria_id: str):
    resp = get_supabase().table("imobiliarias").select("*").eq("id", imobiliaria_id).limit(1).execute()
    return resp.data[0] if resp.data else None

def buscar_regra_imobiliaria(imobiliaria_id: str):
    resp = get_supabase().table("regras_imobiliaria").select("*").eq("imobiliaria_id", imobiliaria_id).eq("ativo", True).order("created_at", desc=True).limit(1).execute()
    return resp.data[0] if resp.data else None

def listar_empreendimentos():
    resp = get_supabase().table("empreendimentos").select("*").eq("ativo", True).order("nome").execute()
    return resp.data or []

# --- LÓGICA DE NEGÓCIO / CÁLCULOS ---

@st.cache_data
def carregar_tabela(arquivo, mod_time):
    df = pd.read_excel(arquivo, skiprows=11)
    df.columns = df.columns.str.strip().str.lower()
    return df

def limpar(valor):
    if pd.isna(valor): return 0.0
    if isinstance(valor, (int, float)): return float(valor)
    texto = str(valor).replace("R$", "").replace(".", "").replace(",", ".")
    try: return float(texto)
    except: return 0.0

def buscar(linha, nomes):
    for col in linha.index:
        for nome in nomes:
            if nome.lower() in col.lower(): return limpar(linha[col])
    return 0.0

def calcular_idade_em_data(nascimento: date, data_referencia: date) -> int:
    return data_referencia.year - nascimento.year - ((data_referencia.month, data_referencia.day) < (nascimento.month, nascimento.day))

def adicionar_meses(data_base: date, meses: int) -> date:
    ano = data_base.year + (data_base.month - 1 + meses) // 12
    mes = (data_base.month - 1 + meses) % 12 + 1
    dia = min(data_base.day, 28) # Simplificado para evitar erro de dia inexistente
    return date(ano, mes, dia)

def formatar_moeda(valor: float) -> str:
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

def criar_zip_bytes(arquivos):
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as zf:
        for arquivo in arquivos:
            if arquivo and os.path.exists(arquivo):
                zf.write(arquivo, arcname=os.path.basename(arquivo))
                os.remove(arquivo) # Limpa o servidor após zipar
    buffer.seek(0)
    return buffer.getvalue()

# --- GERADORES DE DOCUMENTOS ---

def preencher_proposta(d, modelo=MODELO_PROPOSTA_PADRAO):
    wb = load_workbook(modelo)
    ws = wb.active
    # Mapeamento de células conforme o seu modelo
    ws["E5"], ws["D6"], ws["J6"], ws["O6"] = d["nome"], d["cpf"], d["telefone"], d["fixo"]
    ws["D7"], ws["J7"], ws["P7"], ws["D8"], ws["O8"], ws["E9"] = d["nacionalidade"], d["profissao"], d["fone_pref"], d["estado_civil"], d["renda"], d["email"]
    ws["G11"], ws["D13"], ws["J13"], ws["O13"] = d["conjuge"], d["cpf2"], d["tel2"], d["fixo2"]
    ws["G19"], ws["C20"], ws["I20"], ws["C21"] = d["empreendimento"], d["logradouro"], d["unidade"], d["valor_negocio"]
    ws["J21"], ws["O21"], ws["C24"], ws["K24"] = d["entrada_total"], d["valor_imovel"], d["entrada_imovel"], d["data_venc_emp"]
    ws["C25"], ws["K25"], ws["C26"], ws["K26"] = d["parcela_36"], d["data_parcelas"], d["saldo"], d["data_saldo"]
    ws["C33"], ws["K33"] = d["entrada_cliente"], d["data_ato"]

    if not d["entrada_quitada"]:
        ws["B34"], ws["C34"], ws["K34"] = d["parcelas_iguais"], d["valor_parcela_igual"], d["data_parc_entrada"]
        if d["usar_diferente"]:
            ws["C35"], ws["K35"] = d["parcela_diferente"], d["data_parcela_diferente_manual"]

    nome_saida = f"proposta_{int(time.time())}.xlsx"
    wb.save(nome_saida)
    return nome_saida

def preencher_contrato_intermediacao(d, modelo=MODELO_CONTRATO_PADRAO):
    wb = load_workbook(modelo)
    ws = wb.active
    ws["C5"], ws["I5"], ws["C10"], ws["C11"] = d["nome"], d["cpf"], d["nome_imobiliaria"], d["nome_corretor"]
    ws["D17"], ws["J17"], ws["J19"], ws["K23"] = d["empreendimento_contrato"], d["unidade"], d["valor_negocio"], d["valor_total_comissao"]
    ws["E26"], ws["E27"], ws["E28"], ws["E29"] = d["valor_imobiliaria"], d["valor_corretor"], d["valor_ato_minimo"], d["valor_gerente"]
    
    nome_saida = f"contrato_{int(time.time())}.xlsx"
    wb.save(nome_saida)
    return nome_saida

# --- TELAS DO SISTEMA ---

def tela_login():
    st.markdown('<div class="gp-card-dark">', unsafe_allow_html=True)
    st.title("🔐 Login")
    email = st.text_input("Email")
    senha = st.text_input("Senha", type="password")
    if st.button("Entrar", use_container_width=True):
        try:
            resp = get_supabase().auth.sign_in_with_password({"email": email, "password": senha})
            if resp.user:
                profile = buscar_profile_por_id(resp.user.id)
                st.session_state.update({"logado": True, "usuario_id": profile["id"], "usuario_nome": profile["nome"], "usuario_email": email})
                st.rerun()
        except Exception as e: st.error("Erro ao entrar.")
    st.markdown('</div>', unsafe_allow_html=True)

def tela_nova_proposta():
    st.markdown('<div class="gp-card"><div class="gp-section-title">📝 Gerar Nova Proposta</div>', unsafe_allow_html=True)
    empreendimentos = listar_empreendimentos()
    if not empreendimentos: return st.warning("Sem empreendimentos.")
    
    emp = st.selectbox("Empreendimento", empreendimentos, format_func=lambda x: x["nome"])
    tabela_path = Path(emp["tabela_arquivo"])
    if not tabela_path.exists(): return st.error("Tabela não encontrada.")
    
    df = carregar_tabela(str(tabela_path), tabela_path.stat().st_mtime)
    unidade = st.selectbox("Unidade/Lote", df[df.columns[0]].dropna().unique())
    linha = df[df[df.columns[0]] == unidade].iloc[0]

    # Cálculos Automáticos
    v_negocio = buscar(linha, ["valor negócio", "valor negocio"])
    e_imovel = buscar(linha, ["entrada imovel", "entrada imóvel"])
    intermed = buscar(linha, ["intermediação", "intermediacao"])
    e_total = e_imovel + intermed
    
    regra = buscar_regra_imobiliaria(st.session_state["imobiliaria_id"])
    if not regra: return st.error("Regra financeira não configurada.")

    # Formulário
    col1, col2 = st.columns(2)
    with col1:
        nome = st.text_input("Nome Cliente")
        cpf = st.text_input("CPF")
        nasc = st.date_input("Data Nascimento", value=date(1990,1,1))
    with col2:
        v_cliente = st.number_input("Valor de Entrada que o cliente vai pagar", min_value=0.0, value=e_total)
        data_ato = st.date_input("Data do Ato")

    if st.button("🚀 Gerar Documentos", use_container_width=True):
        with st.spinner("Processando arquivos..."):
            dados = {
                "nome": nome, "cpf": cpf, "telefone": "", "fixo": "", "nacionalidade": "", "profissao": "", "fone_pref": "", "estado_civil": "", "renda": "", "email": "",
                "conjuge": "", "cpf2": "", "rg2": "", "tel2": "", "fixo2": "", "nac2": "", "prof2": "", "fone2": "", "civil2": "", "renda2": "", "rg": "",
                "empreendimento": emp["nome"], "logradouro": emp["logradouro"], "unidade": unidade, "valor_negocio": v_negocio, "entrada_total": e_total,
                "valor_imovel": buscar(linha, ["valor imóvel"]), "entrada_imovel": e_imovel, "parcela_36": buscar(linha, ["36x"]), "saldo": buscar(linha, ["saldo"]),
                "entrada_cliente": v_cliente, "entrada_quitada": v_cliente >= e_total, "data_venc_emp": date.today().strftime("%d/%m/%Y"),
                "data_parcelas": date.today().strftime("%d/%m/%Y"), "data_saldo": date.today().strftime("%d/%m/%Y"), "data_ato": data_ato.strftime("%d/%m/%Y"),
                "nome_imobiliaria": st.session_state["imobiliaria_nome"], "nome_corretor": st.session_state["usuario_nome"],
                "empreendimento_contrato": emp.get("contrato_nome", emp["nome"]), "valor_total_comissao": v_negocio * (float(regra["porcentagem_total_comissao"])/100),
                "valor_imobiliaria": v_negocio * (float(regra["porcentagem_imobiliaria"])/100), "valor_corretor": v_negocio * (float(regra["porcentagem_corretor"])/100),
                "valor_ato_minimo": v_negocio * (float(regra["porcentagem_ato_minimo"])/100), "valor_gerente": v_negocio * (float(regra["porcentagem_gerente"])/100),
                "usar_diferente": False, "parcelas_iguais": 0, "valor_parcela_igual": 0, "data_parc_entrada": ""
            }

            ex_prop = preencher_proposta(dados)
            ex_cont = preencher_contrato_intermediacao(dados)
            
            pdf_prop = excel_para_pdf(ex_prop)
            pdf_cont = excel_para_pdf(ex_cont)

            if pdf_prop and pdf_cont:
                st.success("Arquivos prontos!")
                st.download_button("📥 Baixar Proposta e Contrato (PDF)", data=criar_zip_bytes([pdf_prop, pdf_cont]), file_name=f"Proposta_{unidade}.zip")
    st.markdown('</div>', unsafe_allow_html=True)

# --- EXECUÇÃO PRINCIPAL ---

init_state()
if not st.session_state["logado"]:
    tela_login()
else:
    aplicar_tema()
    render_topbar()
    
    if not st.session_state["imobiliaria_id"]:
        st.markdown('<div class="gp-card">', unsafe_allow_html=True)
        imobs = listar_imobiliarias_ativas()
        escolha = st.selectbox("Selecione sua Imobiliária", imobs, format_func=lambda x: x["nome"])
        if st.button("Confirmar Imobiliária"):
            st.session_state.update({"imobiliaria_id": escolha["id"], "imobiliaria_nome": escolha["nome"]})
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.sidebar.title("Menu")
        if st.sidebar.button("🏠 Início"): st.rerun()
        if st.sidebar.button("📝 Nova Proposta"): tela_nova_proposta()
        logout()
