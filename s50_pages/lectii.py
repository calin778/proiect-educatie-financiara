import streamlit as st
from comun import api

st.title("📚 Lectii de educatie financiara")

CATEGORII = ["Toate", "Buget", "Economii", "Credite", "Investitii", "Pensie", "Altele"]

categorie = st.sidebar.selectbox("Categorie", CATEGORII)

params = {}
if categorie != "Toate":
    params["categorie"] = categorie

ok, lectii = api("GET", "/lectii", params=params)
if not ok:
    st.error(lectii)
    st.stop()

if not lectii:
    st.info("Nicio lectie pentru categoria aleasa. Adauga una din 'Adauga lectie'.")
    st.stop()

st.caption(f"{len(lectii)} lectii")

for l in lectii:
    with st.container(border=True):
        c_info, c_sterge = st.columns([6, 1])

        with c_info:
            st.markdown(f"**{l['titlu']}**")
            st.caption(f"{l['categorie']} · adaugata pe {l['data']} · {len(l['continut'])} caractere")
            with st.expander("Continut"):
                st.markdown(l["continut"])

        with c_sterge:
            if st.button("Sterge", key=f"sterge_{l['id']}"):
                ok, rezultat = api("DELETE", f"/lectii/{l['id']}")
                if ok:
                    st.rerun()
                else:
                    st.error(rezultat)
