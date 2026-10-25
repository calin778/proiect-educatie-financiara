import streamlit as st
from comun import api

st.title("➕ Adauga lectie")
st.caption("La salvare, lectia intra si in indexul RAG - profesorul o poate folosi imediat.")

with st.form("form_lectie_noua", clear_on_submit=True):
    c1, c2 = st.columns([3, 1])
    titlu = c1.text_input("Titlu", placeholder="ex: Asigurarea locuintei")
    categorie = c2.selectbox("Categorie", ["Buget", "Economii", "Credite",
                                           "Investitii", "Pensie", "Altele"])
    continut = st.text_area("Continut", height=300,
                            placeholder="Asigurarea locuintei protejeaza impotriva...")

    trimis = st.form_submit_button("Adauga", type="primary")

if trimis:
    # TODO: POST /lectii cu cheile "titlu", "categorie", "continut" si timeout=30
    #   ok -> st.success cu titlul din rezultat; altfel -> st.error(rezultat)
    if not titlu.strip() or not continut.strip():
        st.error("Titlul si continutul sunt obligatorii.")
    else:
        ok, rezultat = api(
            "POST",
            "/lectii",
            json={"titlu": titlu, "categorie": categorie, "continut": continut},
            timeout=30,
        )
        if ok:
            st.success(f"Lectia '{rezultat['titlu']}' a fost adaugata cu succes!")
        else:
            st.error(rezultat)
