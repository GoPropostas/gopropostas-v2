import streamlit as st
from supabase import create_client

st.title("Diagnóstico Supabase")

try:
    url = st.secrets.get("SUPABASE_URL", "")
    key = st.secrets.get("SUPABASE_KEY", "")

    st.write("URL bruta:", repr(url))
    st.write("Key existe:", bool(key))
    st.write("URL começa com https://", str(url).startswith("https://"))
    st.write("URL tem supabase.co", "supabase.co" in str(url))

    if not url:
        st.error("SUPABASE_URL não foi carregada.")
    elif not key:
        st.error("SUPABASE_KEY não foi carregada.")
    else:
        sb = create_client(url, key)
        st.success("Cliente criado com sucesso.")
except Exception as e:
    st.error(f"Erro ao criar cliente: {repr(e)}")
