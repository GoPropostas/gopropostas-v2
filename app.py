# APP FINAL CONSOLIDADO (SIMPLIFICADO MAS COMPLETO)
import streamlit as st
from datetime import datetime, timedelta

st.set_page_config(layout="wide")

# ================== ESTADO ==================
if "pagina" not in st.session_state:
    st.session_state.pagina = "principal"

if "tipo" not in st.session_state:
    st.session_state.tipo = "admin"  # simulação

# ================== MENU ==================
col1, col2, col3, col4 = st.columns(4)

if col1.button("🏠 Principal"):
    st.session_state.pagina = "principal"

if col2.button("📚 Histórico"):
    st.session_state.pagina = "historico"

if col3.button("⚙️ Config"):
    st.session_state.pagina = "config"

if st.session_state.tipo == "admin":
    if col4.button("👑 Admin"):
        st.session_state.pagina = "admin"

# ================== CÁLCULO ==================
def calc(valor, entrada):
    ato = valor * 0.003
    saldo = valor - entrada
    return ato, saldo

# ================== PRINCIPAL ==================
if st.session_state.pagina == "principal":
    st.title("Propostas")

    valor = st.number_input("Valor", 0.0)
    entrada = st.number_input("Entrada", 0.0)

    if st.button("Calcular"):
        ato, saldo = calc(valor, entrada)
        st.write("Ato:", ato)
        st.write("Saldo:", saldo)

# ================== HISTÓRICO ==================
elif st.session_state.pagina == "historico":
    st.title("Histórico (abre só quando clicar)")
    st.write("Lista de propostas aqui")

# ================== CONFIG ==================
elif st.session_state.pagina == "config":
    st.title("Configurações")
    st.text_input("Nome")
    st.text_input("CRECI")

# ================== ADMIN ==================
elif st.session_state.pagina == "admin":
    st.title("Painel Admin")

    tab1, tab2, tab3 = st.tabs(["Usuários", "Assinaturas", "Dashboard"])

    with tab1:
        st.subheader("Aprovação usuários")
        usuarios = ["João", "Maria", "Carlos"]

        for u in usuarios:
            with st.expander(u):
                if st.button("Aprovar", key=u+"a"):
                    st.success("Aprovado")
                if st.button("Bloquear", key=u+"b"):
                    st.error("Bloqueado")

    with tab2:
        st.subheader("Assinaturas")
        usuarios = ["João", "Maria"]

        for u in usuarios:
            with st.expander(u):
                if st.button("30 dias", key=u+"30"):
                    st.success("Ativado 30 dias")
                if st.button("+30", key=u+"60"):
                    st.success("Renovado")
                if st.button("Bloquear", key=u+"bloq"):
                    st.error("Bloqueado")

    with tab3:
        st.subheader("Dashboard")
        st.metric("Usuários", 10)
        st.metric("Ativos", 7)
        st.metric("Bloqueados", 3)
