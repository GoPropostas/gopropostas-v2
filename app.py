import base64
import textwrap
from datetime import datetime
from pathlib import Path

import requests
import streamlit as st
from supabase import Client, create_client

st.set_page_config(
    page_title="GoPropostas V2",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="expanded",
)

LOGO_PADRAO = "logo_padrao.png"


@st.cache_resource
def get_supabase() -> Client:
    return create_client(
        st.secrets["SUPABASE_URL"].strip(),
        st.secrets["SUPABASE_KEY"].strip(),
    )


def img_to_base64(path: str) -> str:
    p = Path(path)
    if not p.exists():
        return ""
    return base64.b64encode(p.read_bytes()).decode()


def aplicar_tema(imob=None):
    cor_primaria = "#0C6D84"
    cor_secundaria = "#F97316"
    bg_inicio = "#062B36"
    bg_fim = "#0A4C5B"

    if imob:
        cor_primaria = imob.get("cor_primaria") or cor_primaria
        cor_secundaria = imob.get("cor_secundaria") or cor_secundaria
        bg_inicio = imob.get("background_inicio") or bg_inicio
        bg_fim = imob.get("background_fim") or bg_fim

    st.markdown(
        f"""
<style>
.stApp {{
    background: linear-gradient(180deg, {bg_inicio} 0%, {bg_fim} 100%);
}}

[data-testid="stSidebar"] {{
    background: linear-gradient(180deg, {bg_inicio} 0%, {bg_fim} 100%);
}}

.gp-card {{
    background: #F8FBFD;
    border-radius: 24px;
    padding: 22px 24px;
    box-shadow: 0 12px 28px rgba(0,0,0,0.16);
    border: 1px solid rgba(12,109,132,0.10);
    margin-bottom: 18px;
}}

.gp-card, .gp-card * {{
    color: #062B36 !important;
}}

.gp-card-dark {{
    background: linear-gradient(135deg, {bg_inicio} 0%, {cor_primaria} 100%);
    color: white;
    border-radius: 24px;
    padding: 22px 24px;
    box-shadow: 0 12px 28px rgba(0,0,0,0.22);
    margin-bottom: 18px;
}}

.gp-card-dark, .gp-card-dark * {{
    color: white !important;
}}

.gp-title {{
    color: #F4F7FA;
    font-size: 2rem;
    font-weight: 800;
    margin: 0;
}}

.gp-subtitle {{
    color: rgba(244,247,250,0.82);
    font-size: 0.98rem;
    margin-top: 4px;
}}

.gp-section-title {{
    font-size: 1.15rem;
    font-weight: 800;
    margin-bottom: 14px;
}}

.stButton > button {{
    background: linear-gradient(90deg, {cor_secundaria} 0%, {cor_primaria} 100%) !important;
    color: white !important;
    border: none !important;
    border-radius: 14px !important;
    font-weight: 800 !important;
    min-height: 46px !important;
}}

.stTextInput input,
.stNumberInput input,
.stTextArea textarea,
.stSelectbox div[data-baseweb="select"] > div {{
    border-radius: 14px !important;
}}

.gp-member {{
    background: rgba(255,255,255,0.92);
    border-radius: 18px;
    padding: 16px;
    margin-bottom: 12px;
    border: 1px solid rgba(12,109,132,0.10);
}}

.gp-member * {{
    color: #062B36 !important;
}}
</style>
        """,
        unsafe_allow_html=True,
    )


def render_topbar(imob=None):
    titulo = imob["nome"] if imob else "GoPropostas V2"
    subtitulo = "Sistema multi-imobiliária"
    logo_base64 = img_to_base64(LOGO_PADRAO)

    html = f"""
<div style="margin-bottom:20px;padding:18px 24px;border-radius:24px;background:rgba(255,255,255,0.06);border:1px solid rgba(255,255,255,0.08);display:flex;align-items:center;gap:18px;">
    {"<img src='data:image/png;base64," + logo_base64 + "' style='max-height:78px;border-radius:12px;' />" if logo_base64 else ""}
    <div>
        <div class="gp-title">{titulo}</div>
        <div class="gp-subtitle">{subtitulo}</div>
    </div>
</div>
"""
    st.markdown(textwrap.dedent(html), unsafe_allow_html=True)


