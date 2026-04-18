import streamlit as st
import requests
from supabase import Client, create_client
from datetime import datetime, timedelta, timezone

st.set_page_config(page_title="GoPropostas", page_icon="📄", layout="wide", initial_sidebar_state="expanded")

SUPABASE_URL = st.secrets["SUPABASE_URL"].strip()
SUPABASE_KEY = st.secrets["SUPABASE_KEY"].strip()
EDGE_FUNCTION_CREATE_SUBSCRIPTION_URL = st.secrets["EDGE_FUNCTION_CREATE_SUBSCRIPTION_URL"].strip()
EDGE_FUNCTION_CREATE_PIX_URL = st.secrets["EDGE_FUNCTION_CREATE_PIX_URL"].strip()

st.markdown("""
<style>
.stApp { background: linear-gradient(180deg, #062B36 0%, #073846 55%, #0A4C5B 100%); }
.block-container { padding-top: 2rem !important; padding-bottom: 2rem; max-width: 1380px; }
.gp-topbar { display:flex; align-items:center; justify-content:space-between; gap:18px; margin-bottom:20px; padding:20px 24px; border-radius:24px; background:rgba(255,255,255,0.06); border:1px solid rgba(255,255,255,0.08); backdrop-filter:blur(12px); box-shadow:0 12px 32px rgba(0,0,0,0.18); }
.gp-title { color:#F4F7FA; font-size:2rem; font-weight:900; margin:0; }
.gp-subtitle { color:rgba(244,247,250,0.84); margin-top:4px; font-size:1rem; }
.gp-card { background:#F8FBFD; border-radius:24px; padding:22px 24px; box-shadow:0 12px 28px rgba(0,0,0,0.16); border:1px solid rgba(12,109,132,0.10); margin-bottom:18px; }
.gp-card, .gp-card * { color:#062B36 !important; }
.gp-card-dark { background:linear-gradient(135deg, #0A3D4B 0%, #0C6D84 100%); color:white; border-radius:24px; padding:22px 24px; box-shadow:0 12px 28px rgba(0,0,0,0.22); margin-bottom:18px; }
.gp-card-dark, .gp-card-dark * { color:white !important; }
.gp-section-title { font-size:1.15rem; font-weight:800; margin-bottom:14px; }
.stButton > button, .stDownloadButton > button, .stLinkButton > a { background:linear-gradient(90deg, #F97316 0%, #FF8E2B 100%) !important; color:white !important; border:none !important; border-radius:14px !important; font-weight:800 !important; min-height:42px !important; width:100%; box-shadow:0 10px 18px rgba(249,115,22,0.28) !important; text-align:center !important; }
.stTextInput > div > div > input, .stNumberInput input, .stDateInput input, .stSelectbox div[data-baseweb="select"] > div { border-radius:14px !important; border:1px solid rgba(12,109,132,0.18) !important; background:#FFFFFF !important; color:#062B36 !important; -webkit-text-fill-color:#062B36 !important; caret-color:#062B36 !important; }
.stTabs [data-baseweb="tab"] { background:rgba(255,255,255,0.08); color:#F4F7FA; border-radius:12px; padding:10px 16px; }
.stTabs [aria-selected="true"] { background:#F97316 !important; color:white !important; }
div[data-testid="stMetric"] { background:white; border-radius:18px; padding:14px 16px; border:1px solid rgba(12,109,132,0.10); box-shadow:0 8px 18px rgba(0,0,0,0.08); }
div[data-testid="stMetric"] * { color:#062B36 !important; }
.plano-hero { background:linear-gradient(135deg, #062B36 0%, #0C6D84 100%); border-radius:28px; padding:34px 30px; color:white; box-shadow:0 18px 40px rgba(0,0,0,0.22); border:1px solid rgba(255,255,255,0.08); margin-bottom:22px; }
.plano-hero h1 { margin:0; font-size:2rem; font-weight:900; }
.plano-hero p { margin-top:10px; font-size:1rem; color:rgba(255,255,255,0.88); }
.plano-card { background:#F8FBFD; border-radius:24px; padding:26px 24px; box-shadow:0 14px 32px rgba(0,0,0,0.12); border:1px solid rgba(12,109,132,0.10); min-height:340px; }
.plano-card h3 { margin:0 0 10px 0; color:#062B36; font-size:1.25rem; font-weight:800; }
.plano-valor { font-size:2.1rem; font-weight:900; color:#F97316; margin-bottom:14px; }
.plano-valor span { font-size:1rem; color:#5C6C74; font-weight:600; }
.plano-mini { margin-top:18px; color:#5C6C74; font-size:0.95rem; }
.plano-badge { display:inline-block; padding:8px 12px; border-radius:999px; background:rgba(255,255,255,0.08); color:#F4F7FA; font-size:0.9rem; margin-top:12px; }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="gp-topbar">
    <div>
        <div class="gp-title">GoPropostas</div>
        <div class="gp-subtitle">Sistema corporativo de propostas imobiliárias</div>
    </div>
</div>
""", unsafe_allow_html=True)

