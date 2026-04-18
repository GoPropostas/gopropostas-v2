import streamlit as st

st.set_page_config(page_title="GoPropostas", layout="wide")

# ================== ESTADO ==================
if "pagina" not in st.session_state:
    st.session_state.pagina = "principal"

# ================== TOPO ==================
st.markdown("""
<h1 style='color:white;'>GoPropostas</h1>
<p style='color:#ccc;'>Sistema corporativo</p>
""", unsafe_allow_html=True)

# ================== MENU ==================
col1, col2, col3 = st.columns(3)

with col1:
    if st.button("🏠 Principal"):
        st.session_state.pagina = "principal"

with col2:
    if st.button("📄 Histórico de Propostas"):
        st.session_state.pagina = "historico"

with col3:
    if st.button("⚙️ Configurações"):
        st.session_state.pagina = "config"

# ================== CONTEÚDO ==================

if st.session_state.pagina == "principal":
    st.success("Área principal (propostas aqui)")

elif st.session_state.pagina == "historico":
    st.info("Aqui aparece o histórico de propostas (ativado só quando clicar)")

elif st.session_state.pagina == "config":
    st.warning("Configurações do usuário aqui")


# ================== ADMIN ==================
st.markdown("---")
st.subheader("Área Admin")

tab1, tab2 = st.tabs(["👥 Aprovação de Usuários", "🏢 Por Imobiliária"])

with tab1:
    st.write("Aprovar / bloquear usuários aqui")
    if st.button("Aprovar usuário"):
        st.success("Usuário aprovado")

    if st.button("Bloquear usuário"):
        st.error("Usuário bloqueado")

with tab2:
    st.write("Aprovação por imobiliária separada")