def init_state():
    defaults = {
        "logado": False,
        "usuario_id": "",
        "usuario_email": "",
        "usuario_nome": "",
        "role_global": "usuario",
        "sb_access_token": "",
        "sb_refresh_token": "",
        "imobiliaria_id": "",
        "imobiliaria_nome": "",
        "cargo_imobiliaria": "",
        "status_vinculo": "",
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v


def aplicar_login(profile: dict):
    st.session_state["logado"] = True
    st.session_state["usuario_id"] = profile["id"]
    st.session_state["usuario_email"] = profile.get("email", "")
    st.session_state["usuario_nome"] = profile.get("nome") or profile.get("email", "")
    st.session_state["role_global"] = profile.get("role_global", "usuario")


def salvar_tokens(auth_response):
    session = getattr(auth_response, "session", None)
    if session:
        st.session_state["sb_access_token"] = session.access_token or ""
        st.session_state["sb_refresh_token"] = session.refresh_token or ""


def restaurar_sessao():
    if st.session_state.get("logado"):
        return

    access_token = st.session_state.get("sb_access_token", "")
    refresh_token = st.session_state.get("sb_refresh_token", "")

    if not access_token or not refresh_token:
        return

    try:
        sb = get_supabase()
        sb.auth.set_session(access_token, refresh_token)
        sessao = sb.auth.get_session()
        session = getattr(sessao, "session", None)

        if not session or not session.user:
            return

        profile = buscar_profile_por_id(session.user.id)
        if profile:
            aplicar_login(profile)
    except Exception:
        pass


def limpar_estado_imobiliaria():
    st.session_state["imobiliaria_id"] = ""
    st.session_state["imobiliaria_nome"] = ""
    st.session_state["cargo_imobiliaria"] = ""
    st.session_state["status_vinculo"] = ""


def logout():
    if st.sidebar.button("🚪 Sair", use_container_width=True):
        try:
            get_supabase().auth.sign_out()
        except Exception:
            pass

        for k in list(st.session_state.keys()):
            del st.session_state[k]

        st.rerun()


# =========================
# BANCO
# =========================
def buscar_profile_por_id(user_id: str):
    resp = (
        get_supabase()
        .table("profiles")
        .select("*")
        .eq("id", user_id)
        .limit(1)
        .execute()
    )
    return resp.data[0] if resp.data else None


def buscar_profile_por_email(email: str):
    resp = (
        get_supabase()
        .table("profiles")
        .select("*")
        .eq("email", email)
        .limit(1)
        .execute()
    )
    return resp.data[0] if resp.data else None


def listar_imobiliarias_ativas():
    resp = (
        get_supabase()
        .table("imobiliarias")
        .select("*")
        .eq("ativa", True)
        .order("nome")
        .execute()
    )
    return resp.data or []


def buscar_imobiliaria_por_id(imobiliaria_id: str):
    resp = (
        get_supabase()
        .table("imobiliarias")
        .select("*")
        .eq("id", imobiliaria_id)
        .limit(1)
        .execute()
    )
    return resp.data[0] if resp.data else None


def buscar_vinculos_usuario(user_id: str):
    resp = (
        get_supabase()
        .table("usuarios_imobiliarias")
        .select("*, imobiliarias(*)")
        .eq("user_id", user_id)
        .order("created_at", desc=True)
        .execute()
    )
    return resp.data or []


def buscar_vinculo(user_id: str, imobiliaria_id: str):
    resp = (
        get_supabase()
        .table("usuarios_imobiliarias")
        .select("*")
        .eq("user_id", user_id)
        .eq("imobiliaria_id", imobiliaria_id)
        .limit(1)
        .execute()
    )
    return resp.data[0] if resp.data else None


def solicitar_acesso(user_id: str, imobiliaria_id: str):
    existente = buscar_vinculo(user_id, imobiliaria_id)
    if existente:
        return existente

    resp = (
        get_supabase()
        .table("usuarios_imobiliarias")
        .insert(
            {
                "user_id": user_id,
                "imobiliaria_id": imobiliaria_id,
                "cargo": "corretor",
                "status": "pendente",
            }
        )
        .execute()
    )
    return resp.data[0] if resp.data else None


def listar_solicitacoes_pendentes():
    resp = (
        get_supabase()
        .table("usuarios_imobiliarias")
        .select("*, imobiliarias(*)")
        .eq("status", "pendente")
        .order("created_at")
        .execute()
    )
    return resp.data or []


def listar_solicitacoes_pendentes_por_imobiliaria(imobiliaria_id: str):
    resp = (
        get_supabase()
        .table("usuarios_imobiliarias")
        .select("*, imobiliarias(*)")
        .eq("status", "pendente")
        .eq("imobiliaria_id", imobiliaria_id)
        .order("created_at")
        .execute()
    )
    return resp.data or []


def listar_membros_imobiliaria(imobiliaria_id: str):
    resp = (
        get_supabase()
        .table("usuarios_imobiliarias")
        .select("*")
        .eq("imobiliaria_id", imobiliaria_id)
        .order("created_at")
        .execute()
    )
    return resp.data or []


def aprovar_vinculo(vinculo_id: str, aprovador_id: str, cargo: str):
    return (
        get_supabase()
        .table("usuarios_imobiliarias")
        .update(
            {
                "status": "aprovado",
                "cargo": cargo,
                "aprovado_por": aprovador_id,
                "aprovado_em": datetime.utcnow().isoformat(),
            }
        )
        .eq("id", vinculo_id)
        .execute()
    )


def rejeitar_vinculo(vinculo_id: str):
    return (
        get_supabase()
        .table("usuarios_imobiliarias")
        .update({"status": "rejeitado"})
        .eq("id", vinculo_id)
        .execute()
    )


def alterar_cargo_vinculo(vinculo_id: str, novo_cargo: str):
    return (
        get_supabase()
        .table("usuarios_imobiliarias")
        .update({"cargo": novo_cargo})
        .eq("id", vinculo_id)
        .execute()
    )


def alterar_status_vinculo(vinculo_id: str, novo_status: str):
    return (
        get_supabase()
        .table("usuarios_imobiliarias")
        .update({"status": novo_status})
        .eq("id", vinculo_id)
        .execute()
    )


def buscar_nome_email_usuario(user_id: str):
    perfil = buscar_profile_por_id(user_id)
    if not perfil:
        return "", ""
    return perfil.get("nome", ""), perfil.get("email", "")


def listar_empreendimentos():
    resp = (
        get_supabase()
        .table("empreendimentos")
        .select("*")
        .eq("ativo", True)
        .order("nome")
        .execute()
    )
    return resp.data or []


def buscar_regra_imobiliaria(imobiliaria_id: str):
    resp = (
        get_supabase()
        .table("regras_imobiliaria")
        .select("*")
        .eq("imobiliaria_id", imobiliaria_id)
        .eq("ativo", True)
        .order("created_at", desc=True)
        .limit(1)
        .execute()
    )
    return resp.data[0] if resp.data else None


# =========================
# AUTH
# =========================
def login(email: str, senha: str):
    return get_supabase().auth.sign_in_with_password(
        {
            "email": email.strip(),
            "password": senha,
        }
    )


def cadastrar(nome: str, email: str, senha: str):
    url = st.secrets["SUPABASE_URL"].strip()
    key = st.secrets["SUPABASE_KEY"].strip()

    resp = requests.post(
        f"{url}/auth/v1/signup",
        headers={
            "apikey": key,
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json",
        },
        json={
            "email": email.strip(),
            "password": senha,
            "data": {"nome": nome.strip()},
        },
        timeout=10,
    )
    return resp


# =========================
# PERMISSÕES
# =========================
def eh_superadmin():
    return st.session_state.get("role_global") == "superadmin"


def pode_ver_todas():
    return eh_superadmin() or st.session_state.get("cargo_imobiliaria") == "administrador"


def pode_aprovar():
    return pode_ver_todas() or st.session_state.get("cargo_imobiliaria") == "diretor"


def pode_gerenciar_membros():
    return pode_ver_todas()


# =========================
# TELAS
# =========================
def tela_login():
    st.markdown('<div class="gp-card-dark">', unsafe_allow_html=True)
    st.title("🔐 Entrar no sistema")
    abas = st.tabs(["Login", "Criar conta"])

    with abas[0]:
        email = st.text_input("Email", key="login_email")
        senha = st.text_input("Senha", type="password", key="login_senha")

        if st.button("Entrar", use_container_width=True):
            try:
                resp = login(email, senha)
                user = resp.user

                if not user:
                    st.error("Email ou senha inválidos.")
                    return

                salvar_tokens(resp)

                profile = buscar_profile_por_id(user.id)
                if not profile:
                    st.error("Perfil não encontrado.")
                    return

                aplicar_login(profile)
                st.success("Login realizado com sucesso.")
                st.rerun()

            except Exception as e:
                st.error(f"Erro no login: {e}")

    with abas[1]:
        nome = st.text_input("Nome completo", key="cad_nome")
        email = st.text_input("Email", key="cad_email")
        senha = st.text_input("Senha", type="password", key="cad_senha")
        confirmar = st.text_input("Confirmar senha", type="password", key="cad_confirm")

        if st.button("Criar conta", key="btn_cadastro", use_container_width=True):
            if senha != confirmar:
                st.warning("Senhas não conferem.")
                return

            if not nome.strip() or not email.strip() or not senha.strip():
                st.warning("Preencha todos os campos.")
                return

            try:
                existente = buscar_profile_por_email(email)
                if existente:
                    st.warning("Já existe uma conta com esse email.")
                    return

                resp = cadastrar(nome, email, senha)

                if resp.status_code in (200, 201):
                    st.success("Conta criada com sucesso. Agora faça login.")
                else:
                    try:
                        erro_json = resp.json()
                        st.error(f"Erro ao criar conta: {erro_json}")
                    except Exception:
                        st.error(f"Erro ao criar conta: {resp.text}")

            except Exception as e:
                st.error(f"Erro ao criar conta: {e}")

    st.markdown("</div>", unsafe_allow_html=True)


def tela_escolha_imobiliaria():
    st.markdown('<div class="gp-card"><div class="gp-section-title">🏢 Escolha uma imobiliária</div>', unsafe_allow_html=True)

    imobiliarias = listar_imobiliarias_ativas()
    vinculos = buscar_vinculos_usuario(st.session_state["usuario_id"])
    mapa_vinculos = {v["imobiliaria_id"]: v for v in vinculos}

    if not imobiliarias:
        st.warning("Nenhuma imobiliária cadastrada.")
        st.markdown("</div>", unsafe_allow_html=True)
        return

    for imob in imobiliarias:
        st.subheader(imob["nome"])
        vinculo = mapa_vinculos.get(imob["id"])

        if eh_superadmin():
            st.success("Acesso liberado como superadmin.")
            if st.button(f"Entrar em {imob['nome']}", key=f"entrar_super_{imob['id']}", use_container_width=True):
                st.session_state["imobiliaria_id"] = imob["id"]
                st.session_state["imobiliaria_nome"] = imob["nome"]
                st.session_state["cargo_imobiliaria"] = "administrador"
                st.session_state["status_vinculo"] = "aprovado"
                st.rerun()
            st.divider()
            continue

        if vinculo:
            status = vinculo["status"]

            if status == "aprovado":
                st.success(f"Acesso aprovado como {vinculo['cargo']}.")
                if st.button(f"Entrar em {imob['nome']}", key=f"entrar_{imob['id']}", use_container_width=True):
                    st.session_state["imobiliaria_id"] = imob["id"]
                    st.session_state["imobiliaria_nome"] = imob["nome"]
                    st.session_state["cargo_imobiliaria"] = vinculo["cargo"]
                    st.session_state["status_vinculo"] = vinculo["status"]
                    st.rerun()

            elif status == "pendente":
                st.info("Sua solicitação está pendente.")

            elif status == "rejeitado":
                st.error("Sua solicitação foi rejeitada.")
        else:
            if st.button(f"Solicitar acesso a {imob['nome']}", key=f"sol_{imob['id']}", use_container_width=True):
                solicitar_acesso(st.session_state["usuario_id"], imob["id"])
                st.success("Solicitação enviada.")
                st.rerun()

        st.divider()

    st.markdown("</div>", unsafe_allow_html=True)


def painel_aprovacoes():
    if not pode_aprovar():
        return

    st.markdown('<div class="gp-card"><div class="gp-section-title">✅ Solicitações pendentes</div>', unsafe_allow_html=True)

    if pode_ver_todas():
        solicitacoes = listar_solicitacoes_pendentes()
    else:
        solicitacoes = listar_solicitacoes_pendentes_por_imobiliaria(st.session_state["imobiliaria_id"])

    if not solicitacoes:
        st.info("Nenhuma solicitação pendente.")
        st.markdown("</div>", unsafe_allow_html=True)
        return

    for s in solicitacoes:
        imob = s.get("imobiliarias") or {}
        nome_usuario, email_usuario = buscar_nome_email_usuario(s["user_id"])

        st.write(f"**Usuário:** {nome_usuario} — {email_usuario}")
        st.write(f"**Imobiliária:** {imob.get('nome', '')}")

        if pode_ver_todas():
            c1, c2, c3, c4 = st.columns(4)
            with c1:
                if st.button("Corretor", key=f"cor_{s['id']}"):
                    aprovar_vinculo(s["id"], st.session_state["usuario_id"], "corretor")
                    st.rerun()
            with c2:
                if st.button("Diretor", key=f"dir_{s['id']}"):
                    aprovar_vinculo(s["id"], st.session_state["usuario_id"], "diretor")
                    st.rerun()
            with c3:
                if st.button("Administrador", key=f"adm_{s['id']}"):
                    aprovar_vinculo(s["id"], st.session_state["usuario_id"], "administrador")
                    st.rerun()
            with c4:
                if st.button("Rejeitar", key=f"rej_{s['id']}"):
                    rejeitar_vinculo(s["id"])
                    st.rerun()
        else:
            c1, c2 = st.columns(2)
            with c1:
                if st.button("Aprovar corretor", key=f"ap_{s['id']}"):
                    aprovar_vinculo(s["id"], st.session_state["usuario_id"], "corretor")
                    st.rerun()
            with c2:
                if st.button("Rejeitar", key=f"rp_{s['id']}"):
                    rejeitar_vinculo(s["id"])
                    st.rerun()

        st.divider()

    st.markdown("</div>", unsafe_allow_html=True)


def painel_membros_imobiliaria():
    if not st.session_state.get("imobiliaria_id"):
        return

    membros = listar_membros_imobiliaria(st.session_state["imobiliaria_id"])

    st.markdown('<div class="gp-card"><div class="gp-section-title">👥 Membros da imobiliária</div>', unsafe_allow_html=True)

    if not membros:
        st.info("Nenhum membro encontrado.")
        st.markdown("</div>", unsafe_allow_html=True)
        return

    for membro in membros:
        nome, email = buscar_nome_email_usuario(membro["user_id"])
        status_atual = membro.get("status", "")
        cargo_atual = membro.get("cargo", "")

        st.markdown('<div class="gp-member">', unsafe_allow_html=True)
        st.write(f"**Nome:** {nome or '-'}")
        st.write(f"**Email:** {email or '-'}")
        st.write(f"**Status atual:** {status_atual}")
        st.write(f"**Cargo atual:** {cargo_atual}")

        if pode_gerenciar_membros():
            col1, col2 = st.columns(2)

            with col1:
                novo_cargo = st.selectbox(
                    f"Novo cargo para {email or membro['user_id']}",
                    ["corretor", "diretor", "administrador"],
                    index=["corretor", "diretor", "administrador"].index(cargo_atual) if cargo_atual in ["corretor", "diretor", "administrador"] else 0,
                    key=f"cargo_sel_{membro['id']}",
                )

                if st.button("Salvar cargo", key=f"salvar_cargo_{membro['id']}", use_container_width=True):
                    alterar_cargo_vinculo(membro["id"], novo_cargo)
                    st.success("Cargo atualizado com sucesso.")
                    st.rerun()

            with col2:
                novo_status = st.selectbox(
                    f"Novo status para {email or membro['user_id']}",
                    ["aprovado", "pendente", "rejeitado"],
                    index=["aprovado", "pendente", "rejeitado"].index(status_atual) if status_atual in ["aprovado", "pendente", "rejeitado"] else 0,
                    key=f"status_sel_{membro['id']}",
                )

                if st.button("Salvar status", key=f"salvar_status_{membro['id']}", use_container_width=True):
                    alterar_status_vinculo(membro["id"], novo_status)
                    st.success("Status atualizado com sucesso.")
                    st.rerun()

        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)


