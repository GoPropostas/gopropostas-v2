import streamlit as st
import base64
from pathlib import Path

st.set_page_config(
    page_title="GoPropostas",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded",
)

def img_to_base64(path: str) -> str:
    p = Path(path)
    if not p.exists():
        return ""
    with open(p, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")

logo_base64 = img_to_base64("logo.png")

st.markdown("""
<style>
.stApp {
    background: linear-gradient(180deg, #062B36 0%, #073846 55%, #0A4C5B 100%);
}
.block-container {
    padding-top: 3rem !important;
    max-width: 1280px;
}
.gp-topbar {
    display: flex;
    align-items: center;
    gap: 18px;
    padding: 20px 24px;
    border-radius: 24px;
    background: rgba(255,255,255,0.06);
    border: 1px solid rgba(255,255,255,0.08);
    backdrop-filter: blur(12px);
    box-shadow: 0 12px 32px rgba(0,0,0,0.18);
}
.gp-topbar img {
    max-height: 64px;
    width: auto;
    border-radius: 12px;
}
.gp-title {
    color: #F4F7FA;
    font-size: 2rem;
    font-weight: 800;
    margin: 0;
    line-height: 1.1;
}
.gp-subtitle {
    color: rgba(244,247,250,0.82);
    font-size: 0.98rem;
    margin-top: 4px;
}
</style>
""", unsafe_allow_html=True)

topo_html = f"""
<div class="gp-topbar">
    {"<img src='data:image/png;base64," + logo_base64 + "' alt='Logo'>" if logo_base64 else ""}
    <div>
        <div class="gp-title">GoPropostas</div>
        <div class="gp-subtitle">Sistema corporativo de propostas imobiliárias</div>
    </div>
</div>
"""

st.markdown(topo_html, unsafe_allow_html=True)

st.success("Sistema funcionando sem erro 🚀")