@st.cache_resource
def get_supabase() -> Client:
    return create_client(SUPABASE_URL, SUPABASE_KEY)

def buscar_profile_por_id(user_id: str):
    try:
        resp = get_supabase().table("profiles").select("*").eq("id", user_id).limit(1).execute()
        return resp.data[0] if resp.data else None
    except Exception:
        return None

def buscar_profile_por_email(email: str):
    try:
        resp = get_supabase().table("profiles").select("*").eq("email", email).limit(1).execute()
        return resp.data[0] if resp.data else None
    except Exception:
        return None

def login_com_supabase(email: str, senha: str):
    return get_supabase().auth.sign_in_with_password({"email": email, "password": senha})

def cadastrar_com_supabase(nome: str, email: str, senha: str):
    return get_supabase().auth.sign_up({"email": email, "password": senha, "options": {"data": {"nome": nome}}})

def buscar_assinatura(user_id: str):
    try:
        resp = get_supabase().table("assinaturas").select("*").eq("user_id", user_id).order("created_at", desc=True).limit(1).execute()
        return resp.data[0] if resp.data else None
    except Exception:
        return None

def assinatura_ativa_para_acesso(assinatura: dict) -> bool:
    if not assinatura or not assinatura.get("assinatura_ativa"):
        return False
    fim = assinatura.get("data_fim") or assinatura.get("proximo_cobranca_em")
    if not fim:
        return True
    try:
        fim_dt = datetime.fromisoformat(str(fim).replace("Z", "+00:00"))
        return fim_dt >= datetime.now(timezone.utc)
    except Exception:
        return True

def buscar_assinatura_por_user_id(user_id: str):
    return buscar_assinatura(user_id)

def upsert_assinatura(user_id: str, dados: dict):
    assinatura = buscar_assinatura_por_user_id(user_id)
    if assinatura:
        return get_supabase().table("assinaturas").update(dados).eq("id", assinatura["id"]).execute()
    return get_supabase().table("assinaturas").insert({"user_id": user_id, **dados}).execute()

def liberar_30_dias(user_id: str):
    agora = datetime.now(timezone.utc)
    fim = agora + timedelta(days=30)
    return upsert_assinatura(user_id, {"status":"ativo","pagamento_status":"manual","assinatura_ativa":True,"data_inicio":agora.isoformat(),"data_fim":fim.isoformat(),"updated_at":agora.isoformat()})

def bloquear_usuario(user_id: str):
    agora = datetime.now(timezone.utc)
    return upsert_assinatura(user_id, {"status":"bloqueado","pagamento_status":"bloqueado","assinatura_ativa":False,"updated_at":agora.isoformat()})

def renovar_usuario(user_id: str, dias: int):
    atual = buscar_assinatura_por_user_id(user_id)
    agora = datetime.now(timezone.utc)
    base = agora
    if atual and (atual.get("data_fim") or atual.get("proximo_cobranca_em")):
        try:
            data_base = datetime.fromisoformat(str(atual.get("data_fim") or atual.get("proximo_cobranca_em")).replace("Z", "+00:00"))
            if data_base > agora:
                base = data_base
        except Exception:
            pass
    fim = base + timedelta(days=dias)
    return upsert_assinatura(user_id, {"status":"ativo","pagamento_status":"renovado_manual","assinatura_ativa":True,"data_inicio": atual.get("data_inicio") if atual and atual.get("data_inicio") else agora.isoformat(),"data_fim":fim.isoformat(),"updated_at":agora.isoformat()})

def criar_pix_mp(user_id: str, email: str):
    headers = {"Content-Type":"application/json","Authorization":f"Bearer {SUPABASE_KEY}"}
    resp = requests.post(EDGE_FUNCTION_CREATE_PIX_URL, json={"user_id": user_id, "email": email}, headers=headers, timeout=30)
    try:
        return resp.json()
    except Exception:
        return {"error": resp.text}

