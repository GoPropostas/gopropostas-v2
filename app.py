import streamlit as st
import requests

st.title("Teste Auth Supabase")

url = st.secrets["SUPABASE_URL"].strip()
key = st.secrets["SUPABASE_KEY"].strip()

st.write("Base URL:", url)

if st.button("Testar settings do Auth"):
    try:
        r = requests.get(
            f"{url}/auth/v1/settings",
            headers={
                "apikey": key,
                "Authorization": f"Bearer {key}",
            },
            timeout=20,
        )
        st.write("Status:", r.status_code)
        st.json(r.json())
    except Exception as e:
        st.error(f"Erro no GET /auth/v1/settings: {repr(e)}")

email = st.text_input("Email teste")
senha = st.text_input("Senha teste", type="password")

if st.button("Testar signup bruto"):
    try:
        r = requests.post(
            f"{url}/auth/v1/signup",
            headers={
                "apikey": key,
                "Authorization": f"Bearer {key}",
                "Content-Type": "application/json",
            },
            json={
                "email": email,
                "password": senha,
                "data": {"nome": "Teste"},
            },
            timeout=20,
        )
        st.write("Status:", r.status_code)
        try:
            st.json(r.json())
        except Exception:
            st.write(r.text)
    except Exception as e:
        st.error(f"Erro no POST /auth/v1/signup: {repr(e)}")
