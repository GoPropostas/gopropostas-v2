# APP COMPLETO - GoPropostas V2 com Plano de Pagamento

import streamlit as st
import requests
from datetime import datetime
from supabase import create_client

st.set_page_config(page_title="GoPropostas", layout="wide")

# ================= CONFIG =================
SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]
EDGE_PIX = st.secrets["EDGE_FUNCTION_CREATE_PIX_URL"]
EDGE_SUB = st.secrets["EDGE_FUNCTION_CREATE_SUBSCRIPTION_URL"]

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# ================= LOGIN =================
def login(email, senha):
    return supabase.auth.sign_in_with_password({"email": email, "password": senha})

def cadastro(nome, email, senha):
    return supabase.auth.sign_up({
        "email": email,
        "password": senha,
        "options": {"data": {"nome": nome}}
    })

# ================= PAGAMENTOS =================
def criar_pix(user_id, email):
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {SUPABASE_KEY}"
    }
    resp = requests.post(EDGE_PIX, json={"user_id": user_id, "email": email}, headers=headers)
    return resp.json()

def criar_assinatura(user_id, email):
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {SUPABASE_KEY}"
    }
    resp = requests.post(EDGE_SUB, json={"user_id": user_id, "email": email}, headers=headers)
    return resp.json()

# ================= UI =================
st.title("🚀 GoPropostas")

if "user" not in st.session_state:
    st.session_state.user = None

# LOGIN
if not st.session_state.user:
    aba1, aba2 = st.tabs(["Login", "Cadastro"])

    with aba1:
        email = st.text_input("Email")
        senha = st.text_input("Senha", type="password")
        if st.button("Entrar"):
            try:
                res = login(email, senha)
                st.session_state.user = res.user
                st.rerun()
            except Exception as e:
                st.error("Erro login")

    with aba2:
        nome = st.text_input("Nome")
        email = st.text_input("Email cadastro")
        senha = st.text_input("Senha cadastro", type="password")
        if st.button("Criar conta"):
            try:
                cadastro(nome, email, senha)
                st.success("Conta criada")
            except:
                st.error("Erro cadastro")

    st.stop()

# ================= VERIFICAR ASSINATURA =================
user_id = st.session_state.user.id
email = st.session_state.user.email

def tem_acesso():
    try:
        r = supabase.table("assinaturas").select("*").eq("user_id", user_id).execute()
        if r.data:
            return r.data[0].get("assinatura_ativa", False)
        return False
    except:
        return False

if not tem_acesso():

    st.markdown("## 💳 Escolha seu plano")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### PIX - R$15/mês")
        if st.button("Gerar PIX"):
            data = criar_pix(user_id, email)
            if "qr_code_base64" in data:
                st.image(f"data:image/png;base64,{data['qr_code_base64']}")
                st.code(data.get("qr_code"))

    with col2:
        st.markdown("### Assinatura automática - R$15/mês")
        if st.button("Assinar"):
            data = criar_assinatura(user_id, email)
            link = data.get("init_point")
            if link:
                st.link_button("Pagar", link)

    st.stop()

# ================= SISTEMA =================
st.success("Acesso liberado!")
st.write("Aqui entra seu sistema principal")