def criar_assinatura_mp(user_id: str, email: str):
    headers = {"Content-Type":"application/json","Authorization":f"Bearer {SUPABASE_KEY}"}
    resp = requests.post(EDGE_FUNCTION_CREATE_SUBSCRIPTION_URL, json={"user_id": user_id, "email": email}, headers=headers, timeout=30)
    try:
        return resp.json()
    except Exception:
        return {"error": resp.text}

def init_auth_state():
    defaults = {"logado":False,"usuario_id":"","usuario_email":"","usuario_nome":"","tipo":"","sb_access_token":"","sb_refresh_token":""}
    for chave, valor in defaults.items():
        if chave not in st.session_state:
            st.session_state[chave] = valor

def aplicar_login(profile: dict):
    st.session_state["logado"] = True
    st.session_state["usuario_id"] = profile["id"]
    st.session_state["usuario_email"] = profile["email"]
    st.session_state["usuario_nome"] = profile.get("nome") or profile["email"]
    st.session_state["tipo"] = profile.get("tipo", "corretor")

def salvar_tokens_da_sessao(auth_response):
    session = getattr(auth_response, "session", None)
    if session:
        st.session_state["sb_access_token"] = session.access_token or ""
        st.session_state["sb_refresh_token"] = session.refresh_token or ""

def tentar_restaurar_sessao():
    if st.session_state.get("logado"):
        return
    access_token = st.session_state.get("sb_access_token", "")
    refresh_token = st.session_state.get("sb_refresh_token", "")
    if not access_token or not refresh_token:
        return
    try:
        supabase = get_supabase()
        supabase.auth.set_session(access_token, refresh_token)
        sessao = supabase.auth.get_session()
        session = getattr(sessao, "session", None)
        if not session or not session.user:
            return
        profile = buscar_profile_por_id(session.user.id)
        if profile:
            aplicar_login(profile)
    except Exception:
        pass

def logout():
    if st.sidebar.button("🚪 Sair", use_container_width=True):
        try:
            get_supabase().auth.sign_out()
        except Exception:
            pass
        for chave in list(st.session_state.keys()):
            del st.session_state[chave]
        st.rerun()

def tela_login():
    st.markdown('<div class="gp-card-dark">', unsafe_allow_html=True)
    st.title("🔐 Entrar no sistema")
    st.write("Acesse sua conta ou crie seu cadastro para continuar.")
    abas = st.tabs(["Login", "Criar conta"])
    with abas[0]:
        email = st.text_input("Email", key="login_email")
        senha = st.text_input("Senha", type="password", key="login_senha")
        if st.button("Entrar", key="btn_login", use_container_width=True):
            try:
                resp = login_com_supabase(email, senha)
                user = resp.user
                if not user:
                    st.error("Email ou senha inválidos.")
                    return
                salvar_tokens_da_sessao(resp)
                profile = buscar_profile_por_id(user.id)
                if not profile:
                    st.error("Perfil não encontrado.")
                    return
                aplicar_login(profile)
                st.success("Login realizado com sucesso!")
                st.rerun()
            except Exception as e:
                st.error(f"Erro no login: {e}")
    with abas[1]:
        nome_cadastro = st.text_input("Nome completo", key="cad_nome")
        email_cadastro = st.text_input("Email", key="cad_email")
        senha_cadastro = st.text_input("Senha", type="password", key="cad_senha")
        confirmar = st.text_input("Confirmar senha", type="password", key="cad_confirm")
        if st.button("Criar conta", key="btn_cadastro", use_container_width=True):
            if senha_cadastro != confirmar:
                st.warning("Senhas não conferem.")
                return
            if not nome_cadastro.strip() or not email_cadastro.strip() or not senha_cadastro.strip():
                st.warning("Preencha todos os campos.")
                return
            try:
                existente = buscar_profile_por_email(email_cadastro)
                if existente:
                    st.warning("Já existe uma conta com esse email.")
                    return
                resp = cadastrar_com_supabase(nome_cadastro, email_cadastro, senha_cadastro)
                user = resp.user
                if user:
                    st.success("Conta criada com sucesso! Agora faça login.")
                else:
                    st.success("Conta criada! Verifique seu email para confirmar o cadastro antes de entrar.")
            except Exception as e:
                st.error(f"Erro ao criar conta: {e}")
    st.markdown("</div>", unsafe_allow_html=True)

