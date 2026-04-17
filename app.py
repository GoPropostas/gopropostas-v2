import streamlit as st
import requests
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
    return supabase.auth.sign_in_with_password({
        "email": email,
        "password": senha
    })

def cadastro(nome, email, senha):
    return supabase.auth.sign_up({
        "email": email,
        "password": senha,
        "options": {"data": {"nome": nome}}
    })

# ================= PAGAMENTO =================
def criar_pix(user_id, email):
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {SUPABASE_KEY}"
    }

    resp = requests.post(
        EDGE_PIX,
        json={"user_id": user_id, "email": email},
        headers=headers
    )

    try:
        return resp.json()
    except:
        return {"erro_bruto": resp.text}


def criar_assinatura(user_id, email):
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {SUPABASE_KEY}"
    }

    resp = requests.post(
        EDGE_SUB,
        json={"user_id": user_id, "email": email},
        headers=headers
    )

    try:
        return resp.json()
    except:
        return {"erro_bruto": resp.text}


# ================= UI =================
st.title("🚀 GoPropostas")

if "user" not in st.session_state:
    st.session_state.user = None

# ================= LOGIN =================
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
                st.error(f"Erro login: {e}")

    with aba2:
        nome = st.text_input("Nome")
        email = st.text_input("Email cadastro")
        senha = st.text_input("Senha cadastro", type="password")

        if st.button("Criar conta"):
            try:
                cadastro(nome, email, senha)
                st.success("Conta criada!")
            except Exception as e:
                st.error(f"Erro cadastro: {e}")

    st.stop()

# ================= VERIFICAR ACESSO =================
user_id = st.session_state.user.id
email = st.session_state.user.email

def tem_acesso():
    try:
        r = supabase.table("assinaturas").select("*").eq("user_id", user_id).execute()

        if r.data:
            return r.data[0].get("assinatura_ativa", False)

        return False

    except Exception as e:
        st.error(f"Erro ao verificar assinatura: {e}")
        return False


# ================= PLANO =================
if not tem_acesso():

    st.markdown("## 💳 Escolha seu plano")

    col1, col2 = st.columns(2)

    # ================= PIX =================
    with col1:
        st.markdown("### PIX - R$15/mês")

        if st.button("Gerar PIX"):
            with st.spinner("Gerando PIX..."):

                data = criar_pix(user_id, email)

                st.write("DEBUG PIX:", data)

                if data.get("qr_code_base64"):
                    st.success("PIX gerado!")
                    st.image(f"data:image/png;base64,{data['qr_code_base64']}")

                    if data.get("qr_code"):
                        st.code(data["qr_code"])

                else:
                    st.error("Erro ao gerar PIX")

    # ================= ASSINATURA =================
    with col2:
        st.markdown("### Assinatura automática - R$15/mês")

        if st.button("Assinar"):
            with st.spinner("Gerando link..."):

                data = criar_assinatura(user_id, email)

                st.write("DEBUG ASSINATURA:", data)

                link = data.get("init_point") or data.get("sandbox_init_point")

                if link:
                    st.success("Link gerado!")
                    st.link_button("Ir para pagamento", link)

                else:
                    st.error("Erro ao gerar assinatura")

    st.stop()

# ================= SISTEMA =================
st.success("✅ Acesso liberado!")
st.write("Aqui entra seu sistema principal")
