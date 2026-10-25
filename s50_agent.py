# =============================================================
# AGENTUL  -  Profesorul de finante personale  (LangChain + RAG)
# =============================================================
# Acelasi agent ca la s49: un singur tool, care cauta in lectiile de
# educatie financiara (prin s50_rag.py), iar modelul raspunde pe baza lor.
#
# Fisierul nu stie nimic de FastAPI sau Streamlit. Il poti testa singur:
#   python3 s50_agent.py
#
# Setup: pip install langchain langchain-openai
#        export OPENAI_API_KEY="sk-..."   (cheia NU se scrie in cod)
# =============================================================

from langchain.agents import create_agent
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI

import s50_model
import s50_rag


# #############################################################
# PARTEA 1 - TOOL-UL DE CAUTARE  (plan: 4.1)
# #############################################################


# TODO 4.1: tool-ul cauta_in_lectii(intrebare: str) -> str
#   La fel ca cauta_in_notite de la s49.
#
#   1. rezultate = s50_rag.cauta(intrebare)
#   2. Pentru fiecare rezultat r, o bucata de text:
#          f"[{r['titlu']}]\n{r['text']}"
#      Bucatile le pui intr-o lista.
#   3. return bucatile unite cu "\n\n".join(...)
@tool
def cauta_in_lectii(intrebare: str) -> str:
    """Cauta in lectiile de educatie financiara lectiile relevante pentru
    intrebare. Foloseste-l pentru ORICE intrebare despre bani: buget,
    economii, fond de urgenta, dobanda, inflatie, credite, carduri,
    investitii, pensii."""
    rezultate = s50_rag.cauta(intrebare)
    bucati = [f"[{r['titlu']}]\n{r['text']}" for r in rezultate]
    return "\n\n".join(bucati)


# #############################################################
# PARTEA 2 - AGENTUL  (gata scris)
# #############################################################
# Pe langa regulile RAG (raspunde DOAR din lectii, spune sursa, nu
# inventa), profesorul are si LIMITE, ca la s45: explica notiuni, dar nu
# recomanda produse financiare concrete si nu promite castiguri.
SYSTEM_PROMPT = (
    "Esti un profesor de educatie financiara pentru adulti. Pentru orice "
    "intrebare despre bani folosesti tool-ul cauta_in_lectii si raspunzi DOAR "
    "pe baza lectiilor gasite. Explici clar, cu exemple simple, si aplici "
    "ideile pe situatia utilizatorului. La final spui din ce lectii ai luat "
    "informatia (titlurile dintre parantezele drepte). Daca lectiile nu acopera "
    "subiectul, spui clar asta - nu inventa. NU recomanzi actiuni, fonduri, "
    "banci sau produse concrete si NU promiti castiguri: spui ca pentru decizii "
    "personale e nevoie de un consultant financiar autorizat. Raspunzi scurt, in romana."
)

llm = ChatOpenAI(model="gpt-4.1-mini")

agent = create_agent(
    llm,
    tools=[cauta_in_lectii],
    system_prompt=SYSTEM_PROMPT,
)


# #############################################################
# PARTEA 3 - ruleaza_agent  (plan: 4.2)
# #############################################################


# TODO 4.2: ruleaza_agent(mesaj, istoric)
#   1. messages = istoric + [{"role": "user", "content": mesaj}]
#   2. rezultat = agent.invoke({"messages": messages})
#   3. apeluri = []; pentru fiecare mesaj m din rezultat["messages"] de tip
#      "ToolMessage" (type(m).__name__), adaugi {"tool": m.name, "rezultat": m.content}
#   4. raspuns = rezultat["messages"][-1].content
#   5. return raspuns, apeluri
def ruleaza_agent(mesaj: str, istoric: list[dict]):
    messages = istoric + [{"role": "user", "content": mesaj}]
    rezultat = agent.invoke({"messages": messages})

    apeluri = []
    for m in rezultat["messages"]:
        if type(m).__name__ == "ToolMessage":
            apeluri.append({"tool": m.name, "rezultat": m.content})

    raspuns = rezultat["messages"][-1].content
    return raspuns, apeluri
if __name__ == "__main__":
    print("Initializare baza si index RAG...")
    s50_model.init_db()
    with s50_model.SessionLocal() as s:
        s50_rag.indexeaza_toate(s50_model.toate_lectiile(s))

    print("\n--- Test Agent ---")
    intrebari_test = [
        "Cheltuiesc 4000 de lei pe lună. Cât ar trebui să am pus deoparte pentru urgențe?",
        "Ce este regula lui 72?",
        "Ce acțiuni să cumpăr mâine ca să mă îmbogățesc rapid?"
    ]
    for q in intrebari_test:
        print(f"\nIntrebare: {q}")
        r, a = ruleaza_agent(q, [])
        print(f"Raspuns: {r}")
        print(f"Apeluri tool: {len(a)}")