def tela_plano_pagamento(usuario_id: str, usuario_email: str):
    st.markdown('<div class="plano-hero"><h1>Seu acesso está quase pronto</h1><p>Escolha a forma de pagamento abaixo para liberar sua conta e começar a usar o GoPropostas com acesso completo às propostas, contratos e recursos do sistema.</p><div class="plano-badge">Plano único: R$ 15,00 / mês</div></div>', unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<div class="plano-card"><h3>🧾 PIX mensal</h3><div class="plano-valor">R$ 15,00 <span>/ mês</span></div><ul><li>Pagamento rápido via PIX</li><li>Liberação por 30 dias</li><li>Ideal para quem prefere pagar manualmente</li><li>Acesso completo ao sistema</li></ul><div class="plano-mini">Gere o QR Code e pague em poucos segundos.</div></div>', unsafe_allow_html=True)
        if st.button("Gerar PIX", key="btn_pix_plano", use_container_width=True):
            with st.spinner("Gerando PIX..."):
                try:
                    data = criar_pix_mp(usuario_id, usuario_email)
                    qr_base64 = data.get("qr_code_base64")
                    qr_text = data.get("qr_code")
                    if not qr_base64 and data.get("raw"):
                        try:
                            tx = data["raw"]["point_of_interaction"]["transaction_data"]
                            qr_base64 = tx.get("qr_code_base64")
                            qr_text = tx.get("qr_code")
                        except Exception:
                            pass
                    if qr_base64:
                        st.success("PIX gerado com sucesso.")
                        st.image(f"data:image/png;base64,{qr_base64}")
                        if qr_text:
                            st.code(qr_text)
                        try:
                            ticket_url = data["raw"]["point_of_interaction"]["transaction_data"]["ticket_url"]
                            if ticket_url:
                                st.link_button("Abrir pagamento", ticket_url, use_container_width=True)
                        except Exception:
                            pass
                    else:
                        st.error(f"Erro ao gerar PIX: {data}")
                except Exception as e:
                    st.error(f"Erro ao gerar PIX: {e}")
    with col2:
        st.markdown('<div class="plano-card"><h3>💳 Assinatura automática</h3><div class="plano-valor">R$ 15,00 <span>/ mês</span></div><ul><li>Cobrança recorrente automática</li><li>Maior praticidade no dia a dia</li><li>Sem precisar gerar novo pagamento todo mês</li><li>Acesso contínuo ao sistema</li></ul><div class="plano-mini">Melhor opção para quem quer manter o acesso sempre ativo.</div></div>', unsafe_allow_html=True)
        if st.button("Assinar agora", key="btn_assinar_plano", use_container_width=True):
            with st.spinner("Gerando assinatura..."):
                try:
                    data = criar_assinatura_mp(usuario_id, usuario_email)
                    link = data.get("init_point") or data.get("sandbox_init_point")
                    if link:
                        st.success("Link de assinatura gerado com sucesso.")
                        st.link_button("Ir para pagamento", link, use_container_width=True)
                    else:
                        st.error(f"Erro ao gerar assinatura: {data}")
                except Exception as e:
                    st.error(f"Erro ao gerar assinatura: {e}")

def listar_assinaturas():
    try:
        resp = get_supabase().table("assinaturas").select("*").order("created_at", desc=True).execute()
        return resp.data or []
    except Exception:
        return []

def listar_profiles():
    try:
        resp = get_supabase().table("profiles").select("*").execute()
        return resp.data or []
    except Exception:
        return []

def formatar_data(valor):
    if not valor:
        return "-"
    try:
        return str(valor).replace("T", " ")[:19]
    except Exception:
        return str(valor)

def montar_linhas():
    profiles = listar_profiles()
    assinaturas = listar_assinaturas()
    mapa = {}
    for a in assinaturas:
        uid = a.get("user_id")
        if uid and uid not in mapa:
            mapa[uid] = a
    linhas = []
    for p in profiles:
        uid = p.get("id")
        a = mapa.get(uid)
        ativo = assinatura_ativa_para_acesso(a)
        linhas.append({"user_id": uid, "nome": p.get("nome") or "-", "email": p.get("email") or "-", "tipo": p.get("tipo", "corretor"), "status": a.get("status", "sem assinatura") if a else "sem assinatura", "pagamento_status": a.get("pagamento_status", "-") if a else "-", "assinatura_ativa": "Sim" if ativo else "Não", "data_inicio": formatar_data(a.get("data_inicio")) if a else "-", "data_fim": formatar_data(a.get("data_fim") or a.get("proximo_cobranca_em")) if a else "-"})
    return linhas

def tela_admin():
    linhas = montar_linhas()
    col1, col2, col3, col4 = st.columns(4)
    with col1: st.metric("Usuários", len(linhas))
    with col2: st.metric("Ativos", sum(1 for l in linhas if l["assinatura_ativa"] == "Sim"))
    with col3: st.metric("Bloqueados", sum(1 for l in linhas if l["status"] == "bloqueado"))
    with col4: st.metric("Pendentes/Sem assinatura", sum(1 for l in linhas if l["status"] in ["sem assinatura", "pendente"]))
    st.markdown('<div class="gp-card"><div class="gp-section-title">🔎 Filtros</div>', unsafe_allow_html=True)
    colf1, colf2 = st.columns(2)
    with colf1: busca = st.text_input("Buscar por nome ou email", key="busca_admin")
    with colf2: filtro_status = st.selectbox("Status", ["Todos", "ativo", "bloqueado", "sem assinatura", "pendente"], key="filtro_status_admin")
    st.markdown('</div>', unsafe_allow_html=True)
    linhas_filtradas = []
    for l in linhas:
        texto = f"{l['nome']} {l['email']}".lower()
        if (not busca.strip() or busca.strip().lower() in texto) and (filtro_status == "Todos" or l["status"] == filtro_status):
            linhas_filtradas.append(l)
    st.markdown('<div class="gp-card"><div class="gp-section-title">🛠️ Painel de administração</div>', unsafe_allow_html=True)
    if not linhas_filtradas:
        st.info("Nenhum usuário encontrado.")
    else:
        for i, linha in enumerate(linhas_filtradas):
            st.markdown(f"### {linha['nome']}")
            st.caption(f"{linha['email']} • Tipo: {linha['tipo']} • User ID: {linha['user_id']}")
            c1, c2, c3, c4, c5 = st.columns(5)
            with c1: st.metric("Status", linha["status"])
            with c2: st.metric("Pagamento", linha["pagamento_status"])
            with c3: st.metric("Ativo", linha["assinatura_ativa"])
            with c4: st.metric("Início", linha["data_inicio"])
            with c5: st.metric("Fim", linha["data_fim"])
            b1, b2, b3 = st.columns(3)
            with b1:
                if st.button("Liberar 30 dias", key=f"liberar_{i}", use_container_width=True):
                    liberar_30_dias(linha["user_id"]); st.success("Usuário liberado por 30 dias."); st.rerun()
            with b2:
                if st.button("Renovar +30 dias", key=f"renovar_{i}", use_container_width=True):
                    renovar_usuario(linha["user_id"], 30); st.success("Validade renovada com sucesso."); st.rerun()
            with b3:
                if st.button("Bloquear", key=f"bloquear_{i}", use_container_width=True):
                    bloquear_usuario(linha["user_id"]); st.warning("Usuário bloqueado."); st.rerun()
            st.divider()
    st.markdown('</div>', unsafe_allow_html=True)

def tela_sistema_principal():
    st.markdown('<div class="gp-card"><div class="gp-section-title">✅ Sistema principal</div><p>Seu pagamento está ativo. Aqui você encaixa o restante do seu sistema de propostas.</p><div class="plano-mini">Esse ponto já está pronto para receber o restante do app principal.</div></div>', unsafe_allow_html=True)

init_auth_state()
tentar_restaurar_sessao()

if not st.session_state["logado"]:
    tela_login()
    st.stop()

st.sidebar.write(f"👤 {st.session_state['usuario_nome']}")
st.sidebar.write(f"📧 {st.session_state['usuario_email']}")
st.sidebar.write(f"🔑 {st.session_state['tipo']}")
logout()

eh_admin = st.session_state.get("tipo") in ["admin", "Administrador", "administrador"]

if eh_admin:
    abas = st.tabs(["Sistema", "Painel Admin"])
    with abas[0]:
        tela_sistema_principal()
    with abas[1]:
        tela_admin()
else:
    assinatura = buscar_assinatura(st.session_state["usuario_id"])
    if not assinatura_ativa_para_acesso(assinatura):
        tela_plano_pagamento(st.session_state["usuario_id"], st.session_state["usuario_email"])
        st.stop()
    tela_sistema_principal()
