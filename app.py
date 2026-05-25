import os
import io
import base64
import zipfile
import subprocess
import ast
from pathlib import Path
from datetime import date, datetime, timedelta, timezone

import pandas as pd
import requests
import streamlit as st
from openpyxl import load_workbook
from openpyxl.styles import Alignment
from supabase import Client, create_client
from PIL import Image, UnidentifiedImageError

st.set_page_config(
    page_title="GoPropostas",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded",
)

EDGE_FUNCTION_CREATE_SUBSCRIPTION_URL = st.secrets.get("EDGE_FUNCTION_CREATE_SUBSCRIPTION_URL", "").strip()
EDGE_FUNCTION_CREATE_PIX_URL = st.secrets.get("EDGE_FUNCTION_CREATE_PIX_URL", "").strip()
LOGO_CANDIDATES = ["logo.png", "logo_padrao.png", "Apresentação de logo moderno e profissional.png"]
CONTRATO_INTERMEDIACAO_MODELO = "Contrato de Intermediação (3).xlsx"
MODELO_PROPOSTA = "modelo_proposta.xlsx"


# =========================
# VISUAL
# =========================
def encontrar_logo() -> str:
    for nome in LOGO_CANDIDATES:
        if Path(nome).exists():
            return nome
    return ""

def img_to_base64_segura(path: str) -> str:
    if not path or not Path(path).exists():
        return ""
    try:
        with Image.open(path) as img:
            img.verify()
        with open(path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    except (UnidentifiedImageError, OSError, Exception):
        return ""

LOGO_PATH = encontrar_logo()
logo_base64 = img_to_base64_segura(LOGO_PATH)

st.markdown("""
<style>
    :root {
        --gp-bg-1: #062B36;
        --gp-bg-2: #073846;
        --gp-bg-3: #0A4C5B;
        --gp-sidebar-1: #06232C;
        --gp-sidebar-2: #083845;
        --gp-surface: rgba(255,255,255,0.06);
        --gp-surface-strong: #F8FBFD;
        --gp-surface-dark: linear-gradient(135deg, #0A3D4B 0%, #0C6D84 100%);
        --gp-border: rgba(255,255,255,0.08);
        --gp-border-soft: rgba(12,109,132,0.18);
        --gp-text: #F4F7FA;
        --gp-text-soft: rgba(244,247,250,0.82);
        --gp-text-dark: #062B36;
        --gp-muted: #6B7C85;
        --gp-accent: #F97316;
        --gp-accent-2: #FF8E2B;
        --gp-metric-bg: #FFFFFF;
        --gp-metric-label: #0C6D84;
        --gp-input-bg: #FFFFFF;
        --gp-header-bg: rgba(0, 0, 0, 0.85);
    }

    html, body, [data-testid="stAppViewContainer"], .stApp {
        background: linear-gradient(180deg, var(--gp-bg-1) 0%, var(--gp-bg-2) 55%, var(--gp-bg-3) 100%) !important;
        color: var(--gp-text) !important;
    }

    .block-container {
        padding-top: 5rem !important;
        padding-bottom: 2rem;
        max-width: 1380px;
    }

    header[data-testid="stHeader"] {
        background: var(--gp-header-bg) !important;
    }

    [data-testid="stToolbar"] {
        right: 1rem;
    }

    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, var(--gp-sidebar-1) 0%, var(--gp-sidebar-2) 100%) !important;
