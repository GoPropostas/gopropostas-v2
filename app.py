import streamlit as st
import base64
from pathlib import Path

# CONFIG
st.set_page_config(page_title="GoPropostas", layout="wide")

# FUNÇÃO LOGO
def img_to_base64(path):
    if not Path(path).exists():
        return ""
    return base64.b64encode(open(path, "rb").read()).decode()

logo_base64 = img_to_base64("logo.png")

# CSS
st.markdown("""
<style>
.stApp {
    background: linear-gradient(180deg, #062B36 0%, #073846 55%, #0A4C5B 100%);
}
.gp-topbar {
    display: flex;
    align-items: center;
    gap: 18px;
    padding: 20px 24px;
    border-radius: 24px;
    background: rgba(255,255,255,0.06);
    border: 1px solid rgba(255,255,255,0.08);
}
.gp-title {
    color: white;
    font-size: 28px;
    font-weight: 800;
}
.gp-subtitle {
    color: #ccc;
}
</style>
""", unsafe_allow_html=True)

# TOPO
st.markdown(f"""
<div class="gp-topbar">
    {"<img src='data:image/png;base64," + logo_base64 + "' style='height:60px'>" if logo_base64 else ""}
    <div>
        <div class="gp-title">GoPropostas</div>
        <div class="gp-subtitle">Sistema corporativo de propostas imobiliárias</div>
    </div>
</div>
""", unsafe_allow_html=True)

# TESTE
st.success("Sistema funcionando sem erro 🚀")
