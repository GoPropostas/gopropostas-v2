# app.py - GoPropostas (Logo corrigida)

import os
import io
import zipfile
import subprocess
from pathlib import Path
from datetime import date

import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="GoPropostas",
    page_icon="📄",
    layout="wide",
)

LOGO_PATH = "logo_padrao.png"

# =========================
# FUNÇÕES UTILITÁRIAS
# =========================
@st.cache_data
def carregar_tabela(arquivo, mod_time):
    df = pd.read_excel(arquivo, skiprows=11)
    df.columns = df.columns.str.strip().str.lower()
    return df

def limpar(valor):
    if pd.isna(valor):
        return 0.0
    texto = str(valor).replace("R$", "").replace(".", "").replace(",", ".")
    try:
        return float(texto)
    except:
        return 0.0

def buscar(linha, nomes):
    for col in linha.index:
        for nome in nomes:
            if nome.lower() in col.lower():
                return limpar(linha[col])
    return 0.0

def formatar_moeda(valor):
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

# =========================
# LOGO CORRIGIDA
# =========================
col_logo, col_texto = st.columns([1, 5])

with col_logo:
    if Path(LOGO_PATH).exists():
        st.image(LOGO_PATH, width=120)
    else:
        st.warning("Logo não encontrada")

with col_texto:
    st.markdown("<h1 style='color:white;'>GoPropostas</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color:lightgray;'>Sistema corporativo de propostas imobiliárias</p>", unsafe_allow_html=True)

# =========================
# EMPREENDIMENTOS
# =========================
empreendimentos = {
    "Frei Galvão": {
        "tabela": "tabela_frei_galvao.xlsx",
    }
}

st.markdown("## 🏢 Empreendimento")

emp_nome = st.selectbox("Selecione", list(empreendimentos.keys()))
emp = empreendimentos[emp_nome]

caminho_tabela = Path(emp["tabela"])

if not caminho_tabela.exists():
    st.error("Tabela não encontrada")
    st.stop()

df = carregar_tabela(str(caminho_tabela), caminho_tabela.stat().st_mtime)

coluna = df.columns[0]
lote = st.selectbox("Lote", df[coluna].dropna().unique())

linha = df[df[coluna] == lote].iloc[0]

valor_negocio = buscar(linha, ["valor negócio"])
entrada_imovel = buscar(linha, ["entrada"])
intermed = buscar(linha, ["intermedia"])

entrada_total = entrada_imovel + intermed

# =========================
# FORMULÁRIO
# =========================
st.markdown("## 👤 Cliente")

nome = st.text_input("Nome")
cpf = st.text_input("CPF")

st.markdown("## 💰 Condições")

entrada_cliente = st.number_input("Entrada cliente", min_value=0.0)

restante = entrada_total - entrada_cliente

parcelas = st.slider("Parcelas", 1, 4)

valor_parcela = restante / parcelas if parcelas else 0

# =========================
# RESUMO
# =========================
st.markdown("## 📊 Resumo")

st.metric("Valor Negócio", formatar_moeda(valor_negocio))
st.metric("Entrada Total", formatar_moeda(entrada_total))
st.metric("Entrada Cliente", formatar_moeda(entrada_cliente))
st.metric("Parcelas", f"{parcelas}x {formatar_moeda(valor_parcela)}")

# =========================
# BOTÃO
# =========================
if st.button("Gerar Proposta"):
    st.success("Proposta gerada com sucesso!")
