# APP FINAL CORRIGIDO (TOPO + HTML FIX)

import streamlit as st
import base64
from pathlib import Path

st.set_page_config(page_title="GoPropostas", layout="wide")

def img_to_base64(path):
    if not Path(path).exists():
        return ""
    return base64.b64encode(open(path, "rb").read()).decode()

logo_base64 = img_to_base64("logo.png")

st.markdown(f'''
<div style="padding:20px;border-radius:20px;background:rgba(255,255,255,0.05);display:flex;align-items:center;gap:15px;">
    {"<img src='data:image/png;base64," + logo_base64 + "' style='height:60px'>" if logo_base64 else ""}
    <div>
        <div style="font-size:28px;font-weight:800;color:white;">GoPropostas</div>
        <div style="color:#ccc;">Sistema corporativo de propostas imobiliárias</div>
    </div>
</div>
''', unsafe_allow_html=True)

st.success("Topo corrigido funcionando!")
