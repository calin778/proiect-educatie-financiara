# =============================================================
# PAGINA  -  Cautare (fara modelul de chat)
# =============================================================
# Aceasta pagina NU este RAG complet - este doar pasul R (Retrieval).
# RAG complet = pagina Profesor AI (Retrieval + Augmented + Generation).
#
# Se folosesc doar modelul de EMBEDDING (transforma intrebarea in numere
# care reprezinta sensul ei; nu scrie text) si CHROMA (compara numerele
# si intoarce lectiile cele mai apropiate). Textul afisat este textul
# lectiei, exact cum e salvat.
# =============================================================
import streamlit as st
from comun import api

st.title("🔎 Cautare in lectii")
st.caption("Cautarea se face dupa SENS: incearca o intrebare care nu foloseste "
           "cuvintele din lectii, ex: *de ce valoreaza banii mei mai putin in fiecare an?*")

with st.expander("ℹ️ Cum functioneaza pagina asta? (fara modelul de chat)"):
    st.markdown(
        "Pe aceasta pagina **nu se foloseste modelul de chat**. Nimeni nu "
        "formuleaza un raspuns - vezi lectiile **exact cum sunt salvate**.\n\n"
        "1. **Embedding** - un model OpenAI dedicat transforma intrebarea intr-o "
        "lista de numere care reprezinta **sensul** ei (nu scrie text).\n"
        "2. **Chroma** - compara aceste numere cu cele ale fiecarei lectii.\n"
        "3. **Rezultat** - lectiile cu sensul cel mai apropiat, ordonate dupa "
        "**distanta** (mai mica = mai potrivita).\n\n"
        "**Este asta RAG?** Doar **prima parte** din el:\n\n"
        "| Pas | Ce face | Cautare | Profesor AI |\n"
        "|---|---|---|---|\n"
        "| **R**etrieval | gaseste lectiile relevante | ✅ | ✅ |\n"
        "| **A**ugmented | da lectiile gasite modelului de chat | ❌ | ✅ |\n"
        "| **G**eneration | modelul scrie raspunsul pe baza lor | ❌ | ✅ |\n\n"
        "Sistemul RAG complet este pagina **Profesor AI**."
    )

intrebare = st.text_input("Intrebare")
n = st.slider("Cate lectii", min_value=1, max_value=5, value=2)

if intrebare:
    ok, rezultate = api("GET", "/cauta", params={"intrebare": intrebare, "n": n}, timeout=30)
    if not ok:
        st.error(rezultate)
        st.stop()

    for r in rezultate:
        with st.container(border=True):
            # TODO: afiseaza titlul lectiei si distanta, apoi textul lectiei
            st.markdown(f"**{r['titlu']}**")
            st.caption(f"Distanta semantica: `{r['distanta']:.4f}`")
            st.markdown(r["text"])

    st.caption("Distanta mai MICA = lectie mai potrivita. Chroma intoarce mereu "
               "n lectii, chiar daca niciuna nu e relevanta - compara distantele.")
