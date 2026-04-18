import streamlit as st
from pathlib import Path

st.set_page_config(page_title="GoPropostas", layout="wide")

# ===== TOPO COM LOGO CORRIGIDO =====
LOGO_PATH = "logo.png"  # coloque sua logo com esse nome

col_logo, col_texto = st.columns([1, 5])

with col_logo:
    if Path(LOGO_PATH).exists():
        st.image(LOGO_PATH, width=110)

with col_texto:
    st.markdown("""
    <div style="padding-top: 10px;">
        <div style="color:#F4F7FA;font-size:2rem;font-weight:800;line-height:1.1;">
            GoPropostas
        </div>
        <div style="color:rgba(244,247,250,0.82);font-size:0.98rem;margin-top:4px;">
            Sistema corporativo de propostas imobiliárias
        </div>
    </div>
    """, unsafe_allow_html=True)

st.success("Logo corrigida funcionando 🚀")
