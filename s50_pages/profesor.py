# =============================================================
# PAGINA  -  Profesor AI  (ca Asistent AI de la s49)
# =============================================================
# Pagina trimite mesajul + istoricul la POST /chat, iar serverul ruleaza
# agentul. Sub fiecare raspuns aratam lectiile gasite (sursele).
#
# Aceasta pagina este sistemul RAG COMPLET:
#   R - Retrieval   : tool-ul cauta_in_lectii gaseste lectiile
#   A - Augmented   : lectiile gasite ajung la modelul de chat
#   G - Generation  : modelul scrie raspunsul pe baza lor
# =============================================================

import streamlit as st
from comun import api

st.title("🎓 Profesorul tau de finante personale")
st.caption("Exemple: *Cheltuiesc 4000 de lei pe luna - cat ar trebui sa am deoparte?* · "
           "*Ce e DAE?* · *De ce sa platesc cardul de credit inainte sa investesc?*")

with st.expander("ℹ️ Cum functioneaza pagina asta? (RAG complet)"):
    st.markdown(
        "Aceasta pagina este **sistemul RAG complet**. La fiecare intrebare:\n"
        "1. **R**etrieval - se cauta in lectii, exact ca in pagina *Cautare*\n"
        "2. **A**ugmented - lectiile gasite sunt date modelului de chat\n"
        "3. **G**eneration - modelul citeste lectiile si scrie raspunsul\n\n"
        "Lectiile folosite apar sub fiecare raspuns, la **📚 Surse**. Daca "
        "raspunsul contine ceva ce nu apare in surse, modelul a inventat.\n\n"
        "Profesorul explica notiuni - **nu** recomanda produse financiare concrete."
    )

if "messages" not in st.session_state:
    st.session_state.messages = []   # [{"role", "content", "apeluri"}]


def arata_apeluri(apeluri):
    if apeluri:
        with st.expander("📚 Surse - lectiile gasite"):
            for a in apeluri:
                st.caption(a["rezultat"])


for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])
        arata_apeluri(m.get("apeluri"))


mesaj = st.chat_input("Intreaba-ma despre bani...")

if mesaj:
    with st.chat_message("user"):
        st.markdown(mesaj)

    istoric = [{"role": m["role"], "content": m["content"]} for m in st.session_state.messages]

    with st.chat_message("assistant"):
        with st.spinner("Profesorul analizeaza lectiile..."):
            ok, rezultat = api("POST", "/chat", json={"mesaj": mesaj, "istoric": istoric}, timeout=60)
            if ok:
                st.markdown(rezultat["raspuns"])
                arata_apeluri(rezultat.get("apeluri"))
                st.session_state.messages.append({"role": "user", "content": mesaj})
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": rezultat["raspuns"],
                    "apeluri": rezultat.get("apeluri", []),
                })
            else:
                st.error(rezultat)

if st.session_state.messages and st.sidebar.button("Conversatie noua"):
    st.session_state.messages = []
    st.rerun()