def tela_home():
    st.markdown('<div class="gp-card"><div class="gp-section-title">🏠 Painel inicial</div>', unsafe_allow_html=True)
    st.write(f"Usuário: **{st.session_state['usuario_nome']}**")
    st.write(f"Imobiliária ativa: **{st.session_state['imobiliaria_nome']}**")
    st.write(f"Cargo: **{st.session_state['cargo_imobiliaria']}**")
    st.markdown("</div>", unsafe_allow_html=True)

    empreendimentos = listar_empreendimentos()
    regra = buscar_regra_imobiliaria(st.session_state["imobiliaria_id"])

    st.markdown('<div class="gp-card"><div class="gp-section-title">🏢 Empreendimentos disponíveis</div>', unsafe_allow_html=True)
    if not empreendimentos:
        st.warning("Nenhum empreendimento cadastrado.")
    else:
        for emp in empreendimentos:
            st.write(f"- {emp['nome']}")
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown('<div class="gp-card"><div class="gp-section-title">📑 Regra da imobiliária</div>', unsafe_allow_html=True)
    if not regra:
        st.error("Regra financeira não encontrada.")
    else:
        st.write(f"**Total comissão:** {float(regra['porcentagem_total_comissao']):.2f}%")
        st.write(f"**Ato mínimo:** {float(regra['porcentagem_ato_minimo']):.2f}%")
        st.write(f"**Imobiliária:** {float(regra['porcentagem_imobiliaria']):.2f}%")
        st.write(f"**Corretor:** {float(regra['porcentagem_corretor']):.2f}%")
        st.write(f"**Gerente:** {float(regra['porcentagem_gerente']):.2f}%")
    st.markdown("</div>", unsafe_allow_html=True)


# =========================
# MAIN
# =========================
init_state()
restaurar_sessao()

imob = buscar_imobiliaria_por_id(st.session_state["imobiliaria_id"]) if st.session_state.get("imobiliaria_id") else None
aplicar_tema(imob)
render_topbar(imob)

if not st.session_state["logado"]:
    tela_login()
    st.stop()

st.sidebar.write(f"👤 {st.session_state['usuario_nome']}")
st.sidebar.write(f"📧 {st.session_state['usuario_email']}")
st.sidebar.write(f"🌐 Perfil global: {st.session_state['role_global']}")

if st.session_state.get("imobiliaria_nome"):
    st.sidebar.write(f"🏢 {st.session_state['imobiliaria_nome']}")
if st.session_state.get("cargo_imobiliaria"):
    st.sidebar.write(f"🔑 {st.session_state['cargo_imobiliaria']}")

if st.sidebar.button("🔄 Trocar imobiliária", use_container_width=True):
    limpar_estado_imobiliaria()
    st.rerun()

logout()

if not st.session_state.get("imobiliaria_id"):
    tela_escolha_imobiliaria()
    st.stop()

painel_aprovacoes()
painel_membros_imobiliaria()
tela_home()
