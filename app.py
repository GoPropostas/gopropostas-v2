if eh_admin:
    with st.expander("🔑 Aprovar usuários por imobiliária", expanded=True):
        pendentes = listar_pendentes_imobiliarias()

        if not pendentes:
            st.info("Nenhuma solicitação pendente.")
        else:
            for p in pendentes:
                perfil = p.get("profile_usuario") or {}
                imob = p.get("imobiliarias") or {}

                st.markdown('<div class="gp-card">', unsafe_allow_html=True)
                st.write(f"**Usuário:** {perfil.get('email', '-')}")
                st.write(f"**Nome:** {perfil.get('nome', '-')}")
                st.write(f"**Imobiliária:** {imob.get('nome', '-')}")

                col_ap1, col_ap2, col_ap3 = st.columns([2, 1, 1])

                with col_ap1:
                    cargo_aprovacao = st.selectbox(
                        "Cargo",
                        ["corretor", "gerente", "diretor"],
                        key=f"cargo_{p['id']}"
                    )

                with col_ap2:
                    if st.button("Aprovar", key=f"aprovar_{p['id']}", use_container_width=True):
                        aprovar_usuario_imobiliaria(p["id"], cargo_aprovacao)
                        st.success("Usuário aprovado")
                        st.rerun()

                with col_ap3:
                    if st.button("Rejeitar", key=f"rejeitar_{p['id']}", use_container_width=True):
                        rejeitar_usuario_imobiliaria(p["id"])
                        st.warning("Usuário rejeitado")
                        st.rerun()

                st.markdown("</div>", unsafe_allow_html=True)
