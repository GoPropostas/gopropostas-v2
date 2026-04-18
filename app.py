import streamlit as st
from pathlib import Path
from PIL import Image, UnidentifiedImageError

st.set_page_config(page_title="GoPropostas", layout="wide")

LOGO_PATH = "logo.png"

st.markdown("""
<style>
.stApp {
    background: linear-gradient(180deg, #04141a 0%, #073846 48%, #0A4C5B 100%);
}
.block-container {
    padding-top: 2.6rem !important;
    max-width: 1200px;
}
.gp-hero {
    border-radius: 30px;
    padding: 30px;
    background: linear-gradient(135deg, rgba(255,255,255,0.08), rgba(255,255,255,0.02));
    border: 1px solid rgba(255,255,255,0.08);
    box-shadow: 0 20px 60px rgba(0,0,0,0.4);
}
.gp-title {
    color: white;
    font-size: 32px;
    font-weight: 900;
}
.gp-subtitle {
    color: #ccc;
    margin-top: 6px;
}
.gp-chip {
    padding: 8px 14px;
    border-radius: 14px;
    background: rgba(255,255,255,0.06);
    margin-right: 6px;
    display: inline-block;
    color: white;
}
</style>
""", unsafe_allow_html=True)

def logo_html():
    if not Path(LOGO_PATH).exists():
        return "🚀"
    try:
        with Image.open(LOGO_PATH) as img:
            img.verify()
        return f"<img src='{LOGO_PATH}' style='height:60px'>"
    except:
        return "🚀"

st.markdown(f"""
<div class="gp-hero">
    {logo_html()}
    <div class="gp-title">GoPropostas</div>
    <div class="gp-subtitle">Sistema corporativo de propostas imobiliárias</div>
    <br>
    <span class="gp-chip">Propostas</span>
    <span class="gp-chip">Contratos</span>
    <span class="gp-chip">Pagamentos</span>
</div>
""", unsafe_allow_html=True)

st.success("Sistema carregado com topo premium 🚀")